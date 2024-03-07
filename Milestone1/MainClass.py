from collections import deque
import queue
from loader import Loader
from register import Register
from mainmemory import Memory
from CPU import CPU
import datetime
import subprocess
from ProgramLoadError import ProgramLoadError
class VMShell:
    def __init__(self):
        self.memory = Memory()
        self.registers = Register()
        # self.registers.write('R2',10)   
        # self.registers.write('R3',5)
        self.loader = Loader(self.memory)
        self.cpus = queue.Queue()
        self.new= queue.Queue()
        self.ready=queue.Queue()
        self.terminated=[]
        self.wait=queue.Queue()
        self.arriavl_times = []
        self.clock = 0 # clock is used to keep track of instructions ran
        self.quantum = 8

    def load_program(self, filename, arrival_time, verbose, pid=None):
        try:
            b_size, first_instruction_address, loader_address = self.loader.loader(filename, verbose)
            new_cpu = CPU(self.memory, self.registers, loader_address, b_size, first_instruction_address, verbose, pid=pid, arrival_time = arrival_time)
            self.registers.write('PC', first_instruction_address)
            #print(self.re)
            if verbose:
                print(f"Loaded {filename} into memory. Byte Size: {b_size}, First instructions address: {loader_address+ first_instruction_address}, Loader Address: {loader_address}")
                print(f'{filename} status set to ready')
            #changing cpu state to ready
            new_cpu.state = 'ready'
            self.cpus.put(new_cpu)
            if verbose:
                print(list(self.cpus.queue)) #testing the queue/ ganntt chart
        except Exception as e:
            self.errordump(e)

    def run_program(self, verbose):
        try:
            while not self.cpus.empty():
                
                #print(list(self.cpus.queue))
                running = self.cpus.get()
                #print(running)
                running.state = 'running'
               
                running.execute_program()
                if verbose:
                    print('process set to running')
                    print("Program executed.")
                    
                if running.state == 'terminated':
                    self.terminated.append(self.ready.get())
                    self.print_queues()
                    # del running    
            else:
                print("End of Programs")
        except Exception as e:
            self.errordump(e)

    def round_robin(self):
        
        # sorted_queue = sorted(self.ready.queue, key=lambda obj: obj.arrival_time)
        # for obj in sorted_queue:
        #     self.ready.put(obj)
        # self.cpus = queue.Queue(sorted_queue) # type: ignore
        # self.ready = queue.Queue() # double ended queue for quick access to both sides
        while not self.cpus.empty() or not self.ready.empty():
            print(self.registers.read('CLOCK'))
            if not self.cpus.empty() and self.cpus.queue[0].arrival_time <= self.registers.read('CLOCK'):
                #print(f"self.cpus.queue[0].arrival_time={self.cpus.queue[0].arrival_time}")
                self.ready.put(self.cpus.get())
                # removes first pid from ready queue
                # # self.ready.get()
            if self.ready.empty():
                for x in range(self.quantum):
                    #print(f"Quantum:::::::::::::::::::::::::::   {x}")
                    self.registers.increment('CLOCK')
                    self.registers.gantt.append('X')
            
            

            if not self.ready.empty():
                running = self.ready.get()
                for x in range(self.quantum):
                    #print(f"Quantum:::::::::::::::::::::::::::   {x}")
                    if running.state == 'terminated':
                        print(".")
                        if running.pid not in self.terminated:
                            self.terminated.append(running.pid)
                        self.registers.gantt.append('X')
                        self.registers.increment('CLOCK')
                        # not sure whether needed or not
                        # del running
                        continue
                    running.execute_single_instruction()
                    # self.registers.increment('CLOCK')
                    self.registers.gantt.append(running.pid)
                if running.state != 'terminated':
                    '''
                    implement pcb saving here
                    '''
                    self.ready.put(running)
            
                
                
            
        # except Exception as e:
        #     self.errordump(e)
        # pass
            
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

    def print_gantt(self):
        print(self.registers.gantt)

    def run_command(self, command, args):
        verbose = "-v" in args
        if verbose:
            print(self.registers)
        if command == "load":
            filename = args[0] if args else None
            if filename:
                self.load_program(filename,0, verbose)
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
            pid = 1
            for i in range(0,len(args),2):
                if args[i] == "-v":
                    break
                if verbose:
                    print('Program name: ', args[i])
                    print('arrival time: ', args[i+1])
                # #FCFS scheduling
                self.new.put(pid)
                self.print_queues()
                self.load_program(args[i], verbose,pid)
                self.ready.put(self.new.get())
                self.print_queues()
                pid+=1
                try:
                    self.arriavl_times.append(args[i+1])
                except:
                    self.arriavl_times.append(0)
        elif command=="rr":
            pid = 1
            for i in range(0,len(args),2):
                if args[i] == "-v":
                    break
                if verbose:
                    print('Program name: ', args[i])
                    print('arrival time: ', args[i+1])
                # #FCFS scheduling
                self.new.put(pid)
                self.print_queues()
                self.load_program(args[i],args[i+1], verbose,pid)
                # self.ready.put(self.new.get())
                self.print_queues()
                pid+=1
                try:
                    self.arriavl_times.append(args[i+1])
                except:
                    self.arriavl_times.append(0)
            self.print_queues()     
            self.round_robin()
            self.print_queues()
            print(self.arriavl_times)
        elif command=="gantt":
            self.print_gantt()        
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

    def print_queues(self):
        # print(list(self.cpus.queue))
        print('-----------------------------------')
        print(f'New queue: {list(self.cpus.queue)}')
        print(f'Ready Queue: {list(self.ready.queue)}')
        print(f'Wait Queue: {list(self.wait.queue)}')
        print(f'Terminated Queue{(self.terminated)}')
        # print(self.arriavl_times)
        print('-----------------------------------')
        
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