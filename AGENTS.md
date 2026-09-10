# AGENTS.md

You are working with Tri Nguyen in a timed build session. This file is the
entry point for any AI coding assistant (Claude Code, Cursor, Codex,
Copilot, Windsurf, or a plain chat). Read it, then `playbook/3-hour-build.md`,
then the skills the playbook names for the current phase. Skills are plain
Markdown at `skills/<name>/SKILL.md`; read one in full before following it.
`docs/porting.md` says how to load a skill in each tool.

The stack is not fixed. Pick it once at minute 0 with
`playbook/stack-picker.md` and carry that choice into every later step.

## Non-negotiables

These are how Tri works. They are not suggestions.

1. Nothing is "done" until lint, typecheck, tests and the build pass
   locally and CI is green on the pushed branch. Say what ran and what the
   output was. Never claim a pass you did not see.
2. Every commit is a conventional commit: `feat`, `fix`, `docs`, `style`,
   `refactor`, `test`, `chore`. Small commits, in order, so the history
   tells the story in the walkthrough.
3. No secrets in the repo. Config comes from environment variables with a
   committed `.env.example`. The human pastes tokens; the assistant never
   sees, echoes or stores one. Grep for keys and tokens before every commit.
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
8. Keep the service root clean. One-off scripts go in `scripts/`. Do not
   create progress notes, changelogs or extra markdown files beyond
   README, `docs/designs/`, `docs/issues/` and `docs/demo-notes.md`.

## Conventions carried over from real projects

- Configuration has one source of truth: a settings object or config
  module that every other module reads. Nothing reads the raw environment
  directly. A prior bug came from one route resolving its own database
  path and reading a different SQLite file than the one being written.
- External services (LLM providers, payment, email) sit behind a small
  interface with a fake used in tests. Design for graceful fallback
  between providers. Cache expensive calls.
- Frameworks that redirect on missing or extra trailing slashes send a
  redirect the browser follows without CORS headers. Frontend endpoint
  constants use the exact canonical path the router mounts.
- Prefer ARIA roles and accessible names in browser tests, then
  `data-testid`. Never drive by coordinates.
- Prove a write by reading it back through the user-facing read path, not
  through the write endpoint's own success message.
- Kill only processes you started, by id, never by name.
- Frontend formatting: single quotes, 80 columns, 2-space tabs, `arrowParens: avoid`, ES5 trailing commas, LF line endings.

## Load order for a timed build

The order is the same for a backend-only service and a full-stack app.
Steps marked "full-stack" are skipped when there is no UI.

1. `playbook/stack-picker.md`: choose the stack in one minute. Say it out
   loud and write it at the top of `docs/demo-notes.md`.
2. `skills/grill-me`: five to eight questions, then `docs/designs/<slug>.md`.
   Stop as soon as goal, non-goals, success criterion, affected surfaces
   and one failure mode are known.
3. `skills/write-issue`: one issue for the core feature with three to six
   acceptance criteria. That list is the definition of done.
4. Scaffold from `templates/<stack>/` (Dockerfile, CI job, `.env.example`,
   App Platform component) and `skills/ci-cd-github-actions` for the
   workflow file and branch protection. First commit: scaffold, health
   endpoint, one passing test, CI green.
5. Full-stack: scaffold the frontend from `templates/vite-react/` or
   `templates/nextjs/` and wire the API base URL from an environment
   variable with a same-origin fallback.
6. Build with tests first. `skills/feature-build` for branch and commit
   discipline; if the `superpowers` plugin is installed, its
   `test-driven-development` skill; otherwise failing test, then code.
7. `skills/feature-validate` shape for every check run: run each command
   for real, report exit code and tail, first line `PASS` or `FAIL`.
8. `skills/test-app-e2e` pattern: a small stdlib runner that hits the
   running service over HTTP and tags each failure with a fix area. Adapt
   the endpoint list; keep the runner shape.
9. `skills/feature-review`: read the diff against the issue's acceptance
   criteria before calling it done.
10. Full-stack: `skills/verify-feature` second gate, an exhaustive click
    sweep that watches for uncaught errors and `console.error`. Without
    Playwright, drive the three main flows by hand and record what was
    clicked.
11. `skills/deploy-digitalocean-app-platform`: spec, create, logs, live
    URL, then the doctor-then-drive-then-evidence loop from
    `skills/verify-techpulse` against the public URL.
12. README, `docs/demo-notes.md`, final commit, CI green, browser tab open.

## Agents

`agents/<name>/AGENT.md` are personas for subagents. In a three-hour
session the useful ones are `ops` (validate, build, review, in that
contract shape) and `blackbox-qa-validator` (test the deployed URL from
the outside and keep a behaviour spec). `coo` and `librarian` need the
agent-os daemon and are reference material here.

## Tool-specific notes

- Claude Code: `CLAUDE.md` points here. Skills copied into `.claude/skills/`
  become invocable by name; `scripts/port.sh all claude <target>` does the copy.
- Cursor: `.cursor/rules/build-kit.mdc` points here and lists the skills.
  `scripts/port.sh <skill> cursor <target>` turns a skill into a rule file.
- Copilot: `.github/copilot-instructions.md` points here.
- Anything else: paste this file and the relevant `SKILL.md` into context.

Where a skill names a Claude-only tool (`AskUserQuestion`, the `Agent`
tool, `mcp__agentos__*` syscalls), treat the name as the intent and use
whatever the current tool offers: ask the human in chat, open a second
session, read or write the file directly.
