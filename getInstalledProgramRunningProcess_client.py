#!/usr/bin/python3

import socket

HOST = "127.0.0.1"  # The server HOST
PORT = 17777  # The Server Port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Test YOYO TEST socket")
    data = s.recv(1024)

print(f"Received from server data: {repr(data)}")
