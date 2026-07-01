import sys
from data_asm import Reg, Type, Instruction
from shunting_yard import shunting_yard
import os
import lexer
N = 11

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

class Asm:
    labels = {}
    vars = {}
    const = {}
    pc = 0

    def pass0(path: str) ->None:
        Asm.pc = 0
        tokens = []
        with open(path, "r") as file:
            for line in file:
                line = line.split(";", 1)[0].strip()
                if not line or line.startswith(";"):
                    continue
                tok = line.split()
                tokens.append(tok)
                first = tok[0]
                if first.endswith(":"):
                    Asm.labels[first[:-1]] = Asm.pc
                elif first == "var":
                    if len(tok) == 3:
                        Asm.vars[tok[1]] = int(tok[2][1:])
                    elif len(tok) > 3:
                        raise ValueError("trop d'elements dans la def var")
                    else:
                        Asm.vars[tok[1]] = 0
                elif first == "const":
                    if len(tok) > 2:
                        Asm.const[tok[1]] = shunting_yard(tok[2:], Asm.vars)
                    else:
                        raise ValueError("des trucs")
                else:
                    Asm.pc += 1
        return tokens
    
    def pass1(tokens):
        executable = []
        for line_src, line in enumerate(tokens, 1):
            if is_com(line[0]):
                continue
            try:
                instr = parse_instr(line_src, line)
            except Exception as e:
                print(e)
            if instr:
                executable.append(instr)
                Asm.pc += 1
        return executable

def asm(path):
    Asm.pc = 0
    tokens = Asm.pass0(path)
    Asm.pc = 0
    return Asm.pass1(tokens)

def parse_instr(line_src, line) -> Instruction:
    opcode, type = Instruction[line[0]]
    instr = Instruction(opcode, type)
    pos_reg = 0
    for pos_token, token in enumerate(line):
        token = token.strip(",")
        if token.startswith(";"):
            return instr
        if not token:
            return None
        if token == "var" or token == "const" or is_label(token):
            return None
        if token in Instruction.tab:
            raise ValueError(f"only one opcode pls, error at line {line_src}")
        elif token in Asm.vars:
            instr.imm = get_imm(Asm.vars[token], instr.type, 0)
        elif token in Asm.const:
            instr.imm = get_imm(Asm.const[token], Type.I, 0)
        elif token in Asm.labels:
            instr.imm = get_imm(Asm.labels[token], instr.type, Asm.pc)
        elif token in Reg.reg:
            if instr.type == Type.S or instr.type == Type.B:
                if pos_reg > 1:
                    raise ValueError("too much regs for B or S type")
                if pos_reg == 0:
                    instr.rs1 = Reg.get_reg(pos_reg + 1, token, type)
                if pos_reg == 1:
                    instr.rs2 = Reg.get_reg(pos_reg + 1, token, type)
            else:
                if pos_reg > 2:
                    raise ValueError("too much regs")
                if pos_reg == 0:
                    instr.rd = Reg.get_reg(pos_reg, token, type)
                if pos_reg == 1:
                    instr.rs1 = Reg.get_reg(pos_reg, token, type)
                if pos_reg == 2:
                    instr.rs2 = Reg.get_reg(pos_reg, token, type)
            pos_reg += 1
        elif token.startswith("#"):
            instr.imm = get_imm(int(token[1:]), instr.type, 0)
        else:
            raise ValueError(
                f"Value Error at line {line_src}, {token=}")
    return instr

def is_label(tok: str)->bool:
    return tok.endswith(":")

def is_com(tok: str)->bool:
    return tok.startswith(";")

def asm_to_binary(path: str):
    if path is None:
        path = "bootloader.s"
    exec = asm(path)
    for line in exec:
        print(hex(line))
    path = redirect_path(path)
    
    with open(path, "wb") as f:
        for byte in exec:
            f.write(byte.to_bytes(4, byteorder="little"))
        f.write(0x00000000.to_bytes(4, byteorder="little"))

def redirect_path(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    # dir/test.s -> ('test', '.s')
    path = "bin/" + name + "_output.bin"
    return path

def main():
    if len(sys.argv) > 2:
        print ("too much args, require only the path of the file" \
        "to assemble")
        return
    asm_to_binary(sys.argv[1])

if __name__ == "__main__":
    main()