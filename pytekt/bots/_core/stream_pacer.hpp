#ifndef PYTEKT_BOTS_STREAM_PACER_HPP
#define PYTEKT_BOTS_STREAM_PACER_HPP

#include <string>
#include <vector>
#include <map>
#include <chrono>
#include <mutex>
#include <algorithm>

namespace pytekt {
namespace bots {

struct PacerDecision {
    bool should_flush = false;
    std::string text_with_cursor;
    std::string text_final;
    bool needs_new_message = false;
    std::string overflow_text;
    size_t flush_count = 0;
};

class StreamPacer {
public:
    StreamPacer(double min_interval = 0.75,
                double max_interval = 1.5,
                size_t min_delta_chars = 12,
                size_t max_length = 4096,
                bool adaptive = true,
                const std::string& cursor = " ▍");
    ~StreamPacer() = default;

    // Core stream operations
    PacerDecision feed(const std::string& chunk, double current_time = 0.0);
    bool should_flush(double current_time = 0.0) const;
    PacerDecision flush(double current_time = 0.0);
    std::string flush_final();

    // 429 backoff handling
    void record_429(double retry_after_seconds, double current_time = 0.0);
    double get_retry_after(double current_time = 0.0) const;
    void reset();

    // Configuration getters & setters
    void set_min_interval(double interval);
    double get_min_interval() const;
    void set_max_interval(double interval);
    double get_max_interval() const;
    void set_min_delta_chars(size_t delta);
    size_t get_min_delta_chars() const;
    void set_max_length(size_t max_len);
    size_t get_max_length() const;
    void set_cursor(const std::string& cursor);
    std::string get_cursor() const;
    void set_adaptive(bool adaptive);
    bool is_adaptive() const;

    // Buffer and statistics
    std::string get_buffer() const;
    size_t get_flush_count() const;
    std::map<std::string, double> get_metrics() const;

    // Boundary detection helper
    static bool is_semantic_boundary(const std::string& text);

private:
    static double current_time_monotonic();
    size_t find_split_point(const std::string& text, size_t limit) const;
    double calculate_dynamic_min_interval() const;

    mutable std::mutex mutex_;
    double min_interval_;
    double max_interval_;
    size_t min_delta_chars_;
    size_t max_length_;
    bool adaptive_;
    std::string cursor_;

    std::string active_text_;
    size_t last_flush_len_;
    double last_flush_time_;
    double start_time_;
    double retry_after_until_;
    size_t flush_count_;
    size_t total_chunks_;
    size_t total_chars_;
};

} // namespace bots
} // namespace pytekt

#endif // PYTEKT_BOTS_STREAM_PACER_HPP
