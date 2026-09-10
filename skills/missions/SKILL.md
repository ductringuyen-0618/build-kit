---
name: missions
description: Multi-agent execution framework for long-running software goals (hours to days, not minutes) that combines an orchestrator, serial worker agents and independent validator agents around validation contracts written before any code. Use when the user wants to hand off a multi-milestone goal ("let it run for hours", "run a mission", "ship feature X end-to-end", "build the whole thing while I sleep") rather than pair on it; builds on grill-me, write-prd, write-issue and feature-brief for planning and on feature-validate and e2e-verify for verification.
---

> **Portability.** "Spawn a subagent" means: start a fresh session or chat
> with only the briefing as input. In Claude Code that is the `Agent`
> tool; in Cursor, Codex or a plain chat it is a new conversation with
> the briefing pasted in. The briefings are in `briefings/` next to this
> file; `README.md` in this folder says how to use them together.

# missions: long-running multi-agent execution

A "mission" is software work that is too big for one conversation but
small enough to define up front: ship a feature, complete a refactor,
build an MVP, migrate a service. You, the orchestrator, plan it, spawn
worker subagents to implement each milestone serially, spawn independent
validator subagents to confirm correctness, and produce a final report.

**Three roles:**

- **Orchestrator** (you): plans, delegates, verifies, never edits code
  directly during execution.
- **Workers** (subagents): fresh context per milestone, implement, commit
  via git, hand off via a structured report.
- **Validators** (subagents): adversarial; have never seen the worker's
  reasoning; produce verdicts independently.

**Validation is a contract written before code, not a check after it.**
The orchestrator writes assertions during planning that define
correctness in terms a worker cannot game by misreading requirements.

## When to use this

- Multi-milestone work the user wants to hand off completely.
- Anything described as "let this run for hours" or "overnight".
- A goal big enough to need planning, decomposition and verification.
- After `grill-me` and `write-prd`, when the user is ready to build.

## When not to use this

- Single-file edits or bug fixes: just do them.
- Open-ended exploration with no goal to converge on.
- Anything the user wants to be in the loop on at every step. Missions
  is for hand-off, not pair programming.
- A timed session of a few hours. Use `feature-brief`, `feature-build`,
  `feature-validate` and `feature-review` directly; the orchestration
  overhead here does not pay back inside three hours.

## The four phases

### Phase 1: Scope (planning)

Do not start implementation. Planning quality determines run quality.

1. **Run `grill-me`** to produce `docs/design.md`. This is the source of
   truth for the mission's goal and constraints.
2. **If scope warrants it (three or more milestones), run `write-prd`**
   to produce `docs/prd.md`. Smaller missions skip this.
3. **Decompose into milestones.** A milestone is one ticketable feature
   that can be delivered and validated independently. Aim for three to
   eight in total. Each milestone gets `write-issue` (a GitHub issue, or
   `docs/issues/<slug>-<n>.md` when `gh` is unavailable).
4. **Write the validation contract** for each milestone. Use the contract
   section of `feature-brief` as the shape and save it as
   `docs/features/<slug>-<n>.md`; that file is what the worker builds
   against and the validator checks against. The contract is:
   - functional assertions (command X produces output Y);
   - behavioural assertions (clicking Z navigates to W);
   - negative assertions (this must not happen);
   - performance assertions where they matter (p95 under N ms);
   - the exact test commands the validator will run.
5. **Save the mission plan** to `docs/missions/<slug>.md` with:
   - links to the design, the PRD if any, each issue and each brief;
   - the ordered list of milestones with their validation contracts;
   - estimated worker count, expected duration, kill-switch criteria.

### Phase 2: Approve

Show the user:

- the mission plan at a high level;
- the milestones in order;
- each milestone's validation contract (top three assertions, link to
  the full file);
- an estimated wall-clock and rough subagent budget.

Ask for explicit approval and wait. Do not start until you get a clear
yes. The user can approve (continue to Phase 3), modify (back to Phase 1
step 3 to re-decompose), or cancel (save the plan as a draft and stop).

### Phase 3: Execute (serial, with validators)

Process milestones one at a time. Workers share the codebase, so
parallel workers conflict; validators do not, so they run in parallel.
For each milestone:

1. **Spawn a worker subagent** using `briefings/worker.md`. The worker
   gets:
   - the milestone's issue and brief paths;
   - the validation contract;
   - the current git HEAD;
   - the hard constraint that it must commit before returning;
   - the hand-off report format from the briefing.
2. **Read the worker's hand-off report.** Check it has the required
   fields. If the worker says it is done but did not commit, treat it as
   a failure.
3. **Spawn the scrutiny validator** using `briefings/validator-scrutiny.md`.
   The validator has not seen the worker's reasoning or report. It
   receives only the milestone goal, the validation contract and the git
   diff. It runs the `feature-validate` procedure (the exact CI commands
   plus the contract's assertions), spawns a code-review pass for
   substantive changes, and returns `PASS` or `FAIL` with reasons.
4. **Spawn the user-testing validator** using
   `briefings/validator-user-testing.md` if the milestone touches a
   user-facing surface (UI, API contract, CLI). It receives only the
   user-flow assertions from the contract, drives the actual app with the
   `e2e-verify` procedure (browser driver, or curl for API-only), and
   returns a verdict plus reproductions of any failure.
5. **Decide the next move:**
   - both validators pass: mark the milestone complete, advance;
   - either fails: spawn the worker again with the failure report as
     additional input. Cap retries at three. After three failures, stop
     and surface the issue to the user.
6. **Update mission state** in `docs/missions/<slug>.md` after each
   milestone: what is done, what is next, what was learned. This file is
   the single source of truth that anyone, or a resumed mission, reads
   to know where things stand.

### Phase 4: Report and encode

When all milestones pass, or when stopping early:

1. **Write a final mission report** to `docs/missions/<slug>-report.md`:
   - what was implemented, linking each commit;
   - what was left undone, and why;
   - issues discovered along the way;
   - validator verdicts per milestone;
   - total wall-clock, subagent count, retries.
2. **Encode learnings.** If a worker tripped over the same gotcha twice,
   a procedure emerged that no existing skill covers, or a class of bug
   was caught by validators, add it to the relevant skill's
   `references/`, to the repo's `AGENTS.md`, or to a new skill.
3. **Hand back to the user** with the report path and a five-line
   summary in chat.

## How to spawn subagents

- **Worker**: a general-purpose agent; prompt is `briefings/worker.md`
  filled in with the milestone's values.
- **Scrutiny validator**: a general-purpose agent, or a code-review agent
  type if the tool has one; prompt is `briefings/validator-scrutiny.md`
  filled in.
- **User-testing validator**: a general-purpose agent with a browser
  driver or shell access; prompt is `briefings/validator-user-testing.md`
  filled in.

Run the two validators in parallel; they do not conflict. Run workers in
series; they share the codebase.

Fresh context is enforced by the briefing: each subagent gets only the
milestone goal, the contract, and the git diff or HEAD. Do not paste your
own reasoning into a briefing; that contaminates the independent check.

## Style rules

- **Plan more than you think you need to.** A thirty-minute plan that
  produces a clean validation contract beats a two-minute plan that
  produces a six-hour debug session.
- **Validators must not see the worker's reasoning.** If they do, they
  inherit the worker's blind spots. Brief them with the goal, not the
  approach.
- **Workers must commit before returning.** Without a commit the next
  worker cannot inherit the changes. "Done" without a commit is not done.
- **One milestone at a time.** For multi-day runs correctness compounds
  and parallelism burns tokens on conflicts.
- **Update mission state after every milestone.** The mission file is
  your only durable memory across the run.
- **Cap retries at three.** After three worker failures on the same
  milestone, surface it. Do not burn budget on a stuck milestone.

## Anti-patterns

- Skipping `grill-me` because "the user already knows what they want".
- Writing a milestone's validation contract after the worker is done.
- Letting workers write their own contracts; they optimise for
  pass-ability, not correctness.
- Briefing a validator with "the worker says it implemented X, please
  verify"; that contaminates the validator.
- Parallel workers on overlapping files.
- A long run with no kill switch. Define stop and rollback conditions
  during planning.

## Bundled files

`README.md` in this folder says how to use them together.

### briefings/

Templates the orchestrator pastes into subagent prompts. Do not
summarise them in chat; paste them whole:

- `runner.md`: the orchestrator's own checklist: mission file shape,
  attempts counter, stop rule.
- `worker.md`: for the implementer subagent.
- `validator-scrutiny.md`: for the code-review and tests validator.
- `validator-user-testing.md`: for the app-driving validator.

### references/

Open these when you need depth on one concept:

- `three-role-architecture.md`: orchestrator, worker and validator roles.
- `validation-contract-template.md`: how to write a milestone contract.
- `handoff-format.md`: the structured worker report shape.
- `serial-vs-parallel.md`: when each pattern beats the other.
- `recovery-procedures.md`: what to do when a milestone fails three times.
- `continuous-learning.md`: how to encode learnings back into skills.

### examples/

- `example-mission.md`: a worked mission file for a two-milestone
  feature, including one failed validation and the fix cycle.

The role pattern behind the briefings, and how to hand a brief to an
agent in each tool, is in the kit's `agents/README.md`.
