# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from __future__ import annotations

import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from core.gpia_server import GPIA_Server

HOST = "127.0.0.1"
PORT = 11435


class Handler(BaseHTTPRequestHandler):
    server: ThreadingHTTPServer
    gpia: GPIA_Server

    def _respond(self, status: int, payload: Any) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path.startswith("/v1/models"):
            response = self.server.gpia.handle_models()
            self._respond(HTTPStatus.OK, response)
            return
        self._respond(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        payload = json.loads(raw.decode("utf-8"))
        if self.path in ("/v1/completions", "/v1/chat/completions"):
            response = self.server.gpia.handle_completion(payload)
            self._respond(HTTPStatus.OK, response)
            return
        self._respond(HTTPStatus.NOT_FOUND, {"error": "endpoint not implemented"})


class GPIAServerRunner:
    def __init__(self, host: str = HOST, port: int = PORT) -> None:
        self.server = ThreadingHTTPServer((host, port), Handler)
        self.server.gpia = GPIA_Server()

    def start(self) -> None:
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        print(f"GPIA server listening on http://{HOST}:{PORT}")
        thread.join()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()


if __name__ == "__main__":
    runner = GPIAServerRunner()
    runner.start()