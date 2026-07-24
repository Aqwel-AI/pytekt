import json
import socket
import threading
import time
import urllib.request

from aion.physics.server import PhysicsHandler, _ThreadingHTTPServer


def test_physics_server_info():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    server = _ThreadingHTTPServer(("127.0.0.1", port), PhysicsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.2)

    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/info", timeout=2) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    assert data["app"] == "physics"

    server.shutdown()
