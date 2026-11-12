import socket
import struct
import time

HOST = '10.0.0.2'  # Server address (Mininet: h2)
PORT = 12346       # Port of the struct (binary) echo service

# TODO: Use the same format string as in struct_echo_server.py
FORMAT = "!BHdd32s"
MSG_SIZE = struct.calcsize(FORMAT)  # should be 51 bytes once FORMAT is correct

TYPE_REQUEST = 1
TYPE_REPLY = 2


def main():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # TODO: Connect to the struct echo server
    server_socket.connect((HOST, PORT))

    print("Type messages and press Enter")
    print("To quit: Ctrl+C or Ctrl+D")

    # Sequence numbers start at 1 and increase by one for every request
    seq = 1

    while True:
        try:
            user_msg = input("> ")
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        # TODO: Pack a request (type, sequence number, client timestamp,
        # server timestamp 0.0, message) and send it to the server
        data = struct.pack(FORMAT, TYPE_REQUEST, seq, time.time(), 0.0, user_msg.encode())
        server_socket.sendall(data)

        # TODO: Receive the MSG_SIZE-byte reply, unpack it, remove the zero-byte
        # padding from the message and print it in the same format as Stage 1, Task 1B:
        # <receive timestamp>:<server timestamp>:<client timestamp>:<message>
        recv_data = server_socket.recv(MSG_SIZE)
        msg_type, seq, client_ts, server_ts, message = struct.unpack(FORMAT, recv_data)
        message = message.rstrip(b'\x00').decode()
        response = f"{time.time()}:{server_ts}:{client_ts}:{message}"
        print(response)

        # TODO: Increase the sequence number
        seq += 1


if __name__ == "__main__":
    main()
