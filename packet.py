from random import randint


class Packet():
    unacknowledged_packets = []

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

    def __cmp__(self, other):
        return cmp((self.seq, self.id), (other.seq, other.id))

    def __str__(self):
        string_rep = "seq: " + str(self.seq) + ", id: " + str(self.id) + ", type: " + \
            self.get_type() + ", length: " + str(self.length) + ", data: " + self.data
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

    @staticmethod
    def pick_id():
        min_id = 0
        max_id = 14
        exclude = Packet.unacknowledged_packets
        rand_int_id = randint(min_id, max_id)
        while rand_int_id in exclude:
            rand_int_id = randint(min_id, max_id)
        return rand_int_id

    @staticmethod
    def checksum(packet):
        checksum = 0
        type_binary = format(packet.p_type, '#010b')
        id_binary = format(packet.id, '#010b')
        print(type_binary+id_binary[2:])
        temp = int(type_binary+id_binary[2:], 2)
        checksum = temp ^ checksum
        checksum = packet.length ^ checksum
        temp_data = int.from_bytes(
            packet.data.encode('UTF-8'), byteorder='big')
        while(temp_data):
            # temp_data_bin = format(temp_data, '#018b')
            temp_data_bin = temp_data & 0xffff
            checksum = temp_data_bin ^ checksum
            temp_data = temp_data >> 16
