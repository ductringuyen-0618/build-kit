# The three-hour build

A plan for a timed session where the output is a working prototype on a
public URL, a repo an interviewer can read, and a walkthrough. Written for
DigitalOcean's build session (see `docs/interview-format.md`) but the
phases hold for any timed build.

Honest framing first. Three hours is enough for: one real feature with
tests, a deploy, a README, and a short set of demo notes. It is usually
not enough for two polished features. The second-feature slot below is
where scope gets cut, and cutting it is the correct call if the deploy is
at risk.

Keep `docs/demo-notes.md` open the whole time. Every time something is
decided, scaffolded, hand-written, verified, or found wrong, add one line.
That file is the walkthrough.

## Before the clock starts (if allowed)

- `doctl auth init` with a token that has write access. Confirm with
  `doctl account get`.
- Connect GitHub to App Platform once in the DigitalOcean control panel so
  `deploy_on_push` works from the spec. If that is not possible, plan to
  push a Docker image to DigitalOcean Container Registry instead.
- Install the DigitalOcean skills: `npx skills add digitalocean-labs/do-app-platform-skills`.
- Have this kit cloned and the assistant pointed at `AGENTS.md`.

## 0-15 minutes: clarify and scaffold

Skills: `grill-me`, `write-issue`.

1. Pick the prompt that is closest to something already built. A CRUD
   service with one interesting rule beats a novel system.
2. `grill-me`, capped at eight questions. Answer most of them yourself out
   loud; the interviewer is listening. Write `docs/designs/<slug>.md`.
3. `write-issue` for the core feature. Three to six acceptance criteria.
   This is the definition of done for minute 90.
4. Scaffold from `templates/`:
   - backend per `templates/backend-fastapi.md` (health endpoint, settings
     object with the single database resolver, one test)
   - `templates/ci.yml` as `.github/workflows/ci.yml`
   - `templates/.env.example`
   - `templates/Dockerfile` into `backend/`
   - `templates/.do/app.yaml` into `.do/app.yaml` with the repo name filled in
   - frontend per `templates/frontend-vite-react.md` only if the prompt
     needs a UI
5. First commit: `chore: scaffold service with health check, tests and ci`.
   Push. CI must go green on this commit; if it does not, fix CI now, not
   later.

Artefacts: `docs/designs/<slug>.md`, `docs/issues/<slug>.md`, a green CI
run, `docs/demo-notes.md` with the prompt choice and why.

## 15-90 minutes: the core feature, tests first

Skills: `feature-build` (branch and commit discipline), `feature-validate`
(how to run checks), `test-app-e2e` (runner pattern), `superpowers:test-driven-development` if installed.

1. Data model and migration first, if there is one. SQLite locally,
   Postgres in the deploy, same SQLAlchemy models. The settings resolver
   handles the URL difference.
2. For each acceptance criterion: failing test, then code, then commit.
   Commit messages name the criterion.
3. Hand-write the part that carries the domain rule. Scaffold the rest.
   Say which is which in the demo notes.
4. Every 20 minutes run the full check: lint, typecheck, tests. Report the
   real exit codes in the `feature-validate` shape.
5. At minute 60 write the smoke runner: a stdlib Python script that hits
   the running service over HTTP for health, the main create path, the
   main read path, and one error path. Keep it under 150 lines. This is
   the `test-app-e2e` pattern with the endpoint list swapped.
6. At minute 85, stop adding. Run everything. Push. CI green.

Artefacts: tests that map to acceptance criteria, `scripts/smoke.py`, a
README with install and run commands that you have executed yourself.

## 90-150 minutes: second feature or hardening

Skills: `write-issue`, `feature-review`, `verify-feature`, `coo-ideate`
(the "pick the next thing" heuristic: something the user would notice,
something the codebase makes cheap).

Decide at minute 90, out loud, using this order:

1. If the deploy has not been proven yet, go to the ship phase now and
   come back if time remains.
2. If the core feature has a known gap, harden: input validation, an
   error envelope, pagination, an index, structured logging, a request id
   header, a rate limit. Each is one commit and one test.
3. Only if both are fine, add the second feature. Write its issue first.
   Give it 40 minutes. If it is not passing by minute 140, revert to the
   last green commit and write the idea into the demo notes as "next".

Whichever path: at minute 140 run `feature-review` against the issues.
Read the diff. First line of the verdict is `PASS` or `FAIL`. Fix `FAIL`
items or cut them.

If there is a UI, run the `verify-feature` second gate: the Playwright
click sweep. If Playwright is not on the machine, drive the three main
flows by hand and list what was clicked in the demo notes.

Artefacts: second issue file or a list of hardening commits, the review
verdict, a green CI run.

## 150-180 minutes: deploy, README, demo notes

Skills: `verify-techpulse` (doctor, drive, evidence), `blackbox-qa-validator` agent if subagents are available.

### DigitalOcean App Platform path

1. Fill in `.do/app.yaml`: repo, branch, `source_dir`, `dockerfile_path`,
   `http_port`, health check path, envs, and a dev database.
2. Create the app:
   ```
   doctl apps create --spec .do/app.yaml
   doctl apps list
   doctl apps logs <app-id> --type build --follow
   ```
3. When the build finishes, `doctl apps get <app-id>` prints the default
   ingress URL. Curl `/health` on it. Then run `scripts/smoke.py --base-url https://<url>`.
4. Set secrets in the control panel or with `doctl apps update <app-id> --spec .do/app.yaml`
   after adding `type: SECRET` envs. Never paste a secret into the spec
   committed to git; use the `EV[...]` encrypted form the panel produces or
   set the value in the panel only.
5. Database: the spec's `databases:` block with `production: false` gives a
   dev Postgres in minutes. The service reads `${db.DATABASE_URL}`.
   Migrations run at start (`alembic upgrade head` in the run command or a
   `jobs:` entry with `kind: PRE_DEPLOY`).

If GitHub is not connected to App Platform, use the registry path:
```
doctl registry create <name>
doctl registry login
docker build -t registry.digitalocean.com/<name>/api:latest backend
docker push registry.digitalocean.com/<name>/api:latest
```
and replace the service's `github:` block with
```
image:
  registry_type: DOCR
  repository: api
  tag: latest
```

### Generic fallback

The `Dockerfile` runs anywhere. On a Droplet: `docker run -d -p 80:8000 --env-file .env <image>`.
On Fly.io, Railway or Render the same image deploys with their CLI. Say
in the README which one was used and why.

### Prove it

Run the doctor-then-drive loop from `verify-techpulse` against the public
URL: health, one write, read the write back through the read path, one
error path. Save the outputs under a temp directory outside the repo and
paste the URLs and status codes into `docs/demo-notes.md`.

### README

Sections, in this order: what it is (two sentences), public URL, run
locally, run tests, deploy, design (five bullets: data model, the one
domain rule, what was scaffolded versus hand-written, known limits, next
steps), and how the AI was used and verified.

### Demo notes

`docs/demo-notes.md` ends with three headings the walkthrough will follow:

- Decisions and trade-offs
- What the AI got wrong and how it was caught
- If traffic spiked: the bottleneck, the first fix, the second fix

Final commit: `docs: readme, deploy spec and demo notes`. Push. Confirm CI
green. Open the public URL in a browser tab before the clock stops.

## If behind

| Time | Situation | Cut |
| --- | --- | --- |
| 45 | tests not passing on the core path | drop the second acceptance criterion, keep the first |
| 90 | core done, no deploy yet | skip the second feature entirely, deploy now |
| 120 | deploy failing | switch to the registry path or the generic fallback; do not debug GitHub integration |
| 160 | deploy up, README thin | README before demo notes; demo notes can be six lines |
