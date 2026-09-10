# Serial versus parallel

## Workers: serial

One worker at a time on the codebase. The reasons, in the order they have
cost real time:

1. Two workers on overlapping files produce a merge nobody briefed for.
   The runner then becomes a worker to resolve it, which breaks the rule
   that the runner never edits code.
2. Milestone 2 usually depends on milestone 1's shape (a model, a route,
   a settings key). A parallel worker guesses the shape and guesses
   wrong.
3. Correctness compounds. A validated milestone 1 is a stable base; an
   unvalidated one is a moving target for everyone downstream.

The author's automated workflow runs one build step per instance and
flips the proposal to `building` so a second builder (a daily scheduled
routine) cannot pick the same feature. That flag is the serial rule in file
form.

The exception: two milestones that touch disjoint directories and share
no interface (a backend endpoint and an unrelated docs page). Even then,
run their validators after both land, on the merged branch.

## Validators: parallel

Scrutiny and user-testing validators do not conflict. One reads the diff
and runs commands; the other drives the app. Brief both in one message
and read both reports before deciding. If the app must be started for
the user-testing validator, start it once, before briefing, and pass the
URL.

## Fix attempts: serial, one at a time

After a `FAIL`, one worker run with the verbatim failure, then both
validators again. Do not start the next milestone while a fix is in
flight; its base would be the unfixed branch.

## In a three-hour session

There is one worker (you, or one assistant session). Serial is the only
option. The parallel part is still worth taking: while the scrutiny
commands run in one terminal, open the URL in the browser and walk the
behavioural assertions yourself.
