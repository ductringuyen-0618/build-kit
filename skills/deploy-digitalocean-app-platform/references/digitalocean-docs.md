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

- DigitalOcean's own App Platform skills for coding agents. The repo
  README installs by `git clone` plus a symlink into `~/.claude/skills`,
  `~/.codex/skills` or `~/.cursor/skills` (the launch blog post mentions
  an `npx skills add` form; the README is authoritative):
  https://github.com/digitalocean-labs/do-app-platform-skills and
  https://www.digitalocean.com/blog/deploy-smarter-with-ai-app-platform-skills-on-digitalocean
- GitHub Action `digitalocean/app_action/deploy@v2` (used by the CI/CD
  skill): https://github.com/digitalocean/app_action

## Verified in a second pass (2026-09-09)

Items the first pass listed as judgment calls, since checked against the
pages named:

- `doctl auth init [flags]`: `--context`, `--access-token`/`-t`,
  `--token-validation-server`; `doctl auth switch --context <name>`:
  https://docs.digitalocean.com/reference/doctl/reference/auth/init/
- `doctl account get` (`--format Email,Team,UUID,Status`):
  https://docs.digitalocean.com/reference/doctl/reference/account/get/
- `doctl apps create --spec <file>` flags `--wait`, `--upsert`,
  `--update-sources`, `--project-id`, `--format` (columns `ID`,
  `Spec.Name`, `DefaultIngress`, `ActiveDeployment.ID`,
  `InProgressDeployment.ID`, `Created`, `Updated`; there is no `LiveURL`
  column): https://docs.digitalocean.com/reference/doctl/reference/apps/create/
- `doctl apps spec validate <spec file>` (`--schema-only`):
  https://docs.digitalocean.com/reference/doctl/reference/apps/spec/validate/
- `doctl apps delete <app id> --force`:
  https://docs.digitalocean.com/reference/doctl/reference/apps/delete/
- `doctl apps create-deployment <app id>` (`--force-rebuild`, `--wait`):
  https://docs.digitalocean.com/reference/doctl/reference/apps/create-deployment/
- `health_check` fields `http_path`, `port` (defaults to `http_port`),
  `initial_delay_seconds` (default 0), `period_seconds` (10),
  `timeout_seconds` (1), `success_threshold` (1), `failure_threshold` (9):
  https://docs.digitalocean.com/products/app-platform/reference/app-spec/
  and https://docs.digitalocean.com/products/app-platform/how-to/manage-health-checks/
- `ingress.rules[]` with `match.path.prefix` or `match.path.exact`,
  `component.name`, `component.preserve_path_prefix` (exclusive with
  `component.rewrite`), plus `redirect` and `cors` blocks: app spec
  reference above.
- `alerts[].rule` values include `DEPLOYMENT_FAILED`, `DEPLOYMENT_LIVE`,
  `DOMAIN_FAILED`, `DOMAIN_LIVE`, `CPU_UTILIZATION`, `MEM_UTILIZATION`,
  `RESTART_COUNT`: app spec reference above.
- `instance_size_slug` current values `apps-s-1vcpu-0.5gb` ($5),
  `apps-s-1vcpu-1gb-fixed` ($10), `apps-s-1vcpu-1gb` ($12),
  `apps-s-1vcpu-2gb`, `apps-s-2vcpu-4gb`, and the `apps-d-*` dedicated
  tiers; `basic-*`/`professional-*` are deprecated:
  https://docs.digitalocean.com/products/app-platform/details/pricing/
- `http_port` default 8080; a `PORT` env var is injected from it if none is
  set. `envs[].scope` `RUN_TIME` | `BUILD_TIME` | `RUN_AND_BUILD_TIME`,
  `envs[].type` `GENERAL` | `SECRET`; `SECRET` values come back as
  `EV[...]` after first submit: app spec reference and
  https://docs.digitalocean.com/products/app-platform/how-to/update-app-spec/
- Dev databases: PostgreSQL only, versions 15 to 18, one size, no standby,
  $7.00 per month; connection exposed as `${<db>.DATABASE_URL}`:
  https://docs.digitalocean.com/products/app-platform/how-to/manage-databases/
- `doctl registry create <name>` (`--region`, `--subscription-tier`),
  `doctl registry login` (`--expiry-seconds`, `--read-only`),
  `doctl registry delete --force`:
  https://docs.digitalocean.com/reference/doctl/reference/registry/create/
  https://docs.digitalocean.com/reference/doctl/reference/registry/login/
  https://docs.digitalocean.com/reference/doctl/reference/registry/delete/
- `doctl compute droplet create <name> --image <slug> --size <slug>
  --region <slug> --ssh-keys <ids> --wait`:
  https://docs.digitalocean.com/reference/doctl/reference/compute/droplet/create/
- Docker 1-Click image slug `docker-20-04`, currently Ubuntu 22.04 based:
  https://docs.digitalocean.com/products/marketplace/catalog/docker/
- Limits: builds time out after 1 hour, deploys after 30 minutes; images
  over 2 GiB are likely to fail:
  https://docs.digitalocean.com/products/app-platform/details/limits/
- do-app-platform-skills README (install by clone and symlink; skills:
  designer, migration, deployment, networking, postgres,
  managed-db-services, troubleshooting):
  https://github.com/digitalocean-labs/do-app-platform-skills

## Still not verified

- The default run command the Node.js and Go buildpacks pick when none is
  set; the skill sets `run_command` explicitly for both.
- Whether `${APP_URL}` resolves inside a `static_sites` build-time env.
  The docs demonstrate `${<component>.PUBLIC_URL}` for that case; the
  templates use `${APP_URL}` and the same-origin fallback covers a blank.
- The authoritative region slug list; `doctl apps list-regions --format Slug`
  prints it.
