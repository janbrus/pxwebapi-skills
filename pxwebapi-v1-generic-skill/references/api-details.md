# API details (PxWebApi v1)

URL structure, hierarchy navigation, search syntax, output formats and limits.
For the request body see `query-syntax.md`; for the response see `json-stat2.md`.

---

## URL structure

```
{host}/{APINAME}/{APIVERSION}/{LANGUAGE}/{DATABASEID}/{LEVEL1}/…/{LEVELN}/{TABLEID}
```

| Segment | Meaning |
|---|---|
| `APINAME` | Root name of the API. Often `api`; SCB uses `OV0104`. A GET here returns an info page or 404. |
| `APIVERSION` | `v1` on most installations, **`v0` at SSB**. A GET here returns an info page or 404. |
| `LANGUAGE` | Language id. A GET lists the available databases. |
| `DATABASEID` | The PC-Axis database. A GET lists its first level. |
| `LEVEL1…LEVELN` | Zero or more subject levels. A GET lists children. |
| `TABLEID` | A table. GET returns metadata, POST returns data. |

Examples verified live on 2026-08-28:

```
https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0101/BE0101A/BefolkManadCKM
https://data.ssb.no/api/v0/no/table/07459
https://pxdata.stat.fi/PXWeb/api/v1/fi/StatFin/vaerak/11ra.px
https://bank.stat.gl/api/v1/en/Greenland/BE/BE01/BE0120/BEXSTA.px
```

Switching language is usually a matter of swapping one segment (`/no/` → `/en/`); value codes stay
the same while `valueTexts` and titles change. It is not universal, though — Statistics Iceland
serves English from a **different APINAME**, `https://px.hagstofa.is/pxen/api/v1/en`, and returns
400 for `.../pxis/api/v1/en`. If a language swap 400s, try the APINAME segment before concluding
the language is unavailable.

### Table id quirks

- **`.px` extension.** Statistics Finland, the Faroe Islands, Greenland and Estonia return table
  ids with a `.px` (or `.PX`) suffix that is part of the URL. SSB and SCB do not. Use the `id`
  exactly as returned by the listing.
- **SSB shortcut.** SSB accepts a 5-digit table number directly after `table/`, skipping the
  subject path: `https://data.ssb.no/api/v0/no/table/11000`. This form is **more stable over
  time** than the full path, because subject hierarchies get reorganised while table numbers do
  not. SSB also accepts the internal table name (`.../table/KPI`).
- **Two identifiers per table.** PxWeb distinguishes the internal table name (`id`, e.g. `KPI`,
  `Framskr2018T2`) from the public table number that appears at the start of `text`/`title`
  (e.g. `11668`). Both may be usable in a URL depending on the installation.

---

## Navigating the hierarchy

A GET on any non-table level returns a flat JSON array of nodes:

```json
[ {"id": "be",  "type": "l", "text": "Befolkning"},
  {"id": "XX",  "type": "h", "text": "Population heading"},
  {"id": "11ra.px", "type": "t", "text": "11ra -- Tunnuslukuja väestöstä alueittain, 1990-2025",
   "updated": "2026-07-01T18:34:16"} ]
```

| `type` | Meaning |
|---|---|
| `l` | Sub-level — append `id` and GET again |
| `t` | Table — a POST target; `text` is the full title, usually `number: description` |
| `h` | Heading — display only, not navigable |

Table nodes carry `updated`. Discontinued series are often collected in a sub-level alongside
live tables at the same depth, so check titles for markers such as "avslutta" / "discontinued"
before using a series.

Two things not to trust in `text`:

- **It may contain HTML.** Statistics Greenland appends the table's internal id wrapped in
  emphasis tags — `"Population by Place of Birth 1977-2026 <em>[BEEST8]</em>"` — in the plain
  hierarchy listing, not only in search results. Strip tags before displaying a title.
- **The stated period may be wrong.** That same table's title claims 1977-2026 while its `time`
  variable holds 1994-2026. Take the actual coverage from metadata, never from the title.

A GET at the database level lists databases:

```json
[{"dbid": "ssd", "text": "Statistics Sweden"}]
```

---

## Search with `?query=`

Append to **any** level URL to search that subtree. Backed by Apache Lucene.NET 2.9.4 query
syntax, case-insensitive, whitespace means AND. By default it searches table titles *and*
variable value texts.

**Availability is not universal.** Verified 2026-08-28: SSB, Statistics Finland, the Faroe
Islands, Greenland and Estonia support it; SCB and Statistics Iceland return `400 Bad Request`.
Probe once, then fall back to hierarchy navigation.

### Result shape

```json
[ {"id": "KPI",
   "path": "/if/if01/kpi/SBMENU4900",
   "title": "03013: Konsumprisindeks, etter konsumgruppe (2015=100) (avslutta serie) 1979M01 - 2025M12",
   "score": 3.02554584,
   "published": "2026-01-09T08:00:00"} ]
```

Build the POST target as `{base_url}{path}/{id}`. Because a table can be filed under several
subjects, the same `id` and `title` may appear multiple times with different `path` values — they
are duplicates, and any one of them works.

### Syntax

| Pattern | Meaning | Example |
|---|---|---|
| `word1 word2` | AND | `?query=funksjon AND 170` |
| `field:term` | Restrict to a field | `?query=title:indeks` |
| `term*` | Truncation | `?query=title:trend anlegg*` |
| `"a b"~5` | Proximity — within 5 words | `?query="varenummer hs"~5` |
| `NOT term` | Exclusion | `?query=alder NOT avslutta` |
| `published:YYYYMMDD*` | Search by publication date, future dates included | `?query=published:20180504*` |
| `published:A TO B` | Date interval | `?query=published:20190301 TO 20190401` |
| `*` with `&filter=*` | List everything — the whole database structure | `?query=*&filter=*` |
| `&filter=codes` | Search **value codes** rather than titles and texts | `?query=KU091&filter=codes` |
| `&filter=title` | Restrict to titles | `?query=trend&filter=title` |
| `\(` `\)` | Escape parentheses in the term | `?query=\(B\) NOT avslutta` |

Truncation matters more than it looks: `?query=title:boligpris` returns **0 hits** at SSB while
`?query=title:boligpris*` returns matches. Terms are matched whole unless truncated.

Searching by the table number in the title is the quick way to resolve a number to its path and
last publication date: `?query=title:03013`.

URL-encode as usual — space is `%20`, and `"` `(` `)` `[` `]` become `%22 %28 %29 %5B %5D`.

`&filter=codes` is the one worth remembering: it searches the **value codes** inside tables, so
`?query=KU091&filter=codes` finds every table containing Helsinki's municipality code (179 hits at
Statistics Finland). That is the fastest way to answer "which tables break this down by X?" when
you know X's code but not which tables use it.

Scope the search by starting from a subject level rather than the root:
`{base_url}/be/?query=hattfjelldal` searches only under Population.

---

## Output formats

Requested in the body, never the query string:

```json
"response": { "format": "json-stat2" }
```

| Format | Version / shape | Notes |
|---|---|---|
| `json-stat2` | json-stat 2.0 | **Recommended.** Logical element order; handles the largest extracts. |
| `json-stat` | json-stat 1.2 | Legacy. Random element order; struggles near the cell limit. |
| `csv3` | codes only | Header = variable codes + table id. Most robust; no locale-specific characters. |
| `csv2` | pivoted, texts | Header = all variables; one value per row. |
| `csv` | legacy | Single header row of variable names and content. Not recommended. |
| `px` | PC-Axis | **Default when `response` is omitted.** |
| `xlsx` | Excel | Fine for end users; times out on large extracts. |
| `json` | PX-JSON | `{"columns": […], "data": [{"key": […], "values": […]}]}` — see below. |
| `sdmx` | SDMX-ML | XML. |

**Spelling is hyphenated.** `json-stat2` and `json-stat` are accepted; `jsonstat2` and `jsonstat`
return `400 {"error":"Parameter error"}` on both SSB and SCB. Much published documentation,
including the official PxWeb 1.0 specification, gives the unhyphenated forms — they are outdated.

**Availability varies.** PxWeb implements all of the above, but agencies disable formats
individually. SSB's own user guide states that `json` (PX-JSON), `px` and `sdmx` are unsupported
there, although the endpoint currently answers 200 for all three — treat undocumented formats as
unsupported for production even when they respond.

CSV conventions in PxWebApi: comma field separator, `.` decimal separator, text fields quoted.
This differs from the semicolon/comma conventions used by some agencies' separate "ready-made
dataset" APIs. Decimal separator is `.` in every format and language; the exception is Excel
output under some locales, which uses the locale's separator.

For flexible CSV, prefer requesting `json-stat2` and converting locally — the json-stat Toolkit's
`jsonstat2csv` (Node.js) lets you pick separators and decimal characters yourself.

### PX-JSON (`format: "json"`)

A compact key/value shape, unrelated to json-stat:

```json
{ "columns": [ {"code": "region", "text": "Region"},
               {"code": "period", "text": "Time", "type": "t"},
               {"code": "x", "text": "Population", "type": "c", "unit": "amount"} ],
  "comments": [ {"variable": "period", "value": "2005", "comment": "Preliminary figures"} ],
  "data": [ {"key": ["02", "2003"], "values": [100]},
            {"key": ["02", "2004"], "values": [101], "comment": ["Imputed"]} ] }
```

Column `type` is `d` (dimension, the default), `t` (time) or `c` (content). `unit` is meaningful
only when `type` is `c`. Key values follow column order; `values` follows the order of the
`type: "c"` columns.

---

## Limits and the `?config` endpoint

v1 **does** publish its limits — as a **query parameter on the LANGUAGE level**, not as a `/config`
path segment. `.../{LANGUAGE}/config` returns 400, which makes it easy to conclude wrongly that no
such endpoint exists:

```
GET https://pxdata.stat.fi/PXWeb/api/v1/en/?config
→ {"maxValues":120000,"maxCells":120000,"maxCalls":40,"timeWindow":60,"CORS":true}
```

| Field | Meaning |
|---|---|
| `maxCells` | Maximum cells per query — the product of all selected value counts, empty cells included |
| `maxValues` | Maximum number of **selected values** across the query — an independent ceiling |
| `maxCalls` | Requests allowed per `timeWindow` |
| `timeWindow` | Rate-limit window in seconds |
| `CORS` | Whether browsers may call the API cross-origin |

Verified on every installation in the inventory, 2026-08-28:

| Agency | `maxCells` | `maxValues` | `maxCalls` | `timeWindow` |
|---|---:|---:|---:|---:|
| Statistics Estonia | 25,000,000 | 25,000,000 | 1,000 | 10 s |
| Statistics Faroe Islands | 8,000,000 | 8,000,000 | 1,000,000 | 1,000,000 s |
| Statistics Greenland | 2,000,000 | 1,000,000 | 10,000 | 10 s |
| Statistics Norway (SSB) | 800,000 | 50,000 | 300 | 60 s |
| Statistics Sweden (SCB) | 150,000 | 110,000 | 30 | 10 s |
| Statistics Finland | 120,000 | 120,000 | 40 | 60 s |
| Statistics Iceland | 100,000 | 5,000 | 200 | 10 s |

Estonia answers only without a trailing slash (`.../api/v1/et?config`); the others accept either.

**`?config` beats the published documentation**, which diverges from it in both directions: SSB's
user guide states 30 calls / 60 s where `?config` reports 300 (re-confirmed 2026-09-03), and
Statistics Finland's help page states 100,000 cells where `?config` reports 120,000 — the latter
settled by bisection against the live endpoint, 117,000 accepted and 124,800 refused. Read
`?config` at the start of a session and believe it over every other source.

**Watch `maxValues` separately from `maxCells`.** They are independent, and the tighter one varies
by installation: Iceland permits 100,000 cells but only 5,000 selected values, SSB 800,000 cells
but only 50,000 values. A `{"filter": "all", "values": ["*"]}` on a large variable can breach the
value ceiling while the cell count still looks comfortable.

Practical guidance:

- Run large queries **in sequence** — wait for each response before sending the next. Parallel
  bursts trip the rate limiter faster than the cell limit.
- Cell count is the product of the selected value counts across all variables, so an
  accidentally non-eliminated breakdown multiplies it without warning.
- Avoid the minutes right after a publishing deadline. SSB publishes at 08:00 CET; its guidance
  is to avoid 07:55–08:15, when first-request latency can reach 30 seconds while caches fill.
- Requests are logged per caller IP (table, cell count) — rate limits are enforced per IP.

---

## Short-form table URLs

Newer PxWeb builds accept a table id **without its subject levels**, which is far more stable than
a full path:

```
https://pxdata.stat.fi/PXWeb/api/v1/en/StatFin/kuol/12af.px   # with levels
https://pxdata.stat.fi/PXWeb/api/v1/en/StatFin/12af.px        # short form — GET and POST both work
```

Verified at Statistics Finland for metadata GET and data POST alike; SSB's `/table/{5-digit number}`
shortcut is the same idea. Statistics Finland's own guidance is that the full path "will still work
more reliably", so prefer levels for anything long-lived and treat the short form as a convenience.

---

## Authenticated (chargeable) databases

Some agencies expose paid databases through the same API. At Statistics Finland
(`pxhopea2.stat.fi`) credentials go **in the URL** for GET, separated by `|` (URL-encoded `%7C`):

```
https://{server}/PxWeb/api/v1/{lang}/%7C{USERNAME}%7C{PASSWORD}
https://{server}/PxWeb/sq/{saved_query_name}%7C{USERNAME}%7C{PASSWORD}
```

and **in headers** for POST — header `un` for the username, header `pw` for the password. Nothing
else about the request changes. Treat such credentials as secrets: they appear in server logs and
browser history when passed in a URL.

## Related APIs on the same hosts

Agencies frequently run a simpler "ready-made dataset" API beside PxWebApi — SSB's is
`https://data.ssb.no/api/v0/dataset/`. Those serve fixed, pre-built datasets over **GET** with no
ability to select subsets, usually in json-stat 1.2 and CSV, and are better cached. When a
ready-made dataset covers the need, it is the cheaper choice; when it does not, PxWebApi v1 is
the flexible one.

Classification services are separate again — SSB's Klass API
(`https://data.ssb.no/api/klass/v1/`) resolves the `urn:ssb:classification:klass:N` URNs that
appear in json-stat2 responses.
