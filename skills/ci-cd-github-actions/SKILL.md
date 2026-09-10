---
name: ci-cd-github-actions
description: Stand up GitHub Actions CI/CD in the first 20 minutes of a timed build and keep it green. Use when scaffolding a new repo, when asked for CI, tests-in-CI, a deploy pipeline, branch protection, secret scanning, or when a workflow run is red and needs reading fast. Covers a minimal ci.yml (lint, typecheck, test, build) per stack, a pnpm monorepo variant, gitleaks, required status checks via gh api, a main-only deploy job to DigitalOcean App Platform or a GHCR image push, and the three failures that hit timed builds most.
---

# CI/CD with GitHub Actions

Goal: from the first commit, every push shows a green check that ran
lint, typecheck, tests and build for real; main is protected by that
check; a deploy job runs only on main after CI passes. Distilled from the
workflows in TechPulse (Python plus Vite), agent-os (pnpm monorepo with
gitleaks and a tagged release), salon-hub (Spring Boot with a Postgres
service container, Docker image publish) and portfolio-website (Vite to
GitHub Pages). Action names and inputs were checked against the docs in
`references/github-docs.md`.

## 1. Minimal `ci.yml` in the first commit

Copy `templates/ci.yml` (backend plus frontend) or
`templates/ci-monorepo.yml` (pnpm workspaces) to
`.github/workflows/ci.yml`, then replace the backend job's steps with the
snippet from `templates/<stack>/ci-job.yml`. Shape that matters:

- Triggers: `push` to `main` and the branch prefixes in use
  (`feature/**`, `bugfix/**`, `hotfix/**`, `refactor/**`, `docs/**`),
  `pull_request` to `main`, and `workflow_dispatch`.
- `concurrency: group: ${{ github.workflow }}-${{ github.ref }}` with
  `cancel-in-progress: true`, so a rapid second push cancels the first
  run instead of queueing behind it.
- `permissions: contents: read` at the top; widen per job only when a
  job writes (packages, pages).
- One job per component. When backend and frontend live in one repo,
  either separate jobs that skip cleanly if their folder is absent (the
  template's `test -f` guard), or `dorny/paths-filter` to run only what
  changed. Separate jobs give separate status checks, which is what
  branch protection wants.
- Caching through the setup actions: `actions/setup-python` with
  `cache: pip` and `cache-dependency-path`; `actions/setup-node` with
  `cache: npm` or `cache: pnpm` (after `pnpm/action-setup`);
  `actions/setup-java` with `cache: gradle`; `actions/setup-go` caches
  modules by default.
- Order inside a job: install, lint, typecheck, test, build. Fail fast;
  do not `|| echo` past a failure. A step that cannot fail is not a check.

### Per-stack steps

| Stack | Setup | Lint | Typecheck | Test | Build |
| --- | --- | --- | --- | --- | --- |
| Python FastAPI | `actions/setup-python@v5` 3.12, `pip install -r requirements.txt ruff mypy pytest` | `ruff check . && ruff format --check .` | `mypy . --ignore-missing-imports` | `pytest tests -q` | `python -c "from src.main import app"` |
| Java Spring Boot | `actions/setup-java@v4` temurin 17 `cache: gradle`; `chmod +x gradlew` | `./gradlew check -x test --no-daemon` (spotless/checkstyle if configured) | (compiler) | `./gradlew test --no-daemon`, Postgres as a `services:` container when tests need it | `./gradlew bootJar --no-daemon` |
| Node/TypeScript | `actions/setup-node@v4` 22 `cache: npm`; `npm ci` | `npm run lint` | `npx tsc --noEmit` | `npm test` | `npm run build` |
| pnpm monorepo | `pnpm/action-setup@v4` then `actions/setup-node@v4` `cache: pnpm`; `pnpm install --frozen-lockfile` | `pnpm lint` | `pnpm -r run typecheck` | `pnpm test` | `pnpm build` |
| Go | `actions/setup-go@v5` with `go-version-file: go.mod` | `go vet ./...` (add `golangci-lint` only if already configured) | (compiler) | `go test ./...` | `go build ./...` |
| Vite/React | `actions/setup-node@v4` 22 `cache: npm`; `npm ci` | `npm run lint` | `npm run typecheck` | Playwright only if specs exist | `npm run build` then assert the output dir exists |
| Next.js | same as Node | `npm run lint` | `npx tsc --noEmit` | `npm test` if present | `npm run build` |

Environment for tests: `ENVIRONMENT=testing` (disables schedulers) and a
throwaway database URL. Never point CI at a real external service; the
provider fake is what runs here.

## 2. Secret scanning from commit one

```yaml
  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

`fetch-depth: 0` so it scans history, not just the tip. It belongs in the
first commit because the first commit is where a pasted token is most
likely: `.env` files, deploy specs, notebook outputs. Catching it on push
number one costs nothing; rotating a leaked token during the interview
costs ten minutes. Add `.gitleaks.toml` only to allow-list a known false
positive, never to silence a real hit.

## 3. Branch protection in one command

After the first green run, require the check names (the jobs' `name:`
values, or the job ids if no name is set) on `main`:

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
```

`strict: true` means the branch must be up to date with main before
merging. `enforce_admins: false` leaves an escape hatch for the owner in a
timed session; say so in the demo. `required_pull_request_reviews: null`
because a solo build has no second reviewer. Check with
`gh api repos/OWNER/REPO/branches/main/protection --jq .required_status_checks.contexts`.

## 4. CD: deploy only from main, only after CI

`templates/deploy-do.yml` deploys to DigitalOcean App Platform with the
official action. It runs on `push` to `main` and uses
`workflow_run` gating or `needs:` inside the same workflow so it never
runs on a red build. The human creates the `DIGITALOCEAN_ACCESS_TOKEN`
repository secret themselves (Settings, Secrets and variables, Actions);
the assistant never handles the token value.

```yaml
      - uses: digitalocean/app_action/deploy@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
          print_build_logs: true
          print_deploy_logs: true
```

The action reads `.do/app.yaml` by default (`app_spec_location`), creates
the app on first run and updates it after, and exposes the app JSON as an
output. Repository secrets passed as `env:` on the step can be referenced
from the spec as `${SOME_SECRET}` bindables.

Generic alternative, an image to GHCR that any host can pull:

```yaml
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: backend
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/api:latest
            ghcr.io/${{ github.repository }}/api:${{ github.sha }}
```

Then the App Platform spec's `image:` block points at
`registry_type: GHCR`, or a Droplet pulls the tag. Both variants are in
`templates/deploy-do.yml`.

## 5. Reading a red run fast

```
gh run list --limit 5
gh run view <run-id> --log-failed
gh pr checks <pr-number> --watch
gh run rerun <run-id> --failed
```

`--log-failed` prints only the failing step's log, which is the whole
point under time pressure. The three failures that account for most red
runs in a timed build:

| Symptom in the log | Cause | One-line fix |
| --- | --- | --- |
| `ruff format --check` or `prettier --check` lists files, or `Would reformat` | formatter drift: code was written faster than it was formatted | run the formatter locally (`ruff format .`, `npx prettier --write src`), commit `style: format` |
| `npm ci` says lockfile out of sync, `pnpm install --frozen-lockfile` fails, pip resolves a different version | lockfile mismatch after adding a dependency by hand | run the install locally without `--frozen`/`ci` once, commit the lockfile |
| `KeyError`, `pydantic ValidationError`, `Settings` missing field, `Cannot read properties of undefined` in a config module | env var present in `.env` locally, absent in CI | add it to the job's `env:` with a safe test value, and to `.env.example` |

Second tier: a test that needs a running database (add a `services:`
container or mark it `integration` and exclude it), a job that assumes
`bash` on a Windows-authored script (`shell: bash` in `defaults`), and
Node native binaries on a different platform (`npm ci` on Linux, do not
commit `node_modules`).

## 6. What to say in the demo

Point at three things: the green check on the latest commit and what it
ran (name the steps), the protected branch (show the required checks in
Settings or the `gh api` output), and the deploy job (the run on main,
its log, the URL it printed). Then name the one thing that turned red
during the session and the fix, because that is the "verify versus trust"
moment the interviewer wants to hear.
