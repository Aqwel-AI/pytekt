#!/usr/bin/env python3
"""Physical-AI query pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from . import electromagnetism, kinematics, mechanics, optics, relativity, thermo, waves


@dataclass
class PhysicsQueryResult:
    """Structured result returned by the physics query router."""

    task: str
    inputs: Dict[str, float]
    output_name: str
    output_value: float
    unit: str
    explanation: str


def simulate_free_fall(*, height: float, gravity: float = 9.80665) -> Dict[str, float]:
    """Return time-to-impact and final speed for ideal free fall from rest."""
    if height < 0:
        raise ValueError("height must be non-negative")
    from math import sqrt

    time_seconds = sqrt((2.0 * height) / gravity) if height > 0 else 0.0
    impact_speed = gravity * time_seconds
    return {"time_seconds": time_seconds, "impact_speed_m_per_s": impact_speed}


def _result(
    task: str,
    inputs: Dict[str, float],
    output_name: str,
    output_value: float,
    unit: str,
    explanation: str,
) -> PhysicsQueryResult:
    return PhysicsQueryResult(
        task=task,
        inputs=inputs,
        output_name=output_name,
        output_value=output_value,
        unit=unit,
        explanation=explanation,
    )


def solve_physics_query(description: str) -> PhysicsQueryResult:
    """Solve natural-language physics tasks via a lightweight rule-based router."""
    normalized = description.casefold()
    values = _extract_named_numbers(description)

    if "kinetic" in normalized and {"mass", "velocity"} <= values.keys():
        energy = mechanics.kinetic_energy(values["mass"], values["velocity"])
        return _result(
            "kinetic_energy",
            {"mass": values["mass"], "velocity": values["velocity"]},
            "kinetic_energy",
            energy,
            "J",
            "Computed kinetic energy using 0.5 * m * v^2.",
        )

    if "potential" in normalized and {"mass", "height"} <= values.keys():
        pe = mechanics.potential_energy(values["mass"], values["height"])
        return _result(
            "potential_energy",
            {"mass": values["mass"], "height": values["height"]},
            "potential_energy",
            pe,
            "J",
            "Computed gravitational potential energy using m * g * h.",
        )

    if "momentum" in normalized and {"mass", "velocity"} <= values.keys():
        p = mechanics.momentum(values["mass"], values["velocity"])
        return _result(
            "momentum",
            {"mass": values["mass"], "velocity": values["velocity"]},
            "momentum",
            p,
            "kg·m/s",
            "Computed linear momentum using p = m * v.",
        )

    if "force" in normalized and {"mass", "acceleration"} <= values.keys():
        f = mechanics.force(values["mass"], values["acceleration"])
        return _result(
            "force",
            {"mass": values["mass"], "acceleration": values["acceleration"]},
            "force",
            f,
            "N",
            "Computed force using F = m * a.",
        )

    if "gravitational" in normalized and {"mass1", "mass2", "distance"} <= values.keys():
        f = mechanics.gravitational_force(
            values["mass1"], values["mass2"], values["distance"]
        )
        return _result(
            "gravitational_force",
            {
                "mass1": values["mass1"],
                "mass2": values["mass2"],
                "distance": values["distance"],
            },
            "gravitational_force",
            f,
            "N",
            "Computed Newtonian gravitational force.",
        )

    if "projectile" in normalized and "range" in normalized:
        v_key = "v0" if "v0" in values else "velocity" if "velocity" in values else None
        angle_key = "angle" if "angle" in values else "launch_angle" if "launch_angle" in values else None
        if v_key and angle_key:
            r = mechanics.projectile_range(values[v_key], values[angle_key])
            return _result(
                "projectile_range",
                {v_key: values[v_key], angle_key: values[angle_key]},
                "range",
                r,
                "m",
                "Computed ideal projectile range without drag.",
            )

    if "pressure" in normalized and {"moles", "temperature", "volume"} <= values.keys():
        pressure = thermo.ideal_gas_pressure(
            values["moles"], values["temperature"], values["volume"]
        )
        return _result(
            "ideal_gas_pressure",
            {
                "moles": values["moles"],
                "temperature": values["temperature"],
                "volume": values["volume"],
            },
            "pressure",
            pressure,
            "Pa",
            "Computed pressure using the ideal gas law P = nRT / V.",
        )

    if "temperature" in normalized and {"pressure", "volume", "moles"} <= values.keys():
        temp = thermo.ideal_gas_temperature(
            values["pressure"], values["volume"], values["moles"]
        )
        return _result(
            "ideal_gas_temperature",
            {
                "pressure": values["pressure"],
                "volume": values["volume"],
                "moles": values["moles"],
            },
            "temperature",
            temp,
            "K",
            "Computed temperature using T = PV / (nR).",
        )

    if "heat" in normalized and {"mass", "c", "delta_t"} <= values.keys():
        q = thermo.heat_energy(values["mass"], values["c"], values["delta_t"])
        return _result(
            "heat_energy",
            {"mass": values["mass"], "c": values["c"], "delta_t": values["delta_t"]},
            "heat_energy",
            q,
            "J",
            "Computed heat energy using Q = m * c * delta_T.",
        )

    if "free fall" in normalized and "height" in values:
        result = simulate_free_fall(height=values["height"])
        return _result(
            "free_fall",
            {"height": values["height"]},
            "impact_speed_m_per_s",
            result["impact_speed_m_per_s"],
            "m/s",
            "Solved ideal free fall from rest and returned the impact speed.",
        )

    if "centripetal" in normalized and {"mass", "velocity", "radius"} <= values.keys():
        f = kinematics.centripetal_force(
            values["mass"], values["velocity"], values["radius"]
        )
        return _result(
            "centripetal_force",
            {
                "mass": values["mass"],
                "velocity": values["velocity"],
                "radius": values["radius"],
            },
            "centripetal_force",
            f,
            "N",
            "Computed centripetal force using m * v^2 / r.",
        )

    if "wave" in normalized and {"frequency", "wavelength"} <= values.keys():
        speed = waves.wave_speed(values["frequency"], values["wavelength"])
        return _result(
            "wave_speed",
            {"frequency": values["frequency"], "wavelength": values["wavelength"]},
            "wave_speed",
            speed,
            "m/s",
            "Computed wave speed using v = f * lambda.",
        )

    if "coulomb" in normalized and {"q1", "q2", "distance"} <= values.keys():
        f = electromagnetism.coulomb_force(values["q1"], values["q2"], values["distance"])
        return _result(
            "coulomb_force",
            {"q1": values["q1"], "q2": values["q2"], "distance": values["distance"]},
            "coulomb_force",
            f,
            "N",
            "Computed Coulomb force magnitude.",
        )

    if "ohms" in normalized or "ohm" in normalized:
        if {"voltage", "resistance"} <= values.keys():
            i = electromagnetism.ohms_law_current(values["voltage"], values["resistance"])
            return _result(
                "ohms_law_current",
                {"voltage": values["voltage"], "resistance": values["resistance"]},
                "current",
                i,
                "A",
                "Computed current using I = V / R.",
            )

    if "snell" in normalized and {"n1", "n2", "angle"} <= values.keys():
        refracted = optics.snells_law(values["n1"], values["n2"], values["angle"])
        return _result(
            "snells_law",
            {"n1": values["n1"], "n2": values["n2"], "angle": values["angle"]},
            "refracted_angle_deg",
            refracted,
            "deg",
            "Computed refracted angle from Snell's law.",
        )

    if "lorentz" in normalized and "velocity" in values:
        gamma = relativity.lorentz_factor(values["velocity"])
        return _result(
            "lorentz_factor",
            {"velocity": values["velocity"]},
            "gamma",
            gamma,
            "",
            "Computed Lorentz factor gamma.",
        )

    if "mass energy" in normalized or "e=mc" in normalized.replace(" ", ""):
        if "mass" in values:
            e = relativity.mass_energy_equivalence(values["mass"])
            return _result(
                "mass_energy_equivalence",
                {"mass": values["mass"]},
                "energy",
                e,
                "J",
                "Computed rest energy using E = m * c^2.",
            )

    raise ValueError(
        "Unsupported physics query. Run supported_physics_tasks() for available tasks."
    )


def _extract_named_numbers(description: str) -> Dict[str, float]:
    """Extract ``name=value`` style parameters from natural-language requests."""
    import re

    matches = re.findall(
        r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([-+]?(?:\d+\.?\d*|\d*\.\d+)(?:[eE][-+]?\d+)?)",
        description,
    )
    return {name.casefold(): float(value) for name, value in matches}


def supported_physics_tasks() -> List[str]:
    """Return the tasks understood by the physics query router."""
    return [
        "force: mass=<kg>, acceleration=<m/s^2>",
        "kinetic energy: mass=<kg>, velocity=<m/s>",
        "potential energy: mass=<kg>, height=<m>",
        "momentum: mass=<kg>, velocity=<m/s>",
        "gravitational force: mass1=<kg>, mass2=<kg>, distance=<m>",
        "projectile range: v0=<m/s>, angle=<deg>",
        "ideal gas pressure: moles=<mol>, temperature=<K>, volume=<m^3>",
        "ideal gas temperature: pressure=<Pa>, volume=<m^3>, moles=<mol>",
        "heat energy: mass=<kg>, c=<J/kg/K>, delta_t=<K>",
        "free fall: height=<m>",
        "centripetal force: mass=<kg>, velocity=<m/s>, radius=<m>",
        "wave speed: frequency=<Hz>, wavelength=<m>",
        "coulomb force: q1=<C>, q2=<C>, distance=<m>",
        "ohms law: voltage=<V>, resistance=<ohm>",
        "snells law: n1=<>, n2=<>, angle=<deg>",
        "lorentz factor: velocity=<m/s>",
        "mass energy: mass=<kg>",
    ]
