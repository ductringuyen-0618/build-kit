# Issue template

The title goes in the issue title field (or the first heading of
`docs/issues/<slug>.md`). Everything below the title is the body. Delete
sections that would be empty.

```markdown
# [<Bug|Feature|Refactor|Chore|Docs|Test>] <imperative one-line title>

**Priority**: P0 / P1 / P2 / P3 · **Estimate**: XS / S / M · **Links**: docs/design.md, docs/prd.md FR<n>

## Context
<2 to 4 sentences: why this work exists, current state, desired state.
Pull from the design file.>

## Description
<Concrete description of what to do. Use observable verbs, not "improve"
or "enhance".>

For a bug:
**Steps to reproduce:**
1. <step>
2. <step>
**Expected:** <what should happen>
**Actual:** <what happens today>

For a feature:
**Today:** <current behaviour>
**After this change:** <new behaviour>

## Acceptance criteria
Done when all of these are true:
- [ ] <observable, testable criterion>
- [ ] <observable, testable criterion>
- [ ] <observable, testable criterion>

## Implementation notes
<Optional hints: files likely involved and why, patterns to mirror, tests
to add. The builder may deviate.>

## Out of scope
- <what this issue deliberately does not do>

## Verification
- <command to run, e.g. the test suite or a curl against the route>
- <manual check on the running app, if any>

## Risks
- <one line each, or delete the section>
```

## Short example

```markdown
# [Feature] Redirect short codes and count clicks

**Priority**: P1 · **Estimate**: S · **Links**: docs/design.md, docs/prd.md FR3

## Context
The service can create short codes (FR1) but following one does nothing
yet. This issue adds the redirect route and the click counter, which is
the core user-visible behaviour of the product.

## Description
**Today:** GET /<code> returns 404 for every code.
**After this change:** GET /<code> looks up the code, increments its
click count, and responds with a 302 to the stored URL. Unknown codes
still return 404 and change nothing.

## Acceptance criteria
- [ ] GET /<known code> responds 302 with `Location` set to the stored URL.
- [ ] Each successful redirect increases `clicks` by one.
- [ ] GET /<unknown code> responds 404 and no row is modified.
- [ ] An automated test covers each of the three cases above.

## Implementation notes
- Reuse the lookup in the links repository; do not add a second query path.
- Increment in the same statement as the lookup to avoid a read-then-write race.

## Out of scope
- Per-visitor analytics, expiry, custom aliases.

## Verification
- Run the test suite; the three new tests pass.
- Create a link, curl the short URL with `-I`, confirm 302 and Location.
- Read the count endpoint and confirm it went up by one.
```
