---
name: grill-me
description: Use before designing, planning, or coding any non-trivial change; asks the user the questions that matter, one at a time, until the design is shared, then writes docs/design.md for write-prd, write-issue, and the build to consume.
---

# grill-me

## Purpose

Most planning failures come from one habit: assuming context instead of
asking for it. This skill breaks the habit. When the user wants to plan or
build something, do not start writing the plan. Ask questions until you can
state the design back to the user and they agree with it. Then write the
shared understanding to `docs/design.md` so every later step reads the
same picture.

Works in any agent tool and any stack. It needs only the ability to ask
the user a question and write a file.

## When to use

- The user says "let's plan", "design X", "I want to build", "how should
  we approach", "grill me", or describes a change that touches more than
  one file or system.
- Before `write-prd`, `write-issue`, an architecture decision, or
  implementation of anything non-trivial.
- After a vague directive such as "make it faster".

## When not to use

- Tiny, well-scoped tasks (rename, type annotation, one-line fix). Just do it.
- The user asked a factual question, not for work.
- `docs/design.md` already covers this topic and the user wants to
  continue from it.

## Inputs

- The user's request, however vague.
- The repo, if one exists. Read it before asking anything it can answer
  (stack, existing routes, schema, test setup).
- `references/question-categories.md` when you are unsure what to ask next.

## Steps

### 1. Hold back

Acknowledge the topic in one sentence without proposing anything:
"Before I sketch anything, I want to make sure we agree on a few things."
No architecture, no option list, no code.

### 2. Ask one question at a time

Ask a single question, wait for the answer, then choose the next question
based on it. If your tool offers a structured multiple-choice prompt, use
it, but still one question per turn. Offer 2 to 4 concrete options where
you can; people pick faster than they generate. Avoid yes/no questions.

Start with the dimensions least obvious from the request. A good opening
sequence:

1. The goal behind the goal: what does this get you that you lack today?
2. The users: who triggers it, sees it, or is affected?
3. Scope: what is in, and what is explicitly out?
4. The success criterion: how will we know it worked?

Then follow the answers into constraints, data shape, affected systems,
failure modes, and alternatives already rejected. Plan on 6 to 12
questions in total. The user may stop you at any point with "that's
enough" or "just write it"; respect that immediately.

Stop early when all of these are true:

- You can state the goal in one sentence the user would endorse.
- You know the explicit non-goals.
- You know the success criterion.
- You know which existing code or systems are affected.
- You can name at least one failure mode and how it is handled.

### 3. Play it back

Summarise the shared understanding in chat in 8 to 15 lines. Ask "does
this match what you have in your head?" Correct and repeat until the user
says yes.

### 4. Write `docs/design.md`

Create the `docs/` folder if needed. Use the structure in
`references/design-template.md` so `write-prd` and `write-issue` can find
each section. Keep the conversation log; it saves re-asking later.

If the repo already has a `docs/design.md` for a different topic, write
`docs/design-<slug>.md` instead and say so.

### 5. Hand off

Say: "Saved to `docs/design.md`. Next: `write-issue` if this is one
ticket's worth of work, or `write-prd` if it is larger."

## Outputs

- `docs/design.md` (or `docs/design-<slug>.md`), following the template.
- A short chat summary the user has agreed to.

## In a 3-hour build

Budget 5 to 10 minutes. Ask 5 to 8 questions, not 12. Cover goal, users,
scope in/out, success criterion, and one failure mode; skip operations,
compliance, and long-horizon metrics. If the task brief already answers a
question, state your reading of it and move on rather than asking. Answer
questions yourself out loud when the user is an observer rather than a
collaborator, and record those answers as assumptions in the design file.
Write the file in one pass; do not polish it.

## Style rules

- One question per turn. Never dump a list of ten.
- Prefer multiple choice with distinct options over open-ended prompts.
- Resist proposing. If you start a sentence with "I think we should",
  turn it into a question.
- Read the codebase before asking anything it can answer.
- Do not ask the same dimension twice in different words.
- Prefer a concrete "what" over a philosophical "why".
- The design file is a working document, not a publication. Shared
  understanding now beats perfect prose.
- Trust the user's "stop". Write the file with what you have.

## Done when

- The user has confirmed the played-back summary.
- `docs/design.md` exists with every template section filled or marked
  "not applicable".
- Open questions are listed rather than silently assumed.

## Bundled files

- `references/design-template.md`: the design file structure plus a short
  filled example.
- `references/question-categories.md`: the question taxonomy, with the
  five to ask when time is short.
