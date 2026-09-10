# Design file template

Write this to `docs/design.md`. Keep the headings exactly as shown;
`write-prd` and `write-issue` look for them by name. Mark a section
"not applicable" rather than deleting it.

```markdown
# Design: <one-line title>

> Written by grill-me on <YYYY-MM-DD>. Source for the PRD, issues, and build.

## Goal
<1 to 2 sentences. What is true after this ships.>

## Why now
<The pressure or opportunity that makes this worth doing now.>

## Users
- **Primary**: <who triggers or depends on this>
- **Secondary**: <who is affected but is not the main audience>

## Scope
**In scope:**
- <bullet>

**Out of scope (explicit non-goals):**
- <bullet>

## Success criteria
<Concrete, observable, ideally measurable.>

## Constraints
- **Tech**: <stack, language, framework, hosting>
- **Time**: <deadline or session length>
- **Compatibility**: <what must keep working>
- **Other**: <budget, security, regulatory, or "none">

## Affected surfaces
<Routes, services, tables, UI screens, external services this touches.>

## Data
- **Inputs**: <where data comes from>
- **Outputs**: <where data goes>
- **Source of truth**: <which store is canonical>

## Failure modes and handling
- <Risk>: <how it is handled or mitigated>

## Alternatives considered (and rejected)
- <Alternative>: <why not>

## Assumptions
<Answers you supplied yourself because the user was not available or
said "you decide". Each one is a candidate open question.>

## Open questions
<Deferred on purpose. Listed so the next step does not re-litigate them.>

## Conversation log
- Q: <question> | A: <answer>
```

## Short example

```markdown
# Design: URL shortener with click counts

> Written by grill-me on 2026-01-15. Source for the PRD, issues, and build.

## Goal
A public service that turns a long URL into a short code and reports how
many times each code was opened.

## Why now
Timed build session; the goal is a deployed, demoable service in three hours.

## Users
- **Primary**: anyone with the public URL; no accounts.
- **Secondary**: the reviewer watching the demo.

## Scope
**In scope:**
- POST /links creates a code; GET /<code> redirects; GET /links/<code> shows the count.
**Out of scope (explicit non-goals):**
- Custom aliases, expiry, authentication, analytics beyond a count.

## Success criteria
Creating, following, and reading the count for a link all work on the
public URL, with automated tests covering each.

## Constraints
- **Tech**: user's chosen stack; single service; managed Postgres or SQLite.
- **Time**: 3 hours including deploy.
- **Compatibility**: none, new repo.
- **Other**: none.

## Affected surfaces
New service; three HTTP routes; one table `links(code, url, clicks, created_at)`.

## Data
- **Inputs**: a URL in a JSON body.
- **Outputs**: a short code; a 302 redirect; a JSON count.
- **Source of truth**: the `links` table.

## Failure modes and handling
- Invalid URL: return 400 with a message; do not store it.
- Unknown code: return 404, do not increment anything.

## Alternatives considered (and rejected)
- Hash of the URL as the code: collisions and leaks structure; use random 7 chars.

## Assumptions
- Counting is best-effort; a lost increment under concurrent load is acceptable.

## Open questions
- Rate limiting: deferred; note it in the README.

## Conversation log
- Q: What is the smallest version that is still valuable? | A: Create, redirect, count.
- Q: Who uses it? | A: Public, no login.
- Q: What must not break? | A: Nothing; greenfield.
- Q: How do we know it worked? | A: The three routes work on the live URL with tests.
- Q: Worst thing when it breaks? | A: Redirect to a bad URL; validate on input.
```
