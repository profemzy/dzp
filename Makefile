.PHONY: help install dev test lint format clean run

# Default target
help:
	@echo "DZP IAC Agent - Available commands:"
	@echo ""
	@echo "  install     Install dependencies with uv"
	@echo "  dev         Install development dependencies"
	@echo "  run         Run the application"
	@echo "  test        Run tests"
	@echo "  lint        Run linting (ruff + mypy)"
	@echo "  format      Format code with black and ruff"
	@echo "  clean       Clean cache and build artifacts"
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