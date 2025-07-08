import socket
import threading

def handle_client(connection):
    while True:
        data = connection.recv(1024)
        if not data:
            break
        connection.sendall(b"+PONG\r\n")
    connection.close()

def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    print("Server is running and waiting for clients...")

    while True:
        client_conn, _ = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_conn,))
        client_thread.start()

if __name__ == "__main__":
    main()

