# Per-feature behaviour map

A behaviour map is one Markdown file per user-facing feature, kept in
the repo (for example `docs/verify/<feature>.md`), that says what a
user can do and what proves each thing works. It turns "verify the app"
from a guess into a recipe, and it accumulates: every verified
behaviour becomes regression coverage for the next run.

Keep it optional. A fresh repo has none; write the first file when you
verify the first feature. Read the existing files before driving
anything.

## Index file (`docs/verify/README.md`)

- Baseline preconditions: how to boot, which port, which env vars, what
  throwaway data to use, which external dependencies gate which
  features.
- One line per feature file, in the order a user meets them.

## Feature file contract

Each file opens with an H1 and one paragraph of user-visible behaviour,
then exactly four H2 sections in this order.

### 1. Sub-features

Short stable IDs, one line each. IDs are what the report cites.

```
- `feed-render` shows a list of items from the real data source.
- `feed-search` narrows the list by free text.
- `feed-reset` clears every active filter.
```

### 2. How to get to it (user POV)

Every entry point: nav item, direct URL, CTA on another page, deep link
from an email or notification.

### 3. Driving it with the harness

Starts with `Preconditions:` (what must be up, which gates must be
green, what data must exist). Then, per sub-feature, pair one user
action with one exact command or selector and one observable result.

```
- `feed-search`. Fill `getByPlaceholder(/search/i)` with a word taken
  from a title already on screen.
  Observable result: item count drops and every remaining title or
  summary contains the term.
```

Assert on shape and non-emptiness for live data. Take test values from
what the page already shows, never from an invented fixture.

### 4. Gotchas

Traps that waste or invalidate a run: a testid that exists on the empty
state too, a persisted filter in local storage that makes a populated
backend look empty, a loose regex that matches a badge, a "dry run"
flag that still writes a row, an endpoint with no auth that deletes
data.

## Proof standards

- Exercise the real user path. Reading a list means the list on screen,
  not the repository behind it.
- Capture the action and the resulting state, not only the final
  screen.
- Prove a write by reading it back through the user-facing read path.
- Verify side effects next to what is visible (a row written, a counter
  changed, a health probe that now reports differently).
- Mock only where a production boundary already isolates the external
  system (a paid LLM, a third-party API). Do not mock the database.
- Report an unreachable path with the attempted command and the unmet
  precondition. Never report a path skipped for a missing gate as
  verified through a different path.

## Danger list

Keep a section in the index for calls that must never run during
verification unless they are the thing under test: bulk delete or wipe
endpoints, retention jobs without a dry-run flag, anything irreversible
on the instance's database, anything that spends real money (paid model
calls, SMS, payments). Two app instances sharing one database file, or
each starting its own scheduler, belong here too.
