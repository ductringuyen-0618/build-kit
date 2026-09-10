# DigitalOcean references used by this skill

Checked 2026-09-09. Every command, flag, and spec field in `SKILL.md` and
the other reference files is backed by one of these pages. If a page and
the skill disagree, the page wins; fix the skill.

## doctl

- `doctl apps` command index (create, list, get, update, delete, logs,
  create-deployment, list-deployments, propose, spec get/validate,
  list-buildpacks, list-regions, restart):
  https://docs.digitalocean.com/reference/doctl/reference/apps/
- `doctl apps create --spec <file>` with `--wait`, `--upsert`,
  `--update-sources`, `--project-id`, `--format` (columns `ID`,
  `Spec.Name`, `DefaultIngress`, `ActiveDeployment.ID`,
  `InProgressDeployment.ID`, `Created`, `Updated`; there is no `LiveURL`
  column): https://docs.digitalocean.com/reference/doctl/reference/apps/create/
- `doctl apps get <app id>` with the same `--format` columns; `--output
  json` for the full spec:
  https://docs.digitalocean.com/reference/doctl/reference/apps/get/
- `doctl apps logs <app name or id> [component name]`. `--type` defaults
  to `run`, allowed `build, deploy, run, run_restarted, autoscale_event`;
  `--follow`/`-f`; `--tail` (default -1); `--deployment`:
  https://docs.digitalocean.com/reference/doctl/reference/apps/logs/
- `doctl apps spec validate <spec file>` (`--schema-only`):
  https://docs.digitalocean.com/reference/doctl/reference/apps/spec/validate/
- `doctl apps update <id> --spec <file>` (`--wait`, `--update-sources`):
  https://docs.digitalocean.com/reference/doctl/reference/apps/update/
- `doctl apps create-deployment <app id>` (`--force-rebuild`, `--wait`):
  https://docs.digitalocean.com/reference/doctl/reference/apps/create-deployment/
- `doctl apps delete <app id> --force`:
  https://docs.digitalocean.com/reference/doctl/reference/apps/delete/
- `doctl auth init [flags]`: `--context`, `--access-token`/`-t`;
  `doctl auth switch --context <name>`; `doctl auth remove --context <name>`:
  https://docs.digitalocean.com/reference/doctl/reference/auth/init/
- `doctl account get` (`--format Email,Team,UUID,Status`):
  https://docs.digitalocean.com/reference/doctl/reference/account/get/
- `doctl registry create <name>` (`--region`, `--subscription-tier`),
  `doctl registry login` (`--expiry-seconds`, `--read-only`),
  `doctl registry delete --force`:
  https://docs.digitalocean.com/reference/doctl/reference/registry/create/
  https://docs.digitalocean.com/reference/doctl/reference/registry/login/
  https://docs.digitalocean.com/reference/doctl/reference/registry/delete/
- `doctl compute droplet create <name> --image <slug> --size <slug>
  --region <slug> --ssh-keys <ids> --wait`:
  https://docs.digitalocean.com/reference/doctl/reference/compute/droplet/create/

## App spec

- App spec reference. Top-level keys `name, region, services,
  static_sites, workers, jobs, functions, databases, domains, envs,
  alerts, ingress`. Service fields `github, image, source_dir,
  dockerfile_path, build_command, run_command, environment_slug,
  instance_size_slug, instance_count, http_port, health_check, envs`.
  `http_port` default 8080; a `PORT` env var is injected from it if none
  is set. `envs[].scope` is `RUN_TIME` | `BUILD_TIME` |
  `RUN_AND_BUILD_TIME`; `envs[].type` is `GENERAL` | `SECRET`.
  `health_check` fields `http_path`, `port` (defaults to `http_port`),
  `initial_delay_seconds` (0), `period_seconds` (10), `timeout_seconds`
  (1), `success_threshold` (1), `failure_threshold` (9). `ingress.rules[]`
  with `match.path.prefix` or `match.path.exact`, `component.name`,
  `component.preserve_path_prefix` (exclusive with `component.rewrite`),
  plus `redirect` and `cors` blocks. `alerts[].rule` values include
  `DEPLOYMENT_FAILED`, `DEPLOYMENT_LIVE`, `DOMAIN_FAILED`, `DOMAIN_LIVE`,
  `CPU_UTILIZATION`, `MEM_UTILIZATION`, `RESTART_COUNT`:
  https://docs.digitalocean.com/products/app-platform/reference/app-spec/
- Health checks how-to:
  https://docs.digitalocean.com/products/app-platform/how-to/manage-health-checks/
- Environment variables and bindable variables. App-wide `${APP_DOMAIN}`,
  `${APP_URL}`, `${APP_ID}`; component `${_self.PUBLIC_URL}`,
  `${_self.PRIVATE_URL}`, `${_self.PRIVATE_DOMAIN}`, `${_self.PRIVATE_PORT}`,
  `${_self.PUBLIC_ROUTE_PATH}`, `${_self.COMMIT_HASH}` and the same with a
  component name in place of `_self`; database `${<db>.HOSTNAME}`, `PORT`,
  `USERNAME`, `PASSWORD`, `DATABASE`, `DATABASE_URL`, `DATABASE_PRIVATE_URL`,
  `CA_CERT`, `JDBC_DATABASE_URL`, `REDIS_URL`:
  https://docs.digitalocean.com/products/app-platform/how-to/use-environment-variables/
- Secrets: `SECRET` values come back as `EV[...]` after the first submit:
  https://docs.digitalocean.com/products/app-platform/how-to/update-app-spec/
- Databases in the spec. Dev database: `engine: PG`, `name`, optional
  `version`; PostgreSQL only, versions 15 to 18, one size, no standby,
  $7.00 per month. Managed cluster: `cluster_name`, `db_name`, `db_user`,
  `production: true`. `DATABASE_URL` combines the individual parameters.
  Pre-deploy jobs (`kind: PRE_DEPLOY`) for migrations:
  https://docs.digitalocean.com/products/app-platform/how-to/manage-databases/
- Deploy from container images. `image:` with `registry_type` one of
  `DOCR, DOCKER_HUB, GHCR`, `registry`, `repository`, `tag` or `digest`
  (not both), `registry_credentials` as `username:token` in plain text on
  first submit. `doctl apps create-deployment` always pulls the image;
  `update` and `create --upsert` reuse it unless the digest changed:
  https://docs.digitalocean.com/products/app-platform/how-to/deploy-from-container-images/
- Monorepo deploys: `source_dir` per component; the whole repo is cloned
  at build time but only the source directory is available at run time:
  https://docs.digitalocean.com/products/app-platform/how-to/deploy-from-monorepo/
- Custom domains (`domains[].domain`, `type: PRIMARY`, CNAME to the
  default ingress host, automatic certificates):
  https://docs.digitalocean.com/products/app-platform/how-to/manage-domains/
- Pricing and `instance_size_slug` values `apps-s-1vcpu-0.5gb` ($5),
  `apps-s-1vcpu-1gb-fixed` ($10), `apps-s-1vcpu-1gb` ($12),
  `apps-s-1vcpu-2gb`, `apps-s-2vcpu-4gb`, and the `apps-d-*` dedicated
  tiers; `basic-*`/`professional-*` are deprecated:
  https://docs.digitalocean.com/products/app-platform/details/pricing/
- Limits: builds time out after 1 hour, deploys after 30 minutes; images
  over 2 GiB are likely to fail:
  https://docs.digitalocean.com/products/app-platform/details/limits/

## Buildpacks

- Buildpack index. Supported: Python, Node.js, Go, PHP, Ruby, .NET, Rust,
  Bun, Hugo, plus Aptfile for system packages. No Java entry, so Spring
  Boot and other JVM apps use a Dockerfile:
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
  the skill uses a Dockerfile:
  https://docs.digitalocean.com/products/app-platform/reference/buildpacks/go/

## Other

- Docker 1-Click Droplet image slug `docker-20-04`, currently Ubuntu
  22.04 based:
  https://docs.digitalocean.com/products/marketplace/catalog/docker/
- DigitalOcean's own App Platform skills for coding agents (designer,
  migration, deployment, networking, postgres, managed-db-services,
  troubleshooting). Optional; install by `git clone` plus a symlink into
  `~/.claude/skills`, `~/.codex/skills` or `~/.cursor/skills` per its
  README. This skill does not depend on them:
  https://github.com/digitalocean-labs/do-app-platform-skills
- GitHub Action `digitalocean/app_action/deploy@v2` for deploying from
  CI: https://github.com/digitalocean/app_action

## Not verified against a page

- The default run command the Node.js and Go buildpacks pick when none is
  set; the skill sets `run_command` for Node and uses a Dockerfile for Go.
- Whether `${APP_URL}` resolves inside a `static_sites` build-time env.
  The docs demonstrate `${<component>.PUBLIC_URL}` for that case; the
  template uses `${APP_URL}` and the frontend should fall back to
  `window.location.origin` when the variable is blank.
- The full region slug list; `doctl apps list-regions --format Slug`
  prints it.
- Static site pricing tiers and the registry starter tier are quoted from
  the pricing page as of the check date and change over time.
