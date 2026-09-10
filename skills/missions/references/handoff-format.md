# Hand-off format

Every role ends with a message in a fixed shape so the runner can read it
mechanically. The first line is the part a script or a tired human reads;
everything after it is evidence.

## Worker

```
## Worker hand-off: <slug>, attempt <n>
- branch: req/<slug>
- head: <sha>
- commits:
  - <sha> <message>
- files changed: <list>
- contract items addressed: <assertion>: done | not done (<why>)
- checks run locally: <command> -> exit <code>
- known gaps: <list or "none">
```

Required: every line. The runner verifies `head` with `git rev-parse
req/<slug>`; a mismatch is a failed hand-off.

## Scrutiny validator

```
PASS | FAIL
### <command>
exit code: <n>
<last 40 lines, scrubbed of paths, tokens, emails>
### Contract
- <assertion>: proven by <test or file:line> | NOT PROVEN, <reason>
### Out of contract
- <file>: <unrequested change>
### Fixes I applied
- <sha> <what>
```

The first line must be exactly `PASS` or `FAIL`. agent-os reads the
first line that is exactly one of those two words, so a validator that
narrates before the verdict is still parsed, but do not rely on it.

## User-testing validator

```
PASS | FAIL | BLOCKED
### Environment
url: <url>   started by me: yes/no   vehicle: <browser|curl|smoke.py|playwright>
### Assertions
- <assertion>: PASS | FAIL. did: <action>. expected: <x>. observed: <y>.
### Negative cases
- <case>: status <n>, body <first line>
### Regressions
- <existing behaviour>: PASS | FAIL
### Reproductions for each FAIL
<curl command or click sequence>
```

## Ship (from `skills/ship-gate`)

```
## Shipped: <slug>
- branch: req/<slug>   pr: <url>   merged: yes/no
- ci: <check name>: pass | fail | skipped   run: <url>
- commits: <sha> <message> ...
- validator findings: <verbatim first lines plus fixes applied>
- reviewer notes: <verbatim>
- left undone: <list or "none">
```

## What the runner does with them

- Copies the first line of each into the mission log with a timestamp.
- Feeds a `FAIL` body verbatim into the next worker briefing as the
  prior failure. Do not paraphrase; paraphrase loses the line numbers.
- Never edits a hand-off. If it is wrong, the role that wrote it runs
  again.
