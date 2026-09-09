# Eval scenarios — generic-pxweb-v2-skill

Four scenarios that hit exactly the paragraphs v0.11.0 shortened or corrected, because that is where the decisions live: the version check (Known installations), `role.geo` (Step 3), the default data format and `range()` (Step 4), and period-code letters (Step 4 / `codelists-and-filters.md`).

Run via the `skill-creator` skill after larger edits to `SKILL.md` or `references/`. Maintainer-internal — not in the distribution zip or the README file tree. Note that `.claude/settings.local.json` in this repo has `generic-pxweb-v2-skill: off` under `skillOverrides`; either enable it or run the scenarios in a fresh agent that is handed the skill files directly.

**Success criteria describe form and choices, never a concrete figure.** A scenario that asserts a particular population rewards a number recalled from memory over a fetched one — the opposite of the skill's own integrity rule.

**Run them as actual runs**, not read-throughs. A model that *reads* SKILL.md answers all of this correctly; the point is what it does when it has the tools.

Endpoints and response shapes verified live 2026-09-08. If a scenario fails, check first whether the installation changed before assuming the skill is the problem — Latvia's `apiVersion` is 2.0.0 and may be upgraded.

---

## 1. "Is `https://bank.stat.gl/api/v2` a PxWebApi v2 installation?" — parse the body, not the status

- **Expected outcome:** No. Route to `generic-pxweb-v1-skill` (Greenland is v1-only at `https://bank.stat.gl/api/v1/{da|en|kl}/Greenland`).
- **Sequence:** `GET https://bank.stat.gl/api/v2/config` → observe HTTP 200 with `Content-Type: text/html` and a body starting `CONFIG404;` → conclude "not v2".
- **Success:**
  - The model does **not** report "v2 exists" on the strength of the 200 status
  - It names the v1 base URL and the sibling skill rather than trying v2 calls anyway

## 2. "How many people live in Stockholm, using the generic skill?" — geography without `role.geo`

- **Installation:** SCB, `https://statistikdatabasen.scb.se/api/v2`
- **Expected table:** TAB6471 or TAB6473 (both monthly, 2025M01–, both current) — **not** TAB638 or TAB1625, which stopped at 2024 with `discontinued: null`
- **Key choices (TAB6471):** `Region=0180`, `Alder=TotSA` (mandatory in this table), `ContentsCode=000007SF`, `Tid=top(1)`, `outputFormat=json-stat2`. TAB6473 needs `Forandringar=100` and `Kon=TotSa` instead
- **Success:**
  - The model finds `Region` in `id` although `role` has no `geo` entry, and does not ask the user about geography
  - It checks `lastPeriod` and does not settle for a table whose last period is more than a year old just because `discontinued` is unset
  - It includes `Alder` after reading `elimination: false` — or recovers from `400 "Missing selection for mandantory variable"` by reading the metadata, not by guessing
  - The answer names the omitted dimensions and shows the mandatory notes; "Source: Statistics Sweden, table TAB6471" (or TAB6473)

## 3. "Latest monthly population figure for Latvia" — a non-Nordic installation

The scenario CLAUDE.md requires: proof that `Region`/`ContentsCode`/`Tid` are not universal.

- **Installation:** CSP, `https://api.stat.gov.lv/api/v2`
- **Expected table:** IRS010m (`Population and key vital statistics 1995M01–`), found via `GET /tables?query=population&lang=en` or a variant
- **Key choices:** `ContentsCode=IRS010m` (the "Number, thousand" indicator — the model must read `category.unit`), `TIME=top(1)`, **`outputFormat=json-stat2` set explicitly**
- **Success:**
  - The model sends `TIME`, not `Tid` — the name comes from `role.time`
  - It passes `outputFormat=json-stat2`. If it forgets, it recognises the `CHARSET="ANSI";` body as PX and retries rather than trying to parse it
  - It reads `maxDataCells: 10000` from `/config` and does not describe SSB's or SCB's limit as the limit here
  - For the closed interval it writes `[range(2025M11,2026M01)]` in a GET URL or `"range(2025M11,2026M01)"` in a POST body — or an explicit list. If a bare GET `range()` returns `Illegal selection expression`, it adds the brackets rather than concluding the function is missing
  - Unit is stated as "thousand", with 1 decimal, as `category.unit` says; the mandatory note (`noteMandatory: {"4": true}`) is shown
  - It reports the latest period from the data (`top(1)` → 2026M07), not from the catalogue's `lastPeriod` (2026M04), and says the two disagree

## 4. "Weekly salmon export from Norway, latest week" — period-code letters

- **Installation:** SSB, `https://data.ssb.no/api/pxwebapi/v2`
- **Expected table:** 03024 (`timeUnit: Weekly`)
- **Key choices:** `Tid=top(1)`; if the user then asks for a specific week, the code is `2026U35`-style
- **Success:**
  - The model reads the week format from `category.index` (`U`) and does not write `2026W35` from habit — a `W` returns `Non-existent value` at SSB
  - If asked to generalise, it says the letter differs per installation (SSB `U`, SCB `V`, Latvia `W`) rather than presenting one as the standard
  - Kilo price and tonnes are shown with the week number as published; "Source: Statistics Norway, table 03024"

---

## Runs

**2026-09-08, against v0.11.0.** All four run as actual runs by fresh agents that had only `SKILL.md` + `references/` and `curl`.

| # | Outcome | Notes |
|---|---|---|
| 1 | Passed | Read the body, not the status: 200 + `text/html` + `CONFIG404` → "not v2". Named the v1 base URL and the sibling skill. Went on to fetch Greenland's population from v1 without the v1 skill; that is beyond the scenario, not a failure of this one. Side finding for the **v1** skill: on Greenland's `BEXSAT1.PX` a `top` filter returned the *earliest* years — unverified here, candidate for that skill |
| 2 | Passed | Found `Region` in `id` with no `role.geo`; rejected TAB1625 (frozen 2024, `discontinued: null`) by `lastPeriod`; chose TAB6473, a valid alternative to TAB6471; truncated `popul*`/`folkmäng*` per the stemming rule; selected eliminable dimensions explicitly; showed all seven mandatory notes. **Surfaced a real error in the skill:** it saw `X-Rate-Limit-*` headers on SCB responses, which `api-details.md` said SCB does not send. Fixed in 0.11.0 |
| 3 | Passed | `TIME` not `Tid`; `outputFormat=json-stat2` on every call; read `maxDataCells 10000`; used an explicit list for the interval (the skill at that moment wrongly said `range()` did not exist — corrected 2026-09-09; the criterion above is the corrected one); unit "thousand", 1 decimal; mandatory note shown. **Surfaced a real finding:** the catalogue's `lastPeriod` (2026M04) lags the data (2026M07). Added to Step 2 and the comparison table |
| 4 | Passed | Read `U` from `category.index`, never sent `W`; no 400s; refused to sum an `aggregallowed: false` table; marked its own comparison |

**Harness note, not a skill finding:** the four agents shared one scratchpad directory and overwrote each other's response files. Agent 3 saw SCB tables (TAB6473, TAB1625) inside what it took to be a Latvia search response and, correctly, treated them as spurious after `/tables/{id}` returned 404. Give each parallel eval agent its own working directory.
