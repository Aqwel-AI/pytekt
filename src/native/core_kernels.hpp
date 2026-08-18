/*
 * Pure C++ numerical kernels for Aqwel-Aion.
 *
 * These routines are language-agnostic and operate directly on raw double
 * pointers and standard C++ containers. Both pybind11 (Python) and Rcpp (R)
 * consume these headers.
 *
 * Author: Aqwel AI Team
 * License: Apache-2.0
 */

#pragma once

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <vector>

namespace aion_core {

// 1D Reductions

inline double fast_sum(const double* ptr, std::size_t n) {
    double s = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        s += ptr[i];
    }
    return s;
}

inline double fast_dot(const double* pa, const double* pb, std::size_t n) {
    double s = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        s += pa[i] * pb[i];
    }
    return s;
}

inline double fast_norm2(const double* ptr, std::size_t n) {
    double s = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        s += ptr[i] * ptr[i];
    }
    return std::sqrt(s);
}

inline double fast_mean(const double* ptr, std::size_t n) {
    if (n == 0) {
        throw std::invalid_argument("fast_mean: empty array");
    }
    return fast_sum(ptr, n) / static_cast<double>(n);
}

inline double fast_variance(const double* ptr, std::size_t n, int ddof = 0) {
    if (n <= static_cast<std::size_t>(ddof)) {
        throw std::invalid_argument("fast_variance: n must be > ddof");
    }
    double mean = fast_mean(ptr, n);
    double sum_sq_diff = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        double diff = ptr[i] - mean;
        sum_sq_diff += diff * diff;
    }
    return sum_sq_diff / static_cast<double>(n - ddof);
}

inline double fast_std(const double* ptr, std::size_t n, int ddof = 0) {
    return std::sqrt(fast_variance(ptr, n, ddof));
}

inline double fast_min(const double* ptr, std::size_t n) {
    if (n == 0) {
        throw std::invalid_argument("fast_min: empty array");
    }
    double m = ptr[0];
    for (std::size_t i = 1; i < n; ++i) {
        if (ptr[i] < m) m = ptr[i];
    }
    return m;
}

inline double fast_max(const double* ptr, std::size_t n) {
    if (n == 0) {
        throw std::invalid_argument("fast_max: empty array");
    }
    double m = ptr[0];
    for (std::size_t i = 1; i < n; ++i) {
        if (ptr[i] > m) m = ptr[i];
    }
    return m;
}

inline std::size_t fast_argmin(const double* ptr, std::size_t n) {
    if (n == 0) {
        throw std::invalid_argument("fast_argmin: empty array");
    }
    std::size_t best_idx = 0;
    double best_val = ptr[0];
    for (std::size_t i = 1; i < n; ++i) {
        if (ptr[i] < best_val) {
            best_val = ptr[i];
            best_idx = i;
        }
    }
    return best_idx;
}

inline std::size_t fast_argmax(const double* ptr, std::size_t n) {
    if (n == 0) {
        throw std::invalid_argument("fast_argmax: empty array");
    }
    std::size_t best_idx = 0;
    double best_val = ptr[0];
    for (std::size_t i = 1; i < n; ++i) {
        if (ptr[i] > best_val) {
            best_val = ptr[i];
            best_idx = i;
        }
    }
    return best_idx;
}

inline double fast_euclidean_distance(const double* pa, const double* pb, std::size_t n) {
    double s = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        double d = pa[i] - pb[i];
        s += d * d;
    }
    return std::sqrt(s);
}

inline double fast_cosine_similarity(const double* pa, const double* pb, std::size_t n) {
    double dot_val = fast_dot(pa, pb, n);
    double na = fast_norm2(pa, n);
    double nb = fast_norm2(pb, n);
    if (na == 0.0 || nb == 0.0) return 0.0;
    return dot_val / (na * nb);
}

// 2D Matrix Operations

inline std::vector<double> fast_matrix_multiply(
    const double* pa,
    const double* pb,
    std::size_t m,
    std::size_t n,
    std::size_t p
) {
    std::vector<double> out(m * p, 0.0);
    for (std::size_t i = 0; i < m; ++i) {
        for (std::size_t k = 0; k < n; ++k) {
            double aik = pa[i * n + k];
            for (std::size_t j = 0; j < p; ++j) {
                out[i * p + j] += aik * pb[k * p + j];
            }
        }
    }
    return out;
}

// Streaming / Window Reductions

inline std::vector<double> prefix_sum(const double* ptr, std::size_t n) {
    std::vector<double> out(n);
    double running = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        running += ptr[i];
        out[i] = running;
    }
    return out;
}

inline std::vector<double> rolling_sum(const double* ptr, std::size_t n, std::size_t window) {
    if (window == 0) {
        throw std::invalid_argument("rolling_sum: window must be > 0");
    }
    if (n == 0 || window > n) {
        return {};
    }
    std::vector<double> out(n - window + 1);
    double running = 0.0;
    for (std::size_t i = 0; i < window; ++i) {
        running += ptr[i];
    }
    out[0] = running;
    for (std::size_t i = window; i < n; ++i) {
        running += ptr[i] - ptr[i - window];
        out[i - window + 1] = running;
    }
    return out;
}

inline std::vector<double> rolling_mean(const double* ptr, std::size_t n, std::size_t window) {
    std::vector<double> sums = rolling_sum(ptr, n, window);
    double w = static_cast<double>(window);
    for (double& val : sums) {
        val /= w;
    }
    return sums;
}

inline std::vector<std::int64_t> histogram(
    const double* ptr,
    std::size_t n,
    std::size_t bins,
    double lo,
    double hi
) {
    if (bins == 0) {
        throw std::invalid_argument("histogram: bins must be > 0");
    }
    if (!(hi > lo)) {
        throw std::invalid_argument("histogram: hi must be greater than lo");
    }
    std::vector<std::int64_t> counts(bins, 0);
    const double width = (hi - lo) / static_cast<double>(bins);
    for (std::size_t i = 0; i < n; ++i) {
        const double val = ptr[i];
        if (val < lo || val > hi) continue;
        std::size_t idx = static_cast<std::size_t>((val - lo) / width);
        if (idx >= bins) idx = bins - 1;
        counts[idx]++;
    }
    return counts;
}

struct ChunkStats {
    std::vector<double> means;
    std::vector<double> mins;
    std::vector<double> maxs;
};

inline ChunkStats chunk_statistics(const double* ptr, std::size_t n, std::size_t chunk_size) {
    if (chunk_size == 0) {
        throw std::invalid_argument("chunk_statistics: chunk_size must be > 0");
    }
    if (n == 0) {
        return { {}, {}, {} };
    }
    const std::size_t chunks = (n + chunk_size - 1) / chunk_size;
    ChunkStats stats;
    stats.means.resize(chunks);
    stats.mins.resize(chunks);
    stats.maxs.resize(chunks);

    for (std::size_t c = 0; c < chunks; ++c) {
        const std::size_t start = c * chunk_size;
        const std::size_t end = std::min(start + chunk_size, n);
        double total = 0.0;
        double min_v = std::numeric_limits<double>::infinity();
        double max_v = -std::numeric_limits<double>::infinity();
        for (std::size_t i = start; i < end; ++i) {
            const double v = ptr[i];
            total += v;
            if (v < min_v) min_v = v;
            if (v > max_v) max_v = v;
        }
        const double count = static_cast<double>(end - start);
        stats.means[c] = total / count;
        stats.mins[c] = min_v;
        stats.maxs[c] = max_v;
    }
    return stats;
}

}  // namespace aion_core
