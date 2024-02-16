from SWI import SWI
class CPU:
    def __init__(self, memory, registers,loader_address,b_size, PC, verbose, arrival_time=0):
        self.memory = memory
        self.registers = registers
        self.loader_address=loader_address
        self.b_size=b_size
        self.verbose=verbose
        self.PC = PC   # Program Counter initialization
        self.state = 'new'
        self.registers.write('PC',PC)
        self.arrival_time = arrival_time

    def fetch(self):
        instruction = []
        for _ in range(6):  # Fetch 6 bytes individually
            instruction.append(self.memory.read(self.loader_address+self.registers.read('PC')))
            print(f"Actual Address in memory from CPU of instructions {self.loader_address+self.registers.read('PC')}")
            self.registers.increment('PC')  # Increment PC for each byte read
            print(f"After incrementing PC {self.registers.read('PC')}" )
        return instruction
    
    def decode(self, instruction):
        opcode = instruction[0]
        destination=instruction[1]
        operand1 = instruction[2]
        operand2 = instruction[3]
        return opcode, destination, operand1, operand2

    def execute(self, instruction):
        opcode, destination, operand1, operand2= self.decode(instruction)
        print(f"Opcode of the instruction being executed {opcode}")
        dest_reg = f'R{destination}'

        if opcode == 16:  # opcode for ADD
            self.add(operand1, operand2, dest_reg)
        elif opcode == 1:
            self.mov(destination, operand1)
        elif opcode == 17:  # opcode for SUBTRACT
            self.subtract(operand1, operand2,dest_reg)
        elif opcode == 18:
            self.multiply(operand1,operand2,dest_reg)
        elif opcode == 19:
            self.divide(operand1,operand2,dest_reg)
        elif opcode == 22:
            self.mvi(dest_reg,operand1)
        elif opcode == 13:
            self.and_operation(destination, operand1)
        elif opcode == 14:
            self.or_operation(destination, operand1)
        elif opcode == 20:
            #call SWI Class
            swi1=SWI(self.memory,self.registers,self.loader_address,self.b_size,self.registers.read('PC'),self.verbose)
            swi1.executeSWI(destination)

        else:
            print(f"Unknown opcode: {opcode}")

    def add(self, operand1, operand2, dest_reg):
        value1 = self.registers.read(f'R{operand1}')
        value2 = self.registers.read(f'R{operand2}')
        result = value1 + value2
        self.registers.write(dest_reg, result)  # Store result in destination register
        if self.verbose:
            print(f"The value of operand 1 in R2 {value1}")
            print(f"The value of operand 2 in R3 {value2}")
        print(f"This is the result after addition stored in R1 is {result}")

    def subtract(self, operand1, operand2, dest_reg):
        value1 = self.registers.read(f'R{operand1}')
        value2 = self.registers.read(f'R{operand2}')
        result = value1 - value2
        self.registers.write(dest_reg, result) 
        if self.verbose:
            print(f"The value of operand 1 in R2 {value1}")
            print(f"The value of operand 2 in R3 {value2}")
        print(f"This is the result after subtract stored in R1 is {result}")


    def multiply(self, operand1, operand2, dest_reg):
        value1 = self.registers.read(f'R{operand1}')
        value2 = self.registers.read(f'R{operand2}')
        result = value1 * value2
        self.registers.write(dest_reg, result)
        if self.verbose:
            print(f"The value of operand 1 in R2 {value1}")
            print(f"The value of operand 2 in R3 {value2}")
        print(f"This is the result after multiply stored in R1 is {result}")

    def divide(self, operand1, operand2, dest_reg):
        value1 = self.registers.read(f'R{operand1}')
        value2 = self.registers.read(f'R{operand2}')
        result = value1 / value2
        self.registers.write(dest_reg, result) 
        if self.verbose:
            print(f"The value of operand 1 in R2 {value1}")
            print(f"The value of operand 2 in R3 {value2}")
        print(f"This is the result after divide stored in R1 is {result}")
    
    def mov(self, reg1_index, reg2_index):
        reg1 = f'R{reg1_index}'  
        reg2 = f'R{reg2_index}'
        value = self.registers.read(reg2)  # Read value from reg2
        self.registers.write(reg1, value) 
        if self.verbose:
            print(f"The value in R1 {value}")
            print(f"The value in R2 {value}")
        print(f"MOV instruction processed.")

    def and_operation(self, operand1, operand2):
        value1 = self.registers.read(f'R{operand1}')
        value2 = self.registers.read(f'R{operand2}')
        result = value1 & value2  # Bitwise AND
        self.registers.write(f'Z', result)
        if self.verbose:
            print(f"The value of operand 1 in R{operand1} is {value1}")
            print(f"The value of operand 2 in R{operand2} is {value2}")
        print(f"The result after AND operation stored in Z register is {result}")

    def or_operation(self, operand1, operand2):
        value1 = self.registers.read(f'R{operand1}')
        value2 = self.registers.read(f'R{operand2}')
        result = value1 | value2  # Bitwise OR
        self.registers.write(f'Z', result)
        if self.verbose:
            print(f"The value of operand 1 in R{operand1} is {value1}")
            print(f"The value of operand 2 in R{operand2} is {value2}")
        print(f"The result after OR operation stored in Z register is {result}")

    def mvi(self, reg, imm):
        imm_name = f'R{imm}'
        self.registers.write(reg, imm_name)
    
    def execute_program(self):
        while self.registers.read('PC') < self.b_size:
            print(f"PC from CPU {self.registers.read('PC')}")
            print(f"b_size from CPU {self.b_size}")
            instruction = self.fetch()
            if instruction[0] == '0':
                #jump to IO queue
                print('todo')
            self.execute(instruction)
            self.registers.increment('CLOCK')
            

        
