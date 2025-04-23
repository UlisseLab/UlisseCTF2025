# Degarble

|         |                            |
| ------- | -------------------------- |
| Authors | Davide Gianessi <@gianetz> |
| Points  | 500                        |
| Tags    | crypto                     |

## Challenge Description

[Woow](https://www.youtube.com/watch?v=jkHc2-4cu4E&list=PLAwxTw4SYaPnCeih6BPvJ5GdqqThGcWlX&index=357), this stuff is craaazy!!

This is a remote challenge, you can connect using the client provided:

./client.py degarble.challs.ulisse.ovh 4456

## Overview

This challenge uses garbled circuits to allow the user to check if they guessed a secret, if they can guess, they get the key to an encrypted flag as the output of the circuit.

Garbled circuit are a technique of multiparty computation, which allow the partecipants to compute the output of a circuit without revealing the inputs to each other. The input(1 bit) are turned into labels(16 bytes), and the generator (the server) creates encrypted entries of the ouptut for each gate, which allow the verifier to get the output label of that gate, corresponding to the input labels that he has, without ever knowing if the labels they hold refer to the value 1 or 0.

the initial label of the generator are simply provided togheter with the circuit, while the input labels of the verifier are obtained through the oblivious transfer protocol:

![oblivious transfer protocol](writeup/ot.png)

In this case, the circuit looks like this

![the circuit](writeup/circuit.png)

which computes wheter the secret of the server is the same as the secret guessed

## Optimizations used by this implementation

To solve this challenge we can start by noticing that we are using the free xor optimization, where labels that corrispond to opposing values of the same input/output are obtained by xoring the other one with a value delta, which is the same for the entire circuit, allowing xor gates to be simple xor operations between the labels.

The delta value is usually generated new for each circuit but in this case it is used for all the circuit in the session, if we can leak this delta we can completely compromise the security of the circuit, we can figure out the secret by decrypting more than one entry for each gate or we can just get the output label corrisponding to 1 when we only have the one corrisponding to 0

The fixed key optimization is also used, it changes the encryption function to only do AES key expansion once, but it's not usefull for solving the challenge

## The mistake

In the oblivious transfer implementation we notice an error in the challenge values generation:

```python
def generate_ot_challenge_values():
    r=random.Random(datetime.now().microsecond % 1000)
    x0=r.randbytes(16)
    x1=r.randbytes(16)
    return x0+x1
```

this has only 1000 possible values, which means there will be collisions, we should keep track of these and use them to our advantage. to simplify the exploit let's always choose v=x0 without the blinding factor r
now the server will give us:

```
w0'=w0
w1'=w1+pow(x0-x1,d,n) (where w1= w0 xor delta)
```

if we know that x0-x1 is the same for two different labels A and B we can correlate them by doing

```
A_w1'-B_w1'= (A_w0 xor delta) - (B_w0 xor delta)
```

## Calculating delta

Now, for each bit, starting from the most significant we can figure out the delta bit by bit
if the i-th bit of A_w0 and B_w0 are the same, then the i-th bit of delta does not have any effect on the difference, as it cancels out, but if it is different:

we can define diff as:

diff= (A_w0 xor delta >> (i+1) ) - (B_w0 xor delta >> (i+1))

then when considering the i-ith bit of the subtraction

```
(diff)  (A_w0[i])-          10 -    10 -    11 -    11 -    00 -    01 -

        (B_w0[i])=           1 =     1 =     0 =     0 =     1 =     0 =

((A_w1'-B_w1')[i+1])(*)     0*      1*      0*      1*      0*      0*

 then delta[i] needs to be:  0       1       1       0       1       0
```

we are basically checking if the (i+1)-ith bit needs to borrow a 1 to be correct and adjusting delta[i] accordingly

the following expression is the equivalent of this

```
( (A_w0 xor delta >> (i+1) ) - (B_w0 xor delta >> (i+1)) - ((A_w1'-B_w1') >> (i+1)) ) xor (B_w0>>i & 1)
```

We can calculate this because we already have found all the bits of delta more significant than i
if the i-th bit of A_w0 and B_w0 are the same then this gives us no info on delta, for this reason we should keep track of all the collision that happen and for each bit, iterate through them until we find one where that bit is different,
by generating 10 circuit we almost surely get enough collisions to do that

## Getting the flag

Once that the delta is leaked, we can xor it with the output label and get the output label of corrisponding to a guessed secret, which is the key to the flag, we decrypt it and we get

```
UlisseCTF{G4r8L3d_5TuFF_Is_C00l}
```

## Full script (adapted from provided client)

```python
#!/usr/bin/python3
from pwn import *
from base64 import b64encode,b64decode
import random
from Crypto.Util.number import long_to_bytes,bytes_to_long
from Crypto.Util.Padding import pad,unpad
from Crypto.Cipher import AES
from hashlib import sha256

#context.log_level = 'debug'
HOST = 'localhost'
PORT = 12345
p = remote(HOST,PORT)

n=int(p.recvline().decode())
e=65537
fixed_key = b64decode(p.recvline())
cipher=AES.new(fixed_key,AES.MODE_ECB)

secret_size=32

def xor_labels(label1, label2):
    return bytes(a ^ b for a, b in zip(label1,label2))

def get_gate_key(label1,label2):
    label1=label1[::-1]
    return ((int.from_bytes(label1, 'big') + int.from_bytes(label2, 'big')) % (2**128)).to_bytes(16, 'big')

def decrypt(key, encrypted_output):
    encrypted_label = encrypted_output[:-4]
    checksum = encrypted_output[-4:]
    decrypted_label = xor_labels(cipher.encrypt(key),encrypted_label)
    #print(f"{key}, {decrypted_label}, {xor_labels(key,decrypted_label)}, {checksum}")
    if xor_labels(key, decrypted_label)[:4] != checksum:
        return b""
    return decrypted_label

def evaluate_garbled_circuit(labels,and_gates,num_inputs):
    xor_outputs = [xor_labels(labels[i], labels[num_inputs//2+i]) for i in range(num_inputs//2)]
    current_label = xor_outputs[0]
    for i in range(1,len(xor_outputs)):
        #print(f"{i}: {current_label}")
        next_label=b""
        key=get_gate_key(current_label,xor_outputs[i])
        for entry in and_gates[i-1]:
            next_label+=decrypt(key,entry)
        current_label=next_label
    #print(f"final: {current_label}")
    return current_label

all_challenges=[]
all_w0=[]
all_w1=[]
final_output=b""
enc_flag=b""

for i in range(10):
    p.sendline(b"start")
    and_gates = b64decode(p.recvline())
    and_gates = [and_gates[i:i+20] for i in range(0,len(and_gates),20)]
    and_gates = [and_gates[i:i+4] for i in range(0,len(and_gates),4)]
    server_labels = b64decode(p.recvline())
    server_labels = [server_labels[i:i+16] for i in range(0,len(server_labels),16)]
    challenges = b64decode(p.recvline())
    challenges = [challenges[i:i+32] for i in range(0,len(challenges),32)]

    all_challenges+=challenges



    rs=[random.getrandbits(128) for i in range(len(challenges))]
    print("guess the secret: (32bit hex)")
    #guess=bytes_to_long(bytes.fromhex(input()))
    guess=bytes_to_long(os.urandom(4))
    vs=[]
    for i in range(len(challenges)):
        v=bytes_to_long(challenges[i][:16])
        vs.append(v)
    for v in vs:
        p.sendline(str(v).encode())
    mylabels=[]
    for i in range(len(challenges)):
        w0=int(p.recvline().decode())
        w1=int(p.recvline().decode())
        all_w0.append(w0)
        all_w1.append(w1)
        mylabel=long_to_bytes(w0)
        mylabel= b"\x00"*(16-len(mylabel))+mylabel
        mylabels.append(mylabel)
    labels=server_labels+mylabels
    output_label=evaluate_garbled_circuit(labels,and_gates,secret_size*2)
    final_output=output_label
    hash0=p.recvline().decode().strip()
    hash1=p.recvline().decode().strip()
    flag=b64decode(p.recvline().strip())
    enc_flag=flag
    if(sha256(output_label).hexdigest() == hash0):
        print("wrong secret")
    elif(sha256(output_label).hexdigest() == hash1):
        print("correct secret")
        print(unpad(AES.new(output_label,AES.MODE_ECB).decrypt(flag),16).decode())
    else:
        print("something went wrong")

aas=[]
bbs= []
ccs= []
reference_w0={}
reference_w1={}

for i in range(len(all_challenges)):
    if all_challenges[i] not in reference_w0:
        reference_w0[all_challenges[i]]=all_w0[i]
        reference_w1[all_challenges[i]]=all_w1[i]
    else:
        if reference_w1[all_challenges[i]]>all_w1[i]:
            aas.append(reference_w1[all_challenges[i]]-all_w1[i])
            bbs.append(reference_w0[all_challenges[i]])
            ccs.append(all_w0[i])
        else:
            aas.append(all_w1[i]-reference_w1[all_challenges[i]])
            bbs.append(all_w0[i])
            ccs.append(reference_w0[all_challenges[i]])

## a = (b ^ delta)-(c ^ delta)
print(aas)
print(bbs)
print(ccs)

delta=0
finding=127

while finding>=0:
    failure=True
    for i in range(len(aas)):
        if bbs[i]&(2**finding) != ccs[i]&(2**finding):
            failure=False

            delta+=( (((bbs[i]^delta)>>(finding+1)) - ((ccs[i]^delta)>>(finding+1)) - ((aas[i])>>(finding+1))) ^ ((ccs[i]>>finding)&1) )<<finding
            break
    if failure:
        print("failure, retry with more collisions")
        exit()
    print("finding:",finding,"\t",bin(delta))
    finding-=1

print(delta)
delta=long_to_bytes(delta)
delta= b"\x00"*(16-len(delta))+delta
good_ending=xor_labels(final_output,delta)
print(unpad(AES.new(good_ending,AES.MODE_ECB).decrypt(flag),16).decode())

```
