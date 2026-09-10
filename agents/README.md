# Agents

Each folder holds one `AGENT.md`: a persona, a permission shape, and hard
rules. Three come from agent-os, where the daemon spawns them as headless
Claude Code sessions with only the tools listed. One is a user-level Claude
Code subagent definition.

| Agent | Origin | How it is meant to be used |
| --- | --- | --- |
| `ops` | agent-os | Runs the `feature-brief`, `feature-build`, `feature-validate` and `feature-review` steps. In a timed build, brief a subagent with the matching skill and this persona: validate runs every check for real and answers `PASS`/`FAIL` first; review is read-only and never passes code it did not read. The daemon-only parts (`heartbeat`, `daily-digest`, `mcp__agentos__*`) do not apply outside agent-os. |
| `blackbox-qa-validator` | user-level `~/.claude/agents/` | A subagent that tests a running app from the outside, never reads source, and keeps `<app>-qa-behaviors.md` as a regression spec. Point it at the deployed URL in the last phase of the playbook. Drop the file into `.claude/agents/` to make it available as a subagent type. The Claude Code harness appends its own memory section at runtime, so that boilerplate is not included here. |
| `coo` | agent-os | Reads a repo and proposes exactly one well-argued feature, then waits for a human decision. Useful as the "what next" heuristic at minute 90 of the playbook. The `propose_feature` syscall it calls exists only in agent-os. |
| `librarian` | agent-os | Owns a wiki: ingest, query, lint. Reference material for how to constrain an agent to a single write path (`remember`) and treat raw input as untrusted. Not used in a timed build. |

Common shape across all four: state the persona in a few sentences, list
allowed tools explicitly, put hard rules last, and make the machine-read
part of the reply (first line `PASS`/`FAIL`, one-line confirmation) exact.
