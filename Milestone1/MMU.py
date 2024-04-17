import struct
class mmu:
    def __init__(self, memory,loader):
        self.memory = memory
        self.page_size = 20
        self.number_of_pages=len(memory)/self.page_size
        self.page_counter=0
        self.page_table = {}
        self.free_pages = [i for i in range(0, memory.size, self.page_size)]
        self.page_number = len(memory) // self.page_size # number of pages for each program
    
    def get_page_size(self):
        return self.page_size

    def set_page_size(self, page_size):
        self.page_size = page_size
        
    def get_page_number(self):
        return self.page_number
    
    def set_page_number(self, page_number):
        self.page_number = page_number
        
    def get_page_table(self):
        return self.page_table
    
    def get_binary_filesize(self, file_path):
        with open(file_path, 'rb') as file:
            reader=struct.Struct('B')
            # Read header information from the byte code file
            b_size, PC = struct.unpack('iii', file.read(8))
        return b_size, PC

    # def allocate_pages(self, b_size, pid, page_number):
    #     for i in page_number:
    #         self.page_table[pid]=self.page_counter+i

    def load_program(self, file_path, verbose,pid):
        # Open the byte code file in binary mode
        with open(file_path, 'rb') as file:
            reader=struct.Struct('B')
            # Read header information from the byte code file
            b_size, PC = struct.unpack('iii', file.read(8))
            file.read(4)

            
            # Display header information
            print(f'File Size{b_size}')
            print(f'Program Counter{PC}')

            for i in range(PC):
                byte=file.read(1)
                directives_code=ord(byte)
               # don't need to pop here
                self.memory.write(self.free_pages.pop(0)*self.page_size,directives_code)
            '''Don't need to pop here'''
                

            # file.read(PC)
            for i in range(PC,b_size,6):# do a for loop that increments by 6 for each command to the end of the file 
                current_page = self.free_pages.pop(0)
                self.page_table[current_page] = pid
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
                    

                    for _ in range(3):
                        self.memory.write(loader_address, ord(file.read(1)))
                        if verbose:
                            print(f'register {self.memory.read(loader_address)} stored in memory at {loader_address}')
                        loader_address += 1
                        
                    
                    file.read(2)
                    loader_address+=2
                    #print(f"Loader address after ADD {loader_address}")
                    #print(f"PC after ADD {PC}")
                    
                elif instruction_code == 17:
                    # subtract
                    if verbose:
                        print('SUB instruction called\n')
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    

                    for _ in range(3):
                        self.memory.write(loader_address, ord(file.read(1)))
                        if verbose:
                            print(f'register {self.memory.read(loader_address)} stored in memory at {loader_address}')
                        loader_address += 1
                        
                    
                    file.read(2)
                    loader_address+=2


                elif instruction_code == 18:
                    #multiply
                    if verbose:
                        print('MUL instruction called\n')
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    

                    for _ in range(3):
                        self.memory.write(loader_address, ord(file.read(1)))
                        if verbose:
                            print(f'register {self.memory.read(loader_address)} stored in memory at {loader_address}')
                        loader_address += 1
                        
                    
                    file.read(2)
                    loader_address+=2
                
                elif instruction_code == 19:
                    #divide
                    if verbose:
                        print('DIVIDE instruction called\n')
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    

                    for _ in range(3):
                        self.memory.write(loader_address, ord(file.read(1)))
                        if verbose:
                            print(f'register {self.memory.read(loader_address)} stored in self.memory at {loader_address}')
                        loader_address += 1
                        
                    
                    file.read(2)
                    loader_address+=2

                elif instruction_code == 22:
                    #move immediate
                    if verbose:
                        print('MVI Immediate instruction executed.\n')
                    #storing instruction code
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    
                    #storing reg
                    self.memory.write(loader_address, ord(file.read(1)))
                    loader_address+=1
                    
                    #storing value
                    self.memory.write(loader_address, ord(file.read(1)))
                    loader_address+=1
                    
                    
                    file.read(3)
                    loader_address+=3

                elif instruction_code == 1: 
                    # Move data from one register to another
                    if verbose:
                        print('MOV instruction executed.\n')

                    # Storing the instruction code
                    self.memory.write(loader_address, ord(byte))
                    loader_address += 1
                    

                    # Storing the source register
                    src_reg = ord(file.read(1))
                    self.memory.write(loader_address, src_reg)
                    loader_address += 1
                    

                    # Storing the destination register
                    dest_reg = ord(file.read(1))
                    self.memory.write(loader_address, dest_reg)
                    loader_address += 1
                    

                    # Handling unused bytes
                    file.read(3)
                    loader_address += 3

                elif instruction_code == 13:
                    #move immediate
                    if verbose:
                        print('AND instruction executed.\n')
                    #storing instruction code
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    
                    #storing reg
                    self.memory.write(loader_address, ord(file.read(1)))
                    loader_address+=1
                    
                    #storing value
                    self.memory.write(loader_address, ord(file.read(1)))
                    loader_address+=1
                    
                    
                    file.read(3)
                    loader_address+=3
                
                elif instruction_code == 14:
                    #move immediate
                    if verbose:
                        print('OR operation instruction executed.\n')
                    #storing instruction code
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    
                    #storing reg
                    self.memory.write(loader_address, ord(file.read(1)))
                    loader_address+=1
                    
                    #storing value
                    self.memory.write(loader_address, ord(file.read(1)))
                    loader_address+=1
                    
                    
                    file.read(3)
                    loader_address+=3
                    
                elif instruction_code == 20:
                    #move immediate
                    if verbose:
                        print('SWI operation called.\n')
                    #storing instruction code
                    self.memory.write(loader_address, ord(byte))
                    loader_address+=1
                    
                    # storing value
                    # and 3 additional bytes
                    for _ in range(4):
                        self.memory.write(loader_address, ord(file.read(1)))
                        loader_address+=1
                        
                    
                    
                    file.read(1)
                    loader_address+=1
                    
        return b_size,original_PC,original_loader_address
    def print_errordump(self, error):
        try:
            with open("errordump.txt", 'r') as file:
                file.write(error)
        except FileNotFoundError:
            print("Error: errordump.txt not found.")
    
        