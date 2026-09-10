# Continuous learning: encoding what the mission taught

A mission that hits the same gotcha twice has found a missing rule. The
last phase of every mission writes those rules down where the next run
will read them, which is the skill, not the chat log.

## Triggers

Encode a learning when any of these happened:

- A worker tripped over the same thing twice (a test location
  convention, a formatter, a settings key).
- A validator caught a class of bug that a contract line would have
  prevented.
- A procedure emerged that no skill described (how to start the app for
  user testing, which port is safe, which command CI really runs).
- A fix attempt succeeded only after reading a log that the briefing
  should have included.

## Where it goes

| Learning is about | Write it in |
| --- | --- |
| this repo's conventions | `AGENTS.md` or `CLAUDE.md` at the repo root, under conventions |
| how to run or test this app | the README's run section, and the mission file's existing-behaviours list |
| a contract line everyone should have | `references/validation-contract-template.md` in this skill |
| a briefing gap for a role | the matching file in `briefings/` |
| a CI failure pattern | `skills/ci-cd-github-actions` section 5's table |
| a deploy failure pattern | `skills/deploy-digitalocean-app-platform` |
| a decision and its alternatives | `docs/DECISIONS.md` (see `skills/walkthrough-prep`) |

The author's agent runtime keeps a `learnings.md` beside each skill and
appends to it after every run. Outside such a runtime the equivalent is a dated line in
the skill's own file under a `## Learnings` heading; keep it to one
line per lesson with the date.

## Shape of a learning

One line: date, what happened, what to do next time.

```
- 2026-09-09: CI ran `ruff format --check` and the worker only ran
  `ruff check`; add the format check to the contract's command list.
```

## What not to encode

- One-off environment problems (a port in use, a flaky network).
- Anything already in the repo's docs or git history.
- Opinions about the code that no validator flagged.

## Closing the loop

The final mission report lists the learnings encoded and where. If the
list is empty after a multi-milestone mission, look harder; the second
attempt on any milestone is almost always a learning.
