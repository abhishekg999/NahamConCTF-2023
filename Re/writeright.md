# **Just One More** (498 pts, 25 solves)

## **Description**
Right, right? right? or left right? whatever.


## **Solution**
We are given a program called `writeright.vsp` which is meant to be run in a processor called `VeSP(VEry Simple Processor)`. The program file itself just has line by line of 4 hex characters representing operations.

```
2000
0000
2001
0000
2001
0004
2000
00CB
0000
3209
0000
2001
0007
2000
...
```

Looking into the `vesp.c` program code they gave, this is what it says.
```c
/* This  computer program simulates the fetch,decode
/* and execute cycles of a hypothetical 16-bit computer,
/* called VESP (_V_Ery _Simple _Processor)
/* Revised to reduce the address field to 12 bits. 2/13/03
/* VESP  has the following registers on which it executes 8 instructions:
/* A:     16 bits (Implicit) It refers to location 0 in  VESP's memory
/* B:     16 bits (Implicit) It refers to location 1 in  VESP's memory
/* MAR:   12 bits  IR:     16 bits  PC:    12 bits
/* Its instruction repertoire consists of the following instructions:
/* ADD: Add         Opcode: 0000  ----- A = A+B HexCode: 0
/* CMP: Compl       Opcode: 0001  ----- A = ~A HexCode: 1
/* LDA: Load        Opcode: 0010  ----- M[IR[3:15] ] = M[MAR+1] HexCode: 2
/* MOV: Move        Opcode: 0011  ----- M[IR[3:15] ] = M[M[MAR+1][3:15]]
HexCode: 3
/* JMP  Jump        Opcode: 0100  ----- PC = IR[3:15] HexCode: 4
/* JEZ: Jump if 0   Opcode: 0101  ----- If (A = 0)  PC = IR[3:15] HexCode: 5
/* JPS: Jump if +   Opcode: 0110  ----- If (A > 0)  PC = IR[3:15] HexCode: 6
/* HLT: Hlt         Opcode: 0111  ----- reset = 1 HexCode: 7 Opcode: 1000  -----
```

So we now can see that VESP is a 16 bit processor. It has 8 supported opcodes, and 2 sort of data registers `A` and `B` which are just the first 2 cells of memory. 

When I started this challenge, I saw that there were so few number of solves, so I assumed it to be alot trickier than it actually was. However due to this, I ended up rewriting the VESP processor in Python so that I can have more fine tune control and debug information about whats happening.

The Python VESP processor can be found [here](vesp.py).

I executed the program and looked at the logs that I had written.
```py
from vesp import VESP, load_program_file

if __name__ == "__main__":
    p = VESP()
    
    program = load_program_file('writeright.vsp')
    p.load(program)

    with open('mem', 'w+') as f:
        while not p.arch.reset:
            p.execute_one_instruction()
```

The full program log is quite verbose. In summary, it repeatedly loads a value to A, loads a value to B, adds A + B, and moves that value somewhere else in memory. Here is the log only showing MOV operations.
```
MOVING VALUE 207 from loc 0 to 521
MOVING VALUE 115 from loc 0 to 384
MOVING VALUE 58 from loc 0 to 299
MOVING VALUE 196 from loc 0 to 571
MOVING VALUE 243 from loc 0 to 288
MOVING VALUE 244 from loc 0 to 553
MOVING VALUE 129 from loc 0 to 467
MOVING VALUE 144 from loc 0 to 527
MOVING VALUE 32 from loc 0 to 464
MOVING VALUE 74 from loc 0 to 471
MOVING VALUE 144 from loc 0 to 440
MOVING VALUE 54 from loc 0 to 381
MOVING VALUE 7 from loc 0 to 425
MOVING VALUE 161 from loc 0 to 395
MOVING VALUE 180 from loc 0 to 512
MOVING VALUE 112 from loc 0 to 576
```

One thing when I was trying to find a flag here initially is I was not sure what I was looking for, and was trying to find ASCII text, however later realized that what I needed was just 16, 2 digit hex values (which hey! we have!). 

I modified the code to get the values that were being MOVED and concatenated them to get the flag.
```py
def OP_MOV(self):
    global Q
    Q.append(self.arch.MEMORY[self.arch.MEMORY[self.arch.MAR + 1]])
    print(f"MOVING VALUE {self.arch.MEMORY[self.arch.MEMORY[self.arch.MAR + 1]]} from loc {self.arch.MEMORY[self.arch.MAR + 1]} to {self.arch.IR & 0x0FFF}")

    self.arch.MEMORY[self.arch.IR & 0x0FFF] = self.arch.MEMORY[self.arch.MEMORY[self.arch.MAR + 1]]
    self.arch.clock += 1
    self.arch.PC += 1
```

```py
Q = []
if __name__ == "__main__":
    p = VESP()
    
    program = load_program_file('writeright.vsp')
    p.load(program)

    while not p.arch.reset:
        p.execute_one_instruction()

    print('flag{' + ''.join("{:02x}".format(x) for x in Q) + '}')
```

```
...
flag{cf733ac4f3f48190204a903607a1b470}
```

## **Flag**: *`flag{cf733ac4f3f48190204a903607a1b470}`*
