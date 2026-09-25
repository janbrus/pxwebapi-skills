#!/usr/bin/env python3
"""Validate example URLs/queries in SKILL.md, references/*.md and docs/*.md
against the live SSB PxWebApi v2.

docs/ ships outside the zip, but docs/instruks-kort.md is a condensed copy of
SKILL.md — checking it here is what catches the copy going stale.

What is checked:

  - Full URLs matching https://data.ssb.no/api/pxwebapi/v2/...  -> GET, require 200
  - Relative GET examples at line start (`GET /tables...`)      -> prepend base, GET, require 200
  - POST examples (`POST /tables/{id}/data` + JSON body)        -> JSON-validate body, then POST, require 200
  - Table IDs referenced in example paths (/tables/NNNNN)       -> /tables/{id} must not be discontinued

Skipped on purpose:

  - Lines/paths containing `{` placeholders (e.g. /tables/{id}/data) — body is
    still JSON-validated if present
  - POST /savedqueries — NEVER posted (creates persistent state at SSB);
    body is JSON-validated only
  - POST examples without a JSON body (illustrative parameter examples)
  - Klass URLs (data.ssb.no/api/klass/...) — different API, out of scope

JSON bodies are extracted by brace-counting and must not contain braces inside
string values. Identical checks are deduplicated.

Exit code: 0 if no errors, 1 otherwise.

Usage:  python3 scripts/check_examples.py [--quiet] [--delay SECONDS]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE = "https://data.ssb.no/api/pxwebapi/v2"
FULL_URL_RE = re.compile(r"https://data\.ssb\.no/api/pxwebapi/v2/\S+")
VERB_RE = re.compile(r"^\s*(?:\d+\.\s*)?(GET|POST)\s+(/\S+)\s*$")
TABLE_ID_RE = re.compile(r"/tables/(\d{4,6})\b")


def encode(url: str) -> str:
    return url.replace("[", "%5B").replace("]", "%5D").replace(" ", "%20")


def strip_trailing(url: str) -> str:
    while url and url[-1] in "`.,;>\"'":
        url = url[:-1]
    # A trailing ')' is junk only if parentheses are unbalanced (top(5) is valid)
    while url.endswith(")") and url.count("(") < url.count(")"):
        url = url[:-1]
    return url


def http(url: str, method: str = "GET", body: str | None = None,
         retries: int = 4) -> tuple[int, bytes]:
    headers = {"Accept": "application/json"}
    data = None
    if body is not None:
        data = body.encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(encode(url), data=data, headers=headers,
                                 method=method)
    delay = 5.0
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < retries - 1:
                wait = float(e.headers.get("Retry-After") or delay)
                time.sleep(wait)
                delay *= 2
                continue
            return e.code, e.read()
    raise RuntimeError("unreachable")


def extract_json_body(lines: list[str], start: int) -> tuple[str | None, int]:
    """Collect a JSON object starting at/after `start` by brace counting.

    Skips blank lines and a Content-Type header before the body. Returns
    (body, next_line_index); body is None if no JSON object follows.
    """
    j = start
    while j < len(lines) and (
        not lines[j].strip() or lines[j].strip().lower().startswith("content-type:")
    ):
        j += 1
    if j >= len(lines) or not lines[j].lstrip().startswith("{"):
        return None, start
    depth = 0
    collected: list[str] = []
    while j < len(lines):
        line = lines[j]
        if line.strip().startswith("```"):
            return None, start  # fence closed before braces balanced
        collected.append(line)
        depth += line.count("{") - line.count("}")
        j += 1
        if depth == 0:
            return "\n".join(collected), j
    return None, start


def collect_checks(path: Path):
    """Yield (lineno, kind, method, url, body) checks for one file.

    kind: 'http' (perform request) or 'json' (validate body syntax only).
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        for m in FULL_URL_RE.finditer(line):
            url = strip_trailing(m.group(0))
            if "{" not in url:
                yield i + 1, "http", "GET", url, None

        vm = VERB_RE.match(line)
        if not vm:
            i += 1
            continue
        verb, rel_path = vm.group(1), strip_trailing(vm.group(2))

        if verb == "GET":
            if "{" not in rel_path:
                yield i + 1, "http", "GET", BASE + rel_path, None
            i += 1
            continue

        # POST: try to pick up a JSON body on the following lines
        body, nxt = extract_json_body(lines, i + 1)
        if body is None:
            i += 1  # illustrative POST without body — nothing to run
            continue
        if "{" in rel_path or rel_path.startswith("/savedqueries"):
            yield i + 1, "json", "POST", BASE + rel_path, body
        else:
            yield i + 1, "http", "POST", BASE + rel_path, body
        i = nxt


def main() -> int:
    ap = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent.parent
    ap.add_argument("--quiet", action="store_true", help="suppress OK lines")
    ap.add_argument("--delay", type=float, default=0.5,
                    help="seconds to sleep between requests")
    args = ap.parse_args()

    files = ([here / "SKILL.md"]
             + sorted((here / "references").glob("*.md"))
             + sorted((here / "docs").glob("*.md")))

    checks = []
    seen = set()
    for f in files:
        for lineno, kind, method, url, body in collect_checks(f):
            key = (kind, method, url, body)
            if key in seen:
                continue
            seen.add(key)
            checks.append((f.name, lineno, kind, method, url, body))

    errors = 0
    table_ids: dict[str, tuple[str, int]] = {}
    for fname, lineno, kind, method, url, body in checks:
        where = f"{fname}:{lineno}"
        for tid in TABLE_ID_RE.findall(url):
            table_ids.setdefault(tid, (fname, lineno))

        if body is not None:
            try:
                json.loads(body)
            except json.JSONDecodeError as e:
                print(f"[ERR] {where}  {method} {url}\n    ERROR: invalid JSON body: {e}")
                errors += 1
                continue

        if kind == "json":
            if not args.quiet:
                print(f"[OK]  {where}  {method} {url} (JSON syntax only)")
            continue

        try:
            status, _ = http(url, method=method, body=body)
        except Exception as e:
            print(f"[ERR] {where}  {method} {url}\n    ERROR: request failed: {e}")
            errors += 1
            continue
        if status != 200:
            print(f"[ERR] {where}  {method} {url}\n    ERROR: HTTP {status}")
            errors += 1
        elif not args.quiet:
            print(f"[OK]  {where}  {method} {url}")
        if args.delay:
            time.sleep(args.delay)

    for tid, (fname, lineno) in sorted(table_ids.items()):
        status, payload = http(f"{BASE}/tables/{tid}?lang=no")
        if status != 200:
            print(f"[ERR] {fname}:{lineno}  table {tid}\n    ERROR: HTTP {status} from /tables/{tid}")
            errors += 1
            continue
        if json.loads(payload).get("discontinued"):
            print(f"[ERR] {fname}:{lineno}  table {tid}\n    ERROR: discontinued=true — replace this example table")
            errors += 1
        elif not args.quiet:
            print(f"[OK]  table {tid} exists, not discontinued")
        if args.delay:
            time.sleep(args.delay)

    print(f"\nChecked {len(checks)} example(s) and {len(table_ids)} table id(s) — {errors} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
