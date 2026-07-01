/*
 * Big-data numeric kernels for Aion's native extension.
 *
 * The goal is not to replace NumPy, but to accelerate common streaming
 * reductions used by the Python algorithms layer:
 * prefix sums, rolling windows, rolling means, and simple histograms.
 */

#pragma once

#include "array_utils.hpp"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <utility>
#include <vector>

namespace aion_native {

inline py::array_t<double> prefix_sum(py::array_t<double> arr) {
    const auto buf = require_1d_double_buffer(arr, "prefix_sum");
    const auto* in_ptr = static_cast<const double*>(buf.ptr);
    const std::size_t n = static_cast<std::size_t>(buf.shape[0]);
    auto out = make_double_array(n);
    auto out_buf = out.request();
    auto* out_ptr = static_cast<double*>(out_buf.ptr);
    double running = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        running += in_ptr[i];
        out_ptr[i] = running;
    }
    return out;
}

inline py::array_t<double> rolling_sum(py::array_t<double> arr, std::size_t window) {
    const auto buf = require_1d_double_buffer(arr, "rolling_sum");
    if (window == 0) {
        throw std::runtime_error("rolling_sum: window must be > 0");
    }
    const std::size_t n = static_cast<std::size_t>(buf.shape[0]);
    if (n == 0 || window > n) {
        return make_double_array(0);
    }
    const auto* in_ptr = static_cast<const double*>(buf.ptr);
    auto out = make_double_array(n - window + 1);
    auto out_buf = out.request();
    auto* out_ptr = static_cast<double*>(out_buf.ptr);
    double running = 0.0;
    for (std::size_t i = 0; i < window; ++i) {
        running += in_ptr[i];
    }
    out_ptr[0] = running;
    for (std::size_t i = window; i < n; ++i) {
        running += in_ptr[i];
        running -= in_ptr[i - window];
        out_ptr[i - window + 1] = running;
    }
    return out;
}

inline py::array_t<double> rolling_mean(py::array_t<double> arr, std::size_t window) {
    auto sums = rolling_sum(std::move(arr), window);
    auto buf = sums.request();
    auto* ptr = static_cast<double*>(buf.ptr);
    const std::size_t n = static_cast<std::size_t>(buf.shape[0]);
    if (window == 0) {
        throw std::runtime_error("rolling_mean: window must be > 0");
    }
    for (std::size_t i = 0; i < n; ++i) {
        ptr[i] /= static_cast<double>(window);
    }
    return sums;
}

inline py::array_t<std::int64_t> histogram(
    py::array_t<double> arr,
    std::size_t bins,
    double lo,
    double hi
) {
    const auto buf = require_1d_double_buffer(arr, "histogram");
    if (bins == 0) {
        throw std::runtime_error("histogram: bins must be > 0");
    }
    if (!(hi > lo)) {
        throw std::runtime_error("histogram: hi must be greater than lo");
    }

    const auto* in_ptr = static_cast<const double*>(buf.ptr);
    const std::size_t n = static_cast<std::size_t>(buf.shape[0]);
    auto counts = make_int64_array(bins);
    auto counts_buf = counts.request();
    auto* out = static_cast<std::int64_t*>(counts_buf.ptr);
    const double width = (hi - lo) / static_cast<double>(bins);
    for (std::size_t i = 0; i < n; ++i) {
        const double value = in_ptr[i];
        if (value < lo || value > hi) {
            continue;
        }
        std::size_t index = static_cast<std::size_t>((value - lo) / width);
        if (index >= bins) {
            index = bins - 1;
        }
        ++out[index];
    }
    return counts;
}

inline py::dict chunk_statistics(py::array_t<double> arr, std::size_t chunk_size) {
    const auto buf = require_1d_double_buffer(arr, "chunk_statistics");
    if (chunk_size == 0) {
        throw std::runtime_error("chunk_statistics: chunk_size must be > 0");
    }
    const auto* in_ptr = static_cast<const double*>(buf.ptr);
    const std::size_t n = static_cast<std::size_t>(buf.shape[0]);
    const std::size_t chunks = (n + chunk_size - 1) / chunk_size;
    auto means = make_double_array(chunks);
    auto mins = make_double_array(chunks);
    auto maxs = make_double_array(chunks);
    auto means_buf = means.request();
    auto mins_buf = mins.request();
    auto maxs_buf = maxs.request();
    auto* mean_ptr = static_cast<double*>(means_buf.ptr);
    auto* min_ptr = static_cast<double*>(mins_buf.ptr);
    auto* max_ptr = static_cast<double*>(maxs_buf.ptr);

    for (std::size_t c = 0; c < chunks; ++c) {
        const std::size_t start = c * chunk_size;
        const std::size_t end = std::min(start + chunk_size, n);
        double total = 0.0;
        double min_v = std::numeric_limits<double>::infinity();
        double max_v = -std::numeric_limits<double>::infinity();
        for (std::size_t i = start; i < end; ++i) {
            const double value = in_ptr[i];
            total += value;
            if (value < min_v) {
                min_v = value;
            }
            if (value > max_v) {
                max_v = value;
            }
        }
        const double count = static_cast<double>(end - start);
        mean_ptr[c] = count > 0.0 ? total / count : 0.0;
        min_ptr[c] = count > 0.0 ? min_v : 0.0;
        max_ptr[c] = count > 0.0 ? max_v : 0.0;
    }

    py::dict result;
    result["mean"] = means;
    result["min"] = mins;
    result["max"] = maxs;
    result["chunk_size"] = static_cast<std::int64_t>(chunk_size);
    return result;
}

}  // namespace aion_native
