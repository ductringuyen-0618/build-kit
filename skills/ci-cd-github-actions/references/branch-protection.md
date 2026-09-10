# Branch protection: rulesets alternative and verification

Companion to step 5 in `SKILL.md`. The classic branch-protection endpoint
there is the shortest path. This file covers the newer rulesets API,
which needs no nullable placeholders and can target the default branch
by name, plus how to verify and undo either.

## Rulesets

```
gh api -X POST repos/OWNER/REPO/rulesets --input - <<'EOF'
{
  "name": "main-ci",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "required_status_checks",
      "parameters": { "strict_required_status_checks_policy": true,
                      "required_status_checks": [
                        { "context": "Backend" },
                        { "context": "Frontend" },
                        { "context": "Secret scan" } ] } },
    { "type": "deletion" },
    { "type": "non_fast_forward" }
  ]
}
EOF
```

- `~DEFAULT_BRANCH` resolves to whatever the default branch is, so the
  command does not change when the branch is called `master` or `trunk`.
- `deletion` and `non_fast_forward` have no parameters; they block
  deleting the branch and force-pushing to it.
- `context` strings are the job `name:` values from the CI workflow
  (job ids when no name is set). A typo here produces a check that
  never reports and a merge button that never unlocks.
- Repository admins bypass a ruleset only if listed in `bypass_actors`;
  the default is no bypass, which is stricter than
  `enforce_admins: false` on the classic endpoint.

List and delete:

```
gh api repos/OWNER/REPO/rulesets --jq '.[] | {id, name, enforcement}'
gh api -X DELETE repos/OWNER/REPO/rulesets/<id>
```

## Classic endpoint: verify and remove

```
gh api repos/OWNER/REPO/branches/main/protection --jq .required_status_checks
gh api -X DELETE repos/OWNER/REPO/branches/main/protection
```

## Delete branch on merge

Either form works; `-F` sends a JSON boolean where `-f` would send the
string `"true"`:

```
gh repo edit OWNER/REPO --delete-branch-on-merge
gh api -X PATCH repos/OWNER/REPO -F delete_branch_on_merge=true
```

## Proving the protection works

1. On a branch, make a test fail on purpose and push. `gh pr checks
   <n> --watch` should end red, and the PR page should show the merge
   button disabled with the failing check named.
2. Revert, push, and watch it turn green.
3. Keep the two run URLs; they are the evidence that the gate is real.
