# Xtens(a)ible Kite

|         |                          |
| ------- | ------------------------ |
| Authors | Davide Berardi <@berdav> |
| Points  | 500                      |
| Tags    | rev,hardware,crypto      |

## Challenge Description

I found a strange chip in my kite. Asking to the producer, they sent me this file but I cannot find what it's doing. Are there some hidden information in this?

## Summary

This CTF is based on zephyr with ESP32 Xtensa module.

It requires some knownledge on the embedded programming and reversing.

With the following command one can see that the flag is being printed by the program.

```shell
ubuntu@ctf:~$ strings -tx ./zephyr.elf | grep flag:
  10b3b flag: %s
```

From file we cannot get information, but from the description of the challenge
we can get the details on the architecture of the device which is xtensa

This also can be derived from a string of the program:

```shell
ubuntu@ctf:~$ strings -tx ./zephyr.elf | grep BoCTF
  10b45 .Starting BoCTF on ESP32-WROOM-ATECC608A
```

After analyzing with `r2 -a xtensa ./zephyr.bin` (after installing the xtensa
module) we can get the flag position with:

```shell
ubuntu@ctf:~$ r2 -a xtensa ./zephyr.elf
WARN: Cannot find asm.parser for xtensa
INFO: Fallback to null
WARN: Cannot find asm.parser for xtensa
WARN: Cannot find asm.parser for xtensa
WARN: Relocs has not been applied. Please use `-e bin.relocs.apply=true` or `-e bin.cache=true` next time
WARN: Cannot find asm.parser for xtensa
 -- The Quick Brown Fox Jumped Over The Lazy Dog!
[0x400834a4]> / flag:
0x3f400b3b hit0_0 .verified: %dflag: %s.Starting B.
```

We can then analyze the binary with `aaaa`:

```shell
[0x400834a4]> aaaa
INFO: Analyze all flags starting with sym. and entry0 (aa)
INFO: Analyze imports (af@@@i)
INFO: Analyze entrypoint (af@ entry0)
WARN: select the calling convention with `e anal.cc=?`
INFO: Analyze symbols (af@@@s)
INFO: Analyze all functions arguments/locals (afva@@@F)
INFO: Analyze function calls (aac)
INFO: Analyze len bytes of instructions for references (aar)
INFO: Finding and parsing C++ vtables (avrr)
INFO: Analyzing methods (af @@ method.*)
INFO: Emulate functions to find computed references (aaef)
INFO: Recovering local variables (afva@@@F)
INFO: Type matching analysis for all functions (aaft)
INFO: Propagate noreturn information (aanr)
INFO: Integrate dwarf function information
INFO: Scanning for strings constructed in code (/azs)
INFO: Finding function preludes (aap)
INFO: Enable anal.types.constraint for experimental type propagation
INFO: Finding xrefs in noncode sections (e anal.in=io.maps.x; aav)
```

With this also, we can find the address of the main function:

```shell
[0x400834a4]> afl~main
0x4008169c    1      7 dbg.main_flash_region_protected
0x400820f0   12    154 dbg.bg_thread_main
0x400d0418    1    326 dbg.main
```

Seeking to main address and disassembling it we can get a better view on what is going on:

```shell
[0x400d0418]> s sym.main
[0x400d0418]> pd 30
            ;-- main:
            ; CALL XREF from dbg.bg_thread_main @ 0x4008217a(x)
┌ 326: int dbg.main (int argc, int32_t argv, int32_t envp, int32_t arg_180h, int32_t arg_190h);
│ `- args(a2, sp[0x88..0x190]) vars(9:sp[0x30..0x1b0])
│           0x400d0418      368103         entry a1, 0x1c0             ; main.c:12 ; int main();
│           0x400d041b      22d101         addmi a2, a1, 0x100         ; main.c:13
│           0x400d041e      b1f8fe         l32r a11, loc._text_start   ; str._Starting_BoCTF_on_ESP32_WROOM_ATECC608A
│                                                                      ; [0x400d0000:4]=0x3f400b45 str..Starting_BoCTF_on_ESP32_WROOM_ATECC608A ; "E\v@?\x84"
│           0x400d0421      2c9c           movi.n a12, 41
│           0x400d0423      a2c218         addi a10, a2, 24
│           0x400d0426      8102ff         l32r a8, sym.memcpy         ; [0x400d0030:4]=0x4000c2c8 sym.memcpy
│           0x400d0429      e00800         callx8 a8
│           0x400d042c      b1f6fe         l32r a11, obj.cfg_ateccx08a_i2c_default ; main.c:19 ; [0x3ffb0084:4]=0
│           0x400d042f      a2a080         movi a10, 128
│           0x400d0432      3c4c           movi.n a12, 52
│           0x400d0434      1aaa           add.n a10, a10, a1
│           0x400d0436      81fefe         l32r a8, sym.memcpy         ; [0x400d0030:4]=0x4000c2c8 sym.memcpy
│           0x400d0439      e00800         callx8 a8
│           0x400d043c      b1f3fe         l32r a11, 0x400d0008        ; main.c:20 ; [0x400d0008:4]=0x3f400b6e
│           0x400d043f      0cc7           movi.n a7, 12
│           0x400d0441      0c05           movi.n a5, 0                ; main.c:21
│           0x400d0443      cd07           mov.n a12, a7               ; main.c:25
│           0x400d0445      a2c271         addi a10, a2, 113
│           0x400d0448      526160         s32i a5, a1, 0x180          ; main.c:21
│           0x400d044b      81f9fe         l32r a8, sym.memcpy         ; main.c:22 ; [0x400d0030:4]=0x4000c2c8 sym.memcpy
│           0x400d044e      e00800         callx8 a8
│           0x400d0451      b1eefe         l32r a11, 0x400d000c        ; main.c:26 ; [0x400d000c:4]=0x3f400b7b
│           0x400d0454      1c06           movi.n a6, 16
│           0x400d0456      cd06           mov.n a12, a6
│           0x400d0458      a2c261         addi a10, a2, 97
│           0x400d045b      81f5fe         l32r a8, sym.memcpy         ; [0x400d0030:4]=0x4000c2c8 sym.memcpy
│           0x400d045e      e00800         callx8 a8
│           0x400d0461      2c0d           movi.n a13, 32              ; main.c:27
│           0x400d0463      b1ebfe         l32r a11, str.jqn6          ; [0x3f400b8c:4]=0x366e716a ; "jqn6\xf0\xb2\xda\\x92O3,H\x9e\xb7\xe9M\x1dL\xb9\xcf<~\xbfim\xe9\xaa\xf5\xc8YN"
│           0x400d0466      cd0d           mov.n a12, a13

```

As you can see, this is the address of the main function. The entire function is not displayied, therefore we need to instruct
radare to disassemble the entire function and print all the calls.

```shell
[0x400d0418]> pd 100~call
│           0x400d0429      e00800         callx8 a8
│           0x400d0439      e00800         callx8 a8
│           0x400d044e      e00800         callx8 a8
│           0x400d045e      e00800         callx8 a8
│           0x400d0471      e00800         callx8 a8
│           0x400d0485      e00800         callx8 a8
│           0x400d0494      e00800         callx8 a8
│           0x400d049c      e51eb4         call8 sym.puts              ; int puts(const char *s)
│           0x400d04b0      e5d202         call8 dbg.atcab_init        ; main.c:37
│           0x400d04ba      651ab4         call8 sym.printf            ; int printf(const char *format)
│           0x400d04c2      e53b03         call8 dbg.calib_wakeup
│           0x400d04ca      6519b4         call8 sym.printf            ; int printf(const char *format)
│           0x400d04d9      655f03         call8 dbg.calib_nonce_load
│           0x400d04e0      e517b4         call8 sym.printf            ; int printf(const char *format)
│           0x400d04f3      e51303         call8 sym.calib_aes_gcm_init
│           0x400d04fa      6516b4         call8 sym.printf            ; int printf(const char *format)
│           0x400d050d      651f03         call8 dbg.calib_aes_gcm_decrypt_update
│           0x400d0514      a514b4         call8 sym.printf            ; int printf(const char *format)
```

Is clear that the device is printing some information (the flag etc..) and using some "calib" and AES functions.

If we search, for instance `calib_aes_gcm_init`, we can find a library from microchip [cryptoauthlib](https://github.com/MicrochipTech/cryptoauthlib/blob/main/lib/calib/calib_basic.h) wich can be used to perform AES operation using external secure modules.

Search aes we can see that the cryptographical functions used by main are:

```shell
[0x400d0418]> pd 300~aes
│           0x400d04f3      e51303         call8 sym.calib_aes_gcm_init
│           0x400d050d      651f03         call8 dbg.calib_aes_gcm_decrypt_update
│           0x400d0527      a51f03         call8 dbg.calib_aes_gcm_decrypt_finish
```

Looking at the signature of these information we can see that the functions have the following signatures:

```
ATCA_STATUS calib_aes_gcm_init(ATCADevice device, atca_aes_gcm_ctx_t* ctx, uint16_t key_id, uint8_t key_block, const uint8_t* iv, size_t iv_size);
ATCA_STATUS calib_aes_gcm_decrypt_update(ATCADevice device, atca_aes_gcm_ctx_t* ctx, const uint8_t* ciphertext, uint32_t ciphertext_size, uint8_t* plaintext);
ATCA_STATUS calib_aes_gcm_decrypt_finish(ATCADevice device, atca_aes_gcm_ctx_t* ctx, const uint8_t* tag, size_t tag_size, bool* is_verified);
```

Isolating the required arguments, we see that we need the key, an IV, the tag, and the ciphertext (due to AES Galois Counter Mode [works](https://en.wikipedia.org/wiki/Galois/Counter_Mode)).

Using radare we can then retrieve the values of the various variables we need.

```shell
[0x400d0418]> afv
arg int argc @ a2
arg int32_t argv @ a1+0x88
arg int32_t envp @ a1+0xb0
arg int32_t arg_180h @ a1+0x180
arg int32_t arg_190h @ a1+0x190
var int is_verified @ a14-0x30
var uint8_t[12] iv @ a14-0x3f
var uint8_t[16] tag @ a14-0x4f
var uint8_t[32] key @ a14-0x6f
var char[41] banner_starting_boctf @ a14-0x98
var uint8_t[50] encrypted_flag @ a14-0xca
var uint8_t[50] plaintext @ a14-0xfc
var ATCAIfaceCfg cfg @ a14-0x130
var atca_aes_gcm_ctx_t ctx @ a14-0x1b0
```

From the variable `banner_starting_boctf` we can find the places of the various data.
For instance, in the case above we can calculate the following information:

```shell
[0x400d0418]> / .Starting
0x3f400b45 hit1_0 .: %dflag: %s.Starting BoCTF on ESP32-.
```

Unfortunately seems to be a bug of radare2, but the address of encryption data can be retrieved by looking in the code.

For instance, a11 is loaded with a strange value

```shell
[0x400d0418]> pd 30~a11
│           0x400d041e      b1f8fe         l32r a11, loc._text_start   ; str._Starting_BoCTF_on_ESP32_WROOM_ATECC608A
│           0x400d042c      b1f6fe         l32r a11, obj.cfg_ateccx08a_i2c_default ; main.c:19 ; [0x3ffb0084:4]=0
│           0x400d043c      b1f3fe         l32r a11, 0x400d0008        ; main.c:20 ; [0x400d0008:4]=0x3f400b6e
│           0x400d0451      b1eefe         l32r a11, 0x400d000c        ; main.c:26 ; [0x400d000c:4]=0x3f400b7b
│           0x400d0463      b1ebfe         l32r a11, str.jqn6          ; [0x3f400b8c:4]=0x366e716a ; "jqn6\xf0\xb2\xda\\x92O3,H\x9e\xb7\xe9M\x1dL\xb9\xcf<~\xbfim\xe9\xaa\xf5\xc8YN"
```

From this we can retrieve the crypto information, seems that the layout of radare is preserved and they're 0 separated:

key:

```shell
[0x400d0418]> px 32 @0x3f400b8c
- offset -  8C8D 8E8F 9091 9293 9495 9697 9899 9A9B  CDEF0123456789AB
0x3f400b8c  6a71 6e36 f0b2 da5c 924f 332c 489e b7e9  jqn6...\.O3,H...
0x3f400b9c  4d1d 4cb9 cf3c 7ebf 696d e9aa f5c8 594e  M.L..<~.im....YN
```

tag:

```shell
[0x400d0418]> px 16 @0x3f400b8c - 1 - 16
- offset -  7B7C 7D7E 7F80 8182 8384 8586 8788 898A  BCDEF0123456789A
0x3f400b7b  ef11 1877 1366 e178 4478 dfbb 52b5 d182  ...w.f.xDx..R...
```

iv:

```shell
[0x400d0418]> px 12 @0x3f400b8c - 1 - 16 - 12 - 1
- offset -  6E6F 7071 7273 7475 7677 7879 7A7B 7C7D  EF0123456789ABCD
0x3f400b6e  5be5 565d 84f7 d480 d4a5 f8a4            [.V]........
```

encrypted flag:

```shell
[0x400d0418]> px 60 @0x3f400b8c + 32 + 1
- offset -  ADAE AFB0 B1B2 B3B4 B5B6 B7B8 B9BA BBBC  DEF0123456789ABC
0x3f400bad  5006 9539 de25 4c68 b106 4278 dd04 d558  P..9.%Lh..Bx...X
0x3f400bbd  ea81 9ca2 3dde 1569 6ecf 4655 0c3c 6bc6  ....=..in.FU.<k.
0x3f400bcd  ecce 77c6 4160 4618 5593 a0fe f3ab 7a87  ..w.A`F.U.....z.
0x3f400bdd  efae 0065 7370 5f63 6c6b 5f74            ...esp_clk_t
```

We don't know the length of the flag, but we see that there is a zero around 50 characters.
Therefore crypto informations are:

iv: `5be5565d84f7d480d4a5f8a4`
key: `6a716e36f0b2da5c924f332c489eb7e94d1d4cb9cf3c7ebf696de9aaf5c8594e`
tag: `ef1118771366e1784478dfbb52b5d182`
ciphertext: `50069539de254c68b1064278dd04d558ea819ca23dde15696ecf46550c3c6bc6ecce77c6416046185593a0fef3ab7a87efae`

So we can implement a decrypter such as:

```js
#!/usr/bin/env nodejs
const crypto = require("crypto");

function decrypt(key, iv, tag, ciphertext) {
  var decipher = crypto.createDecipheriv("aes-256-gcm", key, iv);
  decipher.setAuthTag(tag);
  var decrypted = decipher.update(ciphertext);
  decrypted += decipher.final("utf8");
  return decrypted;
}

console.log(
  decrypt(
    Buffer.from("6a716e36f0b2da5c924f332c489eb7e9", "hex"),
    Buffer.from("5be5565d84f7d480d4a5f8a4", "hex"),
    Buffer.from("ef1118771366e1784478dfbb52b5d182", "hex"),
    Buffer.from(
      "50069539de254c68b1064278dd04d558ea819ca23dde15696ecf46550c3c6bc6ecce77c6416046185593a0fef3ab7a87efae",
      "hex",
    ),
  ),
);
```

And

```shell
ubuntu@ctf:~$ node decrypt.js
node:internal/crypto/cipher:199
  const ret = this[kHandle].final();
                            ^

Error: Unsupported state or unable to authenticate data
    at Decipheriv.final (node:internal/crypto/cipher:199:29)
    at decrypt (/home/ubuntu/decrypt.js:8:27)
    at Object.<anonymous> (/home/ubuntu/decrypt.js:13:2)
    at Module._compile (node:internal/modules/cjs/loader:1356:14)
    at Module._extensions..js (node:internal/modules/cjs/loader:1414:10)
    at Module.load (node:internal/modules/cjs/loader:1197:32)
    at Module._load (node:internal/modules/cjs/loader:1013:12)
    at Function.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:128:12)
    at node:internal/main/run_main_module:28:49

Node.js v18.19.1
```

This will not work :)

Note: I've made this more clear by setting half of the key to 0, which
make more clear that the key is just 16 bytes.

That's due to the fact that the library uses 32Bytes key but in reality (as confirmed by the ATECC608 datasheet, it uses only 16B.

So we just need to change the size of the key and use `aes-128-gcm` as the cipher:

```js
#!/usr/bin/env nodejs
const crypto = require("crypto");

function decrypt(key, iv, tag, ciphertext) {
  var decipher = crypto.createDecipheriv("aes-128-gcm", key, iv);
  decipher.setAuthTag(tag);
  var decrypted = decipher.update(ciphertext);
  decrypted += decipher.final("utf8");
  return decrypted;
}

console.log(
  decrypt(
    Buffer.from("6a716e36f0b2da5c924f332c489eb7e9", "hex"),
    Buffer.from("5be5565d84f7d480d4a5f8a4", "hex"),
    Buffer.from("ef1118771366e1784478dfbb52b5d182", "hex"),
    Buffer.from(
      "50069539de254c68b1064278dd04d558ea819ca23dde15696ecf46550c3c6bc6ecce77c6416046185593a0fef3ab7a87efae",
      "hex",
    ),
  ),
);
```

Running this will give us the flag.

```shell
ubuntu@ctf:~$ node ./decrypt.js
UlisseCTF{r3v3rs3_3ngin33ring_esp32_1s_fun}
```
