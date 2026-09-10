# Agents

Role briefs for splitting a build across several agents. Each brief is
plain Markdown with no tool-specific syntax, so it works in Claude Code,
Cursor, Codex, Copilot, or a second chat window pasted by hand.

## The pattern

- **One coordinator.** It holds the plan and the end goal, assigns roles in
  order, and decides what happens next. It never does the work itself.
- **Roles with a single responsibility.** A role either builds, checks, tests,
  or reviews. It never does two of those, and it never redefines its own
  scope.
- **Fresh context per role.** Each role receives only its brief plus the task
  it is given. In particular, a validator must not see the builder's
  reasoning or report, only the resulting code. This is what makes the check
  independent.
- **Structured report back.** Every role ends with the report format its brief
  specifies. The coordinator reads that report, not the transcript.
- **Nothing is done until CI is green.** A builder saying "done" is a claim.
  Passing checks, run by someone who did not write the code, is evidence.

## The roles

| Role | File | One line |
| --- | --- | --- |
| Coordinator | `coordinator.md` | Keeps the plan, assigns roles in order, counts attempts, stops at 3. |
| Builder | `builder.md` | Implements one validation contract on a branch in small commits. |
| Scrutiny validator | `scrutiny-validator.md` | Runs exactly what CI runs on the diff, reports PASS or FAIL with output. |
| User tester | `user-tester.md` | Uses the running product like a user, black-box, pass or fail with reasons. |
| Product reviewer | `product-reviewer.md` | Judges finish quality: states, copy, consistency, accessibility. |

Order for one unit of work: coordinator writes the task, builder builds,
scrutiny validator checks, user tester exercises (if the change is
user-facing), product reviewer polishes (last pass before shipping). Any
FAIL goes back to the builder with the report attached.

## How to hand a role to an agent

The hand-off is always the same three parts: the role brief verbatim, the
task (goal, validation contract, branch or commit to start from), and the
sentence "Reply using the report format in the brief."

- **Claude Code.** Use the Agent tool with the brief and task as the prompt.
  To make a role a reusable subagent type, copy its file into
  `.claude/agents/<role>.md` and add a frontmatter block with `name` and
  `description`. Give validators and reviewers a fresh agent, never a fork,
  so they do not inherit the builder's context.
- **Cursor.** Start a background agent (or a new chat) and paste brief plus
  task as the first message. Point it at the branch the builder used.
- **Codex.** Start a new thread per role with the same first message. Use a
  separate thread for each validator so nothing leaks from the build thread.
- **Copilot.** Open a new chat session per role, paste brief plus task, and
  attach the changed files or the diff rather than the whole conversation.
- **Any other tool, or by hand.** Open a second chat, paste brief plus task.
  Copy the report back into the coordinator's chat. Nothing here depends on
  a tool feature.

If the tool cannot run commands, the scrutiny validator and user tester
roles cannot be filled by it. Run the commands yourself and paste the
output into the role's report format instead of skipping the step.

## Roles that live upstream

Earlier versions of this folder carried three runtime agents (`coo`,
`librarian`, `ops`) from the author's always-on agent runtime. They need
a scheduler, a wiki, and a set of syscalls that only exist in that
runtime, so they do not belong in a timed build. They live in the agent
runtime repo linked from the README's Provenance section.
