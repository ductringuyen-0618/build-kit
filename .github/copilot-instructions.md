# Copilot instructions

Read `AGENTS.md` at the repo root first. It carries the non-negotiables,
the load order for a timed build and the conventions. Then follow the
playbook it names.

Skills are Agent Skills folders at `skills/<name>/SKILL.md`. Before each
phase, read the skill the playbook names for it in full. If the skills
were installed with `npx skills add ductringuyen-0618/build-kit` (or
`gh skill install ductringuyen-0618/build-kit <name>`) they are under
`.agents/skills/` and load on their own; otherwise attach
`skills/<name>/SKILL.md` to the chat as context. `docs/porting.md` has
the install steps.
