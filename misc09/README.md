# Inter Pianura padana Forks and Spaghetti 🤌

|         |                     |
| ------- | ------------------- |
| Authors | Eyad Issa <@VaiTon> |
| Points  | 500                 |
| Tags    | misc,insanity       |

## Challenge Description

> _My grandma wove childhood tales like threads of golden light—of sunlit fields, secret ponds, and laughter in the trees—while the scent of homemade pasta, pizza, and tortellini filled her kitchen with warmth, and in quiet moments, she surprised us all, dancing through digital puzzles in Capture the Flag games with a mind as sharp as her heart was tender._

```text
bafkreiczv2pwgzj64zi2c7exevevnpvk7snuqyml75jqcdjqqe57jc5uhi
```

## Overview

A basic understanding of IPFS (or ChatGPT) was needed to recognize that the provided string is a Content Identifier (CID).

A Content Identifier is a unique identifier for a **block of data** in the IPFS ecosystem. [^1] CIDs are derived from the content’s cryptographic hash, such as SHA-256, Blake3, or other algorithms.

[^1]: https://docs.ipfs.tech/concepts/content-addressing/

The key point is that it doesn't specify where the content is stored, but rather creates an address based on the content itself.

From the [IPFS wiki](https://docs.ipfs.tech/):

> A Block is a binary blob of data identified by a CID. It could be raw bytes of arbitrary data or a chunk of serialized binary data encoded with IPLD codec.

In particular, files are rarely able to be stored in a single block, so they are divided into multiple blocks (which also aids in deduplication) and are stored using a protobuf structure that links each block together:

> The Unix File System (UnixFS) is the data format used to represent files and all their links and metadata in IPFS. It is loosely based on how files work in Unix. Adding a file to IPFS creates a block, or a tree of blocks, in the UnixFS format and protects it from being garbage-collected.

## Retrieving the data

The IPFS Foundation provides a public gateway at `ipfs.io`, which allows us to resolve CIDs and retrieve the data they point to. However, the data is not guaranteed to be available, as it depends on whether someone is hosting it.

For this challenge, I had to setup a node that serves the data and re-provides it to the network (via the global DHT, read more about it [here](https://docs.ipfs.tech/concepts/dht/)). This is done by running the following command:

```bash
#!/bin/bash

IPFS="ipfs"

echo "Adding file to IPFS"
cid=`$IPFS add --cid-version 1 ricetta.md | awk '{print $2}'`

echo "Recursive CID descend"
echo $cid > blocks.txt
for i in {1..100}; do
    cid=`echo $cid | $IPFS block put`
    echo $cid >> blocks.txt
    echo "Block $i added: $cid"
done

echo "Adding to pins"
$IPFS pin add < blocks.txt

echo "Announcing"
$IPFS routing provide -v < blocks.txt

echo $cid
```

The script above adds the file `ricetta.md` to IPFS and gets the CID of the file.

It then iterates 100 times, creating a new **raw block** each time containing the CID of the previous block.

The script also pins the blocks to ensure they are not garbage collected and announces them to the network.

## Solving the challenge

There are two ways to solve the challenge:

1. **Using a local IPFS node**: This is the **intended** way to solve the challenge (I wanted to make you learn about IPFS).
2. **Using the public IPFS gateway**: This is the **quick and dirty** way to solve the challenge, but it's not guaranteed to work, as the data may not be available on the public gateway or you may be rate limited or the serving node may not be reachable by the public gateway.

### Using the public IPFS gateway

The following code is a simple script that retrieves the initial CID content from the public IPFS gateway and then recursively retrieves the next CID until it reaches the end of the chain (= when the `res.status_code` is not 200).

```python
import requests

cid = "bafkreiczv2pwgzj64zi2c7exevevnpvk7snuqyml75jqcdjqqe57jc5uhi"

i = 0
while True:
    res = requests.get("https://ipfs.io/ipfs/" + cid)
    if res.status_code != 200:
        raise Exception(f"Failed to resolve IPFS CID: {cid}")

    cid = res.text.strip()
    print(f"Attempt {i}: {res.status_code} - {cid}")
    i += 1

```

### Using a local IPFS node

Before running the script you need to install IPFS and run a local node. You can do this by following the instructions on the [IPFS website](https://docs.ipfs.tech/getting-started/installation/).

Once you have a local node running, you can use the following script to retrieve the data:

```bash
cid="bafkreiczv2pwgzj64zi2c7exevevnpvk7snuqyml75jqcdjqqe57jc5uhi"

for i in {1..256}; do
    cid=`echo $cid | ipfs cat`
    echo "[$i] $cid"
done

ipfs get $(echo "$cid"  | awk '{print $2}')
```
