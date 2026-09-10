# AGENTS.md

This is the entry point for any AI coding assistant (Claude Code, Cursor,
Codex, Copilot, Windsurf, or a plain chat) working with this kit. Read it,
then `playbook/3-hour-build.md`, then the skills the playbook names for
the current phase. Skills are plain Markdown at `skills/<name>/SKILL.md`;
read one in full before following it. `docs/porting.md` says how to
install them in each tool.

The stack is not fixed. Pick it once at minute zero with
`playbook/stack-picker.md` and carry that choice into every later step.

## Non-negotiables

1. Nothing is "done" until lint, typecheck, tests and the build pass
   locally and CI is green on the pushed branch. Say what ran and what the
   output was. Never claim a pass you did not see.
2. Every commit is a conventional commit: `feat`, `fix`, `docs`, `style`,
   `refactor`, `test`, `chore`. Small commits, in order, so the history
   tells the story.
3. No secrets in the repo. Config comes from environment variables with a
   committed `.env.example`. The human pastes tokens; you never see, echo
   or store one. Grep for keys and tokens before every commit.
4. The README has run instructions that work from a fresh clone: install,
   run, test, deploy. Write it as you go, not at the end.
5. There is a deploy target from minute one. The default is DigitalOcean
   App Platform via `.do/app.yaml`; the fallback is the Dockerfile on any
   host. A prototype nobody can open in a browser is not a prototype.
6. Verify before you trust. Run the thing. Curl the endpoint. Click the
   button. When a generated result is confident and wrong, say so, fix
   it, and note it in `docs/demo-notes.md`.
7. Ask before you build when the answer changes the design. Use
   `grill-me` for that. Do not ask about things you can read from the
   repo.
8. Keep the service root clean. One-off scripts go in `scripts/`. Do not
   create progress notes, changelogs or extra Markdown beyond the README
   and the files this kit names under `docs/`.

## The loop

Every unit of work, from a three-hour prototype to one feature in an
existing repo, runs the same loop:

1. **Clarify.** Ask until goal, non-goals, success criterion, affected
   surfaces and one failure mode are known (`grill-me`, writing
   `docs/design.md`). For an existing repo, read it first (`codebase-map`).
2. **Brief with a validation contract.** Write `docs/features/<slug>.md`
   (`feature-brief`): what you get, scope, and a contract of functional,
   behavioural and negative assertions plus the exact commands that must
   exit 0. A GitHub issue or `docs/issues/<slug>.md` (`write-issue`) is
   the input to the brief; the brief is the source of truth for the build.
3. **Build on a branch.** `feature/<slug>`, small conventional commits,
   nothing outside the brief's scope (`feature-build`).
4. **Validate with the real CI commands.** Run each one, report exit code
   and output, first line `PASS` or `FAIL` (`feature-validate`). Then
   prove it from the outside (`smoke-verify` for HTTP, `e2e-verify` for a
   UI).
5. **Independent review.** A pass that has not seen the builder's
   reasoning judges the branch against the brief (`feature-review`).
6. **Pull request.** Body is the brief's summary plus the validation and
   review output verbatim.
7. **CI gate.** Green on the pushed branch, or it goes back to step 3.
8. **Ship with a report.** Deploy, prove the public URL, run `ship-gate`,
   and leave `docs/demo-notes.md` and the README in a state a stranger
   can follow.

## Conventions

- Configuration has one source of truth: a settings module that every
  other module reads. Nothing reads the raw environment directly. Two
  code paths that each resolve their own database location will one day
  read and write different files.
- External services (LLM providers, payment, email) sit behind a small
  interface with a fake used in tests. Design for graceful fallback
  between providers. Cache expensive calls.
- Frameworks that redirect on a missing or extra trailing slash send a
  redirect the browser follows without CORS headers. Frontend endpoint
  constants use the exact canonical path the router mounts.
- Prefer ARIA roles and accessible names in browser tests, then
  `data-testid`. Never drive by coordinates.
- Prove a write by reading it back through the user-facing read path, not
  through the write endpoint's own success message.
- Kill only processes you started, by id, never by name.
- Pick one formatter per language at scaffold time, commit its config,
  and run it in CI. Do not argue about style after that.

## Skill load order

### Backend-only service

1. `timebox`: start the clock, know the phase budgets and the cut table.
2. `playbook/stack-picker.md`: choose the stack in one minute. Write it
   at the top of `docs/demo-notes.md`.
3. `grill-me`: five to eight questions, then `docs/design.md`.
4. `write-issue`: one issue for the core feature with three to six
   acceptance criteria, then `feature-brief` to turn it into
   `docs/features/<slug>.md` with the validation contract.
5. `scaffold-service` with `templates/<stack>/`, then
   `ci-cd-github-actions` for the workflow and branch protection. First
   commit: scaffold, health endpoint, one passing test, CI green.
6. `feature-build`: tests first, small commits, on `feature/<slug>`.
7. `feature-validate` after every meaningful change and before every push.
8. `smoke-verify`: hit the running service over HTTP.
9. `feature-review` against the brief before calling it done.
10. `deploy-digitalocean-app-platform`: spec, create, logs, live URL, then
    `smoke-verify` again against the public URL.
11. `ship-gate`, then `walkthrough-prep` for the notes and README.

### Full-stack app

Same order, with these additions:

- After step 5, scaffold the frontend from `templates/vite-react/` or
  `templates/nextjs/` and wire the API base URL from an environment
  variable with a same-origin fallback.
- After step 8, `e2e-verify`: boot both halves, drive the main flow in a
  browser, watch for uncaught errors and `console.error`. Without
  Playwright, click the three main flows by hand and record what was
  clicked.
- In step 10, verify the deployed UI in a browser with the network tab
  open, not only the API.

### When the next thing is not specified

`propose-feature` reads the repo and puts one well-argued feature in
front of the human. `write-prd` sits between `grill-me` and `write-issue`
only when the work is bigger than one ticket. `missions` is the pattern
for multi-hour, multi-milestone runs with independent validators; it is
reference material in a timed session.

## Role briefs

`agents/*.md` are role briefs for splitting work across agents:
coordinator, builder, scrutiny validator, user tester, product reviewer.
Each is a single responsibility with a fixed report format. Validators
and reviewers get a fresh context, never the builder's transcript. See
`agents/README.md` for how to hand one to an agent in each tool.

## Tool-specific notes

- Claude Code: `CLAUDE.md` points here. After `npx skills add`, skills
  are under `.claude/skills/` and invocable by name (`/grill-me`). Role
  briefs can be copied to `.claude/agents/<role>.md` with a `name` and
  `description` frontmatter to become subagent types.
- Cursor: `.cursor/rules/build-kit.mdc` points here. Installed skills
  live under `.agents/skills/`; otherwise reference one with
  `@skills/<name>/SKILL.md`.
- Codex and Windsurf: read `AGENTS.md` and `.agents/skills/` on their own.
- Copilot: `.github/copilot-instructions.md` points here; attach a
  `SKILL.md` as context when it is not installed.
- Anything else: paste this file and the relevant `SKILL.md` into the
  chat.

Where a skill names a tool that only one harness offers (a question
prompt, a subagent tool, a browser driver), treat the name as the intent
and use whatever the current tool has: ask the human in chat, open a
second session, drive the app by hand.
