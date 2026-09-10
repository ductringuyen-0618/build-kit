# Install

The kit follows the open [Agent Skills](https://agentskills.io/specification)
format: every skill is `skills/<name>/SKILL.md` with `name` and
`description` frontmatter, plus optional `references/`, `scripts/`,
`examples/` or `assets/`. Anything that reads that format can load these
skills. There is no repo-level manifest; the `skills/` folder is the
package.

## One command, any tool

The [`skills` CLI](https://github.com/vercel-labs/skills) (from
[skills.sh](https://skills.sh)) discovers `skills/*/SKILL.md` in a GitHub
repo and installs into the folder each tool reads. Run it inside the
session repo:

```
npx skills add ductringuyen-0618/build-kit
```

It prompts for which skills and which tools. Useful flags:

```
npx skills add ductringuyen-0618/build-kit --list            # show what is in the repo
npx skills add ductringuyen-0618/build-kit --all             # every skill, every detected tool, no prompts
npx skills add ductringuyen-0618/build-kit -y \
  -a claude-code cursor codex github-copilot windsurf \
  -s grill-me deploy-digitalocean-app-platform ci-cd-github-actions
npx skills add ductringuyen-0618/build-kit -g ...            # user-level (~/) instead of the project
npx skills add ductringuyen-0618/build-kit --copy ...        # copy instead of symlink
```

What it writes, per tool (verified on 2026-09-09 against the public repo):

| Tool | Project path | User path | Reads it because |
| --- | --- | --- | --- |
| Claude Code | `.claude/skills/<name>/` (symlink to `.agents/skills/<name>/`) | `~/.claude/skills/` | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| Cursor | `.agents/skills/<name>/` | `~/.cursor/skills/` | [Cursor skills](https://cursor.com/docs/skills) reads `.agents/skills/`, `.cursor/skills/` and, for compatibility, `.claude/skills/` |
| Codex | `.agents/skills/<name>/` | `~/.agents/skills/` | [Codex skills](https://learn.chatgpt.com/docs/build-skills) |
| GitHub Copilot | `.agents/skills/<name>/` | `~/.copilot/skills/` | [Copilot agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) reads `.github/skills`, `.claude/skills` or `.agents/skills` |
| Windsurf | `.windsurf/skills/<name>/` (symlink to `.agents/skills/<name>/`) | `~/.codeium/windsurf/skills/` | [Windsurf skills](https://docs.windsurf.com/windsurf/cascade/skills) reads `.windsurf/skills/` and `.agents/skills/` |

`.agents/skills/` is the canonical copy; the other folders are symlinks to
it. The CLI also writes `skills-lock.json` (source, path, content hash) so
`npx skills update` can refresh later. On Windows, symlinks need Developer
Mode or an elevated shell; pass `--copy` if the symlink step is skipped.

Skills carry `references/`, `briefings/` and `scripts/` with them, so a
skill that points at a bundled file (for example `missions` and its
`briefings/`) works from the installed copy.

Once installed, a skill triggers by its `description` when the request
matches, and Claude Code, Cursor and Codex can also invoke it by name
(`/grill-me`).

Copilot users can use GitHub's own installer instead:

```
gh skill install ductringuyen-0618/build-kit grill-me
```

## Entry point

Every tool listed above also reads `AGENTS.md` at the repo root (Copilot
additionally reads `.github/copilot-instructions.md`, Cursor
`.cursor/rules/*.mdc`, Claude Code `CLAUDE.md`). Copy this repo's
`AGENTS.md` into the session repo, or keep the kit checked out next to
it and tell the assistant to read the kit's `AGENTS.md` first. The three
tool-specific files in this repo are one-paragraph pointers at
`AGENTS.md`; copy them too if you want them.

Role briefs in `agents/<role>.md` are plain Markdown. In Claude Code,
copy one to `.claude/agents/<role>.md` in the session repo and add a
`name` and `description` frontmatter to make it a subagent type; in any
other tool paste it as the first message of a new chat (see
`agents/README.md`).

## Manual fallback

No `npx`, or no network to GitHub: clone the kit and copy or symlink the
skill folders yourself. The target is any folder in the table above.

```
git clone https://github.com/ductringuyen-0618/build-kit.git
mkdir -p .agents/skills
cp -R build-kit/skills/grill-me .agents/skills/      # Cursor, Codex, Copilot
cp -R build-kit/skills/grill-me .claude/skills/      # Claude Code
cp -R build-kit/skills/grill-me .windsurf/skills/    # Windsurf
```

PowerShell: `Copy-Item -Recurse build-kit\skills\grill-me .agents\skills\`.

The skill folder is the unit. Copy the whole folder, not just
`SKILL.md`, or the `references/` and `scripts/` links inside it break.

## Plain chat

Paste `AGENTS.md`, then the `SKILL.md` for the current phase, then any
file under its `references/` that the body points to. Skills with
`scripts/` (`smoke-verify`) need the script run locally; paste its
output back. The `missions/briefings/` files are meant to be pasted
whole into a fresh chat, one per role.

## Format notes for contributors

- `name` must equal the folder name, lowercase with hyphens, max 64
  characters. `description` is required, max 1024 characters, and should
  say what the skill does and when to use it. The CLI skips a skill with
  no `name`.
- Optional frontmatter: `license`, `compatibility`, `metadata`,
  `allowed-tools`. Claude Code adds its own fields (`disable-model-invocation`,
  `context: fork`, `paths`, ...) which other tools ignore.
- Keep `SKILL.md` under 500 lines; move detail into `references/`.
- Validate with `skills-ref validate skills/<name>` from
  [agentskills/agentskills](https://github.com/agentskills/agentskills/tree/main/skills-ref).
- Anthropic's own skills at [anthropics/skills](https://github.com/anthropics/skills)
  use the same layout and are a good reference for tone and length.
