# Picasso

|         |                               |
| ------- | ----------------------------- |
| Authors | Alessandro Bombarda <@ale18v> |
| Points  | 500                           |
| Tags    | rev                           |

## Challenge Description

Many people recommended to Elia that he pursue a career in crypto scams. However, he chose to follow his childhood dream of becoming an accomplished painter.

Unfortunately, Elia's art is a bit mysterious. Will you be able to solve the mystery and uncover the flag?

## Summary

The challenge writes on the frame buffer an image.

## Code analysis

The program just checks for the DRM support and then print an image on the screen with the flag.

Analyzing the code is easy to see that the program is writing the entire framebuffer on the screen:

```
*(puVar12 + -8) = 0x1b15;
sym.imp.memset(iStack_c8, 0xff, auStack_d8._8_8_);
puVar15 = puVar12;
*(puVar12 + -8) = 0x1b36;
sub.time_13e4(iStack_c8, auStack_e8._4_4_, uStack_e0);
puVar16 = puVar15;
*(puVar15 + -8) = 0x1b4f;
sym.imp.munmap(iStack_c8, auStack_d8._8_8_);
```

## Exploit

Blocking on the unmapping of the frame will reveal the flag.
To do so, we first need to execute the program in a DRM environment, for instance by isusing `chvt 2` or using CTRL-ALT-2
After this we can simply use (in a shell):

![gdb commands](./writeup/1.png)

And get the following result
![encrypted flag](./writeup/2.png)

As you can see from the image, the flag is not readable.

The write function (here named time_13e4) encrypt the flag with a random key:

```
*(*0x20 + -0x40) = 0x1423;
uVar2 = sym.imp.time(0);
*(*0x20 + -0x38 + -8) = 0x142a;
sym.imp.srand(uVar2);
puVar3 = *0x20 + -0x38;
for (uStack_20 = 0; uStack_20 < 0x18 || uStack_20 == 0x18; uStack_20 = uStack_20 + 1) {
    for (iStack_1c = 0; iStack_1c == 0xf || SBORROW4(iStack_1c, 0xf) != iStack_1c + -0xf < 0;
        iStack_1c = iStack_1c + 1) {
        *(puVar3 + -8) = 0x1447;
        uStack_28 = sym.imp.rand();
        puVar3 = puVar3;
        for (iStack_18 = 0; iStack_18 == 0xb || SBORROW4(iStack_18, 0xb) != iStack_18 + -0xb < 0;
            iStack_18 = iStack_18 + 1) {
            uStack_26 = 1 << ('\f' + iStack_18 * -1 & 0x1fU);
            uVar1 = (*((iStack_1c + uStack_20 * 0x10) * 2 + 0x2020) ^ uStack_28) & uStack_26;
            if ((uVar1 & uVar1) != 0) {
                iStack_10 = iStack_18 + iStack_24;
                iStack_c = iStack_1c + iStack_14;
                if ((((-1 < iStack_10 + 0) && (iStack_10 < iStack_34)) && (-1 < iStack_c + 0)) &&
                   (iStack_c < iStack_38)) {
                    *(iStack_30 + (iStack_10 + iStack_c * iStack_34) * 4 + 2) = 0;
                    *(iStack_30 + (iStack_10 + iStack_c * iStack_34) * 4 + 1) = 0;
                    *(iStack_30 + (iStack_10 + iStack_c * iStack_34) * 4) = 0;
                    *(iStack_30 + (iStack_10 + iStack_c * iStack_34) * 4 + 3) = 0;
                }
            }
        }
    }
    iStack_24 = iStack_24 + 0xc;
}
```

As you can clearly see, the function uses `srand` and `rand` to encrypt the data. Therefore we can just hijack rand to return 0 every time with the following technique:

```bash
$ cat hijack.c
int rand(void)
{
    return 0;
}
$ gcc --shared -o libhijack.so hijack.c
```

And then use `set environment LD_PRELOAD ./libhijack.so` in gdb to nullify the encryption.
![flag](./writeup/3.png)
