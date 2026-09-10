# How Tri builds: the loop behind the skills

Written 2026-09-09 from the evidence, not from memory: the skills in this
kit, the agent-os feature-request workflow and its design spec, a private
COO routine prompt (patterns only), and the last three days of commits,
proposals, pull requests and shipped reports in agent-os and
portfolio-website. Where a claim is an inference rather than something
the evidence shows, it says so.

## The loop, as actually run

One feature went end to end through the automated version of this loop on
2026-09-09: a dark-mode toggle for the portfolio site. Its trail in git
is the cleanest single piece of evidence, so the loop is described
against it.

| Step | What happens | Evidence |
| --- | --- | --- |
| 1. Clarify | Ask until the goal, non-goals, success criterion and one failure mode are known. For a new project this is `grill-me`; for a feature request in an existing repo the brief step reads the repo and wiki instead of asking. | Tri's own account: grill-me "works great for a new project". `feature-brief` step 1-2 read context before writing. |
| 2. Brief with a validation contract | Write a proposal with fixed sections: What you get, Why start this now, Problem, Proposed solution, Effort estimate, Validation contract, Risks. The contract lists the checks the build is held to. | `feature-brief` skill; `docs(coo): propose ...` commit 568c3ad in portfolio-website; the two proposals in agent-os. |
| 3. Human gate | The proposal is pushed with `status: proposed` and the workflow parks on `waitForEvent('decision.resolved')`. Nothing is built until a human flips it to `approved`. Undecided proposals are nudged at 3 and 6 days and expire at 7. | `featureRequest.ts` await-approval step; commit `chore(coo): approve 001-...` (b6f336e); agent-os commit 6da2602 for the nudge/expiry rule. |
| 4. Mark building, build on a branch | Status flips to `building` so a second builder cannot pick the same proposal. The worker creates `req/<slug>` (or resumes it from `git log` if it exists), implements exactly the contract, commits small conventional commits, never pushes. | `mark-building` step; `chore(coo): mark ... building` (8a16c88); three `feat:` commits d0b5c2c, d085b37, 670728a on `req/add-a-dark-mode-toggle-to-the-portfolio-site`. |
| 5. Validate with the real check commands | A separate run with only `Bash` executes every command in the project's `build.checks` list, reports exit code and the last 40 lines per command, first line exactly `PASS` or `FAIL`. | `feature-validate` skill; the report's Validation section shows both commands with exit codes and output. |
| 6. Independent review | A read-only run (`Read`, `Glob`, `Grep`, no shell) judges the diff against the proposal's Proposed solution and Validation contract, not against generic taste. `FAIL` must name file, problem and what fixed looks like. | `feature-review` skill; the report's Review section cites `tailwind.config.js:3`, `index.html:27-34`, etc. |
| 7. One fix attempt | If validate or review fails, the worker runs again with `priorFailure` set to the verbatim failure text, then validate and review run again. A second failure fails the request and hands the proposal back as `approved`. | `build-fix`, `validate-fix`, `review-fix` steps and the `unmark-building` catch in `featureRequest.ts`. The `fix: resolve lint errors blocking dark mode PR` commit (0cca70d) is this path in practice. |
| 8. Open the PR | Body = the proposal's What you get and Why start this now, plus the validation and review output verbatim. | PR #3 on portfolio-website; the adapter's `openPullRequest`. |
| 9. CI gate | Poll the PR's checks every 30 s for up to 30 min. If any check fails, fetch the failing job's log, run the worker once more with that log as `priorFailure`, push, wait again. A second red fails the request. Only after green does `ship` run. | `waitForChecks` and `ci-failure-log`, `build-fix-ci`, `push-fix` steps; the COO prompt's rule "nothing is shipped until the pull request's CI is green. Local checks are necessary, never sufficient." |
| 10. Ship with a report | Flip the proposal to `shipped`, write `docs/missions/coo/reports/<slug>.md` with branch, PR, validation output, review output, and bump the shipped counter in `state.md`. | `chore(coo): ship ...` (91b3ca0), `docs(coo): report ...` (b51bca4); agent-os reports for PR #6 and PR #7. |

The private COO prompt runs the same loop as a single long prompt instead
of a workflow engine. Its additions worth keeping: the worker, scrutiny
validator and product reviewer are three roles that are "each
deliberately skeptical of the last"; the scrutiny validator "has not seen
the worker's reasoning, only the proposal and the diff" and must open the
CI workflow files and run exactly the commands CI runs; every failed
validation or red CI is one attempt, and at three attempts the proposal
is marked `blocked` and never touched again; the validation contract is
written as functional, behavioural and negative assertions plus the exact
test commands; and "What you get" and "Why start this now" are written
as a decision brief for someone reading on a phone.

## What each existing skill contributes

| Skill | Role in the loop | Note |
| --- | --- | --- |
| `grill-me` | Step 1 for a new project. Batches of three or four questions, stop when goal, non-goals, success criterion, affected surfaces and one failure mode are known, then `docs/designs/<slug>.md`. | The design file is the input every later skill reads. Tri reports this is the skill that works best when starting from nothing. |
| `write-issue` | Turns the design into one ticket with three to six testable acceptance criteria. | The acceptance criteria are the validation contract in ticket form. In a timed build this is the definition of done for the core feature. |
| `write-prd` | Bigger-than-one-ticket scoping. | Rarely needed in three hours. Kept for completeness. |
| `missions` | The pattern: orchestrator plans, workers build serially, validators that never saw the worker's reasoning verify, contracts are written before code, retries cap at three, state lives in one file. | Tri's account: "splits the plan so work proceeds toward the end goal without losing track". The skill was the idea; agent-os's four feature skills and the COO prompt are the working implementation. Its `references/` and `briefings/` were never written until now. |
| `feature-brief` | Step 2. | The seven-section proposal shape. |
| `feature-build` | Step 4 and step 7. Resume from `git log`, fix `priorFailure` first, small commits, never push. | The "never push" rule is what makes the CI gate a separate, checkable step. |
| `feature-validate` | Step 5. | The `PASS`/`FAIL` first-line contract is machine-parsed. |
| `feature-review` | Step 6. | Read-only by tool grant, not by promise. |
| `ci-cd-github-actions`, `deploy-digitalocean-app-platform` | The infrastructure the gate and the demo depend on. | Written for the kit, doc-checked. |
| `test-app-e2e`, `verify-feature`, `verify-techpulse` | Validation against a running app. | All three are tied to one project's routes and scripts. Under time pressure they are too heavy to adapt. |
| `coo-ideate` | "What next" at minute 90. | Prefers what users notice and what the codebase makes cheap. |

## What the evidence shows going wrong

These are the places the loop leaked in real runs. Each one maps to a
skill added in this kit.

1. **The CI gate passed on zero checks.** The portfolio-website repo has
   only a deploy workflow that runs on push to `main`, so PR #3 had no
   checks at all. The report reads "CI passed:" followed by an empty
   list. The gate treated "nothing pending, nothing failed" as green. A
   gate that can pass vacuously is not a gate. `ship-gate` requires at
   least one named check and says "no CI" out loud when there is none.
2. **Validator output leaked the local clone path into the PR body.**
   The lint tail in the Validation section carried the machine's
   absolute clone path into a public pull request and the shipped
   report. The output tail is useful; it needs a scrub for paths and
   secrets before it is pasted anywhere public. `ship-gate` includes
   that scrub.
3. **The contract's manual checks were never executed.** The dark-mode
   validation contract had four "manual check" items (OS preference on
   first visit, persistence across reload, toggle visible on every
   route, no unreadable element in dark mode). Validate ran lint and
   tests; review read the code and reasoned that the checks would
   hold. Nobody opened the site. The agent-os reports show the same
   shape: the product reviewer judges "observable: yes" from the diff.
   That is the user-testing validator the missions skill describes and
   nobody had written. `briefings/validator-user-testing.md` and
   `smoke-verify` are that step, sized for a timed build.
4. **The retry budget counts attempts, not minutes.** The workflow allows
   one fix cycle; the COO prompt allows three attempts. Both are right
   for an unattended daemon. In a three-hour session the cap has to be
   a clock: at some minute the fix is abandoned and the last green
   commit is what ships. `timebox` carries the cut rules.
5. **Nothing in the loop starts from an empty directory.** Every run
   above began in a repo that already had CI, tests and a check list.
   The interview begins with nothing. `scaffold-service` is minute 0
   to 15: skeleton, health endpoint, one real test, README,
   `.env.example`, Dockerfile, CI job, first commit, green check.
6. **The report records what passed, not what was decided.** Shipped
   reports carry commits, validator findings and reviewer notes. They
   do not carry the alternatives that were rejected, or which parts of
   the diff were verified versus accepted from the model. The interview's
   second half is entirely about those two things. `walkthrough-prep`
   keeps `docs/DECISIONS.md` as you go and turns it into the talk.
7. **The proposal's H1 was written twice** (once by the brief, once by
   the wiki writer). Cosmetic, but it shows why the brief should own
   the whole file or none of it. The missions briefings give each role
   exactly one write target.

## What a three-hour interview exposes

The loop above was built for hours-to-days runs where a daemon or a
routine has time to wait for a human, retry, and poll CI for half an
hour. The interview compresses it to one person, one clock, and a live
audience judging what was verified versus trusted. The gaps, in the
order they bite:

| Minute | Gap | Skill |
| --- | --- | --- |
| 0 | No scaffold step; no "minute 0" contract for what exists before the first commit. | `scaffold-service` |
| 15 | Contract exists as an issue, but no way to run it against the app without adapting a project-specific runner. | `smoke-verify` |
| 45, 90, 150 | No cut rules, no clock, no commit cadence. | `timebox` |
| 90 | The worker, validator and reviewer roles exist as agent-os skills but not as briefings a person can paste into a second session or read as a checklist. | `missions/briefings/` |
| 150 | Open PR, wait for CI, read the log, one fix, then and only then say shipped. Written in a workflow file, not as a skill. | `ship-gate` |
| 170 | Nothing produces the walkthrough: decisions, trade-offs, verified versus trusted, scaling answers grounded in the platform. | `walkthrough-prep` |

The through-line: every place the daemon version relies on time
(30-minute CI poll, 7-day decision window, three attempts) the interview
version needs a clock rule instead, and every place the daemon version
relies on reading the diff (the product reviewer) the interview version
needs someone to open the URL.
