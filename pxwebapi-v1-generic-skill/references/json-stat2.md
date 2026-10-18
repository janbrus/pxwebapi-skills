# json-stat2 — format reference

json-stat2 is an open format for statistical datasets (https://json-stat.org/). PxWebApi v1
returns it when you ask for `"response": {"format": "json-stat2"}`, and the structure is the one
PxWebApi v2, Eurostat and the World Bank produce too. This file describes the format as v1
delivers it, and says where SSB's v1 and SCB's v1 differ. v1's request shape is in
`query-syntax.md`.

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

1. **Only the data response is json-stat2.** A GET on the table URL returns v1's own thin
   metadata (`{"title", "variables": [{"code", "text", "values", "valueTexts", "elimination",
   "time"}]}`). `role`, units, decimals, notes and `extension` arrive only with the data. When the
   metadata leaves you guessing, run a `top`-1 probe query. (See "Dataset structure and
   indexing")
2. **Start with `role`, then look in `id`.** `metric` is what is measured and `time` is time.
   `geo` is optional: SSB's v1 and Finland set it, SCB's v1 does not. Look for a geographic variable in `id`;
   only when none exists — the table has none, or you eliminated it — do the figures cover the
   whole country or area. Do not ask the user. (See "The fields in the dataset")
3. **Positions follow the table's order, not your query's.** `value` is row-major, but v1 sorts
   the values you asked for into the table's own order — the opposite of v2. Always look the
   position up in `category.index`, iterate `id`, and never filter out `null`. (See "Dataset
   structure and indexing")
4. **Read `value` and `status` separately.** If the cell is `null`, show the symbol, never 0. If
   it has a number, show the number with its flag. (SKILL.md Data integrity, and `status`)
5. **Show mandatory notes.** `extension.noteMandatory` flags table notes, and
   `categoryNoteMandatory` flags value notes. Both arrive with the data, and v1's metadata has
   no notes at all. (SKILL.md Data integrity, and `note`)
6. **Read eliminability from v1's metadata** (`variables[].elimination`), not from the data
   response. (See `elimination`, and `query-syntax.md` for the three rules)
7. **Treat `aggregallowed: false` as "do not sum or average".** Whether it also blocks `agg:`
   varies by installation, and three of seven do not send it at all. (See `extension.px`)
8. **State the `agg:`/`vs:` you used, the variables you eliminated and the frequency yourself.**
   The response records none of them, and v1 has no `timeUnit`. (See "What json-stat2 cannot
   express")

---

## Dataset structure and indexing

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

Older serializers may omit `"version": "2.0"` (Statistics Faroe Islands currently does). The rest
of the structure is unaffected.

`value` is row-major, as in C and NumPy. For `size = [s₀, s₁, …, sₙ]` and category indices
`(i₀, i₁, …, iₙ)` the position is `i₀·(s₁·…·sₙ) + i₁·(s₂·…·sₙ) + … + iₙ`. With two regions and
three years, `id = ["Region", "ContentsCode", "Tid"]` and `size = [2, 1, 3]`. Strides: `Region`
1·3 = 3, `ContentsCode` 3, `Tid` 1.

| Position in `value` | `Region` | `Tid` | Offset |
|---|---|---|---|
| 0, 1, 2 | index 0 | index 0, 1, 2 | `0·3 + 0·3 + t·1` |
| 3, 4, 5 | index 1 | index 0, 1, 2 | `1·3 + 0·3 + t·1` |

The second region's third year is `1·3 + 0·3 + 2·1 = 5`, so `value[5]`. A dimension of size 1
always contributes 0.

**Which region is index 1 depends on the table, not on your query.** At SSB's v1, `item` values
`["4601", "0301"]` on 07459 come back as `{"0301": 0, "4601": 1}`, and years asked for as
`["2026", "2024", "2025"]` come back as `{"2024": 0, "2025": 1, "2026": 2}`. SCB's v1 does the
same: `["0180", "0140"]` on `BefolkningNy` gives `{"0140": 0, "0180": 1}` (both 2026-10-14). v2
does the opposite and keeps the order of the request, so code ported from a v2 client that
assumes request order puts figures under the wrong labels. The keys of `dimension` come in `id`
order at SSB's v1 and v2, SCB, Latvia and Eurostat (2026-10-02), but the specification does not
promise it.

To test an implementation, use https://json-stat.org/samples/order.json, where every value is a
string naming its own position (`A2B1C3`) and `category.index` is in array form. Position 11 in
that file reads `A1B1C4` where it should read `A2B1C4` (a typo, checked 2026-10-02), so correct
code "fails" exactly there.

---

## Shape variants

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

## The fields in the dataset

| Field | What it is |
|---|---|
| `id`, `size` | The variables in the order that governs indexing, and the number of values per variable |
| `value` | The figures as one flat list, with `null` where a figure is missing |
| `status` | Flags per cell, keyed by position in `value`. Absent when no cell is flagged |
| `dimension` | Per variable: codes, labels, unit, notes, `extension` and `link` |
| `role` | `time`, `metric` and, at SSB's v1 and Finland, `geo`. The other variables in `id` are breakdowns |
| `note` | Table notes: boundary changes, base-year changes, coverage gaps |
| `extension`, `link` | The installation's own fields and links, see below |
| `label`, `source`, `updated` | Title, source and last update |

Because v1's metadata has no `role`, the data response is also the reliable way to identify the
metric on an unfamiliar installation: Statistics Finland calls it `contentscode`, and other
installations differ again.

---

## `dimension` and `extension` per variable

`dimension.{var}` has `category.index` (code → position) and `category.label` (code → name). The
metric variable also has `category.unit` per value: `base` is the unit and `decimals` the number
of decimals to show. Notes sit per variable (`note`) and per value (`category.note`, value code →
list). None of this is in v1's metadata.

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

`dimension.{var}.extension` has these fields at SSB's v1 and SCB's v1 (2026-10-14). The PX keyword
each comes from is in parentheses (source: `PxTools/PCAxis.Serializers`, `JsonStat2Serializer.cs`):

| Field | Meaning |
|---|---|
| `elimination` (`ELIMINATION`) | Describes the extract, not the table — see below |
| `eliminationValueCode` (`ELIMINATION`) | The total code, when the response includes it (SCB `Region` → `"00"`) |
| `show` (`PRESTEXT`) | `code`, `value` or `code_value` |
| `categoryNoteMandatory` (`VALUENOTEX`) | Which value notes must be shown: value code → index into `category.note`. SCB `Region`: `{"0140": {"1": true}}` |
| `measuringType` (`STOCKFA`) | `Stock`, `Flow`, `Average` or `Other` |
| `priceType` (`CFPRICES`) | `Current`, `Fixed` or `NotApplicable` |
| `adjustment` (`DAYADJ`, `SEASADJ`) | `SesOnly`, `WorkAndSes` or `None` |
| `basePeriod` (`BASEPERIOD`) | The base period of an index (SSB 14700) |
| `refperiod` (`REFPERIOD`) | The reference time, e.g. `1.1.` for a stock |

The last five sit on the metric variable only. They belong in a careful presentation of the
numbers: an index without its base period is meaningless, and a fixed-price series compared with a
current-price one is wrong. Unlike v2, there is no `codelists` field — v1 has no codelist
endpoint — and no `alternativeText`.

### `elimination`

In a data response `elimination` describes the extract you received, not whether the variable
may be left out: SSB's v1 says `false` for `Region` when you select `0301`, although its metadata
says `true` (2026-10-14). The contract is `variables[].elimination` in v1's metadata, where an absent
field means `false`. PX has two forms, `ELIMINATION("<variable>")=YES` (no total value; the API
sums) and `ELIMINATION("<variable>")="<value name>"` (a named total), and v1 adds a third rule for
variables without the keyword: omitting them returns **all** values instead of failing. The three
rules are in `query-syntax.md`, and the PX side in `px-files-and-classifications.md`.

---

## `extension` at the root and `extension.px`

The root `extension` has `contact`, `px` and, when the table has mandatory notes, `noteMandatory`
(`NOTEX`). `discontinued` is always `null` (SSB's v1 and SCB's v1, 2026-10-14); v1 has no
discontinued flag anywhere else either, so check titles and last periods instead (SKILL.md).

PxWeb puts part of the source PX file's header in `extension.px`, only in the **data** response.
Each key is a PX keyword in lower case (`AGGREGALLOWED` becomes `aggregallowed`). SSB's v1 and
SCB's v1 send the same 14 keys as v2, with `copyright: false` (2026-10-14):

| Key | Meaning |
|---|---|
| `contents` | The short title |
| `heading`, `stub` | The publisher's pivot: the variables in the column head and in the stub |
| `decimals` | The table's default number of decimals (per-value decimals are in `category.unit`) |
| `aggregallowed` | Whether summing is meaningful — see below |
| `tableid`, `matrix` | The table ID |
| `subject-code`, `subject-area` | The subject classification |
| `language` | Follows the URL's language at SSB and SCB. File-based installations may report the PX file's main language instead: Finland returns `fi` on an `/en/` URL (2026-10-14) |
| `official-statistics`, `copyright`, `descriptiondefault`, `infofile` | Flags and a reference from the PX file |

`aggregallowed` is a hint about interpretation. It is **absent at three of the seven verified
installations**, and where it is `false` the installations do not agree on what follows — SSB's
v1 rejects `agg:` with 400, SCB's serves the data (verified 2026-09-04). The full matrix, the
controls behind it and the SSB-v1-vs-v2 difference are in `px-files-and-classifications.md`.
Non-PxWeb json-stat producers have no `extension.px` at all.

---

## `status`, `note` and `link`

### `status`

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

### `note`

v1's metadata endpoint has no notes, so the data response is the only place they appear. Two
levels have been seen flagged as mandatory (2026-10-14):

| Level | The notes | Which must be shown | Seen at |
|---|---|---|---|
| Table | `note` (root, list) | `extension.noteMandatory`, keyed by index: `{"1": true}` means `note[1]` | SSB's v1 (14700), SCB's v1 (`BefolkningNy`) |
| Value | `dimension.{var}.category.note` (value code → list) | `dimension.{var}.extension.categoryNoteMandatory`, value code → index: `{"0140": {"1": true}}` means `category.note["0140"][1]` | SCB's v1 |

A third level, per variable (`dimension.{var}.extension.noteMandatory`), exists at SCB's v2
(population per month, `Alder`); no v1 table with such a note has been checked. Look for it. The index differs per table, so resolve it rather than assuming the first
note. Value-level notes come only for the values you selected.

### `link`

`link.describedby` per variable differs between the two relational installations (2026-10-14):

- **SSB's v1** sends URNs, and a variable can carry two in one space-separated string:
  `{"Region": "urn:ssb:classification:klass:104 urn:ssb:classification:klass:131"}`. On the
  metric variable the key is the value code (`{"KpiIndMnd": "urn:ssb:conceptvariable:vardok:2755"}`).
  The trailing number is a Klass id, resolvable as `https://www.ssb.no/klass/klassifikasjoner/104`
  or `https://data.ssb.no/api/klass/v1/classifications/104`; a VarDok URN resolves as
  `https://www.ssb.no/a/metadata/conceptvariable/vardok/2755/nb` (`/nb`, `/nn` or `/en`).
- **SCB's v1** sends plain text, not a URN: `{"Kon": "Kön"}`.

Neither sends `link.related`, which SSB's and SCB's v2 do.

---

## What json-stat2 cannot express

Worth knowing when moving between PX and json-stat, because the loss is silent:

- **Time periodicity.** PX declares it explicitly (`TIMEVAL(...)=TLIST(A1|H1|Q1|M1|W1)`, which also
  guarantees consecutive periods). json-stat2 has no standard field for it — `role.time` names the
  time dimension but says nothing about its frequency. PxWebApi v2 works around this with
  `timeUnit` on the table resource, *outside* the json-stat2 document; v1 does not expose it at all.
  Consumers must infer frequency from the shape of the value codes, and those codes are not
  guaranteed to be dates (see `query-syntax.md`). The absence is a PxWeb choice rather than a hard
  limit of the format: PxWeb already ships PX header keywords in `extension.px`, and TLIST simply
  is not among them.
- **The aggregation that produced a figure.** Eliminated dimensions vanish from `id` and
  `dimension` entirely, so a dataset does not record what was summed away.
- **Which codelist or valueset a code came from.** In v1 the `agg:`/`vs:` used in the request
  leaves no trace in the response.

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
