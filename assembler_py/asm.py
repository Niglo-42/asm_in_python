import sys
from enum import Enum

class Type(Enum):
    R = 0
    I = 1
    S = 2
    B = 3
    U = 4
    J = 5
    
N = 11

class Reg:
    reg = {
        "x0": 0,
        "ra": 1,
        "sp": 2,
        "gp": 3,
        "tp": 4,
        "t0": 5,
        "t1": 6,
        "t2": 7,
        "fp": 8,
        "s1": 9,
        "a0": 10,
        "a1": 11,
        "a2": 12,
        "a3": 13,
        "a4": 14,
        "a5": 15,
        "a6": 16,
        "a7": 17,
        "s2": 18,
        "s3": 19,
        "s4": 20,
        "s5": 21,
        "s6": 22,
        "s7": 23,
        "s8": 24,
        "s9": 25,
        "s10": 26,
        "s11": 27,
        "t3": 28,
        "t4": 29,
        "t5": 30,
        "t6": 31
    }

    def get_reg(pos: int, token: str, type: Type) ->int:
        if type == Type.B or type == Type.S:
            pos += 1
        return Reg.reg[token] << [7, 15, 20][pos]

def get_imm(val: int, type: Type, pos: int) -> int:
    if type == Type.I or type == Type.U:
        return int(val << 20) & 0xffffffff
    elif type == Type.S:
        five_bits = (val & 0x1f) << 7
        seven_bits = (val & 0xfe0) << 25
        return int(five_bits | seven_bits) & 0xffffffff
    elif type == Type.J:
        eleven_b = (val & 0xffe) << 20
        bit = (val & 0x1000) << 8
        eight_bits = (val & 0x1fe000) << 1
        return int(eleven_b | bit | eight_bits) & 0xffffffff
    elif type == Type.B:
        val = val - pos
        five_bits = (val & 0x1f) << 7
        seven_bits = (val & 0xfe0) << 20
        return int(five_bits | seven_bits) & 0xffffffff


def instruction_table_init(tab: dict):
    tab["add"] = (0x30, Type.R)
    tab["sub"] = (0x40000030, Type.R)
    tab["and"] = (0x7030, Type.R)
    tab["or"] = (0x6030, Type.R)
    tab["xor"] = (0x4030, Type.R)
    tab["jal"] = (0x6c, Type.J)
    tab["jalr"] = (0x64, Type.I)
    tab["lui"] = (0x34, Type.U)
    tab["auipc"] = (0x14, Type.U)
    tab["sll"] = (0x1030, Type.R)
    tab["slt"] = (0x2030, Type.R)
    tab["sltu"] = (0x3030, Type.R)
    tab["sra"] = (0x40005030, Type.R)
    tab["srl"] = (0x5030, Type.R)
    tab["beq"] = (0x0060, Type.B)
    tab["bge"] = (0x5060, Type.B)
    tab["bgeu"] = (0x7060, Type.B)
    tab["blt"] = (0x4060, Type.B)
    tab["bltu"] = (0x6060, Type.B)
    tab["bne"] = (0x1060, Type.B)
    tab["lb"] = (0x00, Type.R)
    tab["lh"] = (0x1000, Type.R)
    tab["lw"] = (0x2000, Type.R)
    tab["lbu"] = (0x4000, Type.R)
    tab["lhu"] = (0x5000, Type.R)
    tab["sb"] = (0x0020, Type.S)
    tab["sh"] = (0x1020, Type.S)
    tab["sw"] = (0x2020, Type.S)

    tab["addi"] = (0x10, Type.I)
    tab["subi"] = (0x40000010, Type.I)
    tab["andi"] = (0x7010, Type.I)
    tab["ori"] = (0x6010, Type.I)
    tab["xori"] = (0x4010, Type.I)
    tab["slli"] = (0x1010, Type.I)
    tab["slti"] = (0x2010, Type.I)
    tab["sltui"] = (0x3010, Type.I)
    tab["srai"] = (0x40005010, Type.I)
    tab["srli"] = (0x5010, Type.I)
    tab["read_file"] = (0x3060, Type.R)

def shunting_yard(toks: list[str], vars: dict) -> int:
    input = []
    value = {
        "+": 2,
        "-": 1,
        "*": 3,
        "/": 3,
        "(": 0,
        ")": 4
    }
    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b
    }
    holding_stack = []
    solve_stack = []
    output = []
    nbrs = []

    for tok in toks:
        nbrs.append([])
        char = 0
        while char < len(tok):
            if tok in vars:
                try:
                    input.append(int(vars[tok]))
                except ValueError:
                    exit(1)
                break
            elif tok[char] in "*/-+()":
                input.append(tok[char])
                char += 1
            else:
                nbr = 0
                while char < len(tok) and tok[char].isdigit():
                    nbr = nbr * 10 + int(tok[char])
                    char += 1
                input.append(nbr)
    i = 0
    while i < len(input):
        if isinstance(input[i], int):
            output.append(input[i])
        elif input[i] == ")":
            while holding_stack[-1] != "(":
                output.append(holding_stack.pop())
            holding_stack.pop()
        else:
            while (holding_stack and value[holding_stack[-1]] > value[input[i]]
                   and input[i] != "("):
                output.append(holding_stack.pop())
            holding_stack.append(input[i])
        i += 1
    while holding_stack:
        output.append(holding_stack.pop())
    if len(output) < 2:
        return int(output[0])
    while output:
        while output and isinstance(output[0], int):
            solve_stack.append(output.pop(0))
        if len(solve_stack):
            b = solve_stack.pop()
        if len(solve_stack):
            a = solve_stack.pop()
        solve_stack.append(ops[output.pop(0)](a, b))
    return int(solve_stack[0])


def asm(executable: list):
    instruction_table = {}
    instruction_table_init(instruction_table)
    tokens = []
    labels = {}
    vars = {}
    const = {}
    i = 0
    with open("bootloader.s", "r") as file:
        for line in file:
            line = line.strip()
            # line = line.split(";", 1)[0].strip()
            if not line or line.startswith(";"):
                continue
            tokens.append(line.split(" "))
            label = tokens[-1][0].find(":")
            if label >= 0:
                labels[tokens[-1][0][0: label]] = i
            elif tokens[-1][0].startswith("var"):
                if len(tokens[-1]) == 3:
                    vars[tokens[-1][1]] = int(tokens[-1][2][1:])
                elif len(tokens[-1]) > 3:
                    raise ValueError("trop d'elements dans la def var")
                else:
                    vars[tokens[-1][1]] = 0
            elif tokens[-1][0].startswith("const"):
                if len(tokens[-1]) > 2:
                    const[tokens[-1][1]] = shunting_yard(tokens[-1][2:], vars)
                else:
                    raise ValueError("des trucs")
            else:
                i += 1
        nb_line = 0
        line_src = 0
        type = Type.R
        executable.append(0)
        # print('\n'.join(str(t) for t in tokens))
        for line in tokens:
            line_src += 1
            pos_token = 0
            if line[0].startswith("const") or line[0].startswith("var"):
                print(f"{line[1]=}")
                continue
            for token in line:
                token = token.strip(",")
                if token.startswith(";") or token.startswith(" ") or token.startswith("\n"):
                    continue
                if token == "" or token == "\n":
                    continue
                if token == "var" or token == "const":
                    break
                if token == "halt":
                    executable[nb_line] |= 0xffffffff
                    return
                if token in instruction_table:
                    type = instruction_table[token][1]
                    executable[nb_line] |= instruction_table[token][0]
                elif token.endswith(":"):
                    continue
                elif token in vars:
                    executable[nb_line] |= vars[token]
                elif token in const:
                    executable[nb_line] |= get_imm(const[token], Type.I, 0)
                elif token in labels:
                    imm = get_imm(labels[token], type, nb_line)
                    if imm == -1:
                        return print(f"error at line {nb_line + 1}, {token=}")
                    executable[nb_line] |= imm
                elif token in Reg.reg:
                    executable[nb_line] |= Reg.get_reg(pos_token, token, type)
                    pos_token += 1
                elif token.startswith("#"):
                    imm = get_imm(int(token[1:]), type, 0)
                    if imm == -1:
                        return print(f"error at line {nb_line}, {token=}")
                    executable[nb_line] |= imm
                else:
                    raise ValueError(
                        f"Value Error at line {line_src}, {token=}")
            if executable[nb_line]:
                executable.append(0)
                nb_line += 1


def main():
    exec = []
    asm(exec)
    for line in exec:
        print(hex(line))
    lenght = len(exec) * 4 + 4
    with open("bootloader.bin", "wb") as f:
        f.write(lenght.to_bytes(4, byteorder="little"))
        for byte in exec:
            f.write(byte.to_bytes(4, byteorder="little"))

if __name__ == "__main__":
    main()
