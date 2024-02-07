class pcb:
    '''process control block to store processes that are not active'''
    def __init__(self, reg,  mem):
        self.reg = reg
        self.mem = mem
    
    def offload(self):
        print('load process data')
    
    def reload(self):
        print('return register values and data to os')

class process:
    '''class to store processes that are not active'''
    def __init__(self, address,  size):
        self.address = address
        self.size = size
        self.state = 'new'
        
    def set_ready(self):
        self.state = 'ready'
        
    def terminate(self):
        self.state = 'terminated'
        
    def set_running(self):
        self.state = 'running'
        
    def set_waiting(self):
        self.state = 'waiting'
        
    
    
    
# r1 = Register(2)
# print(r1.value)
# print(r1.binary)