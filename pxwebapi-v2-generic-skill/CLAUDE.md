# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is **not** an application codebase. It is a Claude Code **Skill** package that teaches Claude how to query *any* PxWebApi v2 installation. Verified installations are listed in `SKILL.md` under "Known PxWebApi v2 installations" — currently SSB (Norway), SCB (Sweden) and CSP (Latvia); more agencies are expected to migrate. There is no application runtime — changes here are documentation/prompt edits that get loaded when the skill triggers.

There *is* a build step: `scripts/build_zip.sh` packages the distributable, and `.github/workflows/check-v2-generic-zip.yaml` (repo root) fails if the committed zip differs from a fresh build. There is **no** example checker, deliberately — the examples are schematic (`{base_url}`, `{id}`), so there is nothing to call. The cost of that choice is that a factual claim here is only as fresh as the last manual verification; the CHANGELOG records the date of each.

Unlike its siblings `ssb-pxwebapi-v2` and `scb-pxwebapi-v2`, this skill is **vendor-neutral**: examples should not assume a specific base URL, table ID, or codelist convention. When agency-specific behaviour matters, describe it as "varies by installation" **and say how**, with the verified values — the comparison table in `references/api-details.md` is the evidence behind every such sentence in `SKILL.md`.

## Commands

```bash
scripts/build_zip.sh                  # writes ./generic-pxweb-v2-skill.zip
scripts/build_zip.sh /tmp/fresh.zip   # write elsewhere, e.g. to diff against the committed zip
```

## Layout

- `SKILL.md` — the skill entrypoint. Frontmatter (`name`, `description`, `metadata.version`) controls when the skill auto-triggers; the body is the operational guide. Structure: data-integrity rule → known installations (with the four query-changing differences, the v1-only list and the version check) → endpoint table → 6-step workflow → pitfalls → fallback.

  **The frontmatter `name` (`generic-pxweb-v2-skill`) is not the folder name (`pxwebapi-v2-generic-skill`).** Claude Code triggers on the folder in practice; the frontmatter name is what counts when the package is uploaded to claude.ai, so `build_zip.sh` uses it as the top-level folder inside the zip and as the zip's name.

  Since 0.11.0 the file is deliberately deduplicated: each rule has **one** primary occurrence in `SKILL.md` plus pointers, and detail lives in `references/`. Before adding a paragraph, grep for the term — if it already appears, extend the existing occurrence or the reference file instead of writing a second one. Terms worth grepping: `elimination`, `noteMandatory`, `top()`, `range()`, `role.geo`, `defaultselection`, `outputFormat`.
- `references/` — deeper reference material loaded on demand:
  - `json-stat2.md` — json-stat2 Dataset structure, row-major indexing, status codes, `extension` at both levels, the metadata-vs-data `elimination` trap, what the format cannot express (vendor-neutral; also applies to Eurostat)
  - `api-details.md` — `/config`, the rate-limit table, **the verified per-installation comparison table**, and output formats (moved here from `SKILL.md` in 0.11.0)
  - `codelists-and-filters.md` — codelist/filter syntax: `codelist[Var]=…`, `top(n)`/`bottom(n)`/`from(x)`/`to(x)`/`range(a,b)`/offset forms, wildcards, explicit lists, and the **GET-bracket / POST-bare** table that explains the `Illegal selection expression` 400; per-installation time-code table; `outputValues` is not load-bearing
  - `troubleshooting.md` — the five 400 titles (identical on all three installations), PX-instead-of-JSON, default-selection figures, search returning 0 hits
- `evals/eval-scenarios.md` — maintainer-internal behavioural fixtures with success criteria stated as *form*, never as a figure. Run as actual runs after larger edits, and append each run's outcome to the log at the bottom. Note `.claude/settings.local.json` has this skill switched off under `skillOverrides`.
- `scripts/`, `evals/`, `.github/` (repo root) — repo-internal, excluded from the distribution.

## Editing guidance

- The **Data integrity — the base rule** section at the top of `SKILL.md` outranks everything else in the skill: never state a number not fetched from the API in that conversation, never blend other sources, never interpolate. Don't weaken, shorten or relocate it — the rest of the workflow assumes it. It mirrors the same section in `ssb-pxwebapi-v2` (Norwegian), `scb-pxwebapi-v2` (Swedish) and `generic-pxweb-v1-skill`; a change to the rule belongs in all four. As of 0.11.0 the mandatory-notes bullet is mirrored here; SSB's three further bullets (verify variable codes, keep precision, flag provisional figures) are not.
- **A behaviour verified on one installation is written as a fact about that installation, never as a rule.** Three claims in this skill were universal rules until 0.11.0 and were wrong on a known installation: "if `role.geo` is missing, assume the whole country" (SCB never sets it), "weekly codes are `YYYYWNN`" (true only at Latvia), and "json-stat2 is the default" (Latvia returns PX). A fourth was the opposite error: `range(from,to)` was declared non-existent after bare GET tests returned 400 on all three — the maintainer disproved it with a bracketed URL, and the POST test that had succeeded had been misread. When you add a claim, say which installations you checked, in which direction (GET and POST behave differently), and when.
- **Neither the specification nor a single 400 is evidence.** `outputValues` is in the spec and does nothing on any deployed installation; `range()` is in the spec, returned 400 on all three, and works — the syntax differs between GET (`[range(a,b)]`) and POST (`"range(a,b)"`). Before writing "does not exist", try the other transport, brackets, and the maintainer's own examples.
- Keep the trigger surface broad (Nordic + generic PxWeb keywords, plus Latvia). The agency-specific skills (`ssb-pxwebapi-v2`, `scb-pxwebapi-v2`) are preferred when the user clearly targets one country — this skill should fire when the agency is unclear or when the user mentions an installation without a dedicated skill.
- The base URL list in `SKILL.md` (Known installations) is the canonical inventory, duplicated on purpose in `README.md` (for humans) and expanded in `references/api-details.md` (the comparison table). Adding an agency means all three, plus a row for each "varies by installation" claim — that is the point of having the table.
- Examples should be **schematic** (`/tables/{id}/data?…`) rather than tied to a real table, since the skill spans many installations. When a concrete table is named as evidence (TAB6471, IRS010m, 03024), hit the live API and record the date in the CHANGELOG. Verified 2026-09-08: all three installations, the Greenland trap, every 400 title, the GET/POST spelling of `range()` on all three (2026-09-09), the wildcard-stemming behaviour on all three.
- Use `valueCodes` (camelCase) consistently in GET examples — matches the OpenAPI spec and the POST body shape, even though the API is case-insensitive.

### Release checklist (every content change)

1. Bump `metadata.version` in `SKILL.md` frontmatter (semver; stay below 1.0.0 while the skill has no published distribution). A version that isn't bumped lies about copies being current. This skill states the version only in frontmatter — there is no prose version line.
2. Add a `CHANGELOG.md` entry — what changed, what was verified live, on what date, on which installations.
3. Rebuild the zip with `scripts/build_zip.sh` — the `zip-sync` CI job fails otherwise.
4. If you added a file to `references/`, update the file tree in `README.md` too.
5. If a factual claim changed, do the **sibling check** below and record its outcome in `CHANGELOG.md`, including when the answer is "does not apply".

**The zip and the README file tree contain user-facing files only**: `SKILL.md`, `README.md`, `CHANGELOG.md`, `references/`. Never add `scripts/`, `evals/` or `CLAUDE.md` to either.

## Related sibling skills

- `ssb-pxwebapi-v2` — Norway-specific, deeper SSB knowledge (Klass/VarDok URNs, `agg_KommFylker`/`agg_KommSummer` with `F-`/`K-` prefixes, common-tables index, live example checker)
- `scb-pxwebapi-v2` — Sweden-specific; since 0.11.0 has its own example checker with a `lastPeriod` staleness test
- `generic-pxweb-v1-skill` — the same vendor-neutral shape for **PxWebApi v1**, which most agencies outside SSB/SCB/CSP are still on (Finland, Iceland, Faroe Islands, Greenland, Estonia, verified 2026-08-30)

The v2 skills share the PxWebApi v2 shape — when fixing a bug in one, check whether the others need the same fix, **and verify against the other installation before porting**: the rate-limit fix from SSB 1.5.0 would have introduced an error at SCB. Vendor-neutral findings (json-stat2 semantics, filter syntax, status codes, the GET-bracket rule, wildcard stemming) belong here first; agency-specific ones belong in the country skill.

**The v1 skill follows a rule in both directions:** the **response** side is shared — json-stat2 semantics, `extension.px`, status codes, elimination *semantics*, classification structure — so a fix to any of that probably belongs in both. The **request** side does not transfer at all: v1 is POST-only with a `{"query": […], "response": {…}}` body and `item`/`all`/`top`/`agg:`/`vs:` filters, v2 is GET-or-POST with `valueCodes[…]`, `codelist[…]` and `top(n)`/`from(x)`. Never copy request syntax across, in either direction. Where v1 and v2 genuinely differ in behaviour (v2 returns 400 for a missing mandatory variable where v1 returns all values; the cell limit is 400 in v2 and 403 in v1), say so explicitly — those are the errors people carry between the two.
