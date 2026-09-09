# Troubleshooting PxWebApi v2

Common errors and solutions.

---

## HTTP error codes

### 400 Bad Request

Invalid request. **Diagnose from `title`, not from `detail`** — `detail` is usually absent. The payload is a small JSON object with `type`, `title` and `status`; `type` is a plain string, not a URI, so treat it as a category label rather than as an RFC 7807 problem type.

The observed `title` values and what each one means:

| `title` | Cause | Fix |
|---|---|---|
| `Non-existent variable` | A `variableCode` / `valueCodes[…]` key is not in the table | Re-fetch metadata and compare the name. Variable and value codes are **not** case-sensitive (`tid`, `contentscode`, `TOP(1)` all accepted on SSB, SCB and Latvia, 2026-09-09), so this error means the name is wrong, not its case. Codelist IDs *are* case-sensitive — see `codelists-and-filters.md` |
| `Non-existent value` | The variable exists, the value code does not | Check `dimension.{var}.category.index`; watch for codelist prefixes |
| `Missing selection for mandantory variable` | A variable with `elimination: false` was omitted | Add it. Note the API's spelling, `mandantory` (sic) — quote it as-is or a log search won't match |
| `Too many cells selected` | Result exceeds `maxDataCells` from `/config` | Narrow the selection — see "Too many cells" below. **This is the one case that also sets `detail`** |
| `Illegal selection expression` | A function with a comma — `range(a,b)`, `top(N,offset)`, `bottom(N,offset)` — written bare in a **GET** URL | Wrap it in square brackets: `valueCodes[Tid]=[range(2024M01,2024M03)]`. The comma is the GET list separator. In a POST body use the bare string instead — see `codelists-and-filters.md` |

Useful positive finding: this payload shape is **identical across installations** — all five titles verified on SSB, SCB and Latvia (2026-09-08), including the `mandantory` spelling. Unlike PxWebApi v1 — where several installations return a bare `Bad Request` with no diagnostic and you have to bisect the selection to find the offending part — a v2 400 tells you what went wrong. Read the `title` before changing anything.

**Other causes that surface as one of the titles above:**
- Wrong time format — using `"2024"` in a monthly table (should be `"2024M01"`). Check `timeUnit` on the `/tables` hit; it is not in the json-stat2 document
- Invalid codelist ID — codelist does not exist for this variable
- Missing `OutputFormatParams` in `POST /savedqueries` — the field is required in the request body even when empty. Send `"outputFormatParams": []` if you don't need any. Symptom: `400 — "The OutputFormatParams field is required."`
- `outputFormatParams` sent together with `outputFormat=json-stat2` (or omitted `outputFormat` on a json-stat2-default installation) — the parameters apply to csv, html and xlsx only; with json-stat2 the call is refused with 400 on all three installations (2026-09-09)

**Solution:** Re-fetch metadata and compare variable codes and value codes exactly.

### curl: `bad range in URL` is not an API error

curl treats `[` and `]` as its own globbing syntax, so a URL with `valueCodes[Region]=…` fails locally, before any request is made:

```
curl: (3) bad range in URL position 66:
```

Pass `-g` (`--globoff`), or URL-encode the brackets as `%5B`/`%5D` — the API accepts both. The same applies to bracketed expressions such as `[range(2024M01,2024M03)]`. If you get no JSON at all, check this first.

### 403 Forbidden

Request understood but denied. The table may not be available via API. **Note:** exceeding the cell limit is a **400** in v2, not a 403 — if you are porting knowledge from PxWebApi v1, where the cell-limit response *is* 403, that mapping does not carry over.

### 404 Not Found

Resource does not exist. Wrong table ID, codelist ID, or saved query ID — **or a GET URL longer than roughly 2 100 characters**, which returns 404 rather than 400 on SSB, SCB and Latvia alike (verified 2026-09-09 with a few hundred explicit codes in one `valueCodes[…]`). Replace long value lists with `*`, `?`, `from()`/`to()`/`[range()]` or a codelist, or switch to POST. The v1 `navigation` endpoint also answers 404 on every v2 installation — the subject hierarchy is in `paths` on each `/tables` hit instead.

**Solution:** Use `GET /tables?query=...` to find the correct ID; if the URL is long, shorten it before concluding the resource is missing.

### 429 Too Many Requests

Rate-limited. The limit is announced in `/config` *or* in `x-ratelimit-*` headers depending on the installation — table and header meanings in `api-details.md`. Run large queries sequentially — wait for one response before sending the next.

### 503 Service Unavailable

The installation is down or reloading. SSB, for instance, refreshes metadata at fixed times each day and the tables are unavailable meanwhile (`api-details.md`). Wait and retry. If it does not come back, apply the fallback in `SKILL.md`: say that the data could not be fetched — never fill the gap from memory.

---

## Common problems

### Too many cells

Cell count = product of number of values per variable. Solution: limit time with `top(N)`, limit region, use codelists for aggregation, select a specific metric value (the `role.metric` variable — often `ContentsCode` in Nordic installations), or omit variables with `elimination: true`.

**Tip:** Fetch `defaultselection` first — it is designed to stay within the cell limit.

### Empty or unexpected search results

- Try alternative keywords or synonyms in the agency's language
- Use `includeDiscontinued=true` for historical series — but a frozen table is often *not* flagged; compare `lastPeriod` with today (SCB TAB638 stops at 2024 with `discontinued: null`; Latvia omits the key from `/tables` hits entirely)
- Check pagination: default `pageSize` is 20 and `page.totalElements` tells you how many hits you have not seen

### Special values in data

`status` maps an index in `value` to a symbol and the value is `null` — symbols and their meanings are in `json-stat2.md`. They vary per agency and per PX file; never treat one as zero.

### The response is not JSON

A body starting `CHARSET="ANSI";` or served as `application/octet-stream` is a **PX file**: you omitted `outputFormat` on an installation whose `defaultDataFormat` is `px` (Latvia). Add `outputFormat=json-stat2`. An HTML body with HTTP 200 on `/config` means the URL is not a v2 installation at all (Statistics Greenland) — see the version check in `SKILL.md`.

### A `GET /data` with no selection returned "something"

Not an error, and not the whole table: it is the table's default selection, verified 2026-08-30 and 2026-09-08. SSB 07459 returns `size [360, 1, 1]` — three of its five dimensions, `Kjonn` and `Alder` summed away. SCB TAB6471 returns `size [3, 1, 1, 1]` with `Region` **absent from `id` altogether**, because the default has an empty value list for it. Latvia IRS010m returns `id: ["TIME", "ContentsCode"]` where the metadata says `["ContentsCode", "TIME"]` — so index `value` by the `id` of the response you hold, never by the metadata's order. In every case the response says nothing about what is missing. Build the selection yourself.

### A search returns 0 hits for a word that is obviously in a title

Truncation matches the *stemmed* index term. `population*` is 0 hits at Latvia and at SSB's English index; `popul*` finds 203 and 403. Swedish `folkmängd*` is 0 at SCB; `folkmäng*` finds 117. Truncate before the ending, or search the full word without a wildcard. A leading wildcard returns HTTP 500 at Latvia.

### Data looks wrong over time

- Administrative boundary changes (municipality mergers, regional reforms) can break time series — use aggregation codelists for consistent series
- Classification schemes (NACE, ISCED) may change between revisions
- Index base years change periodically
- National accounts are revised (preliminary → final figures)
