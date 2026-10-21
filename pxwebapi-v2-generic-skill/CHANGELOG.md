# Changelog — generic-pxweb-v2-skill

What is different for users of the skill, newest first. The current version is in `SKILL.md` frontmatter under `metadata.version`; if your copy has none, it predates 2026-08-30 — get a newer one. Versions below 1.0.0 mark a skill with no published distribution yet.

What was verified, on which installations and when, is in the maintainer's log, [`DEVLOG.md`](https://github.com/janbrus/pxwebapi-skills/blob/main/pxwebapi-v2-generic-skill/DEVLOG.md). It is in the repository, not in the ZIP.

## 0.11.3 — 2026-10-21

- New: with an MCP server connected to a PxWebApi v2 installation, for example pxweb-mcp, Claude loads the skill before it uses the tools, so the rules for table choice, codes, numbers and citation apply there too. Measured against Statistics Latvia with the server named `pxweb-lv`; a question asked in Latvian still often went straight to the tools.
- The chart skill is referred to by its installed name, `ssb-chart`, not `ssb-chart-skill`.

## 0.11.2 — 2026-10-14

- **Corrected: mandatory notes can sit at three levels.** Besides the table's notes, SCB flags notes per variable (`Alder` in TAB6471) and per value (`categoryNoteMandatory`). The answer should show all of them.
- **Corrected: percent-encode non-ASCII letters in the URL.** A raw `ä` or `ī` returns 0 hits at SCB and Latvia, and a raw `ø` returns 400 at SSB.
- **Corrected:** `discontinued` is never set in metadata or data, and on a search hit it appears only when `true` (never at Latvia). The PX elimination forms are now written correctly, and `copyright` in `extension.px` is `false` at all three installations.
- New: `references/json-stat2.md` starts with seven reading rules, and says per installation what `link` and `extension.px` carry.
- New: if a table has a standard error or margin of error as a measure, fetch it before calling a difference real. An obviously right search hit is chosen directly, with the reason given.
- New in the repository, not in the zip: a skill map in `docs/`.

## 0.11.1 — 2026-10-02

- **Corrected: a `status` flag does not always mean the value is missing.** A cell with a data note keeps its number — SSB marks provisional figures `*`. Show the number with its flag, and never drop `null`s before indexing.
- **Corrected:** the structure example in `references/json-stat2.md` had a number in a cell whose status said it was missing.
- New in `references/json-stat2.md`: `-` (nil) in the symbol table, the shapes other publishers use (Eurostat sends `value` as a sparse object), iterate dimensions in `id` order, positions follow the order of the request, and a worked indexing example with two dimensions.
- New in `references/api-details.md`: parquet is beta and names its columns by the variable's label, and a section linking PxTools' user guide, the API specification and the PxWebApi source.

## 0.11.0 — 2026-09-08

- **New installation: Latvia (CSP),** `https://api.stat.gov.lv/api/v2`, and a table of verified differences between SSB, SCB and Latvia in `references/api-details.md`.
- **Corrected: json-stat2 is not the default everywhere.** Latvia returns PX when `outputFormat` is left out. Always pass `outputFormat=json-stat2`.
- **Corrected: an expression with a comma must be bracketed in a GET URL** (`[range(a,b)]`, `[top(3,2)]`); a POST body takes it bare. Expressions and explicit codes can share one `valueCodes`.
- **Corrected: differences between installations that were written as universal rules.** SCB sets no `role.geo`, so look for a geographic variable before assuming the whole country. Weekly codes are `U` at SSB, `V` at SCB and `W` at Latvia. The default search operator is AND at SSB and SCB, OR at Latvia. SCB and Latvia send `X-Rate-Limit-*` headers.
- **Corrected:** search wildcards match the stemmed term (`popul*`, not `population*`); variable and value codes are not case-sensitive; `outputValues` has no effect at SSB or SCB; `discontinued` does not show that a series is alive — compare `lastPeriod` with today.
- New: curl needs `-g`; a repeated value code returns 500 with an empty body; a GET URL over about 2 100 characters returns 404; the catalogue's `lastPeriod` can lag the data; mandatory notes must be shown.
- `SKILL.md` is shorter; nothing was removed, the material moved to `references/`. The ZIP is now `generic-pxweb-v2-skill.zip`, with a top-level folder, the README, this log and the MIT `LICENSE`. The README covers installing in ChatGPT and Codex.

## 0.10.0 — 2026-08-30

- **New: `references/json-stat2.md` rewritten** — the two levels of `extension`, `extension.px` (`aggregallowed`, decimals), dimension metadata such as `basePeriod` and `measuringType`, notes and `noteMandatory`, what json-stat2 cannot express, and tools (pyjstat, rjstat, `PxWebApiData` and others).
- **Corrected: eliminability is read from the metadata response only.** In a data response `extension.elimination` describes the extract, not the table.
- **Corrected: a 400 is diagnosed by its `title`, not `detail`,** and the error shape is the same at every installation.
- New: the five agencies still on v1 are listed and routed to `generic-pxweb-v1-skill`, with a check for which API version an installation runs. Read the body, not the status code — Greenland answers 200 with an HTML error page.
- New: say which dimensions were collapsed and which codelist was used, since the response records neither.

## 0.9.0 — 2026-08-30

- **New: versioning** — `metadata.version` in `SKILL.md`, and this log.
- **New: the data-integrity rule.** Never state a number not fetched from the API in the conversation, take no figures from memory or other sources, and say so when the API fails.
- **Corrected: rate limits.** Check both `/config` and the response headers; `0` in `/config` means "not in use", not "unlimited".
- New: a `GET /data` without a selection returns the table's default selection, which can sum dimensions away without saying so. Prefer `top(N)`/`from(value)` for time.
