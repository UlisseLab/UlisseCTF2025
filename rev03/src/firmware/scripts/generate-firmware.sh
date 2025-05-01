#!/bin/sh

FLAG="$FLAG"
D="$(cd $(dirname $0) ; pwd)"

generate_c_array() {
	echo -n "{ "
	xxd -c 1000 -ps "$1" | sed 's/\(..\)/0x\1, /g' | tr -d '\n'
	echo "}"
}

generate_random_key() {
	dd if=/dev/urandom of=/tmp/key16 bs=1 count=16 2>/dev/null
	cp /tmp/key16 /tmp/key32
	truncate -s 32 /tmp/key32
	generate_c_array /tmp/key32
}

generate_random_iv() {
	dd if=/dev/urandom of=/tmp/iv bs=1 count=12 2>/dev/null
	generate_c_array /tmp/iv
}

encrypt_flag() {
	echo "$FLAG" > /tmp/flag.txt
	~/.nvm/versions/node/*/bin/node "$D/aes.js" encrypt /tmp/key16 /tmp/iv /tmp/flag.txt /tmp/ciphertext /tmp/tag
}

KEY="$(generate_random_key)"
IV="$(generate_random_iv)"

encrypt_flag
cat >"$D/../src/secrets.h" <<_END_
#ifndef _SECRETS
#define _SECRETS
#define SECRET_KEY $KEY
#define SECRET_IV $IV
//$(encrypt_flag)
#define SECRET_TAG $(generate_c_array /tmp/tag)
#define SECRET_FLAG $(generate_c_array /tmp/ciphertext)
#define SECRET_FLAG_LEN $(wc -c /tmp/ciphertext | awk '{print $1}')
#endif /* _SECRETS */
_END_

west build --board esp32_devkitc_wroom/esp32/procpu --sysbuild "$D/../"
