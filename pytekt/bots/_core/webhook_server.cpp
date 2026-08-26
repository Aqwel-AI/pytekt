#include "webhook_server.hpp"
#include <iostream>
#include <sstream>
#include <cstring>
#include <algorithm>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
typedef int socklen_t;
#define close_socket closesocket
#else
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#define close_socket close
#endif

namespace pytekt {
namespace bots {

WebhookServer::WebhookServer() {
#ifdef _WIN32
    WSADATA wsa;
    WSAStartup(MAKEWORD(2, 2), &wsa);
#endif
}

WebhookServer::~WebhookServer() {
    stop();
#ifdef _WIN32
    WSACleanup();
#endif
}

void WebhookServer::add_route(const std::string& path, HttpHandler handler) {
    std::lock_guard<std::mutex> lock(routes_mutex_);
    routes_[path] = handler;
}

void WebhookServer::set_default_handler(HttpHandler handler) {
    std::lock_guard<std::mutex> lock(routes_mutex_);
    default_handler_ = handler;
}

bool WebhookServer::is_running() const {
    return running_.load();
}

int WebhookServer::get_port() const {
    return port_;
}

std::string WebhookServer::get_host() const {
    return host_;
}

bool WebhookServer::start(const std::string& host, int port) {
    if (running_.load()) {
        return true;
    }

    host_ = host;
    port_ = port;

    server_fd_ = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd_ < 0) {
        return false;
    }

    int opt = 1;
#ifdef _WIN32
    setsockopt(server_fd_, SOL_SOCKET, SO_REUSEADDR, (const char*)&opt, sizeof(opt));
#else
    setsockopt(server_fd_, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif

    sockaddr_in addr;
    std::memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(static_cast<uint16_t>(port));

    if (host == "0.0.0.0" || host.empty()) {
        addr.sin_addr.s_addr = INADDR_ANY;
    } else {
        inet_pton(AF_INET, host.c_str(), &addr.sin_addr);
    }

    if (bind(server_fd_, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close_socket(server_fd_);
        server_fd_ = -1;
        return false;
    }

    if (listen(server_fd_, 128) < 0) {
        close_socket(server_fd_);
        server_fd_ = -1;
        return false;
    }

    running_.store(true);
    worker_thread_ = std::thread(&WebhookServer::server_loop, this);
    return true;
}

void WebhookServer::stop() {
    if (!running_.load()) return;
    running_.store(false);

    if (server_fd_ >= 0) {
        // Shutdown socket to unblock accept()
#ifdef _WIN32
        shutdown(server_fd_, SD_BOTH);
        closesocket(server_fd_);
#else
        shutdown(server_fd_, SHUT_RDWR);
        close(server_fd_);
#endif
        server_fd_ = -1;
    }

    if (worker_thread_.joinable()) {
        worker_thread_.join();
    }
}

void WebhookServer::server_loop() {
    while (running_.load()) {
        sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        int client_fd = accept(server_fd_, (struct sockaddr*)&client_addr, &client_len);
        if (client_fd < 0) {
            if (!running_.load()) break;
            continue;
        }

        // Process request in lightweight detached thread
        std::thread([this, client_fd]() {
            handle_client(client_fd);
        }).detach();
    }
}

void WebhookServer::handle_client(int client_fd) {
    char buffer[4096];
    std::string request_str;
    size_t content_length = 0;
    bool headers_done = false;
    size_t header_end_pos = std::string::npos;

    while (true) {
        int bytes = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
        if (bytes <= 0) break;
        buffer[bytes] = '\0';
        request_str.append(buffer, bytes);

        if (!headers_done) {
            header_end_pos = request_str.find("\r\n\r\n");
            if (header_end_pos != std::string::npos) {
                headers_done = true;
                // Parse Content-Length
                std::string headers = request_str.substr(0, header_end_pos);
                std::string cl_key = "Content-Length:";
                size_t pos = headers.find(cl_key);
                if (pos == std::string::npos) {
                    cl_key = "content-length:";
                    pos = headers.find(cl_key);
                }
                if (pos != std::string::npos) {
                    size_t end_line = headers.find("\r\n", pos);
                    std::string len_str = headers.substr(pos + cl_key.length(), end_line - (pos + cl_key.length()));
                    try {
                        content_length = std::stoul(len_str);
                    } catch (...) {
                        content_length = 0;
                    }
                }
            }
        }

        if (headers_done) {
            size_t body_received = request_str.length() - (header_end_pos + 4);
            if (body_received >= content_length) {
                break;
            }
        }
    }

    if (request_str.empty()) {
        close_socket(client_fd);
        return;
    }

    // Parse HTTP request line: METHOD PATH HTTP/1.1
    std::istringstream req_stream(request_str);
    std::string method, path, http_version;
    req_stream >> method >> path >> http_version;

    std::string body;
    if (header_end_pos != std::string::npos && header_end_pos + 4 < request_str.size()) {
        body = request_str.substr(header_end_pos + 4, content_length);
    }

    // Lookup route handler
    HttpHandler handler = nullptr;
    {
        std::lock_guard<std::mutex> lock(routes_mutex_);
        auto it = routes_.find(path);
        if (it != routes_.end()) {
            handler = it->second;
        } else if (default_handler_) {
            handler = default_handler_;
        }
    }

    std::string response_body = "{\"status\":\"ok\"}";
    int status_code = 200;
    std::string status_msg = "OK";

    if (handler) {
        try {
            response_body = handler(method, path, body);
        } catch (const std::exception& e) {
            status_code = 500;
            status_msg = "Internal Server Error";
            response_body = std::string("{\"error\":\"") + e.what() + "\"}";
        }
    } else {
        status_code = 404;
        status_msg = "Not Found";
        response_body = "{\"error\":\"not_found\"}";
    }

    std::ostringstream resp;
    resp << "HTTP/1.1 " << status_code << " " << status_msg << "\r\n";
    resp << "Content-Type: application/json\r\n";
    resp << "Content-Length: " << response_body.length() << "\r\n";
    resp << "Connection: close\r\n\r\n";
    resp << response_body;

    std::string resp_str = resp.str();
    send(client_fd, resp_str.c_str(), static_cast<int>(resp_str.length()), 0);
    close_socket(client_fd);
}

} // namespace bots
} // namespace pytekt
