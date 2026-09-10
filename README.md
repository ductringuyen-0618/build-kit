# build-kit

A kit of AI-agent skills, role briefs, per-stack templates and a
time-boxed playbook for taking a service from an empty folder to a
deployed, tested, documented prototype in a few hours. It works with any
assistant that reads the open [Agent Skills](https://agentskills.io/specification)
format (Claude Code, Cursor, Codex, GitHub Copilot, Windsurf) and with a
plain chat window by pasting.

The kit does not assume a language or framework. It carries six stacks
(Python/FastAPI, Java/Spring Boot, Node/TypeScript, Go, Vite/React,
Next.js), a stack picker to choose one at minute zero, and a deploy path
to DigitalOcean App Platform with a Dockerfile fallback for any host.

## Install

```
npx skills add ductringuyen-0618/build-kit
```

That installs the skills into the folder your tool reads. Flags, per-tool
paths, the manual copy fallback and the plain-chat option are in
[`docs/porting.md`](docs/porting.md).

## How an agent uses it

1. Read [`AGENTS.md`](AGENTS.md). It holds the non-negotiables, the
   build loop and the skill load order.
2. Pick a stack with [`playbook/stack-picker.md`](playbook/stack-picker.md)
   and scaffold from `templates/<stack>/`.
3. Follow [`playbook/3-hour-build.md`](playbook/3-hour-build.md) phase by
   phase, reading each skill it names in full before acting on it.

The one line to give the assistant:

```
Read AGENTS.md in this repo first, then follow playbook/3-hour-build.md for the task I'm about to describe.
```

## Skills

Every skill is `skills/<name>/SKILL.md` with `name` and `description`
frontmatter, plus optional `references/` and `briefings/`. Phases refer
to the playbook: clarify (0-15 min), core (15-90), hardening or second
feature (90-150), ship (150-180).

| Skill | Purpose | Phase |
| --- | --- | --- |
| `grill-me` | Ask the questions that matter, one at a time, until the design is shared; writes `docs/design.md` | clarify |
| `write-prd` | Turn `docs/design.md` into a short PRD at `docs/prd.md` when the work is bigger than one ticket | clarify (rarely in a timed build) |
| `write-issue` | Turn one ticket-sized piece of work into a GitHub issue, or `docs/issues/<slug>.md`, with testable acceptance criteria | clarify, second feature |
| `codebase-map` | Build a working mental map of an unfamiliar repo in ten minutes; writes `docs/CODEBASE.md` | clarify (existing repo) |
| `propose-feature` | Read the repo and propose exactly one well-argued next feature with a validation contract | second feature |
| `scaffold-service` | Stand up the chosen stack with a health endpoint, one passing test, a settings module and the template files | clarify |
| `ci-cd-github-actions` | Minimal CI in the first commit, secret scan, branch protection, main-only deploy job, reading a red run fast | clarify |
| `feature-brief` | Turn a request or issue into `docs/features/<slug>.md`: scope plus a validation contract of checkable assertions and exact commands | clarify, core |
| `feature-build` | Implement the brief on a `feature/<slug>` branch in small conventional commits, nothing outside scope | core |
| `feature-validate` | Run the exact commands CI runs plus the brief's contract; first line `PASS` or `FAIL` with real output | core, hardening |
| `feature-review` | Product-quality review of the validated branch against its brief; `PASS` or `FAIL` with file-level reasons | hardening |
| `e2e-verify` | Boot the app, run a minimal end-to-end smoke suite (Playwright or manual click-through), report with commands and output | core, hardening |
| `smoke-verify` | Hit the running service over HTTP for health, the main write, the main read and one error path | core, ship |
| `ship-gate` | The final checklist before calling a build shipped: CI green, README works, public URL answers, secrets clean | ship |
| `deploy-digitalocean-app-platform` | `.do/app.yaml`, `doctl` create and logs, managed database binding, live URL, registry fallback, cleanup | ship |
| `walkthrough-prep` | Turn the session's notes into the walkthrough: decisions, trade-offs, what the AI got wrong, what is next | ship |
| `timebox` | Hold the clock: phase budgets, the cut table, when to stop adding and ship | every phase |
| `missions` | Orchestrator, worker and independent validator pattern for multi-hour, multi-milestone runs; briefings included | reference (too heavy for a timed build) |

Skills that were removed because they needed a specific runtime or tool
are listed in [`docs/removed-skills.md`](docs/removed-skills.md).
Third-party skills worth installing next to these are in
[`docs/third-party-skills.md`](docs/third-party-skills.md).

## Role briefs

`agents/` holds plain-Markdown briefs for splitting a build across
several agents. Each brief is a single responsibility with a fixed
report format; [`agents/README.md`](agents/README.md) explains the
pattern and how to hand a brief to an agent in each tool.

| Role | File | One line |
| --- | --- | --- |
| Coordinator | `agents/coordinator.md` | Keeps the plan, assigns roles in order, counts attempts, stops at three |
| Builder | `agents/builder.md` | Implements one validation contract on a branch in small commits |
| Scrutiny validator | `agents/scrutiny-validator.md` | Runs exactly what CI runs on the diff, reports `PASS` or `FAIL` with output |
| User tester | `agents/user-tester.md` | Uses the running product like a user, black-box, pass or fail with reasons |
| Product reviewer | `agents/product-reviewer.md` | Judges finish quality: states, copy, consistency, accessibility |

## Templates

| Path | What it is |
| --- | --- |
| `templates/ci.yml` | GitHub Actions workflow: one job per component plus a secret scan |
| `templates/ci-monorepo.yml` | The same for a pnpm workspaces monorepo |
| `templates/deploy-do.yml` | Main-only deploy to App Platform, or a container image push |
| `templates/do-app.yaml` | Worked App Platform spec: service, static site, dev Postgres, migration job, ingress |
| `templates/<stack>/` | `Dockerfile`, `ci-job.yml`, `.env.example`, `app-component.yaml` and a README with scaffold, run, test and lint commands |

Stacks: `python-fastapi`, `java-spring-boot`, `node-typescript`, `go`
(backend); `vite-react`, `nextjs` (frontend). Lines marked `# CHANGE:`
are the ones a new repo must edit.

## Layout

```
AGENTS.md                 entry point for any assistant
CLAUDE.md                 "read AGENTS.md" plus Claude Code notes
.cursor/rules/            always-on Cursor rule pointing at AGENTS.md
.github/                  copilot-instructions.md
playbook/                 3-hour-build.md, stack-picker.md
skills/<name>/            SKILL.md plus references/, briefings/
agents/                   role briefs (coordinator, builder, validators, reviewer)
templates/                ci.yml, ci-monorepo.yml, deploy-do.yml, do-app.yaml, <stack>/
docs/                     porting.md, interview-format.md, third-party-skills.md, removed-skills.md
```

## Provenance

The skills, briefs and conventions were extracted from the author's
production projects and generalised so they read without that context.
The two public sources are
[agent-os](https://github.com/ductringuyen-0618/agent-os), an always-on
agent runtime, and
[ai-tech-news-assistant](https://github.com/ductringuyen-0618/ai-tech-news-assistant),
a full-stack AI service. The timed-session framing comes from
DigitalOcean's AI-native build interview; `playbook/3-hour-build.md` and
`docs/interview-format.md` cover it.

## License

MIT. See `LICENSE`.
