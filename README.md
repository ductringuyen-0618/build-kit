# build-kit

Skills, agent definitions, per-stack templates and a time-boxed playbook
that Tri Nguyen uses to ship small production services fast. The skills
were written for and used on real projects (an AI news aggregator, an
always-on agent daemon, a booking platform, a portfolio site). This repo
packs them into one place so that, at the start of a timed build session
such as DigitalOcean's three-hour build interview, any AI coding assistant
can be pointed at it and work the way Tri works: pick a stack, plan by
asking, build with tests, verify before claiming done, deploy to a public
URL, leave a README and demo notes behind.

## The one line to give the assistant

```
Read AGENTS.md in this repo first, then follow playbook/3-hour-build.md for the task I'm about to describe.
```

`AGENTS.md` is the cross-tool entry point. `CLAUDE.md`,
`.cursor/rules/build-kit.mdc` and `.github/copilot-instructions.md` all
point at it. `docs/porting.md` explains how to load a skill in Claude
Code, Cursor, Codex, Copilot, Windsurf or a plain chat, and
`scripts/port.sh` / `scripts/port.ps1` copy skills into a target repo in
the layout Claude Code or Cursor expects.

## Stacks

The kit is framework-agnostic. `playbook/stack-picker.md` chooses one at
minute zero; `templates/<stack>/` has a Dockerfile, a CI job snippet, a
`.env.example` and an App Platform component for each of
`python-fastapi`, `java-spring-boot`, `node-typescript`, `go`,
`vite-react` and `nextjs`. The deploy and CI/CD skills carry per-stack
tables for build, run, health, port and test commands.

## Skills

Phases refer to the playbook: clarify (0-15 min), core (15-90), second
feature or hardening (90-150), ship (150-180). "Stack" says whether a
skill is generic or tied to one project's stack.

| Skill | Purpose | Phase | Stack | Source |
| --- | --- | --- | --- | --- |
| `grill-me` | Interrogate the task until the design is shared, then write `docs/designs/<slug>.md` | clarify | any | TechPulse |
| `write-issue` | Turn one scoped piece of work into a ticket with testable acceptance criteria | clarify, second feature | any | TechPulse |
| `write-prd` | PRD from a grill-me design context, for work bigger than one ticket | clarify (rarely in 3 hours) | any | TechPulse |
| `ci-cd-github-actions` | Minimal CI in the first commit, secret scan, branch protection, main-only deploy job, reading red runs | clarify | any (per-stack table) | new, distilled from four repos |
| `deploy-digitalocean-app-platform` | `.do/app.yaml`, doctl create and logs, database binding, live URL, fallback, cleanup | ship | any (per-stack table) | new, research-backed |
| `test-app-e2e` | Black-box HTTP smoke battery (stdlib runner) that dispatches a fixer agent per failure | core, hardening | pattern is generic; runner names TechPulse routes (Python FastAPI) | TechPulse |
| `verify-feature` | Two gates: full lint/type/test loop, then an exhaustive Playwright click sweep | hardening | pattern is generic; commands are TechPulse (FastAPI + Vite) | TechPulse |
| `verify-techpulse` | Launch, run a read-only doctor, drive one user path, leave evidence outside the repo | ship (demo proof) | TechPulse-specific (FastAPI + Vite); use as the pattern | TechPulse |
| `missions` | Orchestrator, worker and adversarial validator pattern; `briefings/` (runner, worker, scrutiny validator, user-testing validator) and `references/` are usable on their own in a timed build | core, hardening (briefings); full pattern is reference | any | TechPulse; briefings written from agent-os runs |
| `scaffold-service` | Minute 0-15: skeleton, settings module, health check that touches the database, one real test, README, `.env.example`, Dockerfile, CI job, `.do/app.yaml`, first commit, CI green | clarify | any (per-stack table) | new |
| `smoke-verify` | `scripts/smoke.py`, a stdlib HTTP checker: base URL plus a JSON or inline list of GET/POST checks, PASS/FAIL per check, exit code; run locally after every feature and against the deployed URL before the demo | core, hardening, ship | any (per-stack table) | new; replaces `test-app-e2e`/`verify-feature` under a clock |
| `ship-gate` | Scrub, push, PR, wait for CI, read the failing log, one fix attempt, then the shipped report; zero checks is not green | ship | any | new, lifted from agent-os's CI gate and the COO routine |
| `walkthrough-prep` | `docs/DECISIONS.md` as you go, then the six-part walkthrough script; scaling answers grounded in App Platform, Managed Postgres, Valkey, Spaces and Load Balancer docs (URLs in `references/`) | ship, walkthrough | any (per-stack notes) | new, doc-checked |
| `timebox` | `docs/TIMELOG.md`, commit every fifteen minutes, cut rules at 45/85/90/120/140/150/160/170, the verify-before-trust list | every phase | any | new, from the playbook and the interview write-up |
| `graphify-new-project` | Code-only knowledge graph of a fresh repo, no LLM tokens | clarify (optional) | any (needs graphify installed) | user-level |
| `feature-brief` | Plain-words request to proposal with a validation contract | clarify | any | agent-os |
| `feature-build` | Implement on a `req/<slug>` branch, small conventional commits, never push | core | any | agent-os |
| `feature-validate` | Run every check command for real, first line `PASS` or `FAIL` | core, hardening | any | agent-os |
| `feature-review` | Read-only review against the proposal, `PASS` or `FAIL` with named fixes | hardening | any | agent-os |
| `coo-ideate` | Propose one well-argued feature a day from reading the repo | second feature (pick the next thing) | any | agent-os |
| `heartbeat`, `ingest`, `lint`, `query`, `daily-digest` | agent-os runtime routines (wiki memory, health pulse, digest) | reference only; need the agent-os daemon | n/a | agent-os |

Notes on fidelity:

- `missions`'s `references/`, `briefings/` and `examples/` were never
  committed to the source repo; they were written for this kit from the
  agent-os feature-request workflow and the COO routine that shipped real
  features. `docs/how-tri-builds.md` is the evidence trail;
  `skills/missions/README.md` says how to use them.
- The agent-os skills call `mcp__agentos__*` tools that only exist inside
  the agent-os daemon. Each carries a portability note mapping those calls
  to plain file reads and writes. Their value here is the contract shape:
  payload in, `PASS`/`FAIL` first line out, hard rules at the bottom.
- The new skills (`ci-cd-github-actions`,
  `deploy-digitalocean-app-platform`, `walkthrough-prep`) cite the docs
  they were checked against in their `references/` folder and mark the
  few fields that were not verified. `smoke-verify`'s script was run
  against a local test server for the pass, fail, unreachable and
  JSON-report paths.

## Agents

`agents/` holds four agent definitions with a note on how each is meant to
be used: `coo` (proposes), `librarian` (owns the wiki), `ops` (validates,
builds, reviews), and `blackbox-qa-validator` (tests a running app from
the outside against a behaviour spec). See `agents/README.md`.

## Templates

- `templates/ci.yml`: backend plus frontend jobs, secret scan.
- `templates/ci-monorepo.yml`: pnpm workspaces variant.
- `templates/deploy-do.yml`: main-only deploy to App Platform, or a GHCR image push.
- `templates/do-app.yaml`: worked App Platform spec (service, static site, dev Postgres, migration job, ingress).
- `templates/<stack>/`: `Dockerfile`, `ci-job.yml`, `.env.example`, `app-component.yaml`, and a short `README.md` for the backend and frontend stacks.

## Tools verified

- Claude Code: the kit's own layout (`skills/<name>/SKILL.md` with a
  `description:` frontmatter, `agents/<name>/AGENT.md`) is the one Claude
  Code reads once copied into `.claude/`. `scripts/port.sh all claude` and
  `scripts/port.ps1 all claude` were run once on a temporary directory and
  the resulting `.claude/skills/<name>/` tree was checked.
- Cursor: `scripts/port.sh all cursor` and `port.ps1 all cursor` were run
  once on a temporary directory; the `.cursor/rules/<name>.mdc` files were
  checked for frontmatter and body, and `references/` and `scripts/`
  folders were copied next to them.
- Codex, Copilot, Windsurf: only the file layout (`AGENTS.md`,
  `.github/copilot-instructions.md`) was prepared. Runtime behaviour
  inside those tools was not exercised.

## Proof of work

Public repos where these skills were used:

- agent-os, an always-on daemon that runs teams of Claude Code agents over
  a filesystem memory layer with human approval gates:
  https://github.com/ductringuyen-0618/agent-os
- TechPulse, an AI tech news aggregator (FastAPI, RAG, agentic research,
  knowledge graph; React frontend):
  https://github.com/ductringuyen-0618/ai-tech-news-assistant
- salon-hub, a salon booking platform (Spring Boot API, React UI, monorepo):
  https://github.com/ductringuyen-0618/salon-hub
- portfolio-website, a React 19 portfolio with a client-side WebLLM
  assistant: https://github.com/ductringuyen-0618/portfolio-website

## Layout

```
AGENTS.md                 entry point for any assistant
CLAUDE.md                 "read AGENTS.md" plus Claude Code notes
.cursor/rules/            always-on Cursor rule pointing at AGENTS.md
.github/                  copilot-instructions.md
playbook/                 3-hour-build.md, stack-picker.md
skills/<name>/            SKILL.md plus references/, scripts/, examples/, features/
agents/<name>/            AGENT.md
templates/                ci.yml, ci-monorepo.yml, deploy-do.yml, do-app.yaml, <stack>/
scripts/                  port.sh, port.ps1
docs/                     interview-format.md, how-tri-builds.md, third-party-skills.md, porting.md
```

## License

MIT. See `LICENSE`.
