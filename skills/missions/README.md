# missions: bundled files status

`SKILL.md` refers to two folders that were never committed to the source
repository and could not be found in its git history or on the author's
machine:

- `references/`: `three-role-architecture.md`, `validation-contract-template.md`,
  `handoff-format.md`, `serial-vs-parallel.md`, `recovery-procedures.md`,
  `continuous-learning.md`
- `briefings/`: `worker.md`, `validator-scrutiny.md`, `validator-user-testing.md`
- `examples/example-mission.md`

Do not stall looking for them. `SKILL.md` describes each file's purpose
where it references it, and the four phases plus the style rules are
complete on their own. If a run needs a briefing, write a short one from
the bullet list in "Phase 3" (what the worker or validator receives, what
it must return) and save it under `briefings/` so the next run has it.

This skill is reference material for a timed build. It is designed for
multi-hour, multi-milestone runs and is too heavy for a three-hour
session; use `feature-build`, `feature-validate` and `feature-review`
there instead.
