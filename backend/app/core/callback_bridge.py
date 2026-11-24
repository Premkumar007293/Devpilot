"""Lightweight bridge server ensuring OAuth callback ports route cleanly to the backend."""

import http.server
import socket
import socketserver
import threading
import urllib.parse
import urllib.request
import urllib.error
from typing import Optional
from app.core.config import settings
from app.core.logging import logger

_bridge_server: Optional[socketserver.TCPServer] = None
_bridge_thread: Optional[threading.Thread] = None


class CallbackProxyHandler(http.server.BaseHTTPRequestHandler):
    """Proxy HTTP handler forwarding all requests (OAuth callbacks & API calls) to the FastAPI backend."""

    def log_message(self, format, *args):
        logger.debug("OAuth Bridge [port %s]: " + format, self.server.server_address[1], *args)

    def _proxy(self, method: str):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        backend_target = f"http://127.0.0.1:{settings.BACKEND_PORT}{self.path}"

        headers = {k: v for k, v in self.headers.items() if k.lower() != "host"}

        try:
            req = urllib.request.Request(backend_target, data=body, headers=headers, method=method)

            class NoRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    return None

            opener = urllib.request.build_opener(NoRedirect)
            try:
                with opener.open(req, timeout=15.0) as resp:
                    self.send_response(resp.status)
                    for k, v in resp.headers.items():
                        if k.lower() not in {"transfer-encoding", "content-length"}:
                            self.send_header(k, v)
                    resp_body = resp.read()
                    self.send_header("Content-Length", str(len(resp_body)))
                    self.end_headers()
                    self.wfile.write(resp_body)
            except urllib.error.HTTPError as err:
                self.send_response(err.code)
                for k, v in err.headers.items():
                    if k.lower() not in {"transfer-encoding", "content-length"}:
                        self.send_header(k, v)
                err_body = err.read()
                self.send_header("Content-Length", str(len(err_body)))
                self.end_headers()
                self.wfile.write(err_body)
        except Exception as exc:
            logger.warning("OAuth Bridge [%s] proxy failed for %s: %s", method, self.path, exc)
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"Proxy error: {exc}".encode("utf-8"))

    def do_GET(self): self._proxy("GET")
    def do_POST(self): self._proxy("POST")
    def do_OPTIONS(self): self._proxy("OPTIONS")
    def do_PUT(self): self._proxy("PUT")
    def do_DELETE(self): self._proxy("DELETE")
    def do_PATCH(self): self._proxy("PATCH")
    def do_HEAD(self): self._proxy("HEAD")


def start_callback_bridge() -> None:
    """Start bridge listener on the configured callback port if different from backend port."""
    global _bridge_server, _bridge_thread

    callback_url = settings.GITHUB_CALLBACK_URL
    if not callback_url:
        return

    parsed = urllib.parse.urlparse(callback_url)
    callback_port = parsed.port
    if not callback_port or callback_port == settings.BACKEND_PORT:
        return

    # Check if port is already bound
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", callback_port))
        sock.close()
    except OSError:
        logger.info("Port %s is already bound; skipping bridge listener.", callback_port)
        return

    try:
        socketserver.TCPServer.allow_reuse_address = True
        _bridge_server = socketserver.TCPServer(("127.0.0.1", callback_port), CallbackProxyHandler)
        _bridge_thread = threading.Thread(target=_bridge_server.serve_forever, daemon=True)
        _bridge_thread.start()
        logger.info("Started OAuth callback bridge on port %s -> %s", callback_port, settings.BACKEND_PORT)
    except Exception as exc:
        logger.warning("Could not start OAuth callback bridge on port %s: %s", callback_port, exc)


def stop_callback_bridge() -> None:
    """Stop bridge server on shutdown."""
    global _bridge_server
    if _bridge_server:
        try:
            _bridge_server.shutdown()
            _bridge_server.server_close()
        except Exception:
            pass
        _bridge_server = None
