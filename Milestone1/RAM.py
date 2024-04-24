class Ram:
    def __init__(self, number_of_pages,page_size,memory) -> None:
        self.pages = []
        self.instructions = []
        self.memory = memory
        self.page_faults = 0
        self.number_of_pages = number_of_pages
        self.page_size = memory.page_size
        
    # def read(self, page_number, offset):
    #     return self.instructions[page_number*offset]
    def initial_load(self,instruction_set):
        self.pages.append(instruction_set)
        
    def load_page(self,page_number):
        page_number-=1
        instructions = self.memory.memory[page_number*self.memory.page_size:page_number*self.memory.page_size+self.memory.page_size]
        if self.page_faults < self.number_of_pages:
            self.pages.append(page_number+1)
            self.instructions.append(instructions)
            self.page_faults+=1
        else:    
            self.instructions.pop(0)
            self.instructions.append(instructions)
            self.pages.pop(0)
            self.pages.append(page_number+1)
            self.page_faults+=1
        
    def print_ram(self):
        print(self.pages)
        print(self.instructions)
        
