class MMU:
    def __init__(self, memory):
        self.memory = memory
        self.page_size = 36
        self.page_table = {}
        self.free_pages = [i for i in range(0, memory.size, self.page_size)]
        self.memory_size = memory.size
        self.page_number = self.memory_size // self.page_size
    
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
    
    def load_program(self, program):
        page = self.free_pages.pop(0)
        start_address = page*self.page_size
        for i in range(0, len(program), self.page_size):
            self.memory.write_program(start_address, program[i:i+self.page_size])
            self.page_table[page] = i
            page = self.free_pages.pop(0)
        return page