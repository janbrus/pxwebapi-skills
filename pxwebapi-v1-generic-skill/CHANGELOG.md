# Changelog — generic-pxweb-v1-skill

The current version is in `SKILL.md` frontmatter under `metadata.version`.
If your copy has no `metadata.version`, it predates 2026-08-30 — get a newer one.
Versions below 1.0.0 mark a skill with no published distribution yet.

## 0.12.0 — 2026-09-03

A structural pass: `SKILL.md` goes from 409 lines / 4 215 words to 299 / 3 534 (−16 % words).
**No knowledge was removed — every cut moved material into `references/`**, which is why three
reference files grew. Alongside that, three factual claims were corrected and one was verified for
the first time.

**Addendum 2026-09-09, before 0.12.0 was committed** — sibling check after the `ssb-pxwebapi-v2`
review of SSB's PxWebApi v2 user guide. None of the day's findings touch the v1 request side
(GET-bracket rule, curl `-g`, `outputFormatParams`, csv charset, URL-length 404 are all v2 or
v2-GET matters). Two rows in `references/v1-vs-v2.md` were extended so a v1 reader translating to
v2 is not misled: the filter row now lists the offset forms `top(n,offset)`/`bottom(n,offset)` and
says that comma expressions must be bracketed in a v2 GET URL; the saved-queries row records that
SSB's v1-era web saved-query IDs (`ssb.no/statbank/sq/{id}`) resolve through v2's
`GET /savedqueries/{id}` and `/data` (verified on 10119120) — the answer for a user who arrives with
an old sq link now that the PxWeb v2 web page for it serves only a screen view. Nothing else
changed.

### Corrections

- **Rate limit at SSB.** `references/troubleshooting.md` said the limiter allows "30 / 60 s at SSB",
  contradicting the `?config`-first rule the rest of the skill is built on. `GET
  https://data.ssb.no/api/v0/no/?config` returns `maxCalls: 300, timeWindow: 60` (verified
  2026-09-03; SCB returns 30 / 10 s). Corrected, and the section now points at `api-details.md`
  rather than restating its four sequencing rules.
- **"Two of these do not follow the pattern"** was followed by three bullets. The exceptions moved
  to `references/installations.md` as "Operational notes for the seven verified installations".
- **`extension.codeLists` → `extension.codelists`.** The JSON field is lowercase; `query-syntax.md`
  and `v1-vs-v2.md` both had the wrong casing, so anyone following them literally would read an
  empty list and conclude the table has no aggregations. The *endpoint path* `/codeLists/` accepts
  either casing — only the response field is case-sensitive. Not present in the v2 skills.

### `aggregallowed` — verified, and version-specific

`px-files-and-classifications.md` claimed that `extension.px.aggregallowed: false` means `agg:`
cannot work on that table, citing SSB table 14710 as a live example. `generic-pxweb-v2-skill` says
the opposite for v2 — a signal about interpretation, not a technical block. **Both are right.**
Verified 2026-09-03 at SSB:

| API | Table | `aggregallowed` | `agg:` | `vs:` |
|---|---|---|---|---|
| v1 | 07459 | `true` | 200 | 200 |
| v1 | 14700 | `false` | **400** | 200 |
| v1 | 11342 | `false` | **400** | 200 |
| v2 | 14700 | `false` | **200 with data** | 200 |

The control that makes this hold is 14700: same table, same variable, same codelist family —
`vs:CoiCop2018Kpi01` returns 200 while `agg:CoiCop2018Kpi011` returns 400, which rules out the
alternative reading that v1 simply does not know that classification. Codes were taken from each
codelist itself, not guessed; two earlier 400s in this investigation turned out to be wrong codes
rather than the flag.

Two scope limits are written into the file: the finding is **v1-specific** (the same aggregation
succeeds in v2, so the two skills must not be reconciled) and **SSB-specific**. 14710 was also a
poor example — it has no aggregatable variable at all — and has been replaced by 14700 and 11342.

**The remaining six installations were then probed too (2026-09-04), and the SSB-specific scoping
turned out to be doing real work:**

| Installation | Flag present | `false` seen | `false` blocks `agg:`? |
|---|---|---|---|
| SSB | yes | yes | **Yes — 400** |
| SCB | yes | yes | **No — 200 with the aggregation applied** |
| Finland | yes | no (`true` even on CPI) | untestable |
| Greenland | yes | no (`true` even on price indices) | untestable |
| Iceland, Faroe Islands, Estonia | **absent** | — | n/a |

Three things follow, and all three contradict how earlier revisions framed the flag:

- **It is not universal.** Three installations return an `extension.px` of one or two keys with no
  `aggregallowed`. The advice "run a probe and read the flag" silently yields nothing there, so
  absence must not be read as `true`.
- **Enforcement differs between installations at the same API version.** SCB's `AKURLBefM`
  (v2 `TAB6387`) is `aggregallowed: false` and answers 200 for `agg:ISD2`, categories correctly
  aggregated. Same experiment, opposite result from SSB.
- **The value is an agency cataloguing choice, not a property of the data.** SSB marks CPI tables
  `false`; Finland and Greenland mark the equivalent tables `true`. The earlier line "typical of
  index tables, where a sum would be meaningless" described SSB's habit, not PxWeb's semantics, and
  has been removed.

`SKILL.md` now presents the flag as a hint rather than a prediction: send the `agg:` query and
handle the response. Two dead ends along the way are worth recording — Greenland answers
`GET /api/v2/config` with **HTTP 200 carrying a custom "File not found" page**, so a status-code
probe alone reports a v2 API that does not exist; and SCB's v1 `BefolkManadCKM` is v2 `TAB6471`,
not the similarly-titled `TAB5444`, whose codelists produce a 400 indistinguishable from a
forbidden aggregation. `references/v1-vs-v2.md` now documents `extension.px.tableid` as the
reliable v1→v2 table mapping.

**Sibling check:** `generic-pxweb-v2-skill` and `ssb-pxwebapi-v2` state the v2 behaviour correctly
and were **not** changed. `scb-pxwebapi-v2` makes no claim about the flag. This is the second round
where the "fix it everywhere" reflex would have introduced an error while removing one — see
`CLAUDE.md`, "The sibling check is a check, not a propagation".

### Removed from `SKILL.md` (moved, not deleted)

- **"Limits"** — the seven-row table lives in `api-details.md`; Step 1 keeps the two rules that
  drive decisions (the ceilings are independent, and the spread between installations is about two
  orders of magnitude).
- **"Response format"** — the status-symbol table duplicated `json-stat2.md` and quietly
  contradicted the integrity rule's own point that symbols are per-PX-file. Step 5 now points there,
  and `json-stat2.md` says explicitly that the three common symbols are defaults, not a fixed set.
- **"PX files behind the API"** and **"Troubleshooting"** — both were pointers with a paragraph
  around them; they are now bullets in Fallback.
- **Sweep statistics in Step 1** (43 of 43, five without `maxCells`, 10 of 26 catalogue mismatches)
  — evidence for the maintainer, not instructions for the model. They live on in
  `installations.md` and in this changelog.
- **The CSV-conventions paragraph** in Step 4 and five of the nine output-format rows; both are
  verbatim in `api-details.md`.

### Integrity fix in the examples

The `?config` example printed Finland's actual figures (`maxValues: 120000`, …) directly beneath the
rule that limits vary by two orders of magnitude and only `?config` may be trusted — an example
contradicting the lesson it illustrates, and a number a model can recite when the call fails.
Replaced with placeholders, since the field *names* are the point. Concrete figures remain in
`api-details.md` and `installations.md`, where they are inventory rather than instruction.

### Found by running the new evals — the default output format is not PX everywhere

The eval scenarios were run as actual end-to-end runs against live installations, not read through.
Scenario 4 broke the skill: it stated in four places that omitting `"response"` gives PX. Verified
2026-09-03 by posting the same body with and without `"response"`:

Extended 2026-09-04 to all seven verified installations. **There are three defaults, not two:**

| Body without `"response"` | Installations |
|---|---|
| **json-stat2** | SSB, Statistics Finland, Statistics Estonia |
| **PX** — `CHARSET="ANSI"; AXIS-VERSION="2010"; …` | SCB, Statistics Greenland |
| **PX-JSON** — `{"columns": […], "data": [{"key": …, "values": …}]}` | Statistics Faroe Islands, Statistics Iceland |

So the PxWeb 1.0 spec's stated default holds at two installations out of seven, one of them the
agency that wrote the spec. All seven accept an explicit `json-stat2`. Corrected in `SKILL.md`
(Step 4 intro, the format table, Pitfalls), `references/query-syntax.md` and
`references/troubleshooting.md`.

**PX-JSON is the trap the two-way version of this finding would have missed.** It parses as JSON,
so a client checking "did I get JSON back?" passes and only then discovers there is no `value`,
`dimension`, `id` or `role` — a different shape entirely. PX at least fails loudly at the parse.
`troubleshooting.md` now names both symptoms separately.

The *advice* was never wrong: always set `"response"` explicitly. The **reason** was, and that is
the worse failure — a reader who has seen one installation return JSON on an omitted `"response"`
would have concluded the skill was simply out of date, rather than that the default varies. This is
the same failure shape as the pre-0.12.0 `aggregallowed` claim: a behaviour that varies by
installation, written down as universal.

Two further observations from walking Greenland, the Faroes and Iceland for that test, both of
which qualify claims already in Step 3:

- **Statistics Iceland's English endpoint returns Icelandic variable codes** — `Ár` and `Eining`,
  accents included. An English URL guarantees English *labels*, not English codes. Added to
  "Never assume variable names", which previously implied the risk was confined to non-Nordic
  naming schemes.
- **`role` can be absent from a data response entirely.** Greenland's `BEXSAT1.PX` returns no
  `role` key at all, because the table sets no `time: true` — on a variable it literally names
  `time`. Step 3 advised a `top`-1 probe to recover `role`; that advice now says what to do when
  the probe comes back without it.

Second eval finding, smaller: a model handed a v2 aggregation id wrote `agg:agg_CoiCop2018Kpi011`,
keeping the `agg_` prefix, and got `{"error":"Parameter error"}`. The `agg_X` → `agg:X` mapping was
documented in `query-syntax.md` and `v1-vs-v2.md` but not in `SKILL.md`, where the filter table
lives. Added there as a half-sentence.

**Sibling check for both:** neither claim appears in `generic-pxweb-v2-skill`, `ssb-pxwebapi-v2` or
`scb-pxwebapi-v2` — v2 sets the format in the query string, so the question does not arise there,
and the `agg_` prefix is correct as-is in v2. Outcome: does not apply. Recorded here so the check
is not repeated.

### New installation: Oslo kommune (Oslostatistikken)

`references/installations.md` goes from 49 to 50 entries. Probed end to end 2026-09-04:
`https://statistikkbanken.oslo.kommune.no/statbank/api/v1/no`, one database `db1`, `?query=`
supported, Norwegian only (`/en` → 400), errors as bare `Bad Request`, default output json-stat2.

It earns a paragraph rather than a table row because almost nothing about it follows from the SSB
entry two lines above it:

- **Variable codes are lowercase Norwegian words** — `bosted`, `kjønn`, `alder`, `år`. Same country
  and same language as SSB, and the `Region`/`Kjonn`/`Alder`/`Tid` convention still does not carry
  across. `år` is `time: true` with **sequence-number codes** (`"36"` → label `"2026"`), the same
  shape as Greenland's time variables — the second confirmed instance of that pattern.
- **Level ids are Norwegian phrases with spaces, commas and å/ø** (`Befolkning/Fødte, døde og
  forventet levealder`), so path segments must be percent-encoded.
- **The widest gap between the two ceilings in the whole file**: `maxValues` 1 000 against
  `maxCells` 550 000, a factor of 550 where SSB's is 16.

Two claims were drafted and then corrected before landing, both by reading the surrounding file
instead of trusting the new datum: Oslo is **not** the first sub-national installation here
(Linköping, Sundsvall and Västerås were already listed), and its 1 000-value ceiling is **not**
unusually low — it is the single most common `maxValues` in the inventory, on 19 installations, and
looks like the PxWeb default. What is genuinely distinctive is the *ratio*, not either number.

Oslo also meets the criteria for the operational table in `SKILL.md` (DATABASEID known, hierarchy
walked, `?query=` probed). It has deliberately not been promoted there — that table is the
seven-installation orientation list, and the decision to grow it belongs to a separate round.

### Second eval run (2026-09-04), six scenarios including Oslo

All six passed. The run independently reproduced the three-way format-default finding on three
installations — SSB json-stat2, SCB raw PX, Faroe Islands PX-JSON — and reproduced the SSB
`aggregallowed` 400, this time with the correctly stripped `agg:` name. Two gaps it exposed have
been closed:

- **When `agg:` is unavailable, the level you want may already be an ordinary item code.**
  Hierarchical classifications carry their levels in the code itself: SSB 14700's `VareTjenesteGrp`
  runs `00` → `01` → `01.1` → `01.1.1`, and 07459's `Region` runs 1 digit (country) → 2 (county) →
  4 (municipality). Added to Step 4, with the limit that this is **not** a substitute for `agg:` on
  time series — 07459 carries 41 two-digit county codes because it keeps historical ones, so
  selecting them all mixes boundaries across reforms.
- **No recipe for checking a query against the ceilings.** Step 1 now states it: cells are the
  product of the selected value counts, values the sum, both computable from metadata before
  sending anything.

One claim from the run did **not** survive checking and was not written down: it reported a
metadata field `eliminationValueCode` at Statistics Finland. Finland's variable objects carry
`code`, `text`, `values`, `valueTexts`, `elimination`, `time` and `map` — there is no such field,
at Finland or anywhere else probed. Step 3 now says so explicitly, since the absence is what makes
the omission trick necessary. `map` (e.g. `"Alue 2026"`) is real and previously undocumented; Step 3
now notes that installations may add fields of their own.

- **`scripts/build_zip.sh`** (after the `ssb-pxwebapi-v2-skill` pattern) plus
  `.github/workflows/check-v1-zip.yaml`, which rebuilds the ZIP and `diff -r`s it against the
  committed one. The hand-built ZIP shipped `CLAUDE.md` and had no top-level directory; both are
  fixed, and the class of error is now caught by CI instead of documented around.
- **`evals/eval-scenarios.md`** — five end-to-end scenarios aimed at the passages this release
  shortened. Success criteria describe form and choices, never a numeric value.
- `README.md` file tree gained `CHANGELOG.md`, `evals/` and `scripts/`; `CLAUDE.md` gained a release
  checklist, the corrected section order, the sibling-check rule, and a note that the repo folder
  (`pxwebapi-v1-generic-skill`) does not match the frontmatter name (`generic-pxweb-v1-skill`).

## 0.11.0 — 2026-09-01

One new section. It closes a failure mode that is specific to v1 being POST-only: an assistant can
do the whole workflow correctly and only discover at the last step that its tooling cannot retrieve
data at all.

- **New section "Environment check — before Step 1"**, placed after the v1-vs-v2 pointer and before
  the Workflow. It asks one question up front — *can this environment send an HTTP POST with a JSON
  body?* — and names the three cases:
  - **Bash/shell with network access** to the target host → `curl -X POST` works, proceed normally.
  - **A GET-only web-fetch tool** (one restricted to URLs already seen in a search or fetch result)
    → **cannot** retrieve data. GET reaches metadata, the database/table hierarchy and `?config`,
    and stops there. This is not a limitation to work around; in v1 there is no GET data endpoint
    to fall back on.
  - **An MCP tool wrapping HTTP with POST support** → works if connected.

  The GET-only branch is the point of the section. Instead of abandoning the task, do the parts that
  genuinely don't need POST — identify the installation, walk the hierarchy, pin down the exact
  table and its variable codes from metadata (Steps 1–2) — then route to **Fallback** for the
  figures: hand over the table's URL in the agency's web front end and its "API query for this
  table" button, which emits a ready-made POST body the user or a POST-capable tool can run.

  The closing instruction is the data-integrity rule applied to a *tooling* constraint rather than
  an API failure: state plainly that the figures could not be retrieved in this environment, and
  substitute nothing — not memory, not a third-party aggregator. Without it the GET-only case is
  exactly the situation that tempts an assistant into a plausible number.

Deliberately **not** done:

- **Not propagated to the v2 siblings.** In v2 data retrieval is a GET, so a GET-only fetch tool can
  read the data cube there. The failure mode this section prevents does not exist in
  `generic-pxweb-v2-skill`, `ssb-pxwebapi-v2` or `scb-pxwebapi-v2`.
- **No environment detection logic.** The section describes the classes of tooling and lets the
  assistant recognise its own; probing for POST capability against a live agency host would spend a
  request to learn something already known locally.

## 0.10.0 — 2026-08-31

A broad installation inventory, and two corrections that came out of probing it. Every claim
below was verified against live installations on 2026-08-31.

- **New `references/installations.md`** — 49 known v1 installations with status, languages and
  limits, grouped by country. Sourced from the two catalogues shipped with the R package `pxweb`
  (rOpenGov), merged: URLs and coverage from the development version on GitHub (46 entries,
  modern URLs), the three entries that exist only in CRAN 0.17.0 (`data.ssb.no`, `px.rsv.is`,
  `pxwebapi2.stat.fi`), and **every limit read from live `?config`**.

  43 of the 49 responded. The six that did not are listed with their exact failure.

  This does **not** replace the seven-row table in `SKILL.md`. That table stays the operational
  list — base URL through DATABASEID, hierarchy walked, `?query=` support probed. The new file
  is verified only to the LANGUAGE level. `CLAUDE.md` now records the two levels and the rule
  that an entry cannot be promoted without probing `?query=` and finding its DATABASEID.

- **The bare error text is localised — a correction to how the existing rule reads.** The skill
  already said several installations return a bare `Bad Request` with no diagnostic. Probing
  found Spain's judicial statistics answering **`Solicitud incorrecta`**. Anything that tests for
  the literal string `Bad Request` misclassifies that response, and a failed call can then read
  as an empty result. `SKILL.md`'s integrity bullet and `references/troubleshooting.md` now state
  the structural rule instead: **any 4xx without a JSON body is a failed request.** The 400-body
  table grew from four installations to six.

- **`?config` answered on 43 of 43 reachable installations.** It is universal in v1, not a
  feature some installations happen to offer — `SKILL.md` Step 1 now says so with the number
  behind it. Two findings came with it:
  - **`maxCells` is absent from five payloads** (`etab.llv.li`, Sundsvall, `openstat.psa.gov.ph`,
    `pc-axis.geostat.ge`, Västerås). The field table implied it was always present. Absence is
    not "no cell limit" — the 403 still applies; the ceiling has to be found by bisection.
  - **Third-party limits are unreliable.** Of the 26 installations described by both the R
    catalogue and `?config`, **10 disagree on the call limit and 10 on the value limit**, some by
    orders of magnitude (`askdata.rks-gov.net`: catalogue 10 calls/10 s, `?config` 100 000). The
    pattern is that catalogues record what agencies *publish* while `?config` reports what the
    installation *enforces* — SSB is the clean case, documented at 30 calls/60 s and enforcing
    300. `CLAUDE.md` now forbids writing a limit into this skill from any other source.

- **Two catalogue URLs are wrong**, recorded in the new file and corrected in its tables:
  `pc-axis.geostat.ge` answers 404 over `http` and JSON over `https`; `data.ssb.no` redirects
  `http` → `https`. Geostat is the instructive one — a probe that followed the catalogue
  faithfully would have reported a live installation dead.

Deliberately **not** done:

- **No propagation to the sibling skills.** The integrity rule is mirrored in
  `generic-pxweb-v2-skill`, `ssb-pxwebapi-v2` and `scb-pxwebapi-v2`, but the API-failure bullet
  is already marked as deliberately v1-specific. The localisation finding concerns v1 error
  payloads only.
- **`?query=` support was not probed** for the 42 new installations. Without it they cannot be
  promoted to the `SKILL.md` table, and the new file says so.
- **No limits from the R catalogue** anywhere in the skill, including for the six installations
  that did not respond — they have no limit column at all rather than an unverified one.

## 0.9.0 — 2026-08-30

Versioning introduced, plus the data-integrity rule the v2 sibling skills carry.

- **Versioning introduced** (`metadata.version` in `SKILL.md` frontmatter + this log). A user holding an old copy previously had no way to tell
- **New section "Data integrity — the base rule"**, placed after the POST-only opening and before the installation table: **never state a number you have not fetched from the API in this conversation.** Six bullets — no numbers from memory, no other sources in the same answer, say so when the API fails, no interpolation, mark your own calculations, show `status` values as they are. The rule previously existed only in `ssb-pxwebapi-v2`; it has nothing to do with Norway, and the argument is *stronger* in a vendor-neutral skill that can point at any agency

  Two bullets are deliberately v1-specific:
  - The `status` bullet notes that the symbols are defined **per PX file** (`DATASYMBOL1`–`6`), so they vary between agencies and even between tables — don't assume `.` and `..`
  - The API-failure bullet notes that this matters more in v1 than in v2, because several installations (SCB, Finland, Greenland) return a bare `Bad Request` with no diagnostic, which makes a failed call easy to mistake for an empty result

  There is **no** `discontinued` bullet — v1 has no such flag; hierarchy nodes carry only `updated`.

  `CLAUDE.md` records that the section outranks the rest of the skill, and that it is mirrored in `generic-pxweb-v2-skill`, `ssb-pxwebapi-v2` and `scb-pxwebapi-v2` — a change to the rule belongs in all four.
- Sibling skills: `generic-pxweb-v2-skill` 0.10.0 released at the same time. It now carries the response-side material developed here (json-stat2 `extension` semantics, `extension.px`, status codes, the classification model behind `agg_`/`vs_`), and routes v1-only agencies here. The **request** side deliberately does not transfer in either direction

  One correction worth knowing if you work across both: v2 returns **400** when a non-eliminable variable is omitted, where v1 returns **all of that variable's values** instead. And the cell-limit response is **400** in v2, not v1's **403**. These are the two mistakes people carry between the APIs.
- **Clarified that `PxWebApiData` is not a v1-only client.** Since 1.9.0 the R package covers both API versions — v1 through `ApiData()`, v2 through a separate snake_case interface (`api_data()`, `query_url()`, `meta_data()`, …), with a vignette for each. A user arriving with a `PxWebApiData` script is therefore no evidence that the installation is on v1; check the base URL instead
