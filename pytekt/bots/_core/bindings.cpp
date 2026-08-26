#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

#include "universal_event.hpp"
#include "dispatcher.hpp"
#include "ratelimiter.hpp"
#include "fsm.hpp"
#include "cache.hpp"
#include "webhook_server.hpp"
#include "antispam.hpp"
#include "metrics.hpp"

namespace py = pybind11;
using namespace pytekt::bots;

PYBIND11_MODULE(_native_core, m) {
    m.doc() = "PyTekt Bots C++ High-Performance Core Engine";

    // UniversalEvent binding
    py::class_<UniversalEvent>(m, "UniversalEvent")
        .def(py::init([](const std::string& id, const std::string& chat_id, const std::string& user_id,
                         const std::string& text, const std::string& platform, const std::string& event_type,
                         const std::string& command, const std::vector<std::string>& args,
                         const std::string& raw, const std::map<std::string, std::string>& metadata,
                         double timestamp) {
            auto ev = std::unique_ptr<UniversalEvent>(new UniversalEvent());
            ev->id = id;
            ev->chat_id = chat_id;
            ev->user_id = user_id;
            ev->text = text;
            if (!platform.empty()) ev->platform = platform;
            if (!event_type.empty()) ev->event_type = event_type;
            ev->command = command;
            ev->args = args;
            ev->raw = raw;
            ev->metadata = metadata;
            if (timestamp > 0.0) ev->timestamp = timestamp;
            return ev;
        }), py::arg("id") = "", py::arg("chat_id") = "", py::arg("user_id") = "",
            py::arg("text") = "", py::arg("platform") = "generic", py::arg("event_type") = "message",
            py::arg("command") = "", py::arg("args") = std::vector<std::string>(),
            py::arg("raw") = "", py::arg("metadata") = std::map<std::string, std::string>(),
            py::arg("timestamp") = 0.0)
        .def_readwrite("id", &UniversalEvent::id)
        .def_readwrite("chat_id", &UniversalEvent::chat_id)
        .def_readwrite("user_id", &UniversalEvent::user_id)
        .def_readwrite("text", &UniversalEvent::text)
        .def_readwrite("platform", &UniversalEvent::platform)
        .def_readwrite("event_type", &UniversalEvent::event_type)
        .def_readwrite("command", &UniversalEvent::command)
        .def_readwrite("args", &UniversalEvent::args)
        .def_readwrite("raw", &UniversalEvent::raw)
        .def_readwrite("metadata", &UniversalEvent::metadata)
        .def_readwrite("timestamp", &UniversalEvent::timestamp)
        .def("__repr__", [](const UniversalEvent& e) {
            return "<UniversalEvent id='" + e.id + "' platform='" + e.platform +
                   "' type='" + e.event_type + "' chat_id='" + e.chat_id +
                   "' text='" + e.text.substr(0, 30) + "'>";
        });

    // Dispatcher binding
    py::class_<Dispatcher>(m, "Dispatcher")
        .def(py::init<>())
        .def("add_command_handler", &Dispatcher::add_command_handler, py::arg("command"), py::arg("handler_id"))
        .def("add_pattern_handler", &Dispatcher::add_pattern_handler, py::arg("pattern"), py::arg("handler_id"))
        .def("add_event_handler", &Dispatcher::add_event_handler, py::arg("event_type"), py::arg("handler_id"))
        .def("add_state_handler", &Dispatcher::add_state_handler, py::arg("state_name"), py::arg("handler_id"))
        .def("match", &Dispatcher::match, py::arg("event"), py::arg("current_state") = "")
        .def("parse_telegram", &Dispatcher::parse_telegram, py::arg("json_str"))
        .def("parse_discord", &Dispatcher::parse_discord, py::arg("json_str"))
        .def("parse_generic", &Dispatcher::parse_generic, py::arg("json_str"), py::arg("platform") = "generic")
        .def_static("extract_command_and_args", [](const std::string& text) {
            std::string cmd;
            std::vector<std::string> args;
            Dispatcher::extract_command_and_args(text, cmd, args);
            return py::make_tuple(cmd, args);
        }, py::arg("text"));

    // RateLimiter binding
    py::class_<RateLimiter>(m, "RateLimiter")
        .def(py::init<>())
        .def("set_rule", &RateLimiter::set_rule, py::arg("scope"), py::arg("rate_str"))
        .def("set_custom_rule", &RateLimiter::set_custom_rule, py::arg("scope"), py::arg("capacity"), py::arg("window_seconds"))
        .def("acquire", &RateLimiter::acquire, py::arg("key"), py::arg("tokens") = 1.0)
        .def("check", &RateLimiter::check, py::arg("key"), py::arg("tokens") = 1.0)
        .def("check_and_acquire", &RateLimiter::check_and_acquire, py::arg("user_id"), py::arg("chat_id"), py::arg("tokens") = 1.0)
        .def("record_429", &RateLimiter::record_429, py::arg("key"), py::arg("retry_after_seconds"))
        .def("get_retry_after", &RateLimiter::get_retry_after, py::arg("key"))
        .def("reset", &RateLimiter::reset, py::arg("key") = "")
        .def("size", &RateLimiter::size)
        .def_static("parse_rate", [](const std::string& rate_str) {
            double cap = 1.0, win = 1.0;
            bool ok = RateLimiter::parse_rate(rate_str, cap, win);
            return py::make_tuple(ok, cap, win);
        }, py::arg("rate_str"));

    // FSM binding
    py::class_<FSM>(m, "FSM")
        .def(py::init<>())
        .def("set_state", &FSM::set_state, py::arg("key"), py::arg("state"), py::arg("ttl_seconds") = 0.0)
        .def("get_state", &FSM::get_state, py::arg("key"))
        .def("clear_state", &FSM::clear_state, py::arg("key"))
        .def("set_data", &FSM::set_data, py::arg("key"), py::arg("data_key"), py::arg("data_val"), py::arg("ttl_seconds") = 0.0)
        .def("get_data", &FSM::get_data, py::arg("key"), py::arg("data_key"))
        .def("get_all_data", &FSM::get_all_data, py::arg("key"))
        .def("set_all_data", &FSM::set_all_data, py::arg("key"), py::arg("data"), py::arg("ttl_seconds") = 0.0)
        .def("clear_data", &FSM::clear_data, py::arg("key"))
        .def("reset", &FSM::reset, py::arg("key") = "")
        .def("size", &FSM::size)
        .def("cleanup_expired", &FSM::cleanup_expired);

    // Cache binding
    py::class_<Cache>(m, "Cache")
        .def(py::init<>())
        .def("set", &Cache::set, py::arg("key"), py::arg("value"), py::arg("ttl_seconds") = 0.0)
        .def("get", &Cache::get, py::arg("key"))
        .def("has", &Cache::has, py::arg("key"))
        .def("delete", &Cache::delete_key, py::arg("key"))
        .def("clear", &Cache::clear)
        .def("size", &Cache::size)
        .def("cleanup_expired", &Cache::cleanup_expired)
        .def("keys", &Cache::keys);

    // WebhookServer binding
    py::class_<WebhookServer>(m, "WebhookServer")
        .def(py::init<>())
        .def("add_route", [](WebhookServer& self, const std::string& path, py::object py_handler) {
            self.add_route(path, [py_handler](const std::string& method, const std::string& p, const std::string& body) -> std::string {
                py::gil_scoped_acquire acquire;
                try {
                    py::object res = py_handler(method, p, body);
                    return res.cast<std::string>();
                } catch (const std::exception& e) {
                    return std::string("{\"error\":\"") + e.what() + "\"}";
                }
            });
        }, py::arg("path"), py::arg("handler"))
        .def("set_default_handler", [](WebhookServer& self, py::object py_handler) {
            self.set_default_handler([py_handler](const std::string& method, const std::string& p, const std::string& body) -> std::string {
                py::gil_scoped_acquire acquire;
                try {
                    py::object res = py_handler(method, p, body);
                    return res.cast<std::string>();
                } catch (const std::exception& e) {
                    return std::string("{\"error\":\"") + e.what() + "\"}";
                }
            });
        }, py::arg("handler"))
        .def("start", &WebhookServer::start, py::arg("host") = "0.0.0.0", py::arg("port") = 8443)
        .def("stop", &WebhookServer::stop)
        .def("is_running", &WebhookServer::is_running)
        .def("get_port", &WebhookServer::get_port)
        .def("get_host", &WebhookServer::get_host);

    // AntiSpam binding
    py::class_<AntiSpam>(m, "AntiSpam")
        .def(py::init<size_t, double>(), py::arg("bloom_size") = 65536, py::arg("window_seconds") = 300.0)
        .def("is_duplicate", &AntiSpam::is_duplicate, py::arg("text"), py::arg("user_id") = "")
        .def("add", &AntiSpam::add, py::arg("text"), py::arg("user_id") = "")
        .def("calculate_score", &AntiSpam::calculate_score, py::arg("text"), py::arg("message_rate") = 0.0, py::arg("duplicate_count") = 0)
        .def("is_spam", &AntiSpam::is_spam, py::arg("text"), py::arg("threshold") = 0.7, py::arg("message_rate") = 0.0)
        .def("reset", &AntiSpam::reset);

    // Metrics binding
    py::class_<Metrics>(m, "Metrics")
        .def(py::init<>())
        .def("increment_counter", &Metrics::increment_counter, py::arg("name"), py::arg("value") = 1.0, py::arg("labels") = std::map<std::string, std::string>())
        .def("observe", &Metrics::observe, py::arg("name"), py::arg("value"), py::arg("labels") = std::map<std::string, std::string>())
        .def("record_latency", &Metrics::record_latency, py::arg("command_name"), py::arg("duration_seconds"))
        .def("export_prometheus", &Metrics::export_prometheus)
        .def("reset", &Metrics::reset);
}
