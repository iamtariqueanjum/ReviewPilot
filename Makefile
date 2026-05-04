.PHONY: build up down logs worker shell test lint

# ── Docker ───────────────────────────────────────────────────────────────────

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

logs-worker:
	docker compose logs -f worker

# ── Dev ──────────────────────────────────────────────────────────────────────

shell:
	docker compose exec api bash

worker-shell:
	docker compose exec worker bash

# ── Testing ──────────────────────────────────────────────────────────────────

test:
	docker compose exec api pytest tests/ -v --cov=app --cov-report=term-missing

# ── Code Quality ─────────────────────────────────────────────────────────────

lint:
	docker compose exec api pylint app/

# ── Cleanup ──────────────────────────────────────────────────────────────────

clean:
	docker compose down -v --remove-orphans
	docker image prune -f
