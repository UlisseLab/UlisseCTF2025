#!/bin/env python3

import os
import random
from Crypto.Cipher import AES
from Crypto.Util.number import getPrime, bytes_to_long
from Crypto.Util.Padding import pad, unpad
from datetime import datetime
from base64 import b64encode, b64decode
from hashlib import sha256

FLAG = os.environ.get("FLAG", "UlisseCTF{fakeflag}")

secret_size = 32
secret_value = os.urandom(secret_size // 8)
secret_value = bytes_to_long(secret_value)


def random_label():
    return os.urandom(16)


delta = random_label()
p, q = getPrime(512), getPrime(512)
n = p * q
phi = (p - 1) * (q - 1)
e = 65537
d = pow(e, -1, phi)

print(n)

fixed_key = os.urandom(16)
cipher = AES.new(fixed_key, AES.MODE_ECB)
print(b64encode(fixed_key).decode())


def xor_labels(label1, label2):
    return bytes(a ^ b for a, b in zip(label1, label2))


def get_gate_key(label1, label2):
    label1 = label1[::-1]
    return (
        (int.from_bytes(label1, "big") + int.from_bytes(label2, "big")) % (2**128)
    ).to_bytes(16, "big")


def encrypt(key, value):
    encrypted_output = xor_labels(cipher.encrypt(key), value)
    checksum = xor_labels(key, value)[:4]
    return encrypted_output + checksum


def generate_labels(num_inputs):
    labels = [(random_label(), None) for _ in range(num_inputs)]
    labels = [(L0, xor_labels(L0, delta)) for L0, _ in labels]
    return labels


def garble_and_gate(LA0, LA1, LB0, LB1, LO0, LO1):
    quadruple = []
    for a in [0, 1]:
        for b in [0, 1]:
            key = get_gate_key(LA0 if a == 0 else LA1, LB0 if b == 0 else LB1)
            value = LO0 if (a & b) == 0 else LO1
            ciphertext = encrypt(key, value)
            quadruple.append(ciphertext)
    random.shuffle(quadruple)
    return quadruple


def garble_circuit(num_inputs):
    labels = generate_labels(num_inputs)
    #we are using the free-xor optimization
    xor_outputs = [
        xor_labels(labels[i][0], labels[num_inputs // 2 + i][0])
        for i in range(num_inputs // 2)
    ]
    and_gates = []
    current_label = xor_outputs[0]
    for i in range(1, len(xor_outputs)):
        next_label = random_label()
        and_gate = garble_and_gate(
            current_label,
            xor_labels(current_label, delta),
            xor_outputs[i],
            xor_labels(xor_outputs[i], delta),
            next_label,
            xor_labels(next_label, delta),
        )
        and_gates.append(and_gate)
        current_label = next_label
    return labels, and_gates, current_label


def generate_ot_challenge_values():
    r = random.Random(datetime.now().microsecond % 1000)
    x0 = r.randbytes(16)
    x1 = r.randbytes(16)
    return x0 + x1


def ot(challenge, label, v):
    x0 = bytes_to_long(challenge[:16])
    x1 = bytes_to_long(challenge[16:])
    k0 = pow(v - x0, d, n)
    k1 = pow(v - x1, d, n)
    w0 = bytes_to_long(label[0]) + k0
    w1 = bytes_to_long(label[1]) + k1
    return (w0, w1)


for guess in range(10):
    start = input()
    if start != "start":
        exit()
    labels, and_gates, output_label = garble_circuit(secret_size * 2)
    concatenated = b"".join(item for sublist in and_gates for item in sublist)
    print(b64encode(concatenated).decode())
    mylabels = [
        labels[i][0] if secret_value & (1 << i) else labels[i][1]
        for i in range(secret_size)
    ]  # this input is negated!!
    concatenated = b"".join(mylabels)
    print(b64encode(concatenated).decode())
    challenges = [generate_ot_challenge_values() for i in range(secret_size)]
    concatenated = b"".join(challenges)
    print(b64encode(concatenated).decode())
    vs = []
    for i in range(secret_size):
        vs.append(int(input()))
    ws = [ot(challenges[i], labels[secret_size + i], vs[i]) for i in range(secret_size)]
    for w0, w1 in ws:
        print(w0)
        print(w1)
    print(sha256(output_label).hexdigest())
    print(sha256(xor_labels(output_label, delta)).hexdigest())
    print(
        b64encode(
            AES.new(xor_labels(output_label, delta), AES.MODE_ECB).encrypt(
                pad(FLAG.encode(), 16)
            )
        ).decode()
    )
