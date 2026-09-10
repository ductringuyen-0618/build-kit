#!/usr/bin/env python3
"""Generic HTTP smoke checks. Standard library only, one file, any stack.

    python smoke.py --base-url http://127.0.0.1:8000 "GET /health 200 healthy"
    python smoke.py --base-url https://app.example.com --checks smoke.json
    python smoke.py --base-url URL --checks smoke.json --json > report.json

A check on the command line is one quoted string:
    METHOD PATH STATUS [JSON_BODY] [SUBSTRING]
    "GET /health 200 healthy"
    'POST /api/items/ 201 {"name":"a"} a'
    "GET /api/items/does-not-exist 404 not found"

A checks file is a JSON list of objects with the same fields, plus an
optional name and headers:
    [{"name": "health", "method": "GET", "path": "/health", "status": 200,
      "contains": "healthy"},
     {"method": "POST", "path": "/api/items/", "status": 201,
      "body": {"name": "a"}, "contains": "name"}]

Exit codes: 0 every check passed, 1 at least one failed, 2 the base URL
never answered (every check was a connection error).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request


def parse_cli_check(text: str) -> dict:
    """METHOD PATH STATUS [JSON_BODY] [SUBSTRING]; the substring may contain spaces."""
    parts = text.strip().split(None, 3)
    if len(parts) < 3:
        raise SystemExit(f"bad check (need METHOD PATH STATUS): {text!r}")
    check = {"method": parts[0].upper(), "path": parts[1], "status": int(parts[2])}
    rest = parts[3].strip() if len(parts) == 4 else ""
    if rest and rest[0] in "{[":
        check["body"], end = json.JSONDecoder().raw_decode(rest)
        rest = rest[end:].strip()
    if rest:
        check["contains"] = rest
    return check


def run_check(base: str, check: dict, timeout: float) -> dict:
    method = check.get("method", "GET").upper()
    url = base.rstrip("/") + "/" + check["path"].lstrip("/")
    data = None
    headers = {"Accept": "application/json, text/html;q=0.9, */*;q=0.8"}
    headers.update(check.get("headers") or {})
    if check.get("body") is not None:
        body = check["body"]
        data = (body if isinstance(body, str) else json.dumps(body)).encode()
        headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    started = time.monotonic()
    status, text, error = None, "", None
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status, text = resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:  # a 4xx/5xx is still an answer
        status, text = exc.code, exc.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as exc:
        error = f"connection error: {getattr(exc, 'reason', exc)}"
    ms = int((time.monotonic() - started) * 1000)
    problems = []
    if error:
        problems.append(error)
    else:
        want = int(check.get("status", 200))
        if status != want:
            problems.append(f"expected status {want}, got {status}")
        needle = check.get("contains")
        if needle and needle not in text:
            problems.append(f"body does not contain {needle!r}")
    return {
        "name": check.get("name") or f"{method} {check['path']}",
        "passed": not problems,
        "status": status,
        "ms": ms,
        "detail": "; ".join(problems),
        "snippet": text[:200].replace("\n", " "),
        "connection_error": error is not None,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--checks", help="JSON file with a list of checks")
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--json", action="store_true", help="print a JSON report instead of lines")
    ap.add_argument("check", nargs="*", help='inline checks: "GET /health 200 healthy"')
    args = ap.parse_args(argv)

    checks: list[dict] = []
    if args.checks:
        with open(args.checks, encoding="utf-8") as fh:
            checks.extend(json.load(fh))
    checks.extend(parse_cli_check(c) for c in args.check)
    if not checks:
        checks.append({"name": "health", "method": "GET", "path": "/health", "status": 200})

    results = [run_check(args.base_url, c, args.timeout) for c in checks]
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed
    unreachable = all(r["connection_error"] for r in results)

    if args.json:
        report = {"base_url": args.base_url, "passed": passed, "failed": failed, "results": results}
        print(json.dumps(report, indent=2))
    else:
        for r in results:
            line = f"{'PASS' if r['passed'] else 'FAIL'}  {r['name']}  status={r['status']}  {r['ms']}ms"
            if r["detail"]:
                line += f"  ({r['detail']})"
            print(line)
            if not r["passed"] and r["snippet"]:
                print(f"      body: {r['snippet']}")
        print(f"\n{passed} passed, {failed} failed, {len(results)} total against {args.base_url}")
    return 2 if unreachable else (1 if failed else 0)


if __name__ == "__main__":
    sys.exit(main())
