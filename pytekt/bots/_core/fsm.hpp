#ifndef PYTEKT_BOTS_FSM_HPP
#define PYTEKT_BOTS_FSM_HPP

#include <string>
#include <unordered_map>
#include <map>
#include <mutex>
#include <chrono>

namespace pytekt {
namespace bots {

struct FSMRecord {
    std::string state;
    double state_expires_at = 0.0; // 0.0 means never expires
    std::map<std::string, std::string> data;
    double data_expires_at = 0.0;
};

class FSM {
public:
    FSM();
    ~FSM() = default;

    // State management
    void set_state(const std::string& key, const std::string& state, double ttl_seconds = 0.0);
    std::string get_state(const std::string& key);
    void clear_state(const std::string& key);

    // Data management
    void set_data(const std::string& key, const std::string& data_key, const std::string& data_val, double ttl_seconds = 0.0);
    std::string get_data(const std::string& key, const std::string& data_key);
    std::map<std::string, std::string> get_all_data(const std::string& key);
    void set_all_data(const std::string& key, const std::map<std::string, std::string>& data, double ttl_seconds = 0.0);
    void clear_data(const std::string& key);

    // Full session clearing
    void reset(const std::string& key = "");
    size_t size() const;
    size_t cleanup_expired();

private:
    static double current_time();

    mutable std::mutex mutex_;
    std::unordered_map<std::string, FSMRecord> records_;
};

} // namespace bots
} // namespace pytekt

#endif // PYTEKT_BOTS_FSM_HPP
