import socket
import struct
import time

HOST = '10.0.0.2'  # Server address (Mininet: h2)
PORT = 12347       # Port of the Hacker's Edition echo service

# TODO: Use the same header format string as in hacker_echo_server.py
HEADER_FORMAT = ""
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # should be 21 bytes

TYPE_REQUEST = 1
TYPE_REPLY = 2


def recv_exact(sock, n):
    """Read exactly n bytes from a TCP socket and return them.

    Raise ConnectionError if the server closes the connection before all
    n bytes have arrived.
    """
    # TODO: Implement this function
    raise NotImplementedError


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # TODO: Connect to the server

    print("Type messages and press Enter")
    print("To quit: Ctrl+C or Ctrl+D")

    seq = 1

    while True:
        try:
            user_msg = input("> ")
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        # TODO: Send the header followed by the UTF-8 payload

        # TODO: Use recv_exact() to read the reply header, then the payload, and
        # print the reply in the same format as Stage 1, Tasks 1B and 2B

        # TODO: Increase the sequence number


if __name__ == "__main__":
    main()
