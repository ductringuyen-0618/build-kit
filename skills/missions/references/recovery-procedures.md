# Recovery procedures

What the runner does when the loop stops moving. Each case names the
signal, the first thing to check, and the action. None of them involve
the runner editing application code.

## A milestone reaches three attempts

Signal: the attempts column reads 3 and the last validator still says
`FAIL`.

1. Mark the milestone `blocked` in the mission file with the three
   failure first-lines and the branch head.
2. Leave the branch in place. Do not delete, force-push or squash it.
3. Ask: does any remaining milestone depend on this one? If not, continue
   with the next. If yes, stop the mission and report; a human decides
   whether to re-plan.
4. In the final report, list the blocked milestone under "left undone"
   with what the validators saw. That paragraph is more useful than a
   fourth attempt.

The author's scheduled routine uses the same rule: at three attempts the proposal is
marked `blocked` and never touched again without a human editing it
back.

## A worker returns without a commit

Signal: the hand-off's head sha is not on the branch, or the branch does
not exist.

Treat it as an attempt. Brief the worker again with the line "the
previous attempt reported done without a commit; commit first, then
report". Do not accept a description of work as work.

## A validator says BLOCKED

Signal: the app did not start, a dependency was missing, a variable was
unset.

Not an attempt. Fix the environment (start the server, set the variable
from `.env.example`, install the tool), record what was wrong in the
log, and re-run the same validator with the same briefing.

## CI is red after local checks passed

Signal: `ship-gate` reports a failing check.

`ship-gate` handles the first cycle: read the failing job log, one worker
run with the log tail as prior failure, push, wait again. A second red
is an attempt and comes back to the runner. The usual causes are in
`skills/ci-cd-github-actions` section 5: formatter drift, lockfile
mismatch, an environment variable present locally and absent in CI.

## The session dies mid-milestone

Signal: a new runner starts and finds "Current" in the mission file
pointing at a milestone with status `building`.

1. `git log --oneline -20 feature/<slug>` shows what the worker committed
   before dying. That is the truth; the hand-off may not exist.
2. Re-brief the worker with "the branch exists; resume from its log, do
   not restart from scratch". This is `feature-build` step 1.
3. Continue the loop from the step named in "Current".

## The stop rule fires

Finish the running role, commit whatever is on the branch, update the
mission file, write the report, stop. Do not start "one more quick fix".

## Rolling back

A milestone that is `done` but turns out to break something found later:
revert the merge commit on the base branch (`git revert -m 1 <sha>`),
reopen the milestone as `building` with attempts unchanged, and log why.
Never rewrite the base branch's history.
