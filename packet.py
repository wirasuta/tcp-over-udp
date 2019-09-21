from random import randint

class Packet():    
    unacknowledged_packets = []

    def __init__(self, p_type, id, seq, length, data):
        self.p_type = p_type
        self.id = self.pick_id()
        self.seq = seq
        self.length = length
        self.data = data
        self.checksum = self.checksum()

    @staticmethod
    def pick_id():
        min_id = 0
        max_id = 14
        exclude= unacknowledged_packets
        randInt = randint(min_id, max_id)
        if randInt in exclude:
            pick_id()
        else:
            return randInt 

    def __cmp__(self, other):
        return cmp((self.seq, self.id), (other.seq, other.id))

    def __str__(self):
        string_rep = "seq: "+ self.seq + ", id: "+ self.id +", type: "+ self.p_type +", length :"+ self.length +", data "+ self.data
        return string_rep
    
    def get_type(self):
        return self.p_type

    @staticmethod
    def checksum(self):
        checksum = 0
        id_binary = format(self.id, '#010b')
        type_binary = format(self.p_type, '#010b')
        temp = int(id_binary+''+type_binary.id,2)
        checksum = temp ^ checksum
        checksum = self.length ^ checksum
        temp_data = self.data
        while(temp_data){
            temp_data_bin = format(temp_data, '#018b')
            checksum = int(temp_data_bin,2) ^ checksum
            temp_data = temp_data >> 16
        }





#xor awal 0 semua 
#xor sama 8 bit

# datatemp = data
# bikin while datatemp loop
# dataxor = datatemp & 1111111111111111
# checksumvalue ^= dataxor
# datatemp >>= 16
# 

    
