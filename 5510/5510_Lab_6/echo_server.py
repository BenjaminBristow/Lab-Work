"""
Lab 6, Task 3 - PROVIDED SERVER (you do not need to change this).
A tiny mailbox server. Start it in one terminal with:
    python3 echo_server.py
It listens on http://localhost:8000 with two endpoints:
  POST /send     body: a JSON envelope -> stores it, returns {"status": "stored"}
  GET  /receive  -> returns {"messages": [ ...all stored envelopes... ]}
The server never looks inside the envelopes; it only stores and returns them.
"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAILBOX = []   # stored envelopes (each is a JSON string sent by a client)


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path == "/send":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            MAILBOX.append(body)          # store the envelope as-is
            self._send(200, {"status": "stored"})
        else:
            self._send(404, {"error": "not found"})

    def do_GET(self):
        if self.path == "/receive":
            self._send(200, {"messages": MAILBOX})
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, *args):
        pass   # keep the terminal quiet


if __name__ == "__main__":
    print("echo_server listening on http://localhost:8000")
    ThreadingHTTPServer(("localhost", 8000), Handler).serve_forever()
