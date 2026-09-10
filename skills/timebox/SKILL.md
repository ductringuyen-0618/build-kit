---
name: timebox
description: Run a three-hour build against a clock file at docs/TIMELOG.md with cut rules at fixed minutes, a commit every fifteen minutes, and a verify-before-trust checklist for every claim an assistant makes.
---

# Timebox: the clock is the runner

In a mission the runner keeps the plan and the stop rule. In a three-hour
session the runner is a clock and this file. Everything here exists so
that at minute 180 there is a public URL, a green check, a README that
runs, and a walkthrough with evidence, whatever else got cut.

## The clock file: `docs/TIMELOG.md`

Created at minute 0 by `scaffold-service`. One line per event, minute
first, in the order it happened. Never edited after the fact; a
correction is a new line.

```
# Timelog
start: 2026-09-09T14:00 local
0   stack: python-fastapi (prompt is AI-flavoured; provider fake carries over)
4   grill-me done, docs/designs/booking-rules.md
9   issue written, 4 acceptance criteria
14  scaffold green  https://github.com/<owner>/app/actions/runs/1
15  COMMIT chore: scaffold service with health check, tests and ci
29  COMMIT feat: booking model and create endpoint (criterion 1)
31  VERIFIED pytest 6 passed; curl POST 201 then GET shows row
44  COMMIT feat: reject overlapping bookings (criterion 2)
45  CHECK: criteria 1-2 passing, 3-4 pending. keep 3, cut 4 if not green by 85
58  COMMIT test: past-date rejection
61  smoke.json written, 5 checks, 5 pass locally
75  COMMIT feat: list bookings by room (criterion 3)
85  STOP ADDING. full check: ruff ok, mypy ok, pytest 11 passed, smoke 5/5
88  COMMIT docs: readme run and test sections
90  CHECK: deploy not proven -> ship phase now, second feature later if time
...
```

Three kinds of lines carry weight: `COMMIT` (with the message),
`VERIFIED` (with what was seen, not what was expected), and `CHECK`
(the decision at a cut point). If fifteen minutes pass without a
`COMMIT` line, the next action is a commit.

## Commit every fifteen minutes

The rule is mechanical: at 15, 30, 45, ... if the tree is dirty, commit
what is there with a conventional message. A commit that says
`wip: booking overlap check, tests pending` is better than twenty
minutes of uncommitted work when the machine, the network or the
assistant misbehaves. Squash later if the history needs to be tidy;
never rewrite what is already pushed.

The history is also the walkthrough. Interviewers read `git log` before
they read code. Small, ordered, criterion-named commits tell the story
without narration.

## Cut rules

The decision is written as a `CHECK` line at each minute whether or not
anything is cut.

| Minute | Ask | If the answer is no |
| --- | --- | --- |
| 45 | Are the first two acceptance criteria passing with tests? | Drop the last criterion now. Keep the first. |
| 85 | Is everything green locally (full check plus smoke)? | Stop adding. Fix until green. Nothing new after this line until the deploy is proven. |
| 90 | Is the deploy proven (live URL answering health)? | Skip the second feature. Go to the ship phase now. Come back only if minutes remain after the README. |
| 120 | Is the App Platform deploy green? | Switch to the container registry path or the generic fallback in the deploy skill. Do not debug the GitHub integration. |
| 140 | Did the review and the user-testing pass both return PASS? | Fix FAIL items that take one commit; cut the rest and list them under "next". |
| 150 | Is the second feature passing? | Revert to the last green commit (`git reset --hard <sha>` on the feature branch, or drop the branch). Write the idea into the demo notes as "next". |
| 160 | Is the README complete (what, URL, run, test, deploy)? | README before demo notes. Demo notes can be six lines. |
| 170 | Is the walkthrough script drafted? | Draft it from `docs/DECISIONS.md` and the timelog; three trade-offs and one AI mistake are enough. |

The rule behind the table: a smaller thing that is deployed, tested and
explained beats a bigger thing that is any one of those three short.

## Verify before trust

DigitalOcean's write-up of the interview says the panel watches "what
they verify versus what they trust" and "how they handle the moment
when the AI confidently produces something that doesn't work". Every
line below is a `VERIFIED` line in the timelog when done.

- **Run the test.** The assistant saying "tests pass" is a claim. The
  runner's summary line in your terminal is evidence. Paste it.
- **Open the URL.** After every deploy and after every restart, load
  the health path and the main page in a browser. A 200 from `curl` and
  a blank page in the browser are different facts.
- **Read the log.** After a deploy, `doctl apps logs <id> --type run --tail 50`.
  After a red CI, `gh run view <id> --log-failed`. The summary says
  "failed"; the log says why.
- **Prove the write through the read.** Create, then list. The create
  response's success message is not proof.
- **Try the error path.** Send the empty body, the wrong id. A 500 where
  a 4xx belongs is a bug the happy path hides.
- **Diff what the assistant changed.** `git diff --stat` before every
  commit. A "small fix" that touched twelve files is a question to ask
  out loud.
- **Check the dependency it added.** If a new package appeared, ask why
  and whether the stdlib or an existing dependency covers it.
- **Do not accept a green claim without output.** "I ran the checks and
  they pass" without the command and its last lines is not a pass.
  Ask for the output or run it yourself. This applies to subagents and
  validators too; the `PASS` first line is only as good as the command
  blocks under it.
- **Say the miss out loud.** When the assistant produces something
  confident and wrong, name it, fix it, and write one line in
  `docs/DECISIONS.md` under "what the AI got wrong". That line is the
  one the interviewer wants to hear in the walkthrough.

## Working with an assistant under the clock

- Give it the phase's skill and the contract, not the whole kit. Fewer
  instructions, followed.
- Ask for the diff and the command output, not a summary.
- When it stalls (same error twice), stop it, read the error yourself,
  and re-brief with the log. Two identical failures are a briefing
  problem.
- Keep it on one branch and one criterion at a time. Parallel work in a
  single session is how uncommitted changes get lost.
- At each cut point, decide yourself. The assistant will always want to
  finish the feature.

## Worked example: the minute-90 decision

```
88  COMMIT docs: readme run and test sections
90  CHECK: deploy not proven. criteria 1-3 green, 4 cut at 45.
    -> ship phase now. doctl apps create at 92.
92  doctl apps create --spec .do/app.yaml -> id a1b2c3
104 build ok, deploy failed: health check timeout (uvicorn bound to 127.0.0.1)
106 COMMIT fix: bind 0.0.0.0 in the container command
107 VERIFIED: what the AI got wrong -> generated CMD used 127.0.0.1; found in deploy log; noted in DECISIONS.md
112 deploy green. VERIFIED: curl https://...ondigitalocean.app/health 200 {"status":"healthy","checks":{"database":"ok"}}
114 smoke.py against live URL: 5/5 pass; output pasted into demo-notes.md
118 COMMIT docs: deploy section with live URL
120 CHECK: deploy green, 60 minutes left -> hardening: error envelope + request id, one commit each
```

## Tool notes

Any tool. The timelog is a text file; the clock is a watch. If the
assistant offers a recurring reminder, set one for "commit and log"
every fifteen minutes once; otherwise set a phone timer.
