import socket
import sys

store = {}
config = {
    "dir": "/tmp",
    "dbfilename": "dump.rdb"
}

# Handle CLI args
args = sys.argv
if "--dir" in args:
    config["dir"] = args[args.index("--dir") + 1]
if "--dbfilename" in args:
    config["dbfilename"] = args[args.index("--dbfilename") + 1]

# RESP encoders
def encode_simple_string(s):
    return f"+{s}\r\n".encode()

def encode_bulk_string(s):
    if s is None:
        return b"$-1\r\n"
    return f"${len(s)}\r\n{s}\r\n".encode()

def encode_array(arr):
    encoded = f"*{len(arr)}\r\n"
    for item in arr:
        encoded += f"${len(item)}\r\n{item}\r\n"
    return encoded.encode()

# RESP parser
def parse_request(data):
    lines = data.decode().split("\r\n")
    return [line for line in lines if line and not line.startswith("*") and not line.startswith("$")]

# Command handler
def handle_command(cmd_parts):
    if not cmd_parts:
        return encode_simple_string("")

    command = cmd_parts[0].upper()

    if command == "PING":
        return encode_simple_string("PONG")
    elif command == "ECHO" and len(cmd_parts) > 1:
        return encode_bulk_string(cmd_parts[1])
    elif command == "SET" and len(cmd_parts) > 2:
        store[cmd_parts[1]] = cmd_parts[2]
        return encode_simple_string("OK")
    elif command == "GET" and len(cmd_parts) > 1:
        return encode_bulk_string(store.get(cmd_parts[1]))
    elif command == "CONFIG" and len(cmd_parts) == 3 and cmd_parts[1].upper() == "GET":
        param = cmd_parts[2]
        if param in config:
            return encode_array([param, config[param]])
        else:
            return encode_array([])
    else:
        return b"-ERR unknown command\r\n"

# Main server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("localhost", 6379))
    s.listen()
    print("Server running on localhost:6379")
    while True:
        conn, addr = s.accept()
        with conn:
            data = conn.recv(1024)
            if not data:
                continue
            cmd_parts = parse_request(data)
            response = handle_command(cmd_parts)
            conn.sendall(response)






