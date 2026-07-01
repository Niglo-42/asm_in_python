from enum import Enum

class TokenType(Enum):
    # structure
    OPCODE  = 0
    REG     = 1
    IDENT   = 2
    NUMBER  = 3

    # syntaxe
    COMMA       = 10
    COLON       = 11
    LPAREN      = 12
    RPAREN      = 13
    LBRAKET     = 14
    RBRAKET     = 15
    LSCOPE      = 16
    RSCOPE      = 17
    SEMICOMMA   = 18

    # contrôle / directives
    DIRECTIVE   = 20
    COMMENT     = 21
    LABEL_DEF   = 22

SYMBOLS = {
    ",": TokenType.COMMA,
    # ":": TokenType.COLON,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "[": TokenType.LBRAKET,
    "]": TokenType.RBRAKET,
    "{": TokenType.LSCOPE,
    "}": TokenType.RSCOPE,
}

REGISTERS = {
    "x0": True, "ra": True, "sp": True, "gp": True, "tp": True,
    "t0": True, "t1": True, "t2": True,
    "fp": True, "s1": True,
    "a0": True, "a1": True, "a2": True, "a3": True,
    "a4": True, "a5": True, "a6": True, "a7": True,
    "s2": True, "s3": True, "s4": True, "s5": True,
    "s6": True, "s7": True, "s8": True, "s9": True,
    "s10": True, "s11": True,
    "t3": True, "t4": True, "t5": True, "t6": True,
}

OPCODES = {
    # R type
    "add": TokenType.OPCODE,
    "sub": TokenType.OPCODE,
    "and": TokenType.OPCODE,
    "or": TokenType.OPCODE,
    "xor": TokenType.OPCODE,

    "sll": TokenType.OPCODE,
    "slt": TokenType.OPCODE,
    "sltu": TokenType.OPCODE,
    "sra": TokenType.OPCODE,
    "srl": TokenType.OPCODE,

    "read_file": TokenType.OPCODE,
    "halt": TokenType.OPCODE,

    # I type
    "addi": TokenType.OPCODE,
    "subi": TokenType.OPCODE,
    "andi": TokenType.OPCODE,
    "ori": TokenType.OPCODE,
    "xori": TokenType.OPCODE,
    "slli": TokenType.OPCODE,
    "slti": TokenType.OPCODE,
    "sltui": TokenType.OPCODE,
    "srai": TokenType.OPCODE,
    "srli": TokenType.OPCODE,

    "jalr": TokenType.OPCODE,

    # B type
    "beq": TokenType.OPCODE,
    "bne": TokenType.OPCODE,
    "blt": TokenType.OPCODE,
    "bge": TokenType.OPCODE,
    "bltu": TokenType.OPCODE,
    "bgeu": TokenType.OPCODE,

    # S type
    "sb": TokenType.OPCODE,
    "sh": TokenType.OPCODE,
    "sw": TokenType.OPCODE,

    # load (I type)
    "lb": TokenType.OPCODE,
    "lh": TokenType.OPCODE,
    "lw": TokenType.OPCODE,
    "lbu": TokenType.OPCODE,
    "lhu": TokenType.OPCODE,

    # U/J type
    "lui": TokenType.OPCODE,
    "auipc": TokenType.OPCODE,
    "jal": TokenType.OPCODE,
}

class Token:
    def __init__(self, type, value, line, col):
        self.type = type
        self.value = value
        self.line = line
        self.col = col

class Lexer:
    def __init__(self, src: str):
        self.code = src
        self.i = 0
        self.line = 1
        self.col = 1
        self.tokens = []
    
    def emit(self, type_, value):
        self.tokens.append(Token(type_, value, self.line, self.col))

    def match_word(self, word):
        if word in OPCODES:
            self.emit(TokenType.OPCODE, word)
        elif word in REGISTERS:
            self.emit(TokenType.REG, word)
        elif word.isdigit():
            self.emit(TokenType.NUMBER, word)
        elif word.startswith("#"):
            self.emit(TokenType.NUMBER, word[1:])
        elif word.startswith(";"):
            self.emit(TokenType.COMMENT, word[1:])
        elif word.endswith(":"):
            self.emit(TokenType.LABEL_DEF, word[:-1])
        else:
            self.emit(TokenType.IDENT, word)
    
    def lexe(self):
        word = ""
        while self.i < len(self.code):
            c = self.code[self.i]
            if c == "\n":
                self.col = 1
                self.i += 1
                self.line += 1
            elif c in SYMBOLS:
                self.emit(SYMBOLS[c], c)
                self.i += 1
                self.col += 1
            else:
                word = self.read_word()
                self.match_word(word)
                self.col += len(word)
    
    def read_word(self):
        word = []
        while self.i < len(self.code) and self.code[self.i].isspace():
            self.i += 1
            self.col += 1
        while self.i < len(self.code) and not self.code[self.i].isspace()\
            and self.code[self.i] not in SYMBOLS:
            word.append(self.code[self.i])
            self.i += 1
        c = "".join(word)
        return c
    
    def print_token(self):
        for tok in self.tokens:
            print(f"at line: {tok.line}, col: {tok.col}"
                  f"\tvalue: '{tok.value}' of type: {tok.type}\n")