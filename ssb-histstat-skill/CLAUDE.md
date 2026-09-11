# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is **not** an application codebase. It is a Claude Code **Skill** package that teaches Claude how to navigate SSBs digitized historical publications (1828–2010) under `https://www.ssb.no/a/histstat/`. There are no tests and no runtime — changes here are documentation/prompt edits that get loaded when the `ssb-histstat` skill triggers. The one build step is `scripts/build_zip.sh` (added 2026-09-09), which packages the distribution ZIP.

Unlike its sibling `ssb-pxwebapi-v2`, this skill does not call an API — it points users to static PDFs and HTML pages. The "contract" of the skill is therefore the set of URLs it documents; broken links degrade the skill silently.

## Layout

- `SKILL.md` — the skill entrypoint. Frontmatter (`name`, `description`) controls when the skill auto-triggers; the body is the operational guide. Keep the bilingual trigger surface (Norwegian primary + English secondary) including pre-1980 years, NOS/HS terminology, and historical publication names.
- `scripts/build_zip.sh` — builds `ssb-histstat-skill.zip` from the user-facing files only (`SKILL.md`, `README.md`, `CHANGELOG.md`, `references/`), under the top-level folder `ssb-histstat/` — the frontmatter `name`, **not** the repo folder name `ssb-histstat-skill`. Never pack the folder by hand: `CLAUDE.md` and `scripts/` would end up in the package. `.github/workflows/check-histstat-zip.yaml` (in the **repo root**, not here) rebuilds it on every push touching this skill and `diff -r`s it against the committed one, so a stale zip fails the build.
- `references/structure.md` — the catalog of `/a/histstat/` (emnesider, series, periodika, filename conventions). `SKILL.md` is the workflow; `references/structure.md` is the lookup table. Avoid duplicating catalog data into SKILL.md. **It is an annotation of SSB's live hub `/a/histstat/publikasjoner/`** (the authoritative, `curl`-able index that already encodes the Etter-emne / Etter-serie tree) — the hub is the source of truth; structure.md records which paths are actually fetchable and keeps labels aligned to that page.

## Editing guidance

- **The data-integrity bullet under "Hva denne skillen IKKE gjør" is load-bearing** — this skill returns source URLs and never reads the PDFs, so a number in an answer can only have come from memory. That is the one failure mode that would put a fabricated figure under an SSB citation. It is the short form of the "Dataintegritet — grunnregelen" section in `ssb-pxwebapi-v2`; keep it, and keep it a pointer rather than growing it into a full list — the sibling skill owns the rule.
- **Versioning:** `metadata.version` in `SKILL.md` frontmatter plus a `CHANGELOG.md` entry on every content change (semver; stay below 1.0.0 while the skill has no published distribution). URL fixes count as content changes — a stale URL is the main way this skill degrades. Then rebuild the zip with `scripts/build_zip.sh`, or CI fails.
- **Every URL in SKILL.md and references/structure.md is a contract.** When adding or editing an example, hit the live URL and confirm HTTP 200. A common failure is for an SSB internal URL to redirect to a content-migrated location that returns 404 (especially under `/historisk-statistikk/`). Verify with `curl -o /dev/null -w "%{http_code}" -L <url>`.
- **Beware filename-pattern assumptions.** The `st_<nr>r_<år>.pdf` series ("Statistiske tabeller", 1828–1860, pre-NOS) is documented as a separate convention from NOS, but the files actually live in `/a/histstat/nos/` alongside NOS PDFs. When citing a `st_…` file, use the `/nos/` path.
- **Content correctness matters as much as URL liveness.** A filename containing a year does not guarantee the publication is about that year's main census — verify by reading the title from the NOS index listing (`schema.org/Book` `itemprop="name"`). Example incident: `st_04r_1801-35.pdf` is "Tabeller over Egteviede, Fødte og Døde i Norge for Aarene 1801 til 1835", not the 1801 census. The actual 1801 census is `nos_i_c1_1801-25.pdf`.
- **Emnesider live under the hub, not at the archive root.** The content-bearing topic pages are `/a/histstat/publikasjoner/histemne-NN.html` and `/a/histstat/publikasjoner/ereg77-96.html` (real HTML, hundreds of PDF links, `curl | grep`-able). The root-level `/a/histstat/histemne-NN.html` and `/a/histstat/ereg77-96.html` are empty ~22 KB shells (0 PDF links), and **WebFetch does not rescue them** — it doesn't execute the client-side JS the stubs rely on and returns "no content visible." Earlier guidance ("WebFetch the emneside" / "WebFetch handles migration better than curl") was wrong; always use the `/publikasjoner/` path, and supplement with `fortegnelse.pdf` or the series indexes (all rich and grep-able).
- **Folketellinger landing is a frameset, not content.** `/a/folketellinger/` returns only a ~1.3 KB `<frameset>` (both curl and WebFetch get nothing usable). The real per-census index is `/a/folketellinger/main.html` (lists `fob1769.html … fob1990.html`). The `fobYYYY` years are non-obvious — `fob1866.html` exists but `fob1865.html` is a 404 — so point at `main.html`, not a guessed year (the same "filename year ≠ content year" lesson as `st_04r_1801-35.pdf`).
- The base path `/a/histstat/` is the canonical archive root. Anything under `/historisk-statistikk/` should be treated as suspect — verify before referencing.

## Cross-skill awareness

- **`ssb-pxwebapi-v2`** — for any time series still published in Statistikkbanken. The bridge file `statbank-histu.html` lists tables in Statistikkbanken with start year before 1980; if a user's historical question maps to such a table, prefer the live API via the PxWebApi v2 skill over a PDF.
- **`ssb-pxwebapi-v2`** versus **this skill**: rule of thumb — if the answer is a current/recent number, use PxWebApi v2; if it requires looking at a digitized publication (NOS, HS, Statistisk årbok, folketellinger), use this skill.

## URL stability

PDFs, the NOS index, the `/a/histstat/publikasjoner/` hub, and all series/periodika indexes (`/a/histstat/<kode>/`) are stable and serve real content to plain `curl`. The empty bodies you may hit are specific and few: the **root-level** `/a/histstat/histemne-NN.html` / `ereg77-96.html` stubs and the `/a/folketellinger/` frameset — their fetchable equivalents are `/a/histstat/publikasjoner/histemne-NN.html` and `/a/folketellinger/main.html`. When editing, if a documented URL stops returning content, check both the HTTP status *and* the response body length — a 200 with ~22 KB and 0 `.pdf` links is the empty-shell signature — then update both SKILL.md and `references/structure.md`.
