#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define STACK_SIZE 1024       // max stack depth

// registers
#define REG_IP 0    // instruction pointer
#define REG_RA 1    // register A (RA)
#define REG_RB 2    // register B (RB)
#define REG_RC 3    // register C (RC)
#define REG_RD 4    // register D (RD)
#define REG_RT 5    // return address register (RT)

// opcodes
#define OP_MOV  0x0
#define OP_ADD  0x1
#define OP_SUB  0x2
#define OP_XOR  0x3
#define OP_AND  0x4
#define OP_OR   0x5
#define OP_SHL  0x6
#define OP_SHR  0x7
#define OP_NOP  0x8
#define OP_CALL 0x9
#define OP_RET  0xA
#define OP_CMP  0xB
#define OP_JMP  0xC
#define OP_JEZ  0xD
#define OP_PUSH 0xE
#define OP_POP  0xF

// optypes
#define OT_IMMEDIATE 0x0    // 00: immediate 16-bit constant
#define OT_REGISTER  0x1    // 01: register
#define OT_REG_DEREF 0x2    // 10: register dereference (use register value as memory address)

// vm things
uint8_t*code = NULL;     // buffer with bytecode
size_t code_size = 0;

uint16_t currentBytePointer = 0;
uint16_t registers[6] = {0};        // VM registers: IP, RA, RB, RC, RD, RT
uint16_t stack[STACK_SIZE];
int sp = -1;                        // stack pointer (-1 = empty)

uint8_t fetch_byte() {
    if (currentBytePointer >= code_size) {
        fprintf(stderr, "Error: IP (0x%04X) out of code bounds.\n", currentBytePointer);
        exit(1);
    }
    return code[currentBytePointer++];
}

uint16_t fetch_word() {
    if (currentBytePointer + 1 >= code_size) {
        fprintf(stderr, "Error: Not enough bytes to fetch a word.\n");
        exit(1);
    }
    uint16_t word = code[currentBytePointer] | (code[currentBytePointer + 1] << 8);
    currentBytePointer += 2;
    return word;
}

uint16_t get_operand_value(uint8_t operand_type, uint16_t operand_data) {
    switch(operand_type) {
        case OT_IMMEDIATE:
            return operand_data;
        case OT_REGISTER: {
            // use lower 8 bits as reg index.
            uint8_t reg_index = operand_data & 0xFF;
            return registers[reg_index];
        }
        case OT_REG_DEREF: {
            uint8_t reg_index = operand_data & 0xFF;
            uint16_t addr = registers[reg_index];
            if (addr >= code_size) {
                fprintf(stderr, "Error: Code memory access violation at address 0x%04X.\n", addr);
                exit(1);
            }
            return code[addr];
        }
        default:
            fprintf(stderr, "Error: Undefined operand type (%d).\n", operand_type);
            exit(1);
    }
}

void set_operand_value(uint8_t operand_type, uint16_t operand_data, uint16_t value) {
    switch(operand_type) {
        case OT_REGISTER: {
            uint8_t reg_index = operand_data & 0xFF;
            registers[reg_index] = value;
            break;
        }
        case OT_REG_DEREF: {
            uint8_t reg_index = operand_data & 0xFF;
            uint16_t addr = registers[reg_index];
            if (addr >= code_size) {
                fprintf(stderr, "Error: Memory access violation when writing to address 0x%04X.\n", addr);
                exit(1);
            }
            code[addr] = value & 0xFF;
            break;
        }
        default:
            fprintf(stderr, "Error: Cannot write to operand type (%d).\n", operand_type);
            exit(1);
    }
}

void push(uint16_t value) {
    if (sp >= STACK_SIZE - 1) {
        fprintf(stderr, "Error: Stack overflow.\n");
        exit(1);
    }
    stack[++sp] = value;
}

uint16_t pop() {
    if (sp < 0) {
        fprintf(stderr, "Error: Stack underflow.\n");
        exit(1);
    }
    return stack[sp--];
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <bytecode file>\n", argv[0]);
        return 1;
    }

    // Open and load the binary file containing the bytecode.
    FILE *fp = fopen(argv[1], "rb");
    if(!fp) {
        perror("Error opening bytecode file");
        return 1;
    }
    fseek(fp, 0, SEEK_END);
    code_size = ftell(fp);
    fseek(fp, 0, SEEK_SET);

    code = malloc(code_size);
    if(!code) {
        fprintf(stderr, "Error: Memory allocation failed.\n");
        return 1;
    }
    if(fread(code, 1, code_size, fp) != code_size) {
        fprintf(stderr, "Error: Could not read the bytecode file.\n");
        free(code);
        return 1;
    }
    fclose(fp);

    char flag[100];
    int flagLen;

    printf("Bytecode loaded successfully.\n");
    printf("Can you remember the flag? First, tell me how long do you think it was: ");
    scanf("%d", &flagLen);

    if(flagLen <= 0 || flagLen > 99) {
        printf("nope...\n");
        free(code);
        exit(0);
    }

    printf("Now, take a moment... think about the flag and let's see if you're delirious: ");
    scanf("%99s", flag);

    for(int i = 0; i < 100-flagLen; i++)
        push(0);
    for(int i = flagLen-1; i >= 0; i--)
        push(flag[i]);

    // Main execution loop.
    while (registers[REG_IP] < code_size) {
        currentBytePointer = registers[REG_IP];

        // each instruction is 5 bytes:
        // byte 0: [Opcode:4 | op1 type:2 | op2 type:2]
        // bytes 1-2: operand 1 (16 bits)
        // bytes 3-4: operand 2 (16 bits)
        uint8_t byte0 = fetch_byte();
        uint8_t opcode   = (byte0 >> 4) & 0xF;
        uint8_t op1_type = (byte0 >> 2) & 0x3;
        uint8_t op2_type = byte0 & 0x3;

        uint16_t op1 = fetch_word();
        uint16_t op2 = fetch_word();

        uint16_t val1, val2;

        switch (opcode) {
            case OP_MOV:
                val2 = get_operand_value(op2_type, op2);
                set_operand_value(op1_type, op1, val2);
                break;
            case OP_ADD:
                val1 = get_operand_value(op1_type, op1);
                val2 = get_operand_value(op2_type, op2);
                set_operand_value(op1_type, op1, val1 + val2);
                break;
            case OP_SUB:
                val1 = get_operand_value(op1_type, op1);
                val2 = get_operand_value(op2_type, op2);
                set_operand_value(op1_type, op1, val1 - val2);
                break;
            case OP_XOR:
                val1 = get_operand_value(op1_type, op1);
                val2 = get_operand_value(op2_type, op2);
                set_operand_value(op1_type, op1, val1 ^ val2);
                break;
            case OP_AND:
                val1 = get_operand_value(op1_type, op1);
                val2 = get_operand_value(op2_type, op2);
                set_operand_value(op1_type, op1, val1 & val2);
                break;
            case OP_OR:
                val1 = get_operand_value(op1_type, op1);
                val2 = get_operand_value(op2_type, op2);
                set_operand_value(op1_type, op1, val1 | val2);
                break;
            case OP_SHL:
                val1 = get_operand_value(op1_type, op1);
                val2 = get_operand_value(op2_type, op2);
                set_operand_value(op1_type, op1, val1 << val2);
                break;
            case OP_SHR:
                val1 = get_operand_value(op1_type, op1);
                val2 = get_operand_value(op2_type, op2);
                set_operand_value(op1_type, op1, val1 >> val2);
                break;
            case OP_NOP:
                break;
            case OP_CALL:
                registers[REG_RT] = currentBytePointer;
                val1 = get_operand_value(op1_type, op1);
                currentBytePointer = val1;
                break;
            case OP_RET:
                currentBytePointer = registers[REG_RT];
                break;
            case OP_CMP:
                val1 = get_operand_value(op1_type, op1);
                val2 = get_operand_value(op2_type, op2);
                set_operand_value(op1_type, op1, (val1 == val2) ? 1 : 0);
                break;
            case OP_JMP:
                val1 = get_operand_value(op1_type, op1);
                currentBytePointer = val1;
                break;
            case OP_JEZ:
                val2 = get_operand_value(op1_type, op2);
                if (val2 == 0) {
                    val1 = get_operand_value(op2_type, op1);
                    currentBytePointer = val1;
                }
                break;
            case OP_PUSH:
                val1 = get_operand_value(op1_type, op1);
                push(val1);
                break;
            case OP_POP:
                val1 = pop();
                set_operand_value(op1_type, op1, val1);
                break;
            default:
                fprintf(stderr, "Error: Unknown opcode 0x%X found at 0x%04X.\n", opcode, registers[REG_IP]);
                exit(EXIT_FAILURE);
        }

        registers[REG_IP] = currentBytePointer;
        
    }

    bool rightFlag = registers[REG_RD];
    if(rightFlag) {
        printf("FLAG ACCEPTED!!!!!\n");
    } else {
        printf("Close! well, not really. DELIRIUM.\n");
    }

    free(code);
    return 0;

}
