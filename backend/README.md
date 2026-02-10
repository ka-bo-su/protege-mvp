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

Makefile shortcut (from repo root):
```bash
make dev-backend
```

## Database
- Default DB: SQLite file at `backend/app.db`
- Override with `DATABASE_URL` (example):
	- `DATABASE_URL=sqlite:////absolute/path/to/app.db`

## Migrations (Alembic)
```bash
uv run alembic revision --autogenerate -m "core schema"
uv run alembic upgrade head
sqlite3 app.db ".tables"
```

Makefile shortcuts (from repo root):
```bash
make db-revision MSG="init"
make db-upgrade
```

`alembic_version` will be created in the SQLite DB file above.

## Active goal constraint (goals)
Active goal は user_id ごとに 1 件だけに制限されます。

確認手順:
```bash
uv run alembic upgrade head
sqlite3 app.db ".indexes goals"
```

同一 user_id で active を 2 件入れてみて、2 件目が UNIQUE 制約エラーになることを確認:
```sql
INSERT INTO goals(user_id, content, version, is_active, created_at)
VALUES (1, 'a', 1, 1, CURRENT_TIMESTAMP);
INSERT INTO goals(user_id, content, version, is_active, created_at)
VALUES (1, 'b', 2, 1, CURRENT_TIMESTAMP);
```

## Healthcheck
```bash
curl http://localhost:8000/health
```
