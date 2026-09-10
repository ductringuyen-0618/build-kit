---
name: feature-brief
description: Turn a plain-words feature request into a one-page proposal at docs/features/<slug>.md with "What you get", "Why now", scope, and a validation contract of checkable assertions plus exact test commands. Use before building any feature so the builder, validator and reviewer all hold the same definition of done.
---

# Feature brief

Purpose: convert "add X" into a proposal a builder with no other context
can implement, and a contract a validator and reviewer can hold the build
to. Everything downstream (`feature-build`, `feature-validate`,
`feature-review`) reads this one file, so it must be concrete.

## Where it sits in the chain

```
feature-brief  ->  feature-build  ->  feature-validate  ->  feature-review
 (this skill)      implements the      runs the exact       judges product
 writes the        contract on a       commands, PASS/FAIL  quality, PASS/FAIL
 contract          branch
```

In a 3-hour build: about 10 minutes, inside the first 15. Do not spend
longer. A brief that took 25 minutes has stolen time from the build.

## When to use

- Someone gives you a feature request in plain words, a ticket, or an
  issue file, and you are about to build it.
- Before `feature-build`; never skip it because the feature "is small".
  Small features get a short brief, not no brief.

## Inputs

- The request: a sentence, a ticket, or `docs/issues/<slug>.md` if one
  exists.
- The repository. Read `README.md`, `CLAUDE.md`, `AGENTS.md`,
  `CONTRIBUTING.md` if present, and `.github/workflows/*.yml`.
- The slug: kebab-case from the title, e.g. `add-dark-mode-toggle`. The
  branch name is `feature/<slug>`, so pick it once and keep it.

## Steps

1. **Ground yourself in the repo (3 minutes).** Find the stack, the
   package manager, the test runner, and the commands CI runs. Note which
   files the feature will most likely touch. If a fact is unknown, write
   "unknown" in the brief. Never invent a fact about the project.
2. **Restate the problem** in two sentences, precise enough that a wrong
   reading is impossible. If the request is ambiguous in a way that
   changes the work, list the reading you chose under Assumptions.
3. **Write the validation contract first, then the solution.** The
   contract is the definition of done. Each assertion must be something a
   second agent can check without asking you. Three kinds are required:
   - Functional: what happens on the happy path.
   - Behavioral: what the user sees or the caller gets back (status
     codes, states, copy, timing).
   - Negative: what must not happen, what the feature must not change.
   Then list the exact commands, copied from CI, that must exit 0.
4. **Write `docs/features/<slug>.md`** using the template below. Keep it
   under one screen per section.
5. **Show the brief in chat** and ask for approval when a human is in the
   loop. In an unattended run, say which assumptions you made and
   continue to `feature-build`.

## Output: `docs/features/<slug>.md`

```markdown
# <Title>

Slug: <slug>   Branch: feature/<slug>   Status: proposed

## What you get
One paragraph, plain language, what ships and who notices.

## Why now
Two or three sentences: what it unlocks today, what it costs to wait.

## Problem
The concrete problem, restated precisely.

## Proposed solution
What changes, in which files or modules, roughly how. Name existing
patterns to follow. Specific enough for a builder with no other context.

## Scope
In: <bullets>
Out: <bullets, including things a reader might assume are included>

## Assumptions
<bullets, or "none">

## Effort
small | medium | large, one-line reason, and expected files touched.

## Validation contract
### Functional
- F1. <assertion>
### Behavioral
- B1. <assertion>
### Negative
- N1. <assertion>
### Commands (must exit 0, copied from .github/workflows)
- `<lint command>`
- `<typecheck command>`
- `<test command>`
- `<build command>`
### Manual check
- One thing to do by hand and what you should see.

## Risks
<what could go wrong and how you would notice>
```

## Done when

- `docs/features/<slug>.md` exists with every section filled or marked
  "unknown" / "none".
- Every contract assertion is checkable by someone else. "Works well" is
  not an assertion; "GET /items?page=2 returns 200 and 20 rows" is.
- The commands are copied from CI, not guessed.
- Nothing in the brief is a fact you could not point to in the repo or
  the request.

## Hard rules

- The brief is the only file you write. Do not start the implementation.
- Do not widen the scope beyond the request. Extra ideas go under Out.
- Never write secrets or credentials into the brief.
