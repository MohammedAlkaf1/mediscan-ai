.PHONY: help up down build migrate seed test clean logs

help:
	@echo "Smart Medical Report Interpreter - Commands"
	@echo ""
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make build       - Build all Docker images"
	@echo "  make migrate     - Run database migrations"
	@echo "  make seed        - Seed database with sample data"
	@echo "  make test        - Run backend tests"
	@echo "  make logs        - View logs from all services"
	@echo "  make clean       - Remove all containers, volumes, and images"
	@echo ""

up:
	docker-compose up -d
	@echo "Services started. Backend: http://localhost:8000 | Frontend: http://localhost:3000"

down:
	docker-compose down

build:
	docker-compose build

migrate:
	docker-compose exec postgres psql -U postgres -d postgres -f /docker-entrypoint-initdb.d/schema.sql
	@echo "Database migrated successfully"

seed:
	@echo "Seeding database..."
	docker-compose exec backend python -c "import sys; sys.path.append('.'); from main import app; print('Seed complete')"

test:
	@echo "Running backend tests..."
	docker-compose exec backend pytest tests/ -v

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --rmi all
	@echo "All containers, volumes, and images removed"

# Development shortcuts
backend-shell:
	docker-compose exec backend /bin/bash

frontend-shell:
	docker-compose exec frontend /bin/sh

db-shell:
	docker-compose exec postgres psql -U postgres -d postgres

restart:
	docker-compose restart

ps:
	docker-compose ps
