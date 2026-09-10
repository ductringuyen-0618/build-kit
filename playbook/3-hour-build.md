# The three-hour build

A plan for a timed session where the output is a working prototype on a
public URL, a repo an interviewer can read, and a walkthrough. Written for
DigitalOcean's build session (see `docs/interview-format.md`) but the
phases hold for any timed build and any stack.

Honest framing first. Three hours is enough for: one real feature with
tests, a deploy, a README, and a short set of demo notes. It is usually
not enough for two polished features. The second-feature slot below is
where scope gets cut, and cutting it is the correct call if the deploy is
at risk.

Keep `docs/demo-notes.md` open the whole time. Every time something is
decided, scaffolded, hand-written, verified, or found wrong, add one line.
That file is the walkthrough.

## Before the clock starts (if allowed)

- `doctl auth init` with a token the human pastes; confirm with
  `doctl account get`.
- Connect GitHub to App Platform once in the control panel so
  `deploy_on_push` works from the spec. If that is not possible, plan on
  the container registry path in the deploy skill.
- Install DigitalOcean's skills: `npx skills add digitalocean-labs/do-app-platform-skills`.
- Have this kit cloned and the assistant pointed at `AGENTS.md`.

## 0-15 minutes: pick, clarify, scaffold

Skills: `playbook/stack-picker.md`, `grill-me`, `write-issue`,
`ci-cd-github-actions`.

1. Pick the prompt closest to something already built. A CRUD service
   with one interesting rule beats a novel system.
2. Pick the stack with the stack picker. One minute. Write it at the top
   of `docs/demo-notes.md`.
3. `grill-me`, capped at eight questions. Answer most of them yourself out
   loud; the interviewer is listening. Write `docs/designs/<slug>.md`.
4. `write-issue` for the core feature. Three to six acceptance criteria.
   This is the definition of done for minute 90.
5. Scaffold with the stack picker's command, then copy in from
   `templates/<stack>/`: `Dockerfile`, `.env.example`, the CI job into
   `.github/workflows/ci.yml` (from `templates/ci.yml`), and the App
   Platform component into `.do/app.yaml` (from `templates/do-app.yaml`).
   Frontend, if needed, from `templates/vite-react/` or `templates/nextjs/`.
6. Health endpoint that checks the database, one test that calls it, a
   settings module that is the only reader of the environment.
7. First commit: `chore: scaffold service with health check, tests and ci`.
   Push. CI must go green on this commit; if it does not, fix CI now, not
   later. Then branch protection per the CI/CD skill.

Artefacts: `docs/designs/<slug>.md`, `docs/issues/<slug>.md`, a green CI
run, `docs/demo-notes.md` with the prompt and stack choice and why.

## 15-90 minutes: the core feature, tests first

Skills: `feature-build` (branch and commit discipline), `feature-validate`
(how to run checks), `test-app-e2e` (runner pattern), `superpowers:test-driven-development` if installed.

1. Data model and migration first. Local database of the stack's choice
   (SQLite or a local Postgres container), managed Postgres in the
   deploy, same models. The settings module handles the URL difference.
2. For each acceptance criterion: failing test, then code, then commit.
   Commit messages name the criterion.
3. Hand-write the part that carries the domain rule. Scaffold the rest.
   Say which is which in the demo notes.
4. Every 20 minutes run the stack's full check (the row in the CI/CD
   skill's per-stack table). Report the real exit codes in the
   `feature-validate` shape.
5. At minute 60 write the smoke runner: a small script in the stack's
   language, or the stdlib Python one from `test-app-e2e`, that hits the
   running service over HTTP for health, the main create path, the main
   read path, and one error path. Under 150 lines.
6. At minute 85, stop adding. Run everything. Push. CI green.

Artefacts: tests that map to acceptance criteria, `scripts/smoke.*`, a
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

Skills: `deploy-digitalocean-app-platform` (the whole phase is
time-boxed inside it), `verify-techpulse` (doctor, drive, evidence
pattern), `blackbox-qa-validator` agent if subagents are available.

1. Follow the deploy skill's 30-minute table: prerequisites, spec,
   `doctl apps create`, logs, live URL from `DefaultIngress`.
2. Verify against the live URL: health 200, clean run logs, one write
   read back through the read path, one error path, and for a UI the
   main flow in a browser with the network tab open. Paste URL, status
   codes and timestamps into `docs/demo-notes.md`.
3. If the deploy is not green by minute 170, switch to the skill's
   fallback (same Dockerfile locally or on a Droplet) and say so.
4. README sections, in order: what it is (two sentences), public URL,
   run locally, run tests, deploy, design (five bullets: data model, the
   one domain rule, what was scaffolded versus hand-written, known
   limits, next steps), and how the AI was used and verified.
5. `docs/demo-notes.md` ends with three headings the walkthrough follows:
   decisions and trade-offs; what the AI got wrong and how it was caught;
   if traffic spiked, the bottleneck, the first fix, the second fix.
6. Final commit: `docs: readme, deploy spec and demo notes`. Push. CI
   green. Open the public URL in a browser tab before the clock stops.

## If behind

| Time | Situation | Cut |
| --- | --- | --- |
| 45 | tests not passing on the core path | drop the second acceptance criterion, keep the first |
| 90 | core done, no deploy yet | skip the second feature entirely, deploy now |
| 120 | deploy failing | switch to the registry path or the generic fallback; do not debug GitHub integration |
| 160 | deploy up, README thin | README before demo notes; demo notes can be six lines |
