# Internet of Lighthouses

|         |                     |
| ------- | ------------------- |
| Authors | Eyad Issa <@VaiTon> |
| Points  | 500                 |
| Tags    | forensics,network   |

## Challenge Description

My friend Guglielmo Del Nemico was challenged with keeping the Bologna Lighthouse running.

Although Bologna has no sea, he was determined to keep the lighthouse running and up to date, so he installed a new system to control the lighthouse remotely.

I managed to intercept some of the data exchanged between the lighthouse and the control system, but I can't make sense of it. Could you help me?

**Attention!** The flag is not in the usual format. Please submit the flag in the format `UlisseCTF{FLAG}`.

## Overview

The challenge provides a pcap file containing network traffic between the lighthouse and the control system. The goal is to extract the flag from the traffic.

## PCAP analysis

We can see that the traffic has a consistent pattern, and is made of JSON over HTTP requests.

Requests made to the `/config` endpoint seems to be used to configure the "lighthouse" with various parameters. The only relevant property we can see is the `payload.togglex.onoff` property, that can be either 1 or 0.

We can try to extract something meaningful out of it:

```shell
tshark -r forensic02/attachments/help.pcap -Y json -T fields -e http.file_data | xxd -r -p | jq '.payload.togglex.onoff' -c
```

We get a sequence of 1s and 0s and a lot of null values. To work with this data, let's switch to Python and use the `json` module to parse the data.

## Flag extraction

```python
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
```
