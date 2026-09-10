# python-fastapi

FastAPI + SQLAlchemy + pytest backend in `backend/`. Listens on `PORT`
(default 8000); health check is `GET /health`.

## Scaffold (from the repo root)

```
mkdir -p backend/src backend/tests && cd backend && touch src/__init__.py
python -m venv venv && . venv/bin/activate          # Windows: venv\Scripts\activate
pip install fastapi "uvicorn[standard]" sqlalchemy pydantic-settings pytest httpx ruff mypy
pip freeze > requirements.txt
cp <kit>/templates/python-fastapi/{Dockerfile,.env.example} .
```

`src/main.py` and `tests/test_health.py` to start from:

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "checks": {}}   # add "db": "ok"/"down"; 503 when down
```

```python
from fastapi.testclient import TestClient
from src.main import app

def test_health():
    assert TestClient(app).get("/health").json()["status"] == "healthy"
```

## Commands (run from `backend/`)

| Task | Command |
| --- | --- |
| run | `uvicorn src.main:app --reload --port 8000` |
| test | `pytest -q` |
| lint | `ruff check . && ruff format --check .` |
| typecheck | `mypy . --ignore-missing-imports` |
| build | `docker build -t api .` |

## Files in this folder

- `Dockerfile`: two-stage image (venv builder, slim non-root runtime with HEALTHCHECK). Copy to `backend/Dockerfile`.
- `ci-job.yml`: GitHub Actions job (lint, typecheck, test, import smoke). Paste under `jobs:` in `.github/workflows/ci.yml`.
- `.env.example`: every variable the app reads. Copy to `backend/.env.example`; `.env` is git-ignored.
- `app-component.yaml`: DigitalOcean App Platform `services:` entry. Paste into `.do/app.yaml`.

## Conventions

- One `Settings` class (pydantic-settings) reads the environment; nothing else touches `os.environ`.
- `DATABASE_URL` is a SQLAlchemy URL: `sqlite:///./data/app.db` locally, Postgres in the deploy.
- Mount routes with one slash style (`/api/items/`) and call that exact path from clients;
  FastAPI's 307 redirect does not carry CORS headers.
- `/health` reports each dependency honestly and returns 503 when one is down.
- External services (LLMs, third-party APIs) sit behind a small interface with a fake used in tests.
