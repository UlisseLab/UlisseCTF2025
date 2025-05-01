# POV

|         |                          |
| ------- | ------------------------ |
| Authors | Filippo Nardon <@ufilme> |
| Points  | 500                      |
| Tags    | misc                     |

## Challenge Description

I recently purchased this monitor from faceb00c marketplace.

It is displaying a static noise signal that appears to be frozen.

Can you help me figure out what's going on?

_Note: DOS is not required to complete the challenge._

Website: [http://pov.challs.ulisse.ovh:8888](http://pov.challs.ulisse.ovh:8888)

## Intended Solution

Open the website and analyze the requests made. One of the requests is to the following endpoint:

```text
/api/stream
```

The response is a stream of bytes producing an image.

By refreshing we can see the image changing.

In the request we can see an unusual header:

```http
Index: n of 60
```

This header is used to request a specific frame of the image.

By changing the index we can see the image changing.

Write a script to download all the frames (respecting the rate limiter) and \
use them to create a video for example using ffmpeg:

```shell
ffmpeg -framerate 60 -i image%d.png -t 10 -filter:v "format=yuv420p,loop=loop=-1:size=60" output.mp4
```

The video will show the flag.

## Unintended Solution

You could also download multiple images and then operate a pixel per pixel XOR on them to get the flag.

This works because the pixels that "move" are the ones that are not the flag, and the pixels that are the same are the ones that are the flag. The XOR of the same pixel is 0, and the XOR of different pixels is 1, so you get black for the flag and white for the rest.
