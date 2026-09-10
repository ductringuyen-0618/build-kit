# AGENTS.md

You are working with Tri Nguyen in a timed build session. Read this file,
then `playbook/3-hour-build.md`, then the skills the playbook names for
the current phase. Skills live in `skills/<name>/SKILL.md`. Read a skill in
full before following it; do not summarise it from its description.

## Non-negotiables

These are how Tri works. They are not suggestions.

1. Nothing is "done" until lint, typecheck, tests and the build pass
   locally and CI is green on the pushed branch. Say what ran and what the
   output was. Never claim a pass you did not see.
2. Every commit is a conventional commit: `feat`, `fix`, `docs`, `style`,
   `refactor`, `test`, `chore`. Small commits, in order, so the history
   tells the story in the walkthrough.
3. No secrets in the repo. Config comes from environment variables with a
   committed `.env.example`. Grep for keys and tokens before every commit.
4. The README has run instructions that work from a fresh clone: install,
   run, test, deploy. Write it as you go, not at the end.
5. There is a deploy target from minute one. In a DigitalOcean session that
   is App Platform via `.do/app.yaml`; the fallback is the Dockerfile on
   any host. A prototype nobody can open in a browser is not a prototype.
6. Verify before you trust. Run the thing. Curl the endpoint. Click the
   button. When the model produces something confident and wrong, say so,
   fix it, and note it in `docs/demo-notes.md`. That moment is what the
   interviewer is watching for.
7. Ask before you build when the answer changes the design. Use `grill-me`
   for that. Do not ask about things you can read from the repo.
8. Keep the backend root clean. One-off scripts go in `scripts/`. Do not
   create progress notes, changelogs or extra markdown files beyond
   README, `docs/designs/`, `docs/issues/` and `docs/demo-notes.md`.

## Conventions carried over from real projects

- Database location has one source of truth: a settings object that
  returns the URL, the plain file path, and the SQLAlchemy URL. Every
  repository and route calls it. A prior bug came from one route resolving
  its own path and reading a different SQLite file than the one being
  written.
- Model calls go through a provider abstraction with graceful fallback
  between providers. Mock external AI services in tests. Cache embeddings
  and LLM responses.
- FastAPI with `redirect_slashes=True` returns 307 redirects that carry no
  CORS headers. Frontend endpoint constants use the canonical
  trailing-slash form so the browser never sees the redirect.
- Prefer ARIA roles and accessible names in browser tests, then
  `data-testid`. Never drive by coordinates.
- Prove a write by reading it back through the user-facing read path, not
  through the write endpoint's own success message.
- Kill only processes you started, by id, never by name.
- Frontend formatting: single quotes, 80 columns, 2-space tabs, `arrowParens: avoid`, ES5 trailing commas, LF line endings.

## Skill order for a backend service task

1. `grill-me` (skills/grill-me): five to eight questions, then
   `docs/designs/<slug>.md`. Stop asking as soon as goal, non-goals,
   success criterion, affected surfaces and one failure mode are known.
2. `write-issue` (skills/write-issue): one issue for the core feature with
   three to six acceptance criteria. That list is the definition of done.
3. Scaffold from `templates/backend-fastapi.md`, `templates/ci.yml`,
   `templates/.env.example`, `templates/Dockerfile`, `templates/.do/app.yaml`.
   First commit: scaffold, health endpoint, one passing test, CI file.
4. Build with tests first. If the `superpowers` plugin is installed, use
   its `test-driven-development` skill; otherwise write the failing test,
   then the code.
5. `feature-validate` (skills/feature-validate) shape for every check run:
   run each command for real, report exit code and tail.
6. `test-app-e2e` (skills/test-app-e2e) pattern: a stdlib runner that hits
   the running service over HTTP and tags each failure with a fix area.
   Adapt the endpoint list; keep the runner shape.
7. `feature-review` (skills/feature-review): read the diff against the
   issue's acceptance criteria before calling it done.
8. Deploy per the playbook's ship phase. Then `verify-techpulse`'s
   doctor-then-drive-then-evidence loop against the public URL.

## Skill order for a full-stack task

Same as above with these additions:

- After step 2, scaffold the frontend from `templates/frontend-vite-react.md`
  and wire the API base URL from an environment variable with a
  same-origin fallback.
- If the `designer-skills` pack is installed, `design-brief` is optional
  and must be capped at ten minutes. Otherwise pick one aesthetic and
  state it in the README.
- Before ship, run the `verify-feature` (skills/verify-feature) second
  gate: an exhaustive click sweep with Playwright that watches for
  uncaught errors and `console.error`. If Playwright is not available,
  drive the three main flows by hand and record what you clicked.
- Serve the built frontend from the backend or as an App Platform static
  site with an ingress rule, so there is one public URL.

## Agents

`agents/<name>/AGENT.md` are personas for subagents. In a three-hour
session the useful ones are `ops` (validate, build, review, in that
contract shape) and `blackbox-qa-validator` (test the deployed URL from
the outside and keep a behaviour spec). `coo` and `librarian` need the
agent-os daemon and are reference material here.

## How to use the playbook

`playbook/3-hour-build.md` is time-boxed. At each phase boundary, state
the wall-clock time, what artefacts the phase left behind, and what is
being cut if behind. Cutting scope is expected. Missing the deploy is not.
