# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is **not** an application codebase. It is a Claude Code **Skill** package that teaches Claude how to query Statistics Sweden (SCB) via the public PxWebApi v2 at `https://statistikdatabasen.scb.se/api/v2`. There is no application runtime — changes here are documentation/prompt edits that get loaded when the `scb-pxwebapi-v2` skill triggers.

There *is* a build step and a test: `scripts/build_zip.sh` packages the distributable, and `scripts/check_examples.py` treats every example URL, POST body and table ID written in the markdown as an assertion to verify against the **live** SCB API. Prose is the fixture set; drift upstream at SCB fails the build.

## Commands

Requires Python 3.12+ (stdlib only) and `zip`/`unzip`.

```bash
# Verify every example URL, GET/POST query and table ID in SKILL.md + references/
python3 scripts/check_examples.py            # add --quiet to hide OK lines
python3 scripts/check_examples.py --delay 1.0   # SCB allows 30 calls per 10 s; CI uses this

# Rebuild the distribution zip (required before committing content changes)
scripts/build_zip.sh                  # writes ./scb-pxwebapi-v2-skill.zip
scripts/build_zip.sh /tmp/fresh.zip   # write elsewhere, e.g. to diff against the committed zip
```

`.github/workflows/check-scb-examples.yaml` (repo root — GitHub Actions only reads workflows there) runs two jobs, `check` (the Python script) and `zip-sync` (rebuilds the zip and `diff -r`s it against the committed one), on push/PR touching `SKILL.md`, `references/**`, `scripts/**` or the zip, and by hand via `workflow_dispatch` (Actions tab → *Run workflow*). There is **no scheduled run**: the Monday cron was removed on 2026-10-13 (maintainer's call), so SCB-side drift with no local change surfaces only on the next push or manual run. Run the checker locally before a release.

`check_examples.py` is a port of the SSB skill's checker; only the base URL, the table-ID pattern (`TAB638`-style) and the language differ. It asserts HTTP 200 — **not** that a search example finds the table the example then uses. That has to be checked by hand: `?query=folkmängd` returns 200 with TAB638 on page 3 (position 47 of 117, default `pageSize` 20). It also skips any `GET` line whose path contains a space, so write multi-word searches with `+` if you want them checked at all; the English example (`title:population AND title:month`) cannot be, and was verified by hand. **Write å, ä and ö percent-encoded in examples** (`?query=folkm%C3%A4ngden+per+m%C3%A5nad`): the checker encodes URLs itself and so passes a raw `ä`, but an agent that copies the line into `curl -g` gets 200 with 0 hits and no error (found by the 0.11.2 eval, 2026-10-14). `%` is in the checker's safe set, so an encoded line is not encoded twice.

### The `/savedqueries` safety rule

`check_examples.py` deliberately never issues `POST /savedqueries` — that would create persistent state on SCB's servers. Such examples are JSON-syntax-validated only. Keep this exemption if you extend the checker, and never "verify" a saved-query example by actually posting it.

## Layout

- `SKILL.md` — the skill entrypoint. Frontmatter (`name`, `description`, `license`, `metadata.version`) controls when the skill auto-triggers; the body is the operational guide Claude follows. Keep triggers (Swedish + English keywords for Swedish official statistics) in the `description`. Structure: data-integrity rule → endpoint table → tool selection → language → 6-step workflow (Steg 1–6) → pitfalls → licence → worked examples → fallback.

  **The frontmatter `name` (`scb-pxwebapi-v2`) is not the folder name (`scb-pxwebapi-v2-skill`).** Claude Code triggers on the folder in practice; the frontmatter name is what counts when the package is uploaded to claude.ai, so `build_zip.sh` uses it as the top-level folder inside the zip.

  Since 0.11.0 the file is deliberately deduplicated: each rule has **one** primary occurrence in `SKILL.md` plus pointers, and detail lives in `references/`. Before adding a paragraph, grep for the term — if it already appears, extend the existing occurrence or the reference file instead of writing a second one. Terms worth grepping: `elimination`, `noteMandatory`, `top()`, `Statistikdatabasen`, `role.geo`, rate limit.
- `references/` — deeper reference material loaded on demand:
  - `json-stat2.md` — same layout as SSB's since 0.11.2: table of contents, then «Så läser du ett uttag» (seven numbered rules, actions only, each pointing to its primary occurrence), then the format: Dataset structure and indexing (the TAB6471 stride example), a field table, `extension` per variable with PX keywords in parentheses, root `extension` and `extension.px`, `status`/`note`/`link`, what json-stat2 does not carry, tools. Rules come first and the format sections only describe; counts and verification dates go to `DEVLOG.md`. **SCB differs from SSB on mandatory notes:** it sets them at three levels — root `noteMandatory`, per variable `dimension.{var}.extension.noteMandatory` (TAB6471 `Alder`) and per value `categoryNoteMandatory` keyed value code → index (TAB638 `Region` `{"0140": {"1": true}}`) — and `link.related` appears in data responses too, while `describedby` carries plain text, not URNs. Don't port SSB's «never set per variable» text here
  - `mcp-tools.md` — mapping between `pxweb-mcp` MCP tools (`@jarib/pxweb-mcp`) and API endpoints, the `--url` caveat (the server defaults to SSB), limitations (`language` only `no`/`en`, lossy `search_tables`, no `outputFormatParams`), and the finding that `outputValues`/`output_values` has no effect at SCB. Facts are version-bound — re-verify when the package ships a new major version
  - `search-syntax.md` — Lucene query parser reference for `/tables?query=`, plus the default-`pageSize`-is-20 trap. Swedish term choice and the non-Lucene parameters (`pastDays`, `includeDiscontinued`) belong in `SKILL.md` Steg 2, not here

  The SCB skill is still sparser than `ssb-pxwebapi-v2`: codelist syntax, filter expressions, output formats and troubleshooting live inline in `SKILL.md`, each stated once. There is no `common-tables.md` — SCB table IDs (`TAB6471`, `TAB6596`) appear only in the worked examples.
- `CHANGELOG.md` and `DEVLOG.md` — two logs for two readers, both in Swedish. `CHANGELOG.md` ships in the zip and tells **users** what is different in the answers: a few bullets per version, no sweep counts, no sibling checks. `DEVLOG.md` is the **maintainer's** record and is not shipped: what changed, what was verified live and when, and every sibling-check outcome. It is the old `CHANGELOG.md`, split off on 2026-10-05. Every version appears in both. The `CHANGELOG.md` header links to `DEVLOG.md` by full GitHub URL, because a relative link is dead inside the zip.
- `evals/eval-scenarios.md` — maintainer-internal behavioural fixtures: typical user questions with the expected table ID and endpoint sequence, success criteria stated as *form*, never as a concrete figure. Run via the `skill-creator` skill after larger edits — as actual runs with tools, not read-throughs. Catches *routing* regressions (TAB5737 instead of TAB6596, TAB638 instead of TAB6471); the checker catches *factual* ones. The run log at the bottom of that file records what each scenario found — keep appending to it.
- `docs/` — user-facing but deliberately **outside the zip**: the skill map, in Swedish. `skillkarta-arbetsflode.svg` (Steg 1–6, the endpoints each step calls, which calls are HTTP-only and not in `pxweb-mcp`, the `/data` response as the only source of numbers) and `skillkarta-kontroll-och-paketering.svg` (what `check_examples.py` checks against the live API, the zip build) are hand-drawn and are the only copy of each drawing: `skillkarta.html` wraps them with `<img>` and prose. Each SVG carries its own `<style>` and an opaque background, since GitHub serves it as an image and no page CSS or web font reaches it — size text for wide fallback fonts like DejaVu Sans. Both name the version they were drawn from; `check_examples.py` reads only `SKILL.md` and `references/`, so nothing checks `docs/`. The siblings' `docs/` use the same layout.
- `scripts/`, `evals/`, `.github/` (repo root) — repo-internal tooling, deliberately excluded from the distribution.

## Editing guidance

- Preserve the bilingual (Swedish primary, English secondary) trigger surface in `SKILL.md` frontmatter — removing keywords will cause the skill to stop firing for real user queries.
- The API base URL and endpoint table in `SKILL.md` are the canonical contract; if an endpoint is added/changed upstream, update `SKILL.md`.
- Examples should use real, **currently-published** SCB table IDs. SCB tables use mixed naming (numeric `TAB638`, sometimes named like `BefolkningNy`) and are renamed/retired more often than IDs suggest.
- **`discontinued` is not an aliveness test, and this bit the skill.** SCB freezes a table and continues the series in a *new* one without ever setting the flag. Through v0.10.0 the main worked example used TAB638, which stopped at 2024 (no `discontinued` field, last updated 2025-02-21) while the live series moved to TAB5557 (annual 2025) and TAB6471 (monthly, 2025M01–). Two independent eval runs caught it; `check_examples.py` never did, because the table answers 200. The checker now also compares `lastPeriod` against today (`staleness()`) and fails an example table that is more than a year, eight months, four quarters or 26 weeks behind. When an example fails that way, **find the successor table** rather than raising the allowance.
- For example URLs/queries, run `check_examples.py`. Common 400 causes: missing required variable (`Tid` and `ContentsCode` are never eliminable, but **which others are is per table** — `Alder` is eliminable in TAB638 and mandatory in TAB6471), a codelist used with the table's ordinary codes instead of the codelist's own (`agg_RegionKommungrupp2023-` wants `2023_A1`, not `0180` — `Non-existent value`), wrong time format for the table's `timeUnit` (weekly is `2026V30` at SCB, not `W`).
- Use `valueCodes` (camelCase) consistently in GET examples — matches the OpenAPI spec and the POST body shape, even though the API is case-insensitive.
- Region codes for Sweden are 4-digit SKR codes (e.g. `0180` Stockholm); first two digits are the län code (`01*` = all Stockholm-län municipalities). The "Riket" total is `00`, and it is the `eliminationValueCode` for `Region` — visible only in data responses that include it.
- **From reference year 2025 SCB adds CKM noise to population statistics** (Cell Key Method: a small controlled random perturbation, so reported totals are not always the sum of their parts, and the uncertainty compounds when you sum values yourself). It arrives as a *mandatory* note on the affected tables, and it constrains the arithmetic Steg 5 invites. Keep the Steg 5 bullet that says so; if a future example uses a pre-2025 table, the caveat does not apply to it.
- **Facts verified on one installation are written as facts about that installation.** SCB sets no `role.geo` (SSB does); SCB announces its rate limit in `/config` *and* in `X-Rate-Limit-*` headers — a different spelling from SSB's `x-ratelimit-*`, which is why an earlier grep concluded "no headers"; SCB serves no `parquet` (SSB does). Each of these has been written as a universal rule in some sibling at some point. When porting a fix from `ssb-pxwebapi-v2`, verify it against SCB first — the rate-limit fix from SSB 1.5.0 would have introduced an error here.
- The **Dataintegritet — grundregeln** section at the top of `SKILL.md` outranks everything else in the skill: never state a number not fetched from the API in that conversation, never blend other sources, never interpolate. Don't weaken, shorten or relocate it — the rest of the workflow assumes it. It mirrors the same section in `ssb-pxwebapi-v2` (Norwegian), `generic-pxweb-v2-skill` and `generic-pxweb-v1-skill` (English); a change to the rule belongs in all four. As of 0.11.0 the mandatory-notes bullet is mirrored here; SSB's three further bullets (verify variable codes, keep precision, flag provisional figures) are not.
- Answers must comment only on the numbers fetched in the query — never fetch and blend in data from other sources (Riksbanken, Eurostat, web search); refer the user onward instead. The rule lives in Dataintegritet; Steg 5 and Fallgropar point to it rather than repeating it.
- Worked examples show *form*, not figures: `{N}`, `{år}`/`{year}` in the «→» lines. A number that stands in the instruction text is a number a model can repeat when the API fails. Placeholders go outside the JSON blocks so the checker's brace-counting is untouched.

### Release checklist (every content change)

1. Bump `metadata.version` in `SKILL.md` frontmatter (semver; stay below 1.0.0 while the skill is marked BETA). A version that isn't bumped lies about copies being current.
2. Add a `DEVLOG.md` entry (Swedish) — what changed, what was verified live, on what date. Then add the user entry in `CHANGELOG.md` (Swedish), derived from it: what is different in the answers, in a few bullets, with corrections marked **Rättat:**. Same version and date in both files.
3. Rebuild the zip with `scripts/build_zip.sh` — the `zip-sync` CI job fails otherwise.
4. If you added a file to `references/`, update the file tree in `README.md` too (hand-maintained; `build_zip.sh` globs `references/*.md` so the file ships either way).
5. If a factual claim changed, do the **sibling check** below and record its outcome in `DEVLOG.md`, including when the answer is "does not apply". It stays out of `CHANGELOG.md`, which is about this skill's answers.
6. If you changed a step, an endpoint, a limit or the checker, redraw the matching SVG in `docs/`. Neither is in the zip, so `zip-sync` will not catch them drifting.

**The zip and the README file tree contain user-facing files only**: `SKILL.md`, `README.md`, `CHANGELOG.md`, `references/`, plus `LICENSE` in the zip. Never add `scripts/`, `evals/`, `CLAUDE.md` or `DEVLOG.md` to either; `docs/` is user-facing and in the README tree, but stays out of the zip (see Layout).

`LICENSE` (MIT) lives in the **repo root** and covers the whole repo; `build_zip.sh` copies it into the package because MIT requires the notice to travel with every copy, and the zip is the copy that gets handed out. Don't add a per-skill `LICENSE` — edit the root one, and rebuild **all six** zips when it changes (every zip-sync workflow has `LICENSE` in its `paths:` filter). `SKILL.md` frontmatter carries `license: MIT. LICENSE has complete terms` (the optional Agent Skills field — keep it short, it names the file beside `SKILL.md` in the zip); never put licence text in the body, which is loaded on every trigger.

## Related sibling skills

- `ssb-pxwebapi-v2` — Norway's SSB, same PxWebApi v2 shape, deeper (Klass/VarDok URNs, `agg_KommFylker`/`agg_KommSummer` with `F-`/`K-` prefixes, common-tables index, more reference files). When fixing a bug in one, check whether the other needs the same fix — and verify against the other installation before porting (see "Facts verified on one installation" above).
- `generic-pxweb-v2-skill` — vendor-neutral v2. Response-side findings that hold on both installations (`eliminationValueCode` only in data responses, `outputValues` not load-bearing, `role.geo` optional) belong there too.
- `generic-pxweb-v1-skill` — PxWebApi v1, which SCB still runs alongside v2 at `api.scb.se/OV0104/v1/doris/`. The request side does not transfer at all; only json-stat2 semantics are shared.

Differences to keep in mind between SCB and SSB:

- Different base URLs (SCB: `statistikdatabasen.scb.se/api/v2`; SSB: `data.ssb.no/api/pxwebapi/v2`) and default language (SCB `sv`, SSB `no`)
- SCB uses 4-digit SKR codes; SSB uses 4-digit kommunekoder + special prefixes (`F-`, `K-`) for aggregation codelists. SCB's aggregation codelists carry their own code sets (`2023_A1`…)
- SSB has well-documented Klass/VarDok URN systems exposed via `link.describedby`; SCB metadata is sparser
- SCB: `maxDataCells` 150 000, rate limit 30 calls / 10 s in `/config` plus `X-Rate-Limit-*` headers, no `parquet`, no `role.geo`. SSB: 800 000, `x-ratelimit-*` headers only, `parquet`, `role.geo` set
