import queue
from loader import Loader
from register import Register
from mainmemory import Memory
from CPU import CPU
import datetime
import subprocess
from ProgramLoadError import ProgramLoadError
import MMU
from RAM import Ram
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
        self.programs_pid={}
        self.arrival_program_dict={}
        self.pid=1
        self.Sched="FCFS"
        self.mmu = MMU.mmu(self.memory)
        self.ram = Ram(self.mmu.get_page_number(),self.mmu.get_page_size(),self.memory)
        

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
    
    def load_mmu(self, filename,i):
        try:
            b_size, PC, process_pages = self.mmu.load_program(filename, self.verbose, pid=self.pid)
            new_cpu = CPU(self.memory, self.registers, 0, b_size-PC, 0, self.verbose, pid=self.pid, process_pages=process_pages)
            if i==0:
                for page in range(int(self.mmu.get_page_number())):
                    self.ram.load_page(process_pages[page])
                # process_pages.pop(page)
            print(new_cpu.process_pages)
            if self.verbose:
                print(f"Loaded {filename} into memory. Byte Size: {b_size}, First instructions address: {PC}")
                print(f'{filename} status set to ready')
            #changing cpu state to ready
            new_cpu.state = 'ready'
            self.cpus.put(new_cpu)
        except Exception as e:
            self.errordump(e)


    def run_program(self):
        try:
            while not self.cpus.empty():
                
                print(list(self.cpus.queue))
                running = self.cpus.get()
                #print(running)
                running.state = 'running'
               
                running.execute_program(self.ram)
                if self.verbose:
                    print('process set to running')
                    print("Program executed.")
                
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
                    self.registers.main_gantt.append('X')
            
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
                        self.loader.remove_loader_address(running.loader_address,running.b_size)
                        break
                    running.restore_registers()
                    running.execute_single_instruction()
                    self.registers.increment('CLOCK')
                    self.registers.gantt.append(running.pid)
                    self.registers.gantt1.append('X')
                    self.registers.ganttfcfs.append('X')
                    self.registers.main_gantt.append(running.pid)

                    if running.state == "waiting": # if hit swi
                        running.copy_registers()
                        running.successful_bursts+=1
                        #print('please don\'t be here')
                        if running.failed_bursts+running.successful_bursts == 5 and  running.successful_bursts < 4:
                            running.successful_bursts=0
                            running.failed_bursts=0
                            self.ready1.put(running)
                        else:
                            self.ready.put(running)
                        break
                if running and running.state != 'terminated' and running.state != 'waiting':
                    running.copy_registers()
                    running.failed_bursts+=1
                    if running.failed_bursts+running.successful_bursts == 5 and  running.successful_bursts < 4:
                        running.successful_bursts=0
                        running.failed_bursts=0
                        self.ready1.put(running)
                    else:
                        self.ready.put(running)
                    running.state = 'ready'
                        
                        
            if queue == self.ready1 and not self.ready1.empty():
                running = self.ready1.get()
                for _ in range(self.quantum2):
                    if running.state == "terminated":
                        self.loader.remove_loader_address(running.loader_address,running.b_size)
                        break
                    running.restore_registers()
                    running.execute_single_instruction()
                    self.registers.increment('CLOCK')
                    self.registers.gantt.append("X")
                    self.registers.gantt1.append(running.pid)
                    self.registers.ganttfcfs.append("X")
                    self.registers.main_gantt.append(running.pid)
                    if running.state=="waiting": # hit an swi, completed cpu burst
                        running.successful_bursts +=1
                        running.copy_registers()
                        if self.promote_demote(running,self.ready,self.fcfs_queue, self.ready1):
                            break
                        else:
                            self.ready1.put(running)
                        break
                if running and running.state != 'terminated' and running.state != 'waiting':
                    running.failed_bursts +=1
                    if self.promote_demote(running,self.ready,self.fcfs_queue, self.ready1):
                        pass
                    else:
                        running.copy_registers()
                        self.ready1.put(running)
                    running.state = 'ready'
                    

            if queue==self.fcfs_queue and not self.fcfs_queue.empty():
                running = self.fcfs_queue.get()
                running.execute_program()
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
        
    def print_main_gantt(self):
        print("Main Gantt Chart:")
        print(self.registers.main_gantt)
        
    def print_page_table(self):
        # print("Page Table:")
        self.mmu.print_page_table()

    def ps(self):
        print(f"Free memory size = {len(self.mmu.free_pages)*self.mmu.get_page_size()}/{self.memory.size}")
        print("Free pages")
        print(self.mmu.free_pages)
        # print(f"Memory in use: {}")
        print("Pages associated with PIDs:")
        self.mmu.print_page_table()


    def get_page_size(self):
        print("Page size =",self.mmu.get_page_size())
    
    def set_page_number(self,args):
        self.mmu.set_page_number(int(args))
        self.ram.number_of_pages = int(args)

    def run_command(self, command, args):
        self.verbose = "-v" in args
        if self.verbose:
            print(self.registers)
        
        if command == "load":
            self.registers.clear()
            self.registers.clearClock()
            self.registers.clear_gantt()
            for i in range(0,len(args)):
                filename=args[i]
                if args[i] == "-v":
                    break 
                if self.verbose:
                    print('Program name: ', args[i])
                # #FCFS scheduling
                self.new.put(self.pid)
                #self.print_queues()
                self.load_mmu(filename,i)
                #self.print_queues()
                self.pid+=1
        elif command == "help":
            self.print_help()
        elif command == "print_ram":
            self.ram.print_ram()
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
        elif command == "set_page_size":
            self.memory.set_page_size(int(args[0]))
            self.mmu.set_page_size(int(args[0]))
            self.ram.page_size = int(args[0])
            
            if self.verbose:
                print(f"Page size set to {self.memory.page_size}")
        elif command == "set_page_number":
            self.set_page_number(args[0])
        elif command == "page_faults":
            print("Number of page Faults:",self.ram.page_faults)
        elif command=="setrr":
            self.quantum = int(args[0])
            magnitude = int(args[1])
            self.quantum2=self.quantum*magnitude
            if self.verbose:
                print(f"Quantum set to {self.quantum}")
                
        elif command == "setSched":
            self.Sched=args[0]
            if self.verbose:
                print(f"The Chosen Algorithm is {self.Sched}")

        elif command == "displaypageinfo":
            self.ps()

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
        elif command == "main_gantt":
            self.print_main_gantt() 
        elif command == "getpagesize":
            self.get_page_size()
        elif command == "page_table":
            self.print_page_table()      
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
            
    def print_help(self):
        from rich.console import Console
        from rich.table import Table
        console = Console()
        table = Table(title="OS Commands", show_lines=True)
        table.add_column("Commands", style="bold")
        table.add_column("Utility", justify="center")
        table.add_column("Example", justify="center")
        table.add_row("verbose", "Set OS to verbose mode", "-v")
        table.add_row("load", "loads programs into memory", "load program1.osx ... programn.osx")
        table.add_row("run", "runs programs that are loaded", "run")
        table.add_row("setSched", "Sets the CPU scheduler to RR or MFQ", "setSched mfq")
        table.add_row("setrr", "set the quantums for the round robin, first is quantum size and second is ratio", "setrr {quantum} {ratio}")
        table.add_row("execute","Loads and runs n programs using the selected scheduler","execute program1.osx {arrival_time}...programn.osx {arrival_time}")
        table.add_row("osx","compile listed .asm file to .osx","osx {filename} {loader_address}")
        table.add_row("gantt","Displays the gantt chart from the multi-level feedback queue","gantt")
        table.add_row("main_gantt","prints a gantt chart for all queues in one array","main_gantt")
        table.add_row("clearOS","Clears registers and reinstantiates main memory and loader class","clearOS")
        table.add_row("shell","Starts a new shell","shell")
        table.add_row("coredump","Prints memory and registers to coredump.txt if verbose prints to console","coredump")
        table.add_row("errordump","prints errordump to errordump.txt","errordump")
        table.add_row("ps -proc -free","displays the state of memory, free pages, and pages associated with PIDs","displaypageinfo")
        table.add_row("page table","prints pages assigned a PID","page_table")
        table.add_row("set page size","sets the size (in bytes) of a page in  memory","set_page_size {size}")
        table.add_row("get page size","returns the size (in bytes) of a page in  memory","getpagesize")
        table.add_row("set page number","sets the number of pages stored in virtual memory for quick access","set_page_number {args}")
        # table.add_row("","","")
        console.print(table)
        

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