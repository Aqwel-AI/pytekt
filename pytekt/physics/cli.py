"""``pytekt physics`` subcommands."""

from __future__ import annotations

import argparse
from math import pi

from . import mechanics, thermo, units
from .pipeline import solve_physics_query, supported_physics_tasks


def physics_main(args: argparse.Namespace) -> None:
    action = getattr(args, "physics_action", None) or "help"

    if action == "query":
        result = solve_physics_query(args.text)
        print(f"  Task: {result.task}")
        print(f"  {result.output_name} = {result.output_value} {result.unit}")
        print(f"  {result.explanation}")
        return

    if action == "pendulum":
        from .systems import simulate_pendulum

        theta0 = args.angle_deg * pi / 180.0
        result = simulate_pendulum(
            args.length, theta0, dt=args.dt, steps=args.steps
        )
        print(f"  Pendulum length={args.length} m, angle={args.angle_deg}°")
        print(f"  Small-angle period: {result.summary['small_angle_period_s']:.4f} s")
        print(f"  Steps: {int(result.summary['steps'])}, dt={result.summary['dt']}")
        print(f"  Final theta: {result.trajectory[-1][0]:.4f} rad")
        return

    if action == "projectile":
        from .systems import projectile_motion

        result = projectile_motion(
            args.v0,
            args.angle,
            dt=args.dt,
            steps=args.steps,
            drag_coeff=args.drag,
        )
        print(f"  Range: {result.summary['range_m']:.2f} m")
        print(f"  Max height: {result.summary['max_height_m']:.2f} m")
        print(f"  Flight time: {result.summary['flight_time_s']:.2f} s")
        return

    if action == "force":
        print(f"  Force = {mechanics.force(args.mass, args.acceleration):.4f} N")
        return

    if action == "ke":
        print(f"  Kinetic energy = {mechanics.kinetic_energy(args.mass, args.velocity):.4f} J")
        return

    if action == "gas":
        p = thermo.ideal_gas_pressure(args.moles, args.temperature, args.volume)
        print(f"  Pressure = {p:.4f} Pa")
        return

    if action == "units":
        converters = {
            "km_to_m": units.kilometers_to_meters,
            "m_to_km": units.meters_to_kilometers,
            "c_to_k": units.celsius_to_kelvin,
            "k_to_c": units.kelvin_to_celsius,
            "ev_to_j": units.ev_to_joules,
            "j_to_ev": units.joules_to_ev,
            "deg_to_rad": units.degrees_to_radians,
            "rad_to_deg": units.radians_to_degrees,
        }
        fn = converters.get(args.convert)
        if fn is None:
            print(f"  Unknown conversion: {args.convert}")
            print(f"  Available: {', '.join(sorted(converters))}")
            return
        print(f"  {args.value} {args.convert} = {fn(args.value)}")
        return

    if action == "tasks":
        print("  Supported physics query tasks:")
        for task in supported_physics_tasks():
            print(f"    {task}")
        return

    if action == "demo":
        from .examples.demo_pendulum import main

        main()
        return

    if action == "web":
        from .launch import run_physics_dashboard

        run_physics_dashboard(
            host=getattr(args, "host", "127.0.0.1"),
            port=getattr(args, "port", 3858),
            open_browser=not getattr(args, "no_browser", False),
        )
        return

    print(
        "  Usage: pytekt physics query | pendulum | projectile | force | ke | gas | "
        "units | tasks | demo | web"
    )
