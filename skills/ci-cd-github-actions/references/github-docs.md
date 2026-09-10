# References used by the CI/CD skill

Checked 2026-09-09.

## Source workflows the patterns were distilled from

- TechPulse `.github/workflows/ci.yml`: single build job with
  `dorny/paths-filter@v3` to detect backend/frontend changes,
  `actions/setup-python@v5` with `cache: pip`, `actions/setup-node@v4`
  with `cache: npm`, ruff, mypy, pytest, prettier `--check`, `tsc --noEmit`,
  `npm run build`, an artifact-directory check, `pip-audit` and
  `npm audit`, concurrency group with cancel-in-progress.
- TechPulse `.github/workflows/deploy.yml`: test job, then build and push
  to GHCR with `:main` and `:<sha>` tags, then deploy, then an E2E gate
  against the live URL.
- agent-os `.github/workflows/ci.yml`: `pnpm/action-setup@v4`,
  `actions/setup-node@v4` with `cache: pnpm`, `pnpm install --frozen-lockfile`,
  lint, build, `pnpm -r run typecheck`, test, `gitleaks/gitleaks-action@v2`
  with `GITHUB_TOKEN`, and a tag-triggered release job with
  `softprops/action-gh-release@v2`.
- salon-hub `api-ci.yml` / `ci.yml`: `actions/setup-java@v4` temurin 17,
  Gradle cache via `actions/cache@v4`, a `services: postgres:15`
  container with `pg_isready` health options, `./gradlew test`,
  `integrationTest`, `bootJar --no-daemon`, artifact uploads;
  `api-publish-docker.yml`: `docker/login-action@v3` and
  `docker/build-push-action@v5` to Docker Hub with `latest` and `sha` tags;
  `web-ci.yml`: npm ci, lint, `test:ci`, build with `paths:` filters.
- portfolio-website `deploy.yml`: `actions/checkout@v5`,
  `actions/setup-node@v5` 22, `npm ci`, `npm run build`,
  `peaceiris/actions-gh-pages@v4` to a deploy branch, `concurrency: pages`.

## Actions and APIs

- `digitalocean/app_action/deploy@v2`: input `token` (required),
  `app_spec_location` (default `.do/app.yaml`), `app_name`, `project_id`,
  `print_build_logs`, `print_deploy_logs`, `deploy_pr_preview`; outputs
  `app`, `build_logs`, `deploy_logs`; env vars on the step are usable as
  bindables in the spec: https://github.com/digitalocean/app_action
- `gitleaks/gitleaks-action@v2`, needs `GITHUB_TOKEN` in `env` and
  `fetch-depth: 0` to scan history: https://github.com/gitleaks/gitleaks-action
- `docker/login-action@v3` (`registry`, `username`, `password`):
  https://github.com/docker/login-action
- `docker/build-push-action@v6` (`context`, `file`, `push`, `tags`):
  https://github.com/docker/build-push-action
- `actions/setup-python@v5` `cache: pip` and `cache-dependency-path`:
  https://github.com/actions/setup-python
- `actions/setup-node@v4` `cache: npm|yarn|pnpm` and
  `cache-dependency-path`: https://github.com/actions/setup-node
- `pnpm/action-setup@v4`: https://github.com/pnpm/action-setup
- `actions/setup-java@v4` `distribution: temurin`, `cache: gradle`:
  https://github.com/actions/setup-java
- `actions/setup-go@v5` `go-version-file: go.mod`:
  https://github.com/actions/setup-go
- GitHub REST, update branch protection
  (`PUT /repos/{owner}/{repo}/branches/{branch}/protection` with
  `required_status_checks`, `enforce_admins`,
  `required_pull_request_reviews`, `restrictions`):
  https://docs.github.com/en/rest/branches/branch-protection#update-branch-protection
- `gh repo edit --delete-branch-on-merge`:
  https://cli.github.com/manual/gh_repo_edit
- `gh run list`, `gh run view --log-failed`, `gh run rerun --failed`,
  `gh pr checks --watch`: https://cli.github.com/manual/gh_run and
  https://cli.github.com/manual/gh_pr_checks
- Workflow syntax (`concurrency`, `permissions`, `defaults.run.shell`,
  `services`): https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions

## Not fetched during research (taken from the source workflows above or prior use)

The action pages for gitleaks, docker, setup-* and the GitHub REST and
gh manual pages were not fetched in this session; their inputs are the
ones used in the source workflows listed above, which run today. The
`digitalocean/app_action` page was fetched and quoted.
