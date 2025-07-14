import socket
import sys

store = {}
config = {
    "dir": "/tmp",
    "dbfilename": "dump.rdb"
}

# Parse CLI args
args = sys.argv
if "--dir" in args:
    config["dir"] = args[args.index("--dir") + 1]
if "--dbfilename" in args:
    config["dbfilename"] = args[args.index("--dbfilename") + 1]

def encode_simple_string(s):
    return f"+{s}\r\n".encode()

def encode_bulk_string(s):
    return f"${len(s)}\r\n{s}\r\n".encode()

def encode_array(arr):
    result = f"*{len(arr)}\r\n"
    for item in arr:
        result += f"${len(item)}\r\n{item}\r\n"
    return result.encode()

def handle_command(cmd_parts):
    if not cmd_parts:
        return encode_simple_string("")

    cmd = cmd_parts[0].upper()
    
    if cmd == "PING":
        return encode_simple_string("PONG")
    elif cmd == "ECHO" and len(cmd_parts) > 1:
        return encode_bulk_string(cmd_parts[1])
    elif cmd == "SET" and len(cmd_parts) > 2:
        store[cmd_parts[1]] = cmd_parts[2]
        return encode_simple_string("OK")
    elif cmd == "GET" and len(cmd_parts) > 1:
        val = store.get(cmd_parts[1])
        return encode_bulk_string(val) if val else b"$-1\r\n"
    elif cmd == "CONFIG" and len(cmd_parts) > 2 and cmd_parts[1].upper() == "GET":
        key = cmd_parts[2]
        if key in config:
            return encode_array([key, config[key]])
        else:
            return encode_array([])
    else:
        return encode_simple_string("")

def parse_request(data):
    lines = data.decode().split("\r\n")
    return [line for line in lines if line and not line.startswith(("*", "$"))]

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






