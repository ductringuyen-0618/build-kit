---
name: ci-cd-github-actions
description: Set up GitHub Actions for a new repo of any stack, from a minimal CI workflow in the first commit through secret scanning, branch protection, a main-only deploy job, and reading a red run fast.
---

# CI/CD with GitHub Actions

## Purpose

From the first commit, every push shows a green check that really ran
lint, typecheck, tests and build. The default branch cannot be merged
into while that check is red. A deploy job runs only on the default
branch and only after CI passed. Nothing here depends on a particular
project; every command is either stock GitHub tooling or listed per
stack in the table below. Action versions were checked on the date in
`references/github-docs.md`.

## When to use

- Scaffolding a new repository (before the first push).
- Asked for CI, tests in CI, a deploy pipeline, branch protection, or
  secret scanning.
- A workflow run is red and has to be read and fixed quickly.

## Inputs

- Repository `OWNER/REPO`, its default branch (assumed `main` below), and
  a `gh` CLI logged in with admin rights on the repo (`gh auth status`).
- The stack of each component and the folder it lives in (for example
  `backend/` Python plus `frontend/` Node, or a single root package).
- The package manager and lockfile in use (`requirements.txt`,
  `package-lock.json`, `pnpm-lock.yaml`, `gradlew`, `go.mod`).
- The deploy target, if any: DigitalOcean App Platform (needs a
  `.do/app.yaml`, see `templates/do-app.yaml` and the
  `deploy-digitalocean-app-platform` skill) or a container image on GHCR.
- Secrets are created by a human in the repo settings. Never read, print
  or paste a token value.

## Steps

### 1. Minimal `ci.yml` in the first commit

Copy `templates/ci.yml` to `.github/workflows/ci.yml` (pnpm workspaces:
`templates/ci-monorepo.yml`). Edit every line marked `# CHANGE:`. Delete
the job for a component the repo does not have. Where
`templates/<stack>/ci-job.yml` exists for the stack, its job can replace
the template's backend or frontend job wholesale. The shape that matters:

- Triggers: `push` to the default branch, `pull_request` to it, and
  `workflow_dispatch`. Add branch patterns to `push` only if pushes
  without a PR must also be checked.
- `concurrency` keyed on workflow and ref with `cancel-in-progress: true`,
  so a second push cancels the run still going instead of queueing.
- `permissions: contents: read` at the top; widen per job only when a job
  writes (packages, pages).
- One job per component, each with `defaults.run.working-directory`.
  Separate jobs give separate status checks, which branch protection
  needs.
- Step order in a job: install, lint, typecheck, test, build. Never
  `|| true` or `|| echo` past a failure. A step that cannot fail is not a
  check.
- Test environment: put every variable the app's config reads at import
  or startup into the job's `env:` with throwaway values, and keep
  `.env.example` in sync. CI never talks to a real external service.

Commit the workflow together with the scaffold, a health endpoint and one
passing test, so the first run is green.

### 2. Caching

Cache through the setup action, not a hand-written `actions/cache` step:

| Setup action | Input | Note |
| --- | --- | --- |
| `actions/setup-python@v7` | `cache: pip`, `cache-dependency-path: <dir>/requirements.txt` | also `pipenv`, `poetry` |
| `actions/setup-node@v7` | `cache: npm` (or `yarn`), `cache-dependency-path: <dir>/package-lock.json` | path is from the repo root even with a working directory set |
| `pnpm/action-setup@v6` then `actions/setup-node@v7` | `cache: pnpm` | pnpm must be installed before setup-node |
| `actions/setup-java@v6` | `cache: gradle` or `cache: maven` | |
| `actions/setup-go@v7` | `go-version-file: <dir>/go.mod` | module cache is on by default |

### 3. Per-stack lint, typecheck, test, build

| Stack | Setup | Lint | Typecheck | Test | Build |
| --- | --- | --- | --- | --- | --- |
| Python | `setup-python` 3.12; `pip install -r requirements.txt ruff mypy pytest` | `ruff check . && ruff format --check .` | `mypy . --ignore-missing-imports` | `pytest -q` | `python -c "import <app module>"` |
| Node/TypeScript | `setup-node` 22; `npm ci` | `npm run lint` | `npx tsc --noEmit` | `npm test` | `npm run build` |
| pnpm monorepo | `pnpm/action-setup` then `setup-node`; `pnpm install --frozen-lockfile` | `pnpm lint` | `pnpm -r --if-present run typecheck` | `pnpm test` | `pnpm build` |
| Vite/React | `setup-node` 22; `npm ci` | `npm run lint` | `npx tsc --noEmit` | e2e only if specs exist | `npm run build && test -d dist` |
| Next.js | `setup-node` 22; `npm ci` | `npm run lint` | `npx tsc --noEmit` | `npm test` if present | `npm run build` |
| Java Spring Boot | `setup-java` temurin 17, `cache: gradle`; `chmod +x gradlew` | `./gradlew check -x test --no-daemon` | compiler | `./gradlew test --no-daemon` (Postgres as a `services:` container if needed) | `./gradlew bootJar --no-daemon` |
| Go | `setup-go` with `go-version-file` | `gofmt -l .` must print nothing; `go vet ./...` | compiler | `go test ./...` | `go build ./...` |

Script names (`lint`, `test`, `build`, `typecheck`) must exist in the
package manifest; add them there rather than inventing new ones in CI.

### 4. Secret scanning

The `secrets` job in both CI templates runs `gitleaks/gitleaks-action@v3`
on a `fetch-depth: 0` checkout, so it scans history rather than the tip.
It belongs in the first commit because that commit is where a pasted
token is most likely (`.env` files, deploy specs, notebook outputs).
Personal repos need only `GITHUB_TOKEN`; organisation-owned repos also
need a free `GITLEAKS_LICENSE` secret. Add a `.gitleaks.toml` only to
allow-list a confirmed false positive, never to silence a real hit. If a
real secret is found, rotate it; deleting the commit is not enough.

### 5. Branch protection and delete-branch-on-merge

After the first green run, require the check names (each job's `name:`,
or its id if unnamed) on the default branch. Replace `OWNER/REPO` and the
context strings:

```
gh api -X PUT repos/OWNER/REPO/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  --input - <<'EOF'
{
  "required_status_checks": { "strict": true, "contexts": ["Backend", "Frontend", "Secret scan"] },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
EOF
gh repo edit OWNER/REPO --delete-branch-on-merge
gh api repos/OWNER/REPO/branches/main/protection --jq .required_status_checks.contexts
```

The four keys in the body are all required by the endpoint; the two
`null`s mean "not configured". `strict: true` forces a branch to be up to
date with the default branch before merging. `enforce_admins: false`
leaves the repository owner an escape hatch for a solo build; state that
choice when presenting. The last command verifies. For the newer rulesets
API and the merge-queue variant see `references/branch-protection.md`.

### 6. Deploy job on the default branch

Copy `templates/deploy-do.yml` to `.github/workflows/deploy.yml`, keep one
of its two variants and delete the other:

- **App Platform**: `digitalocean/app_action/deploy@v2` reads
  `.do/app.yaml`, creates the app on the first run and updates it after.
  It needs the `DIGITALOCEAN_ACCESS_TOKEN` repository secret, which a
  human creates (`gh secret set DIGITALOCEAN_ACCESS_TOKEN` prompts for the
  value). Secrets passed as `env:` on the step are usable in the spec as
  `${NAME}`.
- **GHCR image**: `docker/login-action@v4` with `GITHUB_TOKEN`, then
  `docker/build-push-action@v7` pushing `:latest` and `:<sha>` tags. The
  job needs `packages: write`. Any host that pulls images can run it.

The workflow triggers on `workflow_run` of the CI workflow (matched by its
`name:`) on the default branch and checks `conclusion == 'success'`, so a
red CI never deploys. `workflow_dispatch` allows a manual re-deploy.
`concurrency` with `cancel-in-progress: false` stops one deploy from
being killed by the next.

### 7. Reading a red run

```
gh run list --limit 5
gh run view <run-id> --log-failed
gh pr checks <pr-number> --watch
gh run rerun <run-id> --failed
```

`--log-failed` prints only the failing step's log. Read the first error
line, not the last; later lines are usually consequences.

### 8. The three common failures

| Symptom in the log | Cause | Fix |
| --- | --- | --- |
| formatter lists files or says "Would reformat" (`ruff format --check`, `prettier --check`, `gofmt -l`) | code written faster than it was formatted | run the formatter locally, commit `style: format` |
| `npm ci` reports lockfile out of sync; `pnpm install --frozen-lockfile` fails; pip resolves a different version | a dependency was added by hand without updating the lockfile | run the plain install once locally, commit the lockfile |
| config module fails at import: `KeyError`, `ValidationError`, missing field, `Cannot read properties of undefined` | variable present in local `.env`, absent in CI | add it to the job's `env:` with a safe value and to `.env.example` |

More cases (database needed by tests, Windows-authored scripts, native
binaries, wrong check name in protection) are in
`references/red-runs.md`.

## Outputs

- `.github/workflows/ci.yml` with lint, typecheck, test, build and secret
  scan jobs, green on the latest commit.
- Branch protection on the default branch requiring those job names, and
  delete-branch-on-merge enabled.
- `.github/workflows/deploy.yml` (when a deploy target exists) that ran on
  the default branch and printed a live URL or pushed an image tag.

## Done when

- `gh run list --limit 1` shows `completed success` for the latest commit
  on the default branch, and the run's log shows each step executed.
- `gh api repos/OWNER/REPO/branches/main/protection --jq
  .required_status_checks.contexts` lists every CI job name.
- A deliberately failing test pushed on a branch turns the check red and
  blocks the merge; reverting it turns the check green again.
- The deploy run on the default branch shows a URL that answers, or the
  image tag is visible under the repository's Packages.
