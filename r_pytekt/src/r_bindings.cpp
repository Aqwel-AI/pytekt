// [[Rcpp::plugins(cpp14)]]
#include <Rcpp.h>
#include "core_kernels.h"

using namespace Rcpp;

//' Fast Sum of Numeric Vector
//' @param x Numeric vector
//' @return Sum of the vector elements
//' @examples
//' pytekt_sum(c(1.0, 2.0, 3.0, 4.0))
//' @export
// [[Rcpp::export]]
double pytekt_sum(NumericVector x) {
    if (x.size() == 0) return 0.0;
    return aion_core::fast_sum(x.begin(), static_cast<std::size_t>(x.size()));
}

//' Fast Mean
//' @param x Numeric vector
//' @return Arithmetic mean of vector elements
//' @examples
//' pytekt_mean(c(1.0, 2.0, 3.0, 4.0))
//' @export
// [[Rcpp::export]]
double pytekt_mean(NumericVector x) {
    if (x.size() == 0) stop("pytekt_mean: vector is empty");
    return aion_core::fast_mean(x.begin(), static_cast<std::size_t>(x.size()));
}

//' Fast Variance
//' @param x Numeric vector
//' @param ddof Delta degrees of freedom (default: 0)
//' @return Variance of the vector
//' @examples
//' pytekt_variance(c(1.0, 2.0, 3.0, 4.0), ddof = 1)
//' @export
// [[Rcpp::export]]
double pytekt_variance(NumericVector x, int ddof = 0) {
    if (x.size() <= ddof) stop("pytekt_variance: length must be > ddof");
    return aion_core::fast_variance(x.begin(), static_cast<std::size_t>(x.size()), ddof);
}

//' Fast Standard Deviation
//' @param x Numeric vector
//' @param ddof Delta degrees of freedom (default: 0)
//' @return Standard deviation of the vector
//' @examples
//' pytekt_std(c(1.0, 2.0, 3.0, 4.0), ddof = 1)
//' @export
// [[Rcpp::export]]
double pytekt_std(NumericVector x, int ddof = 0) {
    if (x.size() <= ddof) stop("pytekt_std: length must be > ddof");
    return aion_core::fast_std(x.begin(), static_cast<std::size_t>(x.size()), ddof);
}

//' Fast Minimum
//' @param x Numeric vector
//' @return Minimum value in vector
//' @examples
//' pytekt_min(c(4.0, 1.0, 8.0, 2.0))
//' @export
// [[Rcpp::export]]
double pytekt_min(NumericVector x) {
    if (x.size() == 0) stop("pytekt_min: vector is empty");
    return aion_core::fast_min(x.begin(), static_cast<std::size_t>(x.size()));
}

//' Fast Maximum
//' @param x Numeric vector
//' @return Maximum value in vector
//' @examples
//' pytekt_max(c(4.0, 1.0, 8.0, 2.0))
//' @export
// [[Rcpp::export]]
double pytekt_max(NumericVector x) {
    if (x.size() == 0) stop("pytekt_max: vector is empty");
    return aion_core::fast_max(x.begin(), static_cast<std::size_t>(x.size()));
}

//' Fast Argmin (1-indexed)
//' @param x Numeric vector
//' @return 1-based index of minimum element
//' @examples
//' pytekt_argmin(c(4.0, 1.0, 8.0, 2.0))
//' @export
// [[Rcpp::export]]
int pytekt_argmin(NumericVector x) {
    if (x.size() == 0) stop("pytekt_argmin: vector is empty");
    return static_cast<int>(aion_core::fast_argmin(x.begin(), static_cast<std::size_t>(x.size())) + 1);
}

//' Fast Argmax (1-indexed)
//' @param x Numeric vector
//' @return 1-based index of maximum element
//' @examples
//' pytekt_argmax(c(4.0, 1.0, 8.0, 2.0))
//' @export
// [[Rcpp::export]]
int pytekt_argmax(NumericVector x) {
    if (x.size() == 0) stop("pytekt_argmax: vector is empty");
    return static_cast<int>(aion_core::fast_argmax(x.begin(), static_cast<std::size_t>(x.size())) + 1);
}

//' Fast Dot Product of Two Vectors
//' @param a First numeric vector
//' @param b Second numeric vector
//' @return Inner dot product
//' @examples
//' pytekt_dot(c(1.0, 2.0), c(3.0, 4.0))
//' @export
// [[Rcpp::export]]
double pytekt_dot(NumericVector a, NumericVector b) {
    if (a.size() != b.size()) {
        stop("pytekt_dot: vectors must have equal length");
    }
    return aion_core::fast_dot(a.begin(), b.begin(), static_cast<std::size_t>(a.size()));
}

//' Fast L2 Norm
//' @param x Numeric vector
//' @return Euclidean L2 norm
//' @examples
//' pytekt_norm2(c(3.0, 4.0))
//' @export
// [[Rcpp::export]]
double pytekt_norm2(NumericVector x) {
    return aion_core::fast_norm2(x.begin(), static_cast<std::size_t>(x.size()));
}

//' Fast Euclidean Distance
//' @param a First numeric vector
//' @param b Second numeric vector
//' @return Euclidean distance between a and b
//' @examples
//' pytekt_euclidean_distance(c(0.0, 0.0), c(3.0, 4.0))
//' @export
// [[Rcpp::export]]
double pytekt_euclidean_distance(NumericVector a, NumericVector b) {
    if (a.size() != b.size()) {
        stop("pytekt_euclidean_distance: vectors must have equal length");
    }
    return aion_core::fast_euclidean_distance(a.begin(), b.begin(), static_cast<std::size_t>(a.size()));
}

//' Fast Cosine Similarity
//' @param a First numeric vector
//' @param b Second numeric vector
//' @return Cosine similarity in range [-1, 1]
//' @examples
//' pytekt_cosine_similarity(c(1.0, 0.0), c(1.0, 1.0))
//' @export
// [[Rcpp::export]]
double pytekt_cosine_similarity(NumericVector a, NumericVector b) {
    if (a.size() != b.size()) {
        stop("pytekt_cosine_similarity: vectors must have equal length");
    }
    return aion_core::fast_cosine_similarity(a.begin(), b.begin(), static_cast<std::size_t>(a.size()));
}

//' Fast Matrix Multiplication (Row-Major flattened matrices)
//' @param A Flattened matrix A (m x n)
//' @param B Flattened matrix B (n x p)
//' @param m Rows of A
//' @param n Columns of A / Rows of B
//' @param p Columns of B
//' @return Flattened product matrix (m x p)
//' @examples
//' pytekt_matrix_multiply(c(1, 2, 3, 4), c(5, 6, 7, 8), 2, 2, 2)
//' @export
// [[Rcpp::export]]
NumericVector pytekt_matrix_multiply(NumericVector A, NumericVector B, int m, int n, int p) {
    if (A.size() != m * n || B.size() != n * p) {
        stop("pytekt_matrix_multiply: dimension mismatch");
    }
    std::vector<double> res = aion_core::fast_matrix_multiply(
        A.begin(), B.begin(),
        static_cast<std::size_t>(m),
        static_cast<std::size_t>(n),
        static_cast<std::size_t>(p)
    );
    return wrap(res);
}

//' Fast Cumulative Prefix Sum
//' @param x Numeric vector
//' @return Cumulative prefix sum vector
//' @examples
//' pytekt_prefix_sum(c(1.0, 2.0, 3.0, 4.0))
//' @export
// [[Rcpp::export]]
NumericVector pytekt_prefix_sum(NumericVector x) {
    std::vector<double> res = aion_core::prefix_sum(x.begin(), static_cast<std::size_t>(x.size()));
    return wrap(res);
}

//' Fast Rolling Sum
//' @param x Numeric vector
//' @param window Window size
//' @return Rolling sums
//' @examples
//' pytekt_rolling_sum(c(1.0, 2.0, 3.0, 4.0, 5.0), window = 3)
//' @export
// [[Rcpp::export]]
NumericVector pytekt_rolling_sum(NumericVector x, int window) {
    if (window <= 0) stop("pytekt_rolling_sum: window must be > 0");
    std::vector<double> res = aion_core::rolling_sum(
        x.begin(), static_cast<std::size_t>(x.size()), static_cast<std::size_t>(window)
    );
    return wrap(res);
}

//' Fast Rolling Mean
//' @param x Numeric vector
//' @param window Window size
//' @return Rolling means
//' @examples
//' pytekt_rolling_mean(c(1.0, 2.0, 3.0, 4.0, 5.0), window = 3)
//' @export
// [[Rcpp::export]]
NumericVector pytekt_rolling_mean(NumericVector x, int window) {
    if (window <= 0) stop("pytekt_rolling_mean: window must be > 0");
    std::vector<double> res = aion_core::rolling_mean(
        x.begin(), static_cast<std::size_t>(x.size()), static_cast<std::size_t>(window)
    );
    return wrap(res);
}

//' Fast Streaming Histogram
//' @param x Numeric vector
//' @param bins Number of bins
//' @param lo Lower bound
//' @param hi Upper bound
//' @return Integer bin counts
//' @examples
//' pytekt_histogram(c(1.0, 2.0, 3.0, 4.0, 5.0), bins = 5, lo = 1.0, hi = 5.0)
//' @export
// [[Rcpp::export]]
IntegerVector pytekt_histogram(NumericVector x, int bins, double lo, double hi) {
    if (bins <= 0) stop("pytekt_histogram: bins must be > 0");
    if (!(hi > lo)) stop("pytekt_histogram: hi must be greater than lo");
    std::vector<std::int64_t> counts = aion_core::histogram(
        x.begin(), static_cast<std::size_t>(x.size()),
        static_cast<std::size_t>(bins), lo, hi
    );
    return wrap(counts);
}

//' Fast Chunk Statistics
//' @param x Numeric vector
//' @param chunk_size Size of each chunk
//' @return A list with `mean`, `min`, `max`, and `chunk_size`
//' @examples
//' pytekt_chunk_statistics(c(1.0, 2.0, 3.0, 4.0, 5.0, 6.0), chunk_size = 2)
//' @export
// [[Rcpp::export]]
List pytekt_chunk_statistics(NumericVector x, int chunk_size) {
    if (chunk_size <= 0) stop("pytekt_chunk_statistics: chunk_size must be > 0");
    aion_core::ChunkStats stats = aion_core::chunk_statistics(
        x.begin(), static_cast<std::size_t>(x.size()), static_cast<std::size_t>(chunk_size)
    );
    return List::create(
        Named("mean") = wrap(stats.means),
        Named("min") = wrap(stats.mins),
        Named("max") = wrap(stats.maxs),
        Named("chunk_size") = chunk_size
    );
}
