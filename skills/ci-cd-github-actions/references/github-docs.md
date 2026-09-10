# References for the CI/CD skill

Action versions and API shapes below were checked on 2026-09-09 against the
linked pages. Major versions are the newest tag on each action's releases
page on that date; older majors keep working. Re-check the links before
bumping a version.

## Actions and APIs

- `actions/checkout@v7` (`fetch-depth`, `ref`, `token`):
  https://github.com/actions/checkout
- `actions/setup-python@v7` (`python-version`, `python-version-file`,
  `cache: pip|pipenv|poetry`, `cache-dependency-path`):
  https://github.com/actions/setup-python
- `actions/setup-node@v7` (`node-version`, `node-version-file`,
  `cache: npm|yarn|pnpm`, `cache-dependency-path`; pnpm caching needs
  `pnpm/action-setup` first): https://github.com/actions/setup-node
- `pnpm/action-setup@v6` (`version`, optional when `packageManager` is
  set in `package.json`; `run_install`; does not install Node):
  https://github.com/pnpm/action-setup
- `actions/setup-java@v6` (`distribution: temurin`, `java-version`,
  `cache: maven|gradle|sbt`): https://github.com/actions/setup-java
- `gradle/actions/setup-gradle@v6` (optional; caches and build scans):
  https://github.com/gradle/actions
- `actions/setup-go@v7` (`go-version-file`, `cache` defaults to true):
  https://github.com/actions/setup-go
- `dorny/paths-filter@v4` (optional: run a job only when its folder
  changed; `filters`, outputs `steps.<id>.outputs.<name>`; needs
  `pull-requests: read` on PRs): https://github.com/dorny/paths-filter
- `gitleaks/gitleaks-action@v3` (configured through `env`: `GITHUB_TOKEN`
  required; `GITLEAKS_LICENSE` required only for organisation-owned repos;
  `GITLEAKS_CONFIG`, `GITLEAKS_ENABLE_SUMMARY`):
  https://github.com/gitleaks/gitleaks-action
- `docker/login-action@v4` (`registry`, `username`, `password`):
  https://github.com/docker/login-action
- `docker/metadata-action@v6` (`images`, `tags`; outputs `tags`, `labels`):
  https://github.com/docker/metadata-action
- `docker/build-push-action@v7` (`context`, `file`, `push`, `tags`,
  `labels`, `cache-from`/`cache-to: type=gha`):
  https://github.com/docker/build-push-action
- GHCR: `ghcr.io/OWNER/IMAGE`, `GITHUB_TOKEN` authenticates with
  `packages: write`:
  https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- `digitalocean/app_action/deploy@v2`: inputs `token` (required),
  `app_spec_location` (default `.do/app.yaml`), `app_name`, `project_id`,
  `print_build_logs`, `print_deploy_logs`, `deploy_pr_preview`; outputs
  `app` (JSON with `live_url`), `build_logs`, `deploy_logs`; env vars on
  the step are usable as bindables in the spec:
  https://github.com/digitalocean/app_action
- `digitalocean/action-doctl@v2` (`token`, `version`):
  https://github.com/digitalocean/action-doctl
- GitHub REST, update branch protection
  (`PUT /repos/{owner}/{repo}/branches/{branch}/protection`; body must
  include `required_status_checks` (`strict`, `contexts`, optional
  `checks[]`), `enforce_admins`, `required_pull_request_reviews` (nullable),
  `restrictions` (nullable); optional `required_linear_history`,
  `allow_force_pushes`, `allow_deletions`,
  `required_conversation_resolution`):
  https://docs.github.com/en/rest/branches/branch-protection#update-branch-protection
- GitHub REST, create a repository ruleset
  (`POST /repos/{owner}/{repo}/rulesets`; `name`, `target: branch`,
  `enforcement: active`, `conditions.ref_name.include` accepts
  `~DEFAULT_BRANCH`, rule `required_status_checks` with
  `strict_required_status_checks_policy` and `required_status_checks[].context`;
  parameter-less rules `deletion`, `non_fast_forward`,
  `required_linear_history`):
  https://docs.github.com/en/rest/repos/rules#create-a-repository-ruleset
- GitHub REST, update a repository (`PATCH /repos/{owner}/{repo}` with
  `delete_branch_on_merge`, `allow_auto_merge`):
  https://docs.github.com/en/rest/repos/repos#update-a-repository
- `gh api` (`-X/--method`, `--input -` for a JSON body from stdin, `-F`
  typed fields where `true`/`false`/numbers become JSON types, `-f` raw
  strings): https://cli.github.com/manual/gh_api
- `gh repo edit --delete-branch-on-merge`:
  https://cli.github.com/manual/gh_repo_edit
- `gh secret set <name>` (value from prompt, stdin, `--body` or
  `--env-file`): https://cli.github.com/manual/gh_secret_set
- `gh run list` (`--limit`, `--branch`, `--status`), `gh run view <id>
  --log-failed` (`--job`, `--exit-status`), `gh run watch`,
  `gh run rerun --failed`, `gh pr checks <n> --watch` (`--fail-fast`;
  exit code 8 while pending), `gh workflow run`:
  https://cli.github.com/manual/gh_run_list
  https://cli.github.com/manual/gh_run_view
  https://cli.github.com/manual/gh_run_rerun
  https://cli.github.com/manual/gh_pr_checks
- Workflow syntax (`concurrency` with `cancel-in-progress`,
  `on.push.paths`/`paths-ignore`, `permissions`, `defaults.run.shell`,
  `services`, `environment`, `needs`, `if`):
  https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

## Not verified

- The fine-grained token permission names for the branch-protection and
  ruleset endpoints (the pages say admin or owner access is required).
- Whether the DigitalOcean token used by `app_action` needs a narrower
  scope than full write; the README does not say.
