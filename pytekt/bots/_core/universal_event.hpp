#ifndef PYTEKT_BOTS_UNIVERSAL_EVENT_HPP
#define PYTEKT_BOTS_UNIVERSAL_EVENT_HPP

#include <string>
#include <vector>
#include <map>
#include <chrono>

namespace pytekt {
namespace bots {

struct UniversalEvent {
    std::string id;
    std::string chat_id;
    std::string user_id;
    std::string text;
    std::string platform = "generic";
    std::string event_type = "message"; // "message", "command", "photo", "voice", "callback", "interaction", "unknown"
    std::string command;
    std::vector<std::string> args;
    std::string raw;
    std::map<std::string, std::string> metadata;
    double timestamp = 0.0;

    UniversalEvent() {
        auto now = std::chrono::system_clock::now();
        auto duration = now.time_since_epoch();
        timestamp = std::chrono::duration<double>(duration).count();
    }
};

} // namespace bots
} // namespace pytekt

#endif // PYTEKT_BOTS_UNIVERSAL_EVENT_HPP
