from libdebug import debugger

vm_path = './delirivm'
bytecode_path = './delirivm_bytecode'

# You can find these values using a decompiler and revving the VM
INSTRUCTION_SIZE_BYTES = 5
XOR_CASE_ADDR = 0x555555555b6b
IP_REGISTER_ADDR = 0x555555559058

# Launch the process with libdebug
d = debugger(argv=[vm_path, bytecode_path], aslr=False) # ASLR disabled to set breakpoints easier
p = d.run()

d.breakpoint(XOR_CASE_ADDR)

# At the flag prompt, send a placeholder flag (random length, we are going to extract it anyway c: )
flag_len = 20
p.sendline(str(flag_len).encode())
p.sendline(b"A" * flag_len)

d.cont()

recovered_flag = ""

def read_int(memory, len=1):
    return int.from_bytes(d.memory[memory, len], "little")

BYTECODE_BASE_ADDDR = read_int(0x555555559040, len=8)  # 0x5040 is the address of the bytecode loaded in the VM memory

def read_vm_operand(addr):
    return (read_int(addr, len=1) | (read_int(addr+1, len=1) << 8))

def extract_flag_char():
    current_instruction_addr = BYTECODE_BASE_ADDDR+read_int(IP_REGISTER_ADDR, len=2)

    # From the bytecode, a XOR block has always a "MOV ra, {KEYi}" which is 2 instruction above the detected XOR
    set_key_instruction_addr = current_instruction_addr-(2*INSTRUCTION_SIZE_BYTES)
    key_byte_addr = set_key_instruction_addr + 3    # instruction: [opcode: 1, first_operand: 2, second_operand: 2]
    key = read_vm_operand(key_byte_addr)
    
    # From the bytecode, there's always a "CMP ra, {CIPHERi}" which is the next instruction after the detected XOR
    cmp_instruction_addr = current_instruction_addr + (1*INSTRUCTION_SIZE_BYTES)
    cipher_byte_addr = cmp_instruction_addr + 3     # instruction: [opcode: 1, first_operand: 2, second_operand: 2]
    cipher = read_vm_operand(cipher_byte_addr)

    return cipher ^ key

# While on every breakpoint, which is set to any XOR operation
while True:
    flag_char = extract_flag_char()
    if(flag_char > 20 and flag_char < 128): # only allow printable chars
        recovered_flag += chr(flag_char)

        print(recovered_flag)

        if chr(flag_char) == '}':
            break
    
    d.cont() # equivalent of "continue" of gdb

print(recovered_flag)