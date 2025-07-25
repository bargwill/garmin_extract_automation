# Garmin Extract Automation - Development Makefile

.PHONY: help install test lint format clean docs check-deps

help:  ## Show this help message
	@echo "Garmin Extract Automation - Development Commands"
	@echo "================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -e .

test:  ## Run all tests
	pytest

test-cov:  ## Run tests with coverage report
	pytest --cov=. --cov-report=html --cov-report=term

test-fast:  ## Run tests without slow markers
	pytest -m "not slow"

lint:  ## Run all linting checks
	flake8 .
	pylint **/*.py --exit-zero
	black --check --diff .
	isort --check-only --diff .

format:  ## Format code with black and isort
	black .
	isort .

check-deps:  ## Check for security vulnerabilities in dependencies
	pip install safety
	safety check

clean:  ## Clean up temporary files
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

docs:  ## Generate documentation
	@echo "Documentation can be found in README.md"
	@echo "Run 'python sync.py --help' for CLI usage"

validate:  ## Run full validation pipeline
	@echo "Running full validation..."
	make format
	make lint
	make test-cov
	make check-deps
	@echo "✅ All validation checks passed!"

demo:  ## Run a demo with sample data
	python -c "from analytics import create_sample_data, get_workout_metrics; df=create_sample_data(30); print('Sample metrics:', get_workout_metrics(df))"

sync-help:  ## Show sync.py help
	python sync.py --help

# Development shortcuts
dev-setup: install-dev  ## Complete development setup
	@echo "✅ Development environment ready!"

ci-local: format lint test-cov  ## Run CI checks locally
	@echo "✅ Local CI checks passed!"
