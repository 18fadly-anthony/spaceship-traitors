#!/usr/bin/env python3

import sys
import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 5005 # TODO add ability to set port
BUFFER_SIZE = 1024

def send(output):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.sendall(output.encode('utf-8'))
    data = s.recv(BUFFER_SIZE)
    s.close()

def recieve():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    data = s.recv(BUFFER_SIZE)
    s.close()
    print("received data:", data)

send("initial")
recieve() 
