import struct
class Loader:
    def __init__(self,memory):
        self.memory=memory
        self.loader_address_stack= [5]

    def loader(self, file_path, verbose):
        # Open the byte code file in binary mode
        with open(file_path, 'rb') as file:
            reader=struct.Struct('B')
            # Read header information from the byte code file
            b_size, PC, loader_address = struct.unpack('iii', file.read(12))
            if self.loader_address_stack[-1]<loader_address and loader_address+b_size < self.memory.size:
                self.loader_address_stack.append(b_size + loader_address)
            else:
                # from MainClass import ProgramLoadError
                raise ProgramLoadError()
                # raise ProgramLoadError()
            

            # Display header information
            print(f'File Size{b_size}')
            print(f'Program Counter{PC}')
            print(f'Loader Address{loader_address}')
            original_PC=PC
            original_loader_address=loader_address

            for i in range(PC):
                byte=file.read(1)
                directives_code=ord(byte)
                self.memory.write(loader_address,directives_code)
                loader_address+=1

            # file.read(PC)
            for i in range(PC,b_size,6):# do a for loop that increments by 6 for each command to the end of the file 
                #location of command in example file
                #print(i)
                byte = file.read(1)
                #change byte into number for function calls and readability
                instruction_code = ord(byte)
                print(f"Instruction code {instruction_code}")
                if instruction_code == 16:
                    #add
                    if verbose:
                        print('ADD instruction called\n')
                    self.memory.write(loader_address, instruction_code)
                    loader_address+=1
                    PC += 1

                    for _ in range(3):
                        self.memory.write(loader_address, ord(file.read(1)))
                        if verbose:
                            print(f'register {self.memory.read(loader_address)} stored in memory at {loader_address}')
                        loader_address += 1
                        PC += 1
                    
                    file.read(2)
                    loader_address+=2
                    #print(f"Loader address after ADD {loader_address}")
                    PC+=2
                    #print(f"PC after ADD {PC}")
                    
                elif instruction_code == 17:
                    # subtract
                    if verbose:
                        print('SUB instruction called\n')
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    PC += 1

                    for _ in range(3):
                        self.memory.write(loader_address, ord(file.read(1)))
                        if verbose:
                            print(f'register {self.memory.read(loader_address)} stored in memory at {loader_address}')
                        loader_address += 1
                        PC += 1
                    
                    file.read(2)
                    loader_address+=2
                    PC+=2


                elif instruction_code == 18:
                    #multiply
                    if verbose:
                        print('MUL instruction called\n')
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    PC += 1

                    for _ in range(3):
                        self.memory.write(loader_address, ord(file.read(1)))
                        if verbose:
                            print(f'register {self.memory.read(loader_address)} stored in memory at {loader_address}')
                        loader_address += 1
                        PC += 1
                    
                    file.read(2)
                    loader_address+=2
                    PC+=2
                
                elif instruction_code == 19:
                    #divide
                    if verbose:
                        print('DIVIDE instruction called\n')
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    PC += 1

                    for _ in range(3):
                        self.memory.write(loader_address, ord(file.read(1)))
                        if verbose:
                            print(f'register {self.memory.read(loader_address)} stored in self.memory at {loader_address}')
                        loader_address += 1
                        PC += 1
                    
                    file.read(2)
                    loader_address+=2
                    PC+=2

                elif instruction_code == 22:
                    #move immediate
                    if verbose:
                        print('MVI Immediate instruction executed.\n')
                    #storing instruction code
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    PC += 1
                    #storing reg
                    self.memory.write(loader_address, ord(file.read(1)))
                    loader_address+=1
                    PC+=1
                    #storing value
                    self.memory.write(loader_address, ord(file.read(1)))
                    loader_address+=1
                    PC+=1
                    
                    file.read(3)
                    loader_address+=3
                    PC+=3


                elif instruction_code == 1: 
                    # Move data from one register to another
                    if verbose:
                        print('MOV instruction executed.\n')

                    # Storing the instruction code
                    self.memory.write(loader_address, ord(byte))
                    loader_address += 1
                    PC += 1

                    # Storing the source register
                    src_reg = ord(file.read(1))
                    self.memory.write(loader_address, src_reg)
                    loader_address += 1
                    PC += 1

                    # Storing the destination register
                    dest_reg = ord(file.read(1))
                    self.memory.write(loader_address, dest_reg)
                    loader_address += 1
                    PC += 1

                    # Handling unused bytes
                    file.read(3)
                    loader_address += 3
                    PC += 3

                elif instruction_code == 13:
                    #move immediate
                    if verbose:
                        print('AND instruction executed.\n')
                    #storing instruction code
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    PC += 1
                    #storing reg
                    self.memory.write(loader_address, ord(file.read(1)))
                    loader_address+=1
                    PC+=1
                    #storing value
                    self.memory.write(loader_address, ord(file.read(1)))
                    loader_address+=1
                    PC+=1
                    
                    file.read(3)
                    loader_address+=3
                    PC+=3
                
                elif instruction_code == 14:
                    #move immediate
                    if verbose:
                        print('OR operation instruction executed.\n')
                    #storing instruction code
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    PC += 1
                    #storing reg
                    self.memory.write(loader_address, ord(file.read(1)))
                    loader_address+=1
                    PC+=1
                    #storing value
                    self.memory.write(loader_address, ord(file.read(1)))
                    loader_address+=1
                    PC+=1
                    
                    file.read(3)
                    loader_address+=3
                    PC+=3
                    
                elif instruction_code == 20:
                    #move immediate
                    if verbose:
                        print('SWI operation called.\n')
                    #storing instruction code
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    PC += 1
                    # storing value
                    # and 3 additional bytes
                    for _ in range(4):
                        self.memory.write(loader_address, ord(file.read(1)))
                        loader_address+=1
                        PC+=1
                    
                    
                    file.read(1)
                    loader_address+=1
                    PC+=1
                    

        return b_size,original_PC,original_loader_address
