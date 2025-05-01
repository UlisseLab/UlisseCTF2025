COMPOSE := docker compose

up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

chall:
	cp docker-compose.yml docker-compose.yml.bak
	sed -i 's/UlisseCTF{.*}/UlisseCTF{REDACTED}/g' docker-compose.yml
	zip -r telemetry.zip docker-compose.yml requirements.txt Dockerfile app
	mv telemetry.zip $(PWD)/../attachments/telemetry.zip