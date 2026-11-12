import builtins
import os
import struct
import sys
from typing import List, Tuple

# Ensure project root is on sys.path so `import struct_echo_client` works
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Packet format from the lab specification (Stage 1, Task 2)
FORMAT = "!BHdd32s"
MSG_SIZE = struct.calcsize(FORMAT)  # 51 bytes
TYPE_REQUEST = 1
TYPE_REPLY = 2


def _make_fake_socket(monkeypatch, scripted_recv: List[bytes]):
    """
    Create a fake socket class that records connect/sendall calls and
    returns the provided recv payloads sequentially.
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
            self.sent.append(data)

        def recv(self, _bufsize: int) -> bytes:
            if self._recv_queue:
                return self._recv_queue.pop(0)
            # Simulate remote close when no scripted data left
            return b""

        def close(self):
            self.closed = True

    def fake_socket_factory(*args, **kwargs):
        return FakeSocket(*args, **kwargs)

    import socket as _socket

    monkeypatch.setattr(_socket, "socket", fake_socket_factory, raising=True)

    # Expose tracking for inspection in tests
    return FakeSocket, created_instances


def _script_inputs(monkeypatch, inputs: List[str], then_exception: BaseException | None = None):
    seq = list(inputs)

    def _fake_input(prompt: str = "") -> str:
        if seq:
            return seq.pop(0)
        if then_exception is not None:
            raise then_exception
        # End of input stream; simulate EOF
        raise EOFError

    monkeypatch.setattr(builtins, "input", _fake_input, raising=True)


def test_struct_client_sends_packed_request_and_prints_formatted_response(monkeypatch, capsys):
    # Import after monkeypatch helpers are defined
    import struct_echo_client as client

    # Fixed timestamps to make behavior deterministic
    fixed_client_ts = 1730380000.123456
    fixed_server_ts = 1730380000.234567

    import time as _time
    monkeypatch.setattr(_time, "time", lambda: fixed_client_ts, raising=False)

    # Server reply per the specification: type 2, same sequence number and
    # client timestamp, plus the server timestamp
    message = "Hello, World!"
    server_payload = struct.pack(FORMAT, TYPE_REPLY, 1, fixed_client_ts,
                                 fixed_server_ts, message.encode())
    FakeSocket, instances = _make_fake_socket(monkeypatch, [server_payload])

    # Simulate one user input, then EOF to exit
    _script_inputs(monkeypatch, [message], then_exception=EOFError())

    client.main()

    # The printed line has the same format as in Stage 1, Task 1B
    out = capsys.readouterr().out.splitlines()
    assert any(
        line.strip() == f"{fixed_client_ts}:{fixed_server_ts}:{fixed_client_ts}:{message}"
        for line in out
    ), f"Expected formatted echo line not found in output. Got: {out}"

    # Validate the client connected to the configured HOST/PORT
    from struct_echo_client import HOST, PORT
    assert PORT == 12346, f"The struct echo service uses port 12346, not {PORT}"
    assert len(instances) >= 1
    sock = instances[0]
    assert sock.connected_to == (HOST, PORT)

    # Validate the request bytes: exactly one 51-byte packet with the right fields
    assert len(sock.sent) >= 1
    sent = b"".join(sock.sent)
    assert len(sent) == MSG_SIZE, (
        f"Request should be exactly {MSG_SIZE} bytes, got {len(sent)}")
    expected_sent = struct.pack(FORMAT, TYPE_REQUEST, 1, fixed_client_ts, 0.0,
                                message.encode())
    assert sent == expected_sent, (
        f"Client did not send expected packet.\n"
        f"Expected: {struct.unpack(FORMAT, expected_sent)}\n"
        f"Got:      {struct.unpack(FORMAT, sent)}")


def test_struct_client_increments_sequence_number(monkeypatch, capsys):
    import struct_echo_client as client

    import time as _time
    monkeypatch.setattr(_time, "time", lambda: 5.0, raising=False)

    replies = [
        struct.pack(FORMAT, TYPE_REPLY, 1, 5.0, 6.0, b"one"),
        struct.pack(FORMAT, TYPE_REPLY, 2, 5.0, 6.0, b"two"),
    ]
    FakeSocket, instances = _make_fake_socket(monkeypatch, replies)
    _script_inputs(monkeypatch, ["one", "two"], then_exception=EOFError())

    client.main()

    sent = b"".join(instances[0].sent)
    assert len(sent) == 2 * MSG_SIZE, (
        f"Expected two {MSG_SIZE}-byte requests, got {len(sent)} bytes in total")
    first = struct.unpack(FORMAT, sent[:MSG_SIZE])
    second = struct.unpack(FORMAT, sent[MSG_SIZE:])
    assert first[1] == 1, f"First request should have sequence number 1, got {first[1]}"
    assert second[1] == 2, f"Second request should have sequence number 2, got {second[1]}"

    out = capsys.readouterr().out
    assert "5.0:6.0:5.0:one" in out and "5.0:6.0:5.0:two" in out, out


def test_struct_client_exits_gracefully_on_eof(monkeypatch, capsys):
    import struct_echo_client as client

    # Socket shouldn't actually connect anywhere
    _make_fake_socket(monkeypatch, [])

    # Immediately raise EOFError on first input call (Ctrl+D)
    _script_inputs(monkeypatch, [], then_exception=EOFError())

    import time as _time
    monkeypatch.setattr(_time, "time", lambda: 0.0, raising=False)

    # Should not raise; should exit cleanly
    client.main()

    out = capsys.readouterr().out
    assert "Type messages" in out
