#ifndef PYTEKT_BOTS_DISPATCHER_HPP
#define PYTEKT_BOTS_DISPATCHER_HPP

#include "universal_event.hpp"
#include "json_min.hpp"
#include <string>
#include <vector>
#include <unordered_map>
#include <regex>
#include <memory>
#include <mutex>

namespace pytekt {
namespace bots {

struct PatternHandler {
    std::string pattern_str;
    std::regex regex;
    std::string handler_id;
};

class Dispatcher {
public:
    Dispatcher();
    ~Dispatcher() = default;

    // Handler registrations
    void add_command_handler(const std::string& command, const std::string& handler_id);
    void add_pattern_handler(const std::string& pattern, const std::string& handler_id);
    void add_event_handler(const std::string& event_type, const std::string& handler_id);
    void add_state_handler(const std::string& state_name, const std::string& handler_id);

    // Matching
    std::vector<std::string> match(const UniversalEvent& event, const std::string& current_state = "") const;

    // Zero-copy / fast C++ parsers
    UniversalEvent parse_telegram(const std::string& json_str) const;
    UniversalEvent parse_discord(const std::string& json_str) const;
    UniversalEvent parse_generic(const std::string& json_str, const std::string& platform = "generic") const;

    // Helper for command extraction
    static void extract_command_and_args(const std::string& text, std::string& command, std::vector<std::string>& args);

private:
    mutable std::mutex mutex_;
    std::unordered_map<std::string, std::vector<std::string>> command_handlers_;
    std::vector<PatternHandler> pattern_handlers_;
    std::unordered_map<std::string, std::vector<std::string>> event_handlers_;
    std::unordered_map<std::string, std::vector<std::string>> state_handlers_;
};

} // namespace bots
} // namespace pytekt

#endif // PYTEKT_BOTS_DISPATCHER_HPP
