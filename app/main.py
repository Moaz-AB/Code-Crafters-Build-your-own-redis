import socket
import sys

store = {}
config = {
    "dir": "/tmp",
    "dbfilename": "dump.rdb"
}

# Parse command-line arguments
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
    res = f"*{len(arr)}\r\n"
    for item in arr:
        res += f"${len(item)}\r\n{item}\r\n"
    return res.encode()

def handle_command(cmd):
    if not cmd:
        return b""

    command = cmd[0].upper()

    if command == "PING":
        return encode_simple_string("PONG")
    elif command == "ECHO" and len(cmd) > 1:
        return encode_bulk_string(cmd[1])
    elif command == "SET" and len(cmd) > 2:
        store[cmd[1]] = cmd[2]
        return encode_simple_string("OK")
    elif command == "GET" and len(cmd) > 1:
        val = store.get(cmd[1])
        return encode_bulk_string(val) if val else b"$-1\r\n"
    elif command == "CONFIG" and len(cmd) > 2 and cmd[1].upper() == "GET":
        key = cmd[2]
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
            cmd = parse_request(data)
            response = handle_command(cmd)
            conn.sendall(response)
