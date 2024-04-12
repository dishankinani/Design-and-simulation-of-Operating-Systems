class SWI:
    def __init__(self, memory, registers,loader_address,b_size,PC, verbose):
        self.memory = memory
        self.registers = registers
        self.loader_address=loader_address
        self.b_size=b_size
        self.verbose=verbose
        self.PC = PC   # Program Counter initialization
        self.lock = False

    def executeSWI(self,code):
        # code = self.registers.read('SWI')
        #self.registers.set('SWI',1)
        if code==0:
            # get input from keyboard
            self.input_stuff()
        elif code==1:
            # print to screen
            self.output_stuff()
        elif code==2:
            # throw error
            self.standard_error()
        #self.registers.set('SWI',0)
        elif code==3:
            self.registers.create_shared_memory()
        elif code==4:
            self.registers.destroy_shared_memory()
        elif code==5:
            while self.lock:
                pass
            self.lock = True
            self.registers.write_shared_memory(self.registers.read('R2'))
            self.lock = False
        elif code==6:
            #mutex
            while self.lock:
                pass
            self.lock = True
            self.registers.write('R2',self.registers.read_shared_memory())
            self.lock = False
            
    def input_stuff(self):
       value1 = input('Please give an integer value (value will be stored in R2):')
       self.registers.write('R2', int(value1))

    def output_stuff(self):
        print(f'\033[91mPrint Statement: \033[0mValues in the register R2 is {self.registers.read("R2")}')

    def standard_error(self):
        print('todo')

        
        