# Three roles: runner, worker, validators

The point is not the number of agents; it is that the person or process
checking the work did not do the work and did not watch it being done.

| Role | Sees | Can do | Returns |
| --- | --- | --- | --- |
| Runner (orchestrator) | the goal, the plan, every report | brief, read, decide, write the mission file | the next decision, the final report |
| Worker | the milestone goal, the contract, the branch, the prior failure | edit code, run tests, commit on the work branch | a hand-off with head sha and checks run |
| Scrutiny validator | the goal, the contract, the diff, the CI workflow files | run the exact check commands, read code, make small `style:`/`fix:` commits | `PASS`/`FAIL` first line, exit codes and tails, contract proof table |
| User-testing validator | the goal, the behavioural assertions, the running app's URL | drive the app from outside (browser, curl, smoke script) | `PASS`/`FAIL`/`BLOCKED`, observed versus expected per assertion, reproductions |

Product review, a fourth pass some teams run, is the user-testing
validator plus a taste judgement: would a user find this finished. In a
timed build fold it into the user-testing pass: the person who opens
the URL also asks "would I ship this".

## Why the separation holds up

- A worker reports what it intended. A validator reports what it
  observed. The gap between the two is where every "done but broken"
  lives.
- The scrutiny validator runs the same commands CI will run, in the same
  directories. If the workflow files disagree with the contract, the
  workflow files win, and the disagreement is a finding.
- The user-testing validator proves writes through the read path. The
  write endpoint's own `{"ok": true}` proves nothing.
- Independence is enforced by what the briefing contains, not by good
  intentions. A validator briefed with "the worker says it added X;
  please verify" inherits the worker's framing and blind spots.

## In one session, without subagents

The roles still work as three explicit passes with a context break
between them: finish the worker pass and commit; clear the chat or start
a new one; paste the scrutiny briefing with the diff; then the
user-testing briefing with the URL. The commit is the hand-off. The
rule "do not read the previous pass's reasoning" is what you are
protecting.

## Which briefing plays which role

| Role | File |
| --- | --- |
| Runner | `briefings/runner.md`; in a timed build, the `timebox` skill |
| Worker | `briefings/worker.md` |
| Scrutiny validator | `briefings/validator-scrutiny.md` |
| User-testing validator | `briefings/validator-user-testing.md`, with the `smoke-verify` skill for HTTP checks |
| Ship | the `ship-gate` skill |
