from random import randint
from pickle import dumps, loads
from struct import unpack


class Packet():
    unacknowledged_packet_ids = []

    def __init__(self, p_type, id, seq, length, data):
        self.id = id
        self.seq = seq
        self.length = length
        self.data = data
        if p_type == 'DATA':
            self.p_type = 0x0
        elif p_type == 'ACK':
            self.p_type = 0x1
        elif p_type == 'FIN':
            self.p_type = 0x2
        elif p_type == 'FIN-ACK':
            self.p_type = 0x3
        self.checksum = Packet.checksum(self)
        self.unacknowledged_packet_ids.append(self.id)

    def __eq__(self, other):
        return self.seq == other.seq and self.id == other.id

    def __lt__(self, other):
        return self.seq < other.seq or self.id < other.id

    def __str__(self):
        string_rep = "seq: " + str(self.seq) + ", id: " + str(self.id) + ", type: " + \
            self.get_type() + ", length: " + str(self.length) + \
            ", checksum: " + str(self.checksum)

        return string_rep

    def get_type(self):
        if self.p_type == 0x0:
            return 'DATA'
        elif self.p_type == 0x1:
            return 'ACK'
        elif self.p_type == 0x2:
            return 'FIN'
        elif self.p_type == 0x3:
            return 'FIN-ACK'

    def get_reply(self):
        if self.get_type() == 'FIN':
            return Packet('FIN-ACK', self.id, self.seq, 0, '')
        else:
            return Packet('ACK', self.id, self.seq, 0, '')

    def to_bytes(self):
        type_binary = format(self.p_type, '#06b')[2:]
        id_binary = format(self.id, '#06b')[2:]
        seq_binary = format(self.seq, '#018b')[2:]
        len_binary = format(self.length, '#018b')[2:]
        checksum_binary = format(self.checksum, '#018b')[2:]

        head_binary = type_binary + id_binary + \
            seq_binary + len_binary + checksum_binary

        if (isinstance(self.data, str)):
            data_byte = self.data.encode('UTF-8')
        else:
            data_byte = self.data

        packet = int(head_binary, 2).to_bytes(7, byteorder='big') + data_byte
        return packet

    @classmethod
    def pick_id(cls):
        min_id = 0
        max_id = 14
        exclude = cls.unacknowledged_packet_ids
        rand_int_id = randint(min_id, max_id)
        while rand_int_id in exclude:
            rand_int_id = randint(min_id, max_id)
        return rand_int_id

    @staticmethod
    def from_bytes(packet_bytes):
        head_byte = packet_bytes[:7]
        head_unpacked = unpack('>c3H', head_byte)

        p_type = (int.from_bytes(head_unpacked[0], byteorder='big') >> 4) & 0xf
        pid = int.from_bytes(head_unpacked[0], byteorder='big') & 0xf
        seq = head_unpacked[1]
        length = head_unpacked[2]
        checksum = head_unpacked[3]

        data = packet_bytes[7:]

        if p_type == 0x0:
            str_type = 'DATA'
        elif p_type == 0x1:
            str_type = 'ACK'
        elif p_type == 0x2:
            str_type = 'FIN'
        elif p_type == 0x3:
            str_type = 'FIN-ACK'

        return Packet(str_type, pid, seq, length, data)

    @staticmethod
    def checksum(packet):
        checksum = 0

        type_binary = format(packet.p_type, '#010b')
        id_binary = format(packet.id, '#010b')
        type_id_binary = int(type_binary+id_binary[2:], 2)
        checksum = type_id_binary ^ checksum

        checksum = packet.length ^ checksum

        if (isinstance(packet.data, str)):
            temp_data = packet.data.encode('UTF-8')
        else:
            temp_data = packet.data
        temp_data = int.from_bytes(temp_data, byteorder='big')
        while(temp_data):
            temp_data_bin = temp_data & 0xffff
            checksum = temp_data_bin ^ checksum
            temp_data = temp_data >> 16

        return checksum
