# DigitalOcean references used by this skill

Checked 2026-09-09. Quote or paraphrase per URL; anything in the skill not
backed here is marked as a judgment call in the skill text.

## doctl

- `doctl apps` command index (create, list, get, update, delete, logs,
  create-deployment, list-deployments, propose, spec get/validate,
  list-buildpacks, restart):
  https://docs.digitalocean.com/reference/doctl/reference/apps/
- `doctl apps get <app id> [flags]`. `--format` takes a comma-separated
  column list from `ID, Spec.Name, DefaultIngress, ActiveDeployment.ID,
  InProgressDeployment.ID, Created, Updated`. Text output is basic; use
  `--output json` for the full spec:
  https://docs.digitalocean.com/reference/doctl/reference/apps/get/
- `doctl apps logs <app name or id> <component name (defaults to all components)> [flags]`.
  `--type` defaults to `run`, allowed `build, deploy, run, run_restarted, autoscale_event`;
  `--follow`/`-f`; `--tail` (default -1); `--deployment`:
  https://docs.digitalocean.com/reference/doctl/reference/apps/logs/
- `doctl apps create --spec <file>` also accepts `--wait` and
  `--project-id`; `doctl apps update <id> --spec <file>`;
  `doctl apps delete <id> --force` (from the index page above).

## App spec

- App spec reference (top-level keys `name, region, services,
  static_sites, workers, jobs, functions, databases, domains, envs,
  alerts, ingress`; service fields `github, source_dir, dockerfile_path,
  build_command, run_command, environment_slug, instance_size_slug,
  instance_count, http_port, health_check, envs`; env `scope` and
  `type: SECRET`):
  https://docs.digitalocean.com/products/app-platform/reference/app-spec/
- Environment variables and bindable variables. App-wide `${APP_DOMAIN}`,
  `${APP_URL}`, `${APP_ID}`; component `${_self.PUBLIC_URL}`,
  `${_self.PRIVATE_URL}`, `${_self.PRIVATE_DOMAIN}`, `${_self.PRIVATE_PORT}`,
  `${_self.PUBLIC_ROUTE_PATH}`, `${_self.COMMIT_HASH}` and the same with a
  component name in place of `_self`; database `${<db>.HOSTNAME}`, `PORT`,
  `USERNAME`, `PASSWORD`, `DATABASE`, `DATABASE_URL`, `DATABASE_PRIVATE_URL`,
  `CA_CERT`, `JDBC_DATABASE_URL`, `REDIS_URL`. Scopes `RUN_TIME` and
  `BUILD_TIME` are documented there; `RUN_AND_BUILD_TIME` is in the app
  spec reference:
  https://docs.digitalocean.com/products/app-platform/how-to/use-environment-variables/
- Databases in the spec. Dev database: `engine: PG`, `name`, optional
  `version`. Managed cluster: `cluster_name`, `db_name`, `db_user`,
  `production: true`. `DATABASE_URL` combines the individual parameters.
  Pre-deploy jobs: `jobs: - kind: PRE_DEPLOY` for migrations:
  https://docs.digitalocean.com/products/app-platform/how-to/manage-databases/
- Deploy from container images. `image:` with `registry_type` one of
  `DOCR, DOCKER_HUB, GHCR`, `registry`, `repository`, `tag` or `digest`
  (not both), `registry_credentials` as `username:token` in plain text on
  first submit. `doctl apps create-deployment` always pulls the image;
  `update` and `create --upsert` reuse it unless the digest changed:
  https://docs.digitalocean.com/products/app-platform/how-to/deploy-from-container-images/
- Monorepo deploys: `source_dir` per component; the whole repo is cloned
  but only the source directory is available at run time:
  https://docs.digitalocean.com/products/app-platform/how-to/deploy-from-monorepo/

## Buildpacks

- Buildpack index. Supported: Python, Node.js, Go, PHP, Ruby, .NET, Rust,
  Bun, Hugo, plus Aptfile for system packages. No Java entry, so Spring
  Boot uses a Dockerfile:
  https://docs.digitalocean.com/products/app-platform/reference/buildpacks/
- Python: detected by `requirements.txt`, `Pipfile`, `setup.py`, or
  `pyproject.toml` with `uv.lock` and `.python-version`. Default 3.13.x,
  pin with `runtime.txt` (`python-3.12.4`). A run command is required.
  Gunicorn needs `--worker-tmp-dir /dev/shm`:
  https://docs.digitalocean.com/products/app-platform/reference/buildpacks/python/
- Node.js: detected by `package.json` with `package-lock.json`,
  `yarn.lock` or `pnpm-lock.yaml`; preference yarn, then pnpm, then npm.
  The `build` script runs by default. The app must listen on `PORT`.
  Pin with `engines.node`; default 22.x:
  https://docs.digitalocean.com/products/app-platform/reference/buildpacks/nodejs/
- Go: detected by `go.mod` (also dep, Godep, govendor, Glide files).
  Version from `go.mod`, default 1.24, supports 1.11 to 1.26. Uses the
  Heroku Go buildpack. The docs do not state the default run command, so
  the skill recommends a Dockerfile or an explicit `run_command`:
  https://docs.digitalocean.com/products/app-platform/reference/buildpacks/go/

## Other

- DigitalOcean's own App Platform skills for coding agents,
  `npx skills add digitalocean-labs/do-app-platform-skills`:
  https://www.digitalocean.com/blog/deploy-smarter-with-ai-app-platform-skills-on-digitalocean
- GitHub Action `digitalocean/app_action/deploy@v2` (used by the CI/CD
  skill): https://github.com/digitalocean/app_action

## Not verified against docs (judgment calls in the skill)

- `health_check.initial_delay_seconds` field name and the 30-second
  Spring Boot recommendation.
- `ingress.rules` with `component.preserve_path_prefix` and
  `match.path.prefix` (from the app spec reference structure; example
  not fetched in full).
- `doctl compute droplet create` flags and the `docker-20-04` image slug
  in the fallback section.
- `doctl registry create`, `doctl registry login`, `doctl registry delete`.
