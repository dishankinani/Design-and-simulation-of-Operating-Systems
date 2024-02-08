import queue
from loader import Loader
from register import Register
from mainmemory import Memory
from CPU import CPU
import datetime
from process_classes import pcb, process
class ProgramLoadError(Exception):
    def __str__(self):
        return "Error: Cannot load a new program while another program is already ready to run at the same location."
class VMShell:
    def __init__(self):
        self.memory = Memory()
        self.registers = Register()
        self.registers.write('R2',2)
        self.registers.write('R3',3)

        self.cpu = None
        self.process_queue = queue.Queue()

    def load_program(self, filename, verbose):
        if self.cpu and self.cpu.PC < self.cpu.b_size:
            print("Error: Another program is currently loaded and ready to run. Please reset or exit before loading a new program.")
            raise ProgramLoadError()
        try:
            loader = Loader(filename, self.memory, verbose)
            b_size, PC, loader_address = loader.loader(verbose)
            self.process_queue.put(process(loader_address, b_size))
            
            self.cpu = CPU(self.memory, self.registers, loader_address, b_size, PC, verbose)
            if verbose:
                print(f"Loaded {filename} into memory. Byte Size: {b_size}, PC: {PC}, Loader Address: {loader_address}")
        except ProgramLoadError as e:
            print(e)
            self.errordump(e)
        except Exception as e:
            self.errordump(e)

    def run_program(self, verbose):
        try:
            if self.cpu:
                self.cpu.execute_program()  # Assuming CPU has execute_program method
                if verbose:
                    print("Program executed.")
            else:
                print("No program loaded.")
        except Exception as e:
            self.errordump(e)

    def start_new_instance(self):
        print("Starting a new VMShell instance...")
        new_shell = VMShell()
        new_shell.start()

    def errordump(self, error):
        filename = "errordump.txt"
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(filename, 'a') as file:  # 'a' for append mode
            file.write(f"\nError Timestamp: {current_time}\n")
            file.write("Error Dump:\n")
            file.write(str(error) + "\n")  # Write the error message

            import traceback
            traceback.print_exc(file=file)  # Print stack trace to the file

        print(f"Errordump updated in {filename}")

    def print_errordump(self):
        try:
            with open("errordump.txt", 'r') as file:
                print(file.read())
        except FileNotFoundError:
            print("Error: errordump.txt not found.")

    def run_command(self, command, args):
        verbose = "-v" in args
        if verbose:
            print(self.registers)
            
        if command == "load":
            filename = args[0] if args else None
            if filename:
                self.load_program(filename, verbose)
            else:
                print("No filename provided for load command.")
                
        elif command == "run":
            self.run_program(verbose)
            
        elif command=="coredump":
            if verbose:
                for i in range(1,601):
                    print(self.memory.read(i),end=' ')
                    if i % 6 == 0:
                        print('\n')
                print(self.registers)
            with open('output_from_coredump.txt', 'w') as file:
                    for i in range(1, 601):
                        file.write(str(self.memory.read(i))+" ")
                        if i % 6 == 0:
                            file.write('\n')
                    file.write(str(self.registers))
                    
        elif command=="errordump":
            self.print_errordump()
            
        elif command=="shell":
            self.start_new_instance()
            
        else:
            print("Command Not Found")
        # Implement other commands like coredump, errordump
        # ...

    def start(self):
        try:
            while True:
                command_input = input(">> ")
                if command_input in ["exit", "quit"]:
                    break
                parts = command_input.split()
                if parts:
                    command = parts[0]
                    args = parts[1:]
                    self.run_command(command, args)
        except KeyboardInterrupt:
            print("\nInterrupt received. Exiting shell.")
        except Exception as e:
            self.errordump(e)

def main():
    try:
        vm_shell = VMShell()
        vm_shell.start()
    except KeyboardInterrupt:
        print("\nInterrupt received. Exiting shell.")
    except Exception as e:
        vm_shell.errordump(e)

if __name__ == "__main__":
    main()


