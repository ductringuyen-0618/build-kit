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

Keep three files open the whole time: `docs/TIMELOG.md` (the clock,
from `timebox`), `docs/DECISIONS.md` (decision, alternatives, why,
verified versus trusted, from `walkthrough-prep`) and
`docs/demo-notes.md` (what the walkthrough reads from). Every time
something is decided, scaffolded, hand-written, verified, or found
wrong, add one line to the right one. Commit every fifteen minutes.

## Before the clock starts (if allowed)

- `doctl auth init` with a token the human pastes; confirm with
  `doctl account get`.
- Connect GitHub to App Platform once in the control panel so
  `deploy_on_push` works from the spec. If that is not possible, plan on
  the container registry path in the deploy skill.
- Install DigitalOcean's skills: `git clone https://github.com/digitalocean-labs/do-app-platform-skills.git` then symlink it: `ln -s "$PWD/do-app-platform-skills" ~/.claude/skills/do-app-platform-skills` (or `~/.cursor/skills/`, `~/.codex/skills/`).
- Have this kit cloned and the assistant pointed at `AGENTS.md`.

## 0-15 minutes: pick, clarify, scaffold

Skills: `timebox` (start the clock), `playbook/stack-picker.md`,
`grill-me`, `write-issue`, `scaffold-service`, `ci-cd-github-actions`.

1. Pick the prompt closest to something already built. A CRUD service
   with one interesting rule beats a novel system.
2. Pick the stack with the stack picker. One minute. Write it at the top
   of `docs/demo-notes.md`.
3. `grill-me`, capped at eight questions. Answer most of them yourself out
   loud; the interviewer is listening. Write `docs/designs/<slug>.md`.
4. `write-issue` for the core feature. Three to six acceptance criteria.
   This is the definition of done for minute 90.
5. `scaffold-service`, steps 1 to 10: scaffold with the stack picker's
   command, then copy in from `templates/<stack>/`: `Dockerfile`,
   `.env.example`, the CI job into `.github/workflows/ci.yml` (from
   `templates/ci.yml`), and the App Platform component into
   `.do/app.yaml` (from `templates/do-app.yaml`). Frontend, if needed,
   from `templates/vite-react/` or `templates/nextjs/`.
6. Health endpoint that checks the database, one test that calls it, a
   settings module that is the only reader of the environment.
7. First commit: `chore: scaffold service with health check, tests and ci`.
   Push. CI must go green on this commit; if it does not, fix CI now, not
   later. Then branch protection per the CI/CD skill. Log "scaffold
   green" with the run URL in `docs/TIMELOG.md`.

Artefacts: `docs/designs/<slug>.md`, `docs/issues/<slug>.md`, a green CI
run, `docs/demo-notes.md` with the prompt and stack choice and why,
`docs/DECISIONS.md` with the stack entry, `docs/TIMELOG.md` started.

## 15-90 minutes: the core feature, tests first

Skills: `feature-build` and `missions/briefings/worker.md` (branch and
commit discipline), `feature-validate` or
`missions/briefings/validator-scrutiny.md` (how to run checks),
`smoke-verify` (contract to HTTP checks),
`superpowers:test-driven-development` if installed.

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
5. At minute 60 write `smoke.json` from the contract (`smoke-verify`
   says how: one check per HTTP-shaped acceptance criterion, create then
   read back, two negative cases) and run
   `python scripts/smoke.py --base-url http://127.0.0.1:<port> --checks smoke.json`.
   Do not adapt `test-app-e2e`; its runner is tied to another project.
6. At minute 85, stop adding. Run everything, including the smoke
   checks. Push. CI green. `timebox` has the cut rule if it is not.

Artefacts: tests that map to acceptance criteria, `scripts/smoke.py` and
`smoke.json`, a README with install and run commands that you have
executed yourself, `VERIFIED` lines in the timelog.

## 90-150 minutes: second feature or hardening

Skills: `timebox` (the minute-90 decision), `write-issue`,
`feature-review` or `missions/briefings/validator-user-testing.md`,
`verify-feature` (only if Playwright is present), `coo-ideate` (the
"pick the next thing" heuristic: something the user would notice,
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

Whichever path: at minute 140 run `feature-review` against the issues,
and for anything user-facing the user-testing briefing against the
running app. Read the diff, then open the URL. First line of each
verdict is `PASS` or `FAIL`. Fix `FAIL` items that take one commit or
cut them.

If there is a UI, run the `verify-feature` second gate: the Playwright
click sweep. If Playwright is not on the machine, drive the three main
flows by hand and list what was clicked in the demo notes.

Artefacts: second issue file or a list of hardening commits, the review
verdict, a green CI run.

## 150-180 minutes: deploy, ship, README, walkthrough

Skills: `deploy-digitalocean-app-platform` (the whole phase is
time-boxed inside it), `smoke-verify` against the live URL, `ship-gate`
(PR, CI, shipped report), `walkthrough-prep` (minute 170 onward),
`blackbox-qa-validator` agent if subagents are available.

1. Follow the deploy skill's 30-minute table: prerequisites, spec,
   `doctl apps create`, logs, live URL from `DefaultIngress`.
2. Verify against the live URL: `python scripts/smoke.py --base-url <live url> --checks smoke.json`
   (health, one write read back through the read path, one error path),
   clean run logs, and for a UI the main flow in a browser with the
   network tab open. Paste the script's output, the log tail and
   timestamps into `docs/demo-notes.md`.
3. If the deploy is not green by minute 170, switch to the skill's
   fallback (same Dockerfile locally or on a Droplet) and say so.
4. README sections, in order: what it is (two sentences), public URL,
   run locally, run tests, deploy, design (five bullets: data model, the
   one domain rule, what was scaffolded versus hand-written, known
   limits, next steps), and how the AI was used and verified.
5. `ship-gate`: push the branch, open the PR with the contract and the
   validator output (scrubbed of local paths), wait for CI, one fix if
   red, then the shipped report into `docs/demo-notes.md`. If the PR has
   zero checks, say so; do not write "CI passed".
6. `walkthrough-prep` from minute 170: the six headings (architecture in
   two minutes; three trade-offs; scaffolded, hand-written, verified,
   what the AI got wrong; 10x traffic and a spike, grounded in the
   references file; what was not verified and how it would be; with
   more time) into `docs/demo-notes.md` from `docs/DECISIONS.md` and the
   timelog.
7. Final commit: `docs: readme, deploy spec and walkthrough notes`. Push.
   CI green. Open the public URL, the PR and the README in browser tabs
   before the clock stops.

## If behind

The full table with the question to ask at each minute is in
`skills/timebox`. The short form:

| Time | Situation | Cut |
| --- | --- | --- |
| 45 | tests not passing on the core path | drop the last acceptance criterion, keep the first |
| 85 | not green locally | stop adding; fix until green |
| 90 | core done, no deploy yet | skip the second feature entirely, deploy now |
| 120 | deploy failing | switch to the registry path or the generic fallback; do not debug GitHub integration |
| 150 | second feature not passing | revert to the last green commit; write it as "next" |
| 160 | deploy up, README thin | README before demo notes; demo notes can be six lines |
| 170 | no walkthrough script | draft it from `docs/DECISIONS.md`: three trade-offs and one AI mistake are enough |
