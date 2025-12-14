.PHONY: install dev test lint format clean build help

help:
	@echo "ReconPilot Development Commands:"
	@echo "  make install    - Install package in production mode"
	@echo "  make dev        - Install package in development mode with dev dependencies"
	@echo "  make test       - Run tests with pytest"
	@echo "  make lint       - Run linting with ruff"
	@echo "  make format     - Format code with ruff"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make build      - Build package"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	ruff check reconpilot/ tests/

format:
	ruff format reconpilot/ tests/
	ruff check --fix reconpilot/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	python -m build
