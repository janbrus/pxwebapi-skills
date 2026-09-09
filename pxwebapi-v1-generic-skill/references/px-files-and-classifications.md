# PX files, valuesets and aggregations

Why `agg:` and `vs:` are invisible to the API, where their names come from, and which PX-file
keywords surface as API metadata. Background for `query-syntax.md`.

---

## Two kinds of PxWeb installation

PxWeb can read its tables from either a relational database or a directory of flat **PX files**.
This is not a detail — it changes what the API's URLs look like and how discoverable
classifications are.

| | **File-based** (most installations) | **Relational** (SSB, SCB) |
|---|---|---|
| A table is | one `.px` file on disk | a row set in a database |
| Table id in the URL | **includes the extension** — `11ra.px`, `BEXSTA.px`, `RL101.PX` | no extension — `07459`, `BefolkManadCKM` |
| Valuesets / aggregations | `.vs` and `.agg` files in a classification directory | database-managed |
| Discoverable via the API | no | no in v1, **yes in v2** |

The official PxWeb 1.0 specification was written against a relational installation, which is why
its examples omit the extension. Statistics Finland's own API page warns explicitly: "For
Statistics Finland databases always remember to use the extension `.px` after the table name."
Verified live — Finland, the Faroe Islands, Greenland and Estonia all require it; SSB and SCB
reject it.

**A consequence worth stating plainly:** the trick in `v1-vs-v2.md` for recovering aggregation
names from a v2 API only works at SSB and SCB — the two relational installations, which are also
the two least likely to be stuck on v1. On a file-based v1-only installation there is no API route
to the classifications at all. Your options there are the web front end's "API query for this
table" button, or asking the agency.

---

## The classification directory

Since PC-Axis version 99, classifications live in their own files beside the PX files:

| Extension | Contents |
|---|---|
| `.VS` | A **valueset** — a named list of value codes (and optionally texts) |
| `.AGG` | An **aggregation list** — groups of those values |
| `.VSC` | Continuation of a valueset's codes past 1000 values |
| `.VSN` | Continuation of a valueset's texts past 1000 values |

**The name you put in a filter is the filename without its extension.** A file
`25-years classes.agg` is used as `{"filter": "agg:25-years classes", …}`, and `Age5.vs` as
`{"filter": "vs:Age5", …}`. Two practical consequences:

- **Names can contain spaces and punctuation**, because filenames can. Do not assume an
  aggregation name is a single identifier-shaped token.
- **Names are not namespaced by table.** Several tables can share one aggregation, and one
  variable can have several — which is why guessing a name from another table's query so often
  produces `400`.

### Valueset structure (`.vs`)

Mandatory sections `[Descr]`, `[Domain]`, `[Valuecode]`; optional `[Valuetext]`, `[Aggreg]`,
plus `[Level]` or `[Region]` depending on type.

```ini
[Descr]
Name=Age5
Prestext=Ages 0-9 - 60+
Type=V
[Aggreg]
1=25-years classes.agg     ; ← the aggregations available for this valueset
[Domain]
1=age                      ; ← the PX variable(s) this valueset applies to
[Valuecode]
1=0-4
2=5-9
…
[Valuetext]
1=0-4 years
…
```

Three valueset types:

| `Type` | Use | Extra section |
|---|---|---|
| `V` | Ordinary variables (age, industry) | — |
| `H` | Hierarchical variables | `[Level]` — how many characters make up each level |
| `N` | *Nyko* / subarea geography, coded county-municipality-subarea | `[Region]` — which municipalities are present |

For type `H`, `[Level] 1=2, 2=4, 3=5, 4=6` means the first 2 characters are level 1, the first 4
are level 2, and so on — so code `01.111` decomposes as `01` → `01.1` → `01.11` → `01.111`. That
is why hierarchical code prefixes are meaningful and why wildcard filters like `01*` line up with
classification levels.

Valuesets longer than 1000 values end with `1000=****` in `[Valuecode]`; the remainder lives in a
`.VSC` file (codes) and a `.VSN` file (texts), one value per line.

### Aggregation structure (`.agg`)

```ini
[Aggreg]
Name=25-years classes
Valueset=Age5              ; ← an aggregation always belongs to ONE valueset
1=0-24
2=25-49
3=50-74
4=75+
Map=…                      ; optional, for geographical variables
[Aggtext]
1=0-24
…
[0-24]                     ; one section per group, listing its members
1=0-4
2=5-9
3=10-14
4=15-19
5=20-24
```

**An aggregation is defined on a valueset, not directly on a variable.** So `agg:X` is only valid
where the variable is currently expressed through the valueset that `X` belongs to. Mixing an
aggregation from one valueset with codes from another is the commonest cause of
`400 … has an error` on an otherwise well-formed query.

---

## PX keywords that surface in the API

The v1 metadata response is a thin projection of the PX file's header. Knowing the source keyword
explains behaviour the API documents only obliquely.

| PX keyword | Effect in the API |
|---|---|
| `ELIMINATION("var")="value"` | `elimination: true` **with** an elimination value — omitting the variable returns that named total (**rule 1**) |
| `ELIMINATION("var")=YES` | `elimination: true` **without** one — omitting the variable sums every value (**rule 2**) |
| *keyword absent* | `elimination` absent → `false`; omitting the variable returns all values (**rule 3**) |
| `TIMEVAL` … `TLIST(A1\|H1\|Q1\|M1\|W1)` | Marks the time variable → `time: true`. **The scale is discarded** — the API exposes no frequency, and json-stat2 has no field for one |
| `DOMAIN("var")` | Links the variable to a valueset, enabling `vs:` and `agg:` for it |
| `AGGREGALLOWED=NO` | Declares aggregation **not meaningful** for the table — set where summing produces nonsense (indices, averages). Absent from the metadata endpoint, but **exposed in the data response** as `extension.px.aggregallowed`. How strictly it is enforced differs between v1 and v2 — see below |
| `CONTVARIABLE` | The metric variable — the `ContentsCode`-equivalent. Tables without it have **no metric dimension at all** and no `role.metric` |
| `UNITS`, `DECIMALS` | `category.unit.base` and `.decimals` in the json-stat2 data response |
| `CODES`, `VALUES` | `values` and `valueTexts` in the metadata response |
| `DATASYMBOL1`…`6` | The `status` symbols. Defaults are `.` (DATASYMBOL1) and `..` (DATASYMBOL2), but each file may override them — which is why status symbols vary between agencies |

The three elimination rules are not an API convention layered on top of the data; they are a direct
reading of which `ELIMINATION` form the PX file uses. That also explains why the total is sometimes
a selectable code and sometimes not: the first form names an existing value, the second computes
one that never existed as a code.

### Reading PX keywords back out: `extension.px`

The json-stat2 **data** response carries a slice of the PX header verbatim, in both v1 and v2:

```json
"extension": {
  "px": { "tableid": "14710", "matrix": "KpiIndMnd", "decimals": 1,
          "aggregallowed": false, "official-statistics": true, "copyright": false,
          "language": "no", "contents": "14710: Konsumprisindeks (2025=100),",
          "heading": ["ContentsCode", "Tid"], "stub": [],
          "subject-code": "pp", "subject-area": "Priser og prisindekser" } }
```

Verified identical from `POST https://data.ssb.no/api/v0/no/table/14710` (v1) and the v2 equivalent.
This is the only route to several PX keywords the metadata endpoint drops — most usefully
`aggregallowed`, and also `decimals`, plus `heading`/`stub` (the table's default pivot layout).

So `AGGREGALLOWED=NO` **is** detectable, just not where you would look for it: run any small query
and read `extension.px.aggregallowed`.

**But do not read `false` as "aggregation will fail".** All seven verified installations were probed
2026-09-03/04, and the flag turns out to be neither universal nor uniformly enforced:

| Installation | Flag in the response | `false` seen? | Does `false` block `agg:`? |
|---|---|---|---|
| Statistics Norway (SSB) | yes | yes | **Yes — 400** |
| Statistics Sweden (SCB) | yes | yes | **No — 200 with data** |
| Statistics Finland | yes | no, `true` everywhere sampled | untestable |
| Statistics Greenland | yes | no, `true` everywhere sampled | untestable |
| Statistics Iceland | **absent** | — | n/a |
| Statistics Faroe Islands | **absent** | — | n/a |
| Statistics Estonia | **absent** | — | n/a |

Three consequences, each of which was a wrong assumption in an earlier revision of this file:

- **The signal is missing at three of seven installations.** Iceland, the Faroes and Estonia return
  an `extension.px` with one or two keys and no `aggregallowed` at all. "Run a probe and read the
  flag" yields nothing there, so absence must not be read as `true`.
- **Where it is present and `false`, enforcement differs between installations.** At SSB, 14700 and
  11342 reject their own aggregations with `400` while `vs:` on the same table and variable answers
  `200` — `vs:CoiCop2018Kpi01` and `vs:Kommune` respectively — which rules out the reading that v1
  merely does not know those classifications. At SCB the identical experiment gives the opposite
  result: `AKURLBefM` (v2 `TAB6387`) reports `aggregallowed: false` and still returns 200 with data
  for `agg:ISD2`, with the aggregate categories correctly applied. Two relational installations,
  the same API version, opposite behaviour.
- **The flag's *value* is an editorial choice, not a property of the data.** SSB marks its consumer
  price index tables `false`; Finland marks its CPI tables (`rki/11na.px` and neighbours) `true`,
  and Greenland does the same for its price indices. So "index tables are `false`" describes SSB's
  cataloguing habit, not PxWeb.

It is also **version-specific at SSB**: the same aggregation on the same table succeeds in **v2**
(`codelist[VareTjenesteGrp]=agg_CoiCop2018Kpi011` on 14700 → 200 with data). That is what
`generic-pxweb-v2-skill` says, and it is correct there. Do not reconcile the skills; they describe
different APIs, and now also different installations.

**Practical rule.** Read `aggregallowed` as a hint about whether summing the table is *meaningful*,
never as a prediction about whether the request will *succeed*. Send the `agg:` query and handle
the response you get.

**`extension.px` does not carry the time scale.** `TLIST` is absent from the payload in both
versions, even though neighbouring PX keywords come through — see `json-stat2.md`.
