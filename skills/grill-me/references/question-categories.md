# Question categories for grill-me

A taxonomy to draw from while interviewing. Do not ask all of them. Pick
the ones with the highest leverage on what gets built, and skip anything
the codebase or the brief already answers.

## The five to ask when time is short

1. What is the smallest version that would still be valuable?
2. Who uses it, and what do they do today instead?
3. What is explicitly out of scope?
4. How will we know it worked?
5. What is the worst thing that happens when it breaks?

## Goal and motivation
- What does success look like a month after this ships?
- Who feels the pain this fixes? Describe one concrete moment.
- If we did nothing, what is the worst case in six months?
- What is the goal behind the goal?

## Users and audience
- Who triggers this: a person, an automated system, both?
- How often per user, per day?
- What do they do today instead?

## Scope
- What is the smallest version that is still valuable?
- What are we explicitly not doing?
- Is this v1 of something bigger, or complete on its own?
- Does this replace something, or live alongside it?

## Constraints
- What cannot change (API, schema, deployment, auth model)?
- What is the deadline?
- Cost, infrastructure, or headcount limits?
- Compliance, regulatory, or security requirements?

## Data
- Where does input come from? Format, freshness, volume?
- Where does output go? Persisted or ephemeral?
- What is the source of truth?
- What about deletion or right-to-erasure?

## Existing system
- Which parts of the codebase does this touch?
- Extend an existing service or create a new one?
- Which contracts (API, schema, events) must stay stable?
- Same deploy pipeline or a new one?

## Success criteria
- How will you know it worked?
- Leading indicator? Lagging indicator?
- What would make us roll it back?

## Failure modes and risk
- What is the worst thing that happens if this breaks?
- What user data is at risk?
- Can it sit behind a flag and be switched off instantly?
- What is the blast radius of a bug?

## Alternatives
- What did you consider before this, and why did you rule it out?
- Is there an off-the-shelf option we would be reinventing?

## Dependencies
- Does this need work from other people or teams?
- Is an external service, vendor, or library involved?
- What is blocked if this slips?

## Edge cases
- Zero data? Huge data?
- Two users doing this at once?
- Retries, duplicates, partial failure?
- Localisation, accessibility, device class?

## Operations
- Who owns this once it ships?
- What logging or metrics do we want from day one?

## How to use this list

1. Skim it before the first question.
2. Pick the 3 or 4 categories least obvious from the user's prompt.
3. In each, choose the question most likely to surface a surprise.
   Boring questions get boring answers.
4. You are not running a checklist. You are hunting for the places where
   the user's mental model and yours would diverge if you started building
   now.
