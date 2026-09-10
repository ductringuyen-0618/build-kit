---
name: walkthrough-prep
description: Keep docs/DECISIONS.md as you build (decision, alternatives, why, verified versus trusted) and turn it into the walkthrough script with scaling answers grounded in DigitalOcean primitives in the last ten minutes.
---

# Walkthrough prep: the decisions file and the script

DigitalOcean's write-up of the build session says candidates "walked
interviewers through what they'd built: design choices, trade-offs, and
what they'd do differently with more time", then took "hypotheticals
about scaling, business constraints, what it would look like if traffic
spiked". The walkthrough is half the interview. It cannot be written at
minute 170 from memory; it is written at minute 4, 14, 29 and 106 as the
decisions happen, then read aloud.

## Part 1: `docs/DECISIONS.md`, kept as you go

Created at minute 0 (the `scaffold-service` skill does it). One entry per decision, appended when
the decision is made. Five lines each. Under time pressure the
"verified versus trusted" line is the one that must not be skipped.

```
## <minute> <decision in one line>
- alternatives: <what else was on the table>
- why: <one sentence>
- verified: <what you ran, opened or read to check it>
- trusted: <what you accepted from the assistant or the template without checking, and why that was acceptable>
```

Plus one running section at the bottom:

```
## What the AI got wrong
- <minute> <what it produced> | <how it was caught: test, log, browser, diff> | <fix>
```

Worked entries from a bookings service:

```
## 0 Stack: python-fastapi
- alternatives: spring-boot (CRUD-with-rules is its strength), go
- why: the prompt mentions summarising notes; the provider fake and settings pattern carry over from a previous project
- verified: scaffold test passed in 0.3s; health answered locally
- trusted: the Dockerfile template's non-root user and healthcheck lines; checked once by CI's build, not by a local docker build (Docker not on this machine)

## 22 Overlap rule in the service layer, not a database constraint
- alternatives: an exclusion constraint on a tstzrange column in Postgres
- why: SQLite locally has no range types; the rule must work in both; the service check is 12 lines and has a test
- verified: test_overlap_rejected, and curl POST returned 409 with the error envelope
- trusted: nothing; this is the hand-written part

## 106 Container must bind 0.0.0.0
- alternatives: none; this was a fix
- why: App Platform's health check hit the container from outside and uvicorn was on 127.0.0.1
- verified: deploy log line "health check timeout", then curl on the live URL returned 200 after the fix
- trusted: nothing

## What the AI got wrong
- 106 generated CMD bound uvicorn to 127.0.0.1 | caught in doctl apps logs --type deploy | one-line fix, commit 9c1d2e
- 58 generated test asserted 400 for a past date; the route returned 422 | caught by running the test, not by reading it | aligned the route to 422 and said so in the README
```

Decisions worth an entry: the stack; the data model (and what was left
out); where the domain rule lives; SQLite versus Postgres and how the
settings module hides it; buildpack versus Dockerfile; what was
scaffolded versus hand-written; every cut at a clock checkpoint; every
deploy fix.

## Part 2: the script, minute 170 to 180

Six headings, written into the demo notes (`docs/demo-notes.md`) under
"Walkthrough". Read from it; do not improvise the order.

### 1. Architecture in two minutes

One paragraph, in this order: what the service does for whom; the
request path (browser or client, App Platform ingress, the service, the
database); the one domain rule and where it lives; what the health
check covers; where configuration comes from. Then point at the live
URL and run the smoke checks against it while talking.

### 2. Three trade-offs

Pick three entries from `DECISIONS.md` with real alternatives. For each:
what was chosen, what was given up, when the other choice would win.
Good candidates: rule in code versus constraint in the database;
SQLite locally versus Postgres everywhere; `create_all` at startup
versus migrations; buildpack versus Dockerfile; one service versus
service plus static site.

### 3. What was scaffolded, what was hand-written, what was verified

Three lists, from the decisions file's verified/trusted lines. Then
read the "What the AI got wrong" section aloud, every line. This is the
part the panel is listening for; a candidate with nothing on that list
either did not look or did not use the tool.

### 4. What changes at 10x traffic, and at a spike

Ground every answer in a primitive that exists and a number from the
docs (`references/digitalocean-scaling.md`). Name the bottleneck first,
then the first fix, then the second.

| Symptom | Bottleneck | First fix | Second fix |
| --- | --- | --- | --- |
| p95 climbs, CPU flat | one instance handling all requests serially, or a single worker process | raise `instance_count` on the service (1 to 250 per component); on the smallest shared plan raise workers in the run command first | request-based autoscaling: `autoscaling.min_instance_count` / `max_instance_count` with `requests_per_second.per_instance` or `request_duration.p95_milliseconds` (works on shared CPU plans; CPU-percent autoscaling needs a dedicated plan) |
| database CPU high, reads dominate | every request hits the primary | a cache in front of the hot read: Managed Valkey (Redis-compatible) with a TTL, or an in-process cache for one instance | a read-only node on the Managed Postgres cluster and a read-routed session for list endpoints (read-only nodes must be the primary's size or larger; a cluster is at most three nodes) |
| "too many connections" errors when instances scale out | each instance opens its own pool; a 1 GiB Postgres plan allows 22 backend connections | a PgBouncer connection pool on the cluster (transaction mode, size about half the plan's connections) and point `DATABASE_URL` at the pool | move up a plan size (2 GiB allows 47, 4 GiB allows 97) and keep the pool |
| writes spike (imports, bulk creates) | synchronous work inside the request | a worker component in the same app spec reading a queue (Valkey list or a jobs table) with the request returning 202 | rate limits at the service: a per-client token bucket in the middleware, 429 with `Retry-After`; the ingress does not rate-limit for you |
| static assets and uploads slow or expensive | the service serving files | Spaces bucket with the built-in CDN for uploads and assets; the service returns URLs | the frontend as a `static_sites` component, already CDN-backed, so the service only serves the API |
| one instance restarts and users see errors | a single container is not highly available | `instance_count: 2` (App Platform notes apps need two or more containers for failover) | health check tuned so a slow start is not a failed deploy (`initial_delay_seconds`), and `RESTART_COUNT` alert |
| traffic from another continent | latency to one region | Spaces CDN for assets; a read-only Postgres node in that region for reads | a second App Platform region behind a Global Load Balancer if the product needs it; say plainly that this is beyond a prototype |

State the limits you are working inside: 250 instances per component,
100 for request-based autoscaling, 4 GiB local disk per container (so
nothing is written to local disk that must survive), 22 to 997 Postgres
connections depending on plan, PgBouncer at up to 1,000 client
connections per cluster. Numbers are in the references file with URLs;
quote them as "the docs say", not as certainties about a live account.

A Droplet-based alternative (containers on Droplets behind a Regional
Load Balancer with health checks and SSL termination) is worth one
sentence: it trades App Platform's managed build and autoscale for
control over the host. Do not present it as the plan.

### 5. What was not verified, and how it would be

From the "trusted" lines. Typical: the Dockerfile's healthcheck (verify
with `docker run` and `docker inspect`), Postgres type behaviour under
the ORM (run the test suite against a local Postgres container),
behaviour under concurrency (a `hey` or `wrk` run against the live URL
with 50 connections), the migration path (a second migration on a
non-empty database). Name the command for each. "I would test it" is
not an answer; "I would run `hey -z 30s -c 50 <url>/api/items/` and
watch p95 and the run log" is.

### 6. With more time

Three items, ordered by user impact, from the cut lines in the timelog.
Each one sentence.

## Timing

| Minute | Do |
| --- | --- |
| 170 | Copy the six headings into the demo notes. Fill 1 and 4 from this file and the references. |
| 173 | Fill 2, 3 and 5 from `DECISIONS.md`. Read "What the AI got wrong" once aloud. |
| 176 | Fill 6 from the timelog's cut lines. Commit `docs: walkthrough notes`. |
| 178 | Open three tabs: the live URL, the PR or CI run, the repo's README. Run the smoke checks against the live URL once more and leave the output on screen. |

## Per-stack notes for section 4

| Stack | First scaling knob inside the process | Note |
| --- | --- | --- |
| Python FastAPI | `uvicorn --workers N` on a bigger instance, then `instance_count` | async handlers do not help a CPU-bound summariser; a worker component does |
| Java Spring Boot | Tomcat thread pool and HikariCP pool size (keep pool size under the Postgres plan's limit divided by instance count) | JVM memory: `-Xmx` must fit the instance size slug |
| Node Fastify/Express | `instance_count` first; a single event loop per container | never block the loop with the domain rule; offload to a worker |
| Go | `instance_count`; goroutines already use the CPU | `pgxpool` max connections per instance times instances under the plan limit |
| Next.js | `instance_count` for the web service; route handlers scale the same way | static export plus a separate API scales further than SSR for a read-mostly site |

## Tool notes

Any assistant can draft section 4 from `references/digitalocean-scaling.md`;
ask it to cite the URL beside each number so you can check the claim in
the browser tab before saying it. Do not let the assistant invent
limits; if a number is not in the references file, say "I would check
the limits page" and move on.
