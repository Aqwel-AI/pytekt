/*
 * PyTekt — fast physics calculations (physics module)
 *
 * Optional native module: pytekt._pytekt_physics
 * Requires pybind11 and C++14 at build time.
 *
 * License: Apache-2.0
 */

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>
#include <cmath>
#include <stdexcept>
#include <vector>

namespace py = pybind11;

static std::vector<double> rk4_step_impl(
    const py::function& derivative_fn,
    double t,
    const std::vector<double>& state,
    double dt)
{
    if (dt <= 0) {
        throw std::invalid_argument("dt must be positive");
    }
    py::list k1 = derivative_fn(t, state).cast<py::list>();
    std::vector<double> s2(state.size());
    for (size_t i = 0; i < state.size(); ++i) {
        s2[i] = state[i] + 0.5 * dt * k1[i].cast<double>();
    }
    py::list k2 = derivative_fn(t + 0.5 * dt, s2).cast<py::list>();
    std::vector<double> s3(state.size());
    for (size_t i = 0; i < state.size(); ++i) {
        s3[i] = state[i] + 0.5 * dt * k2[i].cast<double>();
    }
    py::list k3 = derivative_fn(t + 0.5 * dt, s3).cast<py::list>();
    std::vector<double> s4(state.size());
    for (size_t i = 0; i < state.size(); ++i) {
        s4[i] = state[i] + dt * k3[i].cast<double>();
    }
    py::list k4 = derivative_fn(t + dt, s4).cast<py::list>();

    std::vector<double> next(state.size());
    for (size_t i = 0; i < state.size(); ++i) {
        double d1 = k1[i].cast<double>();
        double d2 = k2[i].cast<double>();
        double d3 = k3[i].cast<double>();
        double d4 = k4[i].cast<double>();
        next[i] = state[i] + (dt / 6.0) * (d1 + 2.0 * d2 + 2.0 * d3 + d4);
    }
    return next;
}

std::vector<double> rk4_step(
    const py::function& derivative_fn,
    double t,
    const std::vector<double>& state,
    double dt)
{
    return rk4_step_impl(derivative_fn, t, state, dt);
}

std::vector<std::vector<double>> integrate_trajectory_rk4(
    const py::function& derivative_fn,
    const std::vector<double>& initial_state,
    double dt,
    int steps,
    double t0)
{
    if (dt <= 0) {
        throw std::invalid_argument("dt must be positive");
    }
    if (steps < 0) {
        throw std::invalid_argument("steps must be non-negative");
    }
    std::vector<double> state = initial_state;
    double time = t0;
    std::vector<std::vector<double>> trajectory;
    trajectory.push_back(state);
    for (int i = 0; i < steps; ++i) {
        state = rk4_step_impl(derivative_fn, time, state, dt);
        time += dt;
        trajectory.push_back(state);
    }
    return trajectory;
}

std::vector<std::vector<double>> pendulum_trajectory(
    double length,
    double theta0,
    double dt,
    int steps,
    double gravity,
    double omega0)
{
    if (length <= 0) {
        throw std::invalid_argument("length must be positive");
    }
    if (dt <= 0) {
        throw std::invalid_argument("dt must be positive");
    }
    if (steps < 0) {
        throw std::invalid_argument("steps must be non-negative");
    }

    auto pendulum_deriv = [length, gravity](const std::vector<double>& s) -> std::vector<double> {
        double theta = s[0];
        double omega = s[1];
        double alpha = -(gravity / length) * std::sin(theta);
        return {omega, alpha};
    };

    auto rk4 = [&](double t, const std::vector<double>& state) -> std::vector<double> {
        (void)t;
        std::vector<double> k1 = pendulum_deriv(state);
        std::vector<double> s2 = {state[0] + 0.5 * dt * k1[0], state[1] + 0.5 * dt * k1[1]};
        std::vector<double> k2 = pendulum_deriv(s2);
        std::vector<double> s3 = {state[0] + 0.5 * dt * k2[0], state[1] + 0.5 * dt * k2[1]};
        std::vector<double> k3 = pendulum_deriv(s3);
        std::vector<double> s4 = {state[0] + dt * k3[0], state[1] + dt * k3[1]};
        std::vector<double> k4 = pendulum_deriv(s4);
        return {
            state[0] + (dt / 6.0) * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]),
            state[1] + (dt / 6.0) * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]),
        };
    };

    std::vector<double> state = {theta0, omega0};
    std::vector<std::vector<double>> trajectory;
    trajectory.push_back(state);
    for (int i = 0; i < steps; ++i) {
        state = rk4(i * dt, state);
        trajectory.push_back(state);
    }
    return trajectory;
}

PYBIND11_MODULE(_pytekt_physics, m) {
    m.doc() = "PyTekt physics fast calculations";
    m.def("rk4_step", &rk4_step, "Single RK4 integration step");
    m.def("integrate_trajectory_rk4", &integrate_trajectory_rk4, "RK4 trajectory integration");
    m.def("pendulum_trajectory", &pendulum_trajectory, "Simulate simple pendulum");
}
