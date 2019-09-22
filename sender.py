#!/usr/bin/env python3

import socket
from threading import Thread, Event, Lock
from packet import Packet
from itertools import chain, islice
from random import randint

HOST = '127.0.0.1'
PORT = 14045

MAX_DATA_SIZE = 32768
MAX_PACKET_SIZE = 33000
MESSAGE = b'A' * 16
MESSAGE2 = b'B' * 32
MESSAGE3 = b'C' * 32768


class TCPSendThread(Thread):
    def __init__(self, src, dest, timeout, packets, event):
        Thread.__init__(self)
        self.stopped = event
        self.src = src
        self.dest = dest
        self.timeout = timeout
        self.unacknowledged_packets = packets
        self.pid = self.unacknowledged_packets[0].id

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(self.src)

            ack_thread = TCPAckThread(
                self.pid, self.unacknowledged_packets, sock)
            ack_thread.start()

            for unacknowledged_packet in self.unacknowledged_packets:
                sock.sendto(unacknowledged_packet.to_bytes(), self.dest)
                print(f'{self.dest} <- {unacknowledged_packet}')

            while not self.stopped.wait(self.timeout):
                if len(self.unacknowledged_packets) == 0:
                    self.stopped.set()
                for unacknowledged_packet in self.unacknowledged_packets:
                    sock.sendto(
                        unacknowledged_packet.to_bytes(), self.dest)
                    print(f'{self.dest} <- RETR - {unacknowledged_packet}')

            ack_thread.join()

        print(f'[i] All package for id {self.pid} sent!')


class TCPAckThread(Thread):
    def __init__(self, pid, unacknowledged_packets, sock):
        Thread.__init__(self)
        self.stopped = Event()
        self.unacknowledged_packets = unacknowledged_packets
        self.sock = sock
        self.pid = pid

    def run(self):
        while not self.stopped.is_set():
            data, addr = self.sock.recvfrom(MAX_PACKET_SIZE)
            ack_packet = Packet.from_bytes(data)
            print(f'{addr} -> {ack_packet}')

            self.unacknowledged_packets.remove(ack_packet)
            if (ack_packet.get_type() == 'FIN-ACK'):
                self.stopped.set()

        print(f'[i] All package for id {self.pid} acknowledged!')


class TCPSend:
    def __init__(self, dest, timeout, files):
        all_packets = []
        for file_to_split in files:
            all_packets.append(list(self.file_to_packets(file_to_split)))

        stop_flags = []
        send_threads = []
        base_port = randint(1025, 13336)
        for idx, single_file_packets in enumerate(all_packets):
            stop_flag = Event()
            stop_flags.append(stop_flag)

            src = (HOST, base_port + idx)

            send_thread = TCPSendThread(
                src, dest, timeout, single_file_packets, stop_flag)
            send_threads.append(send_thread)
            send_thread.start()

        for idx, thread in enumerate(send_threads):
            thread.join()
            print(f'[i] Thread {idx} done!')

    @staticmethod
    def file_to_packets(filename):
        try:
            with open(filename, 'rb') as file_to_split:
                pid = Packet.pick_id()
                seq = 0
                chunk = file_to_split.read(MAX_DATA_SIZE)
                while chunk:
                    next_chunk = file_to_split.read(MAX_DATA_SIZE)
                    if next_chunk:
                        yield Packet('DATA', pid, seq, len(chunk), chunk)
                        chunk = next_chunk
                    else:
                        yield Packet('FIN', pid, seq, len(chunk), chunk)
                        chunk = False
                    seq += 1
        except OSError as err:
            print(f'File {filename} doesn\'t exist')


if __name__ == '__main__':
    dest_ip = input('Enter destination (IP): ')
    dest_port = input('Enter destination (Port): ')
    dest = tuple([dest_ip.strip(), int(dest_port.strip())])

    timeout = float(input('Timeout (s): '))
    files = input('Files to send (Separated by comma): ')
    files = [f.strip() for f in files.split(',')]

    TCPSend(dest, timeout, files)
