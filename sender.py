#!/usr/bin/env python3

import socket
from threading import Thread, Event, Lock
from packet import Packet

DEST_HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
DEST_PORT = 13337        # Port to listen on (non-privileged ports are > 1023)

HOST = '127.0.0.1'
PORT = 14045

MAX_PACKET_SIZE = 33000
MESSAGE = b'A' * 16
MESSAGE2 = b'B' * 32
MESSAGE3 = b'C' * 32768


class TCPSendThread(Thread):
    def __init__(self, packets, dest, event):
        Thread.__init__(self)
        self.stopped = event
        self.dest = dest
        self.unacknowledged_packets = packets

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((HOST, PORT))
            ack_stop_flag = Event()
            ack_thread = TCPAckThread(
                self.unacknowledged_packets, sock, ack_stop_flag)
            ack_thread.start()

            for unacknowledged_packet in self.unacknowledged_packets:
                sock.sendto(unacknowledged_packet.to_bytes(), self.dest)
                print(f'{self.dest} <- {unacknowledged_packet}')

            while not self.stopped.wait(1):
                if len(self.unacknowledged_packets) == 0:
                    ack_stop_flag.set()
                    self.stopped.set()
                for unacknowledged_packet in self.unacknowledged_packets:
                    sock.sendto(
                        unacknowledged_packet.to_bytes(), self.dest)
                    print(f'Retrying to send {unacknowledged_packet}')

            ack_thread.join()

        print(f'All package sent!')


class TCPAckThread(Thread):
    def __init__(self, unacknowledged_packets, sock, event):
        Thread.__init__(self)
        self.stopped = event
        self.unacknowledged_packets = unacknowledged_packets
        self.sock = sock

    def run(self):
        print(f'Listening on port {PORT}')

        while not self.stopped.is_set():
            data, addr = self.sock.recvfrom(MAX_PACKET_SIZE)
            ack_packet = Packet.from_bytes(data)
            print(f'{addr} -> {ack_packet}')

            self.unacknowledged_packets.remove(ack_packet)
            if (ack_packet.get_type() == 'FIN-ACK'):
                self.stopped.set()

        print(f'All package acknowledged')


if __name__ == '__main__':
    pack1 = Packet('DATA', Packet.pick_id(), 0, len(MESSAGE), MESSAGE)
    pack2 = Packet('DATA', Packet.pick_id(), 0, len(MESSAGE2), MESSAGE2)
    pack3 = Packet('FIN', Packet.pick_id(), 0, len(MESSAGE3), MESSAGE3)
    packets = [pack1, pack2, pack3]
    dest = (DEST_HOST, DEST_PORT)
    stop_flag = Event()

    send_thread = TCPSendThread(packets, dest, stop_flag)
    send_thread.start()
    send_thread.join()
