import select
import socket
import struct
import time

HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 12346       # Port of the struct (binary) echo service

# TODO: Write the struct format string for the packet described in Stage 1,
# Task 2 of the lab specification (type, sequence number, client timestamp,
# server timestamp, 32-byte message). Remember the byte order prefix.
FORMAT = "!BHdd32s"
MSG_SIZE = struct.calcsize(FORMAT)  # should be 51 bytes once FORMAT is correct

TYPE_REQUEST = 1
TYPE_REPLY = 2


def main():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Do not remove the following socket options. These options force the kernel to reuse the server port number. If you remove them, then you may see "Address already in use" errors when you restart the server quickly.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # TODO: Bind the socket to HOST and PORT, and serve multiple clients with
    # select.select(), as in your Stage 1, Task 1C server. For each client socket that is
    # ready to read:
    #   1. Receive MSG_SIZE bytes. Close the connection if the client closed it
    #      or if the packet does not have the expected size.
    #   2. Unpack the packet with struct.unpack(). Close the connection if the
    #      type is not TYPE_REQUEST.
    #   3. Pack and send a reply: type TYPE_REPLY, the same sequence number,
    #      client timestamp and message, and time.time() as the server timestamp.
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    socket_list = [server_socket]

    while True:
        readable, _, _ = select.select(socket_list, [], [])

        for sock in readable:
            # Case 1: New incoming connection on the main server socket
            if sock is server_socket:
                client_socket, client_addr = server_socket.accept()
                print(f"Accepted new connection from {client_addr}")
                socket_list.append(client_socket)

            # Case 2: Incoming message from an existing client socket
            else:
                data = sock.recv(MSG_SIZE)

                if len(data) != MSG_SIZE: # is all the data there or is it empty?
                    socket_list.remove(sock) # if not then remove faulty connection and continue looping
                    sock.close()
                    continue

                msg_type, seq, client_ts, server_ts, message = struct.unpack(FORMAT, data) 
                if msg_type != TYPE_REQUEST:
                    socket_list.remove(sock)
                    sock.close()
                    continue

                response_struct = struct.pack(FORMAT, TYPE_REPLY, seq, client_ts, time.time(), message)
                sock.sendall(response_struct)

if __name__ == "__main__":
    main()
