import builtins
import os
import struct
import sys
from typing import List, Tuple

# Ensure project root is on sys.path so `import hacker_echo_client` works
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Header format from the lab specification (Hacker's Edition)
HEADER_FORMAT = "!BHddH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 21 bytes
TYPE_REQUEST = 1
TYPE_REPLY = 2


def _make_fake_socket(monkeypatch, scripted_recv: List[bytes]):
    """
    Create a fake socket class that records connect/sendall calls and returns
    the provided byte chunks from recv(). Unlike the earlier tests, this fake
    behaves like a real TCP socket: recv(n) never returns more than n bytes,
    and each scripted chunk may be smaller than what the client asked for.
    """

    created_instances: List["FakeSocket"] = []

    class FakeSocket:
        def __init__(self, *args, **kwargs):
            self.connected_to: Tuple[str, int] | None = None
            self.sent: List[bytes] = []
            self._recv_queue = list(scripted_recv)
            self.closed = False
            created_instances.append(self)

        def settimeout(self, _timeout):
            return None

        def connect(self, address):
            self.connected_to = address

        def sendall(self, data: bytes):
            self.sent.append(bytes(data))

        def send(self, data: bytes) -> int:
            self.sent.append(bytes(data))
            return len(data)

        def recv(self, bufsize: int) -> bytes:
            if not self._recv_queue:
                # Simulate remote close when no scripted data left
                return b""
            chunk = self._recv_queue.pop(0)
            if len(chunk) > bufsize:
                # Hand back only what was asked for; keep the rest for later
                self._recv_queue.insert(0, chunk[bufsize:])
                chunk = chunk[:bufsize]
            return chunk

        def close(self):
            self.closed = True

    def fake_socket_factory(*args, **kwargs):
        return FakeSocket(*args, **kwargs)

    import socket as _socket

    monkeypatch.setattr(_socket, "socket", fake_socket_factory, raising=True)
    return FakeSocket, created_instances


def _script_inputs(monkeypatch, inputs: List[str], then_exception: BaseException | None = None):
    seq = list(inputs)

    def _fake_input(prompt: str = "") -> str:
        if seq:
            return seq.pop(0)
        if then_exception is not None:
            raise then_exception
        raise EOFError

    monkeypatch.setattr(builtins, "input", _fake_input, raising=True)


def _reply(seq: int, client_ts: float, server_ts: float, payload: bytes) -> bytes:
    return struct.pack(HEADER_FORMAT, TYPE_REPLY, seq, client_ts, server_ts, len(payload)) + payload


def test_hacker_client_sends_header_and_payload(monkeypatch, capsys):
    import hacker_echo_client as client

    fixed_client_ts = 1730380000.123456
    fixed_server_ts = 1730380000.234567
    import time as _time
    monkeypatch.setattr(_time, "time", lambda: fixed_client_ts, raising=False)

    message = "Hello, World!"
    FakeSocket, instances = _make_fake_socket(
        monkeypatch, [_reply(1, fixed_client_ts, fixed_server_ts, message.encode())])
    _script_inputs(monkeypatch, [message], then_exception=EOFError())

    client.main()

    out = capsys.readouterr().out.splitlines()
    assert any(
        line.strip() == f"{fixed_client_ts}:{fixed_server_ts}:{fixed_client_ts}:{message}"
        for line in out
    ), f"Expected formatted echo line not found in output. Got: {out}"

    from hacker_echo_client import HOST, PORT
    assert PORT == 12347, f"The Hacker's Edition service uses port 12347, not {PORT}"
    sock = instances[0]
    assert sock.connected_to == (HOST, PORT)

    # The header and payload may be sent in one call or two; check the byte stream
    sent = b"".join(sock.sent)
    expected = struct.pack(HEADER_FORMAT, TYPE_REQUEST, 1, fixed_client_ts, 0.0,
                           len(message.encode())) + message.encode()
    assert sent == expected, (
        f"Client did not send the expected bytes.\nExpected: {expected!r}\nGot:      {sent!r}")


def test_hacker_client_reassembles_reply_delivered_in_pieces(monkeypatch, capsys):
    """The reply arrives in small, oddly-sized chunks, as TCP is allowed to do."""
    import hacker_echo_client as client

    import time as _time
    monkeypatch.setattr(_time, "time", lambda: 5.0, raising=False)

    message = "a longer message that arrives in several pieces " * 40  # about 2 KB
    reply = _reply(1, 5.0, 6.0, message.encode())
    # Split the header itself and the payload at awkward points
    cuts = [0, 7, HEADER_SIZE + 1, HEADER_SIZE + 600, HEADER_SIZE + 1500, len(reply)]
    chunks = [reply[cuts[i]:cuts[i + 1]] for i in range(len(cuts) - 1)]

    _make_fake_socket(monkeypatch, chunks)
    _script_inputs(monkeypatch, [message], then_exception=EOFError())

    client.main()

    out = capsys.readouterr().out
    assert f"5.0:6.0:5.0:{message}" in out, (
        "The client did not print the full message. Does it keep calling recv() "
        "until the whole header and the whole payload have arrived?")


def test_hacker_client_exits_gracefully_on_eof(monkeypatch, capsys):
    import hacker_echo_client as client

    _make_fake_socket(monkeypatch, [])
    _script_inputs(monkeypatch, [], then_exception=EOFError())
    import time as _time
    monkeypatch.setattr(_time, "time", lambda: 0.0, raising=False)

    client.main()

    out = capsys.readouterr().out
    assert "Type messages" in out
