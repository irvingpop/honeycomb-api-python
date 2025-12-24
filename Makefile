# Honeycomb API Python Client - Development Makefile
.PHONY: help install install-dev lint lint-fix format typecheck test test-cov test-live clean build publish docs docs-serve docs-build validate-docs

# Default target
help:
	@echo "Honeycomb API Python Client - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install production dependencies"
	@echo "  make install-dev    Install all dependencies (including dev)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run linter (ruff check)"
	@echo "  make lint-fix       Run linter and auto-fix issues"
	@echo "  make format         Format code with ruff"
	@echo "  make typecheck      Run type checker (mypy)"
	@echo "  make check          Run all checks (lint + typecheck)"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all tests"
	@echo "  make test-cov       Run tests with coverage report"
	@echo "  make test-live      Run live API tests (requires HONEYCOMB_API_KEY)"
	@echo "  make test-unit      Run only unit tests"
	@echo ""
	@echo "Build & Publish:"
	@echo "  make build          Build distribution packages"
	@echo "  make publish        Publish to PyPI (requires credentials)"
	@echo "  make publish-test   Publish to Test PyPI"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs-serve     Serve docs locally with live reload"
	@echo "  make docs-build     Build static docs site"
	@echo "  make validate-docs  Validate all documentation code examples"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          Remove build artifacts and cache files"
	@echo "  make update-deps    Update dependencies to latest versions"
	@echo ""
	@echo "CI:"
	@echo "  make ci             Run full CI pipeline (install, format, check, test, validate-docs)"
	@echo "  make validate-docs  Validate documentation code examples"

# =============================================================================
# Setup
# =============================================================================

install:
	poetry install --only main

install-dev:
	poetry install

# =============================================================================
# Code Quality
# =============================================================================

lint:
	poetry run ruff check src/ tests/

lint-fix:
	poetry run ruff check --fix src/ tests/

format:
	poetry run ruff format src/ tests/

typecheck:
	poetry run mypy src/

check: lint typecheck
	@echo "All checks passed!"

# =============================================================================
# Testing
# =============================================================================

test:
	poetry run pytest tests/ -v

test-unit:
	poetry run pytest tests/unit/ -v

test-cov:
	poetry run pytest tests/ -v --cov=honeycomb --cov-report=term-missing --cov-report=html

test-live:
	@if [ -z "$$HONEYCOMB_API_KEY" ]; then \
		echo "Error: HONEYCOMB_API_KEY environment variable is not set"; \
		echo "Run 'direnv allow' or export HONEYCOMB_API_KEY=your-key"; \
		exit 1; \
	fi
	poetry run python scripts/test_live_api.py

# =============================================================================
# Build & Publish
# =============================================================================

build: clean
	poetry build

publish: build
	poetry publish

publish-test: build
	poetry publish -r testpypi

# =============================================================================
# Documentation
# =============================================================================

docs-serve:
	poetry run mkdocs serve --livereload --watch-theme

docs-build:
	poetry run mkdocs build

validate-docs:
	poetry run python scripts/validate_docs_examples.py

# =============================================================================
# Maintenance
# =============================================================================

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf site/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

update-deps:
	poetry update
	poetry export -f requirements.txt --output requirements.txt --without-hashes 2>/dev/null || true

# =============================================================================
# CI Pipeline
# =============================================================================

ci: install-dev format check test validate-docs
	@echo ""
	@echo "============================================"
	@echo "CI pipeline completed successfully!"
	@echo "============================================"
