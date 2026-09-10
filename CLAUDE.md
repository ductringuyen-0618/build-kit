# CLAUDE.md

Read `AGENTS.md` first. It is the entry point for every assistant and
carries the non-negotiables, the loop, the skill load order and the
conventions.

Claude Code specifics:

- Install the skills into the session repo with
  `npx skills add ductringuyen-0618/build-kit`; they land under
  `.claude/skills/<name>/` and become invocable by name (`/grill-me`).
  `docs/porting.md` has the flags and the manual copy fallback.
- Role briefs in `agents/*.md` become subagent types when copied to
  `.claude/agents/<role>.md` with a `name` and `description` frontmatter.
  Give validators and reviewers a fresh agent, never a fork, so they do
  not inherit the builder's context.
- Where a skill says "ask the human", use `AskUserQuestion` when the
  harness offers it; otherwise ask in chat. Where a skill says "spawn a
  subagent", use the `Agent` tool with the role brief as the prompt.
- If the `superpowers` plugin is installed, load
  `superpowers:test-driven-development` before building and
  `superpowers:verification-before-completion` before claiming anything
  is done. They match the non-negotiables in `AGENTS.md`.
