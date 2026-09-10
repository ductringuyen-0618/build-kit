# Manual click-through checklist

Use when no test runner can be installed, or as a second pass when the
smoke suite is green but the feature is visual or interactive. Run it
with the agent's browser tools if any exist. If none do, give this list
to the human and wait for their results. Never mark an item from
reading the code.

Record every item as `PASS`, `FAIL`, or `SKIP <reason>` with one line
of evidence: what you saw, a screenshot path, or the console line.

## Before you start

- [ ] The app is up and answered a real HTTP probe (status recorded).
- [ ] Browser devtools console and network tab are open, or the agent's
      console and network readers are loaded.
- [ ] You are on a throwaway database or data set.

## Load

- [ ] Root URL renders a visible heading within 5 seconds.
- [ ] Console has zero errors on load. Warnings are noted, not failed.
- [ ] Network tab shows no 4xx or 5xx on load.
- [ ] Hard refresh renders the same page, not a blank one or a stale
      cache.

## Navigation

- [ ] Click every top-level nav item. Each renders content, updates the
      URL (if the app routes), and produces no console error.
- [ ] Browser back returns to the previous view.
- [ ] A direct visit to a deep URL (paste it into a new tab) renders,
      not a 404 from the dev server.
- [ ] A made-up URL shows the app's not-found state, not a crash.

## The feature under test

- [ ] Reach it the way a user would (nav, link, or CTA), not by URL.
- [ ] Perform the primary action with valid input. Observe the result
      on screen.
- [ ] Read the result back through a second path (reload the page, open
      the list view, hit the read API). The write's own success toast
      does not count.
- [ ] Perform the action with invalid or empty input. A clear message
      appears; nothing crashes; nothing half-saves.
- [ ] Cancel or dismiss mid-way. State is unchanged.
- [ ] Repeat the action twice. No duplicate rows, no stuck spinner.
- [ ] Screenshot the end state.

## Forms and controls

- [ ] Every button on the touched page does something visible or is
      disabled with a reason.
- [ ] Focus is visible when tabbing; a modal traps focus and closes on
      Escape.
- [ ] Inputs keep their value after a validation error.

## Cross-cutting

- [ ] Resize to 375px wide. Nothing overflows horizontally; nav is
      still reachable.
- [ ] If the app has a dark or light theme, toggle it. Text stays
      readable.
- [ ] Stop the backend (if separate) and click once. The UI shows an
      error state, not a blank page or an infinite spinner. Restart it.
- [ ] Sign out and back in, if auth exists. The session survives a
      reload.

## Report

Copy the items with their PASS/FAIL/SKIP marks and evidence into the
`Ran:` and `Failures:` fields of the report contract in `SKILL.md`. The
first line of the report is `FAIL` if any item is `FAIL`, `BLOCKED` if
the app could not be reached, otherwise `PASS`.
