---
name: feature-build
description: Implement an approved feature brief exactly, on a feature/<slug> branch, in small conventional commits, touching nothing outside the brief's scope. Use after feature-brief has produced docs/features/<slug>.md and before feature-validate runs the checks.
---

# Feature build

Purpose: turn the validation contract in `docs/features/<slug>.md` into
code and tests, on its own branch, without side quests. The builder's
job is fidelity to the contract, not creativity around it.

## Where it sits in the chain

```
feature-brief  ->  feature-build  ->  feature-validate  ->  feature-review
                    (this skill)
```

In a 3-hour build: the 15-to-90 minute block for the core feature, or a
40-minute box for a second feature. Run the contract's commands every 20
minutes, not only at the end. Stop adding at minute 85 and hand off.

## When to use

- A brief exists and has been approved, or the run is unattended and the
  brief's assumptions were stated.
- A validate or review pass returned FAIL and you are the fix attempt.

## Inputs

- `docs/features/<slug>.md`. If it does not exist, stop and run
  `feature-brief` first. Do not build from a one-line request.
- Optional: a FAIL report from `feature-validate` or `feature-review`
  (their chat output, or `docs/features/<slug>.validate.md` and
  `docs/features/<slug>.review.md`). If present this is a retry and the
  report is your first priority.
- Repo conventions: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, lint and
  formatter config, existing code in the modules you will touch.

## Steps

1. **Branch.** Check whether `feature/<slug>` already exists:
   ```
   git rev-parse --verify feature/<slug>
   ```
   If it does, check it out and read `git log --oneline -20` to see what
   an earlier attempt committed. Resume from there. If it does not, create
   it from the default branch: `git checkout -b feature/<slug>`.
2. **If this is a retry**, read the FAIL report in full before touching
   code. Fix exactly what it names. Do not refactor around it.
3. **Read the contract** and turn each assertion (F1, B1, N1, ...) into a
   test or a checkable step before writing implementation. Negative
   assertions usually become tests that already pass today; keep them, they
   guard the scope.
4. **Implement one assertion at a time**: failing test, code, run the
   relevant command, commit. Commit message names the assertion:
   ```
   feat(items): paginate GET /items (F1, B2)
   test(items): page beyond last returns empty list (N1)
   ```
   Use conventional prefixes: `feat`, `fix`, `test`, `refactor`, `chore`,
   `docs`.
5. **Follow existing patterns.** If the repo has a way to do settings,
   errors, logging, or tests, use it. Do not introduce a second pattern
   next to an existing one.
6. **Every 20 minutes** run the full command list from the contract and
   fix red immediately. A red check found at minute 85 costs the whole
   phase.
7. **Update docs the contract implies**: README run instructions, an
   `.env.example` key, an API doc line. Nothing else.
8. **Finish**: run every contract command once more, then set `Status:
   built` in the brief and commit. Report in chat: the branch, the
   commits, the files changed, and any assertion you could not satisfy
   with the reason.

## Output

- Commits on `feature/<slug>`, one per assertion or small step.
- Tests that map to the contract's assertions by name.
- The brief's Status line updated to `built`.
- A chat summary of files changed and anything left unsatisfied.

## Done when

- Every assertion in the contract has a test or a documented manual
  check.
- Every command in the contract exits 0 locally.
- `git diff <default-branch>...feature/<slug> --stat` shows only files the
  brief's Proposed solution or Scope implied. An unexpected file is a
  scope leak; revert it or explain it.
- Nothing is pushed, merged, or opened as a pull request unless the
  human asked for that in this session.

## Hard rules

- Stay on `feature/<slug>`. Never commit to the default branch.
- Do not push, merge, rebase onto main, or open a PR unless told to.
- Do not edit `docs/features/<slug>.md` except its Status line. If the
  contract is wrong, say so in chat and stop; the brief owner changes it.
- Never commit build output, dependencies, `.env` files, or secrets.
- Do not "improve" nearby code the brief did not name. Note the idea in
  chat and move on.
