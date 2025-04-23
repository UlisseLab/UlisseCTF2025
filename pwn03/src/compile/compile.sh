#!/bin/sh

set -eu

D="$(cd "$(dirname $0)" ; pwd)"

FLAG="${FLAG:-$(cat "$D/../../flags.txt")}"
DOCKERNAME="${DOCKERNAME:-cheri_cheri_pwn_sdk}"

sudo docker build -t "$DOCKERNAME" .
sudo docker run --rm -ti -e FLAG="$FLAG" -v "$D/../..:/challenge" "$DOCKERNAME"
