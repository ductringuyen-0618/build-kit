# missions: how to use the bundled files

`SKILL.md` is the pattern: a runner plans, workers build one milestone at
a time, validators who never saw the worker's reasoning verify, and one
mission file is the memory. The folders beside it are the working parts,
written from the version of this loop that shipped real features in the
author's automated feature workflow (see `docs/the-loop.md` at the kit
root).

## briefings/

Paste these into a fresh session with the placeholders filled in. In
Claude Code that is the `Agent` tool; in Cursor, Codex or a plain chat it
is a new conversation. Never paste the runner's own reasoning into them.

| File | Role | First line of its report |
| --- | --- | --- |
| `runner.md` | the orchestrator's own checklist: mission file, attempts counter, stop rule | n/a (writes the mission file) |
| `worker.md` | builds exactly the validation contract on `feature/<slug>`, commits, never pushes | `## Worker hand-off` with head sha |
| `validator-scrutiny.md` | runs the exact CI commands, proves each assertion, reports tails | `PASS` or `FAIL` |
| `validator-user-testing.md` | drives the running app from outside, scores each behavioural assertion | `PASS`, `FAIL` or `BLOCKED` |

## references/

Open when you need depth on one concept:

- `three-role-architecture.md`: who sees what, who may do what, and why
  the separation is enforced by the briefing rather than by trust.
- `validation-contract-template.md`: the contract shape (functional,
  behavioural, negative, performance, exact commands, existing
  behaviours) and how to turn it into `smoke-verify` checks.
- `handoff-format.md`: the fixed report shapes the runner parses.
- `serial-vs-parallel.md`: workers serial, validators parallel, and why.
- `recovery-procedures.md`: three attempts, no commit, BLOCKED, red CI,
  dead session, stop rule, rollback.
- `continuous-learning.md`: where a lesson gets written so the next run
  reads it.

## examples/

`example-mission.md` is a filled-in mission file for a two-milestone
feature, including one failed scrutiny pass and the fix cycle.

## In a three-hour build

The full pattern is too heavy for a timed session, but the roles are
not. Use `skills/timebox` as the runner, `briefings/worker.md` as the
build discipline, `briefings/validator-scrutiny.md` as the check before
every commit, `briefings/validator-user-testing.md` with
`skills/smoke-verify` after every feature, and `skills/ship-gate` to
finish. One or two milestones, not eight.
