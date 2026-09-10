---
name: e2e-verify
description: Stand up a web app locally, run a minimal end-to-end smoke suite (Playwright or a manual click-through) against it, and report PASS/FAIL with the exact commands and output; use before declaring any user-facing feature done, or when asked to verify, smoke test, or check that nothing is broken.
---

# e2e-verify

Prove that the app works from the outside, the way a user meets it: boot
it, drive it through the browser (or HTTP), capture what happened, and
report it honestly. Works for any stack and any agent tool. Nothing here
assumes a particular project, port, or framework.

## When to use

- A user-facing feature, page, route, or API contract was just built or
  changed and someone is about to call it done.
- You are asked to "verify", "smoke test", "run e2e", or "check nothing
  broke".
- Before and after a deploy, a dependency upgrade, or a config change.

Do not use it for a single function (write a unit test) or for visual
polish (this proves behaviour, not layout).

## Inputs

- The repo, at the commit to verify (`git rev-parse --short HEAD`).
- The feature under test, in one sentence, plus its acceptance criteria
  if written down.
- Optional: a behaviour map for the app, see
  [references/behaviour-map.md](references/behaviour-map.md). If one
  exists, read it before driving anything.

## Steps

### 1. Find the run command and port

Read, in this order, and stop at the first hit: the project README's
"run" or "development" section; the package manifest (`package.json`
`scripts.dev` / `scripts.start`, `pyproject.toml`, `Makefile`,
`docker-compose.yml`, `Procfile`); the framework default. Common
defaults, used only when nothing in the repo says otherwise:

| Stack | Run command | Default port |
|---|---|---|
| Vite / SvelteKit | `npm run dev` | 5173 |
| Next.js / Nuxt / CRA / Remix | `npm run dev` | 3000 |
| Angular | `npx ng serve` | 4200 |
| FastAPI | `uvicorn <module>:app --port 8000` | 8000 |
| Django | `python manage.py runserver` | 8000 |
| Flask | `flask run` | 5000 |
| Rails | `bin/rails server` | 3000 |
| Spring Boot | `./mvnw spring-boot:run` | 8080 |
| Go (net/http, Gin, Echo) | `go run .` | 8080 or `$PORT` |
| Rust (Axum, Actix) | `cargo run` | 3000 or 8080 |
| Docker Compose | `docker compose up` | see `ports:` |

The banner the server prints wins over the table and over the README.
Read it. A dev server that silently moves to the next free port is the
most common reason a suite hits nothing.

Also find: the env vars the app needs (`.env.example`, README), whether
the frontend and backend are separate processes, and the URL the
frontend uses to reach the backend.

### 2. Stand the app up

Start each process in the background with output to a log file, record
its PID, and never start a second copy on a port that is already in use.
If the port is taken, check what owns it before killing anything. If it
is not yours, pick another port and pass it to both the app and the
tests.

```bash
(npm run dev > /tmp/e2e-web.log 2>&1 & echo $! > /tmp/e2e-web.pid)
```

Use a throwaway database or data directory when the app has one, so a
verification run never mutates real data. Platform-specific variants
(PowerShell, port ownership, kill by PID) are in
[references/platform-notes.md](references/platform-notes.md).

### 3. Probe readiness before testing

Poll until the app answers, with a hard timeout. Do not sleep a fixed
number of seconds and hope.

```bash
for i in $(seq 1 60); do
  curl -sf -o /dev/null http://localhost:PORT/ && break; sleep 1
done
curl -si http://localhost:PORT/ | head -1        # expect HTTP/1.1 200
```

Probe a real page or a health endpoint if one exists. If the app depends
on an external service (database, LLM, queue), probe that too and record
the result. A missing dependency is an environment finding, not an app
bug, and it limits what you can verify. Say so in the report.

### 4. Pick the vehicle

Use the first that applies:

1. **The project already has an e2e runner** (Playwright, Cypress,
   pytest-playwright, Selenium). Use it. Add your smoke spec to it.
2. **Node is available.** Install Playwright and write the minimal smoke
   suite from
   [references/playwright-smoke.md](references/playwright-smoke.md).
3. **Python only.** `pip install pytest-playwright` and use the Python
   template in the same reference.
4. **No runner is possible** (no Node, no Python, locked-down box).
   Do the HTTP checks with curl, then the manual click-through in
   [references/manual-checklist.md](references/manual-checklist.md).

### 5. Write and run the smoke suite

The minimal suite proves five things and nothing more:

- The root URL loads with HTTP 200 and a visible heading or title.
- No uncaught page errors and no `console.error` during load.
- Every top-level navigation item leads somewhere that renders.
- One API call the UI depends on returns 200 with the expected shape.
- The feature under test: one full user path, from entry point to the
  observable result, asserting on state the user can see.

Run it with the exact command you will paste into the report:

```bash
npx playwright test e2e/smoke.spec.ts --reporter=line
```

Prove a write by reading it back through the user-facing read path, not
through the write endpoint's own success message. Capture a screenshot
at the end state of the feature path. If the run is red, read
[references/troubleshooting.md](references/troubleshooting.md) before
touching app code, and rerun the whole suite after any fix.

### 6. Manual click-through (when there is no runner)

Follow [references/manual-checklist.md](references/manual-checklist.md)
with browser tools if the agent has them. If it does not, hand the
checklist to the human and wait for their results. Never fill in a
manual checklist from what the code "should" do.

### 7. Tear down

Kill only the PIDs you started. Remove the throwaway database. Restore
any shared server-side state the run changed. Leave the logs and
screenshots.

## Outputs

One report, first line `PASS`, `FAIL`, or `BLOCKED`. This is the
contract; every field is required.

```
RESULT: PASS | FAIL | BLOCKED
Commit: <sha>   App: <url(s)>   Stack: <one line>
Boot:   <exact command>  ->  ready after <n>s  (probe: <curl cmd> -> <status>)
Ran:
  1. <exact command>  ->  exit <code>  (<n> passed, <n> failed, <n> skipped)
  2. ...
Output tail (last 30 lines of the failing or final run):
  <verbatim>
Screenshots: <paths, or "none">
Failures: <per failure: test name, assertion text, likely area, or "none">
Not verified: <what could not run and the unmet precondition, or "none">
Cleanup: <pids stopped, ports freed, state restored>
```

## Verify before trust

- Never write `PASS` without the command's real output in the report. A
  claim with no output is `BLOCKED`, not `PASS`.
- A fix that was not re-run is `FAIL`. Skipped tests are not passes.
- If the run could not happen at all (app would not boot, dependency
  missing), the result is `BLOCKED` with the reason, never `PASS`.
- Reading the code is not verification. Only the running app counts.
- Pre-existing failures your change did not touch are reported as such,
  by comparing against the previous commit, and do not become `PASS`.

## Done when

- The app booted from the documented command and answered a real probe.
- The smoke suite (or the manual checklist) ran against it.
- The report above is delivered, with verbatim commands and output.
- Everything you started is stopped.
