.PHONY: dev dev-backend dev-frontend

dev:
	$(MAKE) -j 2 dev-backend dev-frontend

dev-backend:
	cd backend && uv sync
	cd backend && uv run uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm install
	cd frontend && npm run dev -- --host
