---
name: scaffold-service
description: Take an empty directory to a first commit with a health endpoint that checks the database, one real test, a README, .env.example, Dockerfile, CI workflow and deploy spec, and a green CI run, in the first fifteen minutes of a timed build.
---

# Scaffold a service in fifteen minutes

Goal at minute 15: `git log` shows one commit, CI is green on it, a
health endpoint answers locally, one test passes, and the README's run
commands have been executed once. Everything the later phases assume is
in place. Nothing feature-shaped exists yet.

The stack comes from `playbook/stack-picker.md`. Do not revisit it here.
The four per-stack files live in `templates/<stack>/`: `Dockerfile`,
`ci-job.yml`, `.env.example`, `app-component.yaml`, plus a `README.md`
that describes the layout. This skill is the order of operations; the
templates are the content.

## Time box

| Minute | Step | Proof |
| --- | --- | --- |
| 0-2 | `git init`, `.gitignore`, `docs/`, copy `.env.example` | `git status` clean except new files |
| 2-6 | scaffold command, settings module, health endpoint | server answers `/health` |
| 6-9 | one test that calls health, run it | test runner exits 0 |
| 9-11 | Dockerfile, CI workflow, App Platform spec, README run section | files present, README commands run |
| 11-13 | `gh repo create`, first commit, push | commit on origin |
| 13-15 | watch CI, fix if red | green check on the commit |

If minute 15 arrives with CI red, keep going until it is green before
starting the feature. Red CI at the start becomes red CI at the end.

## Steps, any stack

1. **Repo and layout.** `git init -b main`. Write `.gitignore` for the
   stack (venv, node_modules, build output, `.env`, `data/*.db`).
   Create `docs/` with `demo-notes.md` (first line: the stack and why),
   `DECISIONS.md` and `TIMELOG.md` (see `skills/walkthrough-prep` and
   `skills/timebox`). Copy `templates/<stack>/.env.example` to the
   service root and to `.env` for local use; `.env` is ignored.
2. **Scaffold.** Run the stack's scaffold command from the picker table
   below. Delete sample files the generator adds that the README does
   not mention.
3. **Settings module.** One module reads the environment; nothing else
   does. It exposes the database URL, the port, the allowed origins and
   the environment name. Two modules reading the database path
   separately is how a service ends up writing one file and reading
   another, so do this before the first route exists.
4. **Health endpoint.** Returns 200 with a status field and a checks
   object that names the database. It must actually touch the database
   (`SELECT 1` or the driver's ping) and report `degraded` or 503 when
   that fails. A health check that cannot fail is decoration.
5. **One real test.** It starts the app in-process, calls the health
   path, asserts the status code and the status field. Run it; paste the
   runner's last line into `docs/TIMELOG.md`.
6. **Container and CI.** Copy `templates/<stack>/Dockerfile` to the
   service directory. Copy `templates/ci.yml` to
   `.github/workflows/ci.yml` and replace its backend job with
   `templates/<stack>/ci-job.yml`. Keep the secret-scan job. If Docker
   is on the machine, `docker build .` once; if not, say so in the demo
   notes and rely on CI.
7. **Deploy spec.** Copy `templates/do-app.yaml` to `.do/app.yaml` and
   swap the `api` block for `templates/<stack>/app-component.yaml`. Set
   `OWNER/REPO`. Remove the static site block for a backend-only
   service. Do not create the app yet; that is the ship phase.
8. **README.** Four sections, each with commands you have just run:
   what it is (one sentence, placeholder allowed), run locally, run
   tests, deploy. Add sections later; do not leave these empty.
9. **Commit and push.** `gh repo create <name> --private --source . --push`
   (or `--public` if a reviewer will read it), first commit message
   `chore: scaffold service with health check, tests and ci`. Then
   `gh run watch` or `gh run list --limit 1` until the check is green.
   Then require that check on `main` (repository settings, or
   `gh api -X PUT repos/OWNER/REPO/branches/main/protection` with the
   job names as required status checks) once it is.
10. **Log it.** One line in `docs/TIMELOG.md`: minute, "scaffold green",
    the run URL. One line in `docs/DECISIONS.md`: the stack, the
    alternative, why.

## Per-stack commands

Scaffold and first-test commands match `playbook/stack-picker.md`; the
health path and test file match `templates/<stack>/README.md`.

| Stack | Scaffold | Health | Test file | Run test | Run server |
| --- | --- | --- | --- | --- | --- |
| `python-fastapi` | `python -m venv venv && venv/bin/pip install fastapi "uvicorn[standard]" sqlalchemy pydantic-settings pytest httpx ruff mypy` (Windows: `venv\Scripts\pip`), then `pip freeze > requirements.txt` | `GET /health` in `src/main.py` | `tests/test_health.py` with a `TestClient` fixture | `pytest -q` | `uvicorn src.main:app --port 8000` |
| `java-spring-boot` | `curl https://start.spring.io/starter.zip -d dependencies=web,data-jpa,postgresql,flyway,actuator,validation -d type=gradle-project -d javaVersion=17 -o app.zip && unzip app.zip -d backend` | `GET /actuator/health` with `show-details: always` | `src/test/java/<pkg>/HealthTest.java` (`@SpringBootTest` + MockMvc) | `./gradlew test --no-daemon` | `./gradlew bootRun` |
| `node-typescript` | `npm init -y && npm i fastify && npm i -D typescript tsx vitest @types/node eslint prettier && npx tsc --init` | `GET /health` in `src/routes/health.ts` | `test/health.test.ts` using `app.inject()` | `npx vitest run` | `npx tsx src/server.ts` |
| `go` | `go mod init example.com/app && go get github.com/go-chi/chi/v5` | `GET /healthz` in `internal/http/health.go` | `internal/http/health_test.go` with `httptest` | `go test ./...` | `go run ./cmd/server` |
| `vite-react` (frontend) | `npm create vite@latest frontend -- --template react-ts && cd frontend && npm i` | none; `config/api.ts` points at the backend's health | none; `npm run verify` is the gate | `npm run verify` | `npm run dev` |
| `nextjs` | `npx create-next-app@latest frontend --ts --eslint --app --src-dir --no-tailwind --import-alias "@/*"` | `GET /api/health` in `src/app/api/health/route.ts` | none by default; `npm run lint && npx tsc --noEmit` is the gate | `npm run lint && npx tsc --noEmit` | `npm run dev` |

Database at scaffold time: SQLite file for FastAPI, H2 in memory for
Spring Boot (`test` profile), and for Node and Go either a local Postgres
container (`docker run -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16`)
or, if Docker is absent, SQLite through the stack's driver with the URL
in the settings module. The deploy binds `${db.DATABASE_URL}` later; the
settings module is where the difference is absorbed.

## The first commit's checklist

Before `git commit`, all of these are true:

- [ ] Health endpoint answers locally and its body names the database.
- [ ] One test passes and its output was seen, not assumed.
- [ ] Settings module is the only reader of the environment; `.env.example` lists every key it reads.
- [ ] `.env` is ignored; `grep -rn "sk-\|token\|password" --include=*.py --include=*.ts --include=*.java --include=*.go .` finds only placeholders.
- [ ] `Dockerfile`, `.github/workflows/ci.yml`, `.do/app.yaml` exist and name this stack's commands.
- [ ] README run section was executed from a fresh terminal.

## Worked example (FastAPI, minute 0 to 14)

```
git init -b main && mkdir -p backend/src backend/tests docs
python -m venv backend/venv && backend/venv/bin/pip install fastapi "uvicorn[standard]" sqlalchemy pydantic-settings pytest httpx ruff mypy
backend/venv/bin/pip freeze > backend/requirements.txt
cp templates/python-fastapi/.env.example backend/.env.example && cp backend/.env.example backend/.env
# src/core/config.py: Settings with database_url, port, allowed_origins, environment
# src/main.py: app, CORS from settings, GET /health -> {"status": "healthy", "checks": {"database": "ok"}} after SELECT 1
# tests/test_health.py: client.get("/health") -> 200, body["status"] in {"healthy", "degraded"}
cd backend && venv/bin/pytest -q            # 1 passed in 0.31s
venv/bin/uvicorn src.main:app --port 8000 & curl -s localhost:8000/health   # {"status":"healthy",...}  (8000 is this example's port)  (8000 is this example's port)
cp ../templates/python-fastapi/Dockerfile Dockerfile && cd ..
mkdir -p .github/workflows .do && cp templates/ci.yml .github/workflows/ci.yml && cp templates/do-app.yaml .do/app.yaml
# edit .do/app.yaml: OWNER/REPO, drop static_sites and its ingress rule
# README.md: what, run locally, run tests, deploy
gh repo create my-app --private --source . --push
git add -A && git commit -m "chore: scaffold service with health check, tests and ci" && git push
gh run list --limit 1     # completed  success  CI
```

Minute 14: `docs/TIMELOG.md` gets "14 scaffold green <run url>" and the
feature phase starts.

## Tool notes

Any assistant can follow this. If the kit's `templates/<stack>/` folder
is not available, the per-stack table above is enough: write the
Dockerfile, CI job and deploy spec from the stack's official quickstart
and keep the same four-file shape. Attach the layout description to the
chat before step 2 so the layout is not invented.
