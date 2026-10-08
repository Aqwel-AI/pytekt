#include "stream_pacer.hpp"
#include <cmath>

namespace pytekt {
namespace bots {

double StreamPacer::current_time_monotonic() {
    auto now = std::chrono::steady_clock::now();
    return std::chrono::duration<double>(now.time_since_epoch()).count();
}

StreamPacer::StreamPacer(double min_interval,
                         double max_interval,
                         size_t min_delta_chars,
                         size_t max_length,
                         bool adaptive,
                         const std::string& cursor)
    : min_interval_(min_interval),
      max_interval_(max_interval),
      min_delta_chars_(min_delta_chars),
      max_length_(max_length),
      adaptive_(adaptive),
      cursor_(cursor),
      active_text_(""),
      last_flush_len_(0),
      last_flush_time_(0.0),
      start_time_(0.0),
      retry_after_until_(0.0),
      flush_count_(0),
      total_chunks_(0),
      total_chars_(0) {
    if (min_interval_ <= 0.0) min_interval_ = 0.75;
    if (max_interval_ < min_interval_) max_interval_ = min_interval_ * 2.0;
}

double StreamPacer::calculate_dynamic_min_interval() const {
    if (!adaptive_) {
        return min_interval_;
    }
    // Gently scale flush interval as message grows longer to prevent Telegram/Discord flood penalties
    // e.g. 0.75s base -> up to max_interval_ (e.g. 1.2s) after 10+ flushes
    double scale = std::min(1.0, static_cast<double>(flush_count_) / 12.0);
    double dyn = min_interval_ + scale * (max_interval_ - min_interval_) * 0.4;
    return std::min(max_interval_, dyn);
}

bool StreamPacer::is_semantic_boundary(const std::string& text) {
    if (text.empty()) return false;
    char last = text.back();
    if (last == '\n') return true;
    if (last == '.' || last == '!' || last == '?' || last == ':' || last == ';') return true;
    if (text.size() >= 2) {
        char prev = text[text.size() - 2];
        if ((prev == '.' || prev == '!' || prev == '?' || prev == ':') && (last == ' ' || last == '\t')) {
            return true;
        }
    }
    if (text.size() >= 3 && text.substr(text.size() - 3) == "```") {
        return true;
    }
    return false;
}

size_t StreamPacer::find_split_point(const std::string& text, size_t limit) const {
    if (text.size() <= limit) return text.size();
    size_t search_floor = (limit > 500) ? (limit - 500) : 0;

    // Search backwards for paragraph breaks
    size_t pos = text.rfind("\n\n", limit);
    if (pos != std::string::npos && pos >= search_floor) {
        return pos + 2;
    }

    // Search backwards for line breaks
    pos = text.rfind('\n', limit);
    if (pos != std::string::npos && pos >= search_floor) {
        return pos + 1;
    }

    // Search backwards for spaces
    pos = text.rfind(' ', limit);
    if (pos != std::string::npos && pos >= search_floor) {
        return pos + 1;
    }

    return limit;
}

PacerDecision StreamPacer::feed(const std::string& chunk, double current_time) {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = (current_time > 0.0) ? current_time : current_time_monotonic();
    if (start_time_ <= 0.0) {
        start_time_ = now;
    }

    total_chunks_++;
    total_chars_ += chunk.size();
    active_text_ += chunk;

    PacerDecision decision;
    decision.should_flush = false;

    // 1. Check if we need to split into a new message due to platform limit
    if (max_length_ > 0 && active_text_.size() >= max_length_) {
        size_t split_pos = find_split_point(active_text_, max_length_);
        std::string current_msg_final = active_text_.substr(0, split_pos);
        std::string next_text = (split_pos < active_text_.size()) ? active_text_.substr(split_pos) : "";

        decision.should_flush = true;
        decision.needs_new_message = true;
        decision.text_final = current_msg_final;
        decision.text_with_cursor = current_msg_final;
        decision.overflow_text = next_text;

        flush_count_++;
        decision.flush_count = flush_count_;
        active_text_ = next_text;
        last_flush_len_ = active_text_.size();
        last_flush_time_ = now;
        return decision;
    }

    // 2. Check 429 backoff
    if (retry_after_until_ > now) {
        return decision;
    }

    // 3. Check time interval and delta
    double dyn_interval = calculate_dynamic_min_interval();
    double elapsed = (last_flush_time_ > 0.0) ? (now - last_flush_time_) : (now - start_time_);
    size_t delta_chars = (active_text_.size() >= last_flush_len_) ? (active_text_.size() - last_flush_len_) : active_text_.size();

    bool first_flush = (flush_count_ == 0 && !active_text_.empty());
    bool interval_met = (elapsed >= dyn_interval);
    bool max_interval_met = (elapsed >= max_interval_);
    bool has_min_chars = (delta_chars >= min_delta_chars_);
    bool is_boundary = is_semantic_boundary(active_text_);

    if (first_flush || (interval_met && has_min_chars && is_boundary) || (max_interval_met && has_min_chars)) {
        decision.should_flush = true;
        decision.text_with_cursor = active_text_ + cursor_;
        decision.text_final = active_text_;
        flush_count_++;
        decision.flush_count = flush_count_;
        last_flush_len_ = active_text_.size();
        last_flush_time_ = now;
    }

    return decision;
}

bool StreamPacer::should_flush(double current_time) const {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = (current_time > 0.0) ? current_time : current_time_monotonic();
    if (retry_after_until_ > now || active_text_.empty()) return false;

    if (max_length_ > 0 && active_text_.size() >= max_length_) return true;

    double dyn_interval = calculate_dynamic_min_interval();
    double elapsed = (last_flush_time_ > 0.0) ? (now - last_flush_time_) : (now - start_time_);
    size_t delta_chars = (active_text_.size() >= last_flush_len_) ? (active_text_.size() - last_flush_len_) : active_text_.size();

    if (flush_count_ == 0 && !active_text_.empty()) return true;
    if (elapsed >= max_interval_ && delta_chars >= min_delta_chars_) return true;
    if (elapsed >= dyn_interval && delta_chars >= min_delta_chars_ && is_semantic_boundary(active_text_)) return true;

    return false;
}

PacerDecision StreamPacer::flush(double current_time) {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = (current_time > 0.0) ? current_time : current_time_monotonic();

    PacerDecision decision;
    decision.should_flush = true;
    decision.text_with_cursor = active_text_ + cursor_;
    decision.text_final = active_text_;
    flush_count_++;
    decision.flush_count = flush_count_;
    last_flush_len_ = active_text_.size();
    last_flush_time_ = now;
    return decision;
}

std::string StreamPacer::flush_final() {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time_monotonic();
    flush_count_++;
    last_flush_len_ = active_text_.size();
    last_flush_time_ = now;
    return active_text_;
}

void StreamPacer::record_429(double retry_after_seconds, double current_time) {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = (current_time > 0.0) ? current_time : current_time_monotonic();
    retry_after_until_ = now + retry_after_seconds;
    // Increase base interval slightly as a safety precaution against subsequent 429s
    min_interval_ = std::max(min_interval_, 1.0);
}

double StreamPacer::get_retry_after(double current_time) const {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = (current_time > 0.0) ? current_time : current_time_monotonic();
    if (retry_after_until_ > now) {
        return retry_after_until_ - now;
    }
    return 0.0;
}

void StreamPacer::reset() {
    std::lock_guard<std::mutex> lock(mutex_);
    active_text_.clear();
    last_flush_len_ = 0;
    last_flush_time_ = 0.0;
    start_time_ = 0.0;
    retry_after_until_ = 0.0;
    flush_count_ = 0;
    total_chunks_ = 0;
    total_chars_ = 0;
}

void StreamPacer::set_min_interval(double interval) {
    std::lock_guard<std::mutex> lock(mutex_);
    min_interval_ = interval;
}

double StreamPacer::get_min_interval() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return min_interval_;
}

void StreamPacer::set_max_interval(double interval) {
    std::lock_guard<std::mutex> lock(mutex_);
    max_interval_ = interval;
}

double StreamPacer::get_max_interval() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return max_interval_;
}

void StreamPacer::set_min_delta_chars(size_t delta) {
    std::lock_guard<std::mutex> lock(mutex_);
    min_delta_chars_ = delta;
}

size_t StreamPacer::get_min_delta_chars() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return min_delta_chars_;
}

void StreamPacer::set_max_length(size_t max_len) {
    std::lock_guard<std::mutex> lock(mutex_);
    max_length_ = max_len;
}

size_t StreamPacer::get_max_length() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return max_length_;
}

void StreamPacer::set_cursor(const std::string& cursor) {
    std::lock_guard<std::mutex> lock(mutex_);
    cursor_ = cursor;
}

std::string StreamPacer::get_cursor() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return cursor_;
}

void StreamPacer::set_adaptive(bool adaptive) {
    std::lock_guard<std::mutex> lock(mutex_);
    adaptive_ = adaptive;
}

bool StreamPacer::is_adaptive() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return adaptive_;
}

std::string StreamPacer::get_buffer() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return active_text_;
}

size_t StreamPacer::get_flush_count() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return flush_count_;
}

std::map<std::string, double> StreamPacer::get_metrics() const {
    std::lock_guard<std::mutex> lock(mutex_);
    double now = current_time_monotonic();
    double elapsed = (start_time_ > 0.0) ? (now - start_time_) : 0.0;
    double edits_avoided = (total_chunks_ > flush_count_) ? static_cast<double>(total_chunks_ - flush_count_) : 0.0;

    std::map<std::string, double> m;
    m["total_chars"] = static_cast<double>(total_chars_);
    m["total_chunks"] = static_cast<double>(total_chunks_);
    m["flush_count"] = static_cast<double>(flush_count_);
    m["edits_avoided"] = edits_avoided;
    m["elapsed_seconds"] = elapsed;
    return m;
}

} // namespace bots
} // namespace pytekt
