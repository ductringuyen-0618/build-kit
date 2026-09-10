---
name: deploy-digitalocean-app-platform
description: Deploy a service or full-stack app to DigitalOcean App Platform in the last 30 minutes of a timed build. Use when the prompt says "deploy on DigitalOcean", when a public URL is needed for a demo, when writing or fixing .do/app.yaml, when wiring a managed Postgres database, or when a deploy is failing under time pressure and a fallback is needed. Covers doctl, buildpacks versus Dockerfile, secrets, health checks, database binding, per-stack run commands, verification, and cleanup.
---

# Deploy to DigitalOcean App Platform

Goal: a public URL that serves the app, with the database attached, in
under 30 minutes, and a story for the walkthrough about what was verified.
Command syntax below was checked against the DigitalOcean docs listed in
`references/digitalocean-docs.md`; flags not listed there are not used.

If the machine has network access, install DigitalOcean's own skills
first: `git clone https://github.com/digitalocean-labs/do-app-platform-skills.git`
then `mkdir -p ~/.claude/skills && ln -s "$PWD/do-app-platform-skills" ~/.claude/skills/do-app-platform-skills`
(the README gives the same symlink for `~/.codex/skills` and
`~/.cursor/skills`). They are maintained by DigitalOcean (designer,
deployment, networking, Postgres, managed databases, migration,
troubleshooting) and cover more cases than this file. This skill is the
version that works with nothing installed but `doctl`.

## Time box

| Minute | Step | Leave behind |
| --- | --- | --- |
| 0-3 | Prerequisites check | `doctl account get` output in the demo notes |
| 3-8 | Pick build method, write `.do/app.yaml` | committed spec |
| 8-10 | `doctl apps create` | app id in the demo notes |
| 10-20 | Watch build and deploy logs, fix the first failure | green deployment |
| 20-25 | Verify against the live URL | status codes and one read-back in the demo notes |
| 25-30 | README deploy section, final commit | CI green |

If minute 20 arrives with no green deployment, go to "Fallback" below.
Do not spend the last ten minutes debugging the platform.

## 1. Prerequisites

- `doctl` installed (`doctl version`).
- Authenticated. The human runs `doctl auth init` (or
  `doctl auth init --context interview` to keep it apart from an existing
  login) and pastes the token themselves. The assistant never asks for,
  reads, echoes or stores the token. If the assistant is driving a terminal, hand the keyboard over
  for that one command.
- Confirm: `doctl account get` prints the account email and status.
- For GitHub-sourced builds, the DigitalOcean GitHub app must be
  authorised for the repo. That is done once in the control panel
  (Apps, Create App, GitHub, Manage Access). If it is not done and the
  panel is slow, use the container registry path in section 3c.

## 2. Build method

App Platform builds with a buildpack when it recognises the repo, and
with a Dockerfile when `dockerfile_path` is set. Rules of thumb:

| Stack | Buildpack detects | Use buildpack when | Use Dockerfile when |
| --- | --- | --- | --- |
| Python (FastAPI, Flask, Django) | `requirements.txt`, `Pipfile`, `setup.py`; `pyproject.toml` with `uv.lock` and `.python-version` | plain pip deps, one process | native deps, model downloads, exact Python pin |
| Node/TypeScript (Express, Fastify, Next.js) | `package.json` plus lockfile; pnpm via `pnpm-lock.yaml` | `npm run build` then `npm start` is the whole story | monorepo workspaces, custom runtime, standalone Next output |
| Go | `go.mod` | single `main` package | multiple binaries, CGO, or you want the run command unambiguous |
| Java / Spring Boot | no Java buildpack in the DigitalOcean buildpack list | never | always: JDK builder stage, JRE runtime stage |
| Static site (Vite/React) | `package.json` as a `static_sites` component | always | never |

The buildpack sets `PORT` at run time; the app must listen on it. With a
Dockerfile, set `http_port` in the spec to whatever the container exposes.

One-file Dockerfiles for each stack are in `templates/<stack>/Dockerfile`.
The FastAPI one is a two-stage `python:3.12-slim` build with a non-root
user and a curl health check. The Vite one is not needed: the static site
component builds it.

### Per-stack build and run commands

| Stack | build_command | run_command | health path | port | test |
| --- | --- | --- | --- | --- | --- |
| Python FastAPI | (buildpack) | `uvicorn src.main:app --host 0.0.0.0 --port $PORT` | `/health` | `$PORT` (8080 default) | `pytest -q` |
| Java Spring Boot | Dockerfile: `./gradlew bootJar --no-daemon` | `java -jar app.jar` with `server.port=${PORT:8080}` | `/actuator/health` | 8080 | `./gradlew test --no-daemon` |
| Node Express/Fastify | `npm ci && npm run build` | `npm start` (runs `node dist/server.js`) | `/health` | `process.env.PORT` | `npm test` |
| Go net/http or chi | Dockerfile: `go build -o /out/server ./cmd/server` | `/server` | `/healthz` | `PORT` env, default 8080 | `go test ./...` |
| Next.js | `npm ci && npm run build` | `npm start` (`next start -p $PORT`) | `/api/health` | `$PORT` | `npm run lint && npx tsc --noEmit` |
| Vite/React static | `npm ci && npm run build` | none (static) | none | none | `npm run verify` |

## 3. The spec: `.do/app.yaml`

Worked example in `templates/do-app.yaml`: one web service, one static
site, one dev Postgres database, one secret, one pre-deploy migration job,
and an ingress that puts both components under one URL. Copy it, then
change `OWNER/REPO`, `source_dir`, `http_port`, the health path and the
run command for the stack. Field notes:

- `github.deploy_on_push: true` redeploys on every push to `branch`. Turn
  it off during the interview if pushes are frequent and builds are slow;
  turn it back on for the demo.
- `source_dir` is the folder the build runs in. For a monorepo with
  `backend/` and `frontend/`, each component sets its own.
- `http_port` must match the port the process listens on.
- `health_check.http_path` is what the platform polls; a component with a
  failing health check never goes live. Defaults: `initial_delay_seconds`
  0, `period_seconds` 10, `timeout_seconds` 1, `failure_threshold` 9, so a
  slow start gets about 90 seconds before the deploy is marked failed.
  Set `initial_delay_seconds` to cover startup (Spring Boot needs 30 or
  more) and raise `timeout_seconds` if the health handler touches the
  database.
- Environment variables: `scope: RUN_TIME`, `BUILD_TIME`, or
  `RUN_AND_BUILD_TIME`. Mark secrets `type: SECRET` with an empty value in
  the committed file and set the value in the control panel, or paste the
  `EV[...]` ciphertext the panel produces after the first save.
- Bindable variables are filled by the platform: `${APP_URL}` and
  `${APP_DOMAIN}` at app level; `${_self.PUBLIC_URL}` for the current
  component; `${<component>.PUBLIC_URL}` or `${<component>.PRIVATE_URL}`
  for another component; `${<db>.DATABASE_URL}`, `${<db>.HOSTNAME}`,
  `${<db>.PORT}`, `${<db>.USERNAME}`, `${<db>.PASSWORD}`, `${<db>.DATABASE}`,
  `${<db>.CA_CERT}` and `${<db>.JDBC_DATABASE_URL}` for a database.

### 3a. Create and watch

```
doctl apps spec validate .do/app.yaml
doctl apps create --spec .do/app.yaml --format ID,DefaultIngress
doctl apps list
doctl apps get <app-id> --format ID,Spec.Name,DefaultIngress,ActiveDeployment.ID
doctl apps logs <app-id> --type build --follow
doctl apps logs <app-id> --type deploy --follow
doctl apps logs <app-id> --type run --follow
```

`DefaultIngress` in `doctl apps get` is the live URL
(`doctl apps get <app-id> --format DefaultIngress --no-header` prints only
that). `--wait` on `create` or `update` blocks until the deployment
finishes; skip it when you want to watch the logs. `--type` defaults
to `run`. A component name can be passed after the app id to narrow logs
to one component (`doctl apps logs <app-id> api --type build`).

Spec changes: edit the file, then `doctl apps update <app-id> --spec .do/app.yaml`.
The update triggers a new deployment. To redeploy the same spec (for
example after pushing a new container image): `doctl apps create-deployment <app-id>`.

### 3b. Database wiring

Add to the spec:

```yaml
databases:
  - name: db
    engine: PG
    production: false
```

`production: false` is a dev database: provisioned with the app, cheapest
(one size, $7 a month, no standby), PostgreSQL only (versions 15 to 18,
`version: "16"` to pin), fine for a prototype. `production: true` with
`cluster_name` attaches an existing managed cluster. The service reads the connection string from
its env:

```yaml
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${db.DATABASE_URL}
```

Run migrations either at container start (the FastAPI and Spring
templates do this: `alembic upgrade head` and Flyway on boot) or as a
pre-deploy job:

```yaml
jobs:
  - name: migrate
    kind: PRE_DEPLOY
    source_dir: backend
    dockerfile_path: backend/Dockerfile
    run_command: alembic upgrade head
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${db.DATABASE_URL}
```

SQLite to Postgres gotchas, in the order they bite:

- The URL scheme. SQLAlchemy wants `postgresql+psycopg://` (psycopg 3) or
  `postgresql://` (psycopg2). Managed databases hand out `postgresql://`
  with `?sslmode=require`; keep the query string. Normalise the scheme in
  the settings object, never in the route.
- The driver has to be installed: `psycopg[binary]` or `psycopg2-binary`
  in `requirements.txt`. Missing driver shows up as a run log traceback,
  not a build failure.
- Types. SQLite accepts anything; Postgres does not. `Boolean` columns
  fed `0/1` strings, `DateTime` fed naive strings, and `JSON` fed dicts
  without a `JSON` column type all fail on first insert. Run the tests
  once against a local Postgres (`docker run -e POSTGRES_PASSWORD=x -p 5432:5432 postgres:16`)
  before deploying if there is time; otherwise watch the first write.
- `create_all` at startup is acceptable for a prototype. Say so in the
  demo notes and name Alembic or Flyway as the next step.
- Spring Boot: use `${db.JDBC_DATABASE_URL}` for `SPRING_DATASOURCE_URL`;
  the plain `DATABASE_URL` is not JDBC-shaped.

### 3c. Container registry path

When the GitHub integration is not authorised, or the buildpack keeps
failing, build locally and push an image:

```
doctl registry create <registry-name>
doctl registry login
docker build -t registry.digitalocean.com/<registry-name>/api:<sha> backend
docker push registry.digitalocean.com/<registry-name>/api:<sha>
```

Replace the service's `github:` and `dockerfile_path:` with

```yaml
    image:
      registry_type: DOCR
      repository: api
      tag: <sha>
```

then `doctl apps create --spec` or `doctl apps update`. Pushing a new tag
needs `doctl apps create-deployment <app-id>` or a spec update, because
an unchanged spec reuses the existing image. GHCR and Docker Hub work too
(`registry_type: GHCR` or `DOCKER_HUB`, with `registry` and, for private
images, `registry_credentials` in `username:token` form, plain text on
first submit).

## 4. CORS and the frontend's API base URL

One public URL is the goal. In the worked spec the static site is served
at `/` and the service at `/api` and `/health` through `ingress.rules`, so
the frontend calls same-origin paths and no CORS is needed in production.
For the local dev server, the backend's allowed origins list includes
`http://localhost:5173` (Vite) or `http://localhost:3000` (Next).

If the API must be reachable cross-origin (a separate frontend host),
set the backend's allowed origins to `${APP_URL}` and the frontend's
build-time base URL to `${api.PUBLIC_URL}`; both are bindable variables
the platform fills in. Do not use `*` with credentials.

## 5. Verification

Against the live URL from `DefaultIngress`:

1. `curl -sS -o /dev/null -w "%{http_code}\n" https://<url>/health` returns 200
   and the body names the database check as up.
2. `doctl apps logs <app-id> --type run --tail 50` shows the server start
   line and no traceback.
3. One write, then read it back through the read path:
   `curl -X POST .../api/items/ -d '{...}'` then `curl .../api/items/`.
   The write endpoint's own success message proves nothing.
4. One error path returns the documented error shape (404 or 422), not a
   500.
5. Full-stack: open the site in a browser, perform the main flow, watch
   the network tab for the API call and confirm same-origin.
6. Paste URL, status codes and timestamps into `docs/demo-notes.md`.

What to say in the demo: the URL, what the health check covers, that the
database is a managed dev instance bound through the spec, that secrets
are set in the panel and not in git, what was scaffolded versus written,
and the first thing that broke on deploy and how it was found (the logs
command).

## 6. Custom domain (only if asked)

```yaml
domains:
  - domain: app.example.com
    type: PRIMARY
```

then point a CNAME at the default ingress host. Certificates are
automatic. This is never worth the time in a three-hour session unless
the prompt requires it.

## 7. Fallback

Same Dockerfile, different host, so the demo still happens:

- Locally: `docker build -t app backend && docker run --rm -p 8000:8000 --env-file backend/.env app`,
  then demo on `http://localhost:8000`. Say plainly that the App Platform
  deploy is in progress or failed, and what the failure was.
- A Droplet: `doctl compute droplet create demo --image docker-20-04 --size s-1vcpu-1gb --region nyc3 --ssh-keys <key-id> --wait`
  (the Docker 1-Click image; the slug still says 20-04 but it runs Ubuntu 22.04),
  then `ssh root@<ip>`, `docker compose up -d` with the same image. A
  public IP on port 80 counts as deployed on DigitalOcean.
- Any other host that takes a Dockerfile.

## 8. Cost and cleanup

A basic service and a dev database cost a few dollars a month, billed
hourly. After the interview:

```
doctl apps delete <app-id> --force
doctl registry delete --force          # if a registry was created
doctl compute droplet delete demo --force   # if the fallback was used
```

Revoke the token in the control panel (API, Tokens) afterwards.
