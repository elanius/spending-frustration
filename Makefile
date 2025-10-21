.PHONY: backend backend-setup frontend clean-backend-venv

# Ensure we use bash so that 'source' works (dash / sh may not support it fully)
SHELL := /bin/bash

# Run each recipe in a single shell so that cd / venv activation persist across lines
.ONESHELL:

PORT ?= 8000
BACKEND_DIR := backend
FRONTEND_DIR := frontend
VENV := $(BACKEND_DIR)/.venv
REQ := $(BACKEND_DIR)/requirements.txt

backend-setup: ## Create virtual env (if missing) and install backend dependencies
	@if [ ! -d "$(VENV)" ]; then \
		python3 -m venv $(VENV); \
	fi
	. $(VENV)/bin/activate
	pip install --upgrade pip
	pip install -r $(REQ)

backend: ## Run FastAPI backend with auto-reload
	cd $(BACKEND_DIR)
	if [ ! -d ".venv" ]; then \
		echo "[INFO] .venv not found. Run 'make backend-setup' first."; \
		exit 1; \
	fi
	. .venv/bin/activate
	# Export variables from backend/.env if present
	if [ -f .env ]; then \
		set -a; source .env; set +a; \
	fi
	uvicorn app.main:app --port $(PORT) --reload

frontend: ## Run frontend dev server
	cd $(FRONTEND_DIR)
	# Export variables from frontend/.env if present
	if [ -f .env ]; then \
		set -a; source .env; set +a; \
	fi
	npm run dev

clean-backend-venv: ## Remove backend virtual environment
	rm -rf $(VENV)

login-token: ## Generate a JWT token for testing (valid for 10 years)
	curl -X 'POST' \
	'http://localhost:8000/auth/login' \
	-H 'accept: application/json' \
	-H 'Content-Type: application/x-www-form-urlencoded' \
	-d 'grant_type=password&username=demo%40example.com&password=Secret123!&scope=&client_id=&client_secret='

# Start local MongoDB using docker-compose
mongo: ## Start local MongoDB service using docker-compose
	docker-compose up -d mongo

# Help target to display available commands
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS=":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'
