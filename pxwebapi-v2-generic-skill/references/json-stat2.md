# json-stat2 — format reference

json-stat2 is an open format for statistical datasets (https://json-stat.org/). PxWebApi v2, Eurostat and World Bank use it. This file describes the format as PxWebApi v2 delivers it, and says where SSB, SCB and Latvia (CSP) differ. Operational details (limits, rate limiting, publishing times) are in `api-details.md`.

In v2, **both** `/tables/{id}/metadata` and `/tables/{id}/data` return a json-stat2 Dataset. They are not the same document, and some fields mean different things in each.

**Contents**

1. How to read an extract
2. Dataset structure and indexing
3. Shape variants
4. The fields in the dataset
5. `dimension` and `extension` per variable
6. `extension` at the root and `extension.px`
7. `status`, `note` and `link`
8. What json-stat2 cannot express
9. Tooling

---

## How to read an extract

1. **Start with `role`, then look in `id`.** `metric` is what is measured and `time` is time. `geo` is optional: SSB and Latvia set it, SCB does not. Look for a geographic variable in `id`; only when none exists do the figures cover the whole country. Do not ask the user. (SKILL.md Step 3)
2. **`value` is row-major:** the last dimension in `id` varies fastest. The position is the sum of `category.index` × stride, where the stride is the product of `size` for the later dimensions. Iterate `id`, not `Object.keys(dimension)`, and use the `id` of the response you hold. Never assume time is sorted, and never filter out `null`. (See "Dataset structure and indexing")
3. **Read `value` and `status` separately.** If the cell is `null`, show the symbol, never 0. If it has a number, show the number with its flag. (SKILL.md Step 5, and `status`)
4. **Show mandatory notes at every level the table uses:** the table (`extension.noteMandatory`), the variable (`dimension.{var}.extension.noteMandatory`) and the value (`categoryNoteMandatory`). (SKILL.md Step 5, and `note`)
5. **Read `elimination` from metadata only.** Find the total code in `category.label`, or as `eliminationValueCode` in a data response. (See `elimination`)
6. **If `aggregallowed` is `false`, do not sum or average the figures.** If you do anyway, say so. The field blocks no query. (See `extension.px`)
7. **State the codelist, the omitted dimensions and `timeUnit` yourself.** The response records none of them. (SKILL.md Step 5, and "What json-stat2 cannot express")

---

## Dataset structure and indexing

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

Older serializers may omit `"version": "2.0"`. The rest of the structure is unaffected.

`value` is row-major, as in C and NumPy. For `size = [s₀, s₁, …, sₙ]` and category indices `(i₀, i₁, …, iₙ)` the position is `i₀·(s₁·…·sₙ) + i₁·(s₂·…·sₙ) + … + iₙ`. Above, only `Tid` varies, so the order cannot go wrong. With two regions and three years, `id = ["Region", "ContentsCode", "Tid"]` and `size = [2, 1, 3]`. Strides: `Region` 1·3 = 3, `ContentsCode` 3, `Tid` 1.

| Position in `value` | `Region` | `Tid` | Offset |
|---|---|---|---|
| 0, 1, 2 | index 0 | index 0, 1, 2 | `0·3 + 0·3 + t·1` |
| 3, 4, 5 | index 1 | index 0, 1, 2 | `1·3 + 0·3 + t·1` |

The second region's third year is `1·3 + 0·3 + 2·1 = 5`, so `value[5]`. A dimension of size 1 always contributes 0.

`category.index` follows the order of the request: `valueCodes[Tid]=2026,2024,2025` returns `{"2026": 0, "2024": 1, "2025": 2}` at SSB and SCB (2026-10-02) and at Latvia (`TIME`, 2026-10-14). `top(n)` and `from(x)` give ascending order. The keys of `dimension` come in `id` order at SSB, SCB, Latvia and Eurostat (2026-10-02), but the specification does not promise it, and a default-selection response can order `id` differently from the metadata (Latvia IRS010m: metadata `["ContentsCode", "TIME"]`, default data `["TIME", "ContentsCode"]`).

To test an implementation, use https://json-stat.org/samples/order.json, where every value is a string naming its own position (`A2B1C3`) and `category.index` is in array form. Position 11 in that file reads `A1B1C4` where it should read `A2B1C4` (a typo, checked 2026-10-02), so correct code "fails" exactly there.

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

## The fields in the dataset

| Field | What it is |
|---|---|
| `id`, `size` | The variables in the order that governs indexing, and the number of values per variable |
| `value` | The figures as one flat list, with `null` where a figure is missing |
| `status` | Flags per cell, keyed by position in `value`. Absent when no cell is flagged |
| `dimension` | Per variable: codes, labels, unit, notes, `extension` and `link` |
| `role` | `time`, `metric` and, where the installation sets it, `geo`. The other variables in `id` are breakdowns |
| `note` | Table notes: base-year changes, corrections, successor tables |
| `extension`, `link` | The installation's own fields and links, see below |
| `label`, `source`, `updated` | Title, source and last update |

---

## `dimension` and `extension` per variable

`dimension.{var}` has `category.index` (code → position) and `category.label` (code → name). The metric variable also has `category.unit` per value, e.g. `{"Persons1": {"base": "number", "decimals": 0}}`: `base` is the unit and `decimals` the number of decimals to show. Keep that precision — do not add decimals the agency did not publish, and do not round away ones that carry meaning. Notes sit per variable (`note`, a list) and per value (`category.note`, value code → list).

`dimension.{var}.extension` has these fields. The PX keyword each comes from is in parentheses (source: `PxTools/PCAxis.Serializers`, `JsonStat2Serializer.cs`):

| Field | Meaning |
|---|---|
| `elimination` (`ELIMINATION`) | Whether the variable may be omitted. Only metadata answers this, see below |
| `eliminationValueCode` (`ELIMINATION`) | The total code. Only in a data response that includes the total (SSB 07459 `Region` → `"0"`, SCB TAB6471 `Region` → `"00"`) |
| `show` (`PRESTEXT`) | `code`, `value` or `code_value` |
| `codelists` | The codelists (`agg_`/`vs_`) the table offers for this variable |
| `noteMandatory` (`NOTEX`) | Which of the variable's notes must be shown, keyed by index into `dimension.{var}.note`. Set at SCB (TAB6471 `Alder`: `{"0": true}`) |
| `categoryNoteMandatory` (`VALUENOTEX`) | Which value notes must be shown: value code → index into `category.note`. Set at SCB (TAB638 `Region`: `{"0140": {"1": true}}`) |
| `measuringType` (`STOCKFA`) | `Stock`, `Flow`, `Average` or `Other` |
| `priceType` (`CFPRICES`) | `Current`, `Fixed` or `NotApplicable` |
| `adjustment` (`DAYADJ`, `SEASADJ`) | `SesOnly`, `WorkAndSes` or `None` |
| `basePeriod` (`BASEPERIOD`) | The base period of an index |
| `refperiod` (`REFPERIOD`) | The reference time, e.g. 1 January for a stock |
| `alternativeText` | A longer label supplied by the agency |

The variable- and value-level note flags were set on 7 and 11 of 115 dimensions in 28 SCB tables (2026-10-13), on none of 89 at SSB (2026-10-11), and on none of 42 in 12 Latvian tables (2026-10-14). The last six fields sit on the metric variable only, with one value per measure. `measuringType`, `priceType`, `adjustment` and `basePeriod` decide how a number may honestly be described: an index without its base period is meaningless, and a fixed-price series compared with a current-price one is wrong. Where a table has its own adjustment dimension, that dimension says which series you got: SSB 13760 reports `adjustment: WorkAndSes` even for `Justering=IS` (not adjusted).

### `elimination`

In metadata it is the contract: may this variable be left out of a query? In a data response it describes the extract you received: `true` only when the values that came back include the elimination value. Select one ordinary region, or apply a codelist, and it reads `false` although the variable is eliminable. So **never infer eliminability from a data response** (verified on SSB and SCB 2026-08-30, Latvia 2026-09-08).

PX has two forms, and the metadata response does not distinguish them:

- `ELIMINATION("<variable>")=YES` — there is no total value; the API sums the variable when you omit it (SCB TAB638 `Kon`, which has only `1` and `2`).
- `ELIMINATION("<variable>")="<value name>"` — the total exists as a value (SSB 07459 `Region`, `0` = "Hele landet").

In metadata both appear as a bare `elimination: true`, without `eliminationValueCode` — absent from every dimension in a 50-table sweep at SSB and from all six of SCB's TAB638. A data response that includes the total reveals it. If you need to know the form, probe with the total.

Eliminability is a property of the **table**, not of the variable name: SCB's `Alder` is eliminable in TAB638 and mandatory in TAB6471, and `Kon` has the total code `TotSa` in TAB6471 but none in TAB638.

---

## `extension` at the root and `extension.px`

The root `extension` has `contact`, `px` and, when the table has mandatory notes, `noteMandatory` (`NOTEX`). `discontinued` is never set: it is absent from metadata and `null` in data responses at SSB, SCB (2026-10-13) and Latvia (2026-10-14). **`firstPeriod`, `lastPeriod` and the table's `discontinued` flag belong to the `/tables` hit**, not to the dataset.

PxWeb puts part of the source PX file's header in `extension.px`. Each key is a PX keyword in lower case (`AGGREGALLOWED` becomes `aggregallowed`). The same 14 keys appeared at SSB, in 28 of 28 SCB tables (2026-10-13) and in 12 of 12 Latvian tables (2026-10-14):

| Key | Meaning |
|---|---|
| `contents` | The short title |
| `heading`, `stub` | The publisher's pivot: the variables in the column head and in the stub |
| `decimals` | The table's default number of decimals (per-value decimals are in `category.unit`) |
| `aggregallowed` | `false` when the figures must not be summed. A signal about interpretation, not a block: an installation may still offer codelists on such a table and answer HTTP 200. SSB sets `false` on indices and averages; SCB also on some counts (TAB6471, population with disclosure-control noise; 14 of its 28 tables); all 12 Latvian tables had `true` |
| `tableid`, `matrix` | The table ID |
| `subject-code`, `subject-area` | The subject classification |
| `language` | Follows `lang` |
| `official-statistics`, `copyright`, `descriptiondefault`, `infofile` | Flags and a reference from the PX file. `copyright` is `false` at all three. `infofile` is `"None"` at SSB, the product code at SCB (`BE0101`) and `"001"` at Latvia |

This is a PxWeb extension — do not expect it from other json-stat producers.

---

## `status`, `note` and `link`

### `status`

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

### `note`

Mandatory notes can sit at three levels. All travel with the data response, so showing them costs no extra call:

| Level | The notes | Which must be shown | Seen at |
|---|---|---|---|
| Table | `note` (root, list) | `extension.noteMandatory`, keyed by index: `{"1": true}` means `note[1]` | SSB, SCB, Latvia |
| Variable | `dimension.{var}.note` (list) | `dimension.{var}.extension.noteMandatory`, keyed by index | SCB |
| Value | `dimension.{var}.category.note` (value code → list) | `dimension.{var}.extension.categoryNoteMandatory`, value code → index: `{"0140": {"1": true}}` means `category.note["0140"][1]` | SCB |

The index differs per table, so resolve it rather than assuming the first note. Value-level notes come only for the values you selected. Mandatory notes are how an agency warns that a figure needs a caveat — a changed base year, a corrected period, a successor table, disclosure-control noise. If your answer computes something a mandatory note is about, the note belongs in the answer.

### `link`

What `link` carries differs per installation (SSB 2026-10-11, SCB 2026-10-13, Latvia 2026-10-14):

| | SSB | SCB | Latvia |
|---|---|---|---|
| `link.related` | Root: the statistics page and "About the statistics"; per variable: classification and definition pages. **Metadata only** | Root: the statistics page (`https://www.scb.se/BE0101`, `metaid` `PRODUCTCODE:BE0101`), in metadata **and** data | none |
| `link.describedby` per variable | URNs to Klass and VarDok, also in data | plain text, e.g. `{"Kon": "Kön"}` | on 4 of 42 dimensions, value codes mapped to `"1"` |

The `describedby` key is either a variable name (one entry for the whole variable) or a value code (one per value — common for the metric variable).

---

## What json-stat2 cannot express

The loss is silent in every case:

- **Time periodicity.** PX declares it explicitly (`TIMEVAL(...)=TLIST(A1|H1|Q1|M1|W1)`, which also guarantees consecutive periods). json-stat2 has no standard field for it — `role.time` names the time dimension but says nothing about its frequency. PxWebApi v2 works around this with **`timeUnit` on the `/tables` resource, *outside* the json-stat2 document**. If a consumer downstream needs to know whether an axis is monthly or quarterly, carry `timeUnit` across yourself; the dataset will not. `timeUnit: Other` means the codes are not periods at all (Latvia `IRJ010`: `Time01`).
- **`firstPeriod`, `lastPeriod` and `discontinued`.** They are only on the `/tables` hit and `GET /tables/{id}`. There, `discontinued` appears at SSB and SCB only when it is `true` (2 of 43 SCB hits, 2026-10-13), and never at Latvia (0 of 100 hits with `includeDiscontinued=true`, 2026-10-14).
- **The aggregation that produced a figure.** An omitted dimension is eliminated and **disappears from `id` and `dimension` entirely** — the dataset does not record that it was summed away, or over what.
- **Which codelist a code came from.** Requesting `codelist[Var]=…` leaves no trace in the response: the dimension comes back with the codelist's codes and an `extension` that names no codelist (SCB TAB6471 with `vs_CKM02Län`: `{"elimination": false, "show": "code_value"}`, 2026-10-14). Two different aggregations of the same variable produce datasets that look alike and are not.

These are reasons to state your selection alongside your numbers rather than relying on the response to document itself.

---

## Tooling

Client libraries exist for JavaScript, Python, R, Java and Julia — see https://json-stat.org/. Useful in practice:

- **Python** — `pyjstat` converts json-stat into pandas DataFrames.
- **R** — `rjstat`. SSB additionally publishes `PxWebApiData` on CRAN, which reads PxWeb data from Statistics Norway, Statistics Sweden and Statistics Finland. It supports **both API versions** (1.9.0, 2026-02-02) and ships a separate vignette for each. The v2 interface is snake_case — `api_data()`, `get_api_data()`, `query_url()`, plus `meta_frames()`, `meta_code_list()` and `meta_data()`, each with `_1`/`_2`/`_12` variants returning labels, codes or both — against v1's camelCase `ApiData()`.
- **Node.js** — the json-stat Toolkit's command-line converters (`jsonstat2csv`, `csv2jsonstat`, `jsonstat2arrow`, `sdmx2jsonstat`, …). `jsonstat2csv` gives better control over separators and decimal characters than the API's own CSV output.
- **Browsing** — the json-stat explorer at https://json-stat.com/explorer, plus a JSON viewer extension (built into Firefox; jsonview.com for Chromium).
- **Reading guide** — Idescat's JSON-stat skill (https://www.idescat.cat/dev/api/taules/jsonstat/SKILL.md, CC BY 4.0): a short, provider-neutral guide to reading a dataset.
