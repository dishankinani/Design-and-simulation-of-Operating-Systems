import random as rand
import os
filename = input("Enter the name of the file (add .asm): ")
with open(filename, "w") as f:
    for i in range(int(input("Enter the number of operations: "))):
        random = rand.randint(1, 10)
        if random < 3:
            f.write("ADD R1 R2 R3\n")
        else:
            f.write("SWI 1\n")
