.PHONY: help install dev test lint fmt typecheck cli frontend frontend-build compose down clean

VENV := backend/.venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS=":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Create venv and install the backend (dev extras)
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e "backend/.[dev]"

dev: ## Run the backend with autoreload
	cd backend && .venv/bin/uvicorn workflow_intel.api.app:app --reload --port 8000

test: ## Run the backend test suite
	cd backend && .venv/bin/pytest -q

lint: ## Lint the backend
	cd backend && .venv/bin/ruff check .

fmt: ## Format the backend
	cd backend && .venv/bin/ruff format .

typecheck: ## Type-check the backend
	cd backend && .venv/bin/mypy workflow_intel

cli: ## Analyze the canonical example via the CLI (summary)
	cd backend && .venv/bin/python -m workflow_intel.cli analyze "Sales emails contracts to Legal. Legal reviews and sends comments back. Sales updates Salesforce. Finance receives a Slack notification. Contracts are stored in SharePoint."

frontend: ## Run the frontend dev server
	cd frontend && npm install && npm run dev

frontend-build: ## Type-check and build the frontend
	cd frontend && npm install && npm run build

compose: ## Bring up the full stack (backend, frontend, postgres, otel)
	docker compose up --build

down: ## Stop the stack
	docker compose down

clean: ## Remove build artifacts
	rm -rf $(VENV) frontend/node_modules frontend/dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
