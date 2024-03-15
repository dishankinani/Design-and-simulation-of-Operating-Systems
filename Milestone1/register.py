class Register:
    def __init__(self):
        # Initialize registers as a dictionary
        # You can add more registers as needed
        self.registers = {
            'R0': 0,
            'R1': 0,
            'R2': 0,
            'R3': 0,
            'R4': 0,
            'R5': 0,
            'SP': 0,  # Stack Pointer
            'CLOCK': 0,  # Frame Pointer
            'PC': 0,  # Program Counter
            'Modebit': 0, # 0 for user mode, 1 for kernel mode
            'Z': 0,   # Zero Flag
        }
        self.gantt = []

    def read(self, reg_name):
        """ Read the value from a register """
        return self.registers.get(reg_name, None)

    def write(self, reg_name, value):
        """ Write a value to a register """
        if reg_name in self.registers:
            self.registers[reg_name] = value
        else:
            print(f"Register {reg_name} does not exist.")

    def __str__(self):
        """ String representation for debugging """
        return str(self.registers)
    
    def increment(self, reg_name):
        self.registers[reg_name] += 1

    def clear(self):
        """ Clear all non-persistent registers """
        self.write('R0', 0)
        self.write('R1', 0)
        self.write('R2', 0)
        self.write('R3', 0)
        self.write('R4', 0)
        self.write('R5', 0)
        self.write('SP', 0)
        self.write('Z', 0)
        self.write('CLOCK',0)
    
    def clear_gantt(self):
        "Clears Gantt Chart"
        self.gantt.clear()
