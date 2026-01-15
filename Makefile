# Honeycomb API Python Client - Development Makefile
.PHONY: help install install-dev lint lint-fix format typecheck test test-cov test-live clean build publish docs docs-serve docs-build validate-docs generate-tools validate-tools tools ci update-deps release-patch release-minor release-major changelog generate-models generate-models-fresh check-models-sync

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
	@echo "  make test-unit      Run only unit tests"
	@echo "  make test-eval      Run evaluation tests (requires ANTHROPIC_API_KEY)"
	@echo "  make test-eval-debug Run evaluation tests with no cache or parallelism (requires ANTHROPIC_API_KEY)"
	@echo "  make test-live      Run live Claude tool tests (requires ANTHROPIC_API_KEY and HONEYCOMB_MANAGEMENT_KEY)"
	@echo ""
	@echo "Build & Publish:"
	@echo "  make build          Build distribution packages"
	@echo "  make publish        Publish to PyPI (requires credentials)"
	@echo "  make publish-test   Publish to Test PyPI"
	@echo ""
	@echo "Release Management:"
	@echo "  make release-patch  Bump patch version, update changelog, commit & tag"
	@echo "  make release-minor  Bump minor version, update changelog, commit & tag"
	@echo "  make release-major  Bump major version, update changelog, commit & tag"
	@echo "  make changelog      Generate/update CHANGELOG.md"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs-serve     Serve docs locally with live reload"
	@echo "  make docs-build     Build static docs site"
	@echo "  make validate-docs  Validate all documentation code examples"
	@echo ""
	@echo "Claude Tools:"
	@echo "  make tools          Generate and validate Claude tool definitions"
	@echo "  make generate-tools Generate Claude tool definitions (all + per-resource JSON)"
	@echo "  make validate-tools Validate generated tool definitions"
	@echo ""
	@echo "Model Generation:"
	@echo "  make generate-models       Generate Pydantic models from api.yaml"
	@echo "  make generate-models-fresh Fetch latest api.yaml and generate models"
	@echo "  make check-models-sync     Verify generated models are in sync with spec"
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

# Sentinel files to track installation state
.venv-installed: pyproject.toml poetry.lock
	poetry install --only main
	@touch .venv-installed

.venv-dev-installed: pyproject.toml poetry.lock
	poetry install
	@touch .venv-dev-installed

install: .venv-installed

install-dev: .venv-dev-installed

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
	poetry run mypy --warn-unreachable --warn-redundant-casts --warn-unused-ignores src/

check: lint typecheck
	@echo "All checks passed!"

# =============================================================================
# Testing
# =============================================================================

test:
	poetry run pytest tests/ -s -q --tb=short --disable-warnings

test-unit:
	poetry run pytest tests/unit/ -s -q --tb=short --disable-warnings

test-cov:
	poetry run pytest tests/ -v --cov=honeycomb --cov-report=term-missing --cov-report=html

test-live:
	direnv exec . poetry run pytest tests/integration/test_claude_tools_live.py -v -s

test-eval:
	rm -rf tests/integration/.tool_call_cache/*.json
	direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py::TestArgumentCorrectness -v -n 4

test-eval-debug:
	rm -rf tests/integration/.tool_call_cache/*.json
	EVAL_USE_CACHE=false direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v

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
# Release Management
# =============================================================================

release-patch:
	@bash scripts/release.sh patch

release-minor:
	@bash scripts/release.sh minor

release-major:
	@bash scripts/release.sh major

changelog:
	@if ! command -v git-cliff &> /dev/null; then \
		echo "Error: git-cliff is not installed"; \
		echo "Install with: brew install git-cliff (macOS)"; \
		echo "Or see: https://git-cliff.org/docs/installation"; \
		exit 1; \
	fi
	git-cliff --output CHANGELOG.md
	@echo "CHANGELOG.md updated"

# =============================================================================
# Documentation
# =============================================================================

docs-serve:
	poetry run mkdocs serve --livereload --watch-theme

docs-build:
	poetry run mkdocs build

validate-docs:
	poetry run python scripts/validate_docs_examples.py
	poetry run pytest tests/integration/test_doc_examples.py -v

# =============================================================================
# Claude Tools
# =============================================================================

generate-tools:
	@mkdir -p tools
	@echo "Generating monolithic tool definitions..."
	poetry run python -m honeycomb.tools generate --output tools/honeycomb_tools.json
	@echo ""
	@echo "Generating per-resource tool definitions..."
	poetry run python -m honeycomb.tools generate --per-resource --output-dir tools/resources
	@echo ""
	@echo "Generated:"
	@echo "  - tools/honeycomb_tools.json (all tools)"
	@echo "  - tools/resources/*.json (per-resource)"

validate-tools:
	@if [ ! -f tools/honeycomb_tools.json ]; then \
		echo "Error: tools/honeycomb_tools.json not found. Run 'make generate-tools' first."; \
		exit 1; \
	fi
	poetry run python -m honeycomb.tools validate tools/honeycomb_tools.json

tools: generate-tools validate-tools
	@echo "Claude tools generated and validated successfully!"

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
	rm -f .venv-installed .venv-dev-installed
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

update-deps:
	poetry update
	poetry export -f requirements.txt --output requirements.txt --without-hashes 2>/dev/null || true

# =============================================================================
# Model Generation (datamodel-code-generator)
# =============================================================================

generate-models:
	@bash scripts/generate_models.sh

generate-models-fresh:
	@bash scripts/generate_models.sh --fetch

check-models-sync:
	@echo "Checking if generated models are in sync..."
	@bash scripts/generate_models.sh
	@git diff --exit-code src/honeycomb/_generated_models.py || \
		(echo "ERROR: Generated models out of sync! Run 'make generate-models'" && exit 1)
	@echo "✓ Models are in sync."

# =============================================================================
# CI Pipeline
# =============================================================================

ci: install-dev format check test-unit validate-docs
	@echo ""
	@echo "============================================"
	@echo "CI pipeline completed successfully!"
	@echo "============================================"
