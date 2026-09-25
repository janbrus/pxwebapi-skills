---
name: generic-pxweb-v1-skill
description: >
  Access official statistics from any PxWebApi v1 installation (the PxWeb 1.0 API).
  Use when querying statistical databases that run the older POST-based PxWeb API —
  base URLs of the form `/api/v1/{lang}/{database}/…`, or SSB's `/api/v0/`.
  Trigger on "PxWebApi v1", "PxWeb v1", "PxWeb API", "PXAPI", "statbank API",
  "Statistikkbanken API", "Statistikdatabasen API", or when a PxWeb URL contains
  `/api/v0/` or `/api/v1/`. Covers hierarchy navigation, table search, metadata,
  the JSON query body (`{"query": […], "response": {…}}`), the item/all/top/agg/vs
  filters, elimination rules, output formats, and error handling.
  For installations already migrated to PxWebApi v2 (SSB `data.ssb.no/api/pxwebapi/v2`,
  SCB `statistikdatabasen.scb.se/api/v2`) prefer `generic-pxweb-v2-skill`,
  `ssb-pxwebapi-v2` or `scb-pxwebapi-v2` instead.
license: MIT. LICENSE has complete terms
metadata:
  version: "0.12.0"
---

# PxWebApi v1 — Generic Skill

This skill guides you through using **PxWebApi v1** (PxWeb 1.0 API) to navigate, explore, and retrieve official statistics. PxWeb is developed by Statistics Sweden (SCB) and used by statistical agencies worldwide. Many installations are still on v1 and have no migration date.

**The single most important fact:** in v1, **data is retrieved with HTTP POST only.** There is no GET data endpoint. A GET against a table URL returns that table's *metadata*, not its numbers.

## Data integrity — the base rule

Official statistics carry an agency's name. A wrong number under that citation damages trust in the agency, not just in the answer. This rule outranks everything else in this skill:

**Never state a number you have not fetched from the API in this conversation.**

- **No numbers from memory.** If you did not run the query, you do not have the number — including numbers you are confident about. Populations, price indices and unemployment rates all move, and training data has a cutoff.
- **No numbers from other sources in the same answer.** Point the user elsewhere rather than blending.
- **If the API fails, say so.** No estimates, no "roughly". See Fallback. This matters more in v1 than in v2: several installations return a bare `Bad Request` with no diagnostic, so a failed call is easy to mistake for an empty result. **The text is localised** — Spain's judicial statistics answer `Solicitud incorrecta`. Do not test for the string; treat any 4xx without a JSON body as a failed request.
- **No interpolation or projection.** A period missing from the extract is missing from the answer.
- **Mark your own calculations.** Growth rates, shares and sums are yours, not the agency's — show which fetched numbers they rest on, and keep the API's decimals.
- **Show `status` values as they are.** Missing, provisional and confidential values belong in the table, not hidden or replaced by zero. In v1 the symbols are defined per PX file (`DATASYMBOL1`–`6`), so they vary between agencies and even between tables — read them, don't assume `.` and `..`.

Not finding the number is a valid answer. An honest "not found", with suggested search terms, beats a plausible number that is wrong.

## Known PxWebApi v1 installations

All base URLs below were verified live on 2026-08-28.

| Agency | Country | Base URL (through DATABASEID) | `?query=` |
|---|---|---|---|
| Statistics Norway (SSB) | Norway | `https://data.ssb.no/api/v0/{no\|en}/table` | yes |
| Statistics Sweden (SCB) | Sweden | `https://api.scb.se/OV0104/v1/doris/{sv\|en}/ssd` | **no** (400) |
| Statistics Finland | Finland | `https://pxdata.stat.fi/PXWeb/api/v1/{fi\|sv\|en}/StatFin` | yes |
| Statistics Iceland | Iceland | `https://px.hagstofa.is/pxis/api/v1/is/{database}` | **no** (400) |
| Statistics Faroe Islands | Faroe Islands | `https://statbank.hagstova.fo/api/v1/{fo\|en}/H2` | yes |
| Statistics Greenland | Greenland | `https://bank.stat.gl/api/v1/{da\|en\|kl}/Greenland` | yes |
| Statistics Estonia | Estonia | `https://andmed.stat.ee/api/v1/{et\|en}/stat` | yes |

Three of the seven break the shape this table implies: **Iceland and Finland each host several databases** rather than one, and Iceland serves English from a different APINAME (`pxen`, not a language swap) — see `references/installations.md` for those and for SSB's `table`, which is a DATABASEID that merely reads like a path segment.

These seven are verified end to end: base URL through DATABASEID, hierarchy walked, `?query=` support probed. **`references/installations.md` holds the broad inventory of 50 known v1 installations** — status, languages and `?config` limits, most of them probed only to the LANGUAGE level. Look there when the user names an agency missing from this table, then walk its hierarchy as in Step 1; and if it appears in neither list, probe it rather than assuming it does not exist.

**Note:** SSB serves PxWebApi **1.0 at `/api/v0/`** — the `v0` is the URL's API-version segment, not a beta marker. SSB also runs v2 in parallel at `https://data.ssb.no/api/pxwebapi/v2`; so does SCB. When an installation offers both, prefer v2 (`generic-pxweb-v2-skill`) unless the user specifically wants v1.

---

## How v1 differs from v2

If you know PxWebApi v2, read this table before doing anything else. The **response** format is nearly identical (both return json-stat2); the **request** shape and the **discovery** endpoints are completely different.

| | **v1** | **v2** |
|---|---|---|
| Data retrieval | **POST only** | GET or POST |
| Metadata | `GET {table_url}` (same URL you POST to) | `GET /tables/{id}/metadata` |
| Request body key | `{"query": [ … ], "response": {"format": …}}` | `{"selection": [ … ]}` |
| Selection object | `{"code": …, "selection": {"filter": …, "values": […]}}` | `{"variableCode": …, "valueCodes": […]}` |
| Output format | `"response": {"format": "json-stat2"}` in the body | `?outputFormat=json-stat2` in the query string |
| Filters | `item`, `all`, `top`, `agg:X`, `vs:X` | `top(n)`, `bottom(n)`, `from(x)`, `to(x)`, `range(a,b)`, `*`, `?` |
| Codelists / aggregations | **not in metadata** — must be known in advance | `extension.codelists` + `GET /codelists/{id}` |
| Units, decimals, `role` in metadata | no (present in the json-stat2 *data* response only) | yes |

See `references/v1-vs-v2.md` for a migration guide in both directions.

---

## Environment check — before Step 1

v1 data retrieval needs an HTTP **POST** with a JSON body. Confirm you have a tool that can send one before starting the workflow — otherwise you can burn many calls discovering this only at the end.

- **Bash/shell with network access to the host**, or an MCP tool that wraps HTTP with POST support → `curl -X POST` works. Proceed normally.
- **A GET-only web-fetch tool** (e.g. one restricted to URLs already seen in a search result) **cannot** send the body v1 needs. It reaches metadata, hierarchy listings and `?config` — never the data cube.

Without POST, say so plainly and still do the GET-only parts: Steps 1–2 identify the installation, walk the hierarchy and read the variable codes without ever needing POST. Then go to **Fallback** for the figures themselves. State clearly that you could not retrieve them in this environment — do not substitute numbers from memory or from a third-party aggregator.

---

## Workflow

Follow these steps in order. Never skip the metadata step — v1 metadata is thin, and variable codes are wildly installation-specific.

### Step 1: Identify the installation and its base URL

The v1 URL is assembled from fixed parts:

```
{host}/{APINAME}/{APIVERSION}/{LANGUAGE}/{DATABASEID}/{LEVEL1}/…/{LEVELN}/{TABLEID}
```

For example `https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0101/BE0101A/BefolkManadCKM`, where `OV0104` is APINAME, `v1` is APIVERSION, `doris` is a routing segment, `sv` is LANGUAGE and `ssd` is DATABASEID.

If you do not know an installation's base URL, walk it down from the top: a GET on `.../{APIVERSION}/{LANGUAGE}` lists the databases, and a GET on `.../{LANGUAGE}/{DATABASEID}` lists the first level. Every level returns a JSON array of nodes.

**Always start with `?config`.** v1 exposes its limits as a **query parameter on the LANGUAGE level**, not as a `/config` path segment (`/config` as a path returns 400 — that is why it is easy to conclude the endpoint does not exist):

```
GET {host}/{APINAME}/{APIVERSION}/{LANGUAGE}/?config
→ {"maxValues": {n}, "maxCells": {n}, "maxCalls": {n}, "timeWindow": {seconds}, "CORS": true}
```

The field *names* are the point; the values are not. Real figures for the installations probed so far are in `references/api-details.md` and `references/installations.md` — never carry one installation's numbers to another.

| Field | Meaning |
|---|---|
| `maxCells` | Maximum cells per query — the product of all selected value counts |
| `maxValues` | Maximum **selected values** per query, counted across variables — a separate ceiling |
| `maxCalls` / `timeWindow` | Rate limit: `maxCalls` requests per `timeWindow` seconds |
| `CORS` | Whether browser clients can call the API directly |

Every v1 installation probed so far answers it, so treat it as universal rather than as a feature some agencies happen to offer. Estonia is the one quirk: it needs the URL without a trailing slash (`.../et?config`).

Three things to know about what comes back:

- **`maxCells` is sometimes missing.** Absence is not "no cell limit" — the 403 still fires; you just have to find the ceiling by bisection.
- **Check your query against the ceilings before sending it.** Cells are the *product* of the selected value counts, values their *sum*. From a metadata response that is `prod(len(v["values"]))` and `sum(len(v["values"]))` over the variables you did not restrict — cheaper than discovering the limit as a 403.
- **`maxValues` and `maxCells` are independent ceilings, and the tighter one varies by installation.** Selecting `*` on a large variable can breach the value ceiling while the cell count still looks safe. The limits also spread across roughly two orders of magnitude between installations, so a query shaped for one agency can fail outright at another — the measured table is in `references/api-details.md`.
- **Do not take a limit from anywhere else.** Agencies' published figures and third-party catalogues disagree with `?config` routinely, in both directions. SSB is the clean example: its own documentation says 30 calls/60 s, `?config` says 300. `?config` wins — it reports what the installation *enforces*, while the others record what someone *published*.

### Step 2: Find the table

Two routes. Use search where it exists; otherwise navigate.

**a) Navigate the hierarchy (works everywhere).** GET any level to list its children:

```
GET {base_url}/BE
→ [{"id":"BE0001","type":"l","text":"Namnstatistik"},
   {"id":"BE0101","type":"l","text":"Befolkningsstatistik"}, …]
```

Each node has `id`, `text` and `type`:

| `type` | Meaning |
|---|---|
| `l` | a sub-level — append its `id` to the URL and GET again |
| `t` | a **table** — this is a POST target |
| `h` | a heading (display only, not navigable) |

Table nodes usually also carry `updated`. On several installations the table `id` includes a **`.px` extension** that is part of the URL (Finland `11ra.px`, Faroe `fo_sogtol.px`, Greenland `BEXSTA.px`, Estonia `RL101.PX`) — SSB and SCB do not use it. Always use the `id` exactly as returned.

That extension is a tell. **Most PxWeb installations store each table as a flat PX file on disk; only SSB and SCB run off a relational database.** File-based installations expose the `.px` in the URL and keep their aggregations and valuesets as separate `.vs`/`.agg` files that the API never exposes. See `references/px-files-and-classifications.md`.

**b) Search with `?query=` (installation-dependent).** Where supported, append `?query=` to any level URL to search that subtree:

```
GET {base_url}/?query=title:population*
```

Search is Lucene-based (Apache Lucene.NET query syntax), case-insensitive, and space means AND. It searches titles *and* variable value texts by default. Hits come back as `{"id", "path", "title", "score", "published"}` — note the `path`, which you must append to the base URL to build the POST target.

**Search is not universally available.** SCB and Statistics Iceland return `400 Bad Request` for `?query=`. Probe once; if it 400s, navigate the hierarchy instead.

See `references/api-details.md` for the full search syntax (field prefixes, truncation, proximity, date searches, URL-encoding).

**Beware:** the same table can appear under several subject paths, so a search may return apparent duplicates with identical `id` and `title` but different `path`. Any of them works as a POST target.

### Step 3: Read the table's metadata

```
GET {table_url}
```

The same URL you will POST to. The response is deliberately minimal:

```json
{
  "title": "07459: Befolkning, etter region, kjønn, alder, statistikkvariabel og år",
  "variables": [
    { "code": "Region", "text": "region",
      "values": ["0", "31", "3101", …], "valueTexts": ["Hele landet", "Østfold", …],
      "elimination": true },
    { "code": "ContentsCode", "text": "statistikkvariabel",
      "values": ["Personer1"], "valueTexts": ["Personer"] },
    { "code": "Tid", "text": "år",
      "values": ["1986", …, "2026"], "valueTexts": ["1986", …, "2026"],
      "time": true }
  ]
}
```

Each variable object has `code` and `text` (both required), plus optional `elimination` and `time` — **when absent, both default to `false`**. `values` and `valueTexts` are positionally aligned: `values[i]` is the code you put in a query, `valueTexts[i]` is its human label. At most one variable may have `time: true`. Installations may add fields of their own — Statistics Finland attaches `map` (e.g. `"Alue 2026"`) to its geography variable — so read what is there rather than assuming this list is complete. There is **no** field naming the elimination value; that gap is real, and Step 4 explains how to work around it.

**`time: true` tells you nothing about the frequency, and does not guarantee the codes are dates.** The PX file's time scale (`TLIST`) is discarded by v1, and json-stat2 has no field for it either, so read the frequency off the shape of `values` and never construct a code from a pattern you have not seen in that table. Statistics Greenland has a `time: true` variable whose codes are `0`–`50`, with the years only in `valueTexts`. `references/query-syntax.md` has the period formats and the full TLIST story.

**Never assume variable names.** The Nordic convention `Region` / `ContentsCode` / `Tid` holds at SSB and SCB but nowhere near universally — Statistics Finland uses `alue_23_20260101`, `contentscode` and `timeperiod_y` in the same role, and the geography code even embeds a classification date that changes between table versions. Statistics Greenland uses lowercase English words, **including codes that contain spaces** (`place of birth`). Statistics Iceland's *English* endpoint returns codes still in Icelandic, accents and all — `Ár` and `Eining` where you would expect `Tid` and `ContentsCode` — so an English URL is no guarantee of English codes. Read `variables[].code` every time and copy it verbatim into `"code"`.

**What v1 metadata does *not* tell you** — plan around these gaps:

- **No `role`.** You must infer which variable is the metric, the time and the geography. The time variable is the one with `time: true`. The metric is usually the one named like `ContentsCode`/`contentscode`; otherwise it is the variable whose `valueTexts` read as measures ("Persons", "Index", "NOK"). Geography is whatever looks like regions. *The json-stat2 data response usually does include `role`* — so if you are unsure, run a tiny `top`-1 probe query and read `role` off the result. Do not count on it: Greenland's `BEXSAT1.PX` returns **no `role` key at all** (verified 2026-09-04), because its metadata sets no `time: true` on the variable it literally calls `time`. When the probe comes back without `role`, fall back to reading the title and `valueTexts`.
- **There may be no metric variable at all.** Many tables outside the Nordic core have no `ContentsCode`-equivalent: the whole table measures one thing, named only in the title. Statistics Greenland's `BEXST8.px` has variables `age`, `place of birth`, `gender`, `time` and nothing else — its data response comes back with `role: {"time": ["time"]}`, no `metric` and no `geo`. When `role.metric` is absent, do not hunt for it: read the measure off the table title and the subject level, and say so explicitly when presenting.
- **No units or decimals.** Also only in the data response (`dimension.{metric}.category.unit`) — and some installations omit `unit` there too.
- **No codelists or aggregations.** Groupings such as five-year age bands or merged-municipality time series exist and are usable via the `agg:` filter, but are invisible here — on file-based installations they are separate `.vs`/`.agg` files that the API never reads. See `references/query-syntax.md` for how to discover them and `references/px-files-and-classifications.md` for how they are structured.
- **Which route gives you a total.** `elimination: true` usually means the total is *not* in `values` and you get it by omitting the variable — but some tables offer both routes (Greenland's `age` has an explicit `-1` = "Total" *and* `elimination: true`; verified to give the same figure either way), some offer only an explicit code (SCB's `TotSA`/`TotSa`), and some only omission (SSB's `Kjonn` in 07459). Scan `valueTexts` for "Total" / "I alt" / "Hele landet" before deciding. See `references/query-syntax.md`.

### Step 4: Build the query and POST it

```
POST {table_url}
Content-Type: application/json

{
  "query": [
    { "code": "Region",       "selection": { "filter": "item", "values": ["0301"] } },
    { "code": "ContentsCode", "selection": { "filter": "item", "values": ["Personer1"] } },
    { "code": "Tid",          "selection": { "filter": "top",  "values": ["3"] } }
  ],
  "response": { "format": "json-stat2" }
}
```

`"query"` is an array of selection objects. `"response"` is optional — **and omitting it gives three different formats across the seven verified installations**, so always set it explicitly. Measured 2026-09-04: SSB, Finland and Estonia return `json-stat2`; SCB and Greenland return PX; the Faroe Islands and Iceland return PX-JSON. The spec says PX; that is true of two installations out of seven.

The PX-JSON case is the dangerous one, because it *is* JSON — a check like "did I get JSON back?" passes, and only then do you find there is no `value`, `dimension` or `id`, just `columns` / `data` / `metadata` in a completely different shape. Set `"response"` and this never arises.

#### Filters

| `filter` | Meaning | `values` |
|---|---|---|
| `item` | Explicit list of value codes | `["0301", "1103"]` |
| `all` | Wildcard match | `["*"]` = all; `["202*"]` = codes starting with 202 |
| `top` | The N newest (for `time: true`) or first N values | `["5"]` — a single positive integer as a **string** |
| `agg:{name}` | Values come from aggregation `{name}` — if you got the name from v2, drop its `agg_` prefix (`agg_KommFylker` → `agg:KommFylker`); keeping it gives `Parameter error` | `["F-03", "F-11"]` |
| `vs:{name}` | Values come from alternative value set `{name}` | `["01", "02"]` |

Verified live against SSB and SCB: `agg:` takes only explicit codes (never `*`), `?` single-character masking does not exist in any filter, and several wildcards in one `all` list do work on current builds despite the spec saying otherwise. Aggregation and valueset names are filenames, so a name valid on one table is often invalid on another. Details and verification: `references/query-syntax.md`.

Two things worth knowing before you reach for `agg:`:

- `top` is the tool for **rolling queries** — a stored `top` query keeps returning the newest periods as data is published, whereas an `item` list of future dates errors out.
- **`extension.px.aggregallowed` is a hint, not a prediction.** Read it from any small query's response, but do not plan around it: it is **absent entirely** at Iceland, the Faroes and Estonia, and where it is `false` the installations disagree about what that means — SSB rejects `agg:` with 400, SCB serves the data anyway (verified across all seven, 2026-09-03/04). Send the query and handle the answer. See `references/px-files-and-classifications.md`.
- **Before concluding you need `agg:` at all, look at the code shapes in `values`.** Hierarchical classifications usually carry their own levels as ordinary item codes, so the grouping you want may already be selectable: SSB 14700's `VareTjenesteGrp` runs `00` (total) → `01` (main group) → `01.1` → `01.1.1`, and 07459's `Region` runs 1 digit (country) → 2 (county) → 4 (municipality). An `item` selection of the right code length gives you the level directly. This does **not** replace `agg:` for consistent time series — 07459 lists 41 two-digit county codes because it keeps historical ones, so selecting them all mixes boundaries across reforms, which is exactly what `agg:KommFylker` exists to fix.

#### Elimination — omitting a variable

Leaving a variable out of `"query"` is normal and useful. What you get back depends on its `elimination` flag (rules from the PxWeb 1.0 spec, verified live):

1. `elimination: true` **and** the variable has an elimination value → only that total is returned.
2. `elimination: true` **but** no elimination value → all its values are aggregated into one.
3. `elimination: false` (including when the property is absent) → **all** of the variable's values are returned.

Rule 3 is the one that bites. On SCB's `BefolkManadCKM`, omitting `Alder` (`elimination` absent) returns all **134** age values rather than a total. Omitting a `time` variable returns the entire time series — deliberately used to build queries that never need updating.

An empty query `{"query": [], "response": {…}}` is legal and applies these rules to every variable. On a municipality-level table that typically yields whole-country totals for all periods.

**Eliminated variables disappear from the response entirely** — they are absent from `id` and `dimension`, not present with size 1. The response therefore does not record what was aggregated away, so state it yourself when presenting.

#### Output formats

Set in the body as `"response": {"format": "…"}`.

| Format | Notes |
|---|---|
| `json-stat2` | **Recommended.** Rich metadata, logical element order, handles large extracts. |
| `px` | PC-Axis PX. The spec's default when `response` is omitted — but only two of seven installations actually do that. |
| `csv3` | Codes only. The most robust CSV. |
| `xlsx` | Excel. Avoid for large extracts — prone to timeouts. |

**Format names are hyphenated**: `json-stat2` and `json-stat` work, `jsonstat2` and `jsonstat` return 400, and the published spec giving the unhyphenated spellings is simply outdated. The other formats (`json-stat`, `csv2`, `csv`, `json`, `sdmx`), their CSV conventions, and the fact that availability varies by agency: `references/api-details.md`.

### Step 5: Present results

- Display data in a clean markdown table.
- **Always** cite every table used — e.g. "Source: {Agency}, table {id}". Never omit a source table when combining several.
- State units explicitly. v1 metadata has none, so take them from `dimension.{metric}.category.unit` in the json-stat2 response, or from the metric's `valueTexts`. **Both can be missing** — then the unit lives only in the table title, and you must name it yourself rather than presenting bare numbers.
- Say which variables you eliminated and what that means ("all ages and both sexes combined") — the response will not.
- Check `status` for suppressed or missing values before drawing conclusions.
- Explain the numbers in context, in the user's language.

The json-stat2 structure itself — row-major indexing, `role`, units, and the `status` symbols — is in `references/json-stat2.md`.

---

## Pitfalls — never

- Try to fetch data with GET — v1 has no GET data endpoint; a GET returns metadata.
- Rely on the default output format — omitting `"response"` yields PX, PX-JSON or json-stat2 depending on the installation. Always set it.
- Use `jsonstat2`/`jsonstat` as format names — they are rejected; use `json-stat2`/`json-stat`.
- Assume variable codes (`Region`, `ContentsCode`, `Tid`) carry across installations — read metadata every time.
- Assume an omitted variable is summed — if `elimination` is false or absent, you get *all* its values.
- Combine `agg:` with `*`, or use `?` masking — both fail.
- Present data without units, or without saying which dimensions were collapsed.
- Fetch a whole large table without filters — the cell limit rejects it with 403.

---

## Fallback

- **A call failed?** `references/troubleshooting.md` has the verified HTTP codes and how to tell v1's three distinct error payloads apart — including the bare `Bad Request` that carries no diagnostic at all.
- **The query cannot be expressed, or the aggregation name is unknown?** Refer the user to the agency's web statistical database. Most PxWeb front ends offer an **"API query for this table"** button that emits a ready-made v1 query body — the fastest route to aggregation names metadata never exposes, and the thing to hand a user when your own environment cannot POST.
- **Wondering why a classification is invisible?** Most installations are file-based, which is why `.px` appears in their URLs and why their `.vs`/`.agg` classifications are undiscoverable through the API. `references/px-files-and-classifications.md` covers that, and the PX keywords behind the metadata you do see — `ELIMINATION`, whose two forms are exactly the first two elimination rules, and `AGGREGALLOWED`.
