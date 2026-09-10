# Stack picker: one minute at minute zero

Pick once, say it out loud, write it at the top of `docs/demo-notes.md`,
and do not revisit. Every later step reads the choice from there.

## Which stack when

Any of the six stacks in `templates/` can carry a timed build; the wrong
choice costs more than any stack's weaknesses. Prefer the stack the
person or agent doing the work has shipped with most recently, then let
the prompt override: a named language wins outright, a UI-heavy demo
wants Vite/React (or Next.js when server rendering matters) in front of
whichever backend, and a data-heavy or AI-flavoured prompt wants the
ecosystem with the ready-made libraries (Python for AI and data, Spring
Boot for CRUD with business rules and auth, Go for concurrency and small
images, Node/TypeScript when one language across frontend and backend
saves context switches). When nothing pulls, pick the one whose first
test passes fastest from an empty folder.

## Decision table

| Signal | Pick |
| --- | --- |
| The prompt, or the person you are building for, names a language | that language, no debate |
| Prompt is API-first with a data model and one business rule | the backend stack you are fastest in; skip the frontend or serve a minimal page from the backend |
| Prompt needs a visible UI for the demo | backend of choice plus Vite/React; Next.js only if you have shipped with it recently |
| Prompt mentions concurrency, workers, or "handle a spike" | Go or Spring Boot; both have a clean story for the scaling hypotheticals |
| Prompt mentions AI, embeddings, or summarisation | Python FastAPI; the AI client libraries are there and a provider interface with a fake is quick to write |
| Prompt mentions a team, orgs, roles, or auth | Spring Boot (Security, JPA, Flyway) or FastAPI with a simple token; do not reach for a hosted auth provider under time pressure |
| No signal at all | the stack with the most recent muscle memory; FastAPI for AI-flavoured prompts, Spring Boot or Node for CRUD-with-rules prompts |

Tie-breakers, in order: which stack has a passing test in under five
minutes from scaffold; which one App Platform builds without a
Dockerfile; which one you can explain the failure modes of without
notes.

## What App Platform builds without a Dockerfile

Buildpacks auto-detect Python (`requirements.txt`, or `pyproject.toml`
with `uv.lock`), Node (`package.json` plus a lockfile, pnpm included),
Go (`go.mod`; the run command must still be set) and static sites (a
`static_sites` component with a build command). There is no Java
buildpack, so Spring Boot always ships with a Dockerfile, and the Go
template also defaults to its Dockerfile so the run command is
unambiguous. Details and citations in `skills/deploy-digitalocean-app-platform`.

## Scaffold commands

Each `templates/<stack>/` folder holds a README with the scaffold, run,
test, build and lint commands, plus four files to copy into the new
repo: `Dockerfile`, `ci-job.yml` (paste under `jobs:` in
`.github/workflows/ci.yml`; `templates/ci.yml` is the surrounding
workflow), `.env.example` and `app-component.yaml` (paste into
`.do/app.yaml`; `templates/do-app.yaml` is the surrounding spec). Lines
marked `# CHANGE:` are the ones a new repo must edit.

| Stack | Port, health | Scaffold | First test |
| --- | --- | --- | --- |
| `python-fastapi` | 8000, `/health` | `python -m venv venv && venv/bin/pip install fastapi "uvicorn[standard]" sqlalchemy pydantic-settings pytest httpx ruff mypy` then the `src/main.py` in the README | `pytest -q` on the health test |
| `java-spring-boot` | 8080, `/actuator/health` | `curl https://start.spring.io/starter.zip -d type=gradle-project -d javaVersion=17 -d dependencies=web,data-jpa,postgresql,h2,flyway,actuator,validation -d baseDir=backend -o app.zip && unzip app.zip` | `./gradlew test --no-daemon` |
| `node-typescript` | 8080, `/health` | `npm init -y && npm i fastify && npm i -D typescript tsx vitest @types/node eslint prettier && npx tsc --init` | `npx vitest run` on the health test |
| `go` | 8080, `/healthz` | `go mod init example.com/app` (optionally `go get github.com/go-chi/chi/v5`) | `go test ./...` on the health handler |
| `vite-react` | 5173 dev, static build | `npm create vite@latest frontend -- --template react-ts && cd frontend && npm i` | `npm run verify` |
| `nextjs` | 3000, `/api/health` | `npx create-next-app@latest frontend --ts --eslint --app --src-dir --no-tailwind --import-alias "@/*"` | `npm run lint && npx tsc --noEmit` |

The Spring Initializr command takes its default Boot version (4.x as of
2026-09-09; 3.x is no longer offered) and Java 17, the oldest it lists
and what the Dockerfile and CI snippet use. Pin `-d bootVersion=` only
to a value present in `https://start.spring.io/metadata/client`.

For a pnpm monorepo (backend and frontend as workspaces) use
`templates/ci-monorepo.yml` and keep each app's own Dockerfile.

## What each stack must have before the first commit

- A health endpoint that checks the database and returns a status field.
- One passing test that calls it.
- A settings module that is the only reader of the environment.
- A `.env.example` with every variable the settings module reads.
- A Dockerfile that builds locally (`docker build .` once, if Docker is
  on the machine).
- The CI workflow with the stack's job snippet.
