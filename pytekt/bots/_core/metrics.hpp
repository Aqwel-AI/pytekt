#ifndef PYTEKT_BOTS_METRICS_HPP
#define PYTEKT_BOTS_METRICS_HPP

#include <string>
#include <vector>
#include <map>
#include <mutex>

namespace pytekt {
namespace bots {

struct HistogramBucket {
    double upper_bound;
    uint64_t count = 0;
};

struct HistogramData {
    std::vector<HistogramBucket> buckets;
    double sum = 0.0;
    uint64_t count = 0;
};

class Metrics {
public:
    Metrics();
    ~Metrics() = default;

    void increment_counter(const std::string& name, double value = 1.0, const std::map<std::string, std::string>& labels = {});
    void observe(const std::string& name, double value, const std::map<std::string, std::string>& labels = {});
    void record_latency(const std::string& command_name, double duration_seconds);

    std::string export_prometheus() const;
    void reset();

private:
    std::string format_metric_key(const std::string& name, const std::map<std::string, std::string>& labels) const;

    mutable std::mutex mutex_;
    std::map<std::string, double> counters_;
    std::map<std::string, HistogramData> histograms_;
    std::vector<double> default_buckets_ = {0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0};
};

} // namespace bots
} // namespace pytekt

#endif // PYTEKT_BOTS_METRICS_HPP
