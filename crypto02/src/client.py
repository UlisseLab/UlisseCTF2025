#!/bin/env python3

from pwn import *
from base64 import b64encode, b64decode
import random
from Crypto.Util.number import long_to_bytes, bytes_to_long
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from hashlib import sha256
import sys

if len(sys.argv)!=3:
    print(f"usage:\n{sys.argv[0]} HOST PORT")
    exit()

HOST=sys.argv[1]
PORT=int(sys.argv[2])

p = remote(HOST, PORT)

secret_size = 32

n = int(p.recvline().decode())
e = 65537
fixed_key = b64decode(p.recvline())
cipher = AES.new(fixed_key, AES.MODE_ECB)


def xor_labels(label1, label2):
    return bytes(a ^ b for a, b in zip(label1, label2))


def get_gate_key(label1, label2):
    label1 = label1[::-1]
    return (
        (int.from_bytes(label1, "big") + int.from_bytes(label2, "big")) % (2**128)
    ).to_bytes(16, "big")


def decrypt(key, encrypted_output):
    encrypted_label = encrypted_output[:-4]
    checksum = encrypted_output[-4:]
    decrypted_label = xor_labels(cipher.encrypt(key), encrypted_label)
    if xor_labels(key, decrypted_label)[:4] != checksum:
        return b""
    return decrypted_label


def evaluate_garbled_circuit(labels, and_gates, num_inputs):
    xor_outputs = [
        xor_labels(labels[i], labels[num_inputs // 2 + i])
        for i in range(num_inputs // 2)
    ]
    current_label = xor_outputs[0]
    for i in range(1, len(xor_outputs)):
        next_label = b""
        key = get_gate_key(current_label, xor_outputs[i])
        for entry in and_gates[i - 1]:
            next_label += decrypt(key, entry)
        current_label = next_label
    return current_label


for guess in range(10):
    p.sendline(b"start")
    and_gates = b64decode(p.recvline())
    and_gates = [and_gates[i : i + 20] for i in range(0, len(and_gates), 20)]
    and_gates = [and_gates[i : i + 4] for i in range(0, len(and_gates), 4)]
    server_labels = b64decode(p.recvline())
    server_labels = [
        server_labels[i : i + 16] for i in range(0, len(server_labels), 16)
    ]
    challenges = b64decode(p.recvline())
    challenges = [challenges[i : i + 32] for i in range(0, len(challenges), 32)]
    rs = [random.getrandbits(128) for i in range(len(challenges))]
    print("guess the secret: (32bit hex)")
    guess = bytes_to_long(bytes.fromhex(input()))
    vs = []
    for i in range(len(challenges)):
        xb = b""
        if guess & (1 << i):
            xb = challenges[i][16:]
        else:
            xb = challenges[i][:16]
        xb = bytes_to_long(xb)
        v = pow(rs[i], e, n) + xb
        vs.append(v)
    for v in vs:
        p.sendline(str(v).encode())
    mylabels = []
    for i in range(len(challenges)):
        w0 = int(p.recvline().decode())
        w1 = int(p.recvline().decode())
        if guess & (1 << i):
            mylabel = long_to_bytes(w1 - rs[i])
        else:
            mylabel = long_to_bytes(w0 - rs[i])
        mylabel = b"\x00" * (16 - len(mylabel)) + mylabel
        mylabels.append(mylabel)
    labels = server_labels + mylabels
    output_label = evaluate_garbled_circuit(labels, and_gates, secret_size * 2)
    hash0 = p.recvline().decode().strip()
    hash1 = p.recvline().decode().strip()
    flag = b64decode(p.recvline().strip())
    if sha256(output_label).hexdigest() == hash0:
        print("wrong secret")
    elif sha256(output_label).hexdigest() == hash1:
        print("correct secret")
        print(unpad(AES.new(output_label, AES.MODE_ECB).decrypt(flag), 16).decode())
    else:
        print("something went wrong")
print("that's enough guesses for today, better luck next time")
