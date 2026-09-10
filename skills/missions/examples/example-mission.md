# Example mission: scheduled ingestion for a news aggregator

A worked mission file for a small feature on a FastAPI service: fetch RSS
feeds on a schedule instead of only on demand. Two milestones, one
evening. Stack and paths are the kit's `python-fastapi` template layout.

```markdown
# Mission: articles refresh themselves every hour without an operator calling the ingest endpoint
Started: 2026-09-09T20:00   Budget: stop at 23:00 or after 6 worker runs   Stop rule: time
Design: docs/designs/scheduled-ingestion.md   PRD: none

## Milestones
| # | slug | contract | status | attempts | branch | head |
| 1 | ingest-scheduler | docs/issues/ingest-scheduler.md | done | 1 | req/ingest-scheduler | 3f2a9c1 |
| 2 | scheduler-status-endpoint | docs/issues/scheduler-status-endpoint.md | building | 0 | req/scheduler-status-endpoint | |

## Current
Milestone 2: scheduler-status-endpoint. Step: build. Since: 21:40.

## Log
- 20:05 planned two milestones; contracts written into both issue files
- 20:10 worker briefed for milestone 1
- 20:35 hand-off: head 8d1c2e0, 3 commits, pytest 41 passed
- 20:36 scrutiny + user-testing briefed in parallel
- 20:50 scrutiny FAIL: ENVIRONMENT=testing did not disable the scheduler; test_scheduler_disabled_in_testing missing. attempts=1
- 20:50 user-testing PASS: POST /api/ingest/ then GET /api/news/ shows new rows; scheduler log line seen
- 20:52 worker re-briefed with scrutiny output verbatim
- 21:10 hand-off: head 3f2a9c1, +1 commit "test: scheduler stays off when ENVIRONMENT=testing"
- 21:25 scrutiny PASS, user-testing PASS (re-run)
- 21:30 ship-gate: PR #14, CI Backend pass, Secret scan pass; report written
- 21:40 worker briefed for milestone 2
```

## Milestone 1 contract (from `docs/issues/ingest-scheduler.md`)

```
### Functional assertions
- With ENVIRONMENT=development the app starts an APScheduler job named "ingest" with an interval of INGEST_INTERVAL_MINUTES (default 60).
- With ENVIRONMENT=testing no scheduler starts (pytest must not spawn background jobs).
- The job calls the same service function the POST /api/ingest/ route calls.
### Behavioural assertions
- After the job runs once, GET /api/news/ returns at least one article that was not there before.
- The run log contains one line "ingest job finished: N new" per run.
### Negative assertions
- A feed that times out does not stop the job; the log records the feed and the job finishes.
- INGEST_INTERVAL_MINUTES is read only through Settings; grep for os.environ in src/services returns nothing new.
### Check commands
- cd backend && ruff check . && ruff format --check .
- cd backend && mypy . --ignore-missing-imports
- cd backend && pytest tests -q
- python skills/smoke-verify/scripts/smoke.py --base-url http://127.0.0.1:8000 --checks backend/smoke.json
### Existing behaviours
- GET /health 200 with "status": "healthy"
- POST /api/ingest/ still works on demand and returns {"ingested": N}
```

## What the example shows

- The first scrutiny pass failed on a negative assertion, not on a
  command: every check exited 0, but the "no scheduler in testing"
  line had no proof. That is the kind of failure the contract exists to
  catch.
- The user-testing validator passed on the same attempt. Both reports
  were read before deciding; the milestone still failed because either
  `FAIL` fails it.
- The fix was one commit with a test, briefed with the validator's
  output verbatim. Attempts went to 1, not 2, because the second
  validation passed.
- The ship step happened before milestone 2 started. A mission with
  milestone 1 "done" but unshipped has nothing to show if the stop rule
  fires during milestone 2.
