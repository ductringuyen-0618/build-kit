# Validation contract template

Written by the runner during planning, before any worker starts. The
worker builds to it; the scrutiny validator runs its commands; the
user-testing validator exercises its behavioural and negative lines. If
a line cannot be checked by one of those three, rewrite it until it can.

```markdown
## Validation contract: <milestone slug>

### Functional assertions (proven by a test or a command)
- `GET /api/items/` returns 200 and a JSON list.
- `POST /api/items/` with `{"name": "a"}` returns 201 and the created item with an `id`.
- <one line per acceptance criterion in docs/issues/<slug>.md>

### Behavioural assertions (proven by driving the app)
- After creating an item, `GET /api/items/` includes it (write proven through the read path).
- On the page, entering a name and pressing the button labelled "Add" shows the new row without a reload.

### Negative assertions (must NOT happen)
- `POST /api/items/` with an empty body returns 422 with `{"error": ...}`, not 500.
- `GET /api/items/does-not-exist` returns 404.
- No secret, token or absolute local path appears in the diff.

### Performance assertions (only if the milestone is about performance)
- `GET /api/items/?page_size=50` p95 under 300 ms locally with 1,000 rows.

### Check commands (exact, in order, from .github/workflows/)
- `cd backend && ruff check . && ruff format --check .`
- `cd backend && pytest tests -q`
- `cd frontend && npm run verify`
- `python scripts/smoke.py --base-url http://127.0.0.1:PORT --checks smoke.json` (or the curl lines from the `smoke-verify` skill)

### Existing behaviours that must keep working
- `GET /health` returns 200 with `"status": "healthy"`.
- <three to five lines>
```

## Writing rules

- One assertion per line, observable, with the status code or the visible
  text. "Works correctly" is not an assertion.
- Copy the check commands from the CI workflow, not from memory. If the
  workflow does not exist yet, write the commands here first and then
  put them in the workflow; the two must match.
- Negative assertions are the ones workers skip. Write at least two.
- Put the contract in the issue file under `## Verification` so there is
  one copy, and link to it from the mission file.
- Every functional and negative line that is an HTTP call becomes one
  smoke check (a curl line or a `smoke.json` entry, see the
  `smoke-verify` skill). Write them in the same pass.
