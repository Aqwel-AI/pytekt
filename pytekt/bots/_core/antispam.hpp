#ifndef PYTEKT_BOTS_ANTISPAM_HPP
#define PYTEKT_BOTS_ANTISPAM_HPP

#include <string>
#include <vector>
#include <mutex>
#include <chrono>
#include <cstdint>

namespace pytekt {
namespace bots {

class BloomFilter {
public:
    BloomFilter(size_t size_bits = 65536, size_t num_hashes = 4);
    void add(const std::string& item);
    bool contains(const std::string& item) const;
    void clear();

private:
    std::vector<uint64_t> bits_;
    size_t size_bits_;
    size_t num_hashes_;

    std::vector<size_t> get_hashes(const std::string& item) const;
};

class AntiSpam {
public:
    AntiSpam(size_t bloom_size = 65536, double window_seconds = 300.0);
    ~AntiSpam() = default;

    // Duplicate detection
    bool is_duplicate(const std::string& text, const std::string& user_id = "");
    void add(const std::string& text, const std::string& user_id = "");

    // Spam score calculation (0.0 = clean, 1.0 = definitely spam)
    double calculate_score(const std::string& text, double message_rate = 0.0, int duplicate_count = 0);
    bool is_spam(const std::string& text, double threshold = 0.7, double message_rate = 0.0);

    void reset();

private:
    static double current_time();
    void rotate_bloom_if_needed(double now);

    mutable std::mutex mutex_;
    size_t bloom_size_;
    double window_seconds_;
    double last_rotation_;

    BloomFilter current_bloom_;
    BloomFilter previous_bloom_;
};

} // namespace bots
} // namespace pytekt

#endif // PYTEKT_BOTS_ANTISPAM_HPP
