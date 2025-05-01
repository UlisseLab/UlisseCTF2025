include .env
all: challenge dev

NAME=picasso
SRC=chall

gen:
	env FLAG=$(FLAG) python3 scripts/gen_bitmap.py src/flag.h

challenge: gen
	gcc src/$(SRC).c --include-directory=/usr/include/libdrm -ldrm -s -o bin/$(NAME)
dev: gen
	gcc src/$(SRC).c --include-directory=/usr/include/libdrm -ldrm -DDEV -o bin/$(NAME)-dev

deploy: challenge
	cp bin/$(NAME) ../attachments/
	echo $(FLAG) > ../flags.txt
