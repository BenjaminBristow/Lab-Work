import socket
import time

HOST = '10.0.0.2'  # Server address (Mininet: h2)
PORT = 12345       # Echo service port


def main():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # TODO: Connect to the echo server and get a socket object
    server_socket.connect((HOST, PORT))

    print("Type messages and press Enter")
    print("To quit: Ctrl+C or Ctrl+D")

    while True:
        try:
            user_msg = input("> ")
        except EOFError:
            break
        except KeyboardInterrupt:
            break

        # TODO: Append timestamp to message and send to server
        message = f"{time.time()}:{user_msg}".encode()
        server_socket.sendall(message)

        # TODO: Receive response from server and print formatted output
        recieved = server_socket.recv(1024)
        print(recieved.decode())
        
    server_socket.close()

if __name__ == "__main__":
    main()
