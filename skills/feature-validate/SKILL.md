---
name: feature-validate
description: Run the exact commands CI runs, plus the brief's validation contract, on a feature branch and report PASS or FAIL with real exit codes and output. Use after feature-build, as a separate pass that has not seen the builder's reasoning, and any time a green check is claimed without evidence.
---

# Feature validate

Purpose: prove, not assume, that the branch passes. The validator runs
commands and reports what happened. It never edits source and never
grades on intent. A claim of "tests pass" without output is a FAIL.

## Where it sits in the chain

```
feature-brief  ->  feature-build  ->  feature-validate  ->  feature-review
                                       (this skill)
```

Run it as a fresh pass: a new agent, a new chat, or a subagent that is
given only the branch and the brief, not the builder's transcript. The
value is independence.

In a 3-hour build: about 5 minutes per run. Run it every 20 minutes
during the build, at minute 85 before hand-off, and at minute 140 before
review. Full command lists on a cold cache can take longer; start with the
fastest command so a FAIL surfaces early.

## When to use

- `feature-build` reports done.
- Anyone says a check is green and there is no output to show for it.
- Before `feature-review`, which assumes the checks already pass.
- Before deploy.

## Inputs

- The branch name, `feature/<slug>`.
- `docs/features/<slug>.md` for the contract's command list, assertions
  and manual check.
- `.github/workflows/*.yml` (or the equivalent CI config: `.gitlab-ci.yml`,
  `Jenkinsfile`, `azure-pipelines.yml`). CI is the source of truth for
  which commands count.

## Steps

1. **Check out the branch** and confirm it:
   ```
   git checkout feature/<slug>
   git status --short
   git log --oneline <default-branch>..HEAD
   ```
   A dirty tree or zero commits is reported, not fixed.
2. **Build the command list from CI first.** Open every workflow file and
   copy each `run:` step that lints, typechecks, tests, or builds, in the
   order CI runs them, with the same working directory and environment
   variables. Then add any command in the brief's contract that CI does
   not already cover. If CI and the brief disagree, run both and say so.
3. **Install what CI installs** if the environment is fresh (`npm ci`,
   `pip install -r requirements.txt`, `go mod download`, and so on), using
   the same command CI uses.
4. **Run every command, in order, for real.** Do not stop at the first
   failure. Do not describe what a command "would" do. Capture the exit
   code and the last 40 lines of output for each. Set a timeout so one
   hung command cannot eat the phase; a timeout is a FAIL with the reason
   "timed out after N minutes".
5. **Check the assertions.** For each F/B/N item in the contract, name the
   test or command output that demonstrates it. If none does, run the
   manual check or a quick curl, and record what you saw. An assertion
   with no evidence is unverified, and unverified counts as FAIL.
6. **Write the report** (format below) to
   `docs/features/<slug>.validate.md` and paste the same text in chat.
   The first line is exactly `PASS` or `FAIL`. Nothing else on that line.
   Other tools and agents parse it.

## Output: `docs/features/<slug>.validate.md`

```markdown
PASS

Branch: feature/<slug> @ <short sha>   Date: <ISO date>
Source of commands: .github/workflows/ci.yml (jobs: lint, test, build)

## Commands
### `npm run lint`
exit code: 0
<last ~40 lines of output>

### `npm test`
exit code: 0
<last ~40 lines of output>

## Contract assertions
- F1: verified by tests/items.test.ts "paginates 20 per page"
- B1: verified by curl, GET /items?page=2 returned 200 with 20 rows
- N1: verified by tests/items.test.ts "unchanged for page=1"

## Manual check
<what was done and what was seen, or "not run: <reason>">

## Unverified
<assertions with no evidence, or "none">
```

For a FAIL the report is the same shape. The failing command's output tail
must be complete enough that `feature-build` can fix it without re-running
the command: include the file, line and message, not just "1 failed".

## Done when

- Every CI command and every contract command was executed, and each has
  an exit code and output tail in the report.
- Every contract assertion has a named piece of evidence or is listed
  under Unverified.
- The first line is `PASS` only if every exit code is 0 and Unverified is
  "none". Otherwise it is `FAIL`.
- The report file exists and the same text was posted in chat.

## Hard rules

- Read-only for source. Test and build tools may write `dist/`,
  `.cache/`, coverage folders; you never hand-edit a source file, a test,
  or a config to make a check pass. Fixing is `feature-build`'s job.
- Never mark a skipped or summarized command as passed.
- Never push. Never merge.
- Do not read the builder's transcript or reasoning. Read the brief, the
  code and the output.
