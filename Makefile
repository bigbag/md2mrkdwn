.PHONY: help install test lint format clean

PROJECT_NAME = md2mrkdwn
LINT_PATHS = src tests

.DEFAULT_GOAL := help

## Install all dependencies
install:
	@echo "Installing dependencies..."
	uv sync --all-groups
	@echo "Done"

## Run tests with coverage
test:
	@echo "Running tests..."
	uv run pytest --cov=md2mrkdwn --cov-report=term-missing
	@echo "Done"

## Run linters (ruff + mypy)
lint:
	@echo "Checking code style with ruff..."
	uv run ruff format --check $(LINT_PATHS)
	uv run ruff check $(LINT_PATHS)
	@echo "Type checking with mypy..."
	uv run mypy src/$(PROJECT_NAME)
	@echo "Done"

## Format code with ruff
format:
	@echo "Formatting code..."
	uv run ruff format $(LINT_PATHS)
	uv run ruff check --fix $(LINT_PATHS)
	@echo "Done"

## Clean cache and build files
clean:
	@echo "Cleaning..."
	rm -rf .mypy_cache .pytest_cache .ruff_cache .coverage htmlcov dist build
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Done"

## Show available commands
help:
	@echo "Available commands:"
	@echo "  make install  - Install all dependencies"
	@echo "  make test     - Run tests with coverage"
	@echo "  make lint     - Run linters (ruff + mypy)"
	@echo "  make format   - Format code with ruff"
	@echo "  make clean    - Clean cache and build files"
