COMPOSE := docker compose
PWD := $(shell pwd)

up:
	$(COMPOSE) up --build
down:
	$(COMPOSE) down
chall:
	mkdir chall
	cp .env chall/.env
	sed -Ei 's/^(.*=).*/\1REDACTED/' chall/.env
	cp docker-compose.yml chall/docker-compose.yml
	sed -Ei 's/UlisseCTF\{.*\}/UlisseCTF{REDACTED}/g' chall/docker-compose.yml
	cp -r config chall/config
	mkdir chall/backend
	cp backend/libackend.so backend/*.py backend/Dockerfile backend/requirements.txt chall/backend/
	cp -r frontend chall
	zip -r ../attachments/stackbank.zip chall
	rm -rf chall
clean: down
	rm -rf frontend/node_modules/ frontend/.next/
