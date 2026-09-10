---
name: write-issue
description: Use to turn one ticket-sized piece of work (a bug, a feature increment, a bounded refactor) into a GitHub issue with testable acceptance criteria, created with gh or saved under docs/issues/ when gh is unavailable.
---

# write-issue

## Purpose

A good issue is the smallest unit of work one person can claim, finish in
hours to a few days, and verify against an acceptance checklist. This
skill writes one: concise, scoped, with a clear definition of done. It
reads `docs/design.md` (and `docs/prd.md` if present) so the builder does
not have to re-derive context.

## When to use

- One bug fix, one feature increment, one bounded refactor, one chore.
- After `write-prd`: one issue per functional requirement.
- After `grill-me` in a short build: one issue for the core feature.

## When not to use

- The work clearly spans several tickets: run `write-prd` first, then
  come back here for each child.
- The change is trivial (typo, version bump). Just do it.

## Inputs

- `docs/design.md` if it exists; `docs/prd.md` if it exists.
- Otherwise the answers to the mini-grill in step 2.
- `references/issue-template.md` for the structure and a short example.

## Steps

### 1. Locate context

Read `docs/design.md` (or `docs/design-*.md`) and `docs/prd.md` if they
exist. "Affected surfaces", "Constraints", and "Failure modes" fill most
of the issue. If writing from a PRD, take exactly one functional
requirement per issue.

### 2. Mini-grill (only if no design file)

Ask these one at a time, then stop:

1. What outcome are you after? One sentence: the "done" state.
2. What does current behaviour look like? Repro steps for a bug; today's
   gap for a feature.
3. Which file or area do you suspect?
4. How will you know it is done? One to three acceptance criteria.

If the user starts answering with "and we also need to think about how it
interacts with…", the scope is too big. Say so and offer `grill-me`.

### 3. Check it is issue-sized

- One engineer, at most about three days; in a timed build, at most about
  an hour.
- Touches roughly five files or fewer.
- One "done" condition the builder can verify alone.
- No coordination with other teams required.

If any fail, split it or recommend `write-prd`.

### 4. Write the issue

Fill `references/issue-template.md`. Rules:

- Imperative title: "Add source filter to list", not "Source filtering".
- Acceptance criteria are observable and testable. "Returns 200 with
  `{ok: true}` for a valid query" is a criterion; "looks good" is not.
  Aim for three to six.
- Copy affected files and constraints from the design file rather than
  linking to it; the builder should not need both.
- Implementation notes are hints, not orders.
- Delete empty sections. Empty headings are noise.
- If you write "and also" twice, split the issue.

### 5. Create it

Prefer a real GitHub issue:

```sh
gh issue create --title "<title>" --body-file <tmpfile> --label <type>
```

If `gh` is missing, not authenticated, or the repo has no GitHub remote,
save the same body to `docs/issues/<slug>.md` (create the folder) where
`<slug>` is short kebab-case, and tell the user it can be pasted into
any tracker. Either way, report the issue URL or file path.

If the issue is a child of a PRD, add a line under the matching
functional requirement in `docs/prd.md`: `- FR2: … (#<number>)` or
`(docs/issues/<slug>.md)`.

## Outputs

- One GitHub issue (URL) or one file at `docs/issues/<slug>.md`.
- A back-link from `docs/prd.md` when a PRD exists.

## In a 3-hour build

Budget 5 minutes for the core-feature issue; one more issue later for the
second feature or hardening pass. Skip the mini-grill; the design file
has the answers. Fill Context, Description, Acceptance criteria, and
Verification only; drop Implementation notes, Out of scope, and Risks
unless one line each is obvious. Three to five acceptance criteria, each
mapped to a test you will write. Use `docs/issues/` without checking for
`gh` if you are not already authenticated; do not spend time on auth.

## Anti-patterns

- Stakeholder Q&A inside an issue (that belongs in the PRD).
- Subjective criteria ("the UI feels responsive").
- Arguing for the work in the body; it was approved in the design file.
- Bundling a bug fix with an unrelated chore "while we are in there".

## Done when

- The issue exists (URL or file) with three to six testable acceptance
  criteria and a verification step the builder can run.
- The scope check in step 3 passed.
- The PRD, if any, links to the issue.

## Bundled files

- `references/issue-template.md`: the template plus a short filled example.
