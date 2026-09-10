# Stack picker: one minute at minute zero

Pick once, say it out loud, write it at the top of `docs/demo-notes.md`,
and do not revisit. Every later step reads the choice from there.

## Decision table

| Signal | Pick |
| --- | --- |
| Interviewer or prompt names a language | that language, no debate |
| Prompt is API-first with a data model and one business rule | the backend stack you are fastest in; skip the frontend or serve a minimal page from the backend |
| Prompt needs a visible UI for the demo | backend of choice plus Vite/React; Next.js only if you have shipped with it recently |
| Prompt mentions concurrency, workers, or "handle a spike" | Go or Spring Boot; both have a clean story for the scaling hypotheticals |
| Prompt mentions AI, embeddings, or summarisation | Python FastAPI; the provider abstraction and fakes from TechPulse carry over |
| Prompt mentions a team, orgs, roles, or auth | Spring Boot (Security, JPA, Flyway) or FastAPI with a simple token; do not reach for a hosted auth provider under time pressure |
| No signal at all | the stack with the most recent muscle memory; for Tri that is FastAPI for AI-flavoured prompts and Spring Boot for CRUD-with-rules prompts |

Tie-breakers, in order: which stack has a passing test in under five
minutes from scaffold; which one App Platform builds without a
Dockerfile; which one you can explain the failure modes of without
notes.

## What App Platform builds without a Dockerfile

Buildpacks auto-detect Python (`requirements.txt`, `pyproject.toml` with
`uv.lock`), Node (`package.json` plus lockfile, pnpm included), Go
(`go.mod`), static sites (`static_sites` component with a build command).
There is no Java buildpack, so Spring Boot always ships as a Dockerfile.
Details and citations in `skills/deploy-digitalocean-app-platform`.

## Scaffold commands

Each stack has `templates/<stack>/` with a Dockerfile, a CI job snippet,
`.env.example` and the App Platform component. Scaffold, then copy those
four files in.

| Stack | Scaffold | First test |
| --- | --- | --- |
| `python-fastapi` | `python -m venv venv && venv/bin/pip install fastapi "uvicorn[standard]" sqlalchemy pydantic-settings pytest httpx ruff mypy` then `templates/python-fastapi/README.md` layout | `pytest -q` on the health test |
| `java-spring-boot` | `curl https://start.spring.io/starter.zip -d dependencies=web,data-jpa,postgresql,flyway,actuator,validation -d type=gradle-project -d javaVersion=17 -d bootVersion=3.4.5 -o app.zip && unzip app.zip -d backend` | `./gradlew test --no-daemon` |
| `node-typescript` | `npm init -y && npm i fastify && npm i -D typescript tsx vitest @types/node eslint prettier && npx tsc --init` | `npx vitest run` on the health test |
| `go` | `go mod init example.com/app && go get github.com/go-chi/chi/v5` | `go test ./...` on the health handler |
| `vite-react` | `npm create vite@latest frontend -- --template react-ts && cd frontend && npm i` | `npm run verify` |
| `nextjs` | `npx create-next-app@latest frontend --ts --eslint --app --src-dir --no-tailwind --import-alias "@/*"` | `npm run lint && npx tsc --noEmit` |

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
