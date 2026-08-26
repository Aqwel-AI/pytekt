#ifndef PYTEKT_BOTS_WEBHOOK_SERVER_HPP
#define PYTEKT_BOTS_WEBHOOK_SERVER_HPP

#include <string>
#include <unordered_map>
#include <functional>
#include <thread>
#include <atomic>
#include <mutex>

namespace pytekt {
namespace bots {

using HttpHandler = std::function<std::string(const std::string& method, const std::string& path, const std::string& body)>;

class WebhookServer {
public:
    WebhookServer();
    ~WebhookServer();

    void add_route(const std::string& path, HttpHandler handler);
    void set_default_handler(HttpHandler handler);

    bool start(const std::string& host, int port);
    void stop();

    bool is_running() const;
    int get_port() const;
    std::string get_host() const;

private:
    void server_loop();
    void handle_client(int client_fd);

    std::string host_ = "0.0.0.0";
    int port_ = 8443;
    int server_fd_ = -1;
    std::atomic<bool> running_{false};
    std::thread worker_thread_;

    mutable std::mutex routes_mutex_;
    std::unordered_map<std::string, HttpHandler> routes_;
    HttpHandler default_handler_;
};

} // namespace bots
} // namespace pytekt

#endif // PYTEKT_BOTS_WEBHOOK_SERVER_HPP
