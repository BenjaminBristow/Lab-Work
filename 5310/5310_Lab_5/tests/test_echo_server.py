import os
import pytest
import re
import socket
import subprocess
import sys
import time
from contextlib import closing


SERVER_SCRIPT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "echo_server.py")
)


def _is_port_open(host: str, port: int) -> bool:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(0.2)
        try:
            sock.connect((host, port))
            return True
        except OSError:
            return False


def _wait_for_port(host: str, port: int, timeout: float = 5.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _is_port_open(host, port):
            return True
        time.sleep(0.05)
    return False


def _start_server():
    # If something else is already bound on 12345, skip tests to avoid flakiness
    if _is_port_open("127.0.0.1", 12345):
        pytest.skip("Port 12345 already in use; skipping echo server tests")

    # Launch the echo server as a background process
    proc = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=os.path.dirname(SERVER_SCRIPT),
        text=True,
        bufsize=1,
    )
    # Wait until it's listening
    if not _wait_for_port("127.0.0.1", 12345, timeout=5.0):
        try:
            out = proc.communicate(timeout=0.2)[0]
        except Exception:
            out = ""
        finally:
            proc.kill()
        raise RuntimeError(
            f"Server did not start listening on port 12345. Output:\n{out}")
    return proc


def _stop_server(proc: subprocess.Popen | None):
    if proc is None:
        return
    try:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
    except Exception:
        pass


def test_echo_roundtrip():
    proc = _start_server()
    try:
        with socket.create_connection(("127.0.0.1", 12345), timeout=2) as s:
            msg = "Hello"
            s.sendall(msg.encode())
            data = s.recv(1024)
            decoded = data.decode()
            # Expect: "<float>:Hello" (server uses ':' as delimiter)
            assert re.match(r"^[0-9]+\.[0-9]+:Hello$", decoded), decoded
    finally:
        _stop_server(proc)


def test_telnet_close_sequence():
    proc = _start_server()
    try:
        with socket.create_connection(("127.0.0.1", 12345), timeout=2) as s:
            # Send 0xff first byte to signal close as per README/server logic
            s.sendall(b"\xffBYE")
            # After server closes, a recv should return b'' (connection closed)
            s.shutdown(socket.SHUT_WR)
            data = s.recv(1024)
            assert data == b""
    finally:
        _stop_server(proc)


def test_multiple_clients():
    proc = _start_server()
    try:
        s1 = socket.create_connection(("127.0.0.1", 12345), timeout=2)
        s2 = socket.create_connection(("127.0.0.1", 12345), timeout=2)
        try:
            s1.sendall(b"A")
            s2.sendall(b"B")
            d1 = s1.recv(1024).decode()
            d2 = s2.recv(1024).decode()
            assert d1.endswith(":A"), d1
            assert d2.endswith(":B"), d2
        finally:
            s1.close()
            s2.close()
    finally:
        _stop_server(proc)
