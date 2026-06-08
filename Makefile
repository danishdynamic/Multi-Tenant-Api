# SaaS Backend Development Makefile

.PHONY: help install dev up down build logs clean test lint format

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

dev: ## Start development server
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker: ## Start background worker
	python run_worker.py

up: ## Start all Docker services
	docker-compose up -d

down: ## Stop all Docker services
	docker-compose down

build: ## Build Docker images
	docker-compose build

logs: ## View Docker logs
	docker-compose logs -f

logs-api: ## View API logs only
	docker-compose logs -f api

logs-worker: ## View worker logs only
	docker-compose logs -f worker

clean: ## Clean up Docker containers and volumes
	docker-compose down -v
	docker system prune -f

test: ## Run tests
	pytest app/tests/ -v --asyncio-mode=auto

lint: ## Run linting
	flake8 app/ --max-line-length=100

format: ## Format code with black
	black app/

check: ## Run type checking
	mypy app/

shell: ## Open shell in API container
	docker-compose exec api bash

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d saas_analytics_db

redis-shell: ## Open Redis shell
	docker-compose exec redis redis-cli

rabbit-shell: ## Open RabbitMQ shell
	docker-compose exec rabbitmq rabbitmqctl status

health: ## Check API health
	curl http://localhost:8000/api/v1/health/

docs: ## Open API documentation
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Alternative Docs: http://localhost:8000/redoc"