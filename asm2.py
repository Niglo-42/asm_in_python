import sys
from data_asm import Reg, Type, Instruction
from shunting_yard import shunting_yard
import os
from lexer import Lexer, Token
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



def asm(path):
    with open(path, "r") as src:
        lex = Lexer(src.read())
    lex.lexe()
    lex.print_token()
    

def asm_to_binary(path: str):
    if path is None:
        path = "bin/bootloader.s"
    exec = asm(path)
    if exec == None:
        return
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