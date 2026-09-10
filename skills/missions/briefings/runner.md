# Briefing: mission runner (the orchestrator's own checklist)

The runner is the session that owns the plan. It never edits code during
execution. Its job is to keep the end goal and the current milestone in
view at the same time, brief the other roles, read their reports, and
decide the next move. Read this at the start of a mission and again
after every milestone.

## The one file

`docs/missions/<slug>.md` is the runner's memory and the broadcast to
anyone else reading. It holds, in this order:

```
# Mission: <goal in one sentence>
Started: <ISO time>   Budget: <wall-clock or minute limit>   Stop rule: <see below>
Design: docs/designs/<slug>.md   PRD: <path or none>

## Milestones
| # | slug | contract | status | attempts | branch | head |
| 1 | ... | docs/issues/...md | done / building / validating / blocked / cut | 0-3 | req/... | sha |

## Current
Milestone <n>: <slug>. Step: build | scrutiny | user-testing | ship. Since: <time>.

## Log
- <time> <what happened, one line>
```

Update it after every role returns. If the session dies, the next runner
reads this file and resumes from "Current".

## Loop per milestone

1. Read the goal line and the milestone table. Say, in one sentence, how
   this milestone moves the goal forward. If you cannot, the milestone is
   wrong; re-plan before spending a worker on it.
2. Brief the worker (`briefings/worker.md`) with only: repo, branches,
   milestone goal, contract, prior failure if any, attempt number.
3. Read the hand-off. Reject it if any required line is missing or the
   head sha is not on the branch (`git log` is the truth, not the
   message). A rejected hand-off is an attempt.
4. Brief the scrutiny validator (`briefings/validator-scrutiny.md`) and,
   when the milestone has user-facing surface, the user-testing validator
   (`briefings/validator-user-testing.md`), in parallel. Neither gets the
   hand-off.
5. Decide:
   - both `PASS`: mark done, record head sha, next milestone.
   - any `FAIL`: attempts += 1. If attempts < 3, brief the worker again
     with the verbatim failure as prior failure. If attempts == 3, mark
     `blocked`, write why, move to the next milestone that does not
     depend on it, and tell the human.
   - `BLOCKED` from a validator: environment problem, not an attempt; fix
     the environment (start the app, set the variable) and re-run the
     validator.
6. Ship step (`skills/ship-gate`): push, PR, CI gate, report. A milestone
   is not done until its CI is green or the mission explicitly ships
   without CI and says so in the log.
7. Write the log line. Update "Current". Only then start the next loop.

## Attempts counter

One counter per milestone, in the table. It increments on: a validator
`FAIL`, a rejected hand-off, a red CI run. It does not increment on a
`BLOCKED` environment or on a re-plan. It never resets. Three means
blocked. The counter is the only thing that stops a mission from
spending all night on one bug; keep it honest.

## Stop rule

Write the stop rule on the first line of the mission file before the
first worker starts. It is one of:

- a wall-clock time ("stop at 06:00 and report");
- a budget ("stop after N worker runs" or a token or cost cap);
- a state ("stop when milestone 3 is shipped or blocked").

When the stop rule fires: finish the role that is running (do not kill a
worker mid-commit), commit any work on its branch, update the mission
file, write the report (`skills/ship-gate` report shape per shipped
milestone, plus a "left undone" list), and hand back. Never extend the
budget yourself.

In a timed build session the stop rule is the clock in
`skills/timebox`, and the milestone table has one or two rows.

## Things the runner never does

Edit application code. Paste its own analysis into a validator's
briefing. Skip the user-testing validator because "it is just a backend
change" when the change alters a response shape. Mark a milestone done
on the worker's word. Say "shipped" before the ship step's report exists.
