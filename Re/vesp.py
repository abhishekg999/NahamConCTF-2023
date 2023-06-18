# VESP rewritten in Python
# https://user.eng.umd.edu//~yavuz/teaching/courses/enee350/vesp-source-code/vesp1.1X/main.cpp


class Arch:
    def __init__(self):
        self.MAR = 0
        self.PC = 0
        self.IR = 0
        self.clock = 0

        self.MEMORY = [0] * 8192

        self.S = 0
        self.C = 0
        self.F = 0
        self.Z = 0

        self.reset = 0
        self.add = 0
        self.complement = 0

    def rreset(self, clear_mem=False):
        self.MAR = 0
        self.PC = 0
        self.IR = 0
        self.clock = 0

        if clear_mem:
            self.MEMORY = [0] * 8192

        self.S = 0
        self.C = 0
        self.F = 0
        self.Z = 0

        self.reset = 0
        self.add = 0
        self.complement = 0

    def memdump(self):
        return self.MEMORY

    def regdump(self):
        return {
            "MAR": hex(self.MAR),
            "PC": hex(self.PC),
            "IR": hex(self.IR),
            "S": hex(self.S),
            "C": hex(self.C),
            "F": hex(self.F),
            "Z": hex(self.Z),
        }


def hex_to_int(hex_string):
    return int(hex_string, 16)


class VESP:
    def __init__(self) -> None:
        self.arch = Arch()

        self.OP_DICT = {
            0b0000: self.OP_ADD,
            0b0001: self.OP_CMP,
            0b0010: self.OP_LDA,
            0b0011: self.OP_MOV,
            0b0100: self.OP_JMP,
            0b0101: self.OP_JEZ,
            0b0110: self.OP_JPS,
            0b0111: self.OP_HLT,
        }

    def reset(self, start=2):
        self.arch.rreset()
        self.arch.PC = start

    def load(self, program, offset=2):
        self.program = program
        self.arch.PC = offset

        address = self.arch.PC
        for instruction in program:
            self.arch.MEMORY[address] = hex_to_int(instruction)
            address += 1

    def _fetch(self):
        # increment PC
        self.arch.MAR = self.arch.PC
        self.arch.PC = self.arch.PC + 1
        self.arch.clock = self.arch.clock + 1

        # load next instruction
        self.arch.IR = self.arch.MEMORY[self.arch.MAR]

        self.arch.clock = self.arch.clock + 1

    def _decode(self):
        # doesn't do anything
        pass

    def OP_ADD(self):
        temp = (self.arch.MEMORY[0] + self.arch.MEMORY[1]) & 0xFFFF

        if (
            self.arch.MEMORY[0] > 0
            and self.arch.MEMORY[1] > 0
            and temp < 0
            or self.arch.MEMORY[0] < 0
            and self.arch.MEMORY[1] < 0
            and temp >= 0
        ):
            self.arch.F = 1
        else:
            self.arch.F = 0  # Set Overflow flag

        if (
            self.arch.MEMORY[0] < 0
            and self.arch.MEMORY[1] < 0
            or temp > 0
            and (
                self.arch.MEMORY[0] < 0
                and self.arch.MEMORY[1] > 0
                or self.arch.MEMORY[0] > 0
                and self.arch.MEMORY[1] < 0
            )
        ):
            self.arch.C = 1
        else:
            self.arch.C = 0  # Set Carry Flag

        print(f"ADDED {self.arch.MEMORY[0]} + {self.arch.MEMORY[1]} = {temp}")
        self.arch.MEMORY[0] = temp  # Save the sum in MEMORY[0]

        # Set Zero Flag
        if self.arch.MEMORY[0] == 0:
            self.arch.Z = 1
        else:
            self.arch.Z = 0

        # Set Sign Flag
        self.arch.S = (self.arch.MEMORY[0] & 0x8000) >> 15
        self.arch.add = 1

    def OP_CMP(self):
        self.arch.MEMORY[0] = ~self.arch.MEMORY[0] & 0xFFFF
        self.arch.complement = 1

    def OP_LDA(self):
        print(
            f"LOADING VALUE {self.arch.MEMORY[self.arch.MAR + 1]} to location {self.arch.IR & 0x0FFF}"
        )

        self.arch.MEMORY[self.arch.IR & 0x0FFF] = self.arch.MEMORY[self.arch.MAR + 1]
        self.arch.PC += 1

    def OP_MOV(self):
        print(
            f"MOVING VALUE {self.arch.MEMORY[self.arch.MEMORY[self.arch.MAR + 1]]} from loc {self.arch.MEMORY[self.arch.MAR + 1]} to {self.arch.IR & 0x0FFF}"
        )

        self.arch.MEMORY[self.arch.IR & 0x0FFF] = self.arch.MEMORY[
            self.arch.MEMORY[self.arch.MAR + 1]
        ]
        self.arch.clock += 1
        self.arch.PC += 1

    def OP_JMP(self):
        self.arch.PC = self.arch.IR & 0x1FFF

    def OP_JEZ(self):
        if self.arch.MEMORY[0] == 0:
            self.arch.PC = self.arch.IR & 0x0FFF

    def OP_JPS(self):
        if self.arch.MEMORY[0] > 0:
            self.arch.PC = self.arch.IR & 0x0FFF

    def OP_HLT(self):
        self.arch.reset = 1

    def _get_op_name(self, opcode):
        s = str(self.OP_DICT[opcode])
        i = s.index("OP")
        return s[i : i + 6]

    def _execute(self):
        opcode = (self.arch.IR >> 12) & 0xF

        print(f"Executing {self._get_op_name(opcode)}")

        # execute operation
        self.OP_DICT[opcode]()
        self.arch.clock += 1

    def execute_one_instruction(self):
        self._fetch()
        self._decode()
        self.arch.add, self.arch.complement = 0, 0
        self._execute()


def load_program_file(file):
    with open(file, "r") as f:
        content = f.read().split("\n")

    return content


if __name__ == "__main__":
    p = VESP()

    while not p.arch.reset:
        p.execute_one_instruction()
