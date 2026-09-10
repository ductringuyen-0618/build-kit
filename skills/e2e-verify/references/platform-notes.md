# Platform notes: ports, background processes, cleanup

The steps in `SKILL.md` use bash. Equivalents for Windows PowerShell and
the checks that differ by OS.

## Who owns a port

```bash
# macOS / Linux
lsof -i :PORT -sTCP:LISTEN
# or
ss -ltnp | grep :PORT
```

```powershell
# Windows
Get-NetTCPConnection -LocalPort PORT -State Listen |
  Select-Object OwningProcess, @{n='Name';e={(Get-Process -Id $_.OwningProcess).ProcessName}}
```

If the owner is not a process you started, do not kill it. Choose a
different port and pass it to the app and to the tests.

## Start in the background and keep the PID

```bash
(npm run dev > /tmp/e2e-web.log 2>&1 & echo $! > /tmp/e2e-web.pid)
```

```powershell
$web = Start-Process -FilePath npm -ArgumentList 'run','dev' `
  -RedirectStandardOutput "$env:TEMP\e2e-web.log" `
  -RedirectStandardError  "$env:TEMP\e2e-web.err" -PassThru
$web.Id | Out-File "$env:TEMP\e2e-web.pid"
```

Agent tools that offer a "run in background" option are fine too; still
record the PID from the log or from the port owner.

## Readiness probe

```bash
for i in $(seq 1 60); do curl -sf -o /dev/null http://localhost:PORT/ && break; sleep 1; done
```

```powershell
$ok = $false
1..60 | ForEach-Object {
  if (-not $ok) {
    try { Invoke-WebRequest http://localhost:PORT/ -UseBasicParsing -TimeoutSec 2 | Out-Null; $ok = $true }
    catch { Start-Sleep 1 }
  }
}
if (-not $ok) { throw "app did not answer on PORT" }
```

## Stop only what you started

```bash
kill "$(cat /tmp/e2e-web.pid)"
```

```powershell
Stop-Process -Id (Get-Content "$env:TEMP\e2e-web.pid") -ErrorAction SilentlyContinue
```

Never `pkill node` or `Stop-Process -Name python`. Other work on the
machine uses the same runtimes.

## Throwaway data

Prefer env vars the app already reads (`DATABASE_URL`, a data directory
setting) pointed at a temp path. Delete the temp path at teardown.
Check that every process of the app reads the same setting; a frontend
proxy, a worker, and an API that each default differently will disagree
about where data lives.

## Python virtual environments

A committed or stale virtualenv whose interpreter path no longer exists
fails every command with "did not find executable". Create a fresh one
at a short path (long paths break some native wheels on Windows) and
install only what the app needs to boot for this run.

## Playwright on Windows

Run `npx playwright install chromium` once per machine. Use forward
slashes or quoted paths in config. Screenshot baselines carry the
platform in their file name and will not match across OSes.
