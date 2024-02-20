import copy
class PCB:
    def __init__(self, registers, current_instruction_address,loader_address,b_size,arrival_time):
        self.registers = copy.deepcopy(registers)
        self.loader_address = loader_address
        self.b_size = b_size
        self.arrival_time=arrival_time
        self.current_instruction_address = current_instruction_address
        
    def restore(self):
        return self.registers, self.loader_address, self.b_size,self.arrival_time