class SWI:
    def __init__(self, memory, registers,loader_address,b_size,PC, verbose):
        self.memory = memory
        self.registers = registers
        self.loader_address=loader_address
        self.b_size=b_size
        self.verbose=verbose
        self.PC = PC   # Program Counter initialization

    def executeSWI(self,code):
        # code = self.registers.read('SWI')
        if code==0:
            self.input_stuff()
        elif code==1:
            self.output_stuff()
        elif code==2:
            self.standard_error()

    def input_stuff(self):
        print('todo')

    def output_stuff(self):
        print(f'Values in the register R1 is {self.registers.read('R1')}')

    def standard_error(self):
        print('todo')

        
        