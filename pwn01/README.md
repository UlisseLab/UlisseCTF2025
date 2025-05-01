# Zig Zag Zoogle

|         |                     |
| ------- | ------------------- |
| Authors | Eyad Issa <@VaiTon> |
| Points  | 500                 |
| Tags    | pwn                 |

## Challenge Description

Zig is a systems programming language crafted to be a better C.

It strives to be extremely safe... but only if you tell the compiler to try its hardest. 😅

This is a remote challenge, you can connect with:

`nc zig.challs.ulisse.ovh 5331`

## Building

```
zig build-exe main.zig -O ReleaseFast -fno-strip
```

## Challenge Background

This challenge was originally intended to be released with its source code. However, during testing, one of the authors managed to solve it without access to the source. This led to the decision to publish the challenge as a binary-only problem.

## Intended Solution (Original Design)

The file `chall.zig` contains the challenge source code. The challenge is a simple program that takes an arbitrary number of integers and computes their average.

To compile it:

```shell
zig build-exe chall.zig
```

### Key Compilation Detail

Zig offers [three distinct optimization levels](https://ziglang.org/documentation/master/#Build-Mode). By default, it compiles in Debug mode, which includes many safety checks. This challenge, however, was built using ReleaseFast mode, optimizing for performance by stripping out many of those protections:

```shell
zig build-exe chall.zig -O ReleaseFast
```

### Source Code Analysis

Looking at the source code, apart from some utilities functions, we can see that the main function reads the number of integers to average, and then reads the integers one by one in a loop. An interesting check is done at the end of each iteration:

```ziglang
if ((sum ^ zig) < 0 and @as(u32, @bitCast(sum)) == 0xFFFFFFFF) {
    // how ??? you deserve a flag
    try printFlag(allocator);
}
```

To trigger the flag condition, a possible solution is to overflow the i32 sum variable to reach -1 (which equals 0xFFFFFFFF in two's complement representation). This can be achieved with input like:

```shell
❯ ./zigzagzoogle
Enter the number of values to average: 3
Enter value 1: 2147483647
Enter value 2: 2147483647
Enter value 3: 1
FLAG: UlisseCTF{REDACTED}
The average is: -0.33333334
```

## Solution Without Source Code

We can analyze the binary using radare2:

```c
r2 ./zigzagzoogle
[0x0100c650]> aaaa
INFO: Analyze all flags starting with sym. and entry0 (aa)
INFO: Analyze imports (af@@@i)
INFO: Analyze entrypoint (af@ entry0)
INFO: Analyze symbols (af@@@s)
INFO: Analyze all functions arguments/locals (afva@@@F)
INFO: Analyze function calls (aac)
INFO: Analyze len bytes of instructions for references (aar)
INFO: Finding and parsing C++ vtables (avrr)
INFO: Analyzing methods (af @@ method.*)
INFO: Recovering local variables (afva@@@F)
INFO: Type matching analysis for all functions (aaft)
INFO: Propagate noreturn information (aanr)
INFO: Integrate dwarf function information
INFO: Scanning for strings constructed in code (/azs)
INFO: Finding function preludes (aap)
INFO: Enable anal.types.constraint for experimental type propagation
```

This performs deep analysis: symbols, entry points, function arguments, calls, strings, and more.

Let's list the functions that match `start`:

```c
[0x0100c650]> afl~start
0x0100c650    1     32 dbg.start._start
0x0100c670  435   8181 dbg.start.posixCallMainAndExit
0x0100f640    1      1 dbg.start.noopSigHandler
```

We can guess that the entry point is `dbg.start._start`, let's seek to it:

```c
[0x0100c650]> s dbg.start._start
```

The decompiled function shows a standard \_start routine which eventually calls:

```c
dbg.start.posixCallMainAndExit();
```

Let's seek to `dbg.start.posixCallMainAndExit` to see what it does:

```c
[0x0100c650]> s dbg.start.posixCallMainAndExit
[0x0100c670]>
```

During further analysis, we come across code handling input characters like `+`, `-`, and `_`, hinting at custom number parsing logic—perhaps to allow underscores in numeric literals (`1_000_000` style).

```c
if (cVar91 != '_') {
    if (cVar91 == '-') {
...
            if (cVar91 == '+') {

```

Later, we spot this intriguing check:

```c
*(puVar82 + 8) = iVar63;
if ((iVar63 == -1) && ((uVar95 ^ *(puVar82 + 8)) < 0)) {
    *(puVar82 + -8) = 0x100d34b;
    dbg.process.getEnvMap(puVar82 + 0x28);
```

If this condition is met, a sequence is triggered that appears to access the flag:

```c
if (-1 < "FLAG"[uVar90]) goto code_r0x0100d3d0;
   uVar102 = *("FLAG"[uVar90] + 0x1003540);
   if ((uVar102 == 0xf1) || (uVar72 = uVar102 & 7, 4 < uVar90 + uVar72)) break;
   uVar107 = (uVar102 >> 4) << 3;
   uVar103 = 0x809080a080 >> (uVar107 & 0x3f);
   if (("FLAG"[uVar90 + 1] < uVar103) ||
      (0x8fbf9fbfbf >> (uVar107 & 0x3f) < "FLAG"[uVar90 + 1])) break;
   uVar107 = uVar72;
   if (uVar72 != 2) {
       if (uVar72 == 3) {
           cVar91 = "FLAG"[uVar90 + 2];
           uVar107 = 3;
           if (cVar91 == -0x41 || SBORROW1(cVar91,-0x41) != cVar91 + 'A' < '\0')
           goto code_r0x0100d3d0;
       }
       else {
           cVar91 = "FLAG"[uVar90 + 2];
           if ((cVar91 == -0x41 || SBORROW1(cVar91,-0x41) != cVar91 + 'A' < '\0') &&
              (uVar107 = 4,
              SBORROW1("FLAG"[uVar90 + 3],-0x40) != "FLAG"[uVar90 + 3] + '@' < '\0'))
           goto code_r0x0100d3d0;
       }
       break;
   }
```

This code seems to involve intricate bounds and bitwise logic, but the bottom line is that reaching sum == -1 activates the flag path.

We can see the relation better with BinaryNinja:

![Binary Ninja screenshot showing the graph view of the blocks](./writeup/bj.png)

As shown before, feeding carefully chosen inputs causes an integer overflow in the sum:

```shell
❯ ./zigzagzoogle
Enter the number of values to average: 3
Enter value 1: 2147483647
Enter value 2: 2147483647
Enter value 3: 1
FLAG: UlisseCTF{REDACTED}
The average is: -0.33333334
```
