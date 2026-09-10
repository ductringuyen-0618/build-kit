---
name: ship-gate
description: Push, open the pull request, wait for CI, read the failing job log, make one fix attempt, and only after a green run write the shipped report; use before saying done or shipped.
---

# Ship gate: nothing is shipped until CI is green

Local checks are necessary, never sufficient. An automated pipeline
that refuses to write `shipped` until the pull request's checks are
green is the origin of this skill; this is that rule as a checklist a
person or an assistant follows in any tool.

## Preconditions

- The work is on a branch (`feature/<slug>` or `feature/<slug>`), committed,
  with the scrutiny validator's `PASS` in hand and, for user-facing
  work, the user-testing validator's `PASS` too.
- The branch has never been pushed by the worker. Pushing is this
  skill's job, so the gate is a separate, visible step.
- `gh auth status` succeeds. If it does not, the human logs in; the
  assistant never handles the token.

## Steps

1. **Scrub before you push.** The validator output you are about to put
   in a PR body was produced on a local machine. Search it for absolute
   paths, usernames, tokens and email addresses and replace them with
   `<path>` or drop the line. Validator output has ended up in a public
   pull request with a local clone path in it; do not repeat that.

   ```
   grep -n -E '([A-Za-z]:\\|/home/|/Users)[^ ]*' validation.txt
   grep -n -E '(ghp_|sk-|xox[bp]-|AKIA)[A-Za-z0-9_-]{8,}' validation.txt
   ```

2. **Push and open the PR.**

   ```
   git push -u origin feature/<slug>
   gh pr create --base main --head feature/<slug> --title "feat: <title>" --body-file pr-body.md
   ```

   `pr-body.md` has, in order: the proposal's What you get and Why start
   this now (or the issue's context), the validation contract, the
   scrutiny validator's report (first line and the command blocks), the
   user-testing validator's report, and a "left undone" list. No
   secrets, no local paths.

3. **Wait for CI, for real.**

   ```
   gh pr checks <number> --watch --interval 30
   ```

   or, when `--watch` is not available or the terminal is shared:

   ```
   gh pr view <number> --json statusCheckRollup --jq '.statusCheckRollup[] | "\(.name // .context)\t\(.status // .state)\t\(.conclusion // "")"'
   ```

   Repeat every 30 seconds until nothing is pending. Cap the wait at 30
   minutes in a long run and at the `timebox` cut rule in a timed build.

   **Zero checks is not green.** If the rollup is empty, the repo has no
   workflow that runs on pull requests (a deploy-on-push workflow does
   not count). Automated gates have reported "CI passed" over an empty
   list. Say "no CI on this PR" in the report and either add a workflow
   that runs lint, tests and build on `pull_request` now, or ship with
   that sentence in the report. Never write "CI passed" with nothing
   listed.

   Skipped checks are fine. Any `FAILURE`, `TIMED_OUT` or `CANCELLED`
   is not.

4. **Read the failing job's log, not the summary.**

   ```
   gh run list --branch feature/<slug> --limit 3
   gh run view <run-id> --log-failed
   ```

   Keep the last 60 lines of the failing step. That tail is the whole
   input to the fix attempt; a fix briefed with "CI is red" instead of
   the log is a guess.

5. **One fix attempt.** Brief the worker (yourself, or a fresh session
   with the worker briefing from the `missions` skill) with the log tail
   as the prior failure and the instruction "make this exact job pass".
   Commit as `fix:` or `style:`, push, and go back to step 3. The three
   usual causes: formatter drift (run the formatter, commit
   `style: format`), lockfile mismatch (run the install once without
   `--frozen`/`ci`, commit the lockfile), an environment variable present
   locally and absent in the job (add it to the job's `env:` with a safe
   test value and to `.env.example`).

6. **Second red stops the gate.** Do not attempt a third fix inside this
   skill. Leave the branch and the PR in place, record the failing check
   and the run URL in the report under "not shipped", and hand back to
   the runner (in a mission: attempts += 1) or, in a timed build, to the
   `timebox` cut rule: ship the last green commit instead.

7. **Green, then and only then:** merge if the plan says merge
   (`gh pr merge <number> --squash --delete-branch` or keep the branch
   for the walkthrough), then write the shipped report and say the word.

## The shipped report

Written to `docs/missions/<slug>-report.md` in a mission, or appended to
the demo notes in a timed build. Every field is required; an empty
field says "none", never blank.

```
## Shipped: <slug>
- branch: feature/<slug>   pr: <url>   merged: yes | no (kept for review)
- ci: <check name>: pass ... run: <url>          (or: no CI on this PR, see note)
- deployed: <url> | not deployed
- commits:
  - <sha> <message>
- validator findings: <scrutiny first line>; <commands and exit codes>; <fixes the validator applied>
- user-testing findings: <first line>; <assertion: observed> per line
- reviewer notes: <verbatim, or "no separate review; folded into user testing">
- what the AI got wrong and how it was caught: <one or two lines, or "nothing caught">
- left undone: <list or none>
```

The report is the artefact the walkthrough reads from. The "what the AI
got wrong" line is the one a reviewer is listening for.

## Worked example (timed build, minute 155 to 168)

```
$ grep -n -E '([A-Za-z]:\\|/home/|/Users)' validation.txt        # nothing
$ git push -u origin req/booking-overlap
$ gh pr create --base main --head req/booking-overlap --title "feat: reject overlapping bookings" --body-file pr-body.md
https://github.com/<owner>/my-app/pull/2
$ gh pr checks 2 --watch --interval 30
Backend      fail   1m12s   https://github.com/<owner>/my-app/actions/runs/1234
Secret scan  pass   22s     ...
$ gh run view 1234 --log-failed | tail -60
...
Backend  ruff format --check .
Would reformat: src/services/booking_service.py
1 file would be reformatted
```

Fix attempt: `ruff format src`, commit `style: format booking service`,
push, watch again:

```
Backend      pass   1m05s
Secret scan  pass   20s
```

Report line: "ci: Backend pass, Secret scan pass, run .../runs/1235;
what the AI got wrong: the generated service file was not formatted;
caught by CI, fixed in one commit."

## Per-stack notes

The gate is the same for every stack. What differs is the check names
to expect (whatever the workflow's jobs are called) and the usual first
red: Python formatter drift (`ruff format .`), Node lockfile mismatch
(`npm install` once, commit the lockfile), Spring Boot tests needing a
Postgres service container in the job, Go `gofmt -l` listing a file.

## Tool notes

`gh` is the only tool this skill needs. In Claude Code a subagent can
run the fix attempt with the worker briefing; in Cursor or Codex open a
new chat for it so the fix is briefed from the log, not from memory of
the build. A GitHub MCP server can replace `gh pr view` for the poll,
but `--log-failed` has no equivalent there; keep `gh` for step 4.
