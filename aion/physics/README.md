# Aion Physics MVP

This package provides a small but usable physics toolkit:

- mechanics helpers such as force, momentum, and energy
- thermodynamics helpers based on the ideal gas law
- unit conversions
- Euler and RK4 trajectory integration
- a lightweight natural-language query router for a few supported tasks

Example:

```python
from aion.physics import solve_physics_query

result = solve_physics_query("kinetic energy mass=2 velocity=3")
print(result.output_value)  # 9.0
```
