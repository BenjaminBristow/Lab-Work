import builtins
import os
import sys
import io
import types
from typing import List, Tuple

# Ensure project root is on sys.path so `import echo_client` works
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


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


def test_client_sends_timestamp_and_prints_formatted_response(monkeypatch, capsys):
    # Import after monkeypatch helpers are defined
    import echo_client as client

    # Fixed timestamps to make behavior deterministic
    fixed_client_ts = 1730380000.123456
    fixed_server_ts = 1730380000.234567

    # time.time() should return the client timestamp when called by the client
    # We keep it constant to reflect spec: client uses a single timestamp per message
    import time as _time
    monkeypatch.setattr(_time, "time", lambda: fixed_client_ts, raising=False)

    # Prepare fake socket to return server's response per README spec:
    # Server responds: "<server_ts>:<client_ts>:<message>\n"
    message = "Hello, World!"
    server_payload = f"{fixed_server_ts}:{fixed_client_ts}:{message}\n".encode()
    FakeSocket, instances = _make_fake_socket(monkeypatch, [server_payload])

    # Simulate one user input, then EOF to exit
    _script_inputs(monkeypatch, [message], then_exception=EOFError())

    # Run main
    client.main()

    # Capture output and validate printed line contains the expected formatted response
    out = capsys.readouterr().out.splitlines()
    # Look for the final echo line (ignore banner lines)
    assert any(
        line.strip(
        ) == f"{fixed_client_ts}:{fixed_server_ts}:{fixed_client_ts}:{message}"
        for line in out
    ), f"Expected formatted echo line not found in output. Got: {out}"

    # Validate the client connected to the configured HOST/PORT and sent the right payload
    from echo_client import HOST, PORT
    assert len(instances) >= 1
    sock = instances[0]
    assert sock.connected_to == (HOST, PORT)
    assert len(sock.sent) >= 1
    expected_sent = f"{fixed_client_ts}:{message}".encode()
    assert sock.sent[0] == expected_sent, (
        f"Client did not send expected payload.\n"
        f"Expected: {expected_sent!r}\nGot: {sock.sent[0]!r}")


def test_client_exits_gracefully_on_eof(monkeypatch, capsys):
    import echo_client as client

    # Socket shouldn’t actually connect anywhere
    _make_fake_socket(monkeypatch, [])

    # Immediately raise EOFError on first input call (Ctrl+D)
    _script_inputs(monkeypatch, [], then_exception=EOFError())

    # time.time doesn't matter here, but patch for safety
    import time as _time
    monkeypatch.setattr(_time, "time", lambda: 0.0, raising=False)

    # Should not raise; should exit cleanly
    client.main()

    out = capsys.readouterr().out
    # Don’t enforce exact message text; just ensure no stack trace and banner appears
    assert "Type messages" in out
