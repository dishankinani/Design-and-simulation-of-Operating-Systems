import copy
class PCB:
    def __init__(self, registers,loader_address,b_size,arrival_time):
        self.registers = copy.deepcopy(registers)
        self.loader_address = loader_address
        self.b_size = b_size
        self.arrival_time=arrival_time
        
    def restore(self):
        return self.registers, self.loader_address, self.b_size,self.arrival_time