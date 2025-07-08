import socket
import threading
import time

# Key-value store with expiry support
store = {}

# Parse RESP into list of strings
def parse_redis_message(data):
    try:
        lines = data.decode().split("\r\n")
        if lines[0].startswith("*"):
            count = int(lines[0][1:])
            args = []
            i = 1
            while i < len(lines) and len(args) < count:
                if lines[i].startswith("$"):
                    args.append(lines[i + 1])
                    i += 2
                else:
                    i += 1
            return args
    except Exception as e:
        print("Parsing error:", e)
    return []

# Check if a key has expired
def is_expired(key):
    if key not in store:
        return True
    expires_at = store[key].get("expires_at")
    if expires_at is None:
        return False
    return time.time() * 1000 > expires_at

# Handle each client in a thread
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

            elif command == "set":
                key = args[1]
                value = args[2]
                expires_at = None

                if len(args) > 4 and args[3].lower() == "px":
                    try:
                        px = int(args[4])
                        expires_at = time.time() * 1000 + px
                    except:
                        pass  # invalid px value, ignore

                store[key] = {
                    "value": value,
                    "expires_at": expires_at
                }
                connection.sendall(b"+OK\r\n")

            elif command == "get":
                key = args[1]
                if key not in store or is_expired(key):
                    store.pop(key, None)  # remove expired key
                    connection.sendall(b"$-1\r\n")
                else:
                    value = store[key]["value"]
                    response = f"${len(value)}\r\n{value}\r\n"
                    connection.sendall(response.encode())

            else:
                connection.sendall(b"-Error: Unknown command\r\n")

    except Exception as e:
        print("Client error:", e)
    finally:
        connection.close()

# Start server
def main():
    print("Server running on localhost:6379")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        conn, _ = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()

if __name__ == "__main__":
    main()






