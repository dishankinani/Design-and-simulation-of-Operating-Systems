import math
import struct
class mmu:
    def __init__(self, memory, page_size=24):
        self.memory = memory
        self.page_size = page_size
        self.number_of_pages=memory.size/self.page_size
        self.page_counter=0
        self.page_table = {}
        self.free_pages = [i for i in range(0, math.floor(memory.size/self.page_size))]
        self.page_number = memory.size // self.page_size # number of pages for each program
        
    
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

    def load_program(self, file_path, verbose, pid):
        # Open the byte code file in binary mode
        with open(file_path, 'rb') as file:
            page_number_array=[]
            reader=struct.Struct('B')
            # Read header information from the byte code file
            b_size, PC = struct.unpack('ii', file.read(8))
            file.read(4) # fetches loader address
            threshold_address=0
            # Display header information
            print(f'File Size{b_size}')
            print(f'Program Counter{PC}')

            for i in range(PC):
                byte=file.read(1)
                directives_code=ord(byte)
               # don't need to pop here
                # self.memory.write(self.free_pages.pop(0)*self.page_size,directives_code)
            '''Don't need to pop here'''
                
            for page in range(math.ceil((b_size-PC)/self.page_size)):
                current_page=self.free_pages.pop(0)
                if page==0:
                    threshold_address=current_page*self.page_size+(b_size-PC)
                current_address=current_page*self.page_size
                page_number_array.append(current_page)
                # if not pid in self.page_table:
                #     self.page_table[pid]=[]
                # array = self.page_table[pid]
                # array.append(current_page)
                # self.page_table[pid]=array
            # file.read(PC)
            #+current_page*self.page_size
                
                print("Here, current page =", current_page)
                # current_address = current_page * self.page_size
                for i in range(current_address,current_page*self.page_size+self.page_size,6):# do a for loop that increments by 6 for each command to the end of the file    
                    print(f"Current Address {current_address}")
                    if current_address >= threshold_address:
                            break
                    byte = file.read(1)
                    #change byte into number for function calls and readability
                    instruction_code = ord(byte)
                    print(f"Instruction code {instruction_code}")
                    if instruction_code == 16:
                        #add
                        if verbose:
                            print('ADD instruction called\n')
                        self.memory.write(current_address, instruction_code)
                        current_address+=1
                        

                        for _ in range(3):
                            self.memory.write(current_address, ord(file.read(1)))
                            if verbose:
                                print(f'register {self.memory.read(current_address)} stored in memory at {current_address}')
                            current_address += 1
                            
                        
                        file.read(2)
                        current_address+=2
                        #print(f"Loader address after ADD {current_address}")
                        #print(f"PC after ADD {PC}")
                        
                    elif instruction_code == 17:
                        # subtract
                        if verbose:
                            print('SUB instruction called\n')
                        self.memory.write(current_address, ord(byte))
                        current_address+=1
                        

                        for _ in range(3):
                            self.memory.write(current_address, ord(file.read(1)))
                            if verbose:
                                print(f'register {self.memory.read(current_address)} stored in memory at {current_address}')
                            current_address += 1
                            
                        
                        file.read(2)
                        current_address+=2


                    elif instruction_code == 18:
                        #multiply
                        if verbose:
                            print('MUL instruction called\n')
                        self.memory.write(current_address, ord(byte))
                        current_address+=1
                        

                        for _ in range(3):
                            self.memory.write(current_address, ord(file.read(1)))
                            if verbose:
                                print(f'register {self.memory.read(current_address)} stored in memory at {current_address}')
                            current_address += 1
                            
                        
                        file.read(2)
                        current_address+=2
                    
                    elif instruction_code == 19:
                        #divide
                        if verbose:
                            print('DIVIDE instruction called\n')
                        self.memory.write(current_address, ord(byte))
                        current_address+=1
                        

                        for _ in range(3):
                            self.memory.write(current_address, ord(file.read(1)))
                            if verbose:
                                print(f'register {self.memory.read(current_address)} stored in self.memory at {current_address}')
                            current_address += 1
                            
                        
                        file.read(2)
                        current_address+=2

                    elif instruction_code == 22:
                        #move immediate
                        if verbose:
                            print('MVI Immediate instruction executed.\n')
                        #storing instruction code
                        self.memory.write(current_address, ord(byte))
                        current_address+=1
                        
                        #storing reg
                        self.memory.write(current_address, ord(file.read(1)))
                        current_address+=1
                        
                        #storing value
                        self.memory.write(current_address, ord(file.read(1)))
                        current_address+=1
                        
                        
                        file.read(3)
                        current_address+=3

                    elif instruction_code == 1: 
                        # Move data from one register to another
                        if verbose:
                            print('MOV instruction executed.\n')

                        # Storing the instruction code
                        self.memory.write(current_address, ord(byte))
                        current_address += 1
                        

                        # Storing the source register
                        src_reg = ord(file.read(1))
                        self.memory.write(current_address, src_reg)
                        current_address += 1
                        

                        # Storing the destination register
                        dest_reg = ord(file.read(1))
                        self.memory.write(current_address, dest_reg)
                        current_address += 1
                        

                        # Handling unused bytes
                        file.read(3)
                        current_address += 3

                    elif instruction_code == 13:
                        #move immediate
                        if verbose:
                            print('AND instruction executed.\n')
                        #storing instruction code
                        self.memory.write(current_address, ord(byte))
                        current_address+=1
                        
                        #storing reg
                        self.memory.write(current_address, ord(file.read(1)))
                        current_address+=1
                        
                        #storing value
                        self.memory.write(current_address, ord(file.read(1)))
                        current_address+=1
                        
                        
                        file.read(3)
                        current_address+=3
                    
                    elif instruction_code == 14:
                        #move immediate
                        if verbose:
                            print('OR operation instruction executed.\n')
                        #storing instruction code
                        self.memory.write(current_address, ord(byte))
                        current_address+=1
                        
                        #storing reg
                        self.memory.write(current_address, ord(file.read(1)))
                        current_address+=1
                        
                        #storing value
                        self.memory.write(current_address, ord(file.read(1)))
                        current_address+=1
                        
                        
                        file.read(3)
                        current_address+=3
                        
                    elif instruction_code == 20:
                        print('Swi executed')
                        #move immediate
                        if verbose:
                            print('SWI operation called.\n')
                        #storing instruction code
                        self.memory.write(current_address, ord(byte))
                        current_address+=1
                        
                        # storing value
                        # and 3 additional bytes
                        for _ in range(4):
                            self.memory.write(current_address, ord(file.read(1)))
                            current_address+=1
                            
                        
                        
                        file.read(1)
                        current_address+=1
            self.page_table[pid]=page_number_array        
            return b_size, PC, self.page_table[pid]
    def print_page_table(self):
        print(f"The Page table looks like this {self.page_table}")
    def print_errordump(self, error):
        try:
            with open("errordump.txt", 'r') as file:
                file.write(error)
        except FileNotFoundError:
            print("Error: errordump.txt not found.")
    
        