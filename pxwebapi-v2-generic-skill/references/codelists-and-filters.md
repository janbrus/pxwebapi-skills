# Codelists and filter syntax

Reference for codelists and filter expressions in PxWebApi v2.

---

## Codelists

### Two types of codelists

| Type | Prefix | Description | Example |
|---|---|---|---|
| **Aggregation** | `agg_` | Maps many values to one (e.g. municipalities → regions) | `agg_RegionLevel` |
| **Valueset** | `vs_` | Shows an alternative set of values | `vs_RegionOnly` |

Codelist IDs and prefixes vary between installations and tables, and IDs are **case-sensitive** — use the exact string from metadata.

### Where codelists come from, and why mixing them fails

The two prefixes are not two flavours of the same thing — they sit at different levels, and knowing this explains most codelist errors.

Underneath PxWeb, a **valueset** is a named list of value codes for a variable, and an **aggregation** is a set of groups built on top of one specific valueset. In file-based installations these are literally files (`.VS` and `.AGG`) beside the table; in relational installations (SSB, SCB) the database manages them. Either way the relationship is the same:

> **An aggregation is defined on a valueset, not on a variable.**

That single fact is the reason for the "never mix codelists" rule. `agg_X` is valid only while the variable is expressed through the valueset `agg_X` belongs to. Combine an aggregation from one valueset with codes from another and you get a `400`, on a query that otherwise looks well-formed.

Two more consequences worth carrying:

- **Codelist names are not namespaced by table.** Several tables can share one aggregation, and one variable can offer several. This is why copying a codelist name from another table's query so often fails — always read `extension.codelists` for the table in hand.
- **Hierarchical code prefixes are meaningful.** A hierarchical valueset defines its levels by character position, so a code like `01.111` decomposes as `01` → `01.1` → `01.11` → `01.111`. That is why a wildcard such as `01*` lines up cleanly with a classification level instead of matching arbitrarily.

Whether an installation makes aggregation meaningful at all is recorded separately, in `extension.px.aggregallowed` on the dataset — see `json-stat2.md`.

### Finding available codelists

Codelists are listed in metadata under `dimension.{variable}.extension.codelists`.

### Using a codelist in a data query

**POST:**
```json
{
  "selection": [
    {
      "variableCode": "Region",
      "codelist": "agg_RegionLevel",
      "valueCodes": ["*"]
    },
    {
      "variableCode": "ContentsCode",
      "valueCodes": ["Population"]
    },
    {
      "variableCode": "Tid",
      "valueCodes": ["top(5)"]
    }
  ]
}
```

**GET:**
```
GET /tables/{id}/data?valueCodes[Region]=*&codelist[Region]=agg_RegionLevel&valueCodes[ContentsCode]=Population&valueCodes[Tid]=top(5)
```

Which variables must be included is read from `extension.elimination` in the metadata response — per table, not per installation (see `SKILL.md` Step 3).

### Looking up codelist contents

```
GET /codelists/{codelist_id}?lang=en
```

Returns all codes with labels and `valueMap` showing which original codes map to each aggregated code.

### outputValues parameter — not load-bearing

The specification describes `outputValues[variable]=aggregated|single` as controlling whether an aggregation codelist returns summed or individual values, and `pxweb-mcp` maps `output_values` to it. **On both installations where it has been tested it has no observable effect**: SSB (2026-08-30) and SCB (2026-09-07) return identical data for `aggregated`, `single`, the parameter omitted, and the invalid value `nonsense` — HTTP 200 for all four, so the value is not even validated. It is the codelist that aggregates. Do not rely on the parameter, and do not read a 200 as confirmation that it worked.

---

## Filter expressions in valueCodes

### Function-based filters

| Expression | Description | Example |
|---|---|---|
| `top(N)` | Last N values (newest) | `top(5)` → last 5 periods |
| `bottom(N)` | First N values (oldest) | `bottom(3)` → 3 oldest periods |
| `from(value)` | From and including (inclusive) | `from(2020)` → 2020 onwards |
| `to(value)` | Up to and including (inclusive) | `to(2022)` → up to 2022 |
| `range(from,to)` | Closed interval, both ends inclusive | `range(2024M01,2024M03)` → 3 months |
| `top(N,offset)` | N values, skipping the last `offset` | `top(3,2)` → the 3 before the last 2 |
| `bottom(N,offset)` | N values, skipping the first `offset` | `bottom(2,1)` → the 2 after the first |

All verified on SSB, SCB and Latvia (2026-09-09); case does not matter (`TOP(3)` works). An expression **can be mixed with explicit codes** in the same array — `["2015", "top(2)"]` returns 2015 plus the two newest periods (verified on all three installations, GET and POST, 2026-09-09). What does *not* work is two function expressions as an intersection: `["from(2024M01)", "to(2024M03)"]` in one array returns the **union** (319 periods), not the interval — use `range()` for that.

### GET and POST spell the expressions differently

| | GET (`valueCodes[Var]=`) | POST (`"valueCodes": [...]`) |
|---|---|---|
| Single-argument function | `top(3)` or `[top(3)]` — both work | `"top(3)"` |
| Function with a comma | **`[range(2024M01,2024M03)]`, `[top(3,2)]` — brackets required** | `"range(2024M01,2024M03)"`, `"top(3,2)"` — **no brackets** |
| Explicit list | `2024M01,2024M02` — no brackets | `"2024M01", "2024M02"` |

The reason is the comma: in a GET value it is the list separator, so the API needs the brackets to read `range(a,b)` as one expression. Unwrapped it answers `400 — "Illegal selection expression"`, which looks exactly like "this function does not exist" and was documented as such in 0.11.0's first draft until a bracketed URL from the maintainer disproved it. In a POST body the string is already one element, and a bracketed string is looked up as a literal code (`400 — "Non-existent value"`). Verified on all three installations, both directions.

The brackets — and the ones in `valueCodes[Var]` itself — trip **curl**: it treats `[…]` as its own globbing syntax and stops locally with `curl: (3) bad range in URL` before anything is sent. Pass `-g` (`--globoff`), or URL-encode the brackets as `%5B`/`%5D`; the API accepts both.

**For the time dimension, prefer `top(N)` and `from(value)` over explicit period codes.** Relative filters pick up new periods automatically, so a shareable GET URL or a saved query keeps returning current data. This matters most for `/savedqueries`, whose whole purpose is to be re-run later.

### Wildcard filters

| Expression | Description | Example |
|---|---|---|
| `*` | All values, or matches zero or more characters | `*` alone = all values; `03*` = codes starting with "03" |
| `?` | Matches exactly one character | `??` = all two-digit codes |

`*` alone in valueCodes means "select all values for this variable". Combined with a codelist, it means "all values in the codelist". Codes are strings — always quoted in a POST body, even purely numeric ones (`"0301"`, `"2024"`).

Wildcards can be combined with explicit codes in the same valueCodes array:
```json
{ "variableCode": "Region", "valueCodes": ["0301", "46*"] }
```

### Time formats

The format in valueCodes must match the table's `timeUnit` — and **the period letter is a per-installation (and per-language) choice**. Verified forms, 2026-09-08:

| timeUnit | SSB | SCB | Latvia |
|---|---|---|---|
| Annual | `2024` | `2024` | `2024` |
| Monthly | `2024M06` | `2024M06` | `2026M04` |
| Quarterly | `2024K2` | `2020K4` | `2026Q2` |
| Weekly | `2026U35` | `2026V30` | `2026W13` |
| Other | — | — | `Time01` (not a date at all) |

Only the annual and monthly forms are universal. Quarters are `K` in the Nordic installations and `Q` at Latvia; weeks use three different letters on three installations, so a `W` written from habit returns `Non-existent value` at SSB and SCB. **Read the codes from `category.index` before writing a time filter** — they are the only reliable source.

---
