# json-stat2 — format reference

json-stat2 is an open format for statistical datasets (https://json-stat.org/). PxWebApi v1
returns it when you ask for `"response": {"format": "json-stat2"}`, and the structure is the same
one produced by PxWebApi v2, Eurostat and the World Bank. This file documents the format; v1's
request shape lives in `query-syntax.md`.

Two things are specific to v1 and worth stating up front:

- **Only the data response is json-stat2.** A GET on the table URL returns v1's own thin metadata
  shape (`{"title", "variables": [{"code", "text", "values", "valueTexts", "elimination", "time"}]}`),
  not a json-stat2 Dataset. v2 returns json-stat2 for both.
- **The data response carries metadata that v1's metadata endpoint does not** — `role`, units and
  decimals in particular. When metadata leaves you guessing, a minimal probe query is the answer.

---

## Dataset structure

```json
{
  "version": "2.0",
  "class": "dataset",
  "label": "07459: Befolkning, etter region, statistikkvariabel og år",
  "source": "Statistisk sentralbyrå",
  "updated": "2026-02-25T07:00:00Z",
  "note": ["Free-text notes about the table"],
  "id": ["Region", "ContentsCode", "Tid"],
  "size": [1, 1, 3],
  "dimension": { … },
  "value": [724290, 728714, 731500],
  "role": { "time": ["Tid"], "geo": ["Region"], "metric": ["ContentsCode"] }
}
```

### Key elements

- **`id`** — variable names in order. This order governs all indexing: iterate `id`, never
  `Object.keys(dimension)`. The two coincide at SSB (v1 and v2), SCB, Latvia and Eurostat
  (verified 2026-10-02), but the specification does not promise it.
- **`size`** — number of values per variable, same order as `id`.
- **`value`** — flat array of all data values in **row-major order**: the last dimension in `id`
  varies fastest, the first varies slowest (the C/NumPy convention). For `size = [s₀, s₁, …, sₙ]`
  and category indices `(i₀, i₁, …, iₙ)`, the flat index is
  `i₀·(s₁·s₂·…·sₙ) + i₁·(s₂·…·sₙ) + … + iₙ` — each position times its dimension's *stride*, the
  product of the sizes of every later dimension. Category positions come from
  `dimension.{var}.category.index`. Worked example below.
- **`dimension`** — per variable: codes (`category.index`), labels (`category.label`), units
  (`category.unit`), and `extension`.
- **`role`** — which variables are `time`, `geo` and `metric`. **Start your analysis here.**
- **`status`** — flags on individual cells, keyed by index into `value`. Read it **alongside**
  `value`: a missing-value symbol comes with a `null`, but a status can also flag a figure that
  exists (provisional, estimated, a cell note). See "Status codes".
- **`note`** — table-level caveats. Worth reading before interpreting a series; PxWeb often
  records boundary changes and coverage gaps here.
- **`extension`** — agency-specific metadata.

Older serializers may omit `"version": "2.0"` (Statistics Faroe Islands currently does). The rest
of the structure is unaffected.

### Worked example: two dimensions that vary

`id = ["Region", "ContentsCode", "Tid"]`, `size = [2, 1, 3]` — two regions, one measure, three
years. Strides: `Region` 1·3 = 3, `ContentsCode` 3, `Tid` 1.

| Position in `value` | `Region` | `Tid` | Offset |
|---|---|---|---|
| 0, 1, 2 | index 0 | index 0, 1, 2 | `0·3 + 0·3 + t·1` |
| 3, 4, 5 | index 1 | index 0, 1, 2 | `1·3 + 0·3 + t·1` |

The second region's third year is `1·3 + 0·3 + 2·1 = 5`, so `value[5]`. A dimension of size 1
still has a stride, but always contributes 0. To test an implementation, use
https://json-stat.org/samples/order.json, where every value is a string naming its own position
(`A2B1C3`) and `category.index` is in array form. Position 11 in that file reads `A1B1C4` where it
should read `A2B1C4` (a typo, checked 2026-10-02), so correct code "fails" exactly there.

### Shape variants

The json-stat 2.0 specification allows several shapes for the same information. PxWeb sends the
first column; other producers use the second, and code written against PxWeb alone breaks on them:

| Field | PxWeb | Also allowed by the specification |
|---|---|---|
| `value` | array | object keyed by position — sparse, so a missing key means `null` (Eurostat) |
| `status` | object keyed by position, or absent | a single string applying to every cell, or an array parallel to `value` (Eurostat uses the object form too) |
| `category.index` | object `{code: position}` | array `[code0, code1, …]`; omitted when the dimension has only one category |

Verified 2026-10-02 at SSB's v1, on 113 tables across the three v2 installations, and on Eurostat
`nama_10_gdp` and `demo_pjan`; the other v1 installations were not swept. Eurostat's sparseness
is real: `nama_10_gdp` for Albania, Montenegro and Norway 1990–1999 has 30 cells and 15 keys.
Read `value[String(offset)]` there, and treat a missing key as `null`.

---

## Start the analysis with `role`

- **`role.metric`** — what is being measured. In Nordic installations this is usually the
  `ContentsCode` variable, but **check `role.metric` for the actual name** rather than assuming:
  Statistics Finland calls it `contentscode`, and other installations differ again. Read
  `dimension.{metric}.category.unit` for the unit and the number of decimals.
- **`role.time`** — the time dimension.
- **`role.geo`** — geography. **If `role.geo` is missing, the figures cover the installation's
  whole country or area — do not ask the user.** In v1 this happens routinely, because
  eliminating a geographic variable removes it from the response entirely.
- Variables in `id` but not in `role` are breakdown dimensions — sex, age, industry, and so on.

Because v1's metadata endpoint has no `role`, this is also the reliable way to identify the
metric on an unfamiliar installation: run a `top`-1 probe query and read `role` off the result.

---

## What json-stat2 cannot express

Worth knowing when moving between PX and json-stat, because the loss is silent:

- **Time periodicity.** PX declares it explicitly (`TIMEVAL(...)=TLIST(A1|H1|Q1|M1|W1)`, which also
  guarantees consecutive periods). json-stat2 has no standard field for it — `role.time` names the
  time dimension but says nothing about its frequency. PxWebApi v2 works around this with
  `timeUnit` on the table resource, *outside* the json-stat2 document; v1 does not expose it at all.
  Consumers must infer frequency from the shape of the value codes, and those codes are not
  guaranteed to be dates (see `query-syntax.md`).

  Note that the absence is a PxWeb choice rather than a hard limit of the format: PxWeb already
  ships PX header keywords inside the dataset under `extension.px` (see below), and TLIST simply is
  not among them.
- **The aggregation that produced a figure.** Eliminated dimensions vanish from `id` and
  `dimension` entirely, so a dataset does not record what was summed away.
- **Which codelist or valueset a code came from.** In v1 the `agg:`/`vs:` used in the request
  leaves no trace in the response.

---

## `extension.px` — PX keywords inside the dataset

PxWeb adds a non-standard `extension.px` object at the top level of the **data** response, carrying
part of the source PX file's header — `decimals`, `heading`/`stub` (the intended pivot layout),
`official-statistics`, the subject classification and `aggregallowed`. It is the only place several
of them appear; the metadata endpoint has none of them, and non-PxWeb json-stat producers have no
`extension.px` at all.

`aggregallowed` says whether summing the table is meaningful. Treat it as a hint only: it is
**absent from three of the seven verified installations**, and where it is `false` the installations
do not agree on what follows — SSB's v1 rejects `agg:` with 400, SCB's serves the data (verified
2026-09-04). The full matrix, the controls behind it and the SSB-v1-vs-v2 difference are in
`px-files-and-classifications.md`.

---

## Units and decimals

```json
"ContentsCode": {
  "label": "statistikkvariabel",
  "category": {
    "index": { "Personer1": 0 },
    "label": { "Personer1": "Personer" },
    "unit":  { "Personer1": { "base": "antall", "decimals": 0 } }
  },
  "extension": {
    "elimination": false,
    "refperiod":     { "Personer1": "1.1." },
    "measuringType": { "Personer1": "Stock" },
    "priceType":     { "Personer1": "NotApplicable" },
    "adjustment":    { "Personer1": "None" }
  }
}
```

`unit.base` is the unit of measurement and `unit.decimals` how many decimals to display.
`extension` frequently carries the reference period, whether the series is a stock or a flow,
whether prices are current or fixed, and whether the series is seasonally adjusted — all of which
belong in a careful presentation of the numbers, and none of which appear in v1 metadata.

---

## Status codes

`value` and `status` are two parallel channels. Read them separately:

- **`value` is `null`** — the figure does not exist; `status` usually says why (table below).
  Show the symbol, never a zero.
- **`value` is a number and `status` is set** — the figure exists and carries a flag:
  provisional, estimated, or a note on that cell. Show the number **with** the flag. Dropping
  the flag hides a caveat; blanking the number discards data.

PxWeb's json-stat2 serializer produces both (`PxTools/PCAxis.Serializers`,
`JsonStat2Serializer.GetValueAndStatus`): a PX data symbol becomes `null` plus the symbol, while a
cell with a data note (`DATANOTECELL`) keeps its number and gets the note as its status. Observed
2026-10-02: SSB 09842 (GDP per capita) flags 2023–2024 with `"*"` on cells that have numbers, at
both SSB's v1 and v2, and the table's `note` explains it as `* = Foreløpig tall` (provisional).
In a v2 sweep of 113 tables at SSB, SCB and Latvia it was the only table that flagged numbers.
Eurostat flags figures the same way (`nama_10_gdp`: `"p"` on cells that have values).

| Symbol | Meaning |
|---|---|
| `.` | Not applicable — the category did not exist when the data was collected |
| `..` | Data not available — not yet in the database |
| `:` | Confidential — withheld to avoid identifying a person or business |
| `-` | PX's nil symbol (`DATASYMBOLNIL`, value `null`). Its use varies, so show it and do not compute with it |

These are only the common defaults. In PxWeb each symbol is declared per PX file
(`DATASYMBOL1`–`6`), so they vary between agencies and even between tables in one database — read
what the response actually contains rather than matching against this list, and look for a key
in the table's `note`; PxWeb has no field for it, while Eurostat explains its symbols in
`extension.status.label`. Never treat any of them as zero, and never filter `null`s out of
`value` before indexing: a `null` holds its position, and removing it shifts every later cell.

---

## Classification links

Some agencies attach classification URNs:

```json
"link": { "describedby": [ { "extension": { "Region": "urn:ssb:classification:klass:104" } } ] }
```

At SSB the trailing number is a Klass id, resolvable as
`https://www.ssb.no/klass/klassifikasjoner/104` or
`https://data.ssb.no/api/klass/v1/classifications/104`. Variable definitions appear as
`urn:ssb:conceptvariable:vardok:2798` → `https://www.ssb.no/a/metadata/conceptvariable/vardok/2798/nb`
(`/nb`, `/nn` or `/en`).

---

## Tooling

Client libraries exist for JavaScript, Python, R, Java and Julia — see https://json-stat.org/.
Useful in practice:

- **Python** — `pyjstat` converts json-stat into pandas DataFrames.
- **R** — `rjstat`; SSB additionally publishes `PxWebApiData` on CRAN, which wraps v1 query
  construction (`ApiData()`) and works from Power BI as well. It is **not** v1-only: since 1.9.0
  it also covers PxWebApi v2 through a separate snake_case interface (`api_data()`,
  `query_url()`, `meta_data()`, …), with a vignette for each version. A user's `PxWebApiData`
  script is therefore not evidence that the installation is on v1 — check the base URL.
- **Node.js** — the json-stat Toolkit's command-line converters (`jsonstat2csv`, `csv2jsonstat`,
  `jsonstat2arrow`, `sdmx2jsonstat`, …). `jsonstat2csv` gives far better control over separators
  and decimal characters than the API's own CSV output.
- **Browsing** — the json-stat explorer at https://json-stat.com/explorer, plus a JSON viewer
  extension (built into Firefox; jsonview.com for Chromium).
- **Reading guide** — Idescat's JSON-stat skill
  (https://www.idescat.cat/dev/api/taules/jsonstat/SKILL.md, CC BY 4.0): a short,
  provider-neutral guide to reading a dataset.
