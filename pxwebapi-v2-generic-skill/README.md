# Claude Skill: PxWebApi v2 (Generic)

A [Claude Skill](https://support.claude.com/en/articles/12512180-use-skills-in-claude) for accessing official statistics from any PxWebApi v2 installation.

This skill is a reduced, vendor-neutral version derived from the Statistics Norway skill `ssb-pxwebapi-v2` (see link at the bottom of this README).

## What is PxWebApi v2?

PxWebApi v2 is a REST API for statistical databases, developed by Statistics Sweden (SCB) and Statstics Norway (SSB). It is used by national statistical institutes across the Nordics and beyond. It provides a standardized way to search, explore, and retrieve official statistics.

Known v2 installations (all verified live 2026-09-08):

- **Statistics Norway (SSB):** `https://data.ssb.no/api/pxwebapi/v2`
- **Statistics Sweden (SCB):** `https://statistikdatabasen.scb.se/api/v2`
- **Official Statistics Portal of Latvia (CSP):** `https://api.stat.gov.lv/api/v2`

They share the API shape but differ in cell limit (10 000 to 800 000), default data format (Latvia returns PX unless asked for json-stat2), variable names (`Tid` vs `TIME`, `Region` vs `AREA`) and period-code letters. The skill treats every such difference as "read it from `/config` and metadata", and `references/api-details.md` carries the verified comparison table.

## What this skill does

- Guides Claude through the correct workflow: search → metadata → query → present
- Covers all PxWebApi v2 endpoints (tables, metadata, codelists, saved queries, config)
- Handles codelists and aggregations
- Works with any PxWebApi v2 installation — just specify the base URL
- Requires every number to be fetched from the API in the same conversation — never recalled
- Fully in English for international use
- Output format follows the open [json-stat2](https://json-stat.org/) spec, also used by Eurostat and World Bank

## What this skill does NOT include

- Country-specific table lists (no `common-tables.md` — table IDs differ per installation)
- Country-specific codelist IDs or regional codes
- Country-specific metadata conventions (URN links to classification systems)

For a comprehensive SSB-specific skill with curated table lists, codelist documentation, and Norwegian/English support, see [ssb-pxwebapi-v2](../ssb-pxwebapi-v2-skill/). A Swedish counterpart, [scb-pxwebapi-v2](../scb-pxwebapi-v2-skill/), lives in the same repository.

## File structure

```
generic-pxweb-v2-skill/
├── SKILL.md                       # Main skill entrypoint (loaded on trigger)
├── README.md                      # This file
├── CHANGELOG.md                   # Version history; the current version is metadata.version in SKILL.md
├── generic-pxweb-v2-skill.zip     # Packaged skill for upload to Claude.ai
└── references/                    # Loaded on demand
    ├── json-stat2.md              # json-stat2 format spec (Dataset, row-major indexing, extension, status codes — also applies to Eurostat, World Bank)
    ├── api-details.md             # /config, rate limiting, output formats, and the verified per-installation comparison table
    ├── codelists-and-filters.md   # Codelists, filter expressions (and which ones do not exist), time-code formats per installation
    └── troubleshooting.md         # The five 400 titles, PX-instead-of-JSON, default selection, search returning 0 hits
```

`CLAUDE.md`, `scripts/` and `evals/` in the repository are maintainer-internal and are not part of the package.

## Installation

### Claude.ai

1. Download `generic-pxweb-v2-skill.zip`, or build it from the repository:

   ```bash
   scripts/build_zip.sh
   ```

   The package contains only the user-facing files (`SKILL.md`, `README.md`, `CHANGELOG.md`, `references/`) under the top-level folder `generic-pxweb-v2-skill/`.

2. Go to **Settings > Features > Skills**
3. Upload the ZIP file

### Claude Code

The installed name is `generic-pxweb-v2-skill` (the frontmatter `name`); the repository folder is `pxwebapi-v2-generic-skill`. From the repository root:

```bash
cp -r pxwebapi-v2-generic-skill ~/.claude/skills/generic-pxweb-v2-skill

# or symlink a cloned repository, so that git pull keeps the copy current
ln -s "$PWD/pxwebapi-v2-generic-skill" ~/.claude/skills/generic-pxweb-v2-skill
```

## MCP servers

For Claude to call the API directly, you need an MCP server or a tool that can send HTTP GET and POST (e.g. `curl` via Bash):

- **@jarib/pxweb-mcp** (https://www.npmjs.com/package/@jarib/pxweb-mcp) — open source, works with any PxWebApi v2 installation; point it at the installation with `--url {base_url}` (the default is SSB)
- Or build your own with FastMCP or similar

## License

PxWebApi v2 is open source: https://github.com/PxTools/PxWebApi. Data licensing depends on the individual agency — `GET /config` returns the licence URL in `license` (SSB: its own terms; SCB and Latvia: CC0 1.0).
