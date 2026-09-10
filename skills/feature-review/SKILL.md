---
name: feature-review
description: Product-quality review of a validated feature branch against its brief, judging whether it feels finished (states, copy, consistency, accessibility basics, scope fidelity) and returning PASS or FAIL with file-level reasons. Use after feature-validate passes and before merging or demoing.
---

# Feature review

Purpose: the checks are green, now ask whether a user would call this
done. Review fit to the brief and product quality, not test results.
Return a verdict another agent can act on without asking follow-ups.

## Where it sits in the chain

```
feature-brief  ->  feature-build  ->  feature-validate  ->  feature-review
                                                             (this skill)
```

Run it as a fresh pass, like `feature-validate`: a new agent or chat that
receives the branch and the brief, not the builder's transcript. If
`feature-validate` has not returned PASS, stop and run it first. A review
on a red branch wastes the reviewer's time.

In a 3-hour build: about 10 minutes, at minute 140. Fix or cut FAIL items
before the deploy phase at minute 150. Do not open new ideas here.

## When to use

- `feature-validate` says PASS and the feature is about to be merged,
  deployed, or demoed.
- A human asks "is this actually finished?"

## Inputs

- The branch `feature/<slug>` and the default branch to diff against.
- `docs/features/<slug>.md` (the brief), especially Proposed solution,
  Scope, Effort and Validation contract.
- `docs/features/<slug>.validate.md` for what was verified.
- If the feature has a UI: the running app, or screenshots the builder
  or validator captured.

## Steps

1. **Read the diff, then the files.**
   ```
   git diff <default-branch>...feature/<slug> --stat
   git diff <default-branch>...feature/<slug>
   ```
   For any change whose meaning depends on context, open the whole file:
   a new function's neighbours, a changed component's parent, a modified
   route's error handling.
2. **Scope fidelity.** Does the diff do what Proposed solution says, not
   an adjacent thing? Is anything from Out present? Is anything from In
   missing? Does the file count fit the Effort estimate? A "small" brief
   that touched 30 files is a smell worth a sentence.
3. **Finished, not merely working.** Walk the checklist in
   `references/quality-checklist.md`. The short form:
   - States: empty, loading, error, success, and the boundary case each
     assertion implies. A list with no empty state is unfinished.
   - Copy: user-facing text reads like the rest of the product, no
     placeholder strings, no developer jargon in errors, consistent
     casing and terminology.
   - Consistency: same patterns as neighbouring code for naming, errors,
     logging, config, styling. No second way of doing an existing thing.
   - Accessibility basics (UI only): keyboard reachable, visible focus,
     labels on inputs, alt text, contrast not obviously broken, no
     information carried by colour alone.
   - API surface (services): status codes and error envelope match the
     rest of the API, inputs validated, no secrets or stack traces in
     responses.
   - Leftovers: TODOs, commented-out code, debug logs, dead branches,
     skipped tests, stub returns.
4. **Try it once** if you can run it: the manual check from the brief,
   plus one thing a user would do that the brief did not list.
5. **Write the verdict** (format below) to
   `docs/features/<slug>.review.md` and paste it in chat. First line is
   exactly `PASS` or `FAIL`. Every FAIL item names the file, the problem,
   and what fixed looks like. "Needs polish" is not a finding.

## Output: `docs/features/<slug>.review.md`

```markdown
FAIL

Branch: feature/<slug> @ <short sha>   Date: <ISO date>
Reviewed against: docs/features/<slug>.md

## Scope fidelity
<one paragraph: matches / drifts, with specifics>

## Findings
1. src/components/ItemList.tsx: no empty state; renders a blank div when
   items is []. Fixed looks like: a short message and the primary action.
2. src/api/items.py:42: error returns 500 with a raw exception string.
   Fixed looks like: 400 with the shared error envelope used in users.py.

## Passed checks
<bullets of what was checked and found fine, so the next reviewer does
not redo them>

## Notes (not blocking)
<ideas, deferred items, things for the demo notes>
```

A PASS report has the same shape with an empty Findings section.

## Done when

- Every changed file was read, not just listed.
- The verdict is grounded in the brief's sections, not generic taste.
- Each FAIL finding is file-level and actionable enough to be handed to
  `feature-build` as its retry input verbatim.
- The report file exists and the same text was posted in chat.

## Hard rules

- Read-only. No edits, no commits, no pushes. Running the app or a curl
  is fine; changing code is not.
- Never PASS code you have not read.
- Do not re-run the validation suite to second-guess the validator; read
  its report. If you distrust it, say so in Notes and FAIL on the
  specific assertion.
- Do not add scope. New ideas go under Notes.
