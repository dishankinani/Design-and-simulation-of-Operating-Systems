class Memory:
    def __init__(self, size=1000):
        self.size = size
        self.memory = [0] * size
        self.page_size = 18

    def set_page_size(self,page_size):
        self.page_size=page_size

    def get_page_size(self):
        return self.page_size
        
    def read(self, address):
        if 0 <= address < self.size:
            return self.memory[address]
        else:
            raise IndexError(f"Memory read error: Address {address} is out of bounds.")

    def write(self, address, value):
        if 0 <= address < self.size:
            self.memory[address] = value
        else:
            raise IndexError(f"Memory write error: Address {address} is out of bounds.")
    
    def write_program(self, address, program):
        for i in range(0, len(program)):
            self.memory[address+i] = program[i]
               
    def clear(self, address, program_size):
        # Clear the memory from the loader address to the end of the program
        for i in range(address,program_size):
            self.memory[i] = 0
        
