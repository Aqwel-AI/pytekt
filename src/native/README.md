# Native Kernels

This directory holds shared C++ headers used by Aion's optional native extensions.

Current modules:

- `aion_core.cpp` for fast scalar/vector numerics
- `aion_bigdata.cpp` for large-array and streaming reductions
- `aion_universe.cpp` for astronomy and cosmology kernels

Keep new native utilities header-only here when they are shared across multiple extension modules.
