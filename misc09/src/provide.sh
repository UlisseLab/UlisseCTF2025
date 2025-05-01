#!/bin/sh
IPFS="ipfs --api /dns/localhost/tcp/5002"

$IPFS routing provide -v $1
