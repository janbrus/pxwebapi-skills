# Claude Skill: SSB Chart

En [Claude Skill](https://support.claude.com/en/articles/12512180-use-skills-in-claude) som lærer AI-verktøy som Claude å presentere norsk offentlig statistikk fra SSB i SSBs offisielle visuelle stil — som diagram, tabell eller dashboard.

Skillen styrer **hvordan** data vises, ikke hvordan de hentes. Bruk den sammen med [`ssb-pxwebapi-v2`](../ssb-pxwebapi-v2-skill/) som henter dataene; denne skillen tar JSON-Stat2-responsen og gjør den om til en korrekt, SSB-stilet visualisering.

## Hva skillen gjør

- Skiller mellom to **rendringsmål** som ikke deler stilregler: *inline chat-widget* (kun data-blekket er SSB-styrt — chrome, mørk modus og typografi følger vertens designsystem) og *frittstående leveranse* (nedlastbar HTML, PDF, Excel — full SSB-stil). Punktene under gjelder frittstående leveranse med mindre annet er nevnt
- Bruker SSBs **fargesystem** (kategorisk, sekvensiell og divergerende palett) med verdier i hex/RGB/CSS/JS/Python/openpyxl. Den kategoriske paletten gjelder alltid, uansett rendringsmål
- Setter riktig **typografi** (Roboto Condensed for titler, Open Sans for brødtekst, med Arial-fallback)
- Gir en **diagramvalg-matrise** — når man skal bruke linje, horisontal søyle, ring, kart, scorecard, scatter, histogram eller small multiples, og hva man skal unngå (3D, doble y-akser, kakediagram, avkortet y-akse)
- Beskriver **JSON-Stat2 → chart-config**-oppskriften: riktig tids-sortering via `category.index`, desimaler per metric fra `category.unit`, status-koder som visuelle hull (aldri interpolert)
- Dekker **stilregler per output-format**: React/HTML (Recharts, Chart.js), vanilla JS + Chart.js v4, PowerPoint, Excel, matplotlib og markdown-tabeller
- Bygger **deklarative titler** fra `extension.px.contents` og en flerspråklig **kildelinje** (`Kilde: SSB, tabell {id}. Sist oppdatert: {dato}.`)
- Håndhever **statistisk integritet**: y-akse fra 0 på søyler, jevne tidsintervaller, synlig enhet og periode, manglende data vist som hull — ikke skjult
- Følger **WCAG AA** (≥3:1 ikke-tekst, ≥4.5:1 tekst) og krever at diagrammet fungerer uten farge alene

## Filstruktur

```
ssb-chart-skill/
├── SKILL.md                       # Hovedinstruksjoner: prinsipper, rendringsmål, palett, typografi, diagramvalg, sjekkliste
├── README.md                      # Denne filen
├── CHANGELOG.md                   # Endringslogg — versjon står i SKILL.md-frontmatter
├── ssb-chart-skill.zip            # Ferdigpakket skill for opplasting til Claude.ai
└── references/
    ├── chart-selection.md         # Beslutningsmatrise per diagramtype (linje, søyle, ring, kart, scorecard …)
    ├── color-system.md            # Komplett fargespesifikasjon i alle formater (CSS/JS/Python/Recharts/Chart.js/matplotlib)
    ├── format-guidelines.md       # Stilregler per leveranseformat (React, vanilla JS, PPTX, Excel, matplotlib, markdown)
    └── jsonstat-to-chart.md       # Oppskrift: JSON-Stat2-respons → chart-datasets (labels, decimals, status-hull)
```

`CLAUDE.md` og `scripts/` i repoet er vedlikeholder-interne og følger ikke med i pakken.

## Installasjon

### For AI-plattformer som støtter skills

1. Last ned [ssb-chart-skill.zip](ssb-chart-skill.zip), eller bygg den fra repoet med `scripts/build_zip.sh` (ikke zip mappen selv — da følger `CLAUDE.md` og `scripts/` med). Pakken har toppmappe `ssb-chart/` og inneholder kun `SKILL.md`, `README.md`, `CHANGELOG.md` og `references/`
2. Gå til **Settings > Features > Skills** i Claude.ai
3. Last opp ZIP-filen

### Claude Code

Kopier mappen til din globale eller prosjektspesifikke skills-katalog. Fra repo-roten:

```bash
# Kopi, globalt (tilgjengelig i alle prosjekter)
cp -r ssb-chart-skill ~/.claude/skills/ssb-chart-skill

# Eller symlenke fra et klonet repo — da holder git pull kopien oppdatert
ln -s "$PWD/ssb-chart-skill" ~/.claude/skills/ssb-chart-skill

# Per prosjekt
cp -r ssb-chart-skill .claude/skills/ssb-chart-skill
```

## Bruk sammen med datakilde-skillen

Denne skillen inneholder **ingen datahenting** — den forutsetter at du allerede har en JSON-Stat2-respons fra SSBs PxWebApi v2. Last derfor opp begge skillene sammen for komplett arbeidsflyt:

- **`ssb-pxwebapi-v2`** — søker, utforsker og henter SSB-data. Eier dataformat-spesifikasjonen (`references/json-stat2.md`) som denne skillen peker til i stedet for å gjenta.
- **`ssb-chart-skill`** (denne) — styrer presentasjonen av de hentede dataene.

For svenske data finnes en parallell `scb-pxwebapi-v2`-skill; for vilkårlige PxWebApi v2-installasjoner finnes `generic-pxweb-v2-skill`. Chart-skillen er bevisst SSB-spesifikk (SSBs palett og kildelinje) og er ikke ment for andre datakilder.

## Lisens

Skillen er et hjelpemiddel for visualisering av SSBs åpne data. Data fra SSB er lisensiert under [CC BY 4.0](https://www.ssb.no/diverse/lisens).

Fargesystemet er basert på SSBs offisielle designsystem og Plotly-template. Inspirert av Try sin ssb-dataviz-skill.
