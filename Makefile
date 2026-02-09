.PHONY: dev dev-backend dev-frontend db-upgrade db-revision

dev:
	$(MAKE) -j 2 dev-backend dev-frontend

dev-backend:
	cd backend && uv sync
	cd backend && uv run uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm install
	cd frontend && npm run dev -- --host

db-upgrade:
	cd backend && uv run alembic upgrade head

db-revision:
	cd backend && uv run alembic revision -m "$(MSG)"
