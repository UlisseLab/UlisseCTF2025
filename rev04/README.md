# DELIRIVM

|         |                                |
| ------- | ------------------------------ |
| Authors | Cristian Di Nicola <@crih.exe> |
| Points  | 500                            |
| Tags    | rev                            |

## Challenge Description

I came across this strange bytecode that runs on a custom VM, but I can't wrap my head around how it even executes...

It's filled with variations of the word **"delirium"**.

Is this some kind of twisted joke, or am I the one losing my mind?

I swear, I'm not delirious!! 💀

## a useful TL;DR made by ChatGPT

The **delirivm** challenge provides a custom VM (`delirivm`) and encrypted bytecode (`delirivm_bytecode`). The VM executes bytecode which dynamically decrypts and re-encrypts code segments (**FullBlocks**) during execution, performing XOR-based checks to verify each flag character.

- **Bytecode structure**:

  - Each **FullBlock** contains:
    - A `pre_block` (decrypts the next block),
    - A `block` (checks one flag character with XOR),
    - A `post_block` (re-encrypts and prepares subsequent code).

- **Instruction encoding**:

  - Each VM instruction is **5 bytes**: `[Opcode(4bits) | Operand1_type(2bits) | Operand2_type(2bits)] + [Operand1 (2 bytes)] + [Operand2 (2 bytes)]`.
  - Operand types: immediate (`0x0`), register (`0x1`), register dereference (`0x2`).

- **Reversing strategy**:

  - Statically analyzing the VM reveals 16 opcodes (e.g., MOV, XOR, CMP, etc.).
  - The bytecode initially contains readable XOR-decryption logic, revealing offsets and keys used to decrypt code sections.
  - Dynamically decrypting the first **FullBlock** with GDB confirms XOR instructions checking the flag character.
  - Place breakpoints on XOR operations in flag checks to automate extraction of XOR keys and constants with dynamic debugging (`libdebug`) or manually (`gdb`).

The key to solving this challenge is dynamically setting breakpoints on XOR instructions, extracting keys, and XORing them with the compared constants to reconstruct the flag.

**Scroll down to the end for the script!**

---

## Introduction

In this challenge, titled **delirivm**, we are provided with two files:

- `delirivm`: A custom-made virtual machine (VM) executable
- `delirivm_bytecode`: A binary file containing raw bytecode intended to be executed by the VM.

To execute the challenge, we run the VM with the bytecode file as an argument:

```bash
./delirivm delirivm_bytecode
```

Upon running, the VM prompts us to input the flag. After entering our guess, it processes the flag and eventually informs us whether our input is correct or incorrect.

### Initial Observations

Initially examining the provided binary files:

- `delirivm`: Even though the executable is stripped, basic reverse-engineering reveals a clear control flow pattern. Specifically, after the flag input, we notice:

  - Two unusual `for` loops whose immediate purposes aren't yet clear. (its actually pushing the input to the vm stack)
  - A prominent `while` loop containing a large `switch-case` statement, strongly suggesting this is the main execution loop handling the VM opcodes.
  - Counting the `case` labels within this `switch-case` structure, we identify exactly **16 distinct opcodes**. Each of the other cases calls some functions.

- `delirivm_bytecode`: On initial inspection, the bytecode file appears quite strange. Running the `strings` command on it results in numerous repetitions of the string variations of `"DeLiRiUm"` (in mixed casing), alongside fragments of the phrase `"never gonna give you up"` (lol). However, many of these text segments contain corrupted or unreadable characters interspersed among them.

Using `xxd`, we observe:

- Clearly distinguishable sections containing readable ASCII strings mixed with nonsensical or corrupted data.
- Sections with seemingly random bytes interspersed between these ASCII strings.

```auto
00000000: 0501 0000 0014 0100 5a00 0402 00d3 1804  ........Z.......
00000010: 0300 0000 e403 0000 0005 0400 0000 3a02  ..............:.
00000020: 0001 0014 0100 0100 1402 0001 00f4 0300  ................
00000030: 0000 1403 0001 00e4 0300 0000 b403 001e  ................
00000040: 00d5 0400 0300 f403 0000 0004 0400 0100  ................
00000050: 0402 00d3 18c4 0200 0000 256c 6576 6525  ..........%leve%
00000060: 735f 656f 246f 6e3b 5fc4 6669 7665 c47b  s_eo$on;_.five.{
00000070: 6f75 5fb0 0665 705f 2465 453b 69d4 5069  ou_..ep_$eE;i.Pi
00000080: 554d 1545 454e 6994 5369 774d 6560 656d  UM.EENi.SiwMe`em
00000090: 6925 7069 554d 0466 455b 49c4 5049 754d  i%piUM.fE[I.PIuM
000000a0: 2466 6537 7fc4 7049 756d 2546 456c 4904  $fe7..pIum%FElI.
000000b0: 5069 676d 2565 454e 6924 5349 2d4d c445  Pigm%eENi$SI-M.E
000000c0: 456c 49c4 7069 556d b01a 4c4c 4920 6e65  ElI.piUm..LLI ne
000000d0: 7665 2072 5f67 6f20 6e6e 3052 2067 6976  ve r_go nn0R giv
000000e0: 6520 796f 755f 20a8 6870 5f20 6445 6d69  e you_ .hp_ dEmi
000000f0: 2052 6955 4d20 4445 4c69 2052 6942 4d20   RiUM DELi RiBM
00000100: 6465 6c69 2072 6955 4d20 6445 6c49 2052  deli riUM dElI R
00000110: 4975 4d20 6465 b179 2072 4975 6d20 4445  IuM de.y rIum DE
00000120: 6c49 2052 6955 6d20 6445 4c69 2052 496c  lI RiUm dELi RIl
00000130: 4c20 4445 6c49 2072 6955 6d20 c040 4c49  L DElI riUm .@LI
00000140: c0c9 1300 0025 6c65 7665 2573 5f65 6f24  .....%leve%s_eo$
00000150: 6f6e ff57 c466 6976 65c4 7b6f 755f b0c8  on.W.five.{ou_..
00000160: 7b70 5f24 6545 5969 d450 6955 4d15 4545  {p_$eEYi.PiUM.EE
00000170: 4e69 9453 6936 4d65 6065 6d69 2570 6955  Ni.Si6Me`emi%piU
00000180: 4d04 6645 5b49 c450 4975 4d24 6665 9168  M.fE[I.PIuM$fe.h
00000190: c470 4975 6d25 4645 6c49 0450 6967 6d25  .pIum%FElI.Pigm%
000001a0: 6545 4e69 2453 4969 45c4 4545 6c49 c470  eENi$SIiE.EElI.p
000001b0: 6955 6db0 6949 4c49 c0ae 0600 0025 6c65  iUm.iILI.....%le
000001c0: 7665 2573 5f65 6f24 6f6e 2b48 c466 6976  ve%s_eo$on+H.fiv
000001d0: 65c4 7b6f 755f b03f 6670 5f24 6545 3369  e.{ou_.?fp_$eE3i
000001e0: d450 6955 4d15 4545 4e69 9453 6907 4d65  .PiUM.EENi.Si.Me
000001f0: 6065 6d69 2570 6955 4d04 6645 5b49 c450  `emi%piUM.fE[I.P
00000200: 4975 4d24 6665 ba64 c470 4975 6d25 4645  IuM$fe.d.pIum%FE
00000210: 6c49 0450 6967 6d25 6545 4e69 2453 496d  lI.Pigm%eENi$SIm
00000220: 56c4 4545 6c49 c470 6955 6db0 0641 4c49  V.EElI.piUm..ALI
00000230: c0a9 1500 00f4 0200 0000 f403 0000 00e4  ................
00000240: 0400 0000 0401 0000 00e4 0100 0000 3a02  ..............:.
00000250: 0003 0014 0300 0100 1402 0001 00f4 0100  ................
00000260: 0000 1401 0001 00e4 0100 0000 b401 0055  ...............U
00000270: 0005 0400 0000 2404 0023 00d5 0400 0100  ......$..#......
00000280: f401 0000 00f4 0400 0000 f402 0000 00f4  ................
00000290: 0300 0000 e404 0000 0035 0100 0100 e401  .........5......
000002a0: 0000 003a 0200 0300 1403 0001 0014 0200  ...:............
000002b0: 0100 f401 0000 0014 0100 0100 e401 0000  ................
000002c0: 00b4 0100 1e00 0504 0000 0024 0400 2300  ...........$..#.
000002d0: d504 0001 00f4 0100 0000 f404 0000 00a0  ................
000002e0: 0000 0000 206e 6576 6520 725f 676f 206e  .... neve r_go n
000002f0: 6e9d 5d20 6769 7665 2079 6f75 5f20 1d61  n.] give you_ .a
00000300: 705f 2064 4501 6920 5269 554d 2044 454c  p_ dE.i RiUM DEL
```

These initial clues are quite misleading; a first guess might be that the VM parses opcodes from the ASCII sequences or their casing. However, as we'll see later in this analysis, this initial guess doesn't lead us to the solution.

---

## Understanding the VM Instruction Encoding

To write a script that translates bytecode into readable pseudo-assembly, we must first deeply understand the instruction encoding utilized by the virtual machine. Even though the original source code was not provided to players, it's entirely possible to reconstruct its logic and instruction format through careful static analysis of the VM binary itself.

### Reverse Engineering the VM Fetch Loop

By analyzing the main execution loop of the VM, players would notice a structure similar to the following (simplified with named variables) pseudocode derived from decompilation:

```c
while (registers[REG_IP] < code_size) {
    currentBytePointer = registers[REG_IP];

    uint8_t byte0 = fetch_byte();
    uint8_t opcode   = (byte0 >> 4) & 0xF;
    uint8_t op1_type = (byte0 >> 2) & 0x3;
    uint8_t op2_type = byte0 & 0x3;

    uint16_t op1 = fetch_op();
    uint16_t op2 = fetch_op();

    // ...
}
```

From this snippet, it becomes clear how each instruction is structured:

- Each instruction is exactly **5 bytes** long:
  - **Byte 0**: `[Opcode (4 bits) | Operand 1 type (2 bits) | Operand 2 type (2 bits)]`
  - **Bytes 1-2**: Operand 1 (16 bits)
  - **Bytes 3-4**: Operand 2 (16 bits)

### Decoding Opcode Operations

Analyzing the VM's opcode `switch-case` statements through a decompiler reveals operations like addition, subtraction, XOR, and jumps. Each case invokes a function like `sub_152a`, likely responsible for storing results, and `sub_1429`, responsible for fetching operand values.

For instance, here's a snippet of the decompiled (BinaryNinja) VM `switch-case` structure:

```c
switch (opcode) {
    case 0:
        sub_152a(dest, type_dest, sub_1429(op1, type_op1));
        break;
    case 1:
        sub_152a(dest, type_dest, sub_1429(op1, type_op1) + sub_1429(op2, type_op2));
        break;
    case 2:
        sub_152a(dest, type_dest, sub_1429(op1, type_op1) - sub_1429(op2, type_op2));
        break;
    case 3:
        sub_152a(dest, type_dest, sub_1429(op1, type_op1) ^ sub_1429(op2, type_op2));
        break;
    // other cases...
}
```

This strongly suggests that:

- `sub_152a` stores the result into the destination operand.
- `sub_1429` fetches values from operands, handling immediate values, registers, or memory references.

### Decoding Operand Types

By examining how operands are fetched and used, we can infer the meaning of operand types (`op1_type`, `op2_type`):

- `0x0` (**00**): Immediate.
- `0x1` (**01**): Register.
- `0x2` (**10**): Register dereference (the register's value is used as a memory address).
- `0x3` (**11**): Undefined/unused.

Notably, the `0x2` operand type allows for modifying the VM memory dynamically during execution.

### The VM Instruction Set Architecture (ISA)

After carefully reverse-engineering, we can summarize the VM's custom ISA clearly in the following table:

| Opcode   | Instruction | Description                                                                                            |
| -------- | ----------- | ------------------------------------------------------------------------------------------------------ |
| **0000** | **MOV**     | Moves a value from one operand to another (typically from immediate to register or between registers). |
| **0001** | **ADD**     | Adds two operands.                                                                                     |
| **0010** | **SUB**     | Subtracts the second operand from the first.                                                           |
| **0011** | **XOR**     | Performs bitwise XOR between two operands.                                                             |
| **0100** | **AND**     | Performs bitwise AND between two operands.                                                             |
| **0101** | **OR**      | Performs bitwise OR between two operands.                                                              |
| **0110** | **SHL**     | Shifts bits of the first operand to the left by the second operand's amount.                           |
| **0111** | **SHR**     | Shifts bits of the first operand to the right by the second operand's amount.                          |
| **1000** | **NOP**     | No operation (used for alignment or flow control).                                                     |
| **1001** | **CALL**    | Calls a function, saving the return address in the `RT` register.                                      |
| **1010** | **RET**     | Returns from a function using the address in `RT`.                                                     |
| **1011** | **CMP**     | Compares two operands; sets first operand to 1 if equal, otherwise 0.                                  |
| **1100** | **JMP**     | Unconditional jump to a specified address.                                                             |
| **1101** | **JEZ**     | Jumps if the specified register value is zero.                                                         |
| **1110** | **PUSH**    | Pushes a value onto the stack.                                                                         |
| **1111** | **POP**     | Pops a value from the stack into a register.                                                           |

### Writing a Python Script to Decode Bytecode

With this detailed information, players can now write a Python script that reads each 5-byte instruction, decodes the opcode and operand types, and translates each instruction into readable pseudo-assembly, greatly simplifying further analysis.

By following this strategy, you will clearly understand the encrypted bytecode once decrypted, significantly easing the reverse-engineering process.

## Deep Dive: How the Challenge Actually Works

### The Bytecode Decryption Mechanism

The core of the **delirivm** challenge involves an elaborate self-decrypting bytecode structure that verifies the flag character by character using XOR operations. The actual bytecode snippet used to verify each character is quite simple and looks something like this in pseudo-assembly:

```assembly
MOV ra, {var_KEYi}
POP rb               ; User input is pushed automatically onto the stack at start
XOR ra, rb
CMP ra, {var_KEYi ^ ord(chunk.flag_char)}
AND rd, ra           ; rd is initially set to 1, final correctness depends on it
```

However, the complexity arises from the way this bytecode is structured, encrypted, and dynamically decrypted.

### The Structure: "FullBlock"

To make things harder, I made each flag character check packaged into a specialized structure we'll call a **FullBlock**, composed of:

- **pre_block**: Pushes addresses onto the stack (parameters) and calls a special subroutine named `Decrypt`.
- **block**: Contains the actual flag-checking bytecode snippet.
- **post_block**: Pushes addresses (parameters) and calls another subroutine named `Recrypt`.
- **JMP next_fullblock**: Redirects execution to the next FullBlock, ensuring the control flow is shuffled to increase complexity.

---

### Deeper Analysis: Extracting Crucial Information from the First Instructions

Critically, upon static analysis, we discover something important:

Initially, **all** `fullblocks`, including the very first one, are encrypted. At first glance, we cannot directly read any `fullblock`. **But only the initial segment of the bytecode is decrypted and thus readable at the very start.**

Let's carefully examine the initial readable bytecode instructions again, step by step:

```assembly
MOV ra ip
ADD ra 90
MOV rb 6355
MOV rc 0
PUSH rc
MOV rd ip
XOR *rb *ra
ADD ra 1
ADD rb 1
POP rc
ADD rc 1
PUSH rc
CMP rc 30
JEZ rd rc
POP rc
MOV rd 1
MOV rb 6355
JMP rb
; After this point, code is no longer readable
```

From this code snippet, we can extract critical information for our analysis:

- **Register initialization**:

  - `MOV ra, ip` and `ADD ra, 90`:\
    `ra` is set to the current instruction pointer (`ip`) plus 90. Since this code segment starts at offset `0`, `ra` initially points to offset **90**, which is right after these instructions, indicating the location of the decryption key.
  - `MOV rb, 6355`:\
    `rb` is set to offset **6355**, representing the start address of the first encrypted `FULLBLOCK`. Thus, we now know exactly where the first encrypted `pre_block` resides.

- **XOR operation**:

  - `XOR *rb, *ra`: This instruction XORs the byte at the address pointed by `ra` (the key at offset 90) with the byte at the address pointed by `rb` (the encrypted first `pre_block` at offset 6355), writing the result back to address `rb`. Effectively, this decrypts one byte of the first `pre_block`.

- **Loop behavior**:

  - The register `rc` is incremented (`ADD rc, 1`) and then compared to `30` (`CMP rc, 30` followed by `JEZ`).\
    This strongly indicates that the decryption loop runs exactly **30 times**, meaning the size of the encrypted first `pre_block` is **30 bytes**.

To summarize, just from analyzing these initial instructions we found out that:

- The first encrypted `FULLBLOCK` is at offset **6355**.
- The XOR key used for decrypting the first `pre_block` is at offset **90**, right after these initial instructions.
- The size of the encrypted segment (`pre_block`) is exactly **30 bytes**.

This is immensely useful because now, knowing the exact addresses and sizes, we can precisely locate, decrypt, and analyze the first `fullblock`, enabling further reverse engineering steps.

These instructions are actually performing the initial decryption of the very first `pre_block`:

The VM computes an XOR operation between bytes stored just after these instructions (the initial decryption key) and the encrypted first `pre_block`.
After this procedure, the first `pre_block` becomes executable.

Only after this decryption step the first `pre_block` can run, decrypting the corresponding `block` and `post_block` for verifying the first character of the input flag.

### How the Dynamic Encryption/Decryption Works

Within the seemingly random bytes identified earlier, two special functions are embedded: `Decrypt` and `Recrypt`.

Analyzing the bytecode further using a custom script to translate the visible bytecode into pseudo-assembly (ignoring encrypted segments), we observe that the implementations of these two functions are actually **not encrypted** and thus clearly readable in the disassembled output.

Here's how these functions operate:

- `Decrypt(target_addr, xor_key_addr)`\
  XORs bytes at the specified addresses (`target_addr` and `xor_key_addr`) and overwrites the target address with decrypted code.

- `Recrypt(addr_this_block, addr_prev_block, addr_next_preblock, addr_this_preblock)`:\
  Performs three crucial operations:

  1. **Re-encrypts** the just-executed `block` using the previously encrypted `block`.
  2. **Re-encrypts** the just-executed `pre_block`.
  3. **Decrypts** the next `pre_block` (for the following character), based on the current encrypted state.

To further increase complexity and hinder reverse engineering, the bytecode intentionally includes:

- **Multiple clones** of each of these functions scattered randomly throughout the bytecode. Each block randomly chooses one clone from these multiple instances to call at runtime, greatly complicating static analysis.
- **Two primary variations** of the `Decrypt` and `Recrypt` functions exist, adding an additional layer of complexity when tracing execution flow.
- Additionally, there is a special **third variation** that appears precisely once for each function:
  - The first invocation of the `Decrypt` function (used for the initial `pre_block`) has a unique implementation with slightly different behavior.
  - Similarly, the final call to the `Recrypt` function, used at the end of the bytecode execution, has distinct logic.

As a result, each block unpredictably references one of these multiple function clones, introducing further complexity into static and dynamic analysis. The presence of these variations demands careful and methodical reverse engineering to accurately follow and reconstruct the original logic. It's there to slow you down! :)

This chained XOR approach ensures that only a minimal amount of code remains readable at any given moment. Also, each step's decryption directly depends on the previously encrypted states, thus you can't patch it!

The encrypted blocks are carefully crafted so that, when XOR-encrypted, they produce distinctive ASCII strings like `"DeLiRiUm"` and `"never gonna give you up"`, contributing further confusion during static analysis.

---

## Dynamic Reverse Engineering: Decrypting and Analyzing the First FullBlock

With the extensive knowledge gained earlier, we now know exactly where to find the first encrypted **FullBlock** within the bytecode—at offset **6355 (0x18D3)**. Let's dynamically decrypt and analyze this block using `gdb` to confirm our understanding and validate our approach.

### Step 1: Locating the Loaded Bytecode

We first start by running the VM with `gdb`:

```bash
gdb -q delirivm
(gdb) r delirivm_bytecode
```

Within the VM, we identify where the bytecode has been loaded in memory using the address of the global variable obtained by decompiling: `0x5040`

```bash
(gdb) x/2x 0x555555559040
0x555555559040: 0x5555b490      0x00005555
```

Thus, the loaded bytecode base address is `0x8490`.

### Step 2: Inspecting the Encrypted First FullBlock

Adding the offset of `6355 (0x18D3)` to the base address, we inspect the encrypted state of the first `FullBlock`:

```bash
(gdb) x/16x 0x55555555b490+6355
0x55555555cd63: 0x76656e20      0x5f722065      0x6e206f67      0x205f616e
0x55555555cd73: 0x65766967      0x756f7920      0x755f205f      0x64205f70
```

Clearly, at this moment, the block is encrypted (ASCII resembles something like `"never gonna give you up DeLiRiUm..."`).

### Step 3: Dynamically Decrypting the `pre_block`

We set a breakpoint at the switch case of the first unconditional jump (`JMP`) instruction (located at the end of the initial visible bytecode) to pause execution just after decrypting the first `pre_block`:

```bash
(gdb) b*0x555555555e42
(gdb) c
```

Now, inspecting the memory at the same location again:

```bash
(gdb) x/16x 0x55555555b490+6355
0x55555555cd63: 0x00000205      0x00010500      0x01040002      0xe4005a00
0x55555555cd73: 0x00000001      0x000002e4      0x10599000      0x64200000
```

The first `pre_block` has been successfully decrypted!

### Step 4: Disassembling the Decrypted `pre_block`

Converting these decrypted bytes into readable pseudo-assembly (using the earlier reverse-engineered encoding):

```assembly
MOV rb ip
MOV ra rb
MOV ra 90
PUSH ra
PUSH rb
CALL 4185
```

This code clearly sets up registers `ra` (set to `90`, the position of the key) and `rb` (current instruction pointer, so that it points to the first instruction of the fullblock!), then calls a subroutine (`CALL 4185`) that decrypts the subsequent `block`.

### Step 5: Understanding the Decryption Routine at `CALL 4185`

Analyzing the subroutine at address `4185` (also clearly visible in unencrypted bytecode):

```assembly
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
CMP ra 115
JEZ rd ra
POP ra
POP rd
RET
```

This routine XORs two memory areas pointed by registers `rb` and `rc` (previously set up), effectively decrypting the next section (`block` and `post_block`). The loop runs exactly **115 times**, implying the block+post_block is 115 bytes in length.

### Step 6: Decrypting and Analyzing the `block` and `post_block`

We remove the previous breakpoint and set a new one at the `RET` of the above routine to inspect memory just after decrypting the `block`:

```bash
(gdb) del
(gdb) b*0x555555555dc3
(gdb) c
(gdb) x/32x 0x55555555b490+6355
```

Now we see:

```bash
0x55555555cd63: 0x76656e20      0x5f722065      0x6e206f67      0x205f616e
0x55555555cd73: 0x65766967      0x756f7920      0x755f205f      0x01045f70
0x55555555cd83: 0xf4007700      0x00000002      0x02000135      0x0001b400
0x55555555cd93: 0x04450022      0x05000100      0x00000002      0x37000224
0x55555555cda3: 0x0002e400      0x02040000      0xe4167b00      0x00000002
0x55555555cdb3: 0x00000205      0x00022400      0x01050032      0x04000200
0x55555555cdc3: 0x00780001      0x000001e4      0x0002e400      0x7e900000
0x55555555cdd3: 0xc0000009      0x0000167b      0x76656e20      0x5f722065
```

Notably, the decrypted `block` is now visible and can be disassembled to readable instructions:

```assembly
MOV ra 119
POP rb
XOR ra rb
CMP ra 34
AND rd ra
MOV rb ip
SUB rb 55
PUSH rb
MOV rb 5755
PUSH rb
MOV rb ip
SUB rb 50
MOV ra rb
MOV ra 120
PUSH ra
PUSH rb
CALL 2430
JMP 5755
```

### Step 7: Identifying the Flag-Checking Logic

Inspecting closely, we observe the critical XOR and CMP instructions:

```assembly
MOV ra 119
POP rb
XOR ra rb
CMP ra 34
AND rd ra
```

Here, `rb` is presumably loaded with a character of the user's input flag, as you can tell by looking at the first two for loop just after the scanf in the VM. The byte `119` is XORed with the input character and compared to `34`.

Calculating this manually: `119 ^ 34 = 85`, which corresponds to `'U'` in ASCII. This perfectly matches the known first character of the flag `"UlisseCTF{"`.

### Step 8: Exploitation Strategy

We now have the definitive strategy for solving the challenge programmatically:

- We can use a debugger (e.g., `libdebug`) to dynamically set breakpoints precisely at these XOR instructions.
- At each breakpoint, we can extract the XOR key from the immediate set to the register, and the expected XOR result from the subsequent CMP instruction.
- XORing these two values together will directly reveal each character of the flag, character by character.

With this method, we bypass the complexity of the VM's encryption entirely, extracting the flag effectively and cleanly.

---

## Automating the Solution: Extracting the Flag with Python

After all our deep reverse-engineering, we have a solid understanding of how the bytecode encryption works, how the VM operates, and most importantly, how the flag is verified. It's now time to put all this knowledge into a Python script that automatically extracts the flag character by character.

By setting breakpoints at every XOR instruction executed by the VM, the script dynamically intercepts execution to extract both the XOR key and the expected result from the subsequent instructions. XOR-ing these two values instantly reveals the corresponding flag character (or an ignored non-printable char). Repeating this for each XOR allows the script to reconstruct the entire flag automatically.

Here's how I implemented this:

```python
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
```

### Verifying the Flag

Let's now use our freshly recovered flag to verify the solution directly with the VM binary:

```text
$ ./delirivm delirivm_bytecode
Bytecode loaded successfully.
Can you remember the flag? First, tell me how long do you think it was: 40
Now, take a moment... think about the flag and let's see if you're delirious:
UlisseCTF{d1d_y0u_r34lly_und3rst4nd_1t?}

FLAG ACCEPTED!!!!!
```

### The End

Congratulations! If you've followed along and reached this point, you're actually delirious lol. just kidding, you're just exceptionally good at revving!

_p.s. take a look to the writeup folder for the script and the bytecode in a txt readable form! And if you're curious, go read the super messy but diabolic bytecode_generator.py script from the sources >:)_
