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
            # get input from keyboard
            self.input_stuff()
        elif code==1:
            # print to screen
            self.output_stuff()
        elif code==2:
            # throw error
            self.standard_error()

    def input_stuff(self):
       value1 = input('Please give an integer value (value will be stored in R2):')
       self.registers.write('R2', value1)

    def output_stuff(self):
        print(f'Values in the register R1 is {self.registers.read("R1")}')

    def standard_error(self):
        print('todo')

        
        