#!/usr/bin/env python3

import socket
from threading import Thread, Lock
from packet import Packet

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 13337         # Port to listen on (non-privileged ports are > 1023)
MAX_PACKET_SIZE = 33000

add_packet_lock = Lock()


class TCPRecvAssemble:
    def __init__(self, pid):
        self.pid = pid
        self.packet_list = []

    def add_packet(self, packet):
        if Packet.checksum(packet) != packet.checksum:
            return False

        if packet.get_type() == 'FIN' and packet.seq > len(self.packet_list):
            return False

        if packet in self.packet_list:
            return True

        self.packet_list.append(packet)
        return True

    def __eq__(self, other):
        return self.pid == other.pid

    def write_out(self):
        with open(f'{self.pid}.out', 'wb+') as f:
            self.packet_list.sort()
            for packet in self.packet_list:
                f.write(packet.data)

    def get_reply_packet(self, packet):
        seq = packet.seq
        if packet.get_type() == 'FIN':
            return Packet('FIN-ACK', self.pid, seq, 0, '')
        else:
            return Packet('ACK', self.pid, seq, 0, '')


class TCPRecvThread(Thread):
    def __init__(self, sock, addr, data, all_tcp_recv):
        Thread.__init__(self)
        self.sock = sock
        self.addr = addr
        self.data = data
        self.all_tcp_recv = all_tcp_recv

    def run(self):
        recv_packet = Packet.from_bytes(self.data)
        print(f'{self.addr} -> {str(recv_packet)}')

        packet_id = recv_packet.id
        packet_seq = recv_packet.seq
        curr_tcp_recv = TCPRecvAssemble(packet_id)
        reply = None

        with add_packet_lock:
            for instance in self.all_tcp_recv:
                if instance == curr_tcp_recv:
                    curr_tcp_recv = instance
                    if (curr_tcp_recv.add_packet(recv_packet)):
                        reply = curr_tcp_recv.get_reply_packet(recv_packet)
            else:
                self.all_tcp_recv.append(curr_tcp_recv)
                if (curr_tcp_recv.add_packet(recv_packet)):
                    reply = curr_tcp_recv.get_reply_packet(recv_packet)

        if reply is not None:
            self.sock.sendto(reply.to_bytes(), self.addr)
            print(f'{self.addr} <- {str(reply)}')

            if reply.get_type() == 'FIN-ACK':
                curr_tcp_recv.write_out()
                self.all_tcp_recv.remove(curr_tcp_recv)
                print(
                    f'[i] Written file with id {packet_id} to {packet_id}.out')
        else:
            print(f'DROP {str(recv_packet)}')


class TCPRecv:
    def __init__(self, addr):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(addr)
            all_tcp_recv = []

            print(f'[i] Listening on {addr}')

            while True:
                data, addr = s.recvfrom(MAX_PACKET_SIZE)
                conn_thread = TCPRecvThread(s, addr, data, all_tcp_recv)
                conn_thread.start()


if __name__ == "__main__":
    addr_port = int(input('Enter port to bind: '))
    addr = (HOST, addr_port)
    print(addr)

    TCPRecv(addr)
