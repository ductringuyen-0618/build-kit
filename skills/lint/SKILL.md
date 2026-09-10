---
description: Nightly wiki hygiene: contradictions, stale claims, orphan pages, missing sources.
---

> **Portability.** This skill was written for the agent-os daemon, where
> `mcp__agentos__*` are the kernel's syscalls. Outside agent-os, read each
> call as its intent: `get_context` = read the project's index or README;
> `read_wiki(page)` = read that Markdown page; `remember(page, content)` =
> write or append that Markdown page under `docs/` or `wiki/`;
> `request_approval` / `propose_feature` = write the proposal file and ask
> the human in chat; `emit_event` / `schedule` = note it for the human. The
> payload shape, the steps and the hard rules are the part to keep.

# Skill: lint

Trigger: routine `lint`, `cron: "0 3 * * *"`. Agent: `librarian`.

## Steps
1. Call `mcp__agentos__get_context`, then `mcp__agentos__read_wiki('index.md')`.
2. Call `mcp__agentos__read_wiki` for each listed page.
3. Identify contradictions between pages, stale claims (frontmatter
   `updated` far in the past for a topic that likely changed), orphan pages
   (not linked from any other page or the index), and pages missing
   `sources`.
4. Fix what's fixable via `mcp__agentos__remember` with `op: 'lint'`.
5. Call `mcp__agentos__remember` once more with `page: 'lint-report.md'`,
   `op: 'lint'`, summarizing what was found and fixed.

## Hard rules (see os/CLAUDE.md)
Fix via remember only, never direct file edits. Never edit raw/.
