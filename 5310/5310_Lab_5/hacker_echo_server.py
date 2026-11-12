import select
import socket
import struct
import time

HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 12347       # Port of the Hacker's Edition echo service

# TODO: Write the struct format string for the header described in the
# Hacker's Edition (type, sequence number, client timestamp, server timestamp,
# payload length). The payload follows the header and is not part of FORMAT.
HEADER_FORMAT = ""
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # should be 21 bytes

TYPE_REQUEST = 1
TYPE_REPLY = 2


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Do not remove the following socket options.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # TODO: Implement a select()-based echo server for variable-length messages.
    # Your server must never block waiting for one client while other clients
    # have complete messages to be answered. See the lab specification.


if __name__ == "__main__":
    main()
