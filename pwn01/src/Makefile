ZIG := zig
COMPOSE := docker-compose

.PHONY: attachments
attachments: chall
	cp chall ../attachments/zigzagzoogle

.PHONY: up
up: chall
	$(COMPOSE) up -d

.PHONY: down
down:
	$(COMPOSE) down

chall:
	$(ZIG) build-exe chall.zig -O ReleaseFast

.PHONY: clean
clean:
	rm -f chall.o chall
