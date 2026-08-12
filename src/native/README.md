# Native Kernels

This directory holds shared C++ headers used by PyTekt's optional native extensions.

Current modules:

- `pytekt_core.cpp` for fast scalar/vector numerics
- `pytekt_bigdata.cpp` for large-array and streaming reductions
- `pytekt_universe.cpp` for astronomy and cosmology kernels

Keep new native utilities header-only here when they are shared across multiple extension modules.
