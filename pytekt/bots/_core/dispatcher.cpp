#include "dispatcher.hpp"
#include <sstream>
#include <iostream>

namespace pytekt {
namespace bots {

Dispatcher::Dispatcher() {}

void Dispatcher::add_command_handler(const std::string& command, const std::string& handler_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    std::string clean_cmd = command;
    if (!clean_cmd.empty() && (clean_cmd[0] == '/' || clean_cmd[0] == '!')) {
        clean_cmd = clean_cmd.substr(1);
    }
    command_handlers_[clean_cmd].push_back(handler_id);
}

void Dispatcher::add_pattern_handler(const std::string& pattern, const std::string& handler_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    try {
        PatternHandler ph;
        ph.pattern_str = pattern;
        ph.regex = std::regex(pattern, std::regex::ECMAScript | std::regex::optimize);
        ph.handler_id = handler_id;
        pattern_handlers_.push_back(ph);
    } catch (const std::exception& e) {
        // Fallback: simple literal regex
        PatternHandler ph;
        ph.pattern_str = pattern;
        ph.regex = std::regex(std::regex_replace(pattern, std::regex(R"([-[\]{}()*+?.,\^$|#\s])"), R"(\$&)"));
        ph.handler_id = handler_id;
        pattern_handlers_.push_back(ph);
    }
}

void Dispatcher::add_event_handler(const std::string& event_type, const std::string& handler_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    event_handlers_[event_type].push_back(handler_id);
}

void Dispatcher::add_state_handler(const std::string& state_name, const std::string& handler_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    state_handlers_[state_name].push_back(handler_id);
}

void Dispatcher::extract_command_and_args(const std::string& text, std::string& command, std::vector<std::string>& args) {
    command.clear();
    args.clear();

    if (text.empty()) return;

    size_t start = 0;
    while (start < text.size() && std::isspace(static_cast<unsigned char>(text[start]))) {
        start++;
    }
    if (start >= text.size()) return;

    char prefix = text[start];
    if (prefix != '/' && prefix != '!') {
        return;
    }

    size_t end = start + 1;
    while (end < text.size() && !std::isspace(static_cast<unsigned char>(text[end])) && text[end] != '@') {
        end++;
    }

    command = text.substr(start + 1, end - (start + 1));

    // Skip bot username if @botname was attached
    while (end < text.size() && !std::isspace(static_cast<unsigned char>(text[end]))) {
        end++;
    }

    // Parse remaining arguments
    std::string remainder = text.substr(end);
    std::istringstream iss(remainder);
    std::string arg;
    while (iss >> arg) {
        args.push_back(arg);
    }
}

std::vector<std::string> Dispatcher::match(const UniversalEvent& event, const std::string& current_state) const {
    std::lock_guard<std::mutex> lock(mutex_);
    std::vector<std::string> matched;

    // 1. If state matches and is active
    if (!current_state.empty()) {
        auto sit = state_handlers_.find(current_state);
        if (sit != state_handlers_.end()) {
            for (const auto& hid : sit->second) {
                matched.push_back(hid);
            }
        }
    }

    // 2. Command match
    if (!event.command.empty()) {
        auto cit = command_handlers_.find(event.command);
        if (cit != command_handlers_.end()) {
            for (const auto& hid : cit->second) {
                matched.push_back(hid);
            }
        }
    }

    // 3. Regex / Pattern match on text
    if (!event.text.empty()) {
        for (const auto& ph : pattern_handlers_) {
            if (std::regex_search(event.text, ph.regex)) {
                matched.push_back(ph.handler_id);
            }
        }
    }

    // 4. Event type match (e.g. "message", "voice", "photo", "callback")
    if (!event.event_type.empty()) {
        auto eit = event_handlers_.find(event.event_type);
        if (eit != event_handlers_.end()) {
            for (const auto& hid : eit->second) {
                matched.push_back(hid);
            }
        }
    }

    // 5. General message fallback if event_type is command/photo/voice but also considered a message
    if (event.event_type != "message") {
        auto eit = event_handlers_.find("message");
        if (eit != event_handlers_.end()) {
            for (const auto& hid : eit->second) {
                matched.push_back(hid);
            }
        }
    }

    // 6. Generic wildcard / any handlers
    auto any_it = event_handlers_.find("*");
    if (any_it != event_handlers_.end()) {
        for (const auto& hid : any_it->second) {
            matched.push_back(hid);
        }
    }

    return matched;
}

UniversalEvent Dispatcher::parse_telegram(const std::string& json_str) const {
    UniversalEvent ev;
    ev.platform = "telegram";
    ev.raw = json_str;

    JsonValue root = JsonParser::parse(json_str);
    if (!root.is_object()) return ev;

    ev.id = std::to_string(root.get_int64("update_id", 0));

    JsonValue msg;
    if (root.contains("message")) {
        msg = root.get("message");
    } else if (root.contains("edited_message")) {
        msg = root.get("edited_message");
    } else if (root.contains("channel_post")) {
        msg = root.get("channel_post");
    } else if (root.contains("callback_query")) {
        const auto& cb = root.get("callback_query");
        ev.id = cb.get_string("id");
        ev.event_type = "callback";
        ev.text = cb.get_string("data");
        ev.user_id = std::to_string(cb.get("from").get_int64("id", 0));
        if (cb.contains("message")) {
            const auto& cb_msg = cb.get("message");
            ev.chat_id = std::to_string(cb_msg.get("chat").get_int64("id", 0));
            ev.metadata["message_id"] = std::to_string(cb_msg.get_int64("message_id", 0));
        }
        return ev;
    }

    if (!msg.is_object()) return ev;

    int64_t msg_id = msg.get_int64("message_id", 0);
    if (msg_id != 0) {
        ev.id = std::to_string(msg_id);
    }

    if (msg.contains("chat")) {
        ev.chat_id = std::to_string(msg.get("chat").get_int64("id", 0));
    }
    if (msg.contains("from")) {
        const auto& from = msg.get("from");
        ev.user_id = std::to_string(from.get_int64("id", 0));
        ev.metadata["username"] = from.get_string("username");
        ev.metadata["first_name"] = from.get_string("first_name");
        ev.metadata["last_name"] = from.get_string("last_name");
    }

    if (msg.contains("reply_to_message")) {
        ev.metadata["reply_to_message_id"] = std::to_string(msg.get("reply_to_message").get_int64("message_id", 0));
    }

    ev.text = msg.get_string("text");
    if (ev.text.empty() && msg.contains("caption")) {
        ev.text = msg.get_string("caption");
    }

    // Check voice / audio
    if (msg.contains("voice")) {
        ev.event_type = "voice";
        ev.metadata["file_id"] = msg.get("voice").get_string("file_id");
        ev.metadata["duration"] = std::to_string(msg.get("voice").get_int64("duration", 0));
    } else if (msg.contains("audio")) {
        ev.event_type = "voice";
        ev.metadata["file_id"] = msg.get("audio").get_string("file_id");
    }
    // Check photo
    else if (msg.contains("photo") && msg.get("photo").is_array() && !msg.get("photo").arr_val.empty()) {
        ev.event_type = "photo";
        // Get the largest photo (last element in array)
        const auto& photos = msg.get("photo").arr_val;
        const auto& largest = photos.back();
        ev.metadata["file_id"] = largest.get_string("file_id");
        ev.metadata["width"] = std::to_string(largest.get_int64("width", 0));
        ev.metadata["height"] = std::to_string(largest.get_int64("height", 0));
    }

    // Command check
    if (!ev.text.empty() && (ev.text[0] == '/' || ev.text[0] == '!')) {
        extract_command_and_args(ev.text, ev.command, ev.args);
        if (!ev.command.empty()) {
            ev.event_type = "command";
        }
    } else if (ev.event_type.empty() || ev.event_type == "message") {
        ev.event_type = "message";
    }

    return ev;
}

UniversalEvent Dispatcher::parse_discord(const std::string& json_str) const {
    UniversalEvent ev;
    ev.platform = "discord";
    ev.raw = json_str;

    JsonValue root = JsonParser::parse(json_str);
    if (!root.is_object()) return ev;

    // Discord events often wrap payload in "d"
    JsonValue data = root.contains("d") ? root.get("d") : root;

    ev.id = data.get_string("id");
    ev.chat_id = data.get_string("channel_id");
    if (data.contains("guild_id")) {
        ev.metadata["guild_id"] = data.get_string("guild_id");
    }

    if (data.contains("author")) {
        const auto& author = data.get("author");
        ev.user_id = author.get_string("id");
        ev.metadata["username"] = author.get_string("username");
    }

    ev.text = data.get_string("content");

    // Check attachments for photos/audio
    if (data.contains("attachments") && data.get("attachments").is_array()) {
        const auto& atts = data.get("attachments").arr_val;
        for (const auto& att : atts) {
            std::string content_type = att.get_string("content_type");
            std::string url = att.get_string("url");
            if (content_type.find("image/") != std::string::npos) {
                ev.event_type = "photo";
                ev.metadata["url"] = url;
                ev.metadata["file_id"] = att.get_string("id");
                break;
            } else if (content_type.find("audio/") != std::string::npos) {
                ev.event_type = "voice";
                ev.metadata["url"] = url;
                ev.metadata["file_id"] = att.get_string("id");
                break;
            }
        }
    }

    // Interaction / Slash command check
    if (root.get_string("t") == "INTERACTION_CREATE" || root.get_int64("type") == 2) {
        ev.event_type = "interaction";
        if (data.contains("data")) {
            const auto& idata = data.get("data");
            ev.command = idata.get_string("name");
            if (!ev.command.empty()) {
                ev.event_type = "command";
            }
            if (idata.contains("options") && idata.get("options").is_array()) {
                for (const auto& opt : idata.get("options").arr_val) {
                    ev.args.push_back(opt.get_string("value"));
                }
            }
        }
    }

    // Standard command check on text
    if (!ev.text.empty() && (ev.text[0] == '/' || ev.text[0] == '!')) {
        extract_command_and_args(ev.text, ev.command, ev.args);
        if (!ev.command.empty()) {
            ev.event_type = "command";
        }
    } else if (ev.event_type.empty()) {
        ev.event_type = "message";
    }

    return ev;
}

UniversalEvent Dispatcher::parse_generic(const std::string& json_str, const std::string& platform) const {
    UniversalEvent ev;
    ev.platform = platform;
    ev.raw = json_str;

    JsonValue root = JsonParser::parse(json_str);
    if (!root.is_object()) return ev;

    ev.id = root.get_string("id", std::to_string(root.get_int64("id", 0)));
    ev.chat_id = root.get_string("chat_id", std::to_string(root.get_int64("chat_id", 0)));
    ev.user_id = root.get_string("user_id", std::to_string(root.get_int64("user_id", 0)));
    ev.text = root.get_string("text");
    if (ev.text.empty() && root.contains("content")) {
        ev.text = root.get_string("content");
    }
    ev.event_type = root.get_string("event_type", "message");

    if (root.contains("command")) {
        ev.command = root.get_string("command");
    }

    if (!ev.text.empty() && (ev.text[0] == '/' || ev.text[0] == '!') && ev.command.empty()) {
        extract_command_and_args(ev.text, ev.command, ev.args);
        if (!ev.command.empty()) {
            ev.event_type = "command";
        }
    }

    return ev;
}

} // namespace bots
} // namespace pytekt
