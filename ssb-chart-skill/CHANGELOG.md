# Endringslogg — ssb-chart

Hva som er annerledes for deg som bruker skillen, nyeste først. Gjeldende versjon står i `SKILL.md`-frontmatter under `metadata.version`; har din kopi ingen `metadata.version`, er den fra før 2026-08-27 — last ned ny.

Hvorfor og hvordan endringene ble gjort, står i vedlikeholderens logg, [`DEVLOG.md`](https://github.com/janbrus/pxwebapi-skills/blob/main/ssb-chart-skill/DEVLOG.md). Den ligger i repoet, ikke i zip-en.

## 1.2 — 2026-10-02

- **Rettet: foreløpige tall ble tegnet som hull.** `readValue` returnerte `null` for alle celler med `status`. En celle med datanote beholder tallet (09842 har `*` = foreløpig tall), og tegnes nå med merke. Det er `null` i `value` som gir hull.
- **Nytt: oppskriften i `references/jsonstat-to-chart.md` er komplett.** `calculateFlatIndex` og `allCombinations` ble brukt, men var aldri definert. Nå er de skrevet ut.
- Nytt: x-aksen følger rekkefølgen i spørringen (`category.index`). Skriv eksplisitte tidslister stigende.

## 1.1 — 2026-08-30

- **Nytt: visualiser aldri et tall som ikke er hentet fra API-et i samme samtale.** Et diagram gir tall mer autoritet enn en tabell.
- Verdt å vite: aksefrekvensen (måned, kvartal, år) må bæres med fra søkesteget, siden `timeUnit` ikke står i json-stat2-responsen.
- Zip-en har MIT-`LICENSE`, og README beskriver installasjon i ChatGPT og Codex.

## 1.0 — 2026-08-27

- **Nytt: rendringsmål.** Skillen skiller mellom inline chat-widget og frittstående leveranse. I en widget styrer SSB bare seriefargene; akser, bakgrunn, tekst og mørk modus følger verten, og tittel og kildelinje står i chat-teksten.
- **Rettet: legend over eller til høyre, aldri under.** To referansefiler hadde `bottom`.
- Nytt: tema-objektene er delt i seriefarger og chrome, og hver seksjon i `references/format-guidelines.md` sier hvilket rendringsmål den gjelder. Mørk modus er med i sjekklisten.
- Zip-en har én toppmappe, `ssb-chart/`.
