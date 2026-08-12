/*
 * Shared helpers for Aion C++ extensions.
 *
 * These utilities keep the native modules small and consistent while
 * enforcing contiguous double-precision inputs for numeric kernels.
 */

#pragma once

#include <pybind11/numpy.h>

#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <string>

namespace pytekt_native {

namespace py = pybind11;

inline py::buffer_info require_1d_double_buffer(const py::array_t<double>& arr, const char* name) {
    py::buffer_info buf = arr.request();
    if (buf.ndim != 1) {
        throw std::runtime_error(std::string(name) + ": expected a 1D array");
    }
    return buf;
}

inline py::array_t<double> make_double_array(std::size_t size) {
    return py::array_t<double>(static_cast<py::ssize_t>(size));
}

inline py::array_t<std::int64_t> make_int64_array(std::size_t size) {
    return py::array_t<std::int64_t>(static_cast<py::ssize_t>(size));
}

}  // namespace pytekt_native
