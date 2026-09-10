# Copilot instructions

Read `AGENTS.md` at the repo root first. It is the entry point for every
assistant: non-negotiables (tests and CI green before done, conventional
commits, no secrets, README with run instructions, a deploy target from
minute one), the load order for a timed build, and the conventions.

Then follow `playbook/3-hour-build.md`. Choose the stack with
`playbook/stack-picker.md`. Skills are plain Markdown under
`skills/<name>/SKILL.md`; attach the relevant one to the chat as context
before starting a phase. Per-stack scaffolding files live under
`templates/<stack>/`.
