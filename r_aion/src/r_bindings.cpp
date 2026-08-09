// [[Rcpp::plugins(cpp14)]]
#include <Rcpp.h>
#include "../../src/native/core_kernels.hpp"

using namespace Rcpp;

//' Fast Sum of Numeric Vector
//' @param x Numeric vector
//' @export
// [[Rcpp::export]]
double aion_sum(NumericVector x) {
    if (x.size() == 0) return 0.0;
    return aion_core::fast_sum(x.begin(), static_cast<std::size_t>(x.size()));
}

//' Fast Dot Product of Two Vectors
//' @param a First numeric vector
//' @param b Second numeric vector
//' @export
// [[Rcpp::export]]
double aion_dot(NumericVector a, NumericVector b) {
    if (a.size() != b.size()) {
        stop("aion_dot: vectors must have equal length");
    }
    return aion_core::fast_dot(a.begin(), b.begin(), static_cast<std::size_t>(a.size()));
}

//' Fast L2 Norm
//' @param x Numeric vector
//' @export
// [[Rcpp::export]]
double aion_norm2(NumericVector x) {
    return aion_core::fast_norm2(x.begin(), static_cast<std::size_t>(x.size()));
}

//' Fast Mean
//' @param x Numeric vector
//' @export
// [[Rcpp::export]]
double aion_mean(NumericVector x) {
    if (x.size() == 0) stop("aion_mean: vector is empty");
    return aion_core::fast_mean(x.begin(), static_cast<std::size_t>(x.size()));
}

//' Fast Variance
//' @param x Numeric vector
//' @param ddof Delta degrees of freedom (default: 0)
//' @export
// [[Rcpp::export]]
double aion_variance(NumericVector x, int ddof = 0) {
    return aion_core::fast_variance(x.begin(), static_cast<std::size_t>(x.size()), ddof);
}

//' Fast Matrix Multiplication (Row-Major flattened matrices)
//' @param A Flattened matrix A (m x n)
//' @param B Flattened matrix B (n x p)
//' @param m Rows of A
//' @param n Columns of A / Rows of B
//' @param p Columns of B
//' @export
// [[Rcpp::export]]
NumericVector aion_matrix_multiply(NumericVector A, NumericVector B, int m, int n, int p) {
    if (A.size() != m * n || B.size() != n * p) {
        stop("aion_matrix_multiply: dimension mismatch");
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
//' @export
// [[Rcpp::export]]
NumericVector aion_prefix_sum(NumericVector x) {
    std::vector<double> res = aion_core::prefix_sum(x.begin(), static_cast<std::size_t>(x.size()));
    return wrap(res);
}

//' Fast Rolling Sum
//' @param x Numeric vector
//' @param window Window size
//' @export
// [[Rcpp::export]]
NumericVector aion_rolling_sum(NumericVector x, int window) {
    std::vector<double> res = aion_core::rolling_sum(
        x.begin(), static_cast<std::size_t>(x.size()), static_cast<std::size_t>(window)
    );
    return wrap(res);
}

//' Fast Rolling Mean
//' @param x Numeric vector
//' @param window Window size
//' @export
// [[Rcpp::export]]
NumericVector aion_rolling_mean(NumericVector x, int window) {
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
//' @export
// [[Rcpp::export]]
IntegerVector aion_histogram(NumericVector x, int bins, double lo, double hi) {
    std::vector<std::int64_t> counts = aion_core::histogram(
        x.begin(), static_cast<std::size_t>(x.size()),
        static_cast<std::size_t>(bins), lo, hi
    );
    return wrap(counts);
}
