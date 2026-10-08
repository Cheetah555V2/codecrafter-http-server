import socket  # noqa: F401
import threading
import sys
import os

root_file_path = os.path.dirname(__file__)


def handle_request(client_socket, request_encrypt : bytes) -> None:
    
    request_encrypt = client_socket.recv(1024)
    request_decrypt : str = request_encrypt.decode("utf-8") ;print(request_decrypt)
    request = request_decrypt.split("\r\n")

    header = {}
    for i in range(1, len(request)):

        # continue for empty header (end of request)
        if request[i] == '':
            continue

        # map header to content
        for j in range(len(request[i])):
            if request[i][j] == ':':
                header_name = request[i][0 : j].lower()
                content = request[i][j+2 :]
                header[header_name] = content
                break
    print("HEADER :", header)

    request[0] = request[0].split(" ") # type: ignore

    respond = ""

    if request[0][0] == "GET":
        if request[0][1] == "/index.html" or request[0][1] == "/":
            respond = "HTTP/1.1 200 OK\r\n\r\n"
        elif request[0][1].startswith("/echo/"):
            respond =   "HTTP/1.1 200 OK\r\n" \
                        "Content-Type: text/plain\r\n" \
                        f"Content-Length: {len(request[0][1][6:])}\r\n\r\n" \
                        f"{request[0][1][6:]}"
        elif request[0][1] == "/user-agent":
            respond =   "HTTP/1.1 200 OK\r\n" \
                        "Content-Type: text/plain\r\n" \
                        f"Content-Length: {len(header["user-agent"])}\r\n\r\n" \
                        f"{header["user-agent"]}"
        elif request[0][1].startswith("/files/"):
            if os.path.exists(os.path.join(root_file_path, request[0][1][7:])):
                with open(os.path.join(root_file_path, request[0][1][7:]), 'r') as f:
                    file_content = f.read()
                    respond =   "HTTP/1.1 200 OK\r\n" \
                                "Content-Type: application/octet-stream\r\n" \
                                f"Content-Length: {len(file_content)}\r\n\r\n" \
                                f"{file_content}"
    elif request[0][0] == "POST":

        file_path = os.path.join(root_file_path, request[0][1][7:])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(request[-1])
        else:
            with open(file_path, 'x') as f:
                f.write(request[-1])

        respond = "HTTP/1.1 201 Created\r\n\r\n"
    
    if respond == "":
        respond = "HTTP/1.1 404 Not Found\r\n\r\n"

    client_socket.sendall(respond.encode("utf-8"))
    client_socket.close()


def main():
    global root_file_path
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    # handle arguments
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--directory":
            root_file_path = os.path.join(root_file_path, sys.argv[i + 1])
            i += 2

    while True:
        client_socket, address = server_socket.accept()
        threading.Thread(target=handle_request, args=(client_socket, address)).start()


if __name__ == "__main__":
    main()
