SHELL := /bin/zsh

.PHONY: backend-install frontend-install backend-dev frontend-dev test lint typecheck build compose-up compose-down

backend-install:
	cd backend && python3 -m pip install -e '.[dev]'

frontend-install:
	cd frontend && npm ci

backend-dev:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend-dev:
	cd frontend && npm run dev

test:
	cd backend && python3 -m pytest tests -q
	cd frontend && npm run test:run

lint:
	cd frontend && npm run lint

typecheck:
	cd frontend && npm run typecheck

build:
	cd frontend && npm run build

compose-up:
	docker compose up --build

compose-down:
	docker compose down -v
