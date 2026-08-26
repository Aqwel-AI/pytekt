#ifndef PYTEKT_BOTS_CACHE_HPP
#define PYTEKT_BOTS_CACHE_HPP

#include <string>
#include <unordered_map>
#include <vector>
#include <mutex>
#include <chrono>

namespace pytekt {
namespace bots {

struct CacheEntry {
    std::string value;
    double expires_at = 0.0; // 0.0 means never expires
};

class Cache {
public:
    Cache();
    ~Cache() = default;

    void set(const std::string& key, const std::string& value, double ttl_seconds = 0.0);
    std::string get(const std::string& key);
    bool has(const std::string& key);
    bool delete_key(const std::string& key);
    void clear();
    size_t size();
    size_t cleanup_expired();
    std::vector<std::string> keys();

private:
    static double current_time();

    mutable std::mutex mutex_;
    std::unordered_map<std::string, CacheEntry> entries_;
};

} // namespace bots
} // namespace pytekt

#endif // PYTEKT_BOTS_CACHE_HPP
