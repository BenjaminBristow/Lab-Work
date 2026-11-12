import socket
import time
import select

HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 12345       # Port to listen on


def main():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Do not remove the following socket options. These options force the kernel to reuse the server port number. If you remove them, then you may see "Address already in use" errors when you restart the server quickly.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # TODO: Bind the socket to the specified HOST and PORT and accept incoming connectionections
    server_socket.bind((HOST,PORT))
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}...")

    # List of sockets to monitor for incoming data
    sockets_list = [server_socket]

    while True:
        # Wait until at least one socket is ready for reading
        readable, _, _ = select.select(sockets_list, [], [])

        for sock in readable:
            # Case 1: New incoming connection on the main server socket
            if sock is server_socket:
                client_socket, client_addr = server_socket.accept()
                print(f"Accepted new connection from {client_addr}")
                sockets_list.append(client_socket)

            # Case 2: Incoming message from an existing client socket
            else:
                data = sock.recv(1024)
                if data:
                    # Extract the original message (or echo back with new server timestamp)
                    msg = data.decode()
                    # If client sends "timestamp:message", split it to keep just the message
                    if ":" in msg:
                        _, text = msg.split(":", 1)
                    else:
                        text = msg

                    response = f"{time.time()}:{text}".encode()
                    sock.sendall(response)
                else:
                    # Empty data means client closed the connection
                    print("Client disconnected")
                    sockets_list.remove(sock)
                    sock.close()


if __name__ == "__main__":
    main()