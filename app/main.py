import socket
import threading

# In-memory key-value store
store = {}

# Parse Redis RESP protocol into Python list
def parse_redis_message(data):
    try:
        lines = data.decode().split("\r\n")
        if lines[0].startswith("*"):
            count = int(lines[0][1:])
            args = []
            i = 1
            while i < len(lines) and len(args) < count:
                if lines[i].startswith("$"):
                    length = int(lines[i][1:])
                    args.append(lines[i + 1])
                    i += 2
                else:
                    i += 1
            return args
    except Exception as e:
        print("Parsing error:", e)
    return []

# Handle each client in its own thread
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

            elif command == "set" and len(args) >= 3:
                key = args[1]
                value = args[2]
                store[key] = value
                connection.sendall(b"+OK\r\n")

            elif command == "get" and len(args) >= 2:
                key = args[1]
                value = store.get(key)
                if value is not None:
                    response = f"${len(value)}\r\n{value}\r\n"
                    connection.sendall(response.encode())
                else:
                    connection.sendall(b"$-1\r\n")

            else:
                connection.sendall(b"-Error: Unknown command\r\n")

    except Exception as e:
        print(f"Client error: {e}")
    finally:
        connection.close()

# Create the server and accept clients
def main():
    print("Server starting on localhost:6379...")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        conn, _ = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()

if __name__ == "__main__":
    main()





