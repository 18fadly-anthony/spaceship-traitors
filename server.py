#!/usr/bin/env python3

import sys
import socket

ip = '127.0.0.1'
port = 5005 # TODO add ability to set port with commandline option
buffer_size = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ip, port))
s.listen(1)

conn, addr = s.accept()
print('Connection address:', addr)
while 1:
    data = conn.recv(buffer_size)
    if not data: break
    print("received data:", data)
    conn.send(data)  # echo
conn.close()
