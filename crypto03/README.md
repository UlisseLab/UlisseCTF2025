# twisted keystream

|         |                            |
| ------- | -------------------------- |
| Authors | Davide Gianessi <@gianetz> |
| Points  | 500                        |
| Tags    | crypto                     |

## Challenge Description

I was downloading some ram, when an hacker encrypted all of the GLORIUS NOVEL I was writing, now he's asking for a gazillion in EliaSusCoin in exchange for the key.

Can you help me?

## Overview

This challenge gives you a long ciphertext obtained from a custom encryption scheme, where we know that the plaintext has some characteristics (we have the generation script) and we must do some frequency analysis to recover the key and the original message.

the ecryption works like this: at the beginning, from the key we derive the twist, then we xor the first block of the plaintext with the key, to obtain the key for the second block we permute all of the bits according to the twist and we xor it with the second block of the plaintext to get the the second block of the ciphertext, then we permute the key again using the twist and so on

```python
ciphertext=b""
twist=key
for i in range(len(plaintext)//block_size):
    ciphertext+=xor(key,plaintext[block_size*i:block_size*(i+1)])
    key=bytes_to_long(key)
    key=[(key>>i2)&1 for i2 in range(block_size*8)]
    random.Random(twist).shuffle(key)
    key=sum([key[i2]<<i2 for i2 in range(block_size*8)])
    key=long_to_bytes(key)
    key=b"\x00"*(block_size-len(key))+key
```

Well first things first, we have to take a look at our plaintext and what we can say about it,
it is generated like this:

```python
def generate_weighted_words(n, top_n=500000):
    word_list = top_n_list("en", top_n)
    probabilities = [word_frequency(word, "en") for word in word_list]
    total = sum(probabilities)
    probabilities = [p / total for p in probabilities]
    sampled_words = random.choices(word_list, weights=probabilities, k=n)
    return sampled_words

```

## Checking for patterns

We can genererate a few of these plaintexts ourself and check if there are any patterns we can exploit, as the key gets shuffled around, we are less interested in byte patterns and more in bit patters, we can try something like:

```python
plaintext = " ".join(plaintext).encode()
plaintext=plaintext[:(len(plaintext)//block_size)*block_size]
chars={}
for c in plaintext:
    if c not in chars:
        chars[c]=0
    chars[c]+=1
for c in chars.keys():
    padding=""
    if(len(str(bytes([c])))<7):
        padding=" "*3
    print(bytes([c]),padding,"\t",chars[c],"\t",bin_min(c,8))[2])


blocks=[plaintext[block_size*i:block_size*(i+1)] for i in range(len(plaintext)//block_size)]

bits=[0 for i in range(block_size*8)]
for block in blocks:
    block=bytes_to_long(block)
    for i in range(block_size*8):
        bits[i]+=(block>>(127-i))&1

for i in range(block_size):
    print(bits[8*i:8*i+8])
print(len(plaintext)//block_size)

```

and we get an output like this:

```
b'u'             1310    01110101
b's'             2763    01110011
b' '             9998    00100000
b't'             3998    01110100
b'h'             2252    01101000
b'e'             5189    01100101
b'i'             3213    01101001
b'p'             960     01110000
b'r'             2614    01110010
b'o'             3550    01101111
b'g'             881     01100111
b'a'             3611    01100001
b'n'             3145    01101110
b'd'             1587    01100100
b'c'             1326    01100011
b'j'             91      01101010
b'w'             867     01110111
b'l'             1797    01101100
b'b'             708     01100010
b'y'             961     01111001
b'm'             1073    01101101
b"'"             159     00100111
b'f'             978     01100110
b'v'             455     01110110
b'k'             392     01101011
b'6'             5       00110110
b'x'             73      01111000
b'2'             16      00110010
b'q'             35      01110001
b'9'             4       00111001
b'3'             12      00110011
b'8'             3       00111000
b'z'             45      01111010
b'0'             11      00110000
b'1'             11      00110001
b'U'             1       01010101
b'C'             1       01000011
b'T'             1       01010100
b'F'             1       01000110
b'{'             1       01111011
b'}'             1       01111101
b'7'             4       00110111
b'.'             9       00101110
b'\xf0'          3       11110000
b'\x9f'          3       10011111
b'\x98'          2       10011000
b'\xae'          1       10101110
b'4'             9       00110100
b'5'             3       00110101
b'\xe2'          2       11100010
b'\x96'          2       10010110
b'\x92'          1       10010010
b'\xac'          1       10101100
b'\x91'          1       10010001
b'\x8c'          1       10001100
b'\x82'          1       10000010
b'\xc2'          1       11000010
b'\xa9'          1       10101001
[0, 2789, 3384, 931, 1013, 1570, 1170, 1624]
[0, 2753, 3384, 881, 1059, 1592, 1121, 1566]
[1, 2747, 3383, 887, 1080, 1612, 1141, 1581]
[1, 2724, 3384, 913, 1032, 1528, 1111, 1537]
[1, 2715, 3384, 888, 1037, 1518, 1141, 1578]
[1, 2774, 3383, 850, 1053, 1587, 1160, 1658]
[1, 2744, 3383, 858, 1052, 1574, 1084, 1591]
[1, 2704, 3382, 900, 1018, 1526, 1085, 1557]
[1, 2758, 3384, 852, 1066, 1616, 1124, 1557]
[2, 2770, 3383, 847, 1092, 1571, 1127, 1578]
[2, 2724, 3382, 926, 1011, 1559, 1136, 1621]
[2, 2765, 3382, 881, 1060, 1597, 1114, 1615]
[1, 2723, 3384, 915, 1037, 1522, 1155, 1566]
[2, 2731, 3383, 870, 1001, 1583, 1096, 1592]
[2, 2707, 3381, 899, 979, 1536, 1116, 1530]
[2, 2758, 3382, 877, 1029, 1540, 1153, 1622]
3384
```

there are some weird symbols and emojis every now and then, but it's mostly lowercase letters and spaces

the real info is in the second part, where we find that bits in certain positions of the byte have very strong biases either toward one or toward zero
this is the case of the first and the third bit of each byte, for which they are pretty much all zeros or ones with very few exceptions

## Learning the cycles

if we now consider the first bit of the first byte of each block in the ciphertext we now know that this sequence is very close to the first bit of the first byte of the key generated for each round, but due to the way the key is permuted every time with the same twist we know that this sequence is cyclical with size at most 128

while allowing for a little tolerance for the few ones in the plaintext we can test if the cycle is long n by checking if firstbit[i]==firstbit[(i+n)] for each i, once we find the cycle we also find the sequence by checking for the actual values of firstbit

we can do this for the first and the third bits of all the bytes in the block and we find a bunch of cycles, if we are lucky the sum of the size of the different cycles we find (some will be in the same cycle and get the same permutation but rotated) will be already 128 or pretty close meaning that we know all of the keys and we just have to assign each key to a remaining bit

with key here i mean all the bits of the key that corrispond to that bit in that block

```
cycles=[]
firstbit=[[cipher_blocks[i][i2]>>7 & 1 for i in range(len(cipher_blocks))] for i2 in range(block_size)]
thirdbit=[[1-(cipher_blocks[i][i2]>>5 & 1) for i in range(len(cipher_blocks))] for i2 in range(block_size)]
cycle_len_1=[0 for i in range(block_size)]
for i2 in range(block_size):
    for length in range(1,128):
        errors=0
        for i in range(len(firstbit[i2])-length):
            if firstbit[i2][i]!=firstbit[i2][i+length]:
                errors+=1
        if errors<150:
            cycle_len_1[i2]=length
            break
    if cycle_len_1[i2]==0:
        print("cycle finder failed")
        exit()
    if cycle_len_1[i2] not in [len(cycle) for cycle in cycles]:
        cycles.append(firstbit[i2][:cycle_len_1[i2]])
cycle_len_3=[0 for i in range(block_size)]
for i2 in range(block_size):
    for length in range(1,128):
        errors=0
        for i in range(len(thirdbit[i2])-length):
            if thirdbit[i2][i]!=thirdbit[i2][i+length]:
                errors+=1
        if errors<150:
            cycle_len_3[i2]=length
            break
    if cycle_len_3[i2]==0:
        print("cycle finder failed")
        exit()
    if cycle_len_3[i2] not in [len(cycle) for cycle in cycles]:
        cycles.append(thirdbit[i2][:cycle_len_3[i2]])
```

i am doing an approximation here where i check if two cycles are the same cycle by comparing the length, which wouldn't work in the case of two cycles of the same length, but seems to work fine, so it's not a big problem

now if we were not lucky enough to get to 128 immediately, but for example we get 123, then we could add to our list of cycles all possible cycles up to length five, which are manageable, but we where lucky, so that was not necessary

## Using the cycles

now that we have all of the cycles, the bias of the second, fourth, fifth and seventh bit, becomes significant, because we can try all possible starting positions of all possible cycles on each of them, and see which of them follow the trend, the bias is significant enough that usually only one of these (the correct one) will follow the bias significantly

for each of them we can do something like:

```python
fourthbit=[[cipher_blocks[i][i2]>>4 & 1 for i in range(len(cipher_blocks))] for i2 in range(block_size)]

print("fourthbit")
for i in range(block_size):
    print("\tpos:",i)
    found=False
    for cycle in cycles:
        for startingpoint in range(len(cycle)):
            unos=0
            for i2 in range(len(cipher_blocks)):
                if fourthbit[i][i2]!=cycle[(startingpoint+i2) % len(cycle)]:
                    unos+=1
                    if unos>1000:
                        break
            if unos<1000:
                print("\t\tDONE")
                key[i]+=cycle[startingpoint]<<4
                found=True
                break
        if found:
            break
```

## The last two bits

we are left with the sixth and the eight bit of each byte, which do not seem to have a significant bias, however if we pay attention to the distribution of character and bits, we can see that the the vast, vast majority of the bytes with the second bit at 0 are spaces, so if when calculating the second bits we save where each "highly probable space" is, we can rate the starting positions for the last two bits, not by frequency of ones or zeros, but how many "highly probable spaces" they would have the correct bit for that to be a space

so we first find the position of the spaces:

```
secondbit=[[cipher_blocks[i][i2]>>6 & 1 for i in range(len(cipher_blocks))] for i2 in range(block_size)]
where_the_spaces_at=[]

print("secondbit")
for i in range(block_size):
    print("\tpos:",i)
    found=False
    for cycle in cycles:
        for startingpoint in range(len(cycle)):
            spaces=[]
            zeros=0
            for i2 in range(len(cipher_blocks)):
                if secondbit[i][i2]==cycle[(startingpoint+i2) % len(cycle)]:
                    zeros+=1
                    spaces.append(i2)
                    if zeros>800:
                        break
            if zeros<800:
                print("\t\tDONE")
                key[i]+=cycle[startingpoint]<<6
                where_the_spaces_at.append(set(spaces))
                found=True
                break
        if found:
            break
```

and then we use this to find the starting keys of the last two bits

```
sixthbit=[[cipher_blocks[i][i2]>>2 & 1 for i in range(len(cipher_blocks))] for i2 in range(block_size)]

print("sixthbit")
for i in range(block_size):
    print("\tpos:",i)
    found=False
    for cycle in cycles:
        for startingpoint in range(len(cycle)):
            errors=0
            for i2 in range(len(cipher_blocks)):
                if i2 in where_the_spaces_at[i]:
                    if sixthbit[i][i2]!=cycle[(startingpoint+i2) % len(cycle)]:
                        errors+=1
                        if errors>50:
                            break
            if errors<50:
                print("\t\tDONE")
                key[i]+=cycle[startingpoint]<<2
                found=True
                break
        if found:
            break
```

we take all the starting positions that we have found (that make up the key of the first block)
and we attempt to decrypt the message using this key

the method is euristic and there are some approximation here and there, so the key could be off by a couple bits,
but we can combine this with the fact the the first plaintext is made of real words so we can adjust it manually if we get words that are off by a few bits

finally we decrypt the whole ciphertext and we can read it all, including the flag

```
UlisseCTF{spinm3rightround'b4by'rightround}
```
