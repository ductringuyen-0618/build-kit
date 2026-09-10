# The loop behind the skills

Where the kit's loop came from, what leaked when it ran unattended, and
which skill closes each leak. Written from the evidence in the author's
production repositories (linked from the README's Provenance section),
not from memory. Where a claim is an inference rather than something
the evidence shows, it says so.

## The loop, as actually run

The author's automated feature workflow ran one feature end to end
through this loop on a live repository: a small user-facing toggle,
proposed by a scheduled routine, approved by a human, built by an agent,
validated and reviewed by two more, opened as a pull request, gated on
CI, and shipped with a report. Its git trail is the cleanest single
piece of evidence, so the loop is described against it.

| Step | What happens | Evidence |
| --- | --- | --- |
| 1. Clarify | Ask until the goal, non-goals, success criterion and one failure mode are known. For a new project this is `grill-me`; for a feature request in an existing repo the brief step reads the repo instead of asking. | The author's account that `grill-me` is the skill that works best from nothing; `feature-brief` steps 1 and 2 read context before writing. |
| 2. Brief with a validation contract | Write a proposal with fixed sections: what you get, why now, problem, proposed solution, effort, validation contract, risks. The contract lists the checks the build is held to. | `feature-brief`; the `docs: propose ...` commit that opened the run. |
| 3. Human gate | The proposal is pushed as `proposed` and nothing is built until a human flips it to `approved`. Undecided proposals are nudged and eventually expire. | The workflow's await-approval step; the `chore: approve ...` commit. |
| 4. Build on a branch | Status flips to `building` so a second builder cannot pick the same proposal. The worker creates `feature/<slug>`, implements exactly the contract, commits small conventional commits, never pushes. | Three `feat:` commits on the feature branch, one per contract item. |
| 5. Validate with the real check commands | A separate run with only a shell executes every command CI runs, reports exit code and the last lines per command, first line exactly `PASS` or `FAIL`. | `feature-validate`; the report's validation section shows both commands with exit codes and output. |
| 6. Independent review | A read-only run judges the diff against the proposal's solution and contract, not against generic taste. `FAIL` must name file, problem and what fixed looks like. | `feature-review`; the report cites file and line for each finding. |
| 7. One fix attempt | If validate or review fails, the worker runs again with the verbatim failure text, then validate and review run again. A second failure hands the proposal back as `approved`. | A `fix: resolve lint errors blocking ... PR` commit is this path in practice. |
| 8. Open the PR | Body is the proposal's summary plus the validation and review output verbatim. | The pull request the run opened. |
| 9. CI gate | Poll the PR's checks until nothing is pending. If a check fails, fetch the failing job's log, run the worker once more with that log, push, wait again. Only after green does ship run. | The workflow's wait-for-checks and fix-from-log steps; the routine's rule "nothing is shipped until the pull request's CI is green; local checks are necessary, never sufficient". |
| 10. Ship with a report | Flip the proposal to `shipped` and write a report with branch, PR, validation output and review output. | The `chore: ship ...` and `docs: report ...` commits. |

The scheduled routine runs the same loop as one long prompt instead of a
workflow engine. Its additions worth keeping: the worker, scrutiny
validator and product reviewer are three roles, each deliberately
skeptical of the last; the scrutiny validator has not seen the worker's
reasoning, only the proposal and the diff, and must open the CI workflow
files and run exactly the commands CI runs; every failed validation or
red CI is one attempt, and at three attempts the proposal is marked
`blocked` and never touched again; the validation contract is written as
functional, behavioural and negative assertions plus the exact test
commands; and the proposal's first two sections are written as a
decision brief for someone reading on a phone.

## What each skill contributes

| Skill | Role in the loop |
| --- | --- |
| `grill-me` | Step 1 for a new project. Batches of three or four questions, stop when goal, non-goals, success criterion, affected surfaces and one failure mode are known, then `docs/design.md`. |
| `write-issue` | Turns the design into one ticket with three to six testable acceptance criteria. In a timed build this is the definition of done for the core feature. |
| `write-prd` | Bigger-than-one-ticket scoping. Rarely needed in three hours. |
| `feature-brief` | Step 2. The seven-section proposal shape; `docs/features/<slug>.md` is what every later step reads. |
| `feature-build` | Steps 4 and 7. Resume from `git log`, fix the prior failure first, small commits, never push. The "never push" rule is what makes the CI gate a separate, checkable step. |
| `feature-validate` | Step 5. The `PASS`/`FAIL` first line is machine-parsed. |
| `feature-review` | Step 6. Read-only by tool grant, not by promise. |
| `missions` | The pattern: an orchestrator plans, workers build serially, validators that never saw the worker's reasoning verify, contracts are written before code, retries cap at three, state lives in one file. The briefings are the roles as pasteable text. |
| `ci-cd-github-actions`, `deploy-digitalocean-app-platform` | The infrastructure the gate and the demo depend on. |
| `smoke-verify`, `e2e-verify` | Validation against a running app, over HTTP and through the browser, with no project assumptions. |
| `propose-feature` | "What next" when the prompt is open or time remains. Prefers what users notice and what the codebase makes cheap. |

## What the evidence shows going wrong

These are the places the loop leaked in real runs. Each one became a
rule and a skill.

1. **The CI gate passed on zero checks.** The target repo had only a
   deploy workflow that runs on push to the default branch, so the pull
   request had no checks at all. The report read "CI passed" followed by
   an empty list. A gate that can pass vacuously is not a gate.
   `ship-gate` requires at least one named check and says "no CI on this
   PR" out loud when there is none.
2. **Validator output leaked the local clone path into the PR body.**
   The lint tail in the validation section carried the machine's
   absolute path into a public pull request. The output tail is useful;
   it needs a scrub for paths and secrets before it is pasted anywhere
   public. `ship-gate` includes that scrub.
3. **The contract's manual checks were never executed.** The contract
   had four "manual check" items. Validate ran lint and tests; review
   read the code and reasoned that the checks would hold. Nobody opened
   the site. The product reviewer judged "observable: yes" from the
   diff. That is the user-testing validator the missions pattern
   describes and nobody had written. `briefings/validator-user-testing.md`,
   `smoke-verify` and `e2e-verify` are that step.
4. **The retry budget counts attempts, not minutes.** The workflow
   allows one fix cycle; the routine allows three attempts. Both are
   right for an unattended daemon. In a timed session the cap has to be
   a clock: at some minute the fix is abandoned and the last green
   commit is what ships. `timebox` carries the cut rules.
5. **Nothing in the loop starts from an empty directory.** Every run
   began in a repo that already had CI, tests and a check list. A timed
   build begins with nothing. `scaffold-service` is minute 0 to 15:
   skeleton, health endpoint, one real test, README, `.env.example`,
   Dockerfile, CI job, first commit, green check.
6. **The report records what passed, not what was decided.** Shipped
   reports carry commits, validator findings and reviewer notes. They do
   not carry the alternatives that were rejected, or which parts of the
   diff were verified versus accepted from the model. A walkthrough is
   entirely about those two things. `walkthrough-prep` keeps
   `docs/DECISIONS.md` as you go and turns it into the talk.
7. **The proposal's title was written twice** by two roles that both
   thought they owned the file. Cosmetic, but it shows why a brief
   should own the whole file or none of it. The missions briefings give
   each role exactly one write target.

## What a timed build exposes

The loop above was built for hours-to-days runs where a daemon or a
routine has time to wait for a human, retry, and poll CI for half an
hour. A timed session compresses it to one person, one clock, and an
audience judging what was verified versus trusted. The gaps, in the
order they bite:

| Minute | Gap | Skill |
| --- | --- | --- |
| 0 | No scaffold step; no "minute 0" contract for what exists before the first commit. | `scaffold-service` |
| 15 | Contract exists as an issue, but no way to run it against the app without a project-specific runner. | `smoke-verify` |
| 45, 90, 150 | No cut rules, no clock, no commit cadence. | `timebox` |
| 90 | The worker, validator and reviewer roles exist as skills but not as briefings a person can paste into a second session. | `missions/briefings/` |
| 150 | Open PR, wait for CI, read the log, one fix, then and only then say shipped. Written in a workflow file, not as a skill. | `ship-gate` |
| 170 | Nothing produces the walkthrough: decisions, trade-offs, verified versus trusted, scaling answers grounded in the platform. | `walkthrough-prep` |

The through-line: every place the unattended version relies on time (a
long CI poll, a multi-day decision window, three attempts) the timed
version needs a clock rule instead, and every place the unattended
version relies on reading the diff (the product reviewer) the timed
version needs someone to open the URL.

## Verify versus trust

The habits the leaks above turned into. Each one is a `VERIFIED` line in
the timelog when done; the full list is in `timebox`.

- Run the test and paste the runner's summary line. "Tests pass" from an
  assistant is a claim, not evidence.
- Open the URL in a browser after every deploy and restart. A 200 from
  `curl` and a blank page are different facts.
- Read the log after a deploy or a red CI. The summary says "failed";
  the log says why.
- Prove a write through the read path. The create response's success
  message is not proof.
- Try the error path. A 500 where a 4xx belongs is a bug the happy path
  hides.
- Diff what the assistant changed before every commit. A "small fix"
  that touched twelve files is a question to ask out loud.
- Do not accept a green claim without the command and its output. This
  applies to subagents and validators too.
- Say the miss out loud. When the assistant produces something confident
  and wrong, name it, fix it, and write one line under "what the AI got
  wrong".
