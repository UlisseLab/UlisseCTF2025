#!/bin/env python3

import sys
import subprocess
import json

MORSE_CODE_DICT = {
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
    "-----": "0",
    "--..--": ", ",
    ".-.-.-": ".",
    "..--..": "?",
    "-..-.": "/",
    "-....-": "-",
    "-.--.": "(",
    "-.--.-": ")",
}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <pcap>")
        sys.exit(1)

    input_path = sys.argv[1]

    times = (
        subprocess.check_output(
            f"tshark -r {input_path} -Y http -T fields -e frame.time_epoch",
            shell=True,
        )
        .decode()
        .split("\n")
    )

    json_lines = (
        subprocess.check_output(
            f"tshark -r {input_path} -Y json -T fields -e http.file_data | xxd -r -p | jq -c",
            shell=True,
        )
        .decode()
        .split("\n")
    )

    flag = ""
    word = ""

    last_time = -1

    for i in range(len(times)):
        if not json_lines[i]:
            continue

        line = json_lines[i]
        time = float(times[i])

        pkt = json.loads(line)

        payload = pkt["payload"]

        if "togglex" not in payload:
            continue

        if last_time != -1 and time - last_time > 2:
            # end of word
            flag += MORSE_CODE_DICT[word]
            word = ""

        last_time = time

        onoff = payload["togglex"]["onoff"]
        if onoff == 1:
            word += "."
        else:
            word += "-"

    flag += MORSE_CODE_DICT[word]
    print(f"Flag: UlisseCTF{{{flag}}}")
