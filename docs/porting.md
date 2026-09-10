# Porting the kit to a tool

Every skill is a folder with a `SKILL.md` whose frontmatter has a
`description:` line, plus optional `references/`, `scripts/`, `examples/`
or `features/`. The body is plain Markdown with no tool-specific syntax
required to follow it. Where a skill names a Claude-only tool it says so
and the intent is clear without it.

## Claude Code

Copy the folder into the session repo's `.claude/skills/` (project scope)
or `~/.claude/skills/` (every repo). The skill then triggers by its
description and can be invoked by name.

```
sh scripts/port.sh all claude <target-repo>
sh scripts/port.sh grill-me claude <target-repo>
powershell -File scripts/port.ps1 all claude <target-repo>
```

`CLAUDE.md` in the target repo should say "Read AGENTS.md". Agent personas
go in `.claude/agents/<name>.md` (rename `AGENT.md` on copy).

## Cursor

Two options.

1. Reference the file directly in chat: `@skills/grill-me/SKILL.md`.
2. Turn it into a rule: `sh scripts/port.sh grill-me cursor <target-repo>`
   writes `.cursor/rules/grill-me.mdc` with an `.mdc` frontmatter
   (`description`, `globs`, `alwaysApply: false`) and the SKILL.md body,
   and copies the skill's `references/` and `scripts/` next to it. Cursor
   attaches a rule with `alwaysApply: false` when its description matches
   the request, or when you mention it with `@`.

`.cursor/rules/build-kit.mdc` in this repo is the always-on entry rule; copy
it too if the kit lives outside the session repo.

## Codex, Copilot, Windsurf

These read `AGENTS.md` at the repo root (Copilot also reads
`.github/copilot-instructions.md`). Keep the kit inside or next to the
session repo and let `AGENTS.md` link to the skills. When a phase needs a
skill, attach `skills/<name>/SKILL.md` to the chat as context, or paste
its body.

## Plain chat

Paste `AGENTS.md`, then the `SKILL.md` for the current phase. Skills with
`scripts/` (test-app-e2e, verify-techpulse, graphify-new-project) need the
script run locally; paste the script's output back.

## What was verified

The port scripts were run once on a temporary directory for `all claude`
and `all cursor` and the resulting file layout was checked. Runtime
behaviour inside Cursor, Codex, Copilot and Windsurf was not exercised.
