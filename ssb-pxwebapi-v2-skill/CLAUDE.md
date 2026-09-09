# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is **not** an application codebase. It is a Claude Code **Skill** package that teaches Claude how to query Statistics Norway (SSB) via the public PxWebApi v2 at `https://data.ssb.no/api/pxwebapi/v2`. There is no application runtime — changes here are documentation/prompt edits that get loaded when the `ssb-pxwebapi-v2` skill triggers.

There *is* a build step and a test suite, but they are unusual: `scripts/build_zip.sh` packages the distributable, and the Python checkers under `scripts/` treat every example URL, POST body and table ID written in the markdown as an assertion to verify against the **live** SSB API. Prose is the fixture set; drift upstream at SSB fails the build.

Upstream source of truth: https://github.com/janbrus/ssb-api-v2-examples/tree/main/ssb-pxwebapi-v2-skill

## Commands

Requires Python 3.12+ (stdlib only — no dependencies) and `zip`/`unzip`.

```bash
# Verify every example URL, GET/POST query and table ID in SKILL.md + references/
python3 scripts/check_examples.py            # add --quiet to hide OK lines
python3 scripts/check_examples.py --delay 1.0   # slower; use when rate-limited (429)

# Verify references/common-tables.md rows against /tables/{id}
python3 scripts/check_common_tables.py --quiet --delay 1.0
python3 scripts/check_common_tables.py --md references/common-tables.md   # check a single file
python3 scripts/check_common_tables.py --workers 4                        # parallel; ignores --delay

# Rebuild the distribution zip (required before committing content changes)
scripts/build_zip.sh                  # writes ./ssb-pxwebapi-v2-skill.zip
scripts/build_zip.sh /tmp/fresh.zip   # write elsewhere, e.g. to diff against the committed zip
```

There is no single-test flag; scope a run by pointing `check_common_tables.py --md` at one file, or by narrowing `--delay`/`--quiet` for a faster full pass. Both checkers exit non-zero on errors; `check_common_tables.py` warnings (title drift, stale `lastPeriod`) do **not** fail CI.

`.github/workflows/check-tables.yaml` runs two jobs — `check` (both Python scripts) and `zip-sync` (rebuilds the zip and `diff -r`s it against the committed one) — on push/PR touching `SKILL.md`, `references/**`, `scripts/**` or the zip, plus a **Monday 06:00 UTC cron** that catches SSB-side drift with no local change.

### The `/savedqueries` safety rule

`check_examples.py` deliberately never issues `POST /savedqueries` — that would create persistent state on SSB's servers. Such examples are JSON-syntax-validated only. Keep this exemption if you extend the checker, and never "verify" a saved-query example by actually posting it.

## Layout

- `SKILL.md` — the skill entrypoint. Frontmatter (`name`, `description`, `metadata.version`) controls when the skill auto-triggers; the body is the operational guide Claude follows. Keep triggers (Norwegian + English keywords for Norwegian official statistics) in the `description`. Structure: data-integrity rule → routing to sibling skills/tools → endpoint table → tool selection → language → 6-step workflow (Steg 1–6) → pitfalls → worked examples → fallback (which also carries the pointer to `troubleshooting.md`).

Since 1.5.0 the file is deliberately deduplicated: each rule has **one** primary occurrence in `SKILL.md` plus pointers, and detail lives in `references/`. Before adding a paragraph, grep for the term — if it already appears, extend the existing occurrence or the reference file instead of writing a second one. Terms worth grepping: `elimination`, `noteMandatory`, `top()`, `Lagre`, rate limit.
- `references/` — deeper reference material loaded on demand:
  - `json-stat2.md` — json-stat2 Dataset structure, row-major indexing, status codes, `extension` semantics at both dataset and dimension level, `link.related` (vendor-neutral; also covers pyjstat)
  - `api-details.md` — SSB-specific operational info (publishing times, rate-limit headers, license)
  - `codelists-and-filters.md` — codelist/filter syntax: `codelist[Var]=agg_…`, `top(n)`/`from(x)`/`range(a,b)`, wildcards, plus the `outputValues[Var]` parameter and the finding that it is **not load-bearing** at SSB (identical data for `aggregated`, `single` and omitted; an invalid value returns HTTP 200 unvalidated — verified 2026-08-30). Don't reintroduce it as a requirement. Note prefixes: `agg_KommFylker` uses `F-`, `agg_KommSummer` uses `K-`. Includes KPI/COICOP groupings (`vs_CoiCop2018Kpi01`, `agg_CoiCop2018Kpi011`).
  - `search-syntax.md` — pure Lucene query parser reference for `/tables?query=` (PxWebApi uses Lucene.Net under the hood). Non-Lucene search parameters (`pastDays`, `includeDiscontinued`) and Norwegian term choice belong in `SKILL.md` Steg 2, not here
  - `klass-vardok.md` — SSB's Klass (classifications) and VarDok (variable definitions) via URNs in `link.describedby` and ready-made `link.related` links, plus deriving the statistics shortname from `paths[0][2].id` before metadata is fetched
  - `output-formats.md` — `json-stat2`, `csv`, `xlsx`, `html`, `px`, `parquet` and parameters (`UseCodesAndTexts`, `IncludeTitle`, `heading`/`stub` pivoting). Holds the full parquet column contract (`value`/`ContentsCode_{code}` plus the `_symbol` columns that carry `status`); `SKILL.md` keeps one sentence
  - `common-tables.md` — well-known table IDs (KPI, befolkning, etc.); the machine-checked table (`| id | title | frekvens | … |`) is parsed by `check_common_tables.py`, so keep the column order
  - `troubleshooting.md` — common errors and fixes; also the canonical list of SSB's standardtegn (`.`, `..`, `:` plus the pre-2021 symbols) under «NULL-verdier i data» — `json-stat2.md` points here rather than repeating them
  - `mcp-tools.md` — mapping between `pxweb-mcp` MCP tools (`@jarib/pxweb-mcp`) and API endpoints, plus limitations (lossy `search_tables`, no `codelist[Var]` in `fetch_metadata`, no `outputFormatParams`) and the `--url` config caveat. Facts are version-bound — re-verify against the package source when it ships a new major version.
- `evals/eval-scenarios.md` — maintainer-internal behavioral fixtures: typical user questions with the expected table ID and endpoint sequence. Run via the `skill-creator` skill after larger edits to `SKILL.md` or `references/`. This layer catches *routing* regressions (picking discontinued 03013 instead of 14700); the Python checkers catch *factual* regressions. When an eval fails, run `check_examples.py` first — the table may have changed, not the skill.
- `scripts/`, `.github/` — repo-internal tooling, deliberately excluded from the distribution.

## Editing guidance

- The **Dataintegritet** section at the top of `SKILL.md` outranks everything else in the skill: never state a number not fetched from the API in that conversation, never blend other sources, never interpolate. Don't weaken or relocate it — the rest of the workflow assumes it.
- Preserve the bilingual (Norwegian primary, English secondary) trigger surface in `SKILL.md` frontmatter — removing keywords will cause the skill to stop firing for real user queries.
- The API base URL and endpoint table in `SKILL.md` are the canonical contract; if an endpoint is added/changed upstream, update `SKILL.md` first, then cross-check `references/api-details.md`.
- Examples should use real, currently-published SSB table IDs. `check_examples.py` fails on any table with `discontinued: true`, so replace rather than annotate dead IDs.
- For example URLs/queries, hit the live API and confirm HTTP 200 (or just run `check_examples.py`). Codelist prefixes are easy to forget: `agg_KommFylker` requires `F-` codes, `agg_KommSummer` requires `K-` codes. A 400 response usually means a missing prefix or a missing required variable (`Tid`/`ContentsCode` are never eliminable) — read the `title` field, which is the diagnostic; `detail` is only set for `Too many cells selected`.
- Use `valueCodes` (camelCase) consistently in GET examples — matches the OpenAPI spec and the POST body shape, even though the API is case-insensitive.
- Keep `references/*.md` focused; `SKILL.md` should stay the overview and defer detail to references rather than duplicating it.
- `check_examples.py` extracts POST bodies by brace-counting, so a JSON body in the docs must not contain `{` or `}` inside string values, and must not be interrupted by a closing code fence.

### Release checklist (every content change)

1. Bump `metadata.version` in `SKILL.md` frontmatter (semver: PATCH for fact fixes, MINOR for new content). A version that isn't bumped lies about copies being current. `SKILL.md` also states the version in prose ("Denne kopien er v…") — update both.
2. Add a `CHANGELOG.md` entry. Existing entries record the verification date and whether the sibling SCB skill was affected; follow that pattern.
3. Rebuild the zip with `scripts/build_zip.sh` — the `zip-sync` CI job fails otherwise.
4. If you added a file to `references/`, update the file tree in `README.md` too (it's hand-maintained; `build_zip.sh` globs `references/*.md` so the file ships either way).

**The zip and the README file tree contain user-facing files only**: `SKILL.md`, `README.md`, `CHANGELOG.md`, `references/`. Never add `scripts/`, `.github/`, `CLAUDE.md` or `evals/` to either.

## Related sibling skills

A parallel `scb-pxwebapi-v2` skill exists for Sweden's SCB. The two APIs share the PxWebApi v2 shape — when fixing a bug in one, check whether the other needs the same fix, and record the outcome of that check in `CHANGELOG.md` (including "does not apply", with the date).

A third-party `norges-bank-api` skill (github.com/avocodetoast/norges-bank-api-skill, SDMX — not PxWebApi) covers Norges Bank data, and `ssb-histstat` covers digitised historical statistics from before the Statistikkbank era. `SKILL.md` Steg 1 routes such questions there; Steg 5 and Fallgruver require answers to comment only on the fetched SSB numbers — cross-references are routing, **never** data blending from other sources. Keep these references when editing.
