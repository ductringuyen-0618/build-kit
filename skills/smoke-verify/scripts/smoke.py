#!/usr/bin/env python3
"""HTTP smoke checks against a running service. Standard library only.

    python smoke.py --base-url http://127.0.0.1:PORT "GET /health 200 healthy"
    python smoke.py --base-url https://app.example.com --checks smoke.json [--json]

Inline check: METHOD PATH STATUS [JSON_BODY] [SUBSTRING]
    "GET /health 200 healthy"    'POST /api/items/ 201 {"name":"a"} a'
Checks file: JSON list of {"name", "method", "path", "status", "body", "contains", "headers"}.
Exit 0 all passed, 1 any failed, 2 nothing answered (connection errors only).
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request


def parse_inline(text):
    parts = text.strip().split(None, 3)
    if len(parts) < 3:
        sys.exit(f"bad check, need METHOD PATH STATUS: {text!r}")
    check = {"method": parts[0].upper(), "path": parts[1], "status": int(parts[2])}
    rest = parts[3].strip() if len(parts) == 4 else ""
    if rest and rest[0] in "{[":
        check["body"], end = json.JSONDecoder().raw_decode(rest)
        rest = rest[end:].strip()
    if rest:
        check["contains"] = rest
    return check


def run(base, check, timeout):
    url = base.rstrip("/") + "/" + check["path"].lstrip("/")
    headers = {"Accept": "application/json, text/html;q=0.9, */*;q=0.8", **(check.get("headers") or {})}
    data = None
    if check.get("body") is not None:
        body = check["body"]
        data = (body if isinstance(body, str) else json.dumps(body)).encode()
        headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, method=check.get("method", "GET").upper(), headers=headers)
    started, status, text, error = time.monotonic(), None, "", None
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status, text = resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:  # a 4xx/5xx is still an answer
        status, text = exc.code, exc.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as exc:
        error = f"connection error: {getattr(exc, 'reason', exc)}"
    problems = [error] if error else []
    want, needle = int(check.get("status", 200)), check.get("contains")
    if not error and status != want:
        problems.append(f"expected status {want}, got {status}")
    if not error and needle and needle not in text:
        problems.append(f"body does not contain {needle!r}")
    return {"name": check.get("name") or f"{req.get_method()} {check['path']}", "passed": not problems,
            "status": status, "ms": int((time.monotonic() - started) * 1000),
            "detail": "; ".join(problems), "snippet": text[:200].replace("\n", " "),
            "connection_error": error is not None}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--checks", help="JSON file with a list of checks")
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--json", action="store_true", help="print a JSON report")
    ap.add_argument("check", nargs="*", help='inline checks, e.g. "GET /health 200 healthy"')
    args = ap.parse_args()
    checks = []
    if args.checks:
        with open(args.checks, encoding="utf-8") as fh:
            checks += json.load(fh)
    checks += [parse_inline(c) for c in args.check]
    checks = checks or [{"name": "health", "method": "GET", "path": "/health", "status": 200}]

    results = [run(args.base_url, c, args.timeout) for c in checks]
    passed = sum(r["passed"] for r in results)
    failed = len(results) - passed
    if args.json:
        print(json.dumps({"base_url": args.base_url, "passed": passed, "failed": failed, "results": results}, indent=2))
    else:
        for r in results:
            print(f"{'PASS' if r['passed'] else 'FAIL'}  {r['name']}  status={r['status']}  {r['ms']}ms"
                  + (f"  ({r['detail']})" if r["detail"] else ""))
            if not r["passed"] and r["snippet"]:
                print(f"      body: {r['snippet']}")
        print(f"\n{passed} passed, {failed} failed, {len(results)} total against {args.base_url}")
    return 2 if all(r["connection_error"] for r in results) else (1 if failed else 0)


if __name__ == "__main__":
    sys.exit(main())
