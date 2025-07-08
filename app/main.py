import socket  # noqa: F401

def main():
    print("Server starting...")

    # Step 1: Create a TCP server socket
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    # Step 2: Accept a client connection
    connection, _ = server_socket.accept()
    print("Client connected.")

    # Step 3: Send the Redis-style PONG response
    connection.sendall(b"+PONG\r\n")
    print("Sent: +PONG")

if __name__ == "__main__":
    main()

    