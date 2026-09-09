# Claude Skill: PxWebApi v1 (Generic)

A [Claude Skill](https://support.claude.com/en/articles/12512180-use-skills-in-claude) for
accessing official statistics from any **PxWebApi v1** installation — the older, POST-based
PxWeb 1.0 API that most PxWeb installations worldwide still run.

It is the v1 counterpart to `generic-pxweb-v2-skill`, and shares its vendor-neutral approach.

## What is PxWebApi v1?

PxWebApi is the REST API of PxWeb, the statistical database software developed by Statistics
Sweden (SCB) and used by statistical agencies across the Nordics and beyond. Version 1.0 has
been in service since the mid-2010s. A v2 exists, but adoption is partial — many agencies have
no announced migration date, so v1 remains the API most PxWeb users actually meet.

**The defining property: data is retrieved with HTTP POST only.** A GET against a table URL
returns that table's metadata, not its numbers. Queries are JSON documents posted to the table's
own URL.

Installations verified live on 2026-08-28:

| Agency | Base URL |
|---|---|
| Statistics Norway (SSB) | `https://data.ssb.no/api/v0/no/table` |
| Statistics Sweden (SCB) | `https://api.scb.se/OV0104/v1/doris/sv/ssd` |
| Statistics Finland | `https://pxdata.stat.fi/PXWeb/api/v1/fi/StatFin` |
| Statistics Iceland | `https://px.hagstofa.is/pxis/api/v1/is/{database}` |
| Statistics Faroe Islands | `https://statbank.hagstova.fo/api/v1/en/H2` |
| Statistics Greenland | `https://bank.stat.gl/api/v1/en/Greenland` |
| Statistics Estonia | `https://andmed.stat.ee/api/v1/et/stat` |

The list is not exhaustive — many more national and regional agencies run PxWeb.

## What this skill does

- Guides Claude through the v1 workflow: locate table → read metadata → build query → POST → present
- Covers hierarchy navigation and `?query=` search, including **which installations lack search**
- Documents the v1 query body and all five filters (`item`, `all`, `top`, `agg:`, `vs:`)
- Explains the elimination rules, which decide what happens to variables you leave out
- Handles aggregations and groupings, which v1 metadata does not expose — including a verified
  method for discovering them, and an explanation of the `.vs`/`.agg` files they come from
- Explains the split between file-based installations (most of them, `.px` in the URL) and the
  relational ones (SSB, SCB)
- Works with any v1 installation — you supply the base URL
- Fully in English for international use
- Output follows the open [json-stat2](https://json-stat.org/) spec, shared with Eurostat and the
  World Bank

## Corrections to the published documentation

Everything in this skill was reproduced with `curl` against live installations. Three points
where current behaviour differs from the official PxWeb 1.0 specification and from several agency
guides:

- **Format names are hyphenated.** `json-stat2` and `json-stat` work; the documented `jsonstat2`
  and `jsonstat` return `400` on both SSB and SCB.
- **Multiple wildcards in one `all` selection work** (`["199*", "202*"]`), though the
  specification states only one is permitted. Older builds may still enforce the limit.
- **Exceeding the cell limit returns `403`**, not `400` or `413`, with the body
  `{"error":"Too many values selected"}`.

## What this skill does NOT include

- Country-specific table lists — table ids differ per installation
- Country-specific aggregation names or regional codes
- Country-specific metadata conventions

## File structure

```
generic-pxweb-v1-skill/
├── SKILL.md                  # Main skill entrypoint (loaded on trigger)
├── README.md                 # This file
├── CHANGELOG.md              # Version history; every content change gets an entry
├── CLAUDE.md                 # Guidance for Claude Code when editing this skill
├── references/               # Loaded on demand
│   ├── query-syntax.md       # Query body, filters, elimination, aggregations, cURL
│   ├── api-details.md        # URL structure, navigation, search, formats, limits
│   ├── px-files-and-classifications.md  # PX files, .vs/.agg, PX keywords behind the metadata
│   ├── json-stat2.md         # json-stat2 format spec (also Eurostat, World Bank)
│   ├── troubleshooting.md    # HTTP codes and the three v1 error payloads
│   ├── installations.md      # 50 known v1 installations: status, languages, ?config limits
│   └── v1-vs-v2.md           # Translation guide, and using v2 to fill v1's gaps
├── evals/                    # Repo-internal: scenarios for testing the skill end to end
└── scripts/
    └── build_zip.sh          # Builds the distribution ZIP (user-facing files only)
```

The four files above `references/` plus `references/` itself are what ships. `CLAUDE.md`,
`evals/` and `scripts/` are repo-internal and deliberately excluded from the ZIP.

## Installation

### Claude.ai

1. Build the ZIP with `scripts/build_zip.sh` — do not zip the folder by hand, or
   repo-internal files end up in the package
2. Go to **Settings > Features > Skills**
3. Upload the ZIP file

### Claude Code

```bash
cp -r generic-pxweb-v1-skill ~/.claude/skills/generic-pxweb-v1-skill
```

## Related skills

- `generic-pxweb-v2-skill` — the same coverage for PxWebApi v2
- `ssb-pxwebapi-v2` — Norway-specific v2, with curated table lists and codelist documentation
- `scb-pxwebapi-v2` — Sweden-specific v2

## Sources

Built from the PxWeb 1.0 specification (SCB, 2024-10-14), Statistics Norway's
*API mot Statistikkbanken — brukerveiledning* (October 2024) and its accompanying course material,
Statistics Finland's *How to use the Statfi PxWeb API*, the PX-file format specification
(AXIS-VERSION 2013) and the PC-Axis classification-file documentation — and verified against seven
live installations on 2026-08-28.

## License

PxWeb and PxWebApi are open source: https://github.com/PxTools/PxWebApi.
Data licensing depends on the individual agency — SSB, for example, publishes under CC BY 4.0.
