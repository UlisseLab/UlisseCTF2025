# Self Quote

|         |                          |
| ------- | ------------------------ |
| Authors | Davide Berardi <@berdav> |
| Points  | 500                      |
| Tags    | forensics                |

## Challenge Description

Recently our 🦊 agent find this file in a profile directory but he cannot retrive it, it seems a sort of image, can you decrypt it?

## Overview

This challenge is a firefox morgue cache file with a broken header.

The image has been sent over whatsapp, in its web version.

Firefox morgue caches are Snappy Files, which requires the file to have
sNaPpY in the first bytes.

If we analyze a correct snappy file we see:

```shell
bera@neohaigha ~ % xxd ~/git/challenge.orig | head -1
00000000: ff06 0000 734e 6150 7059 00c6 e500 fda7  ....sNaPpY......
```

On the challenge, on the other hand, the binary has been corrupted.

```shell
bera@neohaigha ~ % xxd ~/git/challenge.data | head -1
00000000: ff06 0000 7300 6100 7000 00c6 e500 fda7  ....s.a.p.......
```

Restoring these bytes and executing snappy-fox or equivalent snappy
unzipper we could retrieve the image which contains the flag.

```shell
bera@neohaigha ~ % sed 's/s\x00a\x00p\x00/sNaPpY/' challenge.data > challenge.snappy
bera@neohaigha ~ % ~/snappy-fox/snappy-fox ./challenge.snappy challenge.jpg
```
