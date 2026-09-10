# Third-party skills and plugins

These are not in this repo because they are not Tri Nguyen's work. They
are listed so an assistant can install the ones that are allowed on the
interview machine. Versions are what was installed on 2026-09-09.

## Most relevant to a DigitalOcean build session

| Skill set | Source | Install | What it does |
| --- | --- | --- | --- |
| DigitalOcean App Platform skills | github.com/digitalocean-labs/do-app-platform-skills | `git clone https://github.com/digitalocean-labs/do-app-platform-skills.git` then symlink it: `ln -s "$PWD/do-app-platform-skills" ~/.claude/skills/do-app-platform-skills` (or `~/.cursor/skills/`, `~/.codex/skills/`) | Twelve skills for app-spec generation, managed Postgres defaults, VPC, GitHub Actions deploys, secrets via bindable variables, Heroku migration, troubleshooting. Published by DigitalOcean 2026-03-16. Not installed locally yet; install it first. |

## Claude Code plugins (marketplace `claude-plugins-official`, github.com/anthropics/claude-plugins-official)

Install from inside Claude Code with `/plugin install <name>@claude-plugins-official`.

| Plugin | Version | Note |
| --- | --- | --- |
| superpowers | 6.3.0 | Core workflow skills: brainstorming, test-driven-development, systematic-debugging, writing-plans, executing-plans, verification-before-completion, requesting and receiving code review, git worktrees. The build playbook leans on `test-driven-development` and `verification-before-completion`. |
| feature-dev | 3ea32df27be7 | Guided feature development with code-explorer, code-architect and code-reviewer agents. |
| code-review | 3ea32df27be7 | Multi-agent PR review with confidence scoring. |
| code-simplifier | 1.0.0 | Agent that simplifies recently changed code without changing behaviour. |
| security-guidance | 2.0.8 | Pattern warnings on edits plus an LLM diff review for injection, XSS, SSRF, hardcoded secrets. Worth having on during the session. |
| commit-commands | 3ea32df27be7 | `/commit`, `/commit-push-pr`, `/clean_gone`. |
| skill-creator | 3ea32df27be7 | Create and evaluate skills. |
| frontend-design | 3ea32df27be7 | Anthropic's frontend design guidance (distinct from the designer-skills pack below). |
| playwright | 3ea32df27be7 | Microsoft Playwright MCP server for browser automation and screenshots. Used by `verify-feature` and `verify-techpulse`. |
| context7 | 3ea32df27be7 | Upstash Context7 MCP for current library docs. Useful for FastAPI, SQLAlchemy and Vite version questions. |
| github | 3ea32df27be7 | Official GitHub MCP server. |
| claude-code-setup | 1.0.0 | Recommends hooks, skills and MCP servers for a codebase. |
| claude-md-management | 1.0.0 | Audit and update CLAUDE.md files. |
| remember | 0.29.1 | Continuous memory across sessions. |
| ralph-loop | 1.0.0 | Run one prompt in a loop until done. |
| vercel | 0.48.0 | Vercel deploy, env and platform skills. Not needed for a DigitalOcean target. |
| telegram | 0.0.7 | Telegram messaging bridge. Not needed in an interview. |
| huggingface-skills | 1.0.18 | Hugging Face Hub, Spaces, training. Not needed in an interview. |

## Skill packs installed with the `skills` CLI

| Pack | Source | Install | Note |
| --- | --- | --- | --- |
| designer-skills | github.com/julianoczkowski/designer-skills | `npx skills add julianoczkowski/designer-skills` | brief-to-tasks, design-brief, design-flow, design-review, design-tokens, frontend-design, information-architecture, and a short grill-me. Installed into TechPulse under `.agents/skills/`. Its `grill-me` overwrote Tri's original; this kit ships the original. |
| Clerk skills | Clerk's official agent skills | `npx skills add` from Clerk's skills repository (see clerk.com/docs for the current path) | clerk-setup, clerk-cli, clerk-backend-api, clerk-custom-ui, clerk-nextjs-patterns, clerk-orgs, clerk-testing, clerk-webhooks. Only relevant if the prompt needs hosted auth. |

## Other tools

| Tool | Source | Install | Note |
| --- | --- | --- | --- |
| graphify | github.com/safishamsi/graphify (package `graphifyy`) | `uv tool install graphifyy`, then follow the repo README to register the `/graphify` skill | Turns a codebase into a knowledge graph with community detection. Tri's own `graphify-new-project` skill in this kit is a thin wrapper around it. |
| pstack | github.com/cursor/plugins (pstack, by Lauren Tan, MIT) | Installed locally as a Claude Code port from a local marketplace; upstream is a Cursor plugin | poteto-mode router, 21 principle skills, parallel subagent panels. Not needed in an interview. |
