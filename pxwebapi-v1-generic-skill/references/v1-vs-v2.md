# PxWebApi v1 vs v2

A translation guide for people who know one version and need the other, and for installations
that run both. The sibling skill `generic-pxweb-v2-skill` covers v2 in its own right.

The headline: **the response formats are nearly identical, the requests are not.** 

Both versions return json-stat2 datasets with the same `id` / `size` / `dimension` / `value` / `role` /
`status` structure, so any parsing or charting code carries over unchanged. Everything on the
request side — endpoints, body shape, filters, discovery — differs.

---

## Endpoint map

| Purpose | v1 | v2 |
|---|---|---|
| API limits and capabilities | `GET …/{LANGUAGE}/?config` — a **query parameter**, not a path | `GET /config` — a path segment |
| List databases | `GET /{apiname}/{apiversion}/{lang}` | *(n/a — flat table space)* |
| Browse subjects | `GET …/{db}/{level}/…` | *(n/a)* |
| Search tables | `GET …?query=…` *(where supported)* | `GET /tables?query=…&pageSize=…` |
| Table info | *(part of metadata)* | `GET /tables/{id}` |
| Table metadata | `GET {table_url}` | `GET /tables/{id}/metadata` |
| Default selection | *(none)* | `GET /tables/{id}/defaultselection` |
| **Get data** | **`POST {table_url}`** | `GET` or `POST /tables/{id}/data` |
| Look up a codelist | *(none)* | `GET /codelists/{id}` |
| Saved queries | *(none — only PxWeb's web "saved query" links, e.g. SSB's `ssb.no/statbank/sq/{id}`)* | `POST /savedqueries`, `GET /savedqueries/{id}/data`. At SSB the v1-era web IDs resolve here too: `GET /savedqueries/10119120` returns the definition and `/data` the file (verified 2026-09-09) — the route for a user who arrives with an old sq link, since the PxWeb v2 web page for it no longer serves csv/xlsx |

v1's table space is a **tree**: a table is addressed by its full subject path. v2's is **flat**:
a table is addressed by id alone. SSB's `/table/{5-digit number}` shortcut is a v1 installation
approximating the flat model, and it is the more stable URL form precisely because subject
hierarchies get reorganised.

---

## Request body

**v1** — the selection lives under `"query"`, the format inside the body:

```json
{ "query": [
    { "code": "Region",       "selection": { "filter": "item", "values": ["0301"] } },
    { "code": "ContentsCode", "selection": { "filter": "item", "values": ["Personer1"] } },
    { "code": "Tid",          "selection": { "filter": "top",  "values": ["5"] } } ],
  "response": { "format": "json-stat2" } }
```

**v2** — the selection lives under `"selection"`, the format in the query string:

```
POST /tables/07459/data?outputFormat=json-stat2
```
```json
{ "selection": [
    { "variableCode": "Region",       "valueCodes": ["0301"] },
    { "variableCode": "ContentsCode", "valueCodes": ["Personer1"] },
    { "variableCode": "Tid",          "valueCodes": ["top(5)"] } ] }
```

Field-by-field: `code` → `variableCode`; `selection.values` → `valueCodes`; the `filter` property
disappears, its meaning folded into the value expressions themselves.

---

## Filter translation

| v1 | v2 | Notes |
|---|---|---|
| `{"filter": "item", "values": ["a", "b"]}` | `["a", "b"]` | Plain codes |
| `{"filter": "all", "values": ["*"]}` | `["*"]` | All values |
| `{"filter": "all", "values": ["202*"]}` | `["202*"]` | Wildcard prefix |
| `{"filter": "all", "values": ["199*", "202*"]}` | `["199*", "202*"]` | Multiple wildcards work in both |
| `{"filter": "top", "values": ["5"]}` | `["top(5)"]` | Count is a string in v1 |
| `{"filter": "agg:KommFylker", "values": ["F-03"]}` | `"codelist": "agg_KommFylker", "valueCodes": ["F-03"]` | **`agg:X` ↔ `agg_X`** |
| `{"filter": "vs:NUTS", "values": [...]}` | `"codelist": "vs_NUTS", "valueCodes": [...]` | **`vs:X` ↔ `vs_X`** |
| *(no equivalent)* | `["bottom(3)"]`, `["from(2020)"]`, `["to(2022)"]`, `["range(2018,2023)"]`, `["top(3,2)"]` / `["bottom(5,1)"]` (offset forms) | v2-only. Shown in POST form. In a v2 **GET** URL an expression containing a comma must be bracketed — `valueCodes[Tid]=[range(2018,2023)]` — or it is split on the comma and rejected (`Illegal selection expression`). Expressions may be mixed with plain codes |
| *(no equivalent)* | `["??"]` | `?` masking is v2-only |

That `agg:X` ↔ `agg_X` correspondence is more than cosmetic — see "Using v2 to fill v1's gaps".

---

## Metadata

v1 metadata is a thin, flat description:

```json
{ "title": "…",
  "variables": [ { "code": "Region", "text": "region",
                   "values": ["0301", …], "valueTexts": ["Oslo", …],
                   "elimination": true } ] }
```

v2 metadata is a full json-stat2 Dataset with everything v1 leaves out:

| | v1 | v2 |
|---|---|---|
| Variable codes and labels | yes | yes |
| Value codes and labels | `values` / `valueTexts`, positionally aligned | `category.index` / `category.label` |
| `elimination` flag | yes | yes (`extension.elimination`) |
| `time` flag | yes | via `role.time` |
| **`role` (time/geo/metric)** | **no** | yes |
| **Units and decimals** | **no** | yes (`category.unit`) |
| **Codelists / aggregations** | **no** | yes (`extension.codelists`) |
| **First/last period, discontinued** | **no** | yes (`extension`) |
| **Time frequency** (PX `TLIST`) | **no** — infer from the code shape | yes, as `timeUnit` on the table resource |
| Contacts, notes | limited | yes |

The gaps are the main practical cost of staying on v1. `role`, units and decimals do appear in
the v1 *data* response, so a `top`-1 probe query recovers them. Codelists and aggregations are
recoverable only from outside v1 — from v2, from the web front end, or from the agency's
classification service.

---

## Elimination

Identical semantics in both versions, and the same three rules: `elimination: true` with a total
returns the total; `elimination: true` without one aggregates everything into one value;
`elimination: false` (or absent, in v1) returns **all** values.

One difference in how it is surfaced: v1 omits `elimination` entirely when it is false, so the
absent property must be read as `false`. v2 always states it explicitly in
`extension.elimination`.

In both, eliminated variables disappear from the response's `id` and `dimension`.

---

## Output formats

| v1 | v2 |
|---|---|
| `json-stat2` | `json-stat2` |
| `json-stat` | *(dropped)* |
| `csv`, `csv2`, `csv3` | `csv` + `outputFormatParams` (`UseCodes`, `UseTexts`, `UseCodesAndTexts`, separators) |
| `xlsx` | `xlsx` |
| `px` | `px` |
| `json` (PX-JSON) | `json-px` |
| `sdmx` | *(varies)* |

v2 replaces v1's fixed CSV variants with one `csv` format plus `outputFormatParams`, so v1's
`csv3` (codes) is roughly v2's `csv` with `UseCodes`, and `csv2` (texts) roughly `UseTexts`.

Note the spelling trap on **both** versions: the format is `json-stat2`, hyphenated. `jsonstat2`
is rejected. Much published documentation, including the official PxWeb 1.0 specification, gives
the unhyphenated form.

---

## Using v2 to fill v1's gaps

SSB and SCB are the two relational installations, who can runs both versions over the same tables. The trick helps least where it is available. PxWebApi v2 is the better
discovery tool even if you must retrieve through v1. Verified end to end against SSB table 07459, re-confirmed 2026-09-03:

```
# 1. v2 metadata lists the aggregations v1 will not show you
#    Note the casing: the JSON field is `codelists`, though the endpoint path is /codeLists/
GET https://data.ssb.no/api/pxwebapi/v2/tables/07459/metadata?lang=no
    → dimension.Region.extension.codelists = [{"id": "agg_KommFylker", "label": "Fylker 2024, …"}, …]
      dimension.Alder.extension.codelists  = [{"id": "agg_FemAarigGruppering", …}, …]

# 2. v2 codelist endpoint gives the member codes and what each aggregates
GET https://data.ssb.no/api/pxwebapi/v2/codeLists/agg_KommFylker?lang=no
    → [{"code": "F-31", "label": "Østfold", "valueMap": ["0101", "3124", "0103", …]}, …]

# 3. v1 accepts the same aggregation with `_` swapped for `:`
POST https://data.ssb.no/api/v0/no/table/07459
     {"query": [{"code": "Region",
                 "selection": {"filter": "agg:KommFylker", "values": ["F-03", "F-11"]}}, …]}
    → 200 OK, dimension.Region.category.index = {"F-03": 0, "F-11": 1}
```

The same trick recovers units, decimals and `role` without spending a probe query.

**Matching a v1 table to its v2 id: use `extension.px.tableid`.** The two APIs name tables
differently — SCB's v1 addresses them by PX filename (`BefolkManadCKM`) and its v2 by an opaque id
(`TAB6471`) — so guessing from the label is unreliable, and two tables with near-identical titles
can differ in coverage by decades. Run any small v1 query and read `extension.px.tableid`: it
carries the v2 id directly, and `extension.px.matrix` carries the PX matrix name. Confirm the match
before importing anything from the v2 side; a codelist taken from the wrong table produces a 400
that looks exactly like a forbidden aggregation.

**One thing does not carry across, so check it before assuming a v2 recipe will run on v1.** When
`extension.px.aggregallowed` is `false`, v2 still applies the aggregation and returns data, while
SSB's v1 rejects `agg:` with 400 on the same table with the same codes — verified on tables 14700
and 11342, 2026-09-03. `vs:` is unaffected in both. See `px-files-and-classifications.md`.

If the installation has no v2, the fallbacks are the agency's web front end ("API query for this
table" emits a complete v1 body including aggregation names) and its classification service.

---

## When to prefer which

- **The installation is on v2 → use v2**. Newer, richer metadata, GET URLs you can share, saved queries,
  discoverable limits.
- **The installation is v1-only** → use v1. That is most PxWeb installations worldwide, and it is
  fully capable; the constraint is discovery, not retrieval.
- **Both are available** → v2 for exploration, and v2 for retrieval too unless the user has
  existing v1 tooling. A shared v1 query body is a normal thing to be handed and worth honouring
  as-is.
- **Migrating v1 → v2** → the response-parsing half of the code is unaffected. Rewrite endpoints,
  the request body, and any aggregation lookups that relied on out-of-band knowledge.
