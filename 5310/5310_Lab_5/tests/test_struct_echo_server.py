import os
import pytest
import socket
import struct
import subprocess
import sys
import time
from contextlib import closing


SERVER_SCRIPT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "struct_echo_server.py")
)

PORT = 12346

# Packet format from the lab specification (Stage 1, Task 2)
FORMAT = "!BHdd32s"
MSG_SIZE = struct.calcsize(FORMAT)  # 51 bytes
TYPE_REQUEST = 1
TYPE_REPLY = 2


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
    # If something else is already bound on the port, skip tests to avoid flakiness
    if _is_port_open("127.0.0.1", PORT):
        pytest.skip(f"Port {PORT} already in use; skipping struct echo server tests")

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
    if not _wait_for_port("127.0.0.1", PORT, timeout=5.0):
        try:
            out = proc.communicate(timeout=0.2)[0]
        except Exception:
            out = ""
        finally:
            proc.kill()
        raise RuntimeError(
            f"Server did not start listening on port {PORT}. Output:\n{out}")
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


def _recv_packet(sock: socket.socket) -> bytes:
    """Read one full reply (the test reads carefully even if the server does not)."""
    data = b""
    while len(data) < MSG_SIZE:
        chunk = sock.recv(MSG_SIZE - len(data))
        if not chunk:
            break
        data += chunk
    return data


def test_struct_echo_roundtrip():
    proc = _start_server()
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=2) as s:
            client_ts = 1730380000.123456
            request = struct.pack(FORMAT, TYPE_REQUEST, 7, client_ts, 0.0, b"Hello")
            before = time.time()
            s.sendall(request)
            data = _recv_packet(s)
            after = time.time()

            assert len(data) == MSG_SIZE, (
                f"Reply should be exactly {MSG_SIZE} bytes, got {len(data)}")
            msg_type, seq, echoed_client_ts, server_ts, message = struct.unpack(FORMAT, data)

            assert msg_type == TYPE_REPLY, f"Reply type should be {TYPE_REPLY}, got {msg_type}"
            assert seq == 7, f"Sequence number should be echoed unchanged, got {seq}"
            assert echoed_client_ts == client_ts, (
                f"Client timestamp should be echoed unchanged, got {echoed_client_ts}")
            assert before - 1 <= server_ts <= after + 1, (
                f"Server timestamp {server_ts} is not the current time.time()")
            assert message.rstrip(b"\x00") == b"Hello", message
    finally:
        _stop_server(proc)


def test_struct_echo_several_messages_same_connection():
    proc = _start_server()
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=2) as s:
            for seq, text in [(1, b"first"), (2, b"second"), (3, b"third")]:
                s.sendall(struct.pack(FORMAT, TYPE_REQUEST, seq, 1.5, 0.0, text))
                msg_type, r_seq, _, _, message = struct.unpack(FORMAT, _recv_packet(s))
                assert msg_type == TYPE_REPLY
                assert r_seq == seq
                assert message.rstrip(b"\x00") == text
    finally:
        _stop_server(proc)


def test_struct_wrong_type_closes_connection():
    proc = _start_server()
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=2) as s:
            # A packet with type 2 (reply) is not a valid request
            s.sendall(struct.pack(FORMAT, TYPE_REPLY, 1, 1.0, 0.0, b"bad"))
            # After the server closes, a recv should return b'' (connection closed)
            data = s.recv(1024)
            assert data == b"", f"Server should close the connection, but sent {data!r}"
    finally:
        _stop_server(proc)


def test_struct_multiple_clients():
    proc = _start_server()
    try:
        s1 = socket.create_connection(("127.0.0.1", PORT), timeout=2)
        s2 = socket.create_connection(("127.0.0.1", PORT), timeout=2)
        try:
            s1.sendall(struct.pack(FORMAT, TYPE_REQUEST, 1, 1.0, 0.0, b"A"))
            s2.sendall(struct.pack(FORMAT, TYPE_REQUEST, 2, 2.0, 0.0, b"B"))
            r1 = struct.unpack(FORMAT, _recv_packet(s1))
            r2 = struct.unpack(FORMAT, _recv_packet(s2))
            assert r1[1] == 1 and r1[4].rstrip(b"\x00") == b"A", r1
            assert r2[1] == 2 and r2[4].rstrip(b"\x00") == b"B", r2
        finally:
            s1.close()
            s2.close()
    finally:
        _stop_server(proc)
