#include "antispam.hpp"
#include <algorithm>
#include <cctype>
#include <cmath>

namespace pytekt {
namespace bots {

// 64-bit FNV-1a hash helper
static uint64_t fnv1a_64(const std::string& str, uint64_t seed) {
    uint64_t hash = 0xcbf29ce484222325ULL ^ seed;
    for (char c : str) {
        hash ^= static_cast<uint64_t>(static_cast<unsigned char>(c));
        hash *= 0x100000001b3ULL;
    }
    return hash;
}

// Bloom Filter Implementation
BloomFilter::BloomFilter(size_t size_bits, size_t num_hashes)
    : size_bits_(size_bits), num_hashes_(num_hashes) {
    size_t num_words = (size_bits + 63) / 64;
    bits_.resize(num_words, 0);
}

std::vector<size_t> BloomFilter::get_hashes(const std::string& item) const {
    std::vector<size_t> hashes;
    hashes.reserve(num_hashes_);
    uint64_t h1 = fnv1a_64(item, 0x12345678ULL);
    uint64_t h2 = fnv1a_64(item, 0x9abcdef0ULL);

    for (size_t i = 0; i < num_hashes_; ++i) {
        uint64_t combined = h1 + i * h2;
        hashes.push_back(static_cast<size_t>(combined % size_bits_));
    }
    return hashes;
}

void BloomFilter::add(const std::string& item) {
    auto hashes = get_hashes(item);
    for (size_t bit_idx : hashes) {
        size_t word_idx = bit_idx / 64;
        size_t bit_offset = bit_idx % 64;
        bits_[word_idx] |= (1ULL << bit_offset);
    }
}

bool BloomFilter::contains(const std::string& item) const {
    auto hashes = get_hashes(item);
    for (size_t bit_idx : hashes) {
        size_t word_idx = bit_idx / 64;
        size_t bit_offset = bit_idx % 64;
        if (!(bits_[word_idx] & (1ULL << bit_offset))) {
            return false;
        }
    }
    return true;
}

void BloomFilter::clear() {
    std::fill(bits_.begin(), bits_.end(), 0);
}

// AntiSpam Implementation
AntiSpam::AntiSpam(size_t bloom_size, double window_seconds)
    : bloom_size_(bloom_size),
      window_seconds_(window_seconds),
      current_bloom_(bloom_size, 4),
      previous_bloom_(bloom_size, 4) {
    last_rotation_ = current_time();
}

double AntiSpam::current_time() {
    auto now = std::chrono::steady_clock::now();
    auto duration = now.time_since_epoch();
    return std::chrono::duration<double>(duration).count();
}

void AntiSpam::rotate_bloom_if_needed(double now) {
    if (now - last_rotation_ >= window_seconds_) {
        previous_bloom_ = std::move(current_bloom_);
        current_bloom_ = BloomFilter(bloom_size_, 4);
        last_rotation_ = now;
    }
}

bool AntiSpam::is_duplicate(const std::string& text, const std::string& user_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time();
    rotate_bloom_if_needed(now);

    std::string key = user_id.empty() ? text : (user_id + ":" + text);
    return current_bloom_.contains(key) || previous_bloom_.contains(key);
}

void AntiSpam::add(const std::string& text, const std::string& user_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time();
    rotate_bloom_if_needed(now);

    std::string key = user_id.empty() ? text : (user_id + ":" + text);
    current_bloom_.add(key);
}

double AntiSpam::calculate_score(const std::string& text, double message_rate, int duplicate_count) {
    double score = 0.0;

    if (text.empty()) {
        return score;
    }

    // 1. Message frequency factor
    if (message_rate > 5.0) {
        score += 0.4;
    } else if (message_rate > 2.0) {
        score += 0.2;
    }

    // 2. Duplicate count factor
    if (duplicate_count > 3) {
        score += 0.5;
    } else if (duplicate_count > 0) {
        score += 0.25;
    }

    // 3. Link count & density
    size_t link_count = 0;
    std::vector<std::string> link_markers = {
        "http://", "https://", "t.me/", "telegram.me/", "discord.gg/", "bit.ly/", "t.co/"
    };
    for (const auto& marker : link_markers) {
        size_t pos = 0;
        while ((pos = text.find(marker, pos)) != std::string::npos) {
            link_count++;
            pos += marker.length();
        }
    }
    if (link_count > 3) {
        score += 0.4;
    } else if (link_count >= 1) {
        score += 0.15 * link_count;
    }

    // 4. CAPS ratio
    size_t letters = 0;
    size_t uppercase_letters = 0;
    for (char c : text) {
        if (std::isalpha(static_cast<unsigned char>(c))) {
            letters++;
            if (std::isupper(static_cast<unsigned char>(c))) {
                uppercase_letters++;
            }
        }
    }
    if (letters >= 10) {
        double caps_ratio = static_cast<double>(uppercase_letters) / static_cast<double>(letters);
        if (caps_ratio > 0.8) {
            score += 0.3;
        } else if (caps_ratio > 0.6) {
            score += 0.15;
        }
    }

    // 5. Mention density (@username)
    size_t mention_count = 0;
    for (char c : text) {
        if (c == '@') mention_count++;
    }
    if (mention_count > 4) {
        score += 0.35;
    } else if (mention_count > 2) {
        score += 0.15;
    }

    // 6. Repetitive character runs ("aaaaaa", "!!!!!!")
    int max_run = 1;
    int cur_run = 1;
    for (size_t i = 1; i < text.size(); ++i) {
        if (text[i] == text[i - 1]) {
            cur_run++;
            max_run = std::max(max_run, cur_run);
        } else {
            cur_run = 1;
        }
    }
    if (max_run >= 8) {
        score += 0.25;
    } else if (max_run >= 5) {
        score += 0.1;
    }

    // Bound score to [0.0, 1.0]
    return std::min(1.0, std::max(0.0, score));
}

bool AntiSpam::is_spam(const std::string& text, double threshold, double message_rate) {
    int dup = is_duplicate(text) ? 1 : 0;
    double score = calculate_score(text, message_rate, dup);
    return score >= threshold;
}

void AntiSpam::reset() {
    std::lock_guard<std::mutex> lock(mutex_);
    current_bloom_.clear();
    previous_bloom_.clear();
    last_rotation_ = current_time();
}

} // namespace bots
} // namespace pytekt
