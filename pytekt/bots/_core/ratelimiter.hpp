#ifndef PYTEKT_BOTS_RATELIMITER_HPP
#define PYTEKT_BOTS_RATELIMITER_HPP

#include <string>
#include <unordered_map>
#include <mutex>
#include <chrono>
#include <utility>

namespace pytekt {
namespace bots {

struct RateRule {
    double capacity = 1.0;
    double refill_rate = 1.0; // tokens per second
    double window = 1.0;      // seconds
};

struct TokenBucket {
    double tokens = 1.0;
    double capacity = 1.0;
    double refill_rate = 1.0;
    double last_refill = 0.0;
    double backoff_until = 0.0;
};

class RateLimiter {
public:
    RateLimiter();
    ~RateLimiter() = default;

    // Rule configuration
    void set_rule(const std::string& scope, const std::string& rate_str);
    void set_custom_rule(const std::string& scope, double capacity, double window_seconds);

    // Core acquire and check
    bool acquire(const std::string& key, double tokens = 1.0);
    std::pair<bool, double> check(const std::string& key, double tokens = 1.0);

    // Atomic multi-scope check (user, chat, global)
    std::pair<bool, double> check_and_acquire(const std::string& user_id, const std::string& chat_id, double tokens = 1.0);

    // 429 auto backoff handling
    void record_429(const std::string& key, double retry_after_seconds);
    double get_retry_after(const std::string& key) const;

    // Maintenance
    void reset(const std::string& key = "");
    size_t size() const;

    // Rate string parser helper: "5/10s", "20/60s", "10/1m", "100/1h"
    static bool parse_rate(const std::string& rate_str, double& capacity, double& window_seconds);

private:
    static double current_time();
    void refill_bucket(TokenBucket& bucket, double now) const;

    mutable std::mutex mutex_;
    std::unordered_map<std::string, RateRule> default_rules_; // e.g. "user", "chat", "global"
    std::unordered_map<std::string, TokenBucket> buckets_;
};

} // namespace bots
} // namespace pytekt

#endif // PYTEKT_BOTS_RATELIMITER_HPP
