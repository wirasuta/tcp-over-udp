#!/usr/bin/env python3

import socket, sys
from time import sleep
from threading import Thread, Event, Lock
from packet import Packet
from itertools import chain, islice
from random import randint

HOST = '127.0.0.1'

MAX_DATA_SIZE = 32768
MAX_PACKET_SIZE = 33000
MAX_SINGLE_SEND = 5
N_TRANSFERED = 0

#Menerima input float antara 0 s.d 1 untuk merepresentasikan progress
def update_progress(progress, max_length):
    status = ""
    barLength =  max_length #Sets the length of the bar
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "Error: progress variable must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Error : Progress cannot be negative\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    bar = "\rProgress: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(bar)
    sys.stdout.flush()

class TCPSendThread(Thread):
    """
    Thread for emulating TCP send of single file by doing these things:
    1. Bind to specific address, each file will bind to different port
    2. Send all packet
    3. Check after timeout if any packet is not acknowledged
    4. Retry sending unacknowledged packet
    """
    def __init__(self, src, dest, timeout, packets, event, n_transfered, n_total):
        Thread.__init__(self)
        self.stopped = event
        self.src = src
        self.dest = dest
        self.timeout = timeout
        self.unacknowledged_packets = packets
        self.pid = self.unacknowledged_packets[0].id
        self.n_transfered = n_transfered
        self.n_total = n_total

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(self.src)

            ack_thread = TCPAckThread(
                self.pid, self.unacknowledged_packets, sock, self.n_transfered, self.n_total)
            ack_thread.start()

            for unacknowledged_packet in self.unacknowledged_packets[:MAX_SINGLE_SEND]:
                sock.sendto(unacknowledged_packet.to_bytes(), self.dest)
                # print(f'{self.dest} <- {unacknowledged_packet}')

                f = open("log.txt", "a")
                f.write(f'{self.dest} <- {unacknowledged_packet}' + '\n')
                f.close()

            while not self.stopped.wait(self.timeout):
                if len(self.unacknowledged_packets) == 0:
                    self.stopped.set()
                for unacknowledged_packet in self.unacknowledged_packets[:MAX_SINGLE_SEND]:
                    sock.sendto(
                        unacknowledged_packet.to_bytes(), self.dest)
                    # print(f'{self.dest} <- {unacknowledged_packet}')
                    f = open("log.txt", "a")
                    f.write(f'{self.dest} <- {unacknowledged_packet}' + '\n')
                    f.close()

            ack_thread.join()
        # print(f'[i] All package for id {self.pid} sent!')
        f = open("log.txt", "a")
        f.write(f'[i] All package for id {self.pid} sent!' + '\n')
        f.close()

class TCPAckThread(Thread):
    """
    Thread for handling acknowledgement by removing packets
    from unacknowledged_packets list and stop on FIN-ACK
    """

    def __init__(self, pid, unacknowledged_packets, sock, n_transfered, n_total):
        Thread.__init__(self)
        self.stopped = Event()
        self.unacknowledged_packets = unacknowledged_packets
        self.sock = sock
        self.pid = pid
        self.n_transfered = n_transfered
        self.n_total = n_total

    def run(self):
        while not self.stopped.is_set():
            data, addr = self.sock.recvfrom(MAX_PACKET_SIZE)
            ack_packet = Packet.from_bytes(data)
            # print(f'{addr} -> {ack_packet}')
            
            #UPDATE progress bar
            # self.n_transfered = self.n_transfered + 1
            global N_TRANSFERED
            N_TRANSFERED = N_TRANSFERED+1
            update_progress(N_TRANSFERED/self.n_total, self.n_total)

            f = open("log.txt", "a")
            f.write(f'{addr} -> {ack_packet}' + '\n')
            f.close()

            if ack_packet in self.unacknowledged_packets:
                self.unacknowledged_packets.remove(ack_packet)

            if (ack_packet.get_type() == 'FIN-ACK'):
                self.stopped.set()

        # print(f'[i] All package for id {self.pid} acknowledged!')
        f = open("log.txt", "a")
        f.write(f'[i] All package for id {self.pid} acknowledged!' + '\n')
        f.close()

class TCPSend:
    """
    Emulate TCP sending by splitting files into packets 
    and spawning a send thread for each file
    """

    def __init__(self, dest, timeout, files):
        all_packets = []
        length_of_packets = 0
        n_transfered = 0

        for file_to_split in files:
            splitted_files = list(self.file_to_packets(file_to_split))
            all_packets.append(splitted_files)
            length_of_packets = length_of_packets + len(splitted_files)

        print("length of packets : " + str(length_of_packets))        
        #setup progress bar
        update_progress(0, length_of_packets)

        stop_flags = []
        send_threads = []
        base_port = randint(1025, 65534)

        for idx, single_file_packets in enumerate(all_packets):
            stop_flag = Event()
            stop_flags.append(stop_flag)

            src = (HOST, base_port + idx)

            send_thread = TCPSendThread(
                src, dest, timeout, single_file_packets, stop_flag, n_transfered, length_of_packets)
            send_threads.append(send_thread)
            send_thread.start()

        for idx, thread in enumerate(send_threads):
            thread.join()

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
    dest = (dest_ip.strip(), int(dest_port.strip()))

    timeout = float(input('Timeout (s): '))

    files = input('Files to send (Separated by comma): ')
    files = [f.strip() for f in files.split(',')]

    # for i in range(20):
    #     bar.update(i+1)
    #     sleep(0.1)
    #     bar.finish()

    TCPSend(dest, timeout, files)
