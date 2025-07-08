import socket
import threading

def parse_redis_message(data):
    try:
        lines = data.decode().split("\r\n")
        if lines[0].startswith("*"):  # Array
            count = int(lines[0][1:])
            args = []
            i = 1
            while i < len(lines) and len(args) < count:
                if lines[i].startswith("$"):
                    length = int(lines[i][1:])
                    args.append(lines[i+1])
                    i += 2
                else:
                    i += 1
            return args
    except Exception as e:
        print("Parsing error:", e)
    return []

def handle_client(connection):
    try:
        while True:
            data = connection.recv(1024)
            if not data:
                break

            args = parse_redis_message(data)
            if not args:
                continue

            command = args[0].lower()

            if command == "ping":
                connection.sendall(b"+PONG\r\n")
            elif command == "echo" and len(args) > 1:
                message = args[1]
                response = f"${len(message)}\r\n{message}\r\n"
                connection.sendall(response.encode())
            else:
                connection.sendall(b"-Error: Unknown command\r\n")

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




