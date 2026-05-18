COMPOSE_FILE=docker-compose.yml

.PHONY: help build up down restart logs clean

help:
	@echo "Available targets:"
	@echo "  make build      Build all infrastructure images"
	@echo "  make up         Start the stack in attached mode"
	@echo "  make down       Stop the stack and remove containers"
	@echo "  make restart    Recreate containers from current images"
	@echo "  make logs       Stream logs for the stack"
	@echo "  make clean      Remove containers, networks, and volumes"

build:
	docker compose -f $(COMPOSE_FILE) build

up:
	docker compose -f $(COMPOSE_FILE) up

down:
	docker compose -f $(COMPOSE_FILE) down

restart:
	docker compose -f $(COMPOSE_FILE) down && \
	docker compose -f $(COMPOSE_FILE) up

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

clean:
	docker compose -f $(COMPOSE_FILE) down -v --remove-orphans
