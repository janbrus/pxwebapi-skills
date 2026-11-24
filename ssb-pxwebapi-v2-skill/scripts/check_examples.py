#!/usr/bin/env python3
"""Validate example URLs/queries in SKILL.md, references/*.md, docs/*.md and
docs/*.txt against the live SSB PxWebApi v2.

docs/ ships outside the zip, but docs/instruks-kort.md is a condensed copy of
SKILL.md and docs/llms.txt a condensed proposal for SSB — checking them here is
what catches the copies going stale.

What is checked:

  - Full URLs matching https://data.ssb.no/api/pxwebapi/v2/...  -> GET, require 200
  - Full Klass URLs (https://data.ssb.no/api/klass/v1/...)      -> GET, require 200
  - Relative GET examples at line start (`GET /tables...`)      -> prepend base, GET, require 200
  - POST examples (`POST /tables/{id}/data` + JSON body)        -> JSON-validate body, then POST, require 200
  - Table IDs referenced in example paths (/tables/NNNNN)       -> /tables/{id} must not be discontinued
  - The code template assets/code/hent_uttrekk.py                -> decoded offline from a made-up
    dataset, then run once with its default selection; see check_template()

The template needs requests and pandas, the rest of this script only the
standard library. Without them the template is skipped with a warning; when
the environment variable CI is set (GitHub Actions), that is an error.

Skipped on purpose:

  - Lines/paths containing `{` placeholders (e.g. /tables/{id}/data) — body is
    still JSON-validated if present
  - POST /savedqueries — NEVER posted (creates persistent state at SSB);
    body is JSON-validated only
  - POST examples without a JSON body (illustrative parameter examples)

JSON bodies are extracted by brace-counting and must not contain braces inside
string values. Identical checks are deduplicated.

Every request, retries and Klass included, takes a slot in a sliding window of
half SSB's limit (scripts/ratewindow.py). The x-ratelimit-policy header of the
responses is compared with the limit the window assumes, at no extra call.

Exit code: 0 if no errors, 1 otherwise.

Usage:  python3 scripts/check_examples.py [--quiet]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from collections.abc import Iterator
from pathlib import Path

from ratewindow import RateWindow

BASE = "https://data.ssb.no/api/pxwebapi/v2"
POLICY = "40;w=60s"  # SSB's x-ratelimit-policy, the limit WINDOW is built from
WINDOW = RateWindow(40, 60)
policies: set[str] = set()  # x-ratelimit-policy values seen in responses
FULL_URL_RE = re.compile(r"https://data\.ssb\.no/api/(?:pxwebapi/v2|klass/v1)/\S+")
VERB_RE = re.compile(r"^\s*(?:\d+\.\s*)?(GET|POST)\s+(/\S+)\s*$")
TABLE_ID_RE = re.compile(r"/tables/(\d{4,6})\b")
TEMPLATE = "assets/code/hent_uttrekk.py"
TEMPLATE_TABLE_RE = re.compile(r'^TABELL = "(\d{4,6})"', re.M)

# A made-up dataset for the offline template check. The keys of category.index
# are deliberately not in position order, as after valueCodes[Tid]=2026,2024,2025,
# and one cell is missing (null with status) while another has a number and a flag.
SYNTHETIC = {
    "id": ["A", "ContentsCode", "Tid"],
    "size": [2, 1, 3],
    "dimension": {
        "A": {"category": {"index": {"y": 1, "x": 0},
                           "label": {"x": "X-tekst", "y": "Y-tekst"}}},
        "ContentsCode": {"category": {"index": {"m": 0}, "label": {"m": "M-tekst"},
                                      "unit": {"m": {"base": "antall", "decimals": 1}}}},
        "Tid": {"category": {"index": {"2026": 0, "2024": 1, "2025": 2},
                             "label": {"2024": "2024", "2025": "2025", "2026": "2026"}}},
    },
    "value": [1, 2, None, 4, 5.5, 6],
    "status": {"2": "..", "4": "*"},
    "note": ["frivillig", "obligatorisk"],
    "role": {"metric": ["ContentsCode"], "time": ["Tid"]},
    "updated": "2026-01-02T07:00:00Z",
    "extension": {"noteMandatory": {"1": True},
                  "px": {"tableid": "00000", "aggregallowed": False}},
}


def encode(url: str) -> str:
    return url.replace("[", "%5B").replace("]", "%5D").replace(" ", "%20")


def strip_trailing(url: str) -> str:
    while url and url[-1] in "`.,;:>\"'":
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
        WINDOW.take()
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.headers.get("x-ratelimit-policy"):
                    policies.add(r.headers["x-ratelimit-policy"])
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


def collect_checks(path: Path) -> Iterator[tuple[int, str, str, str, str | None]]:
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


def load_template(path: Path):
    """Import the code template, without leaving a __pycache__ beside it."""
    spec = importlib.util.spec_from_file_location("hent_uttrekk", path)
    mod = importlib.util.module_from_spec(spec)
    keep = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = keep
    # hent() looks _ta_plass up at call time, so the template's requests take
    # slots in this script's window instead of opening a second one.
    mod._ta_plass = WINDOW.take
    return mod


def template_errors(mod, ds: dict, table: str) -> list[str]:
    """Compare what the template makes of `ds` with values worked out here.

    The template builds its rows in product order. Here the position of each
    row is computed from the row's own codes (category.index × stride, as in
    references/json-stat2.md), so a wrong sort order or a shifted value shows
    as a mismatch instead of the same logic agreeing with itself.
    """
    errs: list[str] = []
    ids = ds["id"]
    index: dict[str, dict[str, int]] = {}
    label: dict[str, dict[str, str]] = {}
    for var in ids:
        cat = ds["dimension"][var]["category"]
        ix = cat["index"]
        index[var] = ix if isinstance(ix, dict) else {c: i for i, c in enumerate(ix)}
        label[var] = cat.get("label", {})
    stride: dict[str, int] = {}
    cells = 1
    for var, n in zip(reversed(ids), reversed(ds["size"])):
        stride[var] = cells
        cells *= n
    status = ds.get("status") or {}
    if isinstance(status, list):
        status = {str(i): s for i, s in enumerate(status) if s is not None}

    rows = mod.til_dataframe(ds).to_dict("records")
    if not len(rows) == len(ds["value"]) == cells:
        return [f"til_dataframe(): {len(rows)} rows, size gives {cells} cells "
                f"and value has {len(ds['value'])}"]
    wrong: list[str] = []
    positions = set()
    for row in rows:
        pos = sum(index[var][row[var]] * stride[var] for var in ids)
        positions.add(pos)
        cell = ", ".join(f"{var}={row[var]}" for var in ids)
        want, got = ds["value"][pos], row["value"]
        if got is None or got != got:  # None or NaN: the cell is missing
            got = None
        if (want is None) != (got is None) or (got is not None and float(got) != float(want)):
            wrong.append(f"value {row['value']!r} at {cell}, value[{pos}] is {want!r}")
        flag = row["status"]
        if flag is None or flag != flag:
            flag = None
        if flag != status.get(str(pos)):
            wrong.append(f"status {row['status']!r} at {cell}, "
                         f"status[{pos}] is {status.get(str(pos))!r}")
        for var in ids:
            if row[f"{var}_tekst"] != label[var].get(row[var], row[var]):
                wrong.append(f"{var}_tekst {row[f'{var}_tekst']!r} for code {row[var]!r}")
    if len(positions) != cells:
        wrong.append(f"the rows cover {len(positions)} of {cells} cells")
    if wrong:
        more = f" (and {len(wrong) - 1} more)" if len(wrong) > 1 else ""
        errs.append(f"til_dataframe(): {wrong[0]}{more}")

    notes = ds.get("note") or []
    mandatory = {int(k) for k, v in
                 ((ds.get("extension") or {}).get("noteMandatory") or {}).items() if v}
    if mod.noter(ds) != [(i in mandatory, text) for i, text in enumerate(notes)]:
        errs.append(f"noter(): got {mod.noter(ds)!r}, noteMandatory marks {sorted(mandatory)} "
                    f"of {len(notes)} note(s)")

    date = ds["updated"][:10]
    for lang, want in (("no", f"Kilde: SSB, tabell {table}. Sist oppdatert: {date}."),
                       ("en", f"Source: Statistics Norway, table {table}. Last updated: {date}.")):
        if mod.kilde(ds, lang) != want:
            errs.append(f"kilde(lang={lang!r}): got {mod.kilde(ds, lang)!r}, expected {want!r}")

    allowed = ds["extension"]["px"].get("aggregallowed", True)
    if mod.kan_summeres(ds) is not bool(allowed):
        errs.append(f"kan_summeres(): got {mod.kan_summeres(ds)!r}, "
                    f"extension.px.aggregallowed is {allowed!r}")

    units = mod.enheter(ds)
    metric = ds["role"]["metric"][0]
    if set(units) != set(index[metric]) or not all(
            "base" in u and "decimals" in u for u in units.values()):
        errs.append(f"enheter(): got {units!r}, expected base and decimals for "
                    f"{sorted(index[metric])}")
    return errs


def check_template(path: Path, quiet: bool) -> tuple[int, bool]:
    """Check the code template. Returns (errors, whether it was run).

    Offline: the made-up dataset, with `status` as an object (what SSB sends)
    and as a list (what the JSON-stat spec also allows). No call is sent, and
    nothing here depends on which cells SSB flags this month.
    Live: one POST with the template's own TABELL and UTVALG, so drift in the
    default codes or in the shape of the response fails the build.
    """
    try:
        mod = load_template(path)
    except ImportError as e:
        why = f"{TEMPLATE} not run: {e} (pip install requests pandas)"
        if os.environ.get("CI"):
            print(f"[ERR] {TEMPLATE}\n    ERROR: {why}")
            return 1, False
        print(f"warning: {why}")
        return 0, False
    except Exception as e:
        print(f"[ERR] {TEMPLATE}\n    ERROR: cannot load: {type(e).__name__}: {e}")
        return 1, False

    def run(what: str, ds: dict, table: str) -> list[str]:
        try:
            return [f"{what}: {e}" for e in template_errors(mod, ds, table)]
        except Exception as e:
            return [f"{what}: {type(e).__name__}: {e}"]

    as_list = [SYNTHETIC["status"].get(str(i)) for i in range(len(SYNTHETIC["value"]))]
    errs = run("offline, status as object", SYNTHETIC, "00000")
    errs += run("offline, status as list", {**SYNTHETIC, "status": as_list}, "00000")
    rows = 0
    try:
        ds = mod.hent(mod.TABELL, mod.UTVALG, mod.KODELISTER, "no")
    except Exception as e:
        errs.append(f"hent(): {type(e).__name__}: {e}")
    else:
        rows = len(ds.get("value") or [])
        errs += run(f"POST /tables/{mod.TABELL}/data", ds, mod.TABELL)

    for e in errs:
        print(f"[ERR] {TEMPLATE}\n    ERROR: {e}")
    if not errs and not quiet:
        print(f"[OK]  {TEMPLATE}  offline decoding, and POST /tables/{mod.TABELL}/data "
              f"with the default selection ({rows} cells)")
    return len(errs), True


def main() -> int:
    ap = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent.parent
    ap.add_argument("--quiet", action="store_true", help="suppress OK lines")
    args = ap.parse_args()

    files = ([here / "SKILL.md"]
             + sorted((here / "references").glob("*.md"))
             + sorted((here / "docs").glob("*.md"))
             + sorted((here / "docs").glob("*.txt")))

    checks: list[tuple[str, int, str, str, str, str | None]] = []
    seen: set[tuple[str, str, str, str | None]] = set()
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

    # The template's default table joins the discontinued check below. It is
    # read from the source text, so that works without requests and pandas too.
    source = (here / TEMPLATE).read_text(encoding="utf-8")
    tm = TEMPLATE_TABLE_RE.search(source)
    if tm:
        table_ids.setdefault(tm.group(1), (TEMPLATE, source[:tm.start()].count("\n") + 1))
    else:
        print(f'[ERR] {TEMPLATE}\n    ERROR: no line of the form TABELL = "12345"')
        errors += 1
    template_errs, template_ran = check_template(here / TEMPLATE, args.quiet)
    errors += template_errs

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

    template = "the code template" if template_ran else "no code template (not run)"
    print(f"\nChecked {len(checks)} example(s), {len(table_ids)} table id(s) and "
          f"{template} — {errors} error(s).")
    print(WINDOW.summary())
    if policies != {POLICY}:
        seen = ", ".join(sorted(policies)) or "missing"
        print(f"warning: x-ratelimit-policy is {seen}, expected {POLICY}: "
              "update RateWindow and references/api-details.md")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
