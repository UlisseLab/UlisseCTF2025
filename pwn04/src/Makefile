GCC := gcc
COMPOSE := docker compose
PWD := $(shell pwd)

up: compile
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

compile:
	$(GCC) oracle.c -o oracle

chall: compile
	zip -r oracle.zip oracle libs
	mv oracle.zip $(PWD)/../attachments/oracle.zip
clean: down
	rm -f oracle
