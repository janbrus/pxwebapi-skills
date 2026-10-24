# Changelog — generic-pxweb-v1-skill

What is different for users of the skill, newest first. The current version is in `SKILL.md` frontmatter under
`metadata.version`; if your copy has none, it predates 2026-08-30 — get a newer one. Versions below 1.0.0 mark a beta
skill: fewer verified examples and evals than the SSB skill, not an unstable one.

What was verified, on which installations and when, is in the maintainer's log,
[`DEVLOG.md`](https://github.com/janbrus/pxwebapi-skills/blob/main/pxwebapi-v1-generic-skill/DEVLOG.md). It is in the
repository, not in the ZIP.

## 0.12.4 — 2026-10-23

- Corrected: two lists in `SKILL.md` announced fewer points than they have ("Three things" over four, "Two things"
  over three). The instructions themselves are unchanged.

## 0.12.3 — 2026-10-21

- New: Claude is told to load this skill before using MCP tools that query a PxWeb v1 API, such as the Pipeworx
  agency packs, so the rules for table choice, codes, numbers and citation apply whatever the tool. Not yet tested.

## 0.12.2 — 2026-10-14

- **New: in a v1 response, positions follow the table's order, not the order you asked for** — the opposite of v2.
  Always look the position up in `category.index`; a parser written for v2 puts figures under the wrong labels.
- **New: show mandatory notes.** v1 flags them per table and per value, and they arrive only with the data response.
- **Corrected:** a missing `role.geo` does not mean the whole country — SCB's v1 never sets it. Look for a geographic
  variable in `id` first.
- **Corrected:** percent-encode letters outside ASCII in a search; SSB's v1 rejects a raw `ø` with 400.
- New: `references/json-stat2.md` starts with reading rules, and describes `extension`, `extension.px`, notes and
  `link` as SSB's and SCB's v1 send them.
- New in the repository, not in the ZIP: a skill map in `docs/`.

## 0.12.1 — 2026-09-28

- **Corrected: a table or database that does not exist returns 400, not 404**, at all seven verified installations. A 400
  can therefore mean a wrong table id, not only a bad query body. 404 comes mostly from wrong segments above the language
  level.
- **Corrected: a `status` flag does not always mean the value is missing.** A cell with a data note keeps its number —
  verified at SSB, which marks provisional figures `*`. Show the number with its flag, and never drop `null`s before
  indexing.
- New in `references/json-stat2.md`: the shapes other publishers use (Eurostat sends `value` as a sparse object), iterate
  dimensions in `id` order, and a worked indexing example. `-` (nil) is added to the symbol table.
- New in the repository, not in the ZIP: `docs/llms-template.txt`, an `llms.txt` any v1 installation can fill in, and a
  filled-in example for Statistics Finland.

## 0.12.0 — 2026-09-03

- **Corrected: the default output format varies.** A body without `"response"` returns json-stat2 at SSB, Finland and
  Estonia, PX at SCB and Greenland, and PX-JSON — JSON with a different shape — at the Faroe Islands and Iceland. Earlier
  versions said PX everywhere. Always set `"response"`.
- **Corrected: `aggregallowed: false` is a hint, not a rule.** It blocks `agg:` at SSB (400) but not at SCB, and three
  installations do not send the flag at all. Send the `agg:` query and handle the answer.
- **Corrected:** the metadata field is `extension.codelists` (lowercase), and SSB's rate limit is read from `?config` like
  everywhere else instead of being stated as 30 calls per 60 s.
- New: Statistics Iceland's English endpoint returns Icelandic variable codes, and some tables send no `role` at all.
- New: compute cells and values from metadata before sending a query, and when `agg:` is unavailable, use the level built
  into hierarchical codes (such as two-digit counties).
- New installation in `references/installations.md`: Oslo kommune (Oslostatistikken).
- `SKILL.md` is about 16 % shorter. Nothing was removed; the material moved to `references/`.
- The ZIP has a top-level folder and the MIT `LICENSE`, and no longer contains `CLAUDE.md`. The README covers installing
  in ChatGPT and Codex.

## 0.11.0 — 2026-09-01

- **New: environment check before Step 1.** v1 data is POST-only. In an environment that can only send GET (a web-fetch
  tool, for instance), the skill finds the table and its codes, then hands over the table's web page and the agency's
  "API query" button instead of producing figures.

## 0.10.0 — 2026-08-31

- **New `references/installations.md`:** 49 known v1 installations, with status, languages and limits read from each
  installation's own `?config`.
- **Corrected: any 4xx without a JSON body is a failed request.** The error text is localised (Spain answers
  `Solicitud incorrecta`), so testing for the literal `Bad Request` misses failures.
- `?config` works on every reachable installation. `maxCells` is missing at five; that does not mean there is no cell
  limit.

## 0.9.0 — 2026-08-30

- **New: versioning** — `metadata.version` in `SKILL.md`, and this log.
- **New: the data-integrity rule.** Never state a number not fetched from the API in the conversation, take no figures
  from memory or other sources, and say so when the API fails.
- The R package `PxWebApiData` supports both v1 and v2, so a user's `PxWebApiData` script does not show which API the
  installation runs.
