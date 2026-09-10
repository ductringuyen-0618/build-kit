# Reading a red run: the longer list

Companion to steps 7 and 8 in `SKILL.md`. The three failures there cover
most red runs in a fresh repo. These are the next tier, in the order they
tend to appear.

## Diagnosis order

1. `gh run view <run-id> --log-failed`, then read the first error line.
   Later lines are usually consequences of it.
2. Is the failing step the install? Then it is a lockfile, a cache path or
   a version mismatch, never the code.
3. Does the same command pass locally? If yes, the difference is the
   environment: an env var, a service, the OS, or a file that is
   git-ignored locally but needed.
4. Fix one thing, push, watch. Do not stack three guesses in one push.

## Second-tier failures

| Symptom | Cause | Fix |
| --- | --- | --- |
| tests hang or fail with connection refused on a database port | tests need a real database and CI has none | add a `services:` container (see the Java job in `templates/java-spring-boot/ci-job.yml` for a Postgres example with a health check), or mark those tests `integration` and exclude them in CI |
| `bash: ./script.sh: /bin/bash^M: bad interpreter`, or `Permission denied` on `gradlew` | CRLF line endings or a lost executable bit from a Windows checkout | `git config core.autocrlf false`, re-save the file with LF, `chmod +x` and commit; add `shell: bash` under `defaults.run` |
| `npm ci` succeeds locally, CI fails on a native module (`sharp`, `esbuild`, `better-sqlite3`) | `node_modules` or a platform-specific binary was committed | delete `node_modules` from git, add it to `.gitignore`, let `npm ci` build on the runner |
| a required check never reports; the PR shows "Expected" forever | the context string in branch protection does not match any job `name:` | compare `gh api repos/OWNER/REPO/branches/main/protection --jq .required_status_checks.contexts` against the workflow's job names |
| deploy workflow never triggers after a green CI | `workflow_run.workflows` does not match the CI workflow's `name:`, or the CI run was on a non-default branch | make the strings identical; `workflow_run` only fires for runs on the default branch |
| `Error: Resource not accessible by integration` | job needs a permission it does not have (`packages: write`, `pull-requests: read`) | add it under the job's `permissions:` |
| cache restored but install still slow or wrong | `cache-dependency-path` points at the wrong lockfile | path is relative to the repo root, not to `working-directory` |
| `mypy` or `tsc` errors only in CI | different tool version or missing type stubs in CI | pin the tool version in the lockfile or requirements; install stubs |
| Playwright fails with missing browsers | browsers are not installed on the runner | `npx playwright install --with-deps chromium` before the tests |
| gitleaks fails on a known false positive (test fixture, example key) | pattern match on a fake value | add a `.gitleaks.toml` allow-list entry for that path or regex; never for a real key |

## Cheap habits that prevent most of these

- Run the exact CI commands locally before pushing, in the same order.
- Keep `.env.example` complete; copy its keys into the job's `env:`.
- Add a dependency with the package manager, never by editing the
  lockfile or manifest by hand.
- Pin major versions of actions (`@v7`) and tool versions in lockfiles.
