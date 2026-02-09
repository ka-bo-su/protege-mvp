# Backend

FastAPI backend for the t2ai MVP.

## Requirements
- Python 3.11+ (3.12 recommended)
- uv

## Run (dev)
```bash
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

## Healthcheck
```bash
curl http://localhost:8000/health
```
