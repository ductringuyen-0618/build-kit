# build-kit

Claude Code skills, agent definitions and a time-boxed playbook that Tri
Nguyen uses to ship small production services fast. The skills were
written for and used on real projects (an AI news aggregator, an
always-on agent daemon, a booking platform, a portfolio site). This repo
packs them into one place so that, at the start of a timed build session
such as DigitalOcean's three-hour build interview, an AI coding assistant
can be pointed at it and work the way Tri works: plan by asking, build
with tests, verify before claiming done, deploy to a public URL, leave a
README and demo notes behind.

## The one line to give the assistant

```
Read AGENTS.md in this repo first, then follow playbook/3-hour-build.md for the task I'm about to describe.
```

If the session repo is separate from this one, clone this kit next to it
or into `.claude/` and point the assistant at `AGENTS.md`.

## Skills

Phases refer to the playbook: clarify (0-15 min), core (15-90), second
feature or hardening (90-150), ship (150-180).

| Skill | Purpose | Phase | Source |
| --- | --- | --- | --- |
| `grill-me` | Interrogate the task until the design is shared, then write `docs/designs/<slug>.md` | clarify | TechPulse |
| `write-issue` | Turn one scoped piece of work into a ticket with testable acceptance criteria | clarify, second feature | TechPulse |
| `write-prd` | PRD from a grill-me design context, for work bigger than one ticket | clarify (rarely in 3 hours) | TechPulse |
| `test-app-e2e` | Black-box HTTP smoke battery (stdlib runner) that dispatches a fixer agent per failure | core, hardening | TechPulse |
| `verify-feature` | Two gates: full lint/type/test loop, then an exhaustive Playwright click sweep | hardening | TechPulse |
| `verify-techpulse` | Launch, run a read-only doctor, drive one user path, leave evidence outside the repo | ship (demo proof) | TechPulse |
| `missions` | Orchestrator, worker and adversarial validator pattern for multi-hour runs | reference only; too heavy for 3 hours | TechPulse |
| `graphify-new-project` | Code-only knowledge graph of a fresh repo, no LLM tokens | clarify (optional) | user-level |
| `feature-brief` | Plain-words request to proposal with a validation contract | clarify | agent-os |
| `feature-build` | Implement on a `req/<slug>` branch, small conventional commits, never push | core | agent-os |
| `feature-validate` | Run every check command for real, first line `PASS` or `FAIL` | core, hardening | agent-os |
| `feature-review` | Read-only review against the proposal, `PASS` or `FAIL` with named fixes | hardening | agent-os |
| `coo-ideate` | Propose one well-argued feature a day from reading the repo | second feature (pick the next thing) | agent-os |
| `heartbeat`, `ingest`, `lint`, `query`, `daily-digest` | agent-os runtime routines (wiki memory, health pulse, digest) | reference only; need the agent-os daemon | agent-os |

Notes on fidelity:

- `test-app-e2e`, `verify-feature` and `verify-techpulse` were written for
  the TechPulse repo and name its routes and ports. Use them as the
  pattern (runner script, fix-area cheat sheet, doctor, feature map) and
  swap the endpoints.
- `missions` refers to `references/` and `briefings/` folders that were
  never committed to the source repo. The SKILL.md is complete on its own;
  the briefing templates have to be written before the skill is run.
- The agent-os skills call `mcp__agentos__*` tools that only exist inside
  the agent-os daemon. Their value here is the contract shape: payload in,
  `PASS`/`FAIL` first line out, hard rules at the bottom.

## Agents

`agents/` holds four agent definitions with a note on how each is meant to
be used: `coo` (proposes), `librarian` (owns the wiki), `ops` (validates,
builds, reviews), and `blackbox-qa-validator` (tests a running app from
the outside against a behaviour spec). See `agents/README.md`.

## Templates

`templates/` has the starter files a timed build always needs: a FastAPI
plus SQLAlchemy plus pytest backend layout, a Vite plus React frontend
layout, a GitHub Actions `ci.yml`, a `.env.example` pattern, a backend
`Dockerfile`, and a DigitalOcean App Platform spec at `.do/app.yaml`.

## Proof of work

Public repos where these skills were used:

- agent-os, an always-on daemon that runs teams of Claude Code agents over
  a filesystem memory layer with human approval gates:
  https://github.com/ductringuyen-0618/agent-os
- TechPulse, an AI tech news aggregator (FastAPI, RAG, agentic research,
  knowledge graph; React frontend):
  https://github.com/ductringuyen-0618/ai-tech-news-assistant
- salon-hub, a salon booking platform (API, UI and monorepo):
  https://github.com/ductringuyen-0618/salon-hub
- portfolio-website, a React 19 portfolio with a client-side WebLLM
  assistant: https://github.com/ductringuyen-0618/portfolio-website

## Layout

```
AGENTS.md            entry point for any assistant (CLAUDE.md is a copy)
playbook/            3-hour-build.md
skills/<name>/       SKILL.md plus references/, scripts/, examples/ where they exist
agents/<name>/       AGENT.md
templates/           backend, frontend, ci.yml, .env.example, Dockerfile, .do/app.yaml
docs/                interview-format.md, third-party-skills.md
```

## License

MIT. See `LICENSE`.
