#!/usr/bin/env python3

import socket
import threading
from packet import Packet

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 13337         # Port to listen on (non-privileged ports are > 1023)
MAX_PACKET_SIZE = 33000

# TODO: Check for packet completeness
# TODO: File sequencing and sequencing
# Each file id recieve should have its own thread (?)


class TCPRecvThread(Thread):
    def __init__(self):
        pass

    def run(self):
        pass


class TCPRecv:
    def __init__(self, dest, timeout, files):
        pass

    @staticmethod
    def packets_to_file(filename):
        pass


def handler(sock, addr, data):
    recv_packet = Packet.from_bytes(data)
    print(f'{addr} -> {str(recv_packet)}')

    reply_type = 'ACK' if recv_packet.get_type() == 'DATA' else 'FIN-ACK'
    packet_id = recv_packet.id
    packet_seq = recv_packet.seq

    reply_packet = Packet(reply_type, packet_id, packet_seq, 0, '')
    sock.sendto(reply_packet.to_bytes(), addr)
    print(f'{addr} <- {str(reply_packet)}')


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))

    print(f'Listening on port {PORT}')

    while True:
        data, addr = s.recvfrom(MAX_PACKET_SIZE)
        conn_thread = threading.Thread(target=handler, args=(s, addr, data))
        conn_thread.start()
