# Cheri cheri PWN

|         |                          |
| ------- | ------------------------ |
| Authors | Davide Berardi <@berdav> |
| Points  | 500                      |
| Tags    | pwn,riscv                |

## Challenge Description

Cheri, cheri binary \
Goin' through a network \
Flag is where you find it \
Listen to your de-bug

Cheri, cheri binary \
Living in syscall \
It's always like the first time \
Let me take an address

Cheri, cheri binary \
Like there's no tomorrow \
Take my leak, don't lose it \
Listen to your gdb

Cheri, cheri binary \
To pwn you is to love you \
If you call me AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA (Background voice: 0x41414141414141414141) \
I'll be always Segmentation Fault (Background voice: core dumped)

---

This is a remote challenge, you can connect with:

`nc cheri.challs.ulisse.ovh 5534`

## Overview

This challenge uses cheri as architecture.

The application is composed of 6 classical vulnerabilities, we need in order to:

1. Find an exploitable vulnerability

2. Find a leak to construct the exploit payload

3. Exploit it.

The difficult part of the challenge resides in the understanding of cheri and the use of a not common operating system such as CheriBSD.

To do that, it is provided by the challenge a Dockerfile which is based on cheribsd programming tools.

The user can then try to debug the application trough qemu using the following command.

## Exploitable vulnerability

Cheri covers all static buffers and allocators, but the tracking is lost when dealing with custom heap structures and allocations. Therefore we can exploit vulnerability number 4 overwriting the function pointer of the "class".

This will trigger a custom function, which is controllable by the attacker, the other functions are then unuseful for the exploitation.

## Finding a leak

To find a leak, we can use the format string vulnerability present on vulnerability number 6. Simply use %5$p to get a pointer in the libc. After this we can simply get the pointers to the various required functions and data such as "/bin/sh" string.

Also, the library also do not has PIE, therefore it is only required to get the address of the my_system function (0x0120ee) which is really easy to find trough reverse engineering.

```
[0x00011f70]> axt @0x125b0
(nofunc) 0x120ee [CALL:--x] jal ra, sym.imp.system
```

## Exploiting the vulnerability

Here comes the "hard" part, cheri introduces new faults and signals which are then handled by the operating system. This disable most of the BOF exploits.

As stated by the [exploitation tutorial for cheri](https://ctsrd-cheri.github.io/cheri-exercises/introduction/background.html), the checks can be avoided when dealing with heap-based pointers and direct system calls without special allocators.

Therefore it is simply required to interact with the system in the following way:

```python
from pwn import *
# Check challenge
r = remote(HOST, PORT)

r.sendlineafter(b'> ', b'4')
r.sendline(p64(0x1020ee))
r.sendline(b'cat /flag.txt')
f = r.recvline()
print(f)
```
