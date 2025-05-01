#!/bin/sh

set -eu

D="$(
    cd "$(dirname $0)"
    pwd
)"

FLAG="${FLAG:-$(cat "$D/../flags.txt")}"
DOCKERNAME="${DOCKERNAME:-xtensaible_kite}"

docker build -t "$DOCKERNAME" .
docker run --rm -ti -e FLAG="$FLAG" -v "$D/..:/challenge" "$DOCKERNAME"
