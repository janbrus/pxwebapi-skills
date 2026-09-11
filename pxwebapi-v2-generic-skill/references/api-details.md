# API details (PxWebApi v2)

For the json-stat2 response format (Dataset structure, indexing, status codes) — see `json-stat2.md`. This file covers PxWebApi-specific configuration.

---

## Checking API configuration

Use `GET {base_url}/config` to see current limits. The response shape is the same across installations, but the concrete values are installation-specific. Full response, verified 2026-08-30 (this one from SSB — yours will differ):

```json
{
  "apiVersion": "2.3.2",
  "appVersion": "2.5.0+build.30",
  "languages": [{"id": "no", "label": "Norsk"}, {"id": "en", "label": "English"}],
  "defaultLanguage": "no",
  "maxDataCells": 800000,
  "maxCallsPerTimeWindow": 0,
  "timeWindow": 0,
  "license": "https://www.ssb.no/en/diverse/lisens",
  "sourceReferences": [
    {"language": "en", "text": "Source: Statistics Norway"},
    {"language": "no", "text": "Kilde: Statistisk sentralbyrå"}
  ],
  "defaultDataFormat": "json-stat2",
  "dataFormats": ["json-stat2", "csv", "px", "xlsx", "html", "json-px", "parquet"],
  "features": [{"id": "CORS", "params": [{"key": "enabled", "value": "True"}]}]
}
```

Three things are worth acting on:

- **`sourceReferences` gives you the agency's own citation string, per language.** Use it verbatim in the source line instead of inventing a wording — it is what the agency wants to be cited as.
- **`maxDataCells` varies by 80×** across the three known installations (SSB 800 000, SCB 150 000, Latvia 10 000). Never carry a limit across installations.
- **`defaultDataFormat` and `dataFormats` are per installation.** SSB and SCB default to `json-stat2`; **Latvia defaults to `px`**. SSB serves `parquet`; SCB and Latvia do not. Read the list before offering a format — and read it critically: Latvia's list contains duplicates and v1-era names (`json_stat2`, `csv3`, `html5_table`) that return 400 when used.

## Verified differences between installations

Everything in this table was observed live on 2026-09-08. It is the evidence behind every "varies by installation" in `SKILL.md`. Search-operator row: `population region` returned 199 at SSB (= AND 199, OR 1 832), 207 at SCB (= AND, OR 1 373) and 494 at Latvia (= OR, AND 125).

| | SSB (Norway) | SCB (Sweden) | CSP (Latvia) |
|---|---|---|---|
| `apiVersion` | 2.3.2 | 2.3.2 | 2.0.0 |
| `maxDataCells` | 800 000 | 150 000 | 10 000 |
| Rate limit announced in | `x-ratelimit-*` headers only (`/config` says 0) | `/config` 30 per 10 s **and** `X-Rate-Limit-*` headers | `/config` 30 per 10 s **and** `x-rate-limit-*` headers |
| `defaultDataFormat` | json-stat2 | json-stat2 | **px** |
| `parquet` | yes | no | no |
| Time variable | `Tid` | `Tid` | `TIME` |
| Geographic variable | `Region` | `Region` | `AREA` |
| `role.geo` set | yes | **no** | yes |
| Quarter code | `2024K2` | `2024K2` | `2026Q2` |
| Week code | `2026U35` | `2026V30` | `2026W13` |
| `discontinued` on `/tables` hit | `null` | `null` | **absent** |
| `/tables/{id}` `lastPeriod` vs data | matches | matches | **lags** (2026M04 vs 2026M07 in the data) |
| `range()`/`top(N,offset)` | GET `[range(a,b)]`, POST bare | same | same |
| Search wildcard on stem | `popul*` ok, `population*` 0 | `folkmäng*` ok, `folkmängd*` 0 | `popul*` ok, `population*` 0 |
| Default operator between search words | AND | AND | **OR** |
| 400 payload shape | `type`/`title`/`status` | same | same |
| Variable / value code case | insensitive | insensitive | insensitive |
| Expression + explicit code in one `valueCodes` (`2015,top(2)`) | works | works | works |
| `outputFormatParams` with `json-stat2` | 400 | 400 | 400 |
| CSV `Content-Type` charset | `iso-8859-1` | `iso-8859-1` | **`utf-8`, with BOM** |
| GET URL over ~2 100 chars | 404 | 404 | 404 |
| Repeated value code in one variable | **500**, empty body | **500** | **500** |
| `/navigation` (v1 endpoint) | 404 | 404 | 404 |

(The last six rows verified 2026-09-09.)

Three things are the same everywhere and can be relied on: the metric variable is `ContentsCode`; the five 400 titles are spelled identically (including `mandantory`); every selection expression — `top()`, `bottom()`, `from()`, `to()`, `range()`, the offset forms, wildcards and explicit lists — works, with the same GET-bracket / POST-bare split.

Fields to expect (values vary — never hardcode):

- `apiVersion` / `appVersion` — the PxWebApi contract version and the deployed build. SSB and SCB run API 2.3.2; Latvia runs 2.0.0
- `license` — the licence the data is published under
- `sourceReferences` — the agency's citation string per language
- `features` — optional capabilities, e.g. CORS

- `maxDataCells` — upper bound on cells per query
- `maxCallsPerTimeWindow` / `timeWindow` — rate-limit window in seconds. **`0` means "not in use", not "unlimited"** — see below
- `defaultLanguage` / `languages` — language IDs accepted by `lang=` parameter
- `defaultDataFormat` / `dataFormats` — formats accepted by `outputFormat=` parameter

---

## Rate limiting — check both places

An installation may announce its rate limit in `/config`, in HTTP response headers, or both — and the header *names* differ. Verified 2026-09-08 on all three:

| Installation | `/config` | Response headers |
|---|---|---|
| SSB (Norway) | `maxCallsPerTimeWindow: 0`, `timeWindow: 0` | `x-ratelimit-limit: 40`, `x-ratelimit-policy: 40;w=60s`, `x-ratelimit-remaining`, `x-ratelimit-resource` |
| SCB (Sweden) | `maxCallsPerTimeWindow: 30`, `timeWindow: 10` | `X-Rate-Limit-Limit: 10s`, `X-Rate-Limit-Remaining: 29`, `X-Rate-Limit-Reset: <ISO timestamp>` |
| CSP (Latvia) | `maxCallsPerTimeWindow: 30`, `timeWindow: 10` | `x-rate-limit-limit: 10s`, `x-rate-limit-remaining`, `x-rate-limit-reset` |

Two header schemes, then: SSB's `x-ratelimit-*` (no hyphen inside "ratelimit", limit as a count, window in `-policy`) and the `X-Rate-Limit-*` family at SCB and Latvia (limit field carries the *window* `10s`, the count is only in `/config`, and `-Reset` is a timestamp). Match headers case-insensitively and on both spellings — an earlier version of this file said SCB "sends no headers" because it had only looked for the SSB spelling.

So `/config` alone is not enough at SSB, and the headers alone do not give the count at SCB and Latvia. Read both on your first real call, and treat a `0` in `/config` as "this installation announces the limit elsewhere" — never as "no limit".

| Header | Example | Meaning |
|---|---|---|
| `x-ratelimit-limit` | `40` | Max calls in the window |
| `x-ratelimit-policy` | `40;w=60s` | Limit plus window length: 40 calls per 60 seconds |
| `x-ratelimit-remaining` | `38` | Calls left in the current window |
| `x-ratelimit-resource` | `SB_API_1MIN` | The limit bucket the call counts against |

Check `x-ratelimit-remaining` before a batch of calls. On `429 Too Many Requests`, wait for the window to reset before retrying.

---

## Output formats

Set `outputFormat` explicitly on every data call — the default is per installation (see the table above), and a forgotten parameter at Latvia returns a PX file with `Content-Type: application/octet-stream`.

| Format | `outputFormat` value | Use |
|---|---|---|
| json-stat2 | `json-stat2` | Machine-readable, rich metadata — what this skill assumes |
| CSV | `csv` | Simple tabular format |
| Excel | `xlsx` | For end users |
| HTML | `html` | Table for display |
| PX | `px` | Traditional PX format |
| JSON-PX | `json-px` | JSON variant of PX |
| Parquet | `parquet` | Columnar binary, for large extracts into pandas/Arrow — SSB only among the known installations |

The value is the hyphenated form. Latvia's `dataFormats` also advertises underscore forms (`json_stat2`, `json_stat`) and v1-era names (`csv3`, `html5_table`, `relational_table`); `json_stat2` returns 400 on the same installation that lists it. Trust `/config` for *which* formats exist, and the hyphenated spelling for *how* to ask.

**`outputFormatParams`** (can be combined): `UseCodes`, `UseTexts`, `UseCodesAndTexts`, `IncludeTitle`, `SeparatorTab` / `SeparatorSpace` / `SeparatorSemicolon`. They apply to **csv, html and xlsx only** — sent with `json-stat2` the call is a 400 on all three installations. Without any, you get codes only, no title, and comma as the CSV separator. Several can be given either as a repeated parameter or comma-separated in one (`outputFormatParams=SeparatorSemicolon,UseCodesAndTexts`); both forms work everywhere and the values are not case-sensitive (verified 2026-09-09).

**CSV charset is per installation:** SSB and SCB serve `text/csv; charset=iso-8859-1` (Latin-1); Latvia serves `utf-8` **with a byte-order mark** at the start of the first line — strip it before parsing, or `pd.read_csv(..., encoding="utf-8-sig")`. Read the `Content-Type` header rather than assuming.

**`heading` and `stub`** (comma-separated lists of variable codes) control the pivot for csv/html/xlsx; `extension.px.heading`/`stub` in metadata is the layout the agency itself intends. Putting *every* variable in `stub` gives one row per observation — the long, pivot-friendly shape pandas and Power BI want. In a POST body the same goes in `placement: {"heading": [], "stub": [...]}` next to `selection`.
