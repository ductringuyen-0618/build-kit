# Backend skeleton: FastAPI + SQLAlchemy + pytest

A description, not a generator. Read `skills/grill-me` before deciding the
data model and `skills/feature-build` for commit discipline. The layout
below is the one used on TechPulse, trimmed to what a three-hour build
needs.

## Layout

```
backend/
  src/
    main.py                 app factory, CORS, routers, /health
    core/config.py          Settings (pydantic-settings); the single database resolver
    core/logging.py         structlog or stdlib JSON logging with a request id
    database/base.py        engine + session factory from Settings
    database/models.py      SQLAlchemy models
    api/routes/<resource>.py one router per resource, trailing-slash paths
    repositories/<resource>_repository.py
    services/<resource>_service.py
  tests/
    conftest.py             app fixture with a temp SQLite file, TestClient
    test_health.py
    test_<resource>.py
  scripts/smoke.py          stdlib HTTP smoke runner (test-app-e2e pattern)
  alembic/                  only if there is more than one migration
  requirements.txt
  pytest.ini                markers: unit, integration, e2e, smoke; --strict-markers
  Dockerfile                from templates/Dockerfile
```

## Rules that came from real bugs

- `Settings` exposes `get_database_path()`, `get_database_file_path()`
  and `get_database_sqlalchemy_url()`. Nothing else reads `DATABASE_URL`
  directly. SQLite locally (`sqlite:///./data/app.db`), Postgres in the
  deploy (`${db.DATABASE_URL}` from the App Platform spec).
- Routes are mounted with trailing slashes (`/api/items/`). The frontend
  calls the exact path. FastAPI's 307 redirect does not carry CORS headers.
- `/health` returns `{"status": "healthy" | "degraded" | "unhealthy", "checks": {...}}`.
  Report dependencies honestly; a `/health` that says healthy while the
  database is unreachable is worse than none.
- `ENVIRONMENT=testing` disables schedulers and background jobs.
- External services (LLM providers, third-party APIs) sit behind a small
  interface with a fake implementation used in tests.

## Commands

```
python -m venv venv && venv/bin/pip install -r requirements.txt   # Windows: venv\Scripts\pip
uvicorn src.main:app --host 127.0.0.1 --port 8000
pytest tests -q
ruff check . && ruff format --check .
mypy . --ignore-missing-imports
python scripts/smoke.py --base-url http://127.0.0.1:8000
```

## Minimum dependencies

```
fastapi
uvicorn[standard]
sqlalchemy>=2
pydantic-settings
python-dotenv
psycopg[binary]        # only when Postgres is the deploy target
pytest
httpx                  # TestClient
ruff
mypy
```

## First test

```python
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] in {"healthy", "degraded"}
```

## Smoke runner shape

`scripts/smoke.py` follows `skills/test-app-e2e/scripts/run_e2e.py`: each
check returns a result with `name`, `passed`, `severity`, `detail`,
`request`, `response`, `suggested_fix_area`; `--json` prints the report;
exit 0 on all pass, 1 on failure, 2 when the base URL is unreachable. Keep
it under 150 lines for a three-hour build.
