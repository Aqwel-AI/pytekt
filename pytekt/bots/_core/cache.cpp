#include "cache.hpp"

namespace pytekt {
namespace bots {

Cache::Cache() {}

double Cache::current_time() {
    auto now = std::chrono::steady_clock::now();
    auto duration = now.time_since_epoch();
    return std::chrono::duration<double>(duration).count();
}

void Cache::set(const std::string& key, const std::string& value, double ttl_seconds) {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time();
    CacheEntry entry;
    entry.value = value;
    entry.expires_at = (ttl_seconds > 0.0) ? (now + ttl_seconds) : 0.0;
    entries_[key] = entry;
}

std::string Cache::get(const std::string& key) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = entries_.find(key);
    if (it == entries_.end()) return "";

    double now = current_time();
    if (it->second.expires_at > 0.0 && now >= it->second.expires_at) {
        entries_.erase(it);
        return "";
    }
    return it->second.value;
}

bool Cache::has(const std::string& key) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = entries_.find(key);
    if (it == entries_.end()) return false;

    double now = current_time();
    if (it->second.expires_at > 0.0 && now >= it->second.expires_at) {
        entries_.erase(it);
        return false;
    }
    return true;
}

bool Cache::delete_key(const std::string& key) {
    std::lock_guard<std::mutex> lock(mutex_);
    return entries_.erase(key) > 0;
}

void Cache::clear() {
    std::lock_guard<std::mutex> lock(mutex_);
    entries_.clear();
}

size_t Cache::size() {
    cleanup_expired();
    std::lock_guard<std::mutex> lock(mutex_);
    return entries_.size();
}

size_t Cache::cleanup_expired() {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time();
    size_t cleaned = 0;
    std::vector<std::string> to_remove;

    for (const auto& pair : entries_) {
        if (pair.second.expires_at > 0.0 && now >= pair.second.expires_at) {
            to_remove.push_back(pair.first);
            cleaned++;
        }
    }

    for (const auto& k : to_remove) {
        entries_.erase(k);
    }

    return cleaned;
}

std::vector<std::string> Cache::keys() {
    cleanup_expired();
    std::lock_guard<std::mutex> lock(mutex_);
    std::vector<std::string> result;
    result.reserve(entries_.size());
    for (const auto& pair : entries_) {
        result.push_back(pair.first);
    }
    return result;
}

} // namespace bots
} // namespace pytekt
