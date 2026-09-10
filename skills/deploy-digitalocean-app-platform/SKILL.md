---
name: deploy-digitalocean-app-platform
description: Deploy a backend service, a static frontend, or both to DigitalOcean App Platform with doctl, with a managed Postgres database attached, and prove the public URL works with curl.
---

# Deploy to DigitalOcean App Platform

## Purpose

Give a repo that runs locally a public HTTPS URL on DigitalOcean App
Platform, with a database bound through the app spec, in about 30 minutes,
using only `doctl` and `curl`. Every command and spec field here is backed
by a page listed in `references/digitalocean-docs.md`.

## When to use

- The task says "deploy on DigitalOcean" or needs a public URL for a demo.
- You are writing or fixing `.do/app.yaml`, or a deploy is failing.
- Not for Kubernetes (DOKS) or Functions. A Droplet is only the fallback.

## Inputs

- A GitHub repo with the service in a folder (`backend/`, `frontend/`, or
  the root). Know the folder, the port the process listens on, and the
  health path. If there is no health endpoint, add `GET /health` first.
- `doctl` installed and authenticated (step 1).
- Optional: a Dockerfile. This kit ships one per stack at
  `templates/<stack>/Dockerfile` (`python-fastapi`, `node-typescript`,
  `go`, `java-spring-boot`, `nextjs`, `vite-react`).

## Steps

### 1. Prerequisites (3 min)

```
doctl version
doctl account get
```

If `doctl account get` fails, the human runs `doctl auth init` (or
`doctl auth init --context <name>` to keep a separate login) and pastes
the token. Never ask for, read, echo, or store the token yourself.

For GitHub-sourced builds the DigitalOcean GitHub app must have access to
the repo. That is a one-time click in the control panel: Apps, Create App,
GitHub, Manage Access. If that cannot be done, deploy a container image
instead (`references/registry-and-fallback.md`).

### 2. Choose buildpack or Dockerfile (2 min)

App Platform builds with a buildpack when it recognises the repo and with
a Dockerfile when `dockerfile_path` is set. Java and Go use a Dockerfile
(no Java buildpack exists; the Go buildpack's default run command is
undocumented). Otherwise: buildpack when the app is one process with plain
dependencies, Dockerfile when it needs system packages, exact runtime
pins, a monorepo workspace, or model downloads.

| Stack | Build | build_command | run_command | Health path | Port | Test |
| --- | --- | --- | --- | --- | --- | --- |
| Python (FastAPI/Flask/Django) | buildpack or Dockerfile | (buildpack) | `uvicorn <module>:app --host 0.0.0.0 --port $PORT` | `/health` | `$PORT` | `pytest -q` |
| Node/TypeScript (Express/Fastify) | buildpack or Dockerfile | `npm ci && npm run build` | `npm start` | `/health` | `process.env.PORT` | `npm test` |
| Next.js | buildpack or Dockerfile | `npm ci && npm run build` | `npm start` (`next start -p $PORT`) | `/api/health` | `$PORT` | `npm run lint && npx tsc --noEmit` |
| Go | Dockerfile | (Dockerfile) | binary from the Dockerfile `CMD` | `/healthz` | `PORT` env, default 8080 | `go test ./...` |
| Java / Spring Boot | Dockerfile | (Dockerfile) | `java -jar app.jar`, `server.port=${PORT:8080}` | `/actuator/health` | 8080 | `./gradlew test` |
| Vite/React static | `static_sites` component | `npm ci && npm run build` | none | none | none | `npm run build` |

Buildpack: the platform sets `PORT`; the process must listen on it.
Dockerfile: set `http_port` in the spec to the port the container listens
on. Buildpack detection rules per language are in
`references/digitalocean-docs.md`.

### 3. Write the spec (5 min)

Copy `templates/do-app.yaml` from this kit to `.do/app.yaml` at the repo
root. It contains one web service, one static site, one dev Postgres
database, one pre-deploy migration job, and an ingress that serves both
under one URL. Per-stack service blocks to paste over the `api` block are
in `templates/<stack>/app-component.yaml`. Edit:

- `name`, `region` (`doctl apps list-regions --format Slug` lists slugs).
- `github.repo` (`owner/name`) and `branch` on every component.
- `source_dir`: the folder the build runs in, per component.
- `dockerfile_path` (Dockerfile) or `build_command` + `run_command` (buildpack).
- `http_port` to match the process, and `health_check.http_path`.
- `health_check.initial_delay_seconds`: default 0, and the platform gives
  about 90 seconds of failures before marking the deploy failed. Use 15
  for Python/Node, 40 for Spring Boot. Raise `timeout_seconds` (default 1)
  if the health handler touches the database.
- Delete `static_sites`, the `web` ingress rule, or `jobs` if unused.

Secrets: declare `type: SECRET` with an empty value in the committed
file, then set the value in the control panel (Apps, your app, Settings,
component, Environment Variables). `${APP_URL}`, `${<component>.PUBLIC_URL}`
and `${<db>.DATABASE_URL}` are filled by the platform; the full list is in
`references/digitalocean-docs.md`.

```
doctl apps spec validate .do/app.yaml
```

Fix every error it prints before continuing.

### 4. Create and watch (10 min)

```
doctl apps create --spec .do/app.yaml --format ID,DefaultIngress
doctl apps logs <app-id> --type build --follow
doctl apps logs <app-id> --type deploy --follow
doctl apps logs <app-id> --type run --follow
doctl apps get <app-id> --format DefaultIngress --no-header
```

`DefaultIngress` is the public URL. A component name after the app id
narrows logs (`doctl apps logs <app-id> api --type build`); `--wait` on
`create` or `update` blocks until the deployment finishes. After editing
the spec: `doctl apps update <app-id> --spec .do/app.yaml`. To redeploy
an unchanged spec: `doctl apps create-deployment <app-id>`.

Read the first failure in the logs and fix that one thing; the common
ones are in `references/troubleshooting.md`. No green deployment after
two fixes means go to Fallback.

### 5. Database and migrations (already in the template)

```yaml
databases:
  - name: db
    engine: PG
    production: false
```

`production: false` provisions a dev Postgres with the app (one size, no
standby, versions 15 to 18, pin with `version: "16"`). The service reads
`${db.DATABASE_URL}` from its env. Spring Boot reads
`${db.JDBC_DATABASE_URL}` plus `${db.USERNAME}` and `${db.PASSWORD}`.

Run migrations either at container start (the kit's Dockerfiles for
Python and Spring Boot do this) or as the `PRE_DEPLOY` job in the
template, whose `run_command` is the stack's migration command. Per-stack
commands, driver names, and the SQLite-to-Postgres pitfalls are in
`references/database-and-migrations.md`. Read it before the first write
hits Postgres.

### 6. CORS

With the template's ingress, the frontend is served at `/` and the API at
`/api` and `/health` on one origin, so production needs no CORS. The
backend's allowed-origins list still needs the local dev origin
(`http://localhost:5173` for Vite, `http://localhost:3000` for Next.js).
If the frontend lives on another host, set the backend's allowed origins
to that URL and the frontend's build-time API base URL to
`${api.PUBLIC_URL}`. Never combine `*` with credentials.

### 7. Verify against the live URL (5 min)

Set `URL=$(doctl apps get <app-id> --format DefaultIngress --no-header)`.
Every item must pass; paste the outputs into your notes or README.

```
# 1. Health returns 200 and the body reports the database check
curl -sS -w "\n%{http_code}\n" "$URL/health"

# 2. Run logs show the server start line and no traceback
doctl apps logs <app-id> --type run --tail 50

# 3. Write, then read back through a different endpoint (the write's own
#    success message proves nothing)
curl -sS -X POST "$URL/api/<resource>/" -H "Content-Type: application/json" \
  -d '{"name":"smoke"}' -w "\n%{http_code}\n"
curl -sS "$URL/api/<resource>/" -w "\n%{http_code}\n"

# 4. An error path returns the documented shape, not a 500
curl -sS -o /dev/null -w "%{http_code}\n" "$URL/api/<resource>/does-not-exist"

# 5. Static site serves HTML (full-stack only)
curl -sS -o /dev/null -w "%{http_code} %{content_type}\n" "$URL/"

# 6. CORS preflight from the local dev origin is accepted (only if the
#    browser will call the API cross-origin)
curl -sS -o /dev/null -w "%{http_code}\n" -X OPTIONS "$URL/api/<resource>/" \
  -H "Origin: http://localhost:5173" -H "Access-Control-Request-Method: GET"
```

Then open `$URL` in a browser, perform the main flow, and confirm in the
network tab that API calls go to the same origin.

### 8. Fallback

If minute 20 arrives with no green deployment, stop debugging the
platform and demo the same Dockerfile elsewhere, saying so plainly:
locally with `docker build -t app backend && docker run --rm -p 8080:8080 --env-file backend/.env app`,
or on a DigitalOcean Droplet running the same image (commands in
`references/registry-and-fallback.md`).

### 9. Cleanup

Everything is billed hourly and costs a few dollars a month. When the app
is no longer needed:

```
doctl apps delete <app-id> --force
doctl registry delete --force               # only if a registry was created
doctl compute droplet delete <name> --force # only if the fallback was used
```

Revoke the API token in the control panel (API, Tokens) afterwards.

## Outputs

- `.do/app.yaml` committed at the repo root, secrets empty.
- The app id and public URL, recorded in the README's deploy section.
- The verification outputs from step 7.

## Done when

- `doctl apps get <app-id> --format ActiveDeployment.ID` prints an id.
- All six curl checks in step 7 pass against the public URL.
- The README says how to redeploy (`doctl apps update`) and how to delete.
