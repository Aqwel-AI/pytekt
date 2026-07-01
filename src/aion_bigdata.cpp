/*
 * Aqwel-Aion native big-data kernels.
 *
 * This extension accelerates large-array operations that are common in
 * preprocessing and analytics: prefix sums, rolling windows, histograms,
 * and chunk-level statistics.
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include "native/bigdata_kernels.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_aion_bigdata, m) {
    m.doc() = "Aion native big-data kernels";

    m.def(
        "prefix_sum",
        &aion_native::prefix_sum,
        py::arg("arr"),
        "Compute prefix sums of a 1D numeric array."
    );
    m.def(
        "rolling_sum",
        &aion_native::rolling_sum,
        py::arg("arr"),
        py::arg("window"),
        "Compute rolling sums over a 1D numeric array."
    );
    m.def(
        "rolling_mean",
        &aion_native::rolling_mean,
        py::arg("arr"),
        py::arg("window"),
        "Compute rolling means over a 1D numeric array."
    );
    m.def(
        "histogram",
        &aion_native::histogram,
        py::arg("arr"),
        py::arg("bins"),
        py::arg("lo"),
        py::arg("hi"),
        "Compute histogram bin counts for a 1D numeric array."
    );
    m.def(
        "chunk_statistics",
        &aion_native::chunk_statistics,
        py::arg("arr"),
        py::arg("chunk_size"),
        "Return per-chunk mean/min/max statistics for a 1D numeric array."
    );
}
