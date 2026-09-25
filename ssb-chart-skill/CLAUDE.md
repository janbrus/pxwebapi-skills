# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is **not** an application codebase. It is a Claude Code **Skill** package that teaches Claude how to present Statistics Norway (SSB) data in SSB's official visual style — charts, tables, dashboards. There is no build, no tests, no runtime; changes here are documentation/prompt edits that get loaded when the `ssb-chart` skill triggers.

The skill governs **presentation only**. It assumes a JSON-Stat2 response already exists (fetched via the `ssb-pxwebapi-v2` skill) and turns it into a correct, SSB-styled visualization. It deliberately does **not** restate the data format — it points to the data skill instead (see "Editing guidance").

### The render-target split is the skill's main axis

Since v1.0 the skill branches on **rendringsmål** (render target) before any styling rule applies, and this is the single most important thing to understand before editing:

- **A. Inline chat widget** — rendered inside a conversation by a host tool with its own design system. Only the *categorical series colours* are SSB-controlled (hardcoded hex, because canvas libraries can't read CSS variables). Axes, gridlines, background, general text, and dark mode all follow the **host's tokens**. Title and source line go in the surrounding chat text, never inside the widget. Tables come out as plain markdown.
- **B. Standalone deliverable** — a downloadable HTML file, PDF, Excel dashboard: anything that outlives the conversation as a file. Here the whole skill applies unabridged — full palette, SSB typography, title and source baked into the chart, SSB table style.

Most style tables in `SKILL.md` (typography, table formatting, sequential/diverging palettes, axis hex values) are **target B only**, and each carries a scope note saying so. When reading or editing any style rule, first establish which target it governs.

## Layout

- `CHANGELOG.md` — user-facing Norwegian change log, same format as the sibling `ssb-pxwebapi-v2` skill: newest version first as `## <version> — <YYYY-MM-DD>`, and a header noting that a copy without `metadata.version` predates 2026-08-27. It ships inside the ZIP, because a user who installed from a ZIP has no git history.
- `README.md` — Norwegian user-facing documentation for people installing the skill (what it does, file structure, install steps, licence). Its "Hva skillen gjør" list mirrors SKILL.md's rules — when a rule changes in SKILL.md (fonts, chart types, limits), check whether README.md's summary needs the same change.
- `SKILL.md` — the skill entrypoint. Frontmatter (`name: ssb-chart`, `description`) controls auto-triggering; `metadata.version` and `metadata.source` record the release and its upstream GitHub path. The body is the operational guide: the six core principles, the **"Rendringsmål" section** that splits widget from standalone rendering (read it before any style section), a quick-reference palette + typography table, the chart-selection cheat sheet, text/labelling rules (declarative titles, mandatory source line), table formatting, the data-storytelling arc, and the pre-delivery checklist.
- `references/` — deeper material loaded on demand:
  - `chart-selection.md` — per-chart-type decision matrix (line, horizontal bar, grouped/stacked bar, donut, choropleth, scorecard, scatter, histogram, small multiples): when to use, rules, SSB specifics, common mistakes.
  - `color-system.md` — the complete colour spec. Every palette colour in hex/RGB/CSS/JS/Python/openpyxl, plus ready-made theme objects for Recharts, Chart.js, and matplotlib. This is the canonical source for the hex values.
  - `format-guidelines.md` — style rules per delivery format: React/HTML, vanilla JS + Chart.js v4, PowerPoint, Excel, matplotlib, markdown tables. Includes the language-bound number-format rule and the source-footer snippets.
  - `jsonstat-to-chart.md` — the step-by-step recipe from a JSON-Stat2 response to chart datasets: axis selection, `category.index` ordering, series labels, status-codes-as-gaps, per-metric decimals.

## Editing guidance

- **Preserve the bilingual trigger surface** in `SKILL.md` frontmatter. The `description` carries Norwegian (primary) and English trigger phrases; removing them will cause the skill to stop firing. Keep the "Bruk IKKE denne skillen for andre datakilder" boundary — it stops the skill over-triggering on non-SSB visualizations.
- **Every style rule must declare its render target.** A rule that doesn't say whether it governs the inline widget, the standalone deliverable, or both is a bug — it will get applied in the wrong context. When adding or editing a styling rule, add the scope note in the same edit, matching the phrasing already used in `SKILL.md` ("Gjelder frittstående leveranse", "Gjelder begge rendringsmål"). Corollary: hardcoded hex is not uniformly right or wrong any more. Series colours are hardcoded hex in *both* targets; chrome colours (`#274247`, `#C3DCDC`, backgrounds) are hardcoded only for standalone and must come from host tokens in a widget.
- **This is a companion skill, not standalone.** It points to `ssb-pxwebapi-v2`'s `references/json-stat2.md` for the data format (row-major value array, `role.time`/`role.metric`/`role.geo`, `category.index`, `category.unit.decimals`, status codes, `extension.px.contents`). Do **not** duplicate those details here — keep the pointer. If the data skill's format docs move, update the cross-reference rather than inlining the content.
- **Palette hex values are canonical and must stay in sync.** The same colours appear in `SKILL.md`'s quick table, in `references/color-system.md`'s per-colour entries, in the language-specific arrays/theme objects (JS, Python, Recharts, Chart.js, matplotlib), **and hardcoded inside the code snippets in `references/format-guidelines.md`** (Chart.js options, PPTX/Excel specs). Change a value in one place → change it everywhere; `grep -rn '#<hex>'` across the repo is the reliable way to find every occurrence. `color-system.md` is the source of truth; it is based on SSB's official design system / Plotly template.
- **Don't "fix" the line-chart limit.** Line charts cap at **5 series** while the general categorical rule is 6–7. This is intentional (overlapping lines become unreadable faster than separate bars) and is explained in `chart-selection.md` and SKILL.md. Leave the asymmetry; don't normalise it.
- **Statistical-integrity rules are invariants — never soften them.** Bars (and absolute-value lines) start the y-axis at 0; indices may start elsewhere but must annotate the base year. Missing data (status codes `"."`, `".."`, `":"`) renders as visual gaps (`null` + `spanGaps: false`), never interpolated, dropped, or carried-forward. These are load-bearing; edits that weaken them defeat the skill's purpose.
- **Decimals come from the data, never hardcoded.** The recipe reads precision per ContentsCode from `category.unit[code].decimals` with `extension.px.decimals` as fallback. Keep the worked examples (`Personer1` → 0, `KpiIndMnd` → 1, valuta → 4) — they show why a hardcoded "2 decimals" is wrong.
- **Code snippets in `references/format-guidelines.md` must obey SKILL.md's rules.** The snippets are copied verbatim into deliverables, so a snippet that contradicts a SKILL.md rule (legend placement, beginAtZero, source line, fonts) silently overrides it in practice. When a presentation rule changes, re-check every snippet that encodes it.
- **`references/format-guidelines.md` carries per-section scope notes — keep them.** The file is organised by technology, which cuts across the render-target split, so it opens with a section→target mapping table and every `##` section states its scope in SKILL.md's own phrasing ("Gjelder begge rendringsmål", "Gjelder kun frittstående leveranse"). React/HTML and Chart.js apply to both targets and list their widget deltas explicitly (host tokens instead of `#274247`/`#C3DCDC`, `display: false` on title/subtitle, no Google Fonts import); PPTX/Excel/matplotlib are standalone-only; markdown tables are the required table form in a widget. A new section without a scope note is incomplete.
- **`references/color-system.md` is organised around data-ink vs. chrome — preserve that split.** The colour values themselves are target-agnostic; what decides the render target is *what you apply them to*. Data ink (lines, bars, points, choropleth fills, heatmap cells) is SSB-controlled in both targets; chrome (axes, gridlines, background, text, tooltip, fonts) is SSB-controlled only for standalone and comes from host tokens in a widget. The Recharts theme is therefore split into `SSB_SERIES` + `SSB_CHROME`, and the Chart.js section carries a widget variant beside the standalone defaults. Don't re-merge a theme into one object for convenience — the merge is exactly what makes it unsafe to reuse in a widget.
- (`chart-selection.md` and `jsonstat-to-chart.md` are genuinely target-independent — chart choice and data transformation don't change with the render target — so they need no scope notes. Don't add them.)
- **Legend position is `top` or `right`, never `bottom`.** It's stated in `SKILL.md`, and both `color-system.md` (per-chart-type notes and widget variant) and `format-guidelines.md` (Chart.js snippet) must agree. This one has drifted twice: a `bottom` default in a snippet silently overrides the prose rule, because snippets get copied verbatim.
- **Keep SKILL.md the overview.** Defer detail to `references/` rather than duplicating; SKILL.md should stay a navigable summary with pointers.
- **The source line is mandatory and bilingual.** Every visualization shows `Kilde: SSB, tabell {id}. Sist oppdatert: {dato}.` (or the English form), language chosen from the API's `lang` parameter. When combining tables, list every table ID. Keep this consistent across `SKILL.md` and all format snippets in `format-guidelines.md`.

## Deployment note

This skill has two homes plus a distribution artifact, and all three drift independently:

1. **Deployed copy** — `~/.claude/skills/ssb-chart-skill/` (what Claude Code actually loads). On the maintainer's machine this is a symlink into the repo, so editing the source *is* deploying; elsewhere it is a copy that has to be refreshed.
2. **Version-controlled source** — `ssb-chart-skill/` inside the `pxwebapi-skills` GitHub repo (https://github.com/janbrus/pxwebapi-skills — renamed from `ssb-api-v2-examples`; old URLs redirect). On the maintainer's machine that is `/home/jan/GitHub/pxwebapi-skills/`.
3. **`ssb-chart-skill.zip`** — lives beside the source and is what gets uploaded to Claude.ai. **Build it with `scripts/build_zip.sh`, never by hand** (added 2026-09-09; before that it was hand-built and drifted). The script wraps everything in a single top-level folder named after the skill's frontmatter `name` — `ssb-chart/`, **not** the directory name `ssb-chart-skill` — matching how the sibling `ssb-pxwebapi-v2` skill packs, and globs `references/*.md` so a new reference file cannot silently fall outside the package. It contains user-facing files only: `SKILL.md`, `README.md`, `CHANGELOG.md`, `references/`, plus `LICENSE` from the repo root. Never add `CLAUDE.md`, `scripts/` or anything else maintainer-facing. `LICENSE` (MIT) lives in the **repo root** and covers the whole repo; `build_zip.sh` copies it into the package because MIT requires the notice to travel with every copy, and the zip is the copy that gets handed out. Don't add a per-skill `LICENSE` — edit the root one, and rebuild **all six** zips when it changes (every zip-sync workflow has `LICENSE` in its `paths:` filter). `SKILL.md` frontmatter carries `license: MIT. LICENSE has complete terms` (the optional Agent Skills field — keep it short, it names the file beside `SKILL.md` in the zip); never put licence text in the body, which is loaded on every trigger.

`.github/workflows/check-chart-zip.yaml` (in the **repo root**, not here) rebuilds the zip on every push touching this skill and `diff -r`s it against the committed one, so a stale zip fails the build. `scripts/build_zip.sh /tmp/fresh.zip` writes elsewhere if you want to diff manually.

**Every behaviour change needs a `CHANGELOG.md` entry** — same rule the sibling skill's CLAUDE.md enforces. Record what changed and why it matters to someone holding an older copy, and note whether a sibling skill was affected (for this skill that is normally "none — no SCB/generic chart equivalent exists"). Pure wording fixes don't need an entry; a changed rule always does. Bump `metadata.version` in the same edit.

After editing, mirror to the other home, then **rebuild the ZIP from scratch** rather than updating entries in place — the wrapper folder makes `zip ssb-chart-skill.zip SKILL.md` actively harmful, because it adds a second root-level `SKILL.md` beside `ssb-chart/SKILL.md` and the package silently becomes wrong. Rebuild in a temp dir:

```bash
rm -rf /tmp/pack && mkdir -p /tmp/pack/ssb-chart/references
cp SKILL.md README.md CHANGELOG.md /tmp/pack/ssb-chart/
cp references/*.md /tmp/pack/ssb-chart/references/
(cd /tmp/pack && zip -r ssb-chart-skill.zip ssb-chart)
```

Verify with `diff -r` between the two homes, and check every ZIP entry against its working file (`unzip -p <zip> ssb-chart/<path> | diff - <path>`) rather than trusting `unzip -l` sizes. A stale or duplicated ZIP entry is invisible until someone reinstalls from it, and it has actually happened here. Bump `metadata.version` in `SKILL.md` frontmatter when the change alters behaviour rather than wording.

## Related sibling skills

- **`ssb-pxwebapi-v2`** — the upstream data-fetching skill. This chart skill is its presentation companion; they are designed to be loaded together. Owns the JSON-Stat2 format docs.
- **`scb-pxwebapi-v2`** (Sweden) and **`generic-pxweb-v2-skill`** (any PxWebApi v2 installation) — parallel data skills. There is no SCB/generic equivalent of this chart skill; the SSB palette and "Kilde: SSB"/"Statistics Norway" source line are SSB-specific by design. If a Swedish styling skill is ever added, the structure here is the template, but the colours and source attribution must change.
