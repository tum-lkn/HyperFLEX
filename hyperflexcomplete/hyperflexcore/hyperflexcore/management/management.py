#!/bin/python
import socket

def sendToNetworkEmulator(message):
    ip = 'IP OF MININET VM'
    port = 'PORT TO LISTEN FOR REQUESTS'

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((ip, port))
        sock.sendall(message)
        received = sock.recv(1024)
    finally:
        sock.close()

    return received
