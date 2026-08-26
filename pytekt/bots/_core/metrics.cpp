#include "metrics.hpp"
#include <sstream>
#include <iomanip>

namespace pytekt {
namespace bots {

Metrics::Metrics() {}

std::string Metrics::format_metric_key(const std::string& name, const std::map<std::string, std::string>& labels) const {
    if (labels.empty()) return name;
    std::ostringstream ss;
    ss << name << "{";
    bool first = true;
    for (const auto& kv : labels) {
        if (!first) ss << ",";
        first = false;
        ss << kv.first << "=\"" << kv.second << "\"";
    }
    ss << "}";
    return ss.str();
}

void Metrics::increment_counter(const std::string& name, double value, const std::map<std::string, std::string>& labels) {
    std::lock_guard<std::mutex> lock(mutex_);
    std::string key = format_metric_key(name, labels);
    counters_[key] += value;
}

void Metrics::observe(const std::string& name, double value, const std::map<std::string, std::string>& labels) {
    std::lock_guard<std::mutex> lock(mutex_);
    std::string key = format_metric_key(name, labels);
    auto it = histograms_.find(key);
    if (it == histograms_.end()) {
        HistogramData hd;
        for (double b : default_buckets_) {
            HistogramBucket hb;
            hb.upper_bound = b;
            hb.count = 0;
            hd.buckets.push_back(hb);
        }
        histograms_[key] = hd;
        it = histograms_.find(key);
    }

    auto& hd = it->second;
    hd.count++;
    hd.sum += value;
    for (auto& bucket : hd.buckets) {
        if (value <= bucket.upper_bound) {
            bucket.count++;
        }
    }
}

void Metrics::record_latency(const std::string& command_name, double duration_seconds) {
    std::map<std::string, std::string> labels = {{"command", command_name}};
    observe("bot_command_latency_seconds", duration_seconds, labels);
    increment_counter("bot_command_calls_total", 1.0, labels);
}

std::string Metrics::export_prometheus() const {
    std::lock_guard<std::mutex> lock(mutex_);
    std::ostringstream ss;

    // Export counters
    for (const auto& pair : counters_) {
        ss << pair.first << " " << pair.second << "\n";
    }

    // Export histograms
    for (const auto& pair : histograms_) {
        const std::string& key = pair.first;
        const auto& hd = pair.second;

        // Parse base name and labels if present
        std::string base_name = key;
        std::string label_str = "";
        size_t brace_pos = key.find('{');
        if (brace_pos != std::string::npos) {
            base_name = key.substr(0, brace_pos);
            label_str = key.substr(brace_pos + 1, key.size() - brace_pos - 2); // remove '{' and '}'
        }

        uint64_t cumulative = 0;
        for (const auto& b : hd.buckets) {
            cumulative = b.count;
            ss << base_name << "_bucket{";
            if (!label_str.empty()) ss << label_str << ",";
            ss << "le=\"" << b.upper_bound << "\"} " << cumulative << "\n";
        }
        ss << base_name << "_bucket{";
        if (!label_str.empty()) ss << label_str << ",";
        ss << "le=\"+Inf\"} " << hd.count << "\n";

        ss << base_name << "_sum{";
        if (!label_str.empty()) ss << label_str;
        ss << "} " << hd.sum << "\n";

        ss << base_name << "_count{";
        if (!label_str.empty()) ss << label_str;
        ss << "} " << hd.count << "\n";
    }

    return ss.str();
}

void Metrics::reset() {
    std::lock_guard<std::mutex> lock(mutex_);
    counters_.clear();
    histograms_.clear();
}

} // namespace bots
} // namespace pytekt
