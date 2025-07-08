import socket
import threading

def handle_client(connection):
    try:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            # Respond with +PONG\r\n regardless of input for now
            connection.sendall(b"+PONG\r\n")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        connection.close()

def main():
    print("Server starting on localhost:6379...")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        conn, _ = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.start()

if __name__ == "__main__":
    main()



