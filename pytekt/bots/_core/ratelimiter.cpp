#include "ratelimiter.hpp"
#include <sstream>
#include <cmath>
#include <algorithm>
#include <cctype>

namespace pytekt {
namespace bots {

RateLimiter::RateLimiter() {}

double RateLimiter::current_time() {
    auto now = std::chrono::steady_clock::now();
    auto duration = now.time_since_epoch();
    return std::chrono::duration<double>(duration).count();
}

bool RateLimiter::parse_rate(const std::string& rate_str, double& capacity, double& window_seconds) {
    if (rate_str.empty()) return false;

    // Expected format: "<count>/<duration><unit>" e.g. "5/10s", "20/60s", "100/1m", "5/s"
    size_t slash_pos = rate_str.find('/');
    if (slash_pos == std::string::npos) {
        try {
            capacity = std::stod(rate_str);
            window_seconds = 1.0;
            return true;
        } catch (...) {
            return false;
        }
    }

    std::string count_part = rate_str.substr(0, slash_pos);
    std::string dur_part = rate_str.substr(slash_pos + 1);

    try {
        capacity = std::stod(count_part);
    } catch (...) {
        return false;
    }

    if (dur_part.empty()) {
        window_seconds = 1.0;
        return true;
    }

    // Check unit suffix ('s', 'm', 'h', 'd')
    char unit = dur_part.back();
    double multiplier = 1.0;
    std::string num_part = dur_part;

    if (unit == 's' || unit == 'S') {
        multiplier = 1.0;
        num_part = dur_part.substr(0, dur_part.size() - 1);
    } else if (unit == 'm' || unit == 'M') {
        multiplier = 60.0;
        num_part = dur_part.substr(0, dur_part.size() - 1);
    } else if (unit == 'h' || unit == 'H') {
        multiplier = 3600.0;
        num_part = dur_part.substr(0, dur_part.size() - 1);
    } else if (unit == 'd' || unit == 'D') {
        multiplier = 86400.0;
        num_part = dur_part.substr(0, dur_part.size() - 1);
    }

    if (num_part.empty()) {
        window_seconds = multiplier;
        return true;
    }

    try {
        window_seconds = std::stod(num_part) * multiplier;
        if (window_seconds <= 0.0) window_seconds = 1.0;
        return true;
    } catch (...) {
        return false;
    }
}

void RateLimiter::set_rule(const std::string& scope, const std::string& rate_str) {
    double cap = 1.0, win = 1.0;
    if (parse_rate(rate_str, cap, win)) {
        set_custom_rule(scope, cap, win);
    }
}

void RateLimiter::set_custom_rule(const std::string& scope, double capacity, double window_seconds) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (capacity <= 0.0) capacity = 1.0;
    if (window_seconds <= 0.0) window_seconds = 1.0;

    RateRule rule;
    rule.capacity = capacity;
    rule.window = window_seconds;
    rule.refill_rate = capacity / window_seconds;
    default_rules_[scope] = rule;
}

void RateLimiter::refill_bucket(TokenBucket& bucket, double now) const {
    if (bucket.last_refill <= 0.0) {
        bucket.last_refill = now;
        bucket.tokens = bucket.capacity;
        return;
    }
    double elapsed = now - bucket.last_refill;
    if (elapsed > 0.0) {
        bucket.tokens = std::min(bucket.capacity, bucket.tokens + elapsed * bucket.refill_rate);
        bucket.last_refill = now;
    }
}

bool RateLimiter::acquire(const std::string& key, double tokens) {
    auto res = check(key, tokens);
    if (res.first) {
        // Deduct tokens
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = buckets_.find(key);
        if (it != buckets_.end()) {
            it->second.tokens -= tokens;
        }
        return true;
    }
    return false;
}

std::pair<bool, double> RateLimiter::check(const std::string& key, double tokens) {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time();

    // Check if key or scope is in backoff
    auto it = buckets_.find(key);
    if (it != buckets_.end()) {
        if (now < it->second.backoff_until) {
            return {false, it->second.backoff_until - now};
        }
    }

    // Determine rule to apply
    RateRule rule;
    rule.capacity = 10.0;
    rule.window = 1.0;
    rule.refill_rate = 10.0;

    // Check matching default rule
    if (key.rfind("user:", 0) == 0 && default_rules_.find("user") != default_rules_.end()) {
        rule = default_rules_["user"];
    } else if (key.rfind("chat:", 0) == 0 && default_rules_.find("chat") != default_rules_.end()) {
        rule = default_rules_["chat"];
    } else if (key == "global" && default_rules_.find("global") != default_rules_.end()) {
        rule = default_rules_["global"];
    } else {
        auto rit = default_rules_.find(key);
        if (rit != default_rules_.end()) {
            rule = rit->second;
        }
    }

    // Initialize bucket if not present
    if (it == buckets_.end()) {
        TokenBucket b;
        b.capacity = rule.capacity;
        b.refill_rate = rule.refill_rate;
        b.tokens = rule.capacity;
        b.last_refill = now;
        b.backoff_until = 0.0;
        buckets_[key] = b;
        it = buckets_.find(key);
    }

    refill_bucket(it->second, now);

    if (it->second.tokens >= tokens) {
        return {true, 0.0};
    } else {
        double needed = tokens - it->second.tokens;
        double retry_after = it->second.refill_rate > 0.0 ? (needed / it->second.refill_rate) : 1.0;
        return {false, retry_after};
    }
}

std::pair<bool, double> RateLimiter::check_and_acquire(const std::string& user_id, const std::string& chat_id, double tokens) {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time();

    std::vector<std::string> keys;
    if (!user_id.empty() && default_rules_.find("user") != default_rules_.end()) {
        keys.push_back("user:" + user_id);
    }
    if (!chat_id.empty() && default_rules_.find("chat") != default_rules_.end()) {
        keys.push_back("chat:" + chat_id);
    }
    if (default_rules_.find("global") != default_rules_.end()) {
        keys.push_back("global");
    }

    double max_retry_after = 0.0;
    bool all_allowed = true;

    // 1. Check all buckets
    for (const auto& key : keys) {
        auto it = buckets_.find(key);
        if (it != buckets_.end()) {
            if (now < it->second.backoff_until) {
                all_allowed = false;
                max_retry_after = std::max(max_retry_after, it->second.backoff_until - now);
                continue;
            }
        }

        RateRule rule;
        if (key.rfind("user:", 0) == 0) rule = default_rules_["user"];
        else if (key.rfind("chat:", 0) == 0) rule = default_rules_["chat"];
        else if (key == "global") rule = default_rules_["global"];

        if (it == buckets_.end()) {
            TokenBucket b;
            b.capacity = rule.capacity;
            b.refill_rate = rule.refill_rate;
            b.tokens = rule.capacity;
            b.last_refill = now;
            b.backoff_until = 0.0;
            buckets_[key] = b;
            it = buckets_.find(key);
        }

        refill_bucket(it->second, now);

        if (it->second.tokens < tokens) {
            all_allowed = false;
            double needed = tokens - it->second.tokens;
            double wait_time = it->second.refill_rate > 0.0 ? (needed / it->second.refill_rate) : 1.0;
            max_retry_after = std::max(max_retry_after, wait_time);
        }
    }

    // 2. If all allowed, deduct tokens from all buckets
    if (all_allowed) {
        for (const auto& key : keys) {
            buckets_[key].tokens -= tokens;
        }
        return {true, 0.0};
    }

    return {false, max_retry_after};
}

void RateLimiter::record_429(const std::string& key, double retry_after_seconds) {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time();
    double backoff_time = now + std::max(0.1, retry_after_seconds);

    std::string target_key = key.empty() ? "global" : key;
    buckets_[target_key].backoff_until = backoff_time;
}

double RateLimiter::get_retry_after(const std::string& key) const {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time();
    auto it = buckets_.find(key);
    if (it != buckets_.end()) {
        if (now < it->second.backoff_until) {
            return it->second.backoff_until - now;
        }
    }
    return 0.0;
}

void RateLimiter::reset(const std::string& key) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (key.empty()) {
        buckets_.clear();
    } else {
        buckets_.erase(key);
    }
}

size_t RateLimiter::size() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return buckets_.size();
}

} // namespace bots
} // namespace pytekt
