#!/usr/bin/env python3

# This scripts takes a flag from the environment variables and sends it in morse code to a Home Assistant entity.
# The entity is a switch that will be turned on and off to represent the dots and dashes of the morse code.
# The flag is sent in morse code with a 5 second delay between each letter.
#
# To work, the following environment variables must be set:
# - FLAG:      the flag to send
# - TOKEN:     the Home Assistant API token
# - ENTITY_ID: the entity ID of the switch to control


import os
import requests
import time

FLAG = os.environ.get("FLAG")
TOKEN = os.environ.get("TOKEN")
ENTITY_ID = os.environ.get("ENTITY_ID")

if not FLAG:
    raise ValueError("Please set the FLAG environment variable")
if not TOKEN:
    raise ValueError("Please set the TOKEN environment variable")
if not ENTITY_ID:
    raise ValueError("Please set the ENTITY_ID environment variable")

headers = {"Authorization": "Bearer " + TOKEN}
data = {"entity_id": ENTITY_ID}


def switch(on=True):
    if on:
        url = "http://localhost:8123/api/services/switch/turn_on"
    else:
        url = "http://localhost:8123/api/services/switch/turn_off"

    res = requests.post(url, headers=headers, json=data)
    res.raise_for_status()


MORSE_CODE_DICT = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
    ", ": "--..--",
    ".": ".-.-.-",
    "?": "..--..",
    "/": "-..-.",
    "-": "-....-",
    "(": "-.--.",
    ")": "-.--.-",
}

if __name__ == "__main__":
    print(f"Flag: {FLAG}")

    morse_flag = [MORSE_CODE_DICT[c] for c in FLAG]
    print(f"Morse: {morse_flag}")

    for word in morse_flag:
        for c in word:
            if c == ".":
                switch(on=True)
            else:
                switch(on=False)

        time.sleep(5)
