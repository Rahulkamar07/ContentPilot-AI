.PHONY: setup dev test lint format migrate docker-up docker-down

setup:
	@echo "Installing backend dependencies..."
	cd backend && python -m pip install --upgrade pip && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm ci
	@echo "Installing pre-commit hooks..."
	pre-commit install

dev:
	@echo "Starting development docker services..."
	docker-compose up -d postgres redis

test:
	@echo "Running backend pytest suite..."
	cd backend && pytest

lint:
	@echo "Running backend linters..."
	cd backend && ruff check . && black --check . && isort --check-only . && mypy app
	@echo "Running frontend linter..."
	cd frontend && npm run lint

format:
	@echo "Formatting backend code..."
	cd backend && ruff check --fix . && black . && isort .
	@echo "Formatting frontend code..."
	cd frontend && npm run format

migrate:
	@echo "Executing Alembic database migrations..."
	cd backend && alembic upgrade head

docker-up:
	@echo "Building and launching container stack..."
	docker-compose up -d --build

docker-down:
	@echo "Stopping container stack..."
	docker-compose down -v
