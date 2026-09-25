# PxWebApi-skills

<!--- Language: no --->
[_English see below_](#english)

AI-skills for PxWeb-API-ene til SSB, SCB og andre statistikkbyråer — pluss kodeeksempler for PxWebApi v2. Skillene er uoffiselle. Hverken SSB eller SCB står bak dem.

Et *skill* er ren kunnskap: en `SKILL.md` med arbeidsflyt og regler, og referansefiler som lastes ved behov, i det åpne [Agent Skills](https://agentskills.io)-formatet. Det viser Claude, ChatGPT og andre AI-verktøy som leser slike instruksjoner hvordan API-et fungerer.

Det kaller ikke API-et selv. For det trengs et verktøy som kan sende HTTP GET og POST — en MCP-server, `curl` via Bash, eller en R-/Python-klient. Se «Installasjon».

[![SSB](https://github.com/janbrus/pxwebapi-skills/actions/workflows/check-tables.yaml/badge.svg)](https://github.com/janbrus/pxwebapi-skills/actions/workflows/check-tables.yaml)
[![SCB](https://github.com/janbrus/pxwebapi-skills/actions/workflows/check-scb-examples.yaml/badge.svg)](https://github.com/janbrus/pxwebapi-skills/actions/workflows/check-scb-examples.yaml)
[![Generic v2](https://github.com/janbrus/pxwebapi-skills/actions/workflows/check-v2-generic-zip.yaml/badge.svg)](https://github.com/janbrus/pxwebapi-skills/actions/workflows/check-v2-generic-zip.yaml)
[![Generic v1](https://github.com/janbrus/pxwebapi-skills/actions/workflows/check-v1-zip.yaml/badge.svg)](https://github.com/janbrus/pxwebapi-skills/actions/workflows/check-v1-zip.yaml)

## Skillene

| Skill (installert navn) | Mappe i repoet | Dekker | Språk | Versjon | Status |
| --- | --- | --- | --- | --- | --- |
| `ssb-pxwebapi-v2` | [ssb-pxwebapi-v2-skill/](ssb-pxwebapi-v2-skill/) | SSBs Statistikkbank via PxWebApi v2. Søk, metadata, kodelister, lagrede spørringer, outputformater, Klass/VarDok, ~90 kuraterte tabeller | norsk, engelsk | 1.6.0 | stabil |
| `scb-pxwebapi-v2` | [scb-pxwebapi-v2-skill/](scb-pxwebapi-v2-skill/) | SCB:s Statistikdatabas via PxWebApi v2 | svensk, engelsk | 0.11.0 | beta |
| `generic-pxweb-v2-skill` | [pxwebapi-v2-generic-skill/](pxwebapi-v2-generic-skill/) | Alle PxWebApi v2-installasjoner. Verifisert mot SSB, SCB og Latvia (CSP), med tabell over hva som varierer mellom dem | engelsk | 0.11.0 | beta |
| `generic-pxweb-v1-skill` | [pxwebapi-v1-generic-skill/](pxwebapi-v1-generic-skill/) | Alle PxWebApi v1-installasjoner (den eldre, POST-baserte PxWeb 1.0-API-en). Sju verifisert, 50 kjente | engelsk | 0.12.0 | beta |
| `ssb-chart-skill` | [ssb-chart-skill/](ssb-chart-skill/) | Visualisering av SSB-data i SSBs offisielle stil: palett, typografi, diagramvalg, json-stat2 → chart | norsk | 1.1 | stabil |
| `ssb-histstat` | [ssb-histstat-skill/](ssb-histstat-skill/) | SSBs digitaliserte historiske statistikk 1828–2010 (NOS, Statistisk årbok, folketellinger) | norsk | 0.9.0 | beta |

Versjonen står i `metadata.version` i hver `SKILL.md`; hver mappe har en `CHANGELOG.md` som sier hva som ble endret og hva som ble verifisert mot live API, med dato. «Beta» betyr at skillen har færre verifiserte eksempler og evals enn SSB-skillen, ikke at den er ustabil i bruk.

En språkmodell tolker spørringene og kan velge feil tabell, variabel eller periode. Brukeren må kontrollere tallene mot kilden.

## Hvordan skillene henger sammen

Skillene ruter til hverandre, men blander aldri data. Et svar kommenterer kun tallene som er hentet i den samtalen.

- **Norske tall i dag**, Statistisk sentralbyrå (SSB) → `ssb-pxwebapi-v2`. Svenske, SCB → `scb-pxwebapi-v2`.
- **Vis det som graf** → `ssb-chart-skill`, som tar json-stat2-responsen fra SSB-skillen og styrer bare presentasjonen.
- **Tall fra før ca. 1970** → `ssb-histstat`, som finner riktig publikasjon i historisk statistikk og sender serier som ligger i Statistikkbanken tilbake til SSB-skillen.
- **Styringsrente, valutakurser, statsgjeld** → [norges-bank-api](https://github.com/avocodetoast/norges-bank-api-skill) (tredjepart, SDMX). SSB-skillen henviser dit i stedet for å svare.
- **En annen PxWeb-installasjon** (Latvia, Finland, Island, Færøyene, Grønland, Estland m.fl. ) → `generic-pxweb-v2-skill` hvis den kjører v2, ellers `generic-pxweb-v1-skill`. En URL med `/api/v0/` eller `/api/v1/` er v1; `GET {base}/config` som returnerer `apiVersion` er v2.

Alle seks deler samme grunnregel, skrevet øverst i hver `SKILL.md`: **oppgi aldri et tall som ikke er hentet fra API-et i denne samtalen.** Ingen tall fra hukommelsen, ingen interpolering, ingen innblanding fra andre kilder. Feiler API-et, skal svaret si det.

## Installasjon

**Claude.ai:** last ned zip-filen fra skillens mappe (bygget av `scripts/build_zip.sh` — ikke zip mappen selv, da følger repo-interne filer med) og last den opp under **Settings › Features › Skills**.

**Claude Code:** kopier mappen til skills-katalogen under det *installerte* navnet fra tabellen over. For fire av skillene er det litt forskjellig fra mappenavnet:

```bash
cp -r ssb-pxwebapi-v2-skill ~/.claude/skills/ssb-pxwebapi-v2
```

Eller symlenk fra et klonet repo. Da trenger en bare `git pull` for å oppdatere:

```bash
ln -s "$PWD/ssb-pxwebapi-v2-skill" ~/.claude/skills/ssb-pxwebapi-v2
```

**ChatGPT og Codex:** samme mappe, kopiert eller symlenket til `~/.agents/skills/` (eller `.agents/skills/` i et repo) under det installerte navnet — etter [OpenAIs dokumentasjon](https://developers.openai.com/codex/skills/), ikke testet her. Frittstående skills virker i ChatGPT desktop-app, Codex CLI og IDE-utvidelsen; web og mobil krever plugin-pakking.

**Verktøy for å kalle API-et** (skillene beskriver endepunktene, men henter ikke selv):

- [@jarib/pxweb-mcp](https://www.npmjs.com/package/@jarib/pxweb-mcp) — åpen MCP-server for PxWebApi v2. Standard er SSB; mot SCB eller andre startes den med `--url {base_url}`. SSB- og SCB-skillene har `references/mcp-tools.md` med verktøyoversikt og begrensninger.
- `curl` via Bash — husk `-g`, ellers stopper curl på hakeparenteser, som i `valueCodes[Var]`.
- [PxWebApiData](https://cran.r-project.org/package=PxWebApiData) (R) — støtter både v1 og v2.
- [TRYs MCP-server](https://tools.try.no/ssb-mcp) — hostet, krever registrering, merket eksperimentell.

Hver skill-README har detaljer for sin skill.

## Kvalitetssikring

Eksemplene i skillene er ikke bare illustrasjoner — de er testene. `scripts/check_examples.py` i SSB- og SCB-skillen plukker hver eksempel-URL, POST-body og tabell-ID rett ut av markdown-filene og kaller dem mot det virkelige API-et. Svarer én av dem noe annet enn HTTP 200, feiler bygget. SSB-skillen sjekker i tillegg alle ~90 tabeller i `common-tables.md`, og SCB-skillen at eksempeltabellene fortsatt oppdateres.

GitHub Actions kjører sjekkene ved hver endring, og på nytt hver mandag morgen. Mandagskjøringen er den viktigste: den oppdager at SSB eller SCB har endret noe — en tabell er avsluttet, en variabelkode byttet ut — selv om ingen har rørt repoet. Uten den ville skillen fortsatt si det gamle helt til noen tilfeldigvis oppdaget feilen.

Alle seks skills har dessuten en jobb som bygger zip-filen på nytt og feiler hvis den ikke stemmer med innholdet i mappen. Bygg derfor med `scripts/build_zip.sh` i skillmappa, aldri for hånd.

Fire av skillene har i tillegg `evals/eval-scenarios.md`: typiske brukerspørsmål med fasit for hvilken tabell og hvilke endepunkter svaret bør bygge på. Etter større endringer må en modell faktisk løse dem med verktøy — det holder ikke å lese scenariene og vurdere om svaret ser rimelig ut. Den forskjellen har betydd noe i praksis: eksempeltabellen i SCB-skillen hadde sluttet å oppdateres uten å være merket som avsluttet, og det var en slik kjøring som oppdaget det, ikke HTTP-sjekkene.

## Kodeeksempler

Disse er i hovedsak laget før jeg begynte å arbeide med skill. I mange tilfeller er det en oppdatering av arbeid jeg gjorde med PxWebApi v1.

**Jupyter notebooks** — til en viss grad viser rekkefølgen økende kompleksitet:

- [eks1_doi_csv_nor](eks1_doi_csv_nor.ipynb) viser hvordan hente en enkel tabell, detaljomsetningsindeksen, med de nye parametrene i http GET
- [kt-v2-csv-nor](kt-v2-csv-nor.ipynb) — Hent Konjunkturtendensene som CSV. Lag figurer og en stor tabell med SSBs prognoser markert i blått.
- [laks_v2_nor](laks_nor.ipynb) viser hvordan hente datasett som JSON-stat2 med både http GET og POST.
- [text-code](text-code-api2-nor.ipynb) — Få Kode og Tekst i JSON-stat2 og Pandas - eksempel med HS-varekoder i månedlig Utenrikshandel
- [komm-nr-id](komm-nr-id-nor.ipynb) — Hvordan vise **både** kommunenummer/-kode og kommunenavn i en dataframe, dvs. vise kode og tekst i JSON-stat2
- [get_many_default_tables](get_many_default_tables.ipynb) — Fra API-søk til tabell, hent forhåndsvalgt uttrekk for mange tabeller.

**Javascript**

- [kpi_js_v2](kpi_js_v2.html) — Enkel KPI-figur med Highcharts, nytt basisår 2025

**Verktøy**

- [Lag dynamisk URL](https://nesa.no/ssb/forenkle_url.html) — endre fra statisk til dynamisk tid i en API v2-URL som Statistikkbanken har laget. Kildekoden ligger i [forenkle_url.html](forenkle_url.html).

## Bakgrunn

- [Hva er nytt i PxWebApi versjon 2](nytt_i_v2.md)
- [Brukerhåndbok for PxWebApi v2 (arkivert)](docs/archive/beta-bruker.md) — norsk bearbeiding fra 2025 av SCBs spesifikasjonsutkast, skrevet mens v2 var i beta og uten ordentlig veiledning. Ikke vedlikeholdt, men forklarer begrepsapparatet grundigere enn de gjeldende veiledningene.
- SSBs egen veiledning: [API mot Statistikkbanken – brukerveiledning](https://www.ssb.no/api/pxwebapiv2)
- [PxWebApi 2 User Guide (PxTools)](https://www.pxtools.net/PxWebApi/documentation/user-guide/) og [PxApiSpecs](https://github.com/PxTools/PxApiSpecs) — den felles spesifikasjonen

Data fra SSB er lisensiert under [CC BY 4.0](https://www.ssb.no/diverse/lisens); SCB og Latvia publiserer under CC0. Lisens-URL-en for en installasjon står i `GET /config`.

## Lisens

Skillene, skriptene og kodeeksemplene i repoet er lisensiert under [MIT-lisensen](LICENSE), © 2026 Jan Bruusgaard. Hver skill-zip har lisensteksten med som `LICENSE`. MIT gjelder koden og tekstene her, ikke statistikken som hentes — den har byråenes egne lisenser (se over).

---

<!--- Language: en --->
# English

AI skills for the PxWeb APIs of Statistics Norway (SSB), Statistics Sweden (SCB) and other statistical agencies, plus code examples for PxWebApi v2.

A *skill* is knowledge only: a `SKILL.md` with workflow and rules, and reference files loaded on demand, in the open [Agent Skills](https://agentskills.io) format. It teaches Claude, ChatGPT, Deepseek and other AI tools that read such instructions how the API works, but does not call it — for that you need a tool that can send HTTP GET and POST: an MCP server, `curl` via Bash, or an R/Python client.

| Skill (installed name) | Folder | Covers | Language | Version | Status |
| --- | --- | --- | --- | --- | --- |
| `ssb-pxwebapi-v2` | [ssb-pxwebapi-v2-skill/](ssb-pxwebapi-v2-skill/) | Statistics Norway's Statbank via PxWebApi v2, incl. search, codelists, saved queries, output formats and ~90 curated tables | Norwegian, English | 1.6.0 | stable |
| `scb-pxwebapi-v2` | [scb-pxwebapi-v2-skill/](scb-pxwebapi-v2-skill/) | Statistics Sweden's Statistikdatabasen via PxWebApi v2 | Swedish, English | 0.11.0 | beta |
| `generic-pxweb-v2-skill` | [pxwebapi-v2-generic-skill/](pxwebapi-v2-generic-skill/) | Any PxWebApi v2 installation; verified against SSB, SCB and Latvia (CSP), with a table of what differs between them | English | 0.11.0 | beta |
| `generic-pxweb-v1-skill` | [pxwebapi-v1-generic-skill/](pxwebapi-v1-generic-skill/) | Any PxWebApi v1 installation (the older POST-only PxWeb 1.0 API); seven verified, 50 known | English | 0.12.0 | beta |
| `ssb-chart-skill` | [ssb-chart-skill/](ssb-chart-skill/) | Charts in Statistics Norway's official style, from a json-stat2 response | Norwegian | 1.1 | stable |
| `ssb-histstat` | [ssb-histstat-skill/](ssb-histstat-skill/) | Statistics Norway's digitised historical statistics 1828–2010 | Norwegian | 0.9.0 | beta |

The skills route to each other but never blend data: an answer comments only on the figures fetched in that conversation, and every `SKILL.md` opens with the rule **never state a number that was not fetched from the API in this conversation.** For a country without a dedicated skill, use the generic v2 skill if the installation runs PxWebApi v2 (`GET {base}/config` returns `apiVersion`), otherwise the generic v1 skill (URLs containing `/api/v0/` or `/api/v1/`).

**Installation:** in Claude.ai, upload the zip from the skill's folder (built by `scripts/build_zip.sh`) under **Settings › Features › Skills**. In Claude Code, copy or symlink the folder into `~/.claude/skills/` under the *installed name* from the table — for four of the six it differs from the folder name. For ChatGPT and Codex, put the same folder in `~/.agents/skills/` (or `.agents/skills/` in a repo) — per [OpenAI's documentation](https://developers.openai.com/codex/skills/), untested here. To call the API, use [@jarib/pxweb-mcp](https://www.npmjs.com/package/@jarib/pxweb-mcp) (`--url {base_url}` for anything but SSB), `curl -g`, or [PxWebApiData](https://cran.r-project.org/package=PxWebApiData) in R. Each skill's README has the details.

**Quality:** every example URL, POST body and table ID written in the SSB and SCB skills is checked against the live API by `scripts/check_examples.py`, on every change and every Monday via GitHub Actions; all six skills have a zip-sync job. Four skills also carry eval scenarios that are run as real tool-using runs after larger edits.

**Code examples - Jupyter notebooks**

- [eks1_doi_csv_eng](eks1_doi_csv_eng.ipynb) — how to get a simple dataset, Index of Retail Sales, using the new parameters in http GET
- [laks_v2_eng](laks_eng.ipynb) — shows how to get a dataset as JSON-stat2, using both http GET and POST.
- [text-code-eng](text-code-api2-eng.ipynb) — Get both code and text in JSON-stat2 and Pandas - example with HS codes for goods from monthly foreign trade statistics
- [What's new in PxWebApi version 2](new_in_v2.md)

Background: [Statistics Norway's API user guide](https://www.ssb.no/en/api/pxwebapiv2), the [PxWebApi 2 User Guide (PxTools)](https://www.pxtools.net/PxWebApi/documentation/user-guide/) and [PxApiSpecs](https://github.com/PxTools/PxApiSpecs). SSB data is licensed under [CC BY 4.0](https://www.ssb.no/en/diverse/lisens). SCB and Statistics Latvia publish under CC0.

**License:** the skills, scripts and code examples in this repository are licensed under the [MIT License](LICENSE), © 2026 Jan Bruusgaard. Every skill zip ships the licence text as `LICENSE`. MIT covers the code and text here, not the statistics fetched — those carry each agency's own licence.
