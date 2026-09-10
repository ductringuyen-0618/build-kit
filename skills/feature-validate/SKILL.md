---
description: Runs the project's validation commands on the feature branch and reports PASS or FAIL.
---

> **Portability.** This skill was written for the agent-os daemon, where
> `mcp__agentos__*` are the kernel's syscalls. Outside agent-os, read each
> call as its intent: `get_context` = read the project's index or README;
> `read_wiki(page)` = read that Markdown page; `remember(page, content)` =
> write or append that Markdown page under `docs/` or `wiki/`;
> `request_approval` / `propose_feature` = write the proposal file and ask
> the human in chat; `emit_event` / `schedule` = note it for the human. The
> payload shape, the steps and the hard rules are the part to keep.

# Skill: feature-validate

Trigger: workflow `feature-request`, step `validate` (or `validate-fix`).
Agent: `ops`. Runs in the project's clone on `payload.branch`. Tool
grant: `Bash` only.

Your task payload is JSON: `{ branch, checks }`. `checks` is the exact
list of shell commands from the project's `build.checks` (e.g.
`["pnpm -r --if-present typecheck", "pnpm lint", "pnpm -r --if-present
test"]`).

## Steps
1. `git checkout payload.branch` if not already on it.
2. Run **every** command in `payload.checks`, in order, for real, with
   `Bash` — do not skip a check because an earlier one failed, and do
   not summarize what a check "would probably do" instead of running it.
   Capture each command's exit code and the last ~40 lines of its output.
3. Your final message's **first line** must be exactly `PASS` (every
   check exited 0) or exactly `FAIL` (at least one check exited nonzero).
   This is machine-parsed — nothing else may appear on that line.
4. After the PASS/FAIL line, report one block per check:
   ```
   ### <command>
   exit code: <n>
   <last ~40 lines of output>
   ```
   For a failing check, this tail is what `feature-build`'s next attempt
   (`build-fix`) is told to fix — be complete enough that it doesn't need
   to re-run the check just to see what broke.

## Hard rules
Read-only with respect to the repo's source — you may run test/build
tooling (which may write to `dist/`, `.cache/`, etc.) but never hand-edit
source files; that is `feature-build`'s job. Never push. Never edit
`docs/missions/coo/`.
