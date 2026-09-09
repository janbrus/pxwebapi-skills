---
name: generic-pxweb-v2-skill
description: >
  Access official statistics from any PxWebApi v2 installation. Use when querying
  statistical databases from national statistical institutes running PxWebApi v2.
  Trigger on "PxWeb", "PxWebApi", "statistical database", "Statistikdatabasen",
  "Statistics Latvia", "stat.gov.lv", or similar generic references. For Norwegian (SSB)
  or Swedish (SCB) statistics specifically, prefer the dedicated `ssb-pxwebapi-v2` or
  `scb-pxwebapi-v2` skills which include agency-specific examples and table catalogs.
  Covers table search, metadata, data queries, codelists, and saved queries.
metadata:
  version: "0.11.0"
---

# PxWebApi v2 — Generic Skill

This skill guides you through using PxWebApi v2 to search, explore, and retrieve official statistics. PxWebApi v2 is developed by Statistics Sweden (SCB) and used by several national statistical institutes. Everything below that says *varies by installation* has been verified to vary on the three installations listed under "Known installations".

## Data integrity — the base rule

Official statistics carry an agency's name. A wrong number under that citation damages trust in the agency, not just in the answer. This rule outranks everything else in this skill:

**Never state a number you have not fetched from the API in this conversation.**

- **No numbers from memory.** If you did not run the query, you do not have the number — including numbers you are confident about. Populations, price indices and unemployment rates all move, and training data has a cutoff.
- **No numbers from other sources in the same answer.** Point the user elsewhere rather than blending.
- **If the API fails, say so.** No estimates, no "roughly". See Fallback.
- **No interpolation or projection.** A period missing from the extract is missing from the answer.
- **Mark your own calculations.** Growth rates, shares and sums are yours, not the agency's — show which fetched numbers they rest on, and keep the API's decimals (`category.unit.decimals`).
- **Show `status` values as they are.** Missing, provisional and confidential values belong in the table, not hidden or replaced by zero.
- **Show mandatory notes.** When `extension.noteMandatory` is set, the agency has decided the note travels with the figure. Omitting it presents the number without the caveat the agency attached. See Step 5.
- **Check `discontinued` and `lastPeriod`.** Tables are closed and the series often continues in a new one. If you use a discontinued table, say so and give the last period.

Not finding the number is a valid answer. An honest "not found", with suggested search terms, beats a plausible number that is wrong.

---

## Known PxWebApi v2 installations

| Agency | Country | Base URL | Languages |
|---|---|---|---|
| Statistics Norway (SSB) | Norway | `https://data.ssb.no/api/pxwebapi/v2` | no, en |
| Statistics Sweden (SCB) | Sweden | `https://statistikdatabasen.scb.se/api/v2` | sv, en |
| Official Statistics Portal of Latvia (CSP) | Latvia | `https://api.stat.gov.lv/api/v2` | lv, en |

All three verified live 2026-09-08. They differ more than the shared API shape suggests — the full comparison is in `references/api-details.md`; the four differences that change how you query:

- **Default data format.** SSB and SCB return json-stat2 when `outputFormat` is omitted; **Latvia returns PX** (`application/octet-stream`). Always set `outputFormat=json-stat2` explicitly.
- **Cell limit.** `maxDataCells` is 800 000 at SSB, 150 000 at SCB and **10 000** at Latvia — an 80× spread. Read it from `/config` every time.
- **Variable names.** The metric is `ContentsCode` on all three, but time is `Tid` (SSB, SCB) or `TIME` (Latvia) and geography is `Region` or `AREA`. Read names from `role` and `id`, never assume.
- **Period codes.** Quarters are `2024K2` at SSB/SCB and `2026Q2` at Latvia; weeks are `2026U35` (SSB), `2026V30` (SCB), `2026W13` (Latvia). Read the codes from metadata before writing a time filter.

These agencies were checked on 2026-08-30 and are **still v1-only** — no v2 endpoint responds at any of the usual URL patterns. Use `generic-pxweb-v1-skill` for them:

| Agency | Country | v1 base URL |
|---|---|---|
| Statistics Finland | Finland | `https://pxdata.stat.fi/PXWeb/api/v1/{fi\|sv\|en}/StatFin` |
| Statistics Iceland | Iceland | `https://px.hagstofa.is/pxis/api/v1/is/{database}` |
| Statistics Faroe Islands | Faroe Islands | `https://statbank.hagstova.fo/api/v1/{fo\|en}/H2` |
| Statistics Greenland | Greenland | `https://bank.stat.gl/api/v1/{da\|en\|kl}/Greenland` |
| Statistics Estonia | Estonia | `https://andmed.stat.ee/api/v1/{et\|en}/stat` |

SSB and SCB each still run their v1 API alongside v2 (`data.ssb.no/api/v0/`, `api.scb.se/OV0104/v1/doris/`), so a v1 URL from a user's old script is not evidence that the agency lacks v2.

**Which version is this installation?**

1. `GET {base}/config` — a v2 installation returns a JSON object with `apiVersion`, `maxDataCells`, `dataFormats`.
2. If that fails, try v1's config, which is a **query parameter, not a path**: `GET {v1_base}?config`. The v1 path form `/config` returns 400.

**Check that the body parses as JSON — do not trust the status code.** Statistics Greenland answers `GET /api/v2/config` with **HTTP 200**, `Content-Type: text/html`, and the body `CONFIG404;…<br>Filen findes ikke - File not found` (re-verified 2026-09-08). A version check that only looks at the status code concludes "v2 exists" and every subsequent call fails confusingly.

**For SSB or SCB queries, prefer the dedicated sibling skills** (`ssb-pxwebapi-v2`, `scb-pxwebapi-v2`) — they have agency-specific examples, curated table catalogs, and operational details that this generic skill does not cover.

---

## API endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/config` | GET | **Call first.** `maxDataCells`, rate limit, `defaultDataFormat`, `dataFormats`, languages, `sourceReferences` |
| `/tables` | GET | Search for a table when you do not know the ID |
| `/tables/{id}` | GET | One table: `firstPeriod`/`lastPeriod`, `timeUnit`, `discontinued` |
| `/tables/{id}/metadata` | GET | Variables, codes and codelists — mandatory before fetching data |
| `/tables/{id}/defaultselection` | GET | The table's default selection — a starting point for large tables |
| `/tables/{id}/data` | GET / POST | Fetch data. POST for complex queries, GET for a shareable URL |
| `/codelists/{id}` | GET | Look up one codelist in isolation |
| `/savedqueries` | POST | Create a shareable, reusable query |
| `/savedqueries/{id}` | GET | The definition of a saved query |
| `/savedqueries/{id}/data` | GET | Run a saved query and get data |
| `/savedqueries/{id}/selection` | GET | The selection of a saved query |

All endpoints accept the `lang` parameter; supported languages depend on the installation. Installation-specific configuration, the rate-limit table and output formats: `references/api-details.md`. The json-stat2 document itself (structure, indexing, `extension`, status codes): `references/json-stat2.md` — the format is shared with Eurostat and other non-PxWeb providers.

---

## Workflow

Follow these steps in order. Never skip the metadata step.

### Step 1: Identify the installation

Determine which PxWebApi v2 installation the user needs. If unclear, ask. Set the base URL, then `GET {base_url}/config` first — the version check above tells you how to read it, and the fields are in `references/api-details.md`.

### Step 2: Search for tables

Use `GET {base_url}/tables` with the `query` parameter.

**Search parameters:**

| Parameter | Type | Description |
|---|---|---|
| `query` | string | Free-text search keywords |
| `pastDays` | int | Limit to tables updated in the last N days |
| `includeDiscontinued` | bool | Include discontinued series (default: false) |
| `pageNumber` | int | Page number for pagination |
| `pageSize` | int | Number of results per page (default: 20) |

**Search tips:**
- Use the agency's local-language terms; add a word from the expected title when the hit list is long
- `title:` restricts to the title field; `AND`, `OR` and `"phrase"~N` work (the engine is Lucene). **The default operator between words differs**: AND at SSB and SCB (`population region` = `population AND region`), OR at Latvia (`population region` = `population OR region`, 494 hits against 125). Write the operator out in any query you intend to share
- **Truncation matches the *stemmed* index term, so truncate short.** `population*` returns **0** hits at Latvia and at SSB's English index; `popul*` returns 203 and 403. Swedish `folkmängd*` returns 0 at SCB, `folkmäng*` returns 117. Cut the word before its ending, and check `page.totalElements` before concluding a table does not exist. A leading wildcard (`*ulation`) returns HTTP 500 at Latvia
- Default `pageSize` is 20. A table in position 47 is never on page 1 — raise `pageSize` or page through

**Screen candidates from the search hit, before spending a metadata call each.** A `/tables` hit carries more than the title:

| Field | Use |
|---|---|
| `variableNames` | The table's variable labels. Lets you reject "wrong breakdown" candidates without fetching metadata at all — the single biggest call saver when several tables match |
| `firstPeriod` / `lastPeriod` | Coverage. These live here, **not** in the json-stat2 dataset |
| `timeUnit` | `Annual`, `Quarterly`, `Monthly`, `Weekly`, `Other`. The **only** place frequency is published — json-stat2 has no field for it. `Other` means the codes are not dates at all (Latvia `IRJ010`: `Time01`) |
| `paths` | Where the table sits in the agency's subject hierarchy, as full breadcrumb arrays. Useful for finding sibling tables and for explaining provenance |
| `discontinued` | Whether the series has stopped — **but see below** |
| `source`, `subjectCode`, `updated`, `category` | Attribution and freshness |

**`discontinued` is not an aliveness test — compare `lastPeriod` with today.** Agencies freeze a table and continue the series in a *new* one without setting the flag: SCB's TAB638 stops at 2024 with `discontinued: null` while TAB6471 carries 2025 onwards. At Latvia the key is absent from the `/tables` hit altogether. If `lastPeriod` is further back than the table's frequency should allow, find the successor before answering. The catalogue can also lag the *other* way: Latvia's `/tables/IRS010m` says `lastPeriod: 2026M04` while the data run to 2026M07 — take "latest" from a `top(1)` on the data, not from the hit.

Present the 3–5 most relevant hits with table ID, title, last period, time frequency, and `discontinued` status.

### Step 3: Explore metadata

Use `GET {base_url}/tables/{id}/metadata` to understand the table structure.

Metadata is returned in json-stat2 format. Focus on:

- **`id` array** — variable names; `size` gives the number of values per variable
- **`dimension` object** — per variable: codes (`category.index`), labels (`category.label`), units (`category.unit`), and `extension` with `elimination` and the available `codelists`
- **`role` object** — **start the analysis here.** `role.metric` is what is measured (`ContentsCode` on all three known installations; read `category.unit` for unit and decimals). `role.time` is the time dimension (`Tid` or `TIME`). **`role.geo` is optional and installation-dependent** — SSB and Latvia set it (`Region`, `AREA`), SCB does not, even on tables with 290 municipalities. Look for a geographic variable in `id` first; only when none exists does the data cover the whole area. Do not ask the user. Remaining variables in `id` are breakdown dimensions
- **`note` array + `extension.noteMandatory`** — table notes, and which of them **must be shown**, keyed by index into `note`. See Step 5
- **`extension` (root)** — `noteMandatory`, `contact`, PX metadata under `extension.px`, and `discontinued` when set. **`firstPeriod`/`lastPeriod`/`timeUnit` are not here** — they are on the `/tables` hit and `GET /tables/{id}`

**Key rules:**

- Read `elimination` **from the metadata response only** — in a data response the field describes the extract you received, not the table's contract. Omitting an eliminable variable removes it from the response entirely (from `id` and `dimension`, not as a total row); note it yourself. Metadata does not distinguish a dimension with a predefined total code from one summed on the fly — scan `category.label` for a total, or probe; `eliminationValueCode` appears only in data responses that include the total (verified on SSB, SCB and Latvia). **Which variables are eliminable is a property of the table, not of the variable name**: `Alder` is optional in SCB's TAB638 and mandatory in TAB6471. Details: `references/json-stat2.md`
- Omitting a variable with `elimination: false` fails with `400 — "Missing selection for mandantory variable"` (the API's own spelling, identical on all three installations; quote it as-is). This is the sharpest v1/v2 difference: **v1 returns all the variable's values instead of failing.**

**Codelists:** group values into higher aggregation levels — `agg_` maps many-to-one, `vs_` is an alternative value set. The codelist's *own* codes are what go in `valueCodes` (read them from `GET /codelists/{id}`), and the response does not record which codelist produced a figure. See `references/codelists-and-filters.md`.

**Default selection:** `GET {base_url}/tables/{id}/defaultselection` is a starting point for large tables. **A `GET /data` with no selection is not an error and does not return the whole table** — it silently returns the default selection, HTTP 200, with eliminable dimensions outside it summed away unannounced. SCB's TAB6471 returns three cells with `Region` **absent from the response entirely**; Latvia's default response also orders `id` differently from the metadata. Always build the selection yourself — figures and verification in `references/troubleshooting.md`.

### Step 4: Build and run query

PxWebApi v2 supports **both GET and POST** for data retrieval. You can also use the agency's web interface to build queries graphically — look for a "Save" or "API query" option to get ready-made GET URLs and POST bodies.

**Always pass `outputFormat=json-stat2` explicitly.** The default is per installation: json-stat2 at SSB and SCB, **PX at Latvia** — a body starting `CHARSET="ANSI";` is what you get when you forget.

#### POST (recommended for complex queries)

The example uses `Region`, `ContentsCode` and `Tid` — Nordic names. At Latvia the same query reads `AREA`, `ContentsCode` and `TIME`. Substitute the actual names from `role.geo`, `role.metric` and `role.time`.

```
POST {base_url}/tables/{id}/data?outputFormat=json-stat2
Content-Type: application/json

{
  "selection": [
    { "variableCode": "Region", "valueCodes": ["01"] },
    { "variableCode": "ContentsCode", "valueCodes": ["Population"] },
    { "variableCode": "Tid", "valueCodes": ["top(5)"] }
  ]
}
```

#### GET (simpler queries, shareable URLs)

```
GET {base_url}/tables/{id}/data?valueCodes[Region]=01&valueCodes[ContentsCode]=Population&valueCodes[Tid]=top(5)&outputFormat=json-stat2
```

#### Filter expressions in valueCodes

All of these work, verified on all three installations: `top(N)` = last N values, `bottom(N)` = first N, `from(code)` = from and including, `to(code)` = up to and including, `range(from,to)` = closed interval, `top(N,offset)` / `bottom(N,offset)` = N values starting `offset` from the end / start, `*` and `?` wildcards (`2025M*` = one year of months), and explicit lists.

**In a GET URL, any expression that contains a comma must be wrapped in square brackets** — `valueCodes[Tid]=[range(2024M01,2024M03)]`, `[top(3,2)]` — because a bare comma is the list separator (`valueCodes[Tid]=2024M01,2024M02`). Unwrapped, `range(...)` returns `400 — "Illegal selection expression"` on every installation, which is easy to misread as the function not existing. Single-argument forms (`top(3)`, `from(2024M01)`) work with or without brackets. **In a POST body it is the other way round:** write the bare string (`"valueCodes": ["range(2024M01,2024M03)"]`); a bracketed string is looked up as a code and fails with `Non-existent value`. Expressions can be mixed with explicit codes (`["2015", "top(2)"]`), but two *function* expressions in one array give the *union* — `["from(2024M01)", "to(2024M03)"]` is 319 periods, not the interval. With curl, pass `-g`: the brackets in `valueCodes[Var]` are otherwise parsed by curl itself (`bad range in URL`) — see `references/troubleshooting.md`.

**For the time dimension, prefer `top(N)` or `from(code)` over `range()` and explicit periods** — relative filters capture new periods automatically, so shareable URLs and saved queries stay current instead of freezing on whatever was latest when they were written. Use `range()` when the closed interval is the point. Full syntax: `references/codelists-and-filters.md`.

#### Output formats

Default `json-stat2`; also `csv`, `xlsx`, `html`, `px`, `json-px`, and at some installations `parquet` — `dataFormats` in `/config` is authoritative, and its spelling matters (Latvia lists `json_stat2` too, which returns 400). Parameters (`UseCodesAndTexts`, `IncludeTitle`, separators, `heading`/`stub`): `references/api-details.md`.

**Important limits:**
- `maxDataCells` from `/config` — 10 000 to 800 000 across the known installations; exceeding it is `400 — "Too many cells selected"`
- Rate limiting: check **both** `/config` and the response headers — SSB announces only in `x-ratelimit-*` headers, SCB and Latvia in `/config` *and* `X-Rate-Limit-*` headers (a different spelling; match both). See `references/api-details.md`
- GET URLs cannot exceed ~2,100 characters — use POST for complex queries
- Start narrow — it's easier to expand than to handle too much data

### Step 5: Present results

- Display data in a clean markdown table
- **Say which dimensions you collapsed and which codelist you used — the response records neither.** If the reader cannot reconstruct your query from your answer, the extract is not reproducible. See "What json-stat2 cannot express" in `references/json-stat2.md`
- **Show mandatory notes.** `extension.noteMandatory` is keyed by index into the root `note` array and travels with the data response, so it costs no extra call. A mandatory note may constrain your own arithmetic — SCB's population tables from 2025 carry disclosure-control noise, so published totals are not the sum of their parts; say so when you sum
- **Always** include source attribution listing **every table ID used** — if multiple tables were combined, list all of them; never omit a source table. `/config` `sourceReferences` gives the agency's own citation string per language
- Explain what the numbers mean in context — in the user's language
- Present units clearly (count, percent, index, currency); for an index, give the base period
- Offer to visualize the data or download in another format. If the data came from SSB and the `ssb-chart-skill` skill is available in the environment, use it for the visualization

### Step 6: Saved queries (optional)

To create a shareable, reusable query:

```
POST {base_url}/savedqueries
Content-Type: application/json

{
  "tableId": "{id}",
  "language": "en",
  "selection": {
    "selection": [
      { "variableCode": "Region", "valueCodes": ["01"] },
      { "variableCode": "ContentsCode", "valueCodes": ["Population"] },
      { "variableCode": "Tid", "valueCodes": ["top(5)"] }
    ]
  },
  "outputFormat": "json-stat2",
  "outputFormatParams": []
}
```

Both `outputFormat` and `outputFormatParams` are required in the savedqueries body — pass `outputFormatParams: []` if you don't need any. Include all non-eliminable variables in the selection, otherwise the API returns HTTP 400. The endpoint exists on all three installations.

Useful for reports that are updated regularly — `top(N)` always returns the latest periods.

---

## Pitfalls — never

The integrity rules at the top always apply — in addition:

- Fetch data without filters and assume you got the table — you get the *default selection*, HTTP 200, with eliminable dimensions summed away unannounced (see Step 3)
- Assume table IDs, variable codes, codelists, limits, default format or period-code letters are the same across installations — re-check `/config` and metadata when switching installation
- Mix codes from different codelists
- Present data without units

---

## Fallback

Common errors and their causes (400 titles, 403, 404, 429, PX instead of JSON, empty search results): `references/troubleshooting.md`.

If the API is not available:

1. **Say plainly that the data could not be fetched.** Never fill the gap with numbers from memory — without API access you deliver guidance, not statistics
2. Refer the user to the agency's web-based statistical database
3. Suggest search terms based on the question
