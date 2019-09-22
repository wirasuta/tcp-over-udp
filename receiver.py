#!/usr/bin/env python3

import socket
import threading
from packet import Packet

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 13337         # Port to listen on (non-privileged ports are > 1023)


def handler(sock, addr, data):
    print(Packet.from_bytes(data))


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))

    print(f'Listening on port {PORT}')

    while True:
        data, addr = s.recvfrom(1024)
        print(addr)
        conn_thread = threading.Thread(target=handler, args=(s, addr, data))
        conn_thread.setDaemon(True)
        conn_thread.start()
