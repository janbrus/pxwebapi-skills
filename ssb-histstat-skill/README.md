# Claude Skill: SSB Historisk statistikk

En [Claude Skill](https://support.claude.com/en/articles/12512180-use-skills-in-claude) som lærer AI-verktøy som Claude å navigere SSBs digitaliserte historiske publikasjoner (1828–2010) under `https://www.ssb.no/a/histstat/`.

## Hva skillen gjør

- **Starter på huben `/a/histstat/publikasjoner/`** — SSBs autoritative, `curl`-bare publikasjonskatalog (organisert *Etter emne* og *Etter serie*) som styrer arbeidsflyten
- Guider AI-assistenten til riktig publikasjon for spørsmål om historiske norske tall — typisk fra **før ca. 1980** der `ssb-pxwebapi-v2` har begrenset dekning
- Anbefaler *Historisk statistikk*-utgavene (hs1978, hs1968, hs1994) som førstevalg for brede tidsserier
- Bruker `statbank-histu.html` som bro: identifiserer historiske tidsserier som ennå publiseres i Statistikkbanken og delegerer til `ssb-pxwebapi-v2` for live tall
- Kjenner publikasjonsstrukturen: NOS-serien (1828–2010), 25 emnesider, 12 serier (inkl. SØS-forskningsmonografier), 9 periodika, filnavn-konvensjoner og katalogplassering
- Returnerer URL til PDF/HTML pluss kontekst (serie, år, tema) — parser ikke PDF-innhold

## Når den utløses

Triggers på norske begreper som "historisk statistikk", "NOS", "Norges offisielle statistikk", "folketelling 1769/1801/1865/…", "Statistisk årbok", "tall fra 1800-tallet", samt årstall før 1980 kombinert med statistikkbegreper (befolkning, lønn, priser, handel, jordbruk, fiske, industri, skole, fattigvesen). Også engelsk: "Norwegian historical statistics", "Statistics Norway historical", "Norway 19th century data".

## Filstruktur

```
ssb-histstat-skill/
├── SKILL.md                              # Hovedinstruksjoner: arbeidsflyt + decision tree
├── README.md                             # Denne filen
├── CHANGELOG.md                          # Endringslogg — versjon står i SKILL.md-frontmatter
├── ssb-histstat-skill.zip                # Ferdigpakket skill for opplasting til Claude.ai
└── references/
    └── structure.md                      # Annotering av huben /a/histstat/publikasjoner/: 25 emnesider, 12 serier, 9 periodika, bibliografi, filnavn-konvensjoner
```

`CLAUDE.md` og `scripts/` i repoet er vedlikeholder-interne og følger ikke med i pakken.

## Installasjon

### Claude.ai

1. Last ned [ssb-histstat-skill.zip](ssb-histstat-skill.zip), eller bygg den fra repoet med `scripts/build_zip.sh` (ikke zip mappen selv — da følger `CLAUDE.md` og `scripts/` med). Pakken har toppmappe `ssb-histstat/`
2. Gå til **Settings > Features > Skills**
3. Last opp ZIP-filen

### Claude Code

Installert navn er `ssb-histstat`; mappen i repoet heter `ssb-histstat-skill`. Fra repo-roten:

```bash
# Kopi, globalt (tilgjengelig i alle prosjekter)
cp -r ssb-histstat-skill ~/.claude/skills/ssb-histstat

# Eller symlenke fra et klonet repo — da holder git pull kopien oppdatert
ln -s "$PWD/ssb-histstat-skill" ~/.claude/skills/ssb-histstat

# Per prosjekt
cp -r ssb-histstat-skill .claude/skills/ssb-histstat
```

## Bruk sammen med søsken-skillen

Skillen er **kompletterende til `ssb-pxwebapi-v2`**, ikke en erstatning. Tommelfingerregel:

- Aktuelle/nyere tall, tidsserie som fortsatt oppdateres → `ssb-pxwebapi-v2`
- Historiske tabeller, eldre folketellinger, NOS-publikasjoner, Statistisk årbok → denne skillen
- Tidsserie som *starter* historisk men fortsetter til i dag → start her (sjekk `statbank-histu.html`), deleger så til `ssb-pxwebapi-v2`

Last opp begge skillene i Claude.ai for komplett dekning av norsk offisiell statistikk fra 1769 til i dag.

## Hva skillen IKKE gjør

- Ikke parsing av PDF-innhold til tabelldata — returnerer URL og kontekst, brukeren åpner selv
- Ikke moderne tall — bruk `ssb-pxwebapi-v2`
- Ikke svensk eller dansk historisk statistikk

## Lisens

Skillen er et hjelpemiddel for å navigere SSBs åpne historiske arkiv. Materialet under `/a/histstat/` er publikasjoner som SSB har gjort fritt tilgjengelig; eldre verk er typisk i public domain, mens nyere er dekket av SSBs lisens ([CC BY 4.0](https://www.ssb.no/diverse/lisens)). Sjekk den enkelte publikasjon for spesifikke vilkår.
