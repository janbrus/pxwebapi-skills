# Agent Skill: SSB PxWebApi v2

En [Agent Skill](https://agentskills.io) som lærer AI-verktøy som Claude og ChatGPT å søke, utforske og hente data fra SSBs Statistikkbank via PxWebApi v2. Formatet er en åpen standard som støttes av [Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude), [ChatGPT og Codex](https://developers.openai.com/codex/skills/), Deepseek m.fl.

Skillen er uoffissiell, og SSB står ikke bak. En språkmodell tolker spørringene og kan velge feil tabell, variabel eller periode. Brukeren må kontrollere tallene mot kilden.

## Hva skillen gjør

- Guider AI-assistenten gjennom riktig arbeidsflyt: søk → metadata → query → presenter
- Dekker alle endepunkter i PxWebApi v2 (tabeller, metadata, kodelister, lagrede spørringer, config)
- Håndterer kodelister og aggregeringer (fylker, kommunesammenslåinger, aldersgrupper)
- Støtter norsk og engelsk
- Inkluderer kurert liste over ~90 mye brukte tabeller, med egen KOSTRA-seksjon
- Refererer til SSBs Klass- og VarDok-systemer via URN-er og ferdige `link.related`-lenker i metadata

## Filstruktur

```
ssb-pxwebapi-v2/
├── SKILL.md                              # Hovedinstruksjoner og arbeidsflyt
├── README.md                             # Denne filen
├── CHANGELOG.md                          # Endringslogg — gjeldende versjon står i SKILL.md
├── ssb-pxwebapi-v2-skill.zip             # Ferdigpakket skill — last opp i Claude.ai, eller pakk ut i .agents/skills/ for ChatGPT/Codex, Deepseek.
├── references/
│   ├── json-stat2.md                     # json-stat2 format-spesifikasjon (Dataset, row-major mm — også gyldig for Eurostat, World Bank)
│   ├── api-details.md                    # SSB-spesifikk driftsinformasjon (publiseringstider, grenser, lisens)
│   ├── codelists-and-filters.md          # Kodelister (inkl. KPI/COICOP-grupperinger, næringsgruppering), filtersyntaks
│   ├── search-syntax.md                  # Lucene-basert søkesyntaks for /tables?query=
│   ├── klass-vardok.md                   # Kobling til SSBs Klass (klassifikasjoner) og VarDok (variabeldefinisjoner)
│   ├── kostra.md                         # KOSTRA: mars/juni-syklus, spesielle kostra koder og variabler
│   ├── output-formats.md                 # json-stat2, csv, xlsx, html, px, parquet, parametre for pivotering og etiketter
│   ├── common-tables.md                  # Vedlikeholdt liste over vanlige tabeller
│   ├── troubleshooting.md                # Feilsøking og standardtegn
│   └── mcp-tools.md                      # Mapping til @jarib/pxweb-mcp MCP-verktøy og deres begrensninger
└── docs/                                 # Tillegg — følger ikke med i pakken
    ├── brukerveiledning.md               # Bruksanvisning: forutsetninger, nettverkstilgang, eksempelspørsmål, feilsøking, MCP-oppsett
    └── instruks-kort.md                  # Kondensert instruks for plattformer uten skill-støtte, f.eks. gratisversjoner. Lim instruks inn i prompt 
```

## Installasjon

### Claude.ai

1. Last ned ZIP-filen: [ssb-pxwebapi-v2-skill.zip](ssb-pxwebapi-v2-skill.zip), eller bygg den fra repoet med `scripts/build_zip.sh` (ikke zip mappen selv — da følger repo-interne filer med)
2. Gå til **Settings > Features > Skills** i Claude.ai
3. Last opp ZIP-filen

### Claude Code

Kopier mappen til skills-katalogen under det installerte navnet `ssb-pxwebapi-v2` (mappen i repoet heter `ssb-pxwebapi-v2-skill`). Fra repo-roten:

```bash
# Kopi, globalt (tilgjengelig i alle prosjekter)
cp -r ssb-pxwebapi-v2-skill ~/.claude/skills/ssb-pxwebapi-v2

# Eller symlenke fra et klonet repo — da holder git pull kopien oppdatert
ln -s "$PWD/ssb-pxwebapi-v2-skill" ~/.claude/skills/ssb-pxwebapi-v2

# Per prosjekt
cp -r ssb-pxwebapi-v2-skill .claude/skills/ssb-pxwebapi-v2
```

### ChatGPT og Codex

ChatGPT og Codex leser skills i samme format fra `.agents/skills/` (ifølge [OpenAIs dokumentasjon](https://developers.openai.com/codex/skills/); ikke testet her). Pakk ut zip-filen, eller kopier mappen fra repoet:

```bash
# Globalt (alle prosjekter)
cp -r ssb-pxwebapi-v2-skill ~/.agents/skills/ssb-pxwebapi-v2

# Per repo
cp -r ssb-pxwebapi-v2-skill .agents/skills/ssb-pxwebapi-v2
```

Symlenker fungerer også. Frittstående skills er tilgjengelige i ChatGPT desktop-app. Codex CLI og IDE-utvidelsen; på ChatGPT web og mobil må skillen (på norsk ferdighet) pakkes som plugin. Velg skillen med `@` i ChatGPT eller `$` i Codex, eller la modellen velge den ut fra beskrivelsen.

### Andre

Deepseek Harness ser ut til å være likt ChatGPT/Codex. Følg plattformens dokumentasjon, for å legge til tilpassede instruksjoner eller "skills". Formatet er beskrevet på [agentskills.io](https://agentskills.io).

## Uten skill-støtte: kompakt instruks

Plattformer som ikke leser skills kan likevel få det meste: [`docs/instruks-kort.md`](docs/instruks-kort.md) er SKILL.md kokt ned til én side. Lim den inn i Claude Project-instruksjoner, ChatGPTs egendefinerte instruksjoner eller som systemprompt via API. Den er kondensert — referansefilene er ikke med, så ved tvil er `SKILL.md` og `references/` fasit.

[`docs/brukerveiledning.md`](docs/brukerveiledning.md) forklarer bruken fra brukerens side: hva som må være på plass, hvilke spørsmål som fungerer, hva svarene skal inneholde, og hva du gjør når noe ikke virker.

Ingen av dem følger med i zip-en.

## Bruk sammen med MCP-server eller API-klient

Skillen er ren kunnskap med arbeidsflyt, regler og referansefiler. Den gir AI-assistenten *veiledning* i hvordan PxWebApi v2 fungerer. For at Claude eller ChatGPT skal kunne *kalle* API-et, trenger du også verktøy. Alternativer:

- **@jarib/pxweb-mcp** (https://www.npmjs.com/package/@jarib/pxweb-mcp) — open source MCP-server for PxWebApi-er, fungerer med SSB, SCB og andre statistikkbyråer som bruker PxWeb V2. Skillen inneholder `references/mcp-tools.md` med mapping mellom verktøyene og API-endepunktene.
- **TRYs MCP-server** (https://tools.try.no/ssb-mcp) — hostet MCP-tjeneste; krever e-postregistrering og er av TRY merket som eksperimentell
- **Egen MCP-server** — bygg din egen med FastMCP eller lignende
- **PxWebApiData (R)** (https://cran.r-project.org/package=PxWebApiData) — R-pakke som henter data fra PxWeb/PxWebApi (SSB, SCB, StatFi, Eurostat m.fl) direkte inn i R som data frames. Støtter **både v1 og v2**, med egen vignett for hver: v2 via `api_data()`/`query_url()`/`meta_data()` (snake_case), v1 via `ApiData()`
- **Direkte API-kall** — skillen beskriver endepunktene slik at Claude eller andre kan konstruere korrekte URL-er

## Lisens

Skillen (`SKILL.md`, `references/`, `docs/` og skriptene) er lisensiert under [MIT-lisensen](https://github.com/janbrus/pxwebapi-skills/blob/main/LICENSE), © 2026 Jan Bruusgaard. Lisensteksten ligger i repo-roten og følger med i zip-filen som `LICENSE`. MIT gjelder skillen, ikke dataene den henter — de har sin egen lisens, se under.

Skillen er laget som et hjelpemiddel for bruk av SSBs åpne API. Data fra SSB er lisensiert under [CC BY 4.0](https://www.ssb.no/diverse/lisens).

## Relaterte skills

- **ssb-histstat** ([`../ssb-histstat-skill/`](../ssb-histstat-skill/)) — norsk historisk statistikk fra SSBs digitaliserte publikasjoner, for tall fra før Statistikkbanken-perioden
- **norges-bank-api** (tredjepart: [avocodetoast/norges-bank-api-skill](https://github.com/avocodetoast/norges-bank-api-skill)) — styringsrente, valutakurser, NOWA, statsgjeld m.m. fra Norges Banks datatorg (SDMX-API)

SSB-skillen *henviser* til disse for spørsmål utenfor Statistikkbanken — den henter aldri data fra andre kilder inn i egne svar; presentasjonen kommenterer kun tallene fra SSB-uttrekket.

## Visualisering

Se skill for visualisering av SSB-data i SSBs stil (farger, typografi, diagramtyper): [ssb-chart-skill.zip](../ssb-chart-skill/ssb-chart-skill.zip). Den er designet for å brukes sammen med denne API-skillen — installer begge i Claude.ai, Claude Code eller ChatGPT for komplett arbeidsflyt fra datahenting til ferdig graf. Dataviz-skillen styrer visualisering, ikke datahenting — den fungerer uavhengig av hvilken MCP-server som brukes.
