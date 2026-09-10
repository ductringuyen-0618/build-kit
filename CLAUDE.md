# CLAUDE.md

Read `AGENTS.md` first. It is the entry point for every assistant and
carries the non-negotiables, the load order and the conventions.

Claude Code specifics:

- To make the skills invocable by name, copy them into `.claude/skills/`
  of the session repo (or `~/.claude/skills/` for every repo):
  `sh scripts/port.sh all claude <target-repo>` or
  `powershell -File scripts/port.ps1 all claude <target-repo>`.
- Subagent personas in `agents/` can be dropped into `.claude/agents/`.
- Where a skill names `AskUserQuestion`, use it when the harness offers it;
  otherwise ask in chat. Where a skill names `mcp__agentos__*` tools, those
  only exist inside the agent-os daemon; do the equivalent file read or
  write instead.
- Load `superpowers:test-driven-development` and
  `superpowers:verification-before-completion` if the plugin is installed.
  They match how Tri works.
