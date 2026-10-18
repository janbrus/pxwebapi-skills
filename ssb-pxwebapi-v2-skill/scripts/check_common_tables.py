#!/usr/bin/env python3
"""Validate references/common-tables.md against the live SSB PxWebApi v2.

Parses every markdown table row matching `| <id> | <title> | <freq> | ... |`,
fetches `/tables/{id}`, and reports drift on:

  - discontinued        (any True is an error)
  - label               (markdown title vs API label, token-overlap warning)
  - lastPeriod          (warn if stale relative to timeUnit + today)
  - variableNames       (informational, printed on mismatch/error)

Note: the markdown "Frekvens" column describes *publication cadence* (e.g. a
table published quarterly may still have annual time-series data). The API's
`timeUnit` describes the *time dimension granularity* — these are not the same
thing, so we don't equate them. timeUnit drives the staleness check; the only use
of "Frekvens" is a multi-year cadence ("Minst hvert 5. år"), which widens the
allowed lag for annual tables to the cycle plus two years.

Exit code: 0 if no errors, 1 otherwise. Warnings do not fail CI.

Usage:  python3 scripts/check_common_tables.py [--md PATH] [--quiet]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

API = "https://data.ssb.no/api/pxwebapi/v2/tables/{id}?lang=no"

# Rows look like: | 07459 | Title ... | Årlig | ... |
ROW_RE = re.compile(r"^\|\s*(\d{4,6})\s*\|\s*(.+?)\s*\|\s*([^|]+?)\s*\|")

Row = tuple[int, str, str, str]  # (lineno, tid, title, freq)
Result = tuple[str, int, list[str], list[str], dict[str, Any]]  # (tid, lineno, errors, warnings, info)


def parse_md(path: Path) -> list[Row]:
    rows: list[Row] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = ROW_RE.match(line)
        if not m:
            continue
        tid, title, freq = m.group(1), m.group(2).strip(), m.group(3).strip()
        rows.append((lineno, tid, title, freq))
    return rows


def fetch(tid: str, retries: int = 4) -> dict[str, Any]:
    req = urllib.request.Request(
        API.format(id=tid), headers={"Accept": "application/json"}
    )
    delay = 5.0
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data: dict[str, Any] = json.load(r)
                return data
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < retries - 1:
                wait = float(e.headers.get("Retry-After") or delay)
                time.sleep(wait)
                delay *= 2
                continue
            raise
    raise RuntimeError("unreachable")


def staleness_warning(time_unit: str, last_period: str, md_freq: str = "") -> str | None:
    """Return a warning string if lastPeriod looks unexpectedly old."""
    today = dt.date.today()
    try:
        if time_unit == "Annual":
            year = int(last_period)
            # Frekvens «Minst hvert 5. år» (Forbruksundersøkelsen 14100): allow the cycle plus two years
            cycle = re.search(r"hvert (\d+)\. år", md_freq)
            allowed = int(cycle.group(1)) + 2 if cycle else 2
            if today.year - year > allowed:
                return f"lastPeriod={last_period} is >{allowed} years behind {today.year}"
        elif time_unit == "Monthly" and "M" in last_period:
            y, m = last_period.split("M")
            ref = dt.date(int(y), int(m), 1)
            months = (today.year - ref.year) * 12 + (today.month - ref.month)
            if months > 4:
                return f"lastPeriod={last_period} is {months} months behind today"
        elif time_unit == "Quarterly" and "K" in last_period:
            y, q = last_period.split("K")
            ref_month = (int(q) - 1) * 3 + 1
            ref = dt.date(int(y), ref_month, 1)
            months = (today.year - ref.year) * 12 + (today.month - ref.month)
            if months > 8:
                return f"lastPeriod={last_period} is {months} months behind today"
        elif time_unit == "Weekly" and "U" in last_period:
            y, w = last_period.split("U")
            # Approximate: ISO week to date
            ref = dt.date.fromisocalendar(int(y), int(w), 1)
            days = (today - ref).days
            if days > 60:
                return f"lastPeriod={last_period} is {days} days behind today"
    except (ValueError, KeyError):
        return f"could not parse lastPeriod={last_period!r} for timeUnit={time_unit}"
    return None


def check_row(lineno: int, tid: str, md_title: str, md_freq: str) -> Result:
    errors: list[str] = []
    warnings: list[str] = []
    info: dict[str, Any] = {}
    try:
        data = fetch(tid)
    except urllib.error.HTTPError as e:
        return tid, lineno, [f"HTTP {e.code} fetching /tables/{tid}"], [], {}
    except Exception as e:
        return tid, lineno, [f"fetch failed: {e}"], [], {}

    label = data.get("label", "")
    time_unit = data.get("timeUnit", "")
    last_period = data.get("lastPeriod", "")
    var_names = data.get("variableNames", [])
    discontinued = data.get("discontinued", False)

    info["label"] = label
    info["timeUnit"] = time_unit
    info["lastPeriod"] = last_period
    info["variableNames"] = var_names
    info["discontinued"] = discontinued

    if discontinued:
        errors.append("discontinued=true in API but listed in common-tables.md")

    # Label/title: token-overlap check (markdown is often a shortened title)
    md_norm = re.sub(r"\s+", " ", md_title.lower())
    label_norm = re.sub(r"\s+", " ", label.lower())
    md_tokens = {t for t in re.findall(r"\w{4,}", md_norm, flags=re.UNICODE)}
    label_tokens = set(re.findall(r"\w{4,}", label_norm, flags=re.UNICODE))
    if md_tokens and len(md_tokens & label_tokens) / len(md_tokens) < 0.4:
        warnings.append(f"title drift: md={md_title!r} api={label!r}")

    stale = staleness_warning(time_unit, last_period, md_freq)
    if stale:
        warnings.append(stale)

    return tid, lineno, errors, warnings, info


def main() -> int:
    ap = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent.parent
    ap.add_argument("--md", default=str(here / "references" / "common-tables.md"))
    ap.add_argument("--quiet", action="store_true", help="suppress OK lines")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--delay", type=float, default=0.5,
                    help="seconds to sleep between sequential requests")
    args = ap.parse_args()

    md_path = Path(args.md)
    rows = parse_md(md_path)
    if not rows:
        print(f"No table rows parsed from {md_path}", file=sys.stderr)
        return 2

    total_errors = 0
    total_warnings = 0
    results: list[Result] = []
    if args.workers <= 1:
        for r in rows:
            results.append(check_row(*r))
            if args.delay:
                time.sleep(args.delay)
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = [ex.submit(check_row, *r) for r in rows]
            for f in as_completed(futures):
                results.append(f.result())

    results.sort(key=lambda x: x[1])  # by lineno
    for tid, lineno, errs, warns, info in results:
        status = "ERR" if errs else ("WARN" if warns else "OK")
        if status == "OK" and args.quiet:
            continue
        print(f"[{status}] {tid} (line {lineno})  {info.get('label','')}")
        for e in errs:
            print(f"    ERROR:   {e}")
            total_errors += 1
        for w in warns:
            print(f"    warning: {w}")
            total_warnings += 1
        if errs or warns:
            print(f"    variableNames={info.get('variableNames')}")

    print(
        f"\nChecked {len(rows)} tables — {total_errors} error(s), "
        f"{total_warnings} warning(s)."
    )
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
