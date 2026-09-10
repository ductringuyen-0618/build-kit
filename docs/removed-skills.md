# Removed skills

Skills that were in earlier versions of this kit but could not run outside
the runtime or tool they were written for. Each line says where the
original lives now and what, if anything, replaced it here.

| Skill | Why removed | Where it lives / replacement |
| --- | --- | --- |
| `heartbeat` | Scheduled pulse-check over agent-os routines and its wiki; depends on the daemon's task payload and syscalls. | https://github.com/ductringuyen-0618/agent-os |
| `ingest` | Folds a `raw/` file into the agent-os wiki via `remember`; no meaning without that wiki. | https://github.com/ductringuyen-0618/agent-os |
| `lint` | Nightly wiki hygiene routine (contradictions, orphans, stale pages) for agent-os. | https://github.com/ductringuyen-0618/agent-os |
| `query` | Answers a question from the agent-os wiki alone, citing pages. | https://github.com/ductringuyen-0618/agent-os |
| `daily-digest` | Writes the day's digest from the agent-os wiki log and run history. | https://github.com/ductringuyen-0618/agent-os |
| `coo-ideate` | Daily agent-os routine that proposed one feature per project through the daemon's approval workflow. | Generalised as `skills/propose-feature` (one well-argued next feature for any repo, no runtime needed). |
| `graphify-new-project` | Thin PowerShell wrapper around the graphify tool with two bundled scripts; only useful with that tool installed. | Tool: https://github.com/safishamsi/graphify (`uv tool install graphifyy`). Replaced by `skills/codebase-map` (build a mental map of an unfamiliar repo in ten minutes, no tools required). |
