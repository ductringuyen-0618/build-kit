# Troubleshooting a failing App Platform deploy

Companion to step 4 of `SKILL.md`. Find the first failure, match it below,
apply one fix, redeploy. Two fixes without a green deployment means go to
the fallback.

## Where to look

| Symptom | Command |
| --- | --- |
| Spec rejected before anything runs | `doctl apps spec validate .do/app.yaml` |
| Build failed | `doctl apps logs <app-id> --type build` |
| Build passed, deploy failed | `doctl apps logs <app-id> --type deploy` |
| Deploy passed, app returns errors or restarts | `doctl apps logs <app-id> --type run` |
| Which deployment is active or in progress | `doctl apps get <app-id> --format ActiveDeployment.ID,InProgressDeployment.ID` |
| Full spec as the platform stored it | `doctl apps spec get <app-id>` |
| Past deployments | `doctl apps list-deployments <app-id>` |

Add a component name after the app id to narrow the logs to one
component: `doctl apps logs <app-id> api --type build`.

## Spec validation errors

| Message contains | Fix |
| --- | --- |
| `unknown field` | A typo, or a field at the wrong nesting level. Compare with `templates/do-app.yaml`. |
| `repo ... not found` or `GitHub` | The DigitalOcean GitHub app has no access to the repo, or `repo` is not `owner/name`. Authorise in the control panel or switch to the image path in `references/registry-and-fallback.md`. |
| `region` | Use a slug from `doctl apps list-regions --format Slug` (`nyc`, `ams`, `sfo`, `sgp`, `fra`, `lon`, `blr`, `syd`, `tor`). |
| `instance_size_slug` | Current slugs are `apps-s-1vcpu-0.5gb`, `apps-s-1vcpu-1gb-fixed`, `apps-s-1vcpu-1gb`, `apps-s-1vcpu-2gb`, `apps-s-2vcpu-4gb`; `basic-*` and `professional-*` are deprecated. |
| `preserve_path_prefix` and `rewrite` | They are exclusive; keep one per ingress rule. |

## Build failures

| Log line | Cause | Fix |
| --- | --- | --- |
| `No buildpack groups passed detection` | The buildpack did not recognise `source_dir`. | Check `source_dir` points at the folder with `requirements.txt`, `package.json` + lockfile, or `go.mod`. Java has no buildpack: set `dockerfile_path`. |
| `dockerfile_path ... not found` | Path is relative to the repo root, not to `source_dir`. | Use `backend/Dockerfile`, not `Dockerfile`. |
| `COPY failed` in the Docker build | The Dockerfile's build context is `source_dir`. | Make paths in `COPY` relative to `source_dir`, or set `source_dir: /` and adjust. |
| `npm ERR! missing script: build` | `build_command` calls a script the `package.json` lacks. | Add the script or drop `build_command`. |
| `ERESOLVE` or lockfile mismatch | `npm ci` refuses a stale lockfile. | Run `npm install` locally, commit the lockfile. |
| Python version error | Default Python is 3.13. | Pin with `runtime.txt` (`python-3.12.4`) or `.python-version`, or use the Dockerfile. |
| Go version error | `go.mod` declares a version the buildpack lacks. | Use the Dockerfile with a matching `golang:` base image. |
| Build exceeds 1 hour or image over 2 GiB | Large dependencies (ML models, headless browsers). | Multi-stage Dockerfile; download models at run time to a mounted path, or trim dependencies. |

## Deploy failures

| Log line | Cause | Fix |
| --- | --- | --- |
| `health check failed` or `Readiness probe failed` | The process is not answering on `http_port` at `health_check.http_path` within the window. | Confirm the process listens on `0.0.0.0` and the same port as `http_port` (buildpack: `$PORT`). Confirm the path returns 200 without auth. Raise `initial_delay_seconds` (Spring Boot: 40). |
| `connection refused` in the deploy log | Wrong port. | Dockerfile `EXPOSE`/`ENV PORT` and spec `http_port` must agree. |
| Container exits immediately | Startup crash. | Read `--type run` for the traceback; usually a missing env var or a missing database driver. |
| Job `migrate` failed | Migration error before the service started. | `doctl apps logs <app-id> migrate --type run`. Fix the migration or, for a prototype, drop the job and use `create_all` at startup. |
| Deploy exceeds 30 minutes | Health never passes; the platform keeps retrying. | Cancel by pushing a fix or `doctl apps update` with a corrected spec. |

## Run-time failures after a green deploy

| Symptom | Cause | Fix |
| --- | --- | --- |
| 500 on the first database call | Driver missing, or SQLite-style values sent to Postgres. | See `references/database-and-migrations.md`. |
| `ModuleNotFoundError: psycopg` or `Cannot find module 'pg'` | Driver not in the dependency file. | Add it, commit, redeploy. |
| Browser shows CORS error | Frontend and API on different origins, or `ALLOWED_ORIGINS` empty. | Use the same-origin ingress rules, or set the backend's allowed origins to the frontend's URL. Check with the OPTIONS curl in step 7. |
| Frontend calls `http://localhost:8000` in production | Build-time API base URL not set. | Set the `BUILD_TIME` env var on the static site (`VITE_API_BASE_URL`, `NEXT_PUBLIC_API_BASE_URL`) and redeploy; build-time vars require a rebuild. |
| 404 on `/api/...` but `/health` works | Ingress rule missing or `preserve_path_prefix` absent, so the backend sees `/items` instead of `/api/items`. | Add the rule with `preserve_path_prefix: true`. |
| 307 redirect then CORS failure | Framework redirects `/api/items` to `/api/items/` and the redirect carries no CORS headers. | Call the canonical path (with or without trailing slash, whichever the router defines). |
| Secret is empty at run time | `type: SECRET` with `value: ""` was committed and never filled. | Set the value in the control panel, then `doctl apps create-deployment <app-id>`. |
| Static site shows old build | `deploy_on_push` off, or the push went to another branch. | `doctl apps create-deployment <app-id>` or check `branch`. |
| Every push triggers a slow rebuild | `deploy_on_push: true` on every component. | Set it to `false` while iterating, back to `true` for the demo. |
