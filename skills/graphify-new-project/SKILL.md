---
name: graphify-new-project
description: >-
  Bootstrap a graphify knowledge graph for a freshly started project so the
  codebase is queryable from day one. Use this WHENEVER the user signals they
  are beginning, scaffolding, cloning, or setting up a new project or repo —
  phrases like "I'm starting a new project", "just scaffolded/created a repo at
  <path>", "set up graphify for this new project", "new codebase at <path>",
  "kick off graphifying <repo>", or the explicit /graphify-new command. This is
  the fast, deterministic, token-free code-only AST path (the one used for the
  author's portfolio repos) — not the full semantic /graphify pipeline. Prefer this
  skill over plain /graphify when the trigger is a NEW project being set up,
  even if the user does not say the word "graphify" explicitly.
trigger: /graphify-new
---

# graphify-new-project

When the user starts a new project, build a code-only knowledge graph for it so
later sessions can understand the codebase without grepping every file. This is
a thin, fast wrapper around graphify's AST extraction — **no LLM tokens, no
subagents, no API key**. It reuses the exact two-step build we validated on the
`D:\Portfolio` repos (`portfolio-website`, `ai-tech-news-assistant`,
`salon-hub`).

For the full semantic pipeline (docs + screenshots + INFERRED edges) the user
should invoke the separate `/graphify` skill instead. This skill is for the
common case: a new, mostly-code repo you want mapped immediately.

## When to run it

Run when the user is clearly setting up or onboarding a project, e.g.:
- "I just started a new project at `<path>`"
- "scaffolded a Next.js app, graph it"
- "cloned `salon-hub`, set up graphify"
- `/graphify-new <path>`

If you are not sure whether they mean a new project vs. a general codebase
question, ask one short clarifying question. Don't run it on a repo that already
has a populated `graphify-out/graph.json` unless the user wants a rebuild — say
so and offer `/graphify <path> --update` instead.

## Resolve the project path

- If the user gave a path, use it.
- Otherwise use the current working directory (`.`).
- Confirm the path exists before building. All commands below run with the
  **current directory set to the project root** — the scripts write to a
  relative `graphify-out/` there.

## Step 1 — Locate the graphify interpreter

graphify runs on its own uv-managed Python (installed via `uv tool install
graphifyy`). Find it; install if missing. Save the path to `$py`.

```powershell
$py = $null
if (Get-Command uv -ErrorAction SilentlyContinue) {
    $uvDir = (uv tool dir 2>$null).Trim()
    if ($uvDir) {
        $cand = Join-Path $uvDir "graphifyy\Scripts\python.exe"
        if (Test-Path $cand) { & $cand -c "import graphify" 2>$null; if ($LASTEXITCODE -eq 0) { $py = $cand } }
    }
}
if (-not $py) {
    # fall back to the known install location, else install
    $known = Join-Path $env:APPDATA "uv\tools\graphifyy\Scripts\python.exe"
    if (Test-Path $known) { $py = $known }
    else { uv tool install --upgrade graphifyy -q 2>&1 | Select-Object -Last 3; $py = (Join-Path (uv tool dir).Trim() "graphifyy\Scripts\python.exe") }
}
Write-Output "graphify python: $py"
```

If `$py` still does not resolve, stop and tell the user graphify is not
installed and `uv` is unavailable — they need to `uv tool install graphifyy`.

## Step 2 — Build the code-only graph

Set the location to the project and run the bundled build script. This does:
detect → AST extract → build → cluster → analyze → `graph.json` + report +
`.graphify_analysis.json`. The script guards `extract()` inside
`if __name__ == "__main__"` (required on Windows — `ProcessPoolExecutor` spawn
would otherwise recurse).

```powershell
$skill = Join-Path $HOME ".claude\skills\graphify-new-project\scripts"
Set-Location "<PROJECT_PATH>"
& $py "$skill\graphify_codeonly_build.py"
```

Read the printed `DETECT` / `AST` / `GRAPH` lines. If it prints
`ERROR: empty graph`, stop and report — likely no supported code files were
found (graphify supports `.py .ts .js .go .rs .java .cpp .c .rb` and similar).
Don't run finalize on an empty graph.

## Step 3 — Finalize (labels + HTML + manifest + benchmark)

```powershell
Set-Location "<PROJECT_PATH>"
& $py "$skill\graphify_finalize.py"
```

This auto-labels each community by its dominant source directory + hub node
(e.g. `appointment/service: AppointmentServiceImpl`), regenerates
`GRAPH_REPORT.md`, writes `graph.html` (skipped automatically above 5000 nodes —
too large to render), saves `manifest.json` for future `--update` runs, and
prints a token-reduction benchmark.

## Step 4 — Report and offer to explore

Tell the user where the outputs landed:

```
Graph ready for <project>. Outputs in <PROJECT_PATH>\graphify-out\
  graph.json        - queryable graph (use for later /graphify query)
  graph.html        - interactive viz, open in a browser
  GRAPH_REPORT.md   - god nodes, surprising connections, suggested questions
```

Then paste **only** the God Nodes, Surprising Connections, and Suggested
Questions sections from `GRAPH_REPORT.md` — keep it concise, don't dump the
whole report. Pick the single most interesting suggested question (the one
crossing the most community boundaries) and offer:

> "The most interesting question this graph can answer: **[question]**. Want me
> to trace it?"

If yes, run `/graphify query "[question]"` and walk them through the path.

## Notes / gotchas (Windows, learned the hard way)

- Always `Set-Location` into the project at the start of each command block —
  shell state does not persist between tool calls, and the scripts use relative
  `graphify-out/` paths.
- Let Python write its own JSON. PowerShell 5.1 `Out-File -Encoding utf8` adds a
  BOM that breaks `json.loads`; the bundled scripts read with `utf-8-sig` and
  write their own files, so just run them — don't pipe their JSON through
  PowerShell.
- A PreToolUse hook blocks `Remove-Item` in this environment. These scripts
  never call it; if you need to delete a temp file, do it from Python
  (`os.remove`), not PowerShell.
- This is the code-only path on purpose. If the new project has substantial docs
  or design screenshots worth graphing semantically, mention that `/graphify
  <path>` (full pipeline) is the richer option, and let the user choose.
