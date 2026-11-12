import os
import pytest
import socket
import struct
import subprocess
import sys
import time
from contextlib import closing


SERVER_SCRIPT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "hacker_echo_server.py")
)

PORT = 12347

# Header format from the lab specification (Hacker's Edition)
HEADER_FORMAT = "!BHddH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 21 bytes
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
    if _is_port_open("127.0.0.1", PORT):
        pytest.skip(f"Port {PORT} already in use; skipping Hacker's Edition server tests")

    proc = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=os.path.dirname(SERVER_SCRIPT),
        text=True,
        bufsize=1,
    )
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


def _request(seq: int, payload: bytes, client_ts: float = 1.25) -> bytes:
    return struct.pack(HEADER_FORMAT, TYPE_REQUEST, seq, client_ts, 0.0, len(payload)) + payload


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError(f"connection closed after {len(data)} of {n} bytes")
        data += chunk
    return data


def _recv_reply(sock: socket.socket):
    """Return (type, seq, client_ts, server_ts, payload) for one reply."""
    header = _recv_exact(sock, HEADER_SIZE)
    msg_type, seq, client_ts, server_ts, length = struct.unpack(HEADER_FORMAT, header)
    payload = _recv_exact(sock, length)
    return msg_type, seq, client_ts, server_ts, payload


def test_hacker_roundtrip_short_message():
    proc = _start_server()
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=2) as s:
            before = time.time()
            s.sendall(_request(9, b"Hello", client_ts=1730380000.123456))
            msg_type, seq, client_ts, server_ts, payload = _recv_reply(s)
            after = time.time()
            assert msg_type == TYPE_REPLY
            assert seq == 9
            assert client_ts == 1730380000.123456
            assert before - 1 <= server_ts <= after + 1, server_ts
            assert payload == b"Hello"
    finally:
        _stop_server(proc)


def test_hacker_long_and_empty_messages():
    proc = _start_server()
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=2) as s:
            # Longer than any fixed-size field and than a typical recv buffer
            long_payload = bytes(range(256)) * 40  # 10240 bytes
            s.sendall(_request(1, long_payload))
            _, seq, _, _, payload = _recv_reply(s)
            assert seq == 1
            assert payload == long_payload, "Long payload was not echoed back intact"

            # A zero-length payload is still a valid message
            s.sendall(_request(2, b""))
            _, seq, _, _, payload = _recv_reply(s)
            assert seq == 2
            assert payload == b""
    finally:
        _stop_server(proc)


def test_hacker_message_split_across_sends():
    """TCP may deliver a message in pieces: the header can be cut in two."""
    proc = _start_server()
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=2) as s:
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            packet = _request(3, b"split message")
            for piece in (packet[:5], packet[5:HEADER_SIZE + 3], packet[HEADER_SIZE + 3:]):
                s.sendall(piece)
                time.sleep(0.2)
            _, seq, _, _, payload = _recv_reply(s)
            assert seq == 3
            assert payload == b"split message"
    finally:
        _stop_server(proc)


def test_hacker_two_messages_in_one_send():
    """TCP may also deliver two messages in one recv(): both must be answered."""
    proc = _start_server()
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=2) as s:
            s.sendall(_request(4, b"first") + _request(5, b"second"))
            r1 = _recv_reply(s)
            r2 = _recv_reply(s)
            assert (r1[1], r1[4]) == (4, b"first"), r1
            assert (r2[1], r2[4]) == (5, b"second"), r2
    finally:
        _stop_server(proc)


def test_hacker_stalled_client_does_not_block_others():
    """
    Client A sends only part of a header and then goes quiet. Client B must
    still be served: the server must not block waiting for A's missing bytes.
    """
    proc = _start_server()
    try:
        a = socket.create_connection(("127.0.0.1", PORT), timeout=2)
        b = socket.create_connection(("127.0.0.1", PORT), timeout=2)
        try:
            a.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            packet_a = _request(10, b"from A")
            a.sendall(packet_a[:10])  # incomplete header
            time.sleep(0.3)           # let the server see A's partial data first

            b.sendall(_request(20, b"from B"))
            try:
                reply_b = _recv_reply(b)
            except socket.timeout:
                pytest.fail("Server did not answer client B while client A was "
                            "stalled half-way through a message (the server blocks "
                            "on one client)")
            assert (reply_b[1], reply_b[4]) == (20, b"from B"), reply_b

            # Now A finishes its message and must get its own reply
            a.sendall(packet_a[10:])
            reply_a = _recv_reply(a)
            assert (reply_a[1], reply_a[4]) == (10, b"from A"), reply_a
        finally:
            a.close()
            b.close()
    finally:
        _stop_server(proc)


def test_hacker_wrong_type_closes_connection():
    proc = _start_server()
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=2) as s:
            bad = struct.pack(HEADER_FORMAT, TYPE_REPLY, 1, 1.0, 0.0, 3) + b"bad"
            s.sendall(bad)
            data = s.recv(1024)
            assert data == b"", f"Server should close the connection, but sent {data!r}"
    finally:
        _stop_server(proc)
