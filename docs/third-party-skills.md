# Third-party skills worth installing

None of these ship in this repo. Install the ones the session allows;
each takes under a minute. All install with the same CLI as the kit
(`npx skills add <owner/repo>`, see `docs/porting.md`); the plugin
commands are for when you are already inside that tool.

| Skills | Why | Install |
| --- | --- | --- |
| [DigitalOcean App Platform skills](https://github.com/digitalocean-labs/do-app-platform-skills) | App spec design, deployment, networking, managed Postgres, troubleshooting, written by DigitalOcean. Use next to `deploy-digitalocean-app-platform`. | `npx skills add digitalocean-labs/do-app-platform-skills` (the README also documents `git clone` plus a symlink into `~/.claude/skills`, `~/.cursor/skills` or `~/.codex/skills`) |
| [superpowers](https://github.com/obra/superpowers) | brainstorming, test-driven-development, systematic-debugging, verification-before-completion, writing-plans, git worktrees. The playbook leans on TDD and verification-before-completion. | `npx skills add obra/superpowers`, or in Claude Code `/plugin install superpowers@claude-plugins-official`, in Cursor `/add-plugin superpowers` |
| [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | Anthropic's guidance for UI that does not look generated. Use when the prompt has a visible frontend. | `npx skills add anthropics/skills -s frontend-design`, or in Claude Code `/plugin install frontend-design@claude-plugins-official` |
| [webapp-testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) | Browser-driven checks with Playwright; complements `e2e-verify`. | `npx skills add anthropics/skills -s webapp-testing` |

Also useful, if the tool has it: a Playwright MCP server for screenshots
(`e2e-verify` can use one) and a docs MCP such as
Context7 for current framework APIs. Both are plugins in Claude Code's
`claude-plugins-official` marketplace.
