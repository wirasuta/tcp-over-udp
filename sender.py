#!/usr/bin/env python3

import socket
from packet import Packet

DEST_HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
DEST_PORT = 13337        # Port to listen on (non-privileged ports are > 1023)
MESSAGE = b'A' * 16

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    pack1 = Packet('DATA', Packet.pick_id(), 0, len(MESSAGE), MESSAGE)
    print(pack1)
    s.sendto(pack1.to_bytes(), (DEST_HOST, DEST_PORT))
