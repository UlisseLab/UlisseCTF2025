COMPOSE := docker compose
PWD := $(shell pwd)

up:
	$(COMPOSE) up -d
down:
	$(COMPOSE) down
chall:
	cp challenge.c $(PWD)/../attachments/challenge.c
clean:	down
	rm -f $(PWD)/../attachments/challenge.c
