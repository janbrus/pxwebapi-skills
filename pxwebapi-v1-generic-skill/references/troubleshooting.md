# Troubleshooting PxWebApi v1

**Diagnostics vary enormously between installations, and most give you nothing.** Verified across
four installations on 2026-08-28 and two more on 2026-08-31:

| Installation | 400 body | Cell-limit body |
|---|---|---|
| SSB | JSON: `{"error":"…"}`, three distinct messages | `403 {"error":"Too many values selected"}` |
| SCB | plain text `Bad Request` | — |
| Statistics Finland | plain text `Bad Request` | `403` + an **IIS HTML page** (`403 - Forbidden: Access is denied.`) |
| Statistics Greenland | plain text `Bad Request` | — |
| Nordic Health and Welfare Statistics | plain text `Bad Request` | — |
| Judicial statistics, Spain | plain text **`Solicitud incorrecta`** | — |

So the diagnostic messages documented below are **an SSB feature, not a v1 feature**. On every
other installation tested, a 400 tells you only that something in the request was wrong. Plan for
that: see "Debugging without diagnostics".

**The bare error text is localised.** Spain answers `Solicitud incorrecta` — its own language, not
English. Any code or reasoning that tests for the literal string `Bad Request` will classify that
response as something else and may read a failed call as an empty result. The rule that holds
across installations is structural, not textual:

> **Any 4xx without a JSON body is a failed request.** Do not match on the message.

Two corollaries worth keeping in view. A 200 is not proof of success either — at least one
installation (Statistics Greenland, on its v2 endpoint) answers 200 with `text/html` and an error
in the body, so **check that the body parses as JSON**. And a 403 here means "too big", not "not
allowed" — see below.

---

## HTTP status codes

| Code | Meaning | Typical cause |
|---|---|---|
| 200 | OK | — |
| 400 | Bad Request | Malformed JSON, unknown variable, bad value code, bad filter, unsupported format, unsupported `?query=` |
| 403 | Forbidden | **Result exceeds the cell limit** — not an authorisation problem |
| 404 | Not Found | Wrong table id, path, language or database segment |
| 429 | Too Many Requests | Rate limit exceeded |
| 503 | Service Unavailable | Timeout (60 s at SSB), or heavy load — common with large `xlsx` extracts |

**403 is the surprise.** Most APIs signal an oversized result with 413 or 400. PxWeb v1 uses 403
with the body `{"error":"Too many values selected"}`. Read it as "too big", not "not allowed".

---

## SSB's three error messages

Only SSB returns these. They are worth knowing because SSB is the installation most often queried,
and the distinction between the first two saves real time.

### `{"error":"Parameter error"}` — the request could not be parsed

The request never reached value validation. Causes, in order of likelihood:

- Malformed JSON (truncated body, trailing comma, unbalanced brackets).
- A `code` that is not a variable in this table — including a case mismatch.
- An unsupported `"response": {"format": …}` value. **Most often: `jsonstat2` or `jsonstat`
  instead of `json-stat2` / `json-stat`.**
- Missing or wrong `Content-Type: application/json`.

Fix: validate the JSON, then re-fetch metadata with a GET on the same URL and compare every
`code` character for character.

### `{"error":"The request for variable 'X' has an error. Please check your query."}` — the variable is real, its selection is not

The structure parsed and `X` exists, but its `selection` is unusable:

- A value code not present in that variable's `values`.
- A wrong time format — `"2024"` in a monthly table that wants `"2024M06"`.
- An unknown aggregation or value set — `agg:KommSummer` where the table's aggregation is
  actually `agg:KommFylker`.
- Aggregation member codes without their prefix — `0301` instead of `K-0301`, `03` instead of
  `F-03`.
- `{"filter": "agg:X", "values": ["*"]}` — **wildcards are not allowed with `agg:`**.
- `?` used for single-character masking — not supported by v1 at all.
- `top` given something other than one positive integer as a string.

Fix: GET the metadata and check `values` for that variable. If the filter is `agg:` or `vs:`,
metadata will not help — see "Discovering aggregations" in `query-syntax.md`.

### `{"error":"Too many values selected"}` with 403 — over the cell limit

Cell count is the product of the selected value counts across **all** variables, empty cells
included. Reduce it by:

- Limiting time with `{"filter": "top", "values": ["N"]}`.
- Naming specific regions instead of `{"filter": "all", "values": ["*"]}`.
- Selecting one metric value rather than all of them.
- Using an `agg:` grouping instead of individual values.
- Omitting eliminable variables — **but check `elimination` first.** Omitting a variable whose
  `elimination` is `false` or absent returns *all* of its values and makes the problem worse.

Read the limit rather than guessing: `GET {host}/{apiname}/{apiversion}/{lang}/?config` returns
`maxCells` and `maxValues`. They differ by two orders of magnitude across installations (Iceland
100,000 cells / 5,000 values; SSB 800,000 / 50,000; Estonia 25,000,000), and `maxValues` can be
breached while the cell count still looks safe.

---

## Debugging without diagnostics

On SCB, Finland, Greenland and most other installations a 400 is opaque. Bisect instead of
guessing — each step is one cheap request:

1. **GET the table URL.** If that fails, the path or table id is wrong (a missing `.px`, or the
   wrong language/database segment), not the query.
2. **POST the minimal legal body**, `{"query": [], "response": {"format": "json-stat2"}}`. If this
   400s, the problem is the envelope or the format name — check the hyphen in `json-stat2`. If it
   403s, the table is simply too big to take whole (see below); that is not a syntax error.
3. **Add one selection object at a time**, re-POSTing after each. The first one that flips the
   response to 400 identifies the offending variable.
4. **Within that variable, replace the filter with `{"filter": "top", "values": ["1"]}`.** If that
   succeeds, the variable code is fine and the problem is in your value codes — compare them
   character for character against `values` in the metadata, watching for case, spaces inside
   codes, and time granularity (`2025` in a monthly table wants `2025M01`).

Step 2 doubles as a cheap way to read `role` and `unit` off an unfamiliar table, provided the
table is small enough to return.

## Symptoms that are not errors

### A GET returned metadata instead of numbers

Working as designed. v1 has **no GET data endpoint** — the table URL serves metadata on GET and
data on POST. If you need a shareable data URL, the installation must be on v2, or you must use
the agency's separate ready-made-dataset API.

### The response is not the format you expected

`"response"` was omitted. **There is no single v1 default** — the same omission produces three
different formats across the seven verified installations, measured 2026-09-04:

| Default when `"response"` is omitted | Installations |
|---|---|
| `json-stat2` | SSB, Statistics Finland, Statistics Estonia |
| PX (as the PxWeb 1.0 spec prescribes) | SCB, Statistics Greenland |
| PX-JSON (`{"columns": …, "data": …}`) | Statistics Faroe Islands, Statistics Iceland |

Always set `"response": {"format": "json-stat2"}` explicitly; all seven accept it.

Two distinct symptoms, and the second is the nastier one:

- **PX** starts `CHARSET="ANSI";`. A JSON parser fails on it immediately, in a way that can look
  like a transport error rather than a format mismatch.
- **PX-JSON parses fine as JSON** — so a "did I get JSON back?" check passes. It simply has none
  of the json-stat2 fields: no `value`, no `dimension`, no `id`, no `role`. Instead there is
  `columns` (one entry per variable plus the metric, tagged `type: "t"` / `"d"` / `"c"`), `data`
  as a list of `{"key": […], "values": […]}` rows, and `metadata`. If your code reports "no data
  found" against a 200 response, check this before blaming the query.

### `?query=` returns 400 Bad Request

Search is not enabled on that installation — verified as absent at SCB and Statistics Iceland.
Navigate the hierarchy instead: GET each level and read the `type: "l"` / `type: "t"` nodes.

### Search returns the same table several times

Expected. A table filed under multiple subjects appears once per path, with identical `id` and
`title` but different `path`. Any of them is a valid POST target.

### A search term that obviously exists returns 0 hits

Terms match whole words unless truncated. `title:boligpris` finds nothing at SSB while
`title:boligpris*` finds matches. Add `*`. Also check the language segment — many tables have
titles in only one written form.

### A variable you omitted came back with every value

Its `elimination` is `false` or absent, so rule 3 applies: all values are returned. Only
`elimination: true` collapses to a total.

### A dimension is missing from the response entirely

It was eliminated. Eliminated variables are dropped from `id` and `dimension` rather than
appearing with size 1. The response therefore does not record what was aggregated away — state
it yourself when presenting the numbers.

### `role` is present in the data but not in the metadata

Correct: v1 metadata has no `role`, `unit` or decimals, but the json-stat2 *data* response does.
When you cannot tell which variable is the metric or the geography, run a minimal probe query
(`top` 1 on the time variable) and read `role` off the result.

### `role.geo` is absent from the response

Either the table has no geographic dimension, or the geographic variable was eliminated. In both
cases the figures cover the whole country or area — do not ask the user to disambiguate.

### Numbers changed between two runs of the same query

- A `top` filter is rolling by design: it follows new publications.
- Preliminary figures get revised to final ones.
- Administrative boundary changes break series built from `item` region codes; `agg:` groupings
  are the fix.
- Classification revisions (NACE, ISCED) and index base-year changes shift the meaning of codes.

### Nulls in `value` with symbols in `status`

Not missing data in the transport sense — deliberate markers, and the symbols are defined per PX
file, so read them rather than assuming. The table of symbols is in `json-stat2.md`. Never treat
any of them as zero.

---

## Sequencing and load

Run large queries in sequence and stay off the minutes after a publishing deadline — the four
practical rules are in `api-details.md` under "Practical guidance". Two response codes matter here:

- 429 means back off, not retry immediately. The limiter counts requests per IP over a sliding
  window; read the actual ceiling from `?config` (300 / 60 s at SSB, 30 / 10 s at SCB, verified
  2026-09-03), never from published documentation.
- 503 usually means the extract was too large or too slow rather than that the service is down.
  Narrow the selection, or switch from `xlsx` to `json-stat2` or `csv3`.
