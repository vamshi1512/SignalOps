SHELL := /bin/bash

.PHONY: backend-install frontend-install backend-dev frontend-dev test-backend test-frontend test-e2e test compose-up compose-down

backend-install:
	cd backend && python3 -m pip install -e '.[dev]'

frontend-install:
	cd frontend && npm ci

backend-dev:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend-dev:
	cd frontend && npm run dev

test-backend:
	cd backend && pytest

test-frontend:
	cd frontend && npm run lint && npm run test:run && npm run build

test-e2e:
	cd frontend && npm run test:e2e

test: test-backend test-frontend

compose-up:
	docker compose up --build

compose-down:
	docker compose down --remove-orphans
