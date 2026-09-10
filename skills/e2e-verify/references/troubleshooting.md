# Troubleshooting flaky or failing e2e runs

Read the matching section before touching app code. Fix the root cause,
rerun the whole suite, and paste the new output. Do not blanket-suppress
console errors, raise timeouts across the board, or add retries to make
a red run green; those hide the exact class of bug e2e exists to catch.

## Cascades: fix the first failure only

If the app failed to boot or the first probe failed, every later test
failed for the same reason. Fix that, rerun, and only then read the
rest.

## App never came up

- Read the last 50 lines of the server log. The cause is almost always
  the final traceback.
- Port already in use: find the owner before killing anything (see
  `platform-notes.md`). If it is not yours, run on another port and pass
  it to the tests through `BASE_URL`.
- Missing env var: compare `.env.example` with what is set. Settings
  files are often loaded relative to the working directory, so launching
  from the wrong directory silently reads different config.
- Import or compile error after a recent edit: the boot command fails
  fast; the log names the file.
- Dev server moved to the next free port: read the banner, not the
  README.

## Tests hit the wrong URL

- `baseURL` in the test config disagrees with the port the server
  printed.
- The frontend calls the backend at a hardcoded origin and the backend
  is on another port. Symptom: every panel empty, `ERR_CONNECTION_REFUSED`
  in the console, a "failed to fetch" toast.
- Trailing slash mismatch: a framework that redirects `/api/x` to
  `/api/x/` with a 307 may drop CORS headers on the redirect. Use the
  canonical path the server expects.

## CORS

- The browser blocks the response even though curl works. Check the
  allowed-origins setting includes the exact origin the frontend serves
  from, including port. Wildcard origins disable credentialed requests;
  list the origin instead.

## Two data stores

- A write reports success but the read path shows nothing. The write
  path and the read path resolve the database differently (two env vars,
  two defaults, a relative path from two working directories). Confirm
  both point at one file before blaming the UI.

## Empty screen on a populated backend

- A persisted filter or preference in local storage (or a cookie)
  survives reloads and restarts. Clear it, or click the app's own
  "reset filters" control, before concluding data is missing.
- Check the count the app itself displays: a non-zero count with an
  empty list is a filter; a zero count is a data problem.

## Console errors that are not the feature's fault

- Every "backend down" path logs `console.error`, so a suite that
  asserts a clean console fails for that reason alone when a dependency
  is missing. Read the message before blaming the assertion.
- Third-party scripts (analytics, fonts) blocked by the sandbox log
  errors. Allow-list those messages explicitly by text, not by
  disabling the check.

## Timing

- Waiting a fixed number of seconds is the source of most flakes. Wait
  on a condition: `expect(locator).toBeVisible()`, `waitForResponse`,
  `waitForLoadState('networkidle')`.
- A spinner selector that is also present on the empty state proves the
  panel mounted, not that data rendered. Count rows.
- Slow-motion and video settings meant for humans make agent runs time
  out. Set slow-mo to 0 and video to `retain-on-failure` for automated
  runs.

## Selectors

- A loose regex matches more than one element ("Saved" also matches
  "Unsaved changes"). Use `exact: true` or a tighter name.
- A click early in a sweep mutates the DOM and a later handle goes
  stale. Re-run scoped to that page before calling it a bug.
- Visual baselines depend on live content and on the platform the
  screenshot was taken on. Exclude them from the smoke loop.

## External dependencies

- A local model server, a queue, or a paid API is not running or has no
  credentials. This is an environment finding: report the feature as
  `Not verified` with the unmet precondition. Do not edit app code to
  make the test pass without the dependency.
- A dry-run flag may still write a bookkeeping row and change what a
  status endpoint reports afterwards. Observe what a dry run touched;
  do not trust the name.

## The test itself is wrong

- The response shape changed on purpose and the assertion is stale. Fix
  the test, not the app, and say so in the report.
- Never change app behaviour to satisfy a buggy test.

## Before you report

- Rerun the full suite once more after every fix, even if a subagent
  says it did. Paste that final output.
- State which failures are new versus pre-existing by running the suite
  against the previous commit (`git stash` or a second worktree).
