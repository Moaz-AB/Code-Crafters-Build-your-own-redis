import socket

def main():
    print("Server starting...")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    connection, _ = server_socket.accept()
    print("Client connected.")

    while True:
        data = connection.recv(1024)
        if not data:
            break  # connection closed
        print(f"Received: {data}")
        connection.sendall(b"+PONG\r\n")

if __name__ == "__main__":
    main()
