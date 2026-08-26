#include "fsm.hpp"
#include <vector>

namespace pytekt {
namespace bots {

FSM::FSM() {}

double FSM::current_time() {
    auto now = std::chrono::steady_clock::now();
    auto duration = now.time_since_epoch();
    return std::chrono::duration<double>(duration).count();
}

void FSM::set_state(const std::string& key, const std::string& state, double ttl_seconds) {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time();
    auto& rec = records_[key];
    rec.state = state;
    rec.state_expires_at = (ttl_seconds > 0.0) ? (now + ttl_seconds) : 0.0;
}

std::string FSM::get_state(const std::string& key) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = records_.find(key);
    if (it == records_.end()) return "";

    double now = current_time();
    if (it->second.state_expires_at > 0.0 && now >= it->second.state_expires_at) {
        it->second.state.clear();
        it->second.state_expires_at = 0.0;
        return "";
    }
    return it->second.state;
}

void FSM::clear_state(const std::string& key) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = records_.find(key);
    if (it != records_.end()) {
        it->second.state.clear();
        it->second.state_expires_at = 0.0;
    }
}

void FSM::set_data(const std::string& key, const std::string& data_key, const std::string& data_val, double ttl_seconds) {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time();
    auto& rec = records_[key];
    rec.data[data_key] = data_val;
    rec.data_expires_at = (ttl_seconds > 0.0) ? (now + ttl_seconds) : 0.0;
}

std::string FSM::get_data(const std::string& key, const std::string& data_key) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = records_.find(key);
    if (it == records_.end()) return "";

    double now = current_time();
    if (it->second.data_expires_at > 0.0 && now >= it->second.data_expires_at) {
        it->second.data.clear();
        it->second.data_expires_at = 0.0;
        return "";
    }

    auto dit = it->second.data.find(data_key);
    if (dit != it->second.data.end()) {
        return dit->second;
    }
    return "";
}

std::map<std::string, std::string> FSM::get_all_data(const std::string& key) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = records_.find(key);
    if (it == records_.end()) return {};

    double now = current_time();
    if (it->second.data_expires_at > 0.0 && now >= it->second.data_expires_at) {
        it->second.data.clear();
        it->second.data_expires_at = 0.0;
        return {};
    }

    return it->second.data;
}

void FSM::set_all_data(const std::string& key, const std::map<std::string, std::string>& data, double ttl_seconds) {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time();
    auto& rec = records_[key];
    rec.data = data;
    rec.data_expires_at = (ttl_seconds > 0.0) ? (now + ttl_seconds) : 0.0;
}

void FSM::clear_data(const std::string& key) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = records_.find(key);
    if (it != records_.end()) {
        it->second.data.clear();
        it->second.data_expires_at = 0.0;
    }
}

void FSM::reset(const std::string& key) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (key.empty()) {
        records_.clear();
    } else {
        records_.erase(key);
    }
}

size_t FSM::size() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return records_.size();
}

size_t FSM::cleanup_expired() {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time();
    size_t cleaned = 0;
    std::vector<std::string> to_remove;

    for (auto& pair : records_) {
        bool state_expired = (pair.second.state_expires_at > 0.0 && now >= pair.second.state_expires_at);
        if (state_expired) {
            pair.second.state.clear();
            pair.second.state_expires_at = 0.0;
        }

        bool data_expired = (pair.second.data_expires_at > 0.0 && now >= pair.second.data_expires_at);
        if (data_expired) {
            pair.second.data.clear();
            pair.second.data_expires_at = 0.0;
        }

        if (pair.second.state.empty() && pair.second.data.empty()) {
            to_remove.push_back(pair.first);
            cleaned++;
        }
    }

    for (const auto& k : to_remove) {
        records_.erase(k);
    }

    return cleaned;
}

} // namespace bots
} // namespace pytekt
