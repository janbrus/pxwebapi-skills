# json-stat2 — format reference

json-stat2 is an open format for statistical datasets (https://json-stat.org/). It is used by PxWebApi v2 but also by other statistical providers such as Eurostat and World Bank. This file documents the format itself — installation-specific operational details (publishing times, limits, rate limiting) belong in `api-details.md`.

In v2, **both** `/tables/{id}/metadata` and `/tables/{id}/data` return a json-stat2 Dataset. They are not the same document, and several fields mean different things in each — see "Metadata response vs data response" below.

---

## Dataset structure

```json
{
  "version": "2.0",
  "class": "dataset",
  "label": "Table title",
  "source": "Agency name",
  "updated": "2026-02-25T07:00:00Z",
  "note": ["Free-text notes about the table"],
  "id": ["Region", "ContentsCode", "Tid"],
  "size": [1, 1, 5],
  "dimension": { … },
  "value": [100, 200, 300, null, 500],
  "status": { "3": ".." },
  "role": { "time": ["Tid"], "geo": ["Region"], "metric": ["ContentsCode"] },
  "extension": { "px": { … }, "contact": [ … ] },
  "link": { "describedby": [ … ] }
}
```

### Key elements

- **`id`** — variable names in order. This order governs all indexing: iterate `id`, never `Object.keys(dimension)` — the two coincide at SSB, SCB, Latvia and Eurostat (verified 2026-10-02), but the specification does not promise it.
- **`size`** — number of values per variable, same order as `id`.
- **`value`** — flat array of all data values in **row-major order**: the last dimension in `id` varies fastest, the first varies slowest (the C/NumPy convention). For `size = [s₀, s₁, …, sₙ]` and category indices `(i₀, i₁, …, iₙ)`, the flat index is `i₀·(s₁·s₂·…·sₙ) + i₁·(s₂·…·sₙ) + … + iₙ` — each position times its dimension's *stride*, the product of the sizes of every later dimension. Category positions come from `dimension.{var}.category.index`. Worked example below. **Use the `id` of the response you are indexing** — a default-selection response can order dimensions differently from the metadata (Latvia IRS010m: metadata `["ContentsCode", "TIME"]`, default data `["TIME", "ContentsCode"]`).
- **`dimension`** — per variable: codes (`category.index`), labels (`category.label`), units (`category.unit`), per-value notes (`category.note`), and `extension`.
- **`role`** — which variables are `time`, `geo` and `metric`. **Start your analysis here** (see below).
- **`status`** — flags on individual cells, keyed by index into `value`. Read it **alongside** `value`, not instead of it: a missing-value symbol comes with a `null`, but a status can also flag a figure that exists (provisional, estimated, a cell note). See "Status codes".
- **`note`** — an **array** of table-level caveats. Read it before interpreting a series: boundary changes, base-year changes and coverage gaps are recorded here. See "Notes" below — some of them are mandatory to display.
- **`extension`** — installation-specific metadata, at two levels. See below.
- **`link`** — classification and definition references. See below.

Older serializers may omit `"version": "2.0"`. The rest of the structure is unaffected.

### Worked example: two dimensions that vary

`id = ["Region", "ContentsCode", "Tid"]`, `size = [2, 1, 3]` — two regions, one measure, three years. Strides: `Region` 1·3 = 3, `ContentsCode` 3, `Tid` 1.

| Position in `value` | `Region` | `Tid` | Offset |
|---|---|---|---|
| 0, 1, 2 | index 0 | index 0, 1, 2 | `0·3 + 0·3 + t·1` |
| 3, 4, 5 | index 1 | index 0, 1, 2 | `1·3 + 0·3 + t·1` |

The second region's third year is `1·3 + 0·3 + 2·1 = 5`, so `value[5]`. A dimension of size 1 still has a stride, but always contributes 0. Positions follow the order of the request, not a sorted one: `valueCodes[Tid]=2026,2024,2025` returns `{"2026": 0, "2024": 1, "2025": 2}` at SSB, and SCB does the same (verified 2026-10-02; Latvia not tested). Always look the position up in `category.index`. To test an implementation, use https://json-stat.org/samples/order.json, where every value is a string naming its own position (`A2B1C3`) and `category.index` is in array form. Position 11 in that file reads `A1B1C4` where it should read `A2B1C4` (a typo, checked 2026-10-02), so correct code "fails" exactly there.

---

## Shape variants

The json-stat 2.0 specification allows several shapes for the same information. PxWebApi always sends the first column; other producers use the second, and code written against PxWeb alone breaks on them:

| Field | PxWebApi (SSB, SCB, Latvia) | Also allowed by the specification |
|---|---|---|
| `value` | array | object keyed by position — sparse, so a missing key means `null` (Eurostat) |
| `status` | object keyed by position, or absent | a single string applying to every cell, or an array parallel to `value` (Eurostat uses the object form too) |
| `category.index` | object `{code: position}` | array `[code0, code1, …]`; omitted when the dimension has only one category |

Verified 2026-10-02 on 88 SSB, 13 SCB and 12 Latvian tables, and on Eurostat `nama_10_gdp` and `demo_pjan`. Eurostat's sparseness is real: `nama_10_gdp` for Albania, Montenegro and Norway 1990–1999 has 30 cells and 15 keys. Read `value[String(offset)]` there, and treat a missing key as `null`.

---

## Start the analysis with `role`

- **`role.metric`** — what is being measured. Named `ContentsCode` on all three known installations (Nordic and Latvian alike), but **check `role.metric` for the actual name** rather than assuming. Read `dimension.{metric}.category.unit` for the unit and the number of decimals.
- **`role.time`** — the time dimension: `Tid` at SSB and SCB, `TIME` at Latvia.
- **`role.geo`** — geography, **when the installation sets it.** SSB and Latvia do (`Region`, `AREA`); SCB does not, even on tables with a 290-municipality `Region` dimension (verified 2026-09-07 on TAB638, TAB6471, TAB5444 — all `role: {time, metric}`). Look for a geographic variable in `id` first; only when none exists do the figures cover the whole country or area. Do not ask the user.
- Variables in `id` but not in `role` are breakdown dimensions — sex, age, industry, and so on.

---

## `extension` — two levels, not one

`extension` appears both at the **dataset** level and inside **each dimension**, and the two carry different things. Confusing them is the most common misreading of a PxWeb json-stat2 document.

### Dataset level (`extension` in the root)

| Field | Meaning |
|---|---|
| `px` | PX header keywords — see next section |
| `contact` | Structured contact details for the statistic |
| `noteMandatory` | Which entries in the root `note` array must be displayed — see "Notes" |
| `discontinued` | Whether the table is closed. Often `null`; present in data responses |

**`firstPeriod`, `lastPeriod` and the table's `discontinued` flag are fields of the `/tables` search hit, not of the dataset.** If you need the table's coverage before fetching data, read them from `GET /tables?query=…`, not from the json-stat2 document.

### Dimension level (`dimension.{var}.extension`)

| Field | Meaning |
|---|---|
| `elimination` | Whether the dimension may be omitted from a query — **metadata only**, see the trap below |
| `eliminationValueCode` | The code that represents the total, when one exists — **data responses only**, see the trap below |
| `codelists` | Available aggregations (`agg_`) and valuesets (`vs_`) for this dimension, with labels and links |
| `show` | How the agency intends values to be labelled: `value`, `code`, `code_value` |
| `refperiod` | Reference period per value, e.g. a stock measured at 1 January |
| `measuringType` | `Stock`, `Flow`, `Average`, … — what kind of quantity this is |
| `priceType` | Current prices, fixed prices, or not applicable |
| `adjustment` | Seasonal / working-day adjustment, or `None` |
| `basePeriod` | The base period of an index, e.g. `2025=100` |
| `alternativeText` | An alternative label supplied by the agency |
| `noteMandatory`, `categoryNoteMandatory` | Which dimension- or value-level notes must be displayed |

`measuringType`, `priceType`, `adjustment` and `basePeriod` decide how a number may honestly be described. An index without its base period is meaningless; a fixed-price series compared against a current-price one is wrong. Read them before writing the sentence that explains what the figure means.

### Trap: eliminability is readable only from the metadata response

`extension.elimination` answers a **different question** in each response type (verified on SSB and SCB 2026-08-30, Latvia 2026-09-08):

- **In a metadata response** it is the contract: *may this dimension be left out of a query?* This is the one you want.
- **In a data response** it describes the extract you just received: it is `true` only when the value set that came back still contains the elimination value, and `false` otherwise. Select one ordinary region and it reads `false`; apply a codelist and it reads `false`; and neither says anything about whether the dimension was eliminable.

So **never infer eliminability from a data response.** Re-read the metadata instead.

The same asymmetry runs the other way for `eliminationValueCode`, which is why a table can look as if it has no total code when it has one. PX has two elimination forms and the metadata response does not distinguish them:

- `ELIMINATION=YES` — there is no total value; the API sums the dimension on the fly when you omit it. (A sex dimension whose only categories are "women" and "men".)
- `ELIMINATION("<value>")` — a predefined total value already exists in the value set. (A region dimension carrying a "whole country" code alongside the municipalities.)

In metadata both appear as a bare `elimination: true` — `eliminationValueCode` was absent from every dimension across a 50-table sweep at SSB, and from all six dimensions of SCB's TAB638. A **data** response that includes the total is what reveals it, as `eliminationValueCode: "<code>"` (SSB 07459 `Region` → `"0"`, SCB TAB6471 `Region` → `"00"`). If you need to know which form a dimension uses, that probe is the way to find out.

Eliminability is a property of the **table**, not of the variable name: SCB's `Alder` is eliminable in TAB638 and mandatory in TAB6471.

---

## `extension.px` — PX keywords inside the dataset

PxWeb adds a non-standard `px` object to the dataset-level `extension`, carrying part of the source PX file's header:

```json
"extension": {
  "px": { "tableid": "…", "matrix": "…", "decimals": 1,
          "aggregallowed": false, "official-statistics": true,
          "heading": ["ContentsCode", "Tid"], "stub": ["Region"],
          "subject-code": "pp", "subject-area": "Prices and price indices",
          "contents": "…", "language": "en", "copyright": true }
}
```

Useful fields:

- **`aggregallowed`** — whether summing this table is meaningful at all. This is the only place the answer appears. It is commonly `false` for index tables, where adding index points produces nonsense. Treat it as a signal about interpretation, **not** as a technical block: an installation may still offer codelists on such a table and answer HTTP 200 for them.
- **`decimals`** — the table's default decimal count (per-value decimals live in `category.unit`).
- **`heading` / `stub`** — the pivot layout the agency intends, i.e. which variables belong in columns and which in rows. Useful when rendering a table the way its publisher does.
- **`subject-code` / `subject-area`** — the subject classification.

This is a PxWeb extension — do not expect it from other json-stat producers.

---

## Notes

Two levels, and both may be **mandatory to display**:

- **`note`** (root) — an array of table-level notes. `extension.noteMandatory` is keyed by index into that array: `{"1": true}` means `note[1]` must be shown to the user. The index differs per table, so resolve it rather than assuming the first note.
- **`category.note`** (inside a dimension) — notes attached to individual values, gated by `extension.categoryNoteMandatory` in the same way. This is where boundary changes and definition breaks are recorded, per value.

Mandatory notes are how an agency warns that a figure needs a caveat — a changed base year, a corrected period, a discontinued table with a successor. They travel with the **data** response too, so displaying them costs no extra call. If a note is flagged mandatory and your answer computes something the note is about, the note belongs in the answer.

---

## Units and decimals

```json
"ContentsCode": {
  "label": "statistical variable",
  "category": {
    "index": { "Persons1": 0 },
    "label": { "Persons1": "Persons" },
    "unit":  { "Persons1": { "base": "number", "decimals": 0 } }
  },
  "extension": { "elimination": false, "measuringType": { "Persons1": "Stock" } }
}
```

`unit.base` is the unit of measurement and `unit.decimals` how many decimals to display. Keep that precision: do not add decimals the agency did not publish, and do not round away ones that carry meaning.

---

## Status codes

`value` and `status` are two parallel channels. Read them separately:

- **`value` is `null`** — the figure does not exist; `status` usually says why (table below). Show the symbol, never a zero.
- **`value` is a number and `status` is set** — the figure exists and carries a flag: provisional, estimated, or a note on that cell. Show the number **with** the flag. Dropping the flag hides a caveat; blanking the number discards data.

PxWebApi's serializer produces both (`PxTools/PCAxis.Serializers`, `JsonStat2Serializer.GetValueAndStatus`): a PX data symbol (`DATASYMBOL1`–`6`, the sum symbol, `DATASYMBOLNIL`) becomes `null` plus the symbol, while a cell with a data note (`DATANOTECELL`) keeps its number and gets the note as its status. Observed 2026-10-02 in a sweep of 88 SSB, 13 SCB and 12 Latvian tables: one table flags numbers — SSB 09842 marks 2023–2024 with `"*"`, explained in the table's `note` as `* = Foreløpig tall` (provisional). Every other status sat on a `null`. Eurostat flags figures the same way (`nama_10_gdp`: `"p"` on cells that have values).

| Symbol | Meaning |
|---|---|
| `.` | Not applicable — the category did not exist when the data was collected |
| `..` | Data not available — not yet in the database |
| `:` | Confidential — withheld to avoid identifying a person or business |
| `-` | PX's nil symbol (`DATASYMBOLNIL`, value `null`). Its use varies, so show it and do not compute with it |

Exact symbols vary by installation, because they come from the source PX file's `DATASYMBOL1`–`6` keywords and each file may override the defaults (Latvia sends `…` where SSB sends `..`). Check the response, and look for a key to the symbols in the table's `note` — PxWeb has no field for it, while Eurostat explains its symbols in `extension.status.label`. **Never treat any symbol as zero**, never silently drop the row, and never filter `null`s out of `value` before indexing: a `null` holds its position, and removing it shifts every later cell.

---

## Classification links

Some agencies attach classification URNs to `link.describedby`:

```json
"link": { "describedby": [ { "extension": { "Region": "urn:…:classification:…:104" } } ] }
```

The `extension` key is either a variable name (a URN for the whole variable) or a single value code (a URN per value — common for the metric variable). Some installations additionally publish ready-made human-readable links under `link.related` in metadata responses; availability varies by installation, so check rather than assume.

---

## What json-stat2 cannot express

The loss is silent in all three cases:

- **Time periodicity.** PX declares it explicitly (`TIMEVAL(...)=TLIST(A1|H1|Q1|M1|W1)`, which also guarantees consecutive periods). json-stat2 has no standard field for it — `role.time` names the time dimension but says nothing about its frequency. PxWebApi v2 works around this with **`timeUnit` on the `/tables` resource, *outside* the json-stat2 document**. If a consumer downstream needs to know whether an axis is monthly or quarterly, carry `timeUnit` across yourself; the dataset will not. `timeUnit: Other` means the codes are not periods at all (Latvia `IRJ010`: `Time01`).
- **The aggregation that produced a figure.** An omitted dimension is eliminated and **disappears from `id` and `dimension` entirely** — the dataset does not record that it was summed away, or over what.
- **Which codelist a code came from.** Requesting `codelist[Var]=agg_…` leaves no trace in the response: the dimension comes back with the aggregated codes and an `extension` that names no codelist. Two different aggregations of the same variable produce datasets that look alike and are not.

All three are reasons to state your selection alongside your numbers rather than relying on the response to document itself.

---

## Tooling

Client libraries exist for JavaScript, Python, R, Java and Julia — see https://json-stat.org/. Useful in practice:

- **Python** — `pyjstat` converts json-stat into pandas DataFrames.
- **R** — `rjstat`. SSB additionally publishes `PxWebApiData` on CRAN, which reads PxWeb data from Statistics Norway, Statistics Sweden and Statistics Finland. It supports **both API versions** (1.9.0, 2026-02-02) and ships a separate vignette for each. The v2 interface is snake_case — `api_data()`, `get_api_data()`, `query_url()`, plus `meta_frames()`, `meta_code_list()` and `meta_data()`, each with `_1`/`_2`/`_12` variants returning labels, codes or both — against v1's camelCase `ApiData()`.
- **Node.js** — the json-stat Toolkit's command-line converters (`jsonstat2csv`, `csv2jsonstat`, `jsonstat2arrow`, `sdmx2jsonstat`, …). `jsonstat2csv` gives better control over separators and decimal characters than the API's own CSV output.
- **Browsing** — the json-stat explorer at https://json-stat.com/explorer, plus a JSON viewer extension (built into Firefox; jsonview.com for Chromium).
- **Reading guide** — Idescat's JSON-stat skill (https://www.idescat.cat/dev/api/taules/jsonstat/SKILL.md, CC BY 4.0): a short, provider-neutral guide to reading a dataset.
