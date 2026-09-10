---
name: smoke-verify
description: Run a generic HTTP smoke check (stdlib Python, one file, any stack) against a running service, locally after every feature and against the deployed URL before the demo. Turns a validation contract or an issue's acceptance criteria into a JSON list of GET and POST checks with expected status and substring, prints PASS or FAIL per check and exits nonzero on failure. Use when asked to "smoke test", "verify the deploy", "check the endpoints", "is it up", or before saying a feature is done.
---

# Smoke-verify: prove the running service does what the contract says

`scripts/smoke.py` is about 130 lines of standard-library Python. It
takes a base URL and a list of checks, sends each request, compares the
status code and an optional substring, and prints one line per check
and a summary. Exit 0 when everything passed, 1 when something failed,
2 when the base URL never answered. No install step, no framework
knowledge, works against FastAPI, Spring Boot, Fastify, Go, Next.js or
anything else that speaks HTTP.

It is the HTTP half of verification; `e2e-verify` is the browser half
for a UI. Both are black-box, over the wire, one result per check with
enough detail to act on, and neither assumes a project's routes, scripts
or ports.

## When to run it

| Moment | Base URL | Checks |
| --- | --- | --- |
| After the scaffold commit | `http://127.0.0.1:<port>` | health only (the default when no checks are given) |
| After every feature, before its commit | local | the feature's contract lines plus health |
| Before the ship phase | local, against the last green commit | the whole file |
| After deploy, before the demo | the App Platform `DefaultIngress` URL | the whole file; paste the output into `docs/demo-notes.md` |
| During the walkthrough, if asked "does it work" | deployed | run it live; the output is the answer |

A green run against localhost says nothing about the deploy. Run it
against the public URL and keep that output.

## Usage

```
python skills/smoke-verify/scripts/smoke.py --base-url http://127.0.0.1:8000
python skills/smoke-verify/scripts/smoke.py --base-url http://127.0.0.1:8000 "GET /health 200 healthy"
python skills/smoke-verify/scripts/smoke.py --base-url https://my-app-xxxxx.ondigitalocean.app --checks smoke.json
python skills/smoke-verify/scripts/smoke.py --base-url URL --checks smoke.json --json > docs/smoke-report.json
```

Copy the script into the session repo as `scripts/smoke.py` (the skill
installer carries `scripts/` with the skill) so the README can say `python
scripts/smoke.py --base-url ... --checks smoke.json` and CI can run it
against a server started in the job.

Inline check grammar, one quoted string per check:

```
METHOD PATH STATUS [JSON_BODY] [SUBSTRING]
"GET /health 200 healthy"
'POST /api/items/ 201 {"name":"a"} a'
"GET /api/items/does-not-exist 404 not found"
```

JSON file grammar, a list of objects:

```json
[
  {"name": "health", "method": "GET", "path": "/health", "status": 200, "contains": "healthy"},
  {"name": "create", "method": "POST", "path": "/api/items/", "status": 201, "body": {"name": "widget"}, "contains": "widget"},
  {"name": "read back", "method": "GET", "path": "/api/items/", "status": 200, "contains": "widget"},
  {"name": "empty body rejected", "method": "POST", "path": "/api/items/", "status": 422, "body": {}},
  {"name": "missing id", "method": "GET", "path": "/api/items/does-not-exist", "status": 404},
  {"name": "admin needs token", "method": "POST", "path": "/api/admin/wipe", "status": 401, "headers": {"X-Admin-Token": "wrong"}}
]
```

`headers` is optional. `body` may be an object (sent as JSON) or a
string (sent as-is). Checks run in order, so a create followed by a
read-back proves the write through the read path, which is the rule
from `AGENTS.md`.

## Turning a contract into checks

Take the issue's acceptance criteria or the proposal's validation
contract and write one check per line that is an HTTP call:

| Contract line | Check |
| --- | --- |
| "returns 200 and a JSON list" | `GET` path, status 200, contains `[` |
| "creates and returns the item with an id" | `POST` with body, status 201, contains `"id"` |
| "the created item appears in the list" | `GET` list after the `POST`, contains the unique name you posted |
| "empty body is rejected with 422, not 500" | `POST` with `{}`, status 422 |
| "unknown id returns 404" | `GET` a made-up id, status 404 |
| "health names the database" | `GET /health`, status 200, contains `database` |
| "admin route needs the token" | `POST` with a wrong header value, status 401 or 403 |

Lines that are not HTTP calls (a UI element is visible, a log line
appears, a scheduler runs) belong to the user-testing briefing in
`skills/missions/briefings/validator-user-testing.md`, not here.

Use a unique value per run for the create-then-read pair (a timestamp
in the name) so a stale row from a previous run cannot make the
read-back pass.

## Without Python: the curl equivalent

The script is a convenience, not a dependency. Each check is one `curl`
call; the status code and a substring are what you compare.

```
BASE=http://127.0.0.1:8000
curl -s -o body.txt -w '%{http_code}\n' "$BASE/health" ; grep -c healthy body.txt
curl -s -o body.txt -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' -d '{"name":"widget"}' "$BASE/api/items/" ; grep -c '"id"' body.txt
curl -s -o body.txt -w '%{http_code}\n' "$BASE/api/items/" ; grep -c widget body.txt
curl -s -o /dev/null -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' -d '{}' "$BASE/api/items/"   # expect 422
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/items/does-not-exist"                                        # expect 404
```

PowerShell: `(Invoke-WebRequest -Uri "$BASE/health" -SkipHttpErrorCheck).StatusCode`
and `.Content -match 'healthy'`. Report the result the same way the
script prints it: one line per check, `PASS` or `FAIL`, expected versus
observed.

## Reading the output

```
PASS  health  status=200  12ms
PASS  create  status=201  8ms
FAIL  read back  status=200  6ms  (body does not contain 'widget-1694')
      body: []
PASS  empty body rejected  status=422  5ms
FAIL  missing id  status=500  40ms  (expected status 404, got 500)
      body: Internal Server Error

3 passed, 2 failed, 5 total against http://127.0.0.1:8000
```

The first failure is a write that did not land in the read path: check
which database each side is reading (the settings-module rule). The
second is an unhandled exception where an error envelope should be:
add the handler and the test. Both are one commit each. Exit code 2
means the URL is wrong or the server is down; fix that before reading
anything else.

## Per-stack notes

| Stack | Health path | Typical error status for bad input | Note |
| --- | --- | --- | --- |
| Python FastAPI | `/health` | 422 (validation) | routes mount with trailing slashes; check the exact path the router uses |
| Java Spring Boot | `/actuator/health` | 400 (`@Valid`) | body contains `"status":"UP"`; the database component appears only with `show-details: always` |
| Node Fastify/Express | `/health` | 400 | no trailing-slash redirect by default; pick one form |
| Go chi or net/http | `/healthz` | 400 | body `{"status":"ok"}` per the template |
| Next.js route handlers | `/api/health` | 400 | a static site component has no health path; check the backend's |

## Worked example

Contract for a bookings service (Spring Boot): create a booking, list
bookings, reject an overlapping booking with 409, reject a past date
with 400.

`smoke.json`:

```json
[
  {"name": "health", "method": "GET", "path": "/actuator/health", "status": 200, "contains": "UP"},
  {"name": "create", "method": "POST", "path": "/api/bookings", "status": 201, "body": {"room": "A", "start": "2030-01-01T10:00:00Z", "end": "2030-01-01T11:00:00Z"}, "contains": "\"id\""},
  {"name": "listed", "method": "GET", "path": "/api/bookings?room=A", "status": 200, "contains": "2030-01-01T10:00"},
  {"name": "overlap rejected", "method": "POST", "path": "/api/bookings", "status": 409, "body": {"room": "A", "start": "2030-01-01T10:30:00Z", "end": "2030-01-01T11:30:00Z"}},
  {"name": "past date rejected", "method": "POST", "path": "/api/bookings", "status": 400, "body": {"room": "A", "start": "2000-01-01T10:00:00Z", "end": "2000-01-01T11:00:00Z"}}
]
```

Run locally after the feature commit, then against the deployed URL
after `doctl apps create`. The second run's output goes into
`docs/demo-notes.md` under "verified against the live URL", with the
timestamp.

## Tool notes

Any assistant can run the script through its shell tool, or the curl
equivalent above when Python is not on the machine. A subagent briefed with
`skills/missions/briefings/validator-user-testing.md` should paste the
script's output into its report rather than describe it.
