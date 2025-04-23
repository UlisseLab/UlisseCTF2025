# AWAWA

|         |                                   |
| ------- | --------------------------------- |
| Authors | Alessandro Orciari <@AleaStatica> |
| Points  | 500                               |
| Tags    | forensics                         |

## Challenge Description

My friend Marco went to Windhoek and took a lot of pictures. He told me that he saw a lot of animals, but one of them was really strange.

Among the antelopes, birds, and other wildlife, he spotted a small, round creature perched on a rock. It had short legs, tiny ears, and beady eyes that stared right at him. At first, he thought it was just an ordinary hyrax—until it opened its mouth and, instead of a typical chirp or squeak, it said:

**"AWAWA."**

Marco couldn’t believe his ears. A hyrax? Saying _that_? He quickly snapped a picture, but by the time he looked back, the little creature had vanished. To this day, he swears it really happened.

## Overview

The challenge is in the `forensic` category, so we can assume it is a steganography challenge.

The image provided shows a hyrax, which is a small mammal that lives in Africa and the Middle East.

## Intended Solution

```shell
> steghide extract -sf hyrax.jpg
Enter passphrase: <blank>
wrote extracted data to "Huh.wav".
```

Open the extracted file with a spectrogram viewer and you will see the flag.

![Flag spectrogram](writeup/audacity.png)

Tada!
