/*
 * PyTekt - C++ extension for fast numerical operations
 *
 * Optional native module: if built, pytekt._core uses these for speed.
 * Requires pybind11 and a C++14 compiler at build time.
 *
 * Author: Aqwel AI Team
 * License: Apache-2.0
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "native/core_kernels.hpp"
#include <cmath>
#include <algorithm>
#include <limits>

namespace py = pybind11;

// ---- 1D reductions (contiguous double) ----

double fast_sum(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_sum: expected 1D array");
    }
    return aion_core::fast_sum(static_cast<const double*>(buf.ptr), buf.shape[0]);
}

double fast_dot(py::array_t<double> a, py::array_t<double> b) {
    py::buffer_info ba = a.request(), bb = b.request();
    if (ba.ndim != 1 || bb.ndim != 1) {
        throw std::runtime_error("fast_dot: expected 1D arrays");
    }
    const size_t n = ba.shape[0];
    if (bb.shape[0] != n) {
        throw std::runtime_error("fast_dot: shape mismatch");
    }
    return aion_core::fast_dot(
        static_cast<const double*>(ba.ptr),
        static_cast<const double*>(bb.ptr),
        n
    );
}

double fast_norm2(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_norm2: expected 1D array");
    }
    return aion_core::fast_norm2(static_cast<const double*>(buf.ptr), buf.shape[0]);
}

double fast_mean(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_mean: expected 1D array");
    }
    const size_t n = buf.shape[0];
    if (n == 0) {
        throw std::runtime_error("fast_mean: empty array");
    }
    return aion_core::fast_mean(static_cast<const double*>(buf.ptr), n);
}

double fast_variance(py::array_t<double> arr, int ddof) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_variance: expected 1D array");
    }
    const size_t n = buf.shape[0];
    if (n <= static_cast<size_t>(ddof)) {
        throw std::runtime_error("fast_variance: n must be > ddof");
    }
    return aion_core::fast_variance(static_cast<const double*>(buf.ptr), n, ddof);
}

// ---- 1D index ----

int64_t fast_argmax(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_argmax: expected 1D array");
    }
    const size_t n = buf.shape[0];
    if (n == 0) {
        throw std::runtime_error("fast_argmax: empty array");
    }
    const double* ptr = static_cast<const double*>(buf.ptr);
    size_t best = 0;
    double best_val = ptr[0];
    for (size_t i = 1; i < n; ++i) {
        if (ptr[i] > best_val) {
            best_val = ptr[i];
            best = i;
        }
    }
    return static_cast<int64_t>(best);
}

int64_t fast_argmin(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_argmin: expected 1D array");
    }
    const size_t n = buf.shape[0];
    if (n == 0) {
        throw std::runtime_error("fast_argmin: empty array");
    }
    const double* ptr = static_cast<const double*>(buf.ptr);
    size_t best = 0;
    double best_val = ptr[0];
    for (size_t i = 1; i < n; ++i) {
        if (ptr[i] < best_val) {
            best_val = ptr[i];
            best = i;
        }
    }
    return static_cast<int64_t>(best);
}

double fast_min(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_min: expected 1D array");
    }
    const size_t n = buf.shape[0];
    if (n == 0) {
        throw std::runtime_error("fast_min: empty array");
    }
    const double* ptr = static_cast<const double*>(buf.ptr);
    double m = ptr[0];
    for (size_t i = 1; i < n; ++i) {
        if (ptr[i] < m) m = ptr[i];
    }
    return m;
}

double fast_max(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_max: expected 1D array");
    }
    const size_t n = buf.shape[0];
    if (n == 0) {
        throw std::runtime_error("fast_max: empty array");
    }
    const double* ptr = static_cast<const double*>(buf.ptr);
    double m = ptr[0];
    for (size_t i = 1; i < n; ++i) {
        if (ptr[i] > m) m = ptr[i];
    }
    return m;
}

double fast_norm1(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_norm1: expected 1D array");
    }
    const double* ptr = static_cast<const double*>(buf.ptr);
    const size_t n = buf.shape[0];
    double s = 0.0;
    for (size_t i = 0; i < n; ++i) {
        s += std::fabs(ptr[i]);
    }
    return s;
}

// ---- 1D element-wise (return new array) ----

py::array_t<double> fast_relu(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_relu: expected 1D array");
    }
    const size_t n = buf.shape[0];
    const double* in_ptr = static_cast<const double*>(buf.ptr);
    auto out = py::array_t<double>(n);
    py::buffer_info obuf = out.request();
    double* out_ptr = static_cast<double*>(obuf.ptr);
    for (size_t i = 0; i < n; ++i) {
        out_ptr[i] = in_ptr[i] > 0.0 ? in_ptr[i] : 0.0;
    }
    return out;
}

py::array_t<double> fast_softmax(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_softmax: expected 1D array");
    }
    const size_t n = buf.shape[0];
    if (n == 0) {
        throw std::runtime_error("fast_softmax: empty array");
    }
    const double* in_ptr = static_cast<const double*>(buf.ptr);
    double max_val = in_ptr[0];
    for (size_t i = 1; i < n; ++i) {
        if (in_ptr[i] > max_val) max_val = in_ptr[i];
    }
    auto out = py::array_t<double>(n);
    double* out_ptr = static_cast<double*>(out.request().ptr);
    double sum = 0.0;
    for (size_t i = 0; i < n; ++i) {
        out_ptr[i] = std::exp(in_ptr[i] - max_val);
        sum += out_ptr[i];
    }
    for (size_t i = 0; i < n; ++i) {
        out_ptr[i] /= sum;
    }
    return out;
}

py::array_t<double> fast_cumsum(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_cumsum: expected 1D array");
    }
    const size_t n = buf.shape[0];
    const double* in_ptr = static_cast<const double*>(buf.ptr);
    auto out = py::array_t<double>(n);
    double* out_ptr = static_cast<double*>(out.request().ptr);
    double s = 0.0;
    for (size_t i = 0; i < n; ++i) {
        s += in_ptr[i];
        out_ptr[i] = s;
    }
    return out;
}

namespace {
inline double stable_sigmoid(double x) {
    if (x >= 0.0) {
        return 1.0 / (1.0 + std::exp(-x));
    }
    double z = std::exp(x);
    return z / (1.0 + z);
}
}  // namespace

py::array_t<double> fast_sigmoid(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_sigmoid: expected 1D array");
    }
    const size_t n = buf.shape[0];
    const double* in_ptr = static_cast<const double*>(buf.ptr);
    auto out = py::array_t<double>(n);
    double* out_ptr = static_cast<double*>(out.request().ptr);
    for (size_t i = 0; i < n; ++i) {
        out_ptr[i] = stable_sigmoid(in_ptr[i]);
    }
    return out;
}

py::array_t<double> fast_tanh(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_tanh: expected 1D array");
    }
    const size_t n = buf.shape[0];
    const double* in_ptr = static_cast<const double*>(buf.ptr);
    auto out = py::array_t<double>(n);
    double* out_ptr = static_cast<double*>(out.request().ptr);
    for (size_t i = 0; i < n; ++i) {
        out_ptr[i] = std::tanh(in_ptr[i]);
    }
    return out;
}

py::array_t<double> fast_clip(py::array_t<double> arr, double lo, double hi) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_clip: expected 1D array");
    }
    if (lo > hi) {
        throw std::runtime_error("fast_clip: lo must be <= hi");
    }
    const size_t n = buf.shape[0];
    const double* in_ptr = static_cast<const double*>(buf.ptr);
    auto out = py::array_t<double>(n);
    double* out_ptr = static_cast<double*>(out.request().ptr);
    for (size_t i = 0; i < n; ++i) {
        double v = in_ptr[i];
        if (v < lo) {
            out_ptr[i] = lo;
        } else if (v > hi) {
            out_ptr[i] = hi;
        } else {
            out_ptr[i] = v;
        }
    }
    return out;
}

// ---- Matrix-vector: (M, N) @ (N,) -> (M,) ----

py::array_t<double> fast_matrix_vector_mul(py::array_t<double> mat, py::array_t<double> vec) {
    py::buffer_info bm = mat.request(), bv = vec.request();
    if (bm.ndim != 2 || bv.ndim != 1) {
        throw std::runtime_error("fast_matrix_vector_mul: expected 2D matrix and 1D vector");
    }
    const size_t M = bm.shape[0];
    const size_t N = bm.shape[1];
    if (bv.shape[0] != N) {
        throw std::runtime_error("fast_matrix_vector_mul: matrix cols != vector size");
    }
    const double* m_ptr = static_cast<const double*>(bm.ptr);
    const double* v_ptr = static_cast<const double*>(bv.ptr);
    auto out = py::array_t<double>(M);
    double* out_ptr = static_cast<double*>(out.request().ptr);
    for (size_t i = 0; i < M; ++i) {
        double s = 0.0;
        for (size_t j = 0; j < N; ++j) {
            s += m_ptr[i * N + j] * v_ptr[j];
        }
        out_ptr[i] = s;
    }
    return out;
}

// ---- Binary search: lower_bound style (first index where arr[i] >= value) ----

int64_t fast_lower_bound(py::array_t<double> arr, double value) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_lower_bound: expected 1D array");
    }
    const double* ptr = static_cast<const double*>(buf.ptr);
    const size_t n = buf.shape[0];
    size_t lo = 0, hi = n;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (ptr[mid] < value) {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    return static_cast<int64_t>(lo);
}

int64_t fast_upper_bound(py::array_t<double> arr, double value) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error("fast_upper_bound: expected 1D array");
    }
    const double* ptr = static_cast<const double*>(buf.ptr);
    const size_t n = buf.shape[0];
    size_t lo = 0, hi = n;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (ptr[mid] <= value) {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    return static_cast<int64_t>(lo);
}

PYBIND11_MODULE(_pytekt_core, m) {
    m.def("fast_sum", &fast_sum,
          "Sum of a 1D float64 array.");
    m.def("fast_dot", &fast_dot,
          "Dot product of two 1D float64 arrays.");
    m.def("fast_norm2", &fast_norm2,
          "L2 norm of a 1D float64 array.");
    m.def("fast_mean", &fast_mean,
          "Mean of a 1D float64 array.");
    m.def("fast_variance", &fast_variance,
          py::arg("arr"), py::arg("ddof") = 0,
          "Variance of a 1D float64 array (ddof=0 population, ddof=1 sample).");
    m.def("fast_argmax", &fast_argmax,
          "Index of maximum value in a 1D float64 array.");
    m.def("fast_argmin", &fast_argmin,
          "Index of minimum value in a 1D float64 array.");
    m.def("fast_min", &fast_min,
          "Minimum value in a 1D float64 array.");
    m.def("fast_max", &fast_max,
          "Maximum value in a 1D float64 array.");
    m.def("fast_norm1", &fast_norm1,
          "L1 norm (sum of absolute values) of a 1D float64 array.");
    m.def("fast_relu", &fast_relu,
          "ReLU(x) = max(0, x) element-wise; returns new 1D array.");
    m.def("fast_softmax", &fast_softmax,
          "Numerically stable softmax over 1D float64 array; returns new array.");
    m.def("fast_sigmoid", &fast_sigmoid,
          "Sigmoid 1 / (1 + exp(-x)) element-wise; numerically stable; returns new array.");
    m.def("fast_tanh", &fast_tanh,
          "Hyperbolic tangent element-wise; returns new array.");
    m.def("fast_clip", &fast_clip,
          py::arg("arr"), py::arg("lo"), py::arg("hi"),
          "Clamp each element to [lo, hi]; returns new array.");
    m.def("fast_cumsum", &fast_cumsum,
          "Cumulative sum of a 1D float64 array; returns new array.");
    m.def("fast_matrix_vector_mul", &fast_matrix_vector_mul,
          "Matrix-vector product: (M, N) @ (N,) -> (M,).");
    m.def("fast_lower_bound", &fast_lower_bound,
          "First index i where arr[i] >= value (assumes ascending order).");
    m.def("fast_upper_bound", &fast_upper_bound,
          "First index i where arr[i] > value (assumes ascending order).");
}
