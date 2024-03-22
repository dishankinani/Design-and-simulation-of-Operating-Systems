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
        self.ready = queue.Queue()
        self.ready1 = queue.Queue()
        self.fcfs_queue = queue.Queue()
        self.terminated=[]
        self.wait=queue.Queue()
        self.arriavl_times = []
        self.clock = 0 # clock is used to keep track of instructions ran
        self.quantum = 8
        self.quantum2 = 16
        self.verbose=False
        self.arrival_program_dict={}
        self.pid=1
        self.Sched="FCFS"
        

    def load_program(self, filename, arrival_time):
        try:
            b_size, first_instruction_address, loader_address = self.loader.loader(filename, self.verbose)
            new_cpu = CPU(self.memory, self.registers, loader_address, b_size, first_instruction_address, self.verbose, pid=self.pid, arrival_time = arrival_time)
            self.registers.write('PC', first_instruction_address)
            #print(self.re)
            if self.verbose:
                print(f"Loaded {filename} into memory. Byte Size: {b_size}, First instructions address: {loader_address+ first_instruction_address}, Loader Address: {loader_address}")
                print(f'{filename} status set to ready')
            #changing cpu state to ready
            new_cpu.state = 'ready'
            self.cpus.put(new_cpu)
            if self.verbose:
                print(list(self.cpus.queue)) #testing the queue/ ganntt chart
        except Exception as e:
            self.errordump(e)

    def run_program(self):
        try:
            while not self.cpus.empty():
                
                #print(list(self.cpus.queue))
                running = self.cpus.get()
                #print(running)
                running.state = 'running'
               
                running.execute_program()
                if self.verbose:
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
        while not self.cpus.empty() or not self.ready.empty() or self.arriavl_times:
            print(f"Value of clock {self.registers.read('CLOCK')}")
            if self.arriavl_times:
                    while self.arriavl_times and self.arriavl_times[0] <= self.registers.read('CLOCK') :
                        #print(f"self.cpus.queue[0].arrival_time={self.cpus.queue[0].arrival_time}")
                        program_name=self.arrival_program_dict.get(str(self.arriavl_times[0]))
                        self.load_program(program_name,self.arriavl_times[0])
                        self.pid+=1
                        del self.arrival_program_dict[str(self.arriavl_times.pop(0))]
                        self.ready.put(self.cpus.get())
            if self.ready.empty():
                for x in range(self.quantum):
                    self.registers.increment('CLOCK')
                    self.registers.gantt.append('X')
            
            if not self.ready.empty():
                running = self.ready.get()
                running.restore_registers()
                for _ in range(self.quantum):
                    if running.state == 'terminated':
                        if running.pid not in self.terminated:
                            self.terminated.append(running.pid)
                        self.registers.gantt.append('X')
                        self.registers.increment('CLOCK')
                        # not sure whether needed or not
                        # del running
                        continue
                    running.execute_single_instruction()
                    self.registers.gantt.append(running.pid)
                if running.state == 'terminated':
                    self.loader.remove_loader_address(running.loader_address,running.b_size)
                if self.arriavl_times:
                    while self.arriavl_times and self.arriavl_times[0] <= self.registers.read('CLOCK') :
                        #print(f"self.cpus.queue[0].arrival_time={self.cpus.queue[0].arrival_time}")
                        program_name=self.arrival_program_dict.get(str(self.arriavl_times[0]))
                        self.load_program(program_name,self.arriavl_times[0])
                        self.pid+=1
                        del self.arrival_program_dict[str(self.arriavl_times.pop(0))]
                        self.ready.put(self.cpus.get())
                if running.state != 'terminated': 
                    running.copy_registers()
                    self.ready.put(running)
        # except Exception as e:
        #     self.errordump(e)
        # pass
        
    def mfq(self):
        while not self.cpus.empty() or not self.ready.empty() or not self.ready1.empty() or not self.fcfs_queue.empty() or self.arriavl_times:
            if self.arriavl_times:
                while self.arriavl_times and self.arriavl_times[0] <= self.registers.read('CLOCK') :
                    #print(f"self.cpus.queue[0].arrival_time={self.cpus.queue[0].arrival_time}")
                    program_name=self.arrival_program_dict.get(str(self.arriavl_times[0]))
                    self.load_program(program_name,self.arriavl_times[0])
                    self.pid+=1
                    del self.arrival_program_dict[str(self.arriavl_times.pop(0))]
                    self.ready.put(self.cpus.get())
            if self.ready.empty() and self.ready1.empty() and self.fcfs_queue.empty():
                for _ in range(self.quantum):
                    self.registers.increment('CLOCK')
                    self.registers.gantt.append('X')
                    self.registers.gantt1.append('X')
                    self.registers.ganttfcfs.append('X')
            
            self.alternate_roundrobin(quantums = 4, queue = self.ready)
            self.alternate_roundrobin(quantums = 2, queue = self.ready1)
            self.alternate_roundrobin(quantums = 1, queue = self.fcfs_queue)
        
    
    def alternate_roundrobin(self, quantums, queue):
        
        if queue.empty():
            return
        for _ in range(0,quantums):
            if self.arriavl_times:
                while self.arriavl_times and self.arriavl_times[0] <= self.registers.read('CLOCK') and self.arrival_program_dict:
                    #print(f"self.cpus.queue[0].arrival_time={self.cpus.queue[0].arrival_time}")
                    program_name=self.arrival_program_dict.get(str(self.arriavl_times[0]))
                    self.load_program(program_name,self.arriavl_times[0])
                    self.pid+=1
                    del self.arrival_program_dict[str(self.arriavl_times.pop(0))]
                    self.ready.put(self.cpus.get())
                
            if queue == self.ready and not self.ready.empty():
                running = self.ready.get()
                for _ in range(self.quantum):
                    if running.state == "terminated":
                        if running.loader_address in self.loader.loader_address_stack:
                            self.loader.remove_loader_address(running.loader_address,running.b_size)
                        break
                    running.restore_registers()
                    running.execute_single_instruction()
                    self.registers.increment('CLOCK')
                    self.registers.gantt.append(running.pid)
                    self.registers.gantt1.append('X')
                    self.registers.ganttfcfs.append('X')

                    if running.state == "waiting": # if hit swi
                        running.copy_registers()
                        running.state = 'ready'
                        running.successful_bursts+=1
                        # print('please don\'t be here')
                        if running.failed_bursts+running.successful_bursts == 5 and  running.successful_bursts < 4:
                            running.successful_bursts=0
                            running.failed_bursts=0
                            self.ready1.put(running)
                        else:
                            self.ready.put(running)
                        break
                if running and running.state != 'terminated':
                    running.copy_registers()
                    running.failed_bursts+=1
                    if running.failed_bursts+running.successful_bursts == 5 and  running.successful_bursts < 4:
                        running.successful_bursts=0
                        running.failed_bursts=0
                        self.ready1.put(running)
                    else:
                        self.ready.put(running)
                        
                        
            if queue == self.ready1 and not self.ready1.empty():
                running = self.ready1.get()
                for _ in range(self.quantum2):
                    if running.state == "terminated":
                        if running.loader_address in self.loader.loader_address_stack:
                            self.loader.remove_loader_address(running.loader_address,running.b_size)
                        break
                    running.restore_registers()
                    running.execute_single_instruction()
                    self.registers.increment('CLOCK')
                    self.registers.gantt.append("X")
                    self.registers.gantt1.append(running.pid)
                    self.registers.ganttfcfs.append("X")
                    if running.state=="waiting": # h it an swi, completed cpu burst
                        running.successful_bursts +=1
                        running.copy_registers()
                        running.state = "ready"
                        if self.promote_demote(running,self.ready,self.fcfs_queue, self.ready1):
                            break
                        else:
                            self.ready1.put(running)
                        running = None
                        break
                if running:
                    running.failed_bursts +=1
                    if self.promote_demote(running,self.ready,self.fcfs_queue, self.ready1):
                        pass
                    else:
                        running.copy_registers()
                        self.ready1.put(running)

            if queue==self.fcfs_queue and not self.fcfs_queue.empty():
                running = self.fcfs_queue.get()
                running.execute_program()
                if running.state == "terminated":
                        self.loader.remove_loader_address(running.loader_address,running.b_size)
        
    
    def fcfs(self):
        pass

    def promote_demote(self, running , promote_destination,demote_destination, source) -> bool:
        if running.failed_bursts+running.successful_bursts == 5 and  running.successful_bursts >= 4:
            promote_destination.put(running)
            running.successful_bursts=0
            running.failed_bursts=0
            return True
        elif running.failed_bursts+running.successful_bursts == 5 and  running.successful_bursts < 4:
            demote_destination.put(running)
            running.successful_bursts=0
            running.failed_bursts=0
            return True
        else:
            return False
        # else:
        #     source.put(running)    

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
        print(f"First Queue (quantum = {self.quantum}):")
        print(self.registers.gantt)
        print(f"Second Queue (quantum = {self.quantum2}):")
        print(self.registers.gantt1)
        print("FCFS Queue:")
        print(self.registers.ganttfcfs)

    def run_command(self, command, args):
        self.verbose = "-v" in args
        if self.verbose:
            print(self.registers)
        if command == "load":
            filename = args[0] if args else None
            if filename:
                self.load_program(filename,0)
            else:
                print("No filename provided for load command.")
        elif command == "run":
            self.run_program()
        elif command=="coredump":
            if self.verbose:
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
                    
        elif command=="clearOS":
            self.memory = Memory()
            self.registers = Register()
            self.loader = Loader(self.memory)
            self.cpus = queue.Queue()

        elif command=="errordump":
            self.print_errordump()
        elif command=="shell":
            self.start_new_instance()
        elif command=="osx":
            filename = args[0] if args else None
            if filename:
                if args[1]:
                    self.osx(filename, args[1])
                else:
                    self.osx(filename)
            else:
                print("No filename provided for load command.")
        elif command=="oldexecute":
            pid = 1
            for i in range(0,len(args),2):
                if args[i] == "-v":
                    break
                if self.verbose:
                    print('Program name: ', args[i])
                    print('arrival time: ', args[i+1])
                # #FCFS scheduling
                self.new.put(pid)
                self.print_queues()
                self.load_program(args[i], self.verbose)
                self.ready.put(self.new.get())
                self.print_queues()
                pid+=1
                try:
                    self.arriavl_times.append(int(args[i+1]))
                except:
                    self.arriavl_times.append(0)
        
        elif command=="setrr":
            self.quantum = int(args[0])
            self.quantum2 = int(args[1])
            if self.verbose:
                print(f"Quantum set to {self.quantum}")
                
        elif command == "setSched":
            self.Sched=args[0]
            if self.verbose:
                print(f"The Chosen Algorithm is {self.Sched}")

        elif command=="execute":
            if self.Sched == "fcfs":
                self.fcfs()
            if self.Sched=="mfq":
                self.registers.clear()
                self.registers.clearClock()
                self.registers.clear_gantt()
                for i in range(0,len(args),2):
                    if args[i] == "-v":
                        break 
                    if self.verbose:
                        print('Program name: ', args[i])
                        print('arrival time: ', args[i+1])
                    # #FCFS scheduling
                    self.new.put(self.pid)
                    #self.print_queues()
                    program_name = args[i]
                    arrival_time = args[i + 1]
                    if i==0:
                        self.load_program(args[i],args[i+1])
                        self.ready.put(self.cpus.get())
                    else:
                        self.arrival_program_dict[arrival_time] = program_name
                    #self.print_queues()
                    self.pid+=1
                    try:
                        if i!=0:
                            self.arriavl_times.append(int(args[i+1]))
                    except:
                        self.arriavl_times.append(0)
                self.arriavl_times.sort()      
                print(self.arriavl_times)
                print(self.arrival_program_dict)
                self.mfq()
                '''
                run 3 queues 4, 2, 1 processes
                restart, 
                if cpu burst doesn't finish(hitting IO) -> demote to queue 1
                if cpu burst finishes in 2 -> promote to queue 0
                if cpu burst doesnt finish in 2 -> demote to fcfs
                '''
            elif self.Sched == "rr":
                self.registers.clear()
                self.registers.clearClock()
                self.registers.clear_gantt()
                for i in range(0,len(args),2):
                    if args[i] == "-v":
                        break 
                    if self.verbose:
                        print('Program name: ', args[i])
                        print('arrival time: ', args[i+1])
                    # #FCFS scheduling
                    self.new.put(self.pid)
                    #self.print_queues()
                    program_name = args[i]
                    arrival_time = args[i + 1]
                    if i==0:
                        self.load_program(args[i],args[i+1])
                        self.ready.put(self.cpus.get())
                    else:
                        self.arrival_program_dict[arrival_time] = program_name
                    #self.print_queues()
                    self.pid+=1
                    try:
                        if i!=0:
                            self.arriavl_times.append(int(args[i+1]))
                    except:
                        self.arriavl_times.append(0)
                self.arriavl_times.sort()      
                print(self.arriavl_times)
                print(self.arrival_program_dict)
                #self.print_queues()     
                self.round_robin()
                #self.print_queues()
        elif command=="gantt":
            self.print_gantt()        
        else:
            print("Command Not Found")
        
    def osx(self, filename, loader_address=0):
        if loader_address != 0:
            load_address = loader_address
        else:
            load_address = str(self.loader.loader_address_stack[-1] + 1)
        command = f'osx.exe {filename} {load_address}'
        #brkt_command = ['osx.exe', filename, load_address]
        try:
            subprocess.run(command, check=False, shell=True)  # Add shell=True parameter
            if self.verbose:
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