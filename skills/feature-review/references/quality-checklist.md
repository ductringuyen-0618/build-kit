# Product-quality checklist

Use during step 3 of `feature-review`. Skip sections that do not apply
(a backend-only change has no UI section). Each item is a question; a
"no" becomes a finding with a file and a fix.

## States
- Empty: what shows when there is nothing yet? Is there a next action?
- Loading: is there feedback for anything over about 300 ms?
- Error: is the message specific, recoverable, and free of stack traces?
- Success: does the user learn it worked, and where the result went?
- Boundaries: zero, one, many, maximum, unicode, very long strings,
  concurrent edits if the brief implies them.
- Partial: what happens if a dependency (DB, API, queue) is down?

## Copy
- Reads like the rest of the product: same tone, casing, terminology.
- No placeholder text (`lorem`, `TODO`, `asdf`, `Test button`).
- Error text says what happened and what to do, in user words.
- Labels, buttons and headings are consistent with existing screens.

## Consistency
- Naming matches neighbouring code (files, functions, routes, fields).
- Same error handling, logging, config access and validation approach as
  the rest of the codebase. No new pattern beside an old one.
- Styling uses existing tokens, components and spacing, not one-offs.
- Tests live where the other tests live and use the same runner.

## Accessibility basics (UI)
- Every interactive element is reachable and operable by keyboard.
- Focus is visible and moves sensibly, including into and out of dialogs.
- Inputs have labels; icon-only buttons have accessible names.
- Images and charts have alt text or a text equivalent.
- Colour is not the only carrier of meaning; contrast is not obviously
  low.
- Motion respects reduced-motion where the codebase already does.
- Layout survives a narrow viewport and 200 percent zoom.

## API surface (services)
- Status codes match the rest of the API for the same situations.
- Errors use the shared envelope; nothing leaks internals.
- Inputs are validated at the boundary; limits are enforced.
- Pagination, filtering and sorting follow existing conventions.
- Responses are stable: no field renamed or removed outside the brief.

## Leftovers
- TODO, FIXME, XXX, commented-out code, `console.log`, `print(` debug
  lines, `sleep` used to hide a race, skipped or focused tests.
- Files the brief did not name (scope leak).
- Generated files, lockfile churn, or formatting-only diffs mixed into
  feature commits.

## Documentation
- README or docs updated where the brief said they would be.
- `.env.example` has every new key with a comment, never a value.
