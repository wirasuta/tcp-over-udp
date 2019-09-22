#!/usr/bin/env python3

import socket
from threading import Thread, Lock
from packet import Packet

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
MAX_PACKET_SIZE = 33000

add_packet_lock = Lock()
find_defragment_lock = Lock()


class TCPRecvDefragment:
    """
    Contains utility to defragment packet by storing received packets
    into a list and sorting them by sequence number before written out.
    Identified by sender address and packet id to support multiple
    file on single connection and multiple sender.
    """

    def __init__(self, sender_addr, pid):
        self.sender_addr = sender_addr
        self.pid = pid
        self.packet_list = []

    def add_packet(self, packet):
        if Packet.checksum(packet) != packet.checksum:
            return False

        if packet.get_type() == 'FIN' and packet.seq > len(self.packet_list):
            return False

        with add_packet_lock:
            if packet in self.packet_list:
                return True

            self.packet_list.append(packet)

        return True

    def __eq__(self, other):
        return self.sender_addr == other.sender_addr and self.pid == other.pid

    def write_out(self):
        filename = self.sender_addr[0].replace(
            '.', '_') + '_' + str(self.sender_addr[1]) + '_' + str(self.pid) + '.out'

        with open(filename, 'wb+') as f:
            self.packet_list.sort()
            for packet in self.packet_list:
                f.write(packet.data)

        return filename


class TCPRecvThread(Thread):
    """
    Thread for handling incoming data by doing these things:
    1. Recreate packet from received bytes
    2. Get packet defragment object for the corresponding packet 
       or create a new one if it doesn't exist
    3. Add packet to defragment object
    4. Get corresponding acknowledgement packet if the packet is 
       added successfully
    5. Send reply
    6. If packet is complete, write out to file
    """

    def __init__(self, sock, sender_addr, data, all_tcp_recv):
        Thread.__init__(self)
        self.sock = sock
        self.sender_addr = sender_addr
        self.data = data
        self.all_tcp_recv = all_tcp_recv

    def run(self):
        recv_packet = Packet.from_bytes(self.data)
        print(f'{self.sender_addr} -> {str(recv_packet)}')

        packet_id = recv_packet.id
        packet_seq = recv_packet.seq
        curr_tcp_recv = TCPRecvDefragment(self.sender_addr, packet_id)
        reply = None

        with find_defragment_lock:
            for instance in self.all_tcp_recv:
                if instance == curr_tcp_recv:
                    curr_tcp_recv = instance
                    break
            else:
                self.all_tcp_recv.append(curr_tcp_recv)

        if (curr_tcp_recv.add_packet(recv_packet)):
            reply = recv_packet.get_reply()

        if reply is not None:
            self.sock.sendto(reply.to_bytes(), self.sender_addr)
            print(f'{self.sender_addr} <- {str(reply)}')

            if reply.get_type() == 'FIN-ACK':
                filename = curr_tcp_recv.write_out()

                if curr_tcp_recv in self.all_tcp_recv:
                    self.all_tcp_recv.remove(curr_tcp_recv)
                print(
                    f'[i] Written file from {self.sender_addr} with id {packet_id} to {filename}')
        else:
            print(f'DROP {str(recv_packet)}')


class TCPRecv:
    """
    Emulate TCP receiving end by binding to specific address
    and spawn a handler thread for every incoming data 
    """

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

    TCPRecv(addr)
