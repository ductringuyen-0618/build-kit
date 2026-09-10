# PRD template

Write this to `docs/prd.md`. Keep the headings; `write-issue` reads the
Functional requirements list.

```markdown
# PRD: <one-line title>

| Field        | Value                                    |
|--------------|------------------------------------------|
| Status       | Draft / In review / Approved / Shipped   |
| Owner        | <name or role>                           |
| Created      | <YYYY-MM-DD>                             |
| Target ship  | <date, or "end of session">              |
| Design file  | docs/design.md                           |

## Summary
<2 to 3 sentences: what we are building, for whom, and the core value.
Readable on its own.>

## Problem
<The pain we address, concrete enough to picture the moment a user feels it.
Pull from the design file's Goal and Why now.>

## Goals and non-goals
### Goals
- <outcome>
### Non-goals
- <explicitly not doing this round>

## Users and use cases
### Primary user
<who they are, what they are trying to do, what they do instead today>
### Use cases
1. <named concrete scenario walking through the moment of value>
2. <scenario>

## Requirements
### Functional
- FR1: <one observable behaviour>
- FR2: <one observable behaviour>
### Non-functional
- **Performance**: <e.g. p95 under 500 ms, or not applicable>
- **Reliability**: <e.g. retries, or not applicable>
- **Security**: <e.g. auth required, secrets in env>
- **Accessibility**: <e.g. keyboard navigable, or not applicable>

## Success metrics
### Leading indicators
<what we watch in the first days>
### Lagging indicators
<the outcome metric later>
### Rollback criteria
<what makes us revert; be specific>

## Rollout plan
1. <phase>
2. <phase>

## Dependencies
- **Internal**: <people or components>
- **External**: <vendors, APIs, libraries>

## Risks and mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| <risk> | L/M/H | L/M/H | <how we handle it> |

## Open questions
- <question>: owner = <name>

## FAQ (out of scope)
**Q: Will this also do X?**
A: No, X is out of scope for v1. See Non-goals.
```

## Short example

```markdown
# PRD: URL shortener with click counts

| Field        | Value            |
|--------------|------------------|
| Status       | Draft            |
| Owner        | the builder      |
| Created      | 2026-01-15       |
| Target ship  | end of session   |
| Design file  | docs/design.md   |

## Summary
A public HTTP service that shortens URLs and reports how often each short
link is opened. No accounts; anyone with the URL can use it.

## Problem
Long links are awkward to share and give no signal about whether anyone
opened them. A minimal shortener with a count solves both.

## Goals and non-goals
### Goals
- Create, follow, and count links on a public URL.
- Every route covered by an automated test.
### Non-goals
- Custom aliases, expiry, authentication, per-visitor analytics.

## Users and use cases
### Primary user
Anyone sharing a link; today they paste the long URL and never learn if it
was opened.
### Use cases
1. Share: post a long URL, get a short code, paste it in a chat.
2. Check: open the count endpoint a day later and see the number.

## Requirements
### Functional
- FR1: POST /links with a valid URL returns 201 and a short code.
- FR2: POST /links with an invalid URL returns 400 and stores nothing.
- FR3: GET /<code> redirects with 302 and increments the count.
- FR4: GET /links/<code> returns the URL and count; unknown code returns 404.
### Non-functional
- **Performance**: not applicable.
- **Reliability**: lost increments under concurrency are acceptable.
- **Security**: reject non-http(s) schemes.
- **Accessibility**: not applicable (API only).

## Success metrics
### Leading indicators
All four FRs pass on the live URL at the end of the session.
### Lagging indicators
not applicable
### Rollback criteria
Redirect route returns 5xx on the live URL.

## Rollout plan
1. Deploy to the public URL at the end of the session.

## Dependencies
- **Internal**: none
- **External**: the hosting platform and its managed database.

## Risks and mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Code collision | L | M | 7 random chars; retry on unique-constraint failure |

## Open questions
- Rate limiting: owner = the builder, deferred to README.

## FAQ (out of scope)
**Q: Can I pick my own alias?**
A: No, not in v1. See Non-goals.
```
