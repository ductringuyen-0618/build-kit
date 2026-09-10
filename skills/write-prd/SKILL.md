---
name: write-prd
description: Use after grill-me when the work is bigger than one ticket; turns docs/design.md into a short product requirements document at docs/prd.md that a builder can split into issues.
---

# write-prd

## Purpose

A PRD states the product-level "what and why" for work that spans more
than one ticket: a feature with several parts, a new surface, a
significant behaviour change. It assumes the design is already shared, so
this skill is a thin layer over `grill-me`. It does not reopen decisions
the design file already made. The deliverable is `docs/prd.md`.

## When to use

- `grill-me` has produced `docs/design.md` for this work.
- The work needs three or more issues to build.
- The user says "PRD", "spec", "requirements doc", or "write up what this
  feature is".

## When not to use

- One ticket's worth of work: use `write-issue` directly.
- No design file yet: run `grill-me` first. Do not invent context.
- The user wants an architecture decision record; that has a different
  shape and audience.

## Inputs

- `docs/design.md` (or `docs/design-<slug>.md`). Required.
- Answers to the gap questions in step 3.
- `references/prd-template.md` for the structure and a short example.

## Steps

### 1. Locate the design file

Look for `docs/design.md`, then `docs/design-*.md` matching the topic. If
none exists, say: "There is no design file for this yet. Want me to run
`grill-me` first, then come back to the PRD?" Wait for the answer. If the
user insists on skipping, ask the five short-time questions from
`grill-me/references/question-categories.md` inline, then continue.

### 2. Read the design file end to end

Note anything under "Open questions" or "Assumptions": each must be
resolved here or carried into the PRD as a risk. Note anything terse or
vague; that is where to ask a gap question.

### 3. Ask the gap questions that are missing

A PRD needs a few things the design file may not have. Ask only the ones
that are missing, one at a time, at most four:

- **Owner**: who decides when this is done?
- **Timeline**: target date or session length; milestones if any.
- **Rollout**: flag, gradual, pilot users, or straight to everyone?
- **Metrics**: what will be watched after launch?
- **Dependencies**: other people, services, or reviews needed.

### 4. Write `docs/prd.md`

Use `references/prd-template.md`. Fill every section or mark it "not
applicable"; do not leave placeholder text. Quote the design file's
wording rather than paraphrasing, so readers can cross-reference. If a
`docs/prd.md` for a different topic already exists, write
`docs/prd-<slug>.md` and say so.

### 5. Hand off

Say: "PRD saved to `docs/prd.md`, status Draft. Next: run `write-issue`
once per functional requirement to produce buildable tickets." Ask for
review from the owner if the owner is not the user.

## Outputs

- `docs/prd.md` (or `docs/prd-<slug>.md`).
- A list of functional requirements, each phrased so `write-issue` can turn
  it into one ticket.

## In a 3-hour build

Budget 5 minutes, and only if the work genuinely needs three or more
issues; most 3-hour builds skip the PRD and go from `docs/design.md`
straight to `write-issue`. If you do write one: fill Summary, Problem,
Goals and non-goals, Functional requirements, and Rollback criteria. Mark
Success metrics, Rollout plan, Dependencies, and the FAQ "not applicable"
unless the design file already answers them. Do not ask gap questions;
take Owner as the user, Timeline as the session, and Rollout as "deploy
to the public URL at the end".

## Style rules

- Readable by a non-engineer. A PRD's audience includes product, design,
  and review, not only the builder.
- Be honest about open questions. Three listed unknowns beat confident
  filler.
- Do not pad. A one-row risk table is fine.
- Match length to scope. A small feature fits on one screen.
- Each functional requirement is one observable behaviour, not a bundle.

## Done when

- `docs/prd.md` exists with every section filled or marked not applicable.
- Every open question from the design file is resolved or listed as a risk.
- Each functional requirement could be handed to `write-issue` as is.

## Bundled files

- `references/prd-template.md`: the template plus a short filled example.
