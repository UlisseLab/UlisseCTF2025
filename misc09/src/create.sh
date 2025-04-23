#!/bin/bash

IPFS="ipfs --api /dns/localhost/tcp/5002"
# IPFS="ipfs"

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
