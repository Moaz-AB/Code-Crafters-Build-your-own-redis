import threading

def handle_client(connection):
    while True:
        connection.sendall(b"+PONG\r\n")

while True:
    conn, _ = server_socket.accept()
    threading.Thread(target=handle_client, args=(conn,)).start()
def parse_resp_command(data):
    parts = data.split(b"\r\n")
    array_len = int(parts[0][1:])
    elements = []
    i = 2
    while len(elements) < array_len:
        elements.append(parts[i])
        i += 2
    return elements

def handle_client(connection):
    while True:
        data = connection.recv(1024)
        if not data:
            break

        command_parts = parse_resp_command(data)

        if len(command_parts) == 1 and command_parts[0].lower() == b"ping":
            connection.sendall(b"+PONG\r\n")
        elif len(command_parts) == 2 and command_parts[0].lower() == b"echo":
            message = command_parts[1]
            response = b"$" + str(len(message)).encode() + b"\r\n" + message + b"\r\n"
            connection.sendall(response)
        else:
            connection.sendall(b"-Unknown command\r\n")

    connection.close()


