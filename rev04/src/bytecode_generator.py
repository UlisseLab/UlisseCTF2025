import sys
import os
import random

# random per rendere la generazione della chall deterministica
random.seed(0xdeadbeef1337)

INSTRUCTION_SIZE = 5

OPCODES = {
    "MOV":  0x0,
    "ADD":  0x1,
    "SUB":  0x2,
    "XOR":  0x3,
    "AND":  0x4,
    "OR":   0x5,
    "SHL":  0x6,
    "SHR":  0x7,
    "NOP":  0x8,
    "CALL": 0x9,
    "RET":  0xA,
    "CMP":  0xB,
    "JMP":  0xC,
    "JEZ":  0xD,
    "PUSH": 0xE,
    "POP":  0xF,
}

# 00 = immediate, 01 = registro, 10 = dereference
OPERAND_TYPES = {
    "imm": 0b00,
    "reg": 0b01,
    "mem": 0b10,
}

REGISTERS = {
    "IP": 0,
    "RA": 1,
    "RB": 2,
    "RC": 3,
    "RD": 4,
    "RT": 5
}

def determine_operand(operand: str):
    """
    trova il tipo e il valore dell'operando in base al primo carattere.
     - se inizia con un numero (o -numero): immediate.
     - se inizia con 'r': registro.
     - se inizia con '*': dereference.
    ritorna tipo, valore, dove tipo è una stringa tra "imm", "reg" o "mem".
    """
    if operand == None:
        return "imm", 0
    if operand[0].isdigit() or (operand[0] == '-' and operand[1].isdigit()):
        return "imm", int(operand)
    elif operand[0].isalpha():
        reg_name = operand.upper()
        return "reg", REGISTERS[reg_name]
    elif operand[0] == '*':
        # dereference: es. "*rb" -> usa il registro "rb"
        reg_name = operand[1:].upper()
        return "mem", REGISTERS[reg_name]
    else:
        raise ValueError(f"Formato operando non riconosciuto: {operand}")

def encode_instruction(mnemonic, operand1 = None, operand2 = None):
    """
    crea una singola istruzione in 5 byte.
    
    formato:
    byte 1: [opcode (4 bit) | op1_type (2 bit) | op2_type (2 bit)]
    byte 2,3: operando 1 (16 bit)
    byte 4,5: operando 2 (16 bit)
    """
    opcode = OPCODES.get(mnemonic.upper())
    
    op1_type, op1_val = determine_operand(operand1)
    op2_type, op2_val = determine_operand(operand2)
    
    # [opcode (4 bit) | op1_type (2 bit) | op2_type (2 bit)]
    first_byte = (opcode << 4) | ((OPERAND_TYPES[op1_type] & 0b11) << 2) | (OPERAND_TYPES[op2_type] & 0b11)
    
    op1_low_byte = op1_val & 0x00FF
    op1_high_byte = (op1_val & 0xFF00) >> 8
    op2_low_byte = op2_val & 0x00FF
    op2_high_byte = (op2_val & 0xFF00) >> 8

    return bytes([first_byte, op1_low_byte, op1_high_byte, op2_low_byte, op2_high_byte])

def generate_temp_bytecode(instructions):
    bytecode = bytearray()
    for instr in instructions:
        instr_bytes = encode_instruction(*instr)
        bytecode.extend(instr_bytes)
    
    return bytecode

def generate_bytecode(output_file, instructions):
    bytecode = bytearray()
    with open(f"{output_file}.asm", "w") as f:
        for instr in instructions:
            f.write(f"{instr[0]} {instr[1] if instr[1] != None else ''} {instr[2] if instr[2] != None else ''}\n")
            instr_bytes = encode_instruction(*instr)
            bytecode.extend(instr_bytes)
    
    print(f"ASM scritto in '{output_file}.asm'. opcodes size: {len(bytecode)} bytes")
    return bytecode

def instr(line, instructions):
    line = line.strip()
    if len(line) < 3: # probabile linea vuota
        return
    line = line.split()
    instructions.append((line[0], line[1] if len(line) > 1 else None, line[2] if len(line) > 2 else None))

class CodeChunk:
    def __init__(self, len):
        self.len = len
        self.position = None
    
    def set_position(self, position):
        self.position = position

class BlockChunk(CodeChunk):
    def __init__(self, len, flag_char, key_char, previous, next):
        super().__init__(len)
        self.previous = previous
        self.next = next
        self.flag_char = flag_char
        self.key_char = key_char
    
    def set_next(self, block):
        self.next = block

class DecryptChunk(CodeChunk):
    def __init__(self, len, code):
        super().__init__(len)
        self.code = code

class RecryptChunk(CodeChunk):
    def __init__(self, len, code):
        super().__init__(len)
        self.code = code

PREBLOCK_LEN = 6
BLOCK_LEN = 5
POSTBLOCK_LEN = 12
FULLBLOCK_LEN = PREBLOCK_LEN + BLOCK_LEN + POSTBLOCK_LEN + 1

DECRYPT_CLONES = 5
DECRYPT_VARIATIONS = [
    DecryptChunk(18, f"""
                        POP rb
                        POP rc
                        PUSH rd
                        XOR ra ra
                        PUSH ra
                        XOR *rb *rc
                        ADD rc 1
                        ADD rb 1
                        POP ra
                        ADD ra 1
                        PUSH ra
                        CMP ra {(FULLBLOCK_LEN - 1)*INSTRUCTION_SIZE}
                        MOV rd ip
                        SUB rd {7*INSTRUCTION_SIZE}
                        JEZ rd ra
                        POP ra
                        POP rd
                        RET
                     """
                ),
    DecryptChunk(21, f"""
                        POP rb
                        POP rc
                        PUSH rd
                        MOV ra 0
                        PUSH ra
                        PUSH rb
                        MOV rb rc
                        POP rc
                        XOR *rc *rb
                        ADD rb 1
                        POP ra
                        ADD ra 1
                        PUSH ra
                        ADD rc 1
                        CMP ra {(FULLBLOCK_LEN - 1)*INSTRUCTION_SIZE}
                        MOV rd ip
                        SUB rd {7*INSTRUCTION_SIZE}
                        JEZ rd ra
                        POP ra
                        POP rd
                        RET
                     """
                ),
]
FIRST_DECRYPT_CHUNK = DecryptChunk(17, f"""
                                        POP rb
                                        POP rc
                                        PUSH rd
                                        SUB ra ra
                                        PUSH ra
                                        MOV rd ip
                                        XOR *rb *rc
                                        POP ra
                                        ADD ra 1
                                        PUSH ra
                                        ADD rc 1
                                        ADD rb 1
                                        CMP ra {(FULLBLOCK_LEN - 1)*INSTRUCTION_SIZE}
                                        JEZ rd ra
                                        POP ra
                                        POP rd
                                        RET
                                       """
)

decrypt_layout = []
for i in range(DECRYPT_CLONES):
    decrypt_chunk = DECRYPT_VARIATIONS[i%len(DECRYPT_VARIATIONS)]
    decrypt_layout.append(DecryptChunk(decrypt_chunk.len, decrypt_chunk.code))

RECRYPT_CLONES = 5
RECRYPT_VARIATIONS = [
    RecryptChunk(35, f"""
                        POP rb
                        POP rc
                        PUSH rd
                        MOV ra 0
                        PUSH ra
                        XOR *rb *rc
                        ADD rc 1
                        ADD rb 1
                        POP ra
                        ADD ra 1
                        PUSH ra
                        CMP ra {(BLOCK_LEN+POSTBLOCK_LEN)*INSTRUCTION_SIZE}
                        MOV rd ip
                        SUB rd {7*INSTRUCTION_SIZE}
                        JEZ rd ra
                        POP ra
                        POP rd
                        POP rb
                        POP rc
                        PUSH rd
                        XOR ra ra
                        PUSH ra
                        XOR *rb *rc
                        ADD rc 1
                        ADD rb 1
                        POP ra
                        ADD ra 1
                        PUSH ra
                        CMP ra {(PREBLOCK_LEN)*INSTRUCTION_SIZE}
                        MOV rd ip
                        SUB rd {7*INSTRUCTION_SIZE}
                        JEZ rd ra
                        POP ra
                        POP rd
                        RET
                     """
                ),
    RecryptChunk(41, f"""
                        POP rb
                        POP rc
                        PUSH rd
                        XOR ra ra
                        PUSH ra
                        PUSH rb
                        MOV rb rc
                        POP rc
                        XOR *rc *rb
                        POP ra
                        ADD ra 1
                        PUSH ra
                        ADD rb 1
                        ADD rc 1
                        CMP ra {(BLOCK_LEN+POSTBLOCK_LEN)*INSTRUCTION_SIZE}
                        MOV rd ip
                        SUB rd {7*INSTRUCTION_SIZE}
                        JEZ rd ra
                        POP ra
                        POP rd
                        POP rc
                        POP rb
                        PUSH rd
                        SUB ra ra
                        PUSH ra
                        PUSH rb
                        MOV rb rc
                        POP rc
                        XOR *rb *rc
                        ADD rc 1
                        POP ra
                        ADD ra 1
                        ADD rb 1
                        PUSH ra
                        CMP ra {(PREBLOCK_LEN)*INSTRUCTION_SIZE}
                        MOV rd ip
                        SUB rd {7*INSTRUCTION_SIZE}
                        JEZ rd ra
                        POP ra
                        POP rd
                        RET
                     """
                ),
]
LAST_RECRYPT_CHUNK = RecryptChunk(18, f"""
                                        POP rb
                                        POP rc
                                        PUSH rd
                                        XOR ra ra
                                        PUSH ra
                                        XOR *rb *rc
                                        ADD rc 1
                                        ADD rb 1
                                        POP ra
                                        ADD ra 1
                                        PUSH ra
                                        CMP ra {(BLOCK_LEN+POSTBLOCK_LEN)*INSTRUCTION_SIZE}
                                        MOV rd ip
                                        SUB rd {7*INSTRUCTION_SIZE}
                                        JEZ rd ra
                                        POP ra
                                        POP rd
                                        RET
                                      """
)

recrypt_layout = []
for i in range(RECRYPT_CLONES):
    recrypt_chunk = RECRYPT_VARIATIONS[i%len(RECRYPT_VARIATIONS)]
    recrypt_layout.append(RecryptChunk(recrypt_chunk.len, recrypt_chunk.code))

instructions = []
with open("../flags.txt") as file:
    flag = file.readline()
key = "w@!t_r_u_r3@lLy_l0$1ng_t!m3_unV3!l1ng_th!s_e@$T3r_3gg?!?"

blocks_layout = []

for i in range(len(flag)):
    block = None

    flag_char = flag[i]
    key_char = key[i%len(key)]

    if(i == 0):
        block = BlockChunk(FULLBLOCK_LEN, flag_char, key_char, None, None)
    else:
        block = BlockChunk(FULLBLOCK_LEN, flag_char, key_char, blocks_layout[i-1], None)
        blocks_layout[i-1].set_next(block)
    
    blocks_layout.append(block)

FIRST_BLOCK = blocks_layout[0]
chunks_layout = blocks_layout + decrypt_layout + recrypt_layout + [FIRST_DECRYPT_CHUNK] + [LAST_RECRYPT_CHUNK]

random.shuffle(chunks_layout)

INIT_DECRYPT_CHUNK_LEN = 18 # 18 e' il numero di istruzioni di INIT_DECRYPT_CHUNK
FIRST_BLOCK_KEY_PADDING = FULLBLOCK_LEN-1

current_pos = len(instructions)*INSTRUCTION_SIZE + INIT_DECRYPT_CHUNK_LEN*INSTRUCTION_SIZE + FIRST_BLOCK_KEY_PADDING*INSTRUCTION_SIZE
for chunk in chunks_layout:
    chunk.set_position(current_pos)
    current_pos += chunk.len*INSTRUCTION_SIZE
FINAL_CHUNK_POS = current_pos

INIT_DECRYPT_CHUNK = f"""
                        MOV ra ip
                        ADD ra {INIT_DECRYPT_CHUNK_LEN*INSTRUCTION_SIZE}
                        MOV rb {FIRST_BLOCK.position}
                        MOV rc 0
                        PUSH rc
                        MOV rd ip
                        XOR *rb *ra
                        ADD ra 1
                        ADD rb 1
                        POP rc
                        ADD rc 1
                        PUSH rc
                        CMP rc {PREBLOCK_LEN*INSTRUCTION_SIZE}
                        JEZ rd rc
                        POP rc
                        MOV rd 1
                        MOV rb {FIRST_BLOCK.position}
                        JMP rb
                     """

for line in INIT_DECRYPT_CHUNK.splitlines(): instr(line, instructions)

INIT_DECRYPT_KEY_POS = len(instructions)*INSTRUCTION_SIZE
for line in range(FULLBLOCK_LEN-1): instr("NOP", instructions) # fill space for the first decrypt key

for chunk in chunks_layout:
    if isinstance(chunk, BlockChunk):
        var_RANDOM_DECRYPT_ADDR = decrypt_layout[random.randint(0, DECRYPT_CLONES-1)].position
        var_RANDOM_RECRYPT_ADDR = recrypt_layout[random.randint(0, RECRYPT_CLONES-1)].position

        var_KEYi = ord(chunk.key_char)
        var_CIPHERi = var_KEYi^ord(chunk.flag_char)

        if chunk.previous == None: # primo chunk
            var_ADDR_NEXT_PREBLOCK = chunk.next.position
            code = f"""
                    MOV rb ip
                    MOV ra rb
                    MOV ra {INIT_DECRYPT_CHUNK_LEN*INSTRUCTION_SIZE}
                    PUSH ra
                    PUSH rb
                    CALL {FIRST_DECRYPT_CHUNK.position}
                    MOV ra {var_KEYi}
                    POP rb
                    XOR ra rb
                    CMP ra {var_CIPHERi}
                    AND rd ra
                    MOV rb ip
                    SUB rb {11*INSTRUCTION_SIZE}
                    PUSH rb
                    MOV rb {var_ADDR_NEXT_PREBLOCK}
                    PUSH rb
                    MOV rb ip
                    SUB rb {10*INSTRUCTION_SIZE}
                    MOV ra rb
                    MOV ra {(INIT_DECRYPT_CHUNK_LEN+PREBLOCK_LEN)*INSTRUCTION_SIZE}
                    PUSH ra
                    PUSH rb
                    CALL {var_RANDOM_RECRYPT_ADDR}
                    JMP {var_ADDR_NEXT_PREBLOCK}
                    """
        elif chunk.next == None: # ultimo chunk
            var_ADDR_PREV_PREBLOCK = chunk.previous.position
            var_ADDR_PREV_BLOCK = chunk.previous.position + PREBLOCK_LEN*INSTRUCTION_SIZE
            code = f"""
                    MOV rb ip
                    MOV ra rb
                    MOV ra {var_ADDR_PREV_PREBLOCK}
                    PUSH ra
                    PUSH rb
                    CALL {var_RANDOM_DECRYPT_ADDR}
                    MOV ra {var_KEYi}
                    POP rb
                    XOR ra rb
                    CMP ra {var_CIPHERi}
                    AND rd ra
                    NOP
                    NOP
                    NOP
                    NOP
                    NOP
                    MOV rb ip
                    SUB rb {10*INSTRUCTION_SIZE}
                    MOV ra rb
                    MOV ra {var_ADDR_PREV_BLOCK}
                    PUSH ra
                    PUSH rb
                    CALL {LAST_RECRYPT_CHUNK.position}
                    JMP {FINAL_CHUNK_POS}
                    """
        else:
            var_ADDR_PREV_PREBLOCK = chunk.previous.position
            var_ADDR_NEXT_PREBLOCK = chunk.next.position
            var_ADDR_PREV_BLOCK = chunk.previous.position + PREBLOCK_LEN*INSTRUCTION_SIZE
            code = f"""
                    MOV rb ip
                    MOV ra rb
                    MOV ra {var_ADDR_PREV_PREBLOCK}
                    PUSH ra
                    PUSH rb
                    CALL {var_RANDOM_DECRYPT_ADDR}
                    MOV ra {var_KEYi}
                    POP rb
                    XOR ra rb
                    CMP ra {var_CIPHERi}
                    AND rd ra
                    MOV rb ip
                    SUB rb {11*INSTRUCTION_SIZE}
                    PUSH rb
                    MOV rb {var_ADDR_NEXT_PREBLOCK}
                    PUSH rb
                    MOV rb ip
                    SUB rb {10*INSTRUCTION_SIZE}
                    MOV ra rb
                    MOV ra {var_ADDR_PREV_BLOCK}
                    PUSH ra
                    PUSH rb
                    CALL {var_RANDOM_RECRYPT_ADDR}
                    JMP {var_ADDR_NEXT_PREBLOCK}
                    """
        for line in code.splitlines(): instr(line, instructions)
    else: # decrypt o recrypt 
        for line in chunk.code.splitlines(): instr(line, instructions)

# FINAL CHUNK
instr("MOV rt -1", instructions)
instr("RET", instructions)

OUTPUT_FILE = "delirivm_bytecode"

#print(instructions)
bytecode = generate_bytecode(OUTPUT_FILE, instructions)

# first block
target = bytecode[FIRST_BLOCK.position:FIRST_BLOCK.position+(FIRST_BLOCK.len-1)*INSTRUCTION_SIZE] # target = che cosa vogliamo che sia effettivamente (dopo essere decriptato)

# qui genero i bytes dei blocchi quando sono criptati. volendo si potrebbe fare in modo che invece che essere
# un easter egg, sia proprio dell'altro codice che sembra fare altro, per confondere ancora di piu' il player
temp_instructions = []
easter_egg_string = "never_gonna_giveyou__up_"
while len(easter_egg_string) < 92:
    easter_egg_string += ''.join(random.choice([str.upper, str.lower])(c) for c in "delirium")
for _ in range(23):
    i = _*4
    op1 = ((ord(easter_egg_string[(i+1)%len(easter_egg_string)]) & 0xFF) << 8) | ord(easter_egg_string[(i)%len(easter_egg_string)]) & 0xFF
    op2 = ((ord(easter_egg_string[(i+3)%len(easter_egg_string)]) & 0xFF) << 8) | ord(easter_egg_string[(i+2)%len(easter_egg_string)]) & 0xFF
    instr(f"SUB {op1} {op2}", temp_instructions) # SUB perche' nell'isa e' 00100000 ovvero \n in ascii. cosi' con strings e' leggibile >:)
source = generate_temp_bytecode(temp_instructions)   # source = che cosa vogliamo che sembri dal codice (ancora criptato)

# key = target ^ source
key = bytearray(x ^ y for x, y in zip(target, source))  # key = che cosa deve essere per rendere vero il resto

bytecode[FIRST_BLOCK.position:FIRST_BLOCK.position+(FIRST_BLOCK.len-1)*INSTRUCTION_SIZE] = source
bytecode[INIT_DECRYPT_KEY_POS:INIT_DECRYPT_KEY_POS+(FIRST_BLOCK.len-1)*INSTRUCTION_SIZE] = key

for i in range(1, len(blocks_layout)):
    prev_block = blocks_layout[i-1]
    block = blocks_layout[i]
    target = bytecode[block.position:block.position+(block.len-1)*INSTRUCTION_SIZE]
    key = bytecode[prev_block.position:prev_block.position+(prev_block.len-1)*INSTRUCTION_SIZE]

    source = bytearray(x^y for x, y in zip(target, key))
    bytecode[block.position:block.position+(block.len-1)*INSTRUCTION_SIZE] = source

with open(OUTPUT_FILE, "wb") as f:
    f.write(bytecode)
