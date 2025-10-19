.PHONY: help install dev test lint format clean run docker-build docker-up docker-down docker-logs docker-ps docker-clean docker-test

# Default target
help:
	@echo "DZP IAC Agent - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     Install dependencies with uv"
	@echo "  dev         Install development dependencies"
	@echo "  run         Run the application"
	@echo "  test        Run tests"
	@echo "  lint        Run linting (ruff + mypy)"
	@echo "  format      Format code with black and ruff"
	@echo "  clean       Clean cache and build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build       Build Docker images"
	@echo "  docker-up          Start all services"
	@echo "  docker-up-ollama   Start with Ollama"
	@echo "  docker-down        Stop all services"
	@echo "  docker-restart     Restart services"
	@echo "  docker-logs        View logs"
	@echo "  docker-ps          Show containers"
	@echo "  docker-clean       Remove everything"
	@echo "  docker-test        Test deployment"
	@echo ""
	@echo "  help        Show this help message"

# Install dependencies
install:
	uv sync

# Install development dependencies
dev:
	uv sync --dev

# Run the application
run:
	uv run main.py

# Run tests
test:
	uv run pytest

# Run linting
lint:
	uv run ruff check src/ main.py
	uv run mypy src/

# Format code
format:
	uv run black src/ main.py
	uv run ruff check --fix src/ main.py

# Clean up
clean:
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Development setup (one-time)
setup-dev:
	@echo "Setting up development environment..."
	uv sync --dev
	@echo "Development environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Copy .env.example to .env and configure your API key"
	@echo "2. Run 'make run' to start the application"
	@echo "3. Run 'make test' to run tests"

#===========================================
# Docker Commands
#===========================================

# Build Docker images
docker-build:
	@echo "🔨 Building Docker images..."
	docker-compose build

docker-build-no-cache:
	@echo "🔨 Building Docker images (no cache)..."
	docker-compose build --no-cache

# Start services
docker-up:
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "📍 Web Interface: http://localhost:8080"
	@echo "📍 API Server: http://localhost:8000"

docker-up-ollama:
	@echo "🚀 Starting services with Ollama..."
	docker-compose --profile with-ollama up -d
	@echo "✅ Services started!"
	@echo "📍 Web Interface: http://localhost:8080"
	@echo "📍 API Server: http://localhost:8000"
	@echo "📍 Ollama: http://localhost:11434"

# Stop services
docker-down:
	@echo "🛑 Stopping services..."
	docker-compose down

docker-down-volumes:
	@echo "🛑 Stopping services and removing volumes..."
	docker-compose down -v

# Restart services
docker-restart:
	@echo "🔄 Restarting services..."
	docker-compose restart

# View logs
docker-logs:
	docker-compose logs -f

docker-logs-web:
	docker-compose logs -f web

docker-logs-api:
	docker-compose logs -f api

# Show containers
docker-ps:
	docker-compose ps

# Clean up
docker-clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v --rmi all
	@echo "✅ Cleanup complete!"

# Test deployment
docker-test:
	@echo "🧪 Testing Docker deployment..."
	@sleep 5
	@curl -sf http://localhost:8080/api/health > /dev/null && echo "✅ Web interface healthy" || echo "❌ Web interface failed"
	@curl -sf http://localhost:8000/health > /dev/null && echo "✅ API server healthy" || echo "❌ API server failed"

# Shell access
docker-shell-web:
	docker-compose exec web bash

docker-shell-api:
	docker-compose exec api bash

# Initialize Docker setup
docker-init:
	@echo "🎬 Initializing Docker setup..."
	@if [ ! -f .env ]; then cp .env.docker .env; echo "📝 Created .env file"; fi
	@mkdir -p terraform backups
	@echo "✅ Docker initialization complete!"
	@echo "Edit .env and run: make docker-up"