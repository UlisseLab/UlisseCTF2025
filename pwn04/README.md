# x864Oracle

|         |                            |
| ------- | -------------------------- |
| Authors | Alan Davide Bovo <@AlBovo> |
| Points  | 500                        |
| Tags    | pwn                        |

## Challenge Description

I've just graduated from pwn.college🎉 and decided to create my first pwn Oracle—it's soooo safe, I bet you can't break it🧨.

- _Note 1: execution of this program may require sufficient privileges, such as root access, to run certain functions._
- _Note 2: the flag is located @ `/home/user/flag`_

---

This is a remote challenge, you can connect with:

`nc x864oracle.challs.ulisse.ovh 5353`

## Overview

This challenge provided a dynamically linked ELF binary along with its `libc.so.6` and linker. Upon connecting to the remote service, the binary prompts the user to input the length of their name, followed by the name itself. The input is echoed back after each step, including a final prompt asking the user for a brief description, which is also echoed.

## Binary Analysis

The binary was compiled from C source code using `gcc`, with several mitigations enabled:

- **`PIE`**: Enabled
- **`Stack canary`**: Enabled
- **`NX` (Non-eXecutable stack)**: Enabled
- **`RELRO`**: _Partial RELRO_

The presence of Partial RELRO and the provided `libc` suggests a potential `ret2libc` exploitation path, particularly since the GOT is only partially protected.

### Functions of Interest

The following functions are implemented in the binary:

- `main`
- `readString`
- `readSize`
- `setSecurity`
- `init`

### main()

The `main` function implements the core challenge logic. Interestingly, it attempts to manually zero out GOT entries in a naive attempt to prevent typical `ret2libc` exploitation:

```c
init(argc, argv, envp);

printf("Write the size of your name: ");
Size = readSize(v8);

printf("You chose a name of size %s\n", v8);
printf("Write your name: ");
readString(v7, Size);

printf("Hello %s\n", v7);

// RWX memory mapping
v6 = (const char *)mmap((void *)0x13370000, 0x50u, 7, 34, -1, 0);

printf("Write a description: ");
readString(v6, 80);

printf("Your description is: %s\n", v6);
puts("Bye");

setSecurity();

// GOT wiping attempt
for (i = 0; i <= 10; ++i)
    *(&stdin + i - 14) = 0;
```

It's also important to notice that the description is stored in a memory region explicitly mapped at `0x13370000` with `RWX` permissions via `mmap`.

### readString()

This function is fairly straightforward and not particularly interesting from an exploitation perspective. It reads `n` bytes from `stdin` into a user-supplied buffer and removes the trailing newline character if present:

```c
v3 = read(0, a1, a2);
result = (unsigned __int8 *)a1[v3 - 1];
if ((_BYTE)result == 10)
{
    result = &a1[v3 - 1];
    *result = 0;
}
return result;
```

Despite its simplicity, note that the function does not enforce strict bounds checking — depending on the context in which it is used, this could lead to buffer overflows or memory corruption.

### readSize()

This function contains a subtle but interesting vulnerability related to inconsistent input parsing. It first reads up to 17 bytes into a buffer, then validates the input using `atoi`, and finally returns the parsed result using `strtol`.

```c
endptr[1] = (char *)__readfsqword(0x28u);  // stack canary reference
readString(a1, 17);

if ((unsigned int)atoi((const char *)a1) > 40)
{
    puts("Invalid size");
    exit(0);
}

return strtol((const char *)a1, endptr, 0);
```

The key issue here is the discrepancy between how `atoi` and `strtol` interpret numeric strings.

From the man page:

> The atoi() function converts the initial portion of the string pointed to by nptr to int.
> The behavior is the same as: `strtol(nptr, NULL, 10);`

However, in this case, `strtol` is called with a base of `0`, which enables **automatic base detection**:

- A prefix of `0x` will be interpreted as hexadecimal
- A prefix of `0` will be interpreted as octal
- No prefix will be interpreted as decimal

This creates an **inconsistent parsing bug**: the validation with `atoi` assumes base 10, while `strtol` may interpret the same input differently depending on the format. For example:

- Input: `0x100` → `atoi` returns 0 (fails the check), but `strtol` returns 256
- Input: `040` → `atoi` returns 40 (passes the check), but `strtol` returns 32 (octal)
- Input: `100` → both `atoi` and `strtol` return 100 (decimal)

This inconsistency can be exploited to bypass the validation logic and feed in a size greater than 40, potentially leading to an overflow or memory corruption in the calling function (main).

### setSecurity()

This function installs a basic [Seccomp Filter](https://www.kernel.org/doc/html/v5.0/userspace-api/seccomp_filter.html) that blacklists all syscalls except for `read` and `write`, effectively sandboxing any code executed from the description's memory region.

```
 line  CODE  JT   JF      K
=================================
 0000: 0x20 0x00 0x00 0x00000008  A = instruction_pointer
 0001: 0x35 0x00 0x05 0x13370000  if (A < 0x13370000) goto 0007
 0002: 0x35 0x04 0x00 0x13370050  if (A >= 0x13370050) goto 0007
 0003: 0x20 0x00 0x00 0x00000000  A = sys_number
 0004: 0x15 0x02 0x00 0x00000000  if (A == read) goto 0007
 0005: 0x15 0x01 0x00 0x00000001  if (A == write) goto 0007
 0006: 0x06 0x00 0x00 0x00000000  return KILL
 0007: 0x06 0x00 0x00 0x7fff0000  return ALLOW
```

**P.S.**: Apologies for the inconvenience caused by the missing `PR_SET_NO_NEW_PRIVS`.

### init()

Nothing particularly interesting happens inside this function, it simply sets the buffering mode for the standard I/O streams to **unbuffered** using `setvbuf`.

## Connect the dots

Basically, this challenge provided an opportunity to exploit a **buffer overflow** in the main function's stack buffer (protected by the **stack canary**), as well as the ability to write **shellcode** in a memory region with a known address, which is controlled by the attacker.

Additionally, the buffer overflow caused by reading the attacker's name could lead to a leak of the **canary** value, specifically through the overwriting of its null byte (`\0`).

## Exploit

Once the behavior of the binary was understood, several exploitation paths became apparent. The intended exploitation path was as follows:

1. **Leak the canary**: As mentioned previously, the attacker could overwrite the null byte of the canary, causing it to be printed along with the user's name. This would allow the attacker to leak the canary value, bypassing the stack protection.

2. **Write shellcode** inside the description memory region with the following steps:

   1. Read the address of the **`__libc_start_main`** function from the stack frame.
   2. Store this address in a register and subtract the known offset to get the base address of **libc**.
   3. Add the offset of either the **`system`** or **`execve`** function to the libc base address.
   4. Call the function with the correct parameters (e.g., `/bin/sh`), which could be stored anywhere, leveraging the shellcode itself for flexibility.

3. **Overflow** the return address of the `main` stack frame to redirect execution to the shellcode, effectively gaining control of the process and executing the payload.
