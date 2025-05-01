COMPOSE := docker compose
PWD := $(shell pwd)

up: 
	$(COMPOSE) up -d
down:
	$(COMPOSE) down
chall:
	tar -czvf challenge.tar.gz server.py client.py startserver.sh
	mv challenge.tar.gz $(PWD)/../attachments/challenge.tar.gz
clean:	down
	rm -f $(PWD)/../attachments/challenge.tar.gz
