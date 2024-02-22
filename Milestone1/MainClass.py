import queue
from loader import Loader
from register import Register
from mainmemory import Memory
from CPU import CPU
import datetime
import subprocess
class ProgramLoadError(Exception):
    def __str__(self):
        return "Error: Cannot load a new program while another program is already ready to run at the same location."
class VMShell:
    def __init__(self):
        self.memory = Memory()
        self.registers = Register()
        # self.registers.write('R2',10)   
        # self.registers.write('R3',5)
        self.loader = Loader(self.memory)
        self.cpus = queue.Queue()
        self.clock = 0 # clock is used to keep track of instructions ran

    def load_program(self, filename, verbose):
        try:
            b_size, first_instruction_address, loader_address = self.loader.loader(filename, verbose)
            new_cpu = CPU(self.memory, self.registers, loader_address, b_size, first_instruction_address, verbose)
            self.registers.write('PC', first_instruction_address)
            #print(self.re)
            if verbose:
                print(f"Loaded {filename} into memory. Byte Size: {b_size}, First instructions address: {loader_address+ first_instruction_address}, Loader Address: {loader_address}")
                print(f'{filename} status set to ready')
            #changing cpu state to ready
            new_cpu.state = 'ready'
            self.cpus.put(new_cpu)
            print(list(self.cpus.queue))
            
        except ProgramLoadError as e:
            print(e)
            self.errordump(e)
        except Exception as e:
            self.errordump(e)

    def run_program(self, verbose):
        try:
            while not self.cpus.empty():
                print(list(self.cpus.queue))
                running = self.cpus.get()
                print(running)
                running.state = 'running'
                running.execute_program()
                print("skjhfkjshfkjhifhdijfbdkjfhkjdfghdfgkhdfkjghdkjghkjdfhgjhdfkjgkj")  # Assuming CPU has execute_program method
                if verbose:
                    print('process set to running')
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
        # elif command == "execute":
        #     self.run 
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
        elif command=="osx":
            filename = args[0] if args else None
            if filename:
                if args[1]:
                    self.osx(filename, verbose, args[1])
                else:
                    self.osx(filename, verbose)
            else:
                print("No filename provided for load command.")
        elif command=="execute":
            for i in len(args):
                #FCFS scheduling
                self.load_program(i, verbose)
                arrival_time = args[i+1]
                self.run_program(verbose)
                i+=1
            
                
        else:
            print("Command Not Found")
        
    def osx(self, filename, verbose, loader_address=0):
        if loader_address != 0:
            load_address = loader_address
        else:
            load_address = str(self.loader.loader_address_stack[-1] + 1)
        command = f'osx.exe {filename} {load_address}'
        #brkt_command = ['osx.exe', filename, load_address]
        try:
            subprocess.run(command, check=False, shell=True)  # Add shell=True parameter
            if verbose:
                print(f"OSX compiled .asm to .osx file.")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            self.errordump(e)
        
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


