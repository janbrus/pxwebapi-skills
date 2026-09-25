---
name: ssb-pxwebapi-v2
description: >
  Norsk offisiell statistikk fra SSB via PxWebApi v2. Bruk ALLTID når noen spør om
  norske tall, statistikk, befolkning, KPI, inflasjon, arbeidsledighet, lønn, priser,
  BNP, økonomi, handel, eksport, import, utdanning, helse, bolig, kostra, kommune- eller
  fylkesdata, eller nevner SSB, Statistisk sentralbyrå eller Statistikkbanken.
  Trigger på "finn tall på", "hvor mange bor i", "KPI siste år", "befolkningsvekst",
  "prisindeks", "boligpriser" og lignende. Also trigger on "Norwegian statistics",
  "population of Norway", "Statistics Norway", "SSB data", "Norway GDP",
  "inflation in Norway", "housing prices Norway" or similar. Bruk denne fremfor
  websøk når svaret finnes i norsk offentlig statistikk. Dekker kodelister,
  lagrede spørringer og outputformater (json-stat2, csv, xlsx).
license: MIT. LICENSE has complete terms
metadata:
  version: "1.6.0"
  source: https://github.com/janbrus/pxwebapi-skills/tree/main/ssb-pxwebapi-v2-skill
---

# SSB PxWebApi v2 — Komplett guide

Denne skillen guider deg gjennom riktig bruk av SSBs PxWebApi v2 for å søke, utforske og hente norsk offentlig statistikk. API-ets base-URL er:

```
https://data.ssb.no/api/pxwebapi/v2
```

**Skillen vedlikeholdes her:** https://github.com/janbrus/pxwebapi-skills/tree/main/ssb-pxwebapi-v2-skill

Sjekk repoet for nyere versjon, referansefiler og endringslogg. Denne kopien er v1.6.0.

## Dataintegritet — grunnregelen

SSB er Norges offisielle statistikkprodusent. Tilliten til tallene er selve produktet. Denne regelen går foran alt annet i skillen:

**Oppgi aldri et tall du ikke har hentet fra API-et i denne samtalen.**

- **Ingen tall fra hukommelsen.** Har du ikke kjørt spørringen, har du ikke tallet. Dette gjelder også tall du er sikker på — folketall, KPI-nivåer, ledighetsrater endrer seg, og treningsdata har en skjæringsdato.
- **Ingen tall fra andre kilder i samme svar.** Ikke Norges Bank, Eurostat, OECD, websøk eller nyhetsartikler. Henvis videre i stedet.
- **Feiler API-et, si det.** Ikke anslå, ikke rund av fra minnet, ikke «omtrent». Se «Fallback».
- **Ingen interpolering eller framskriving.** Mangler en periode i uttrekket, mangler den i svaret.
- **Merk egne beregninger.** Vekst i prosent, andeler, summer og indeksomregninger er dine, ikke SSBs. Vis hvilke hentede tall de bygger på.
- **Behold API-ets presisjon.** Bruk desimalene fra `category.unit.decimals`. Ikke legg til presisjon som ikke finnes, og ikke rund bort presisjon som betyr noe.
- **Verifiser variabelkoder mot metadata.** Tabell-ID-er er permanente og endres aldri, men variabelkoder (`ContentsCode`, verdikoder) skal bekreftes med metadata før bruk — ikke gjettes fra hukommelsen.
- **Sjekk `discontinued` og `lastPeriod`.** Tabeller avsluttes, og serien fortsetter ofte i en ny tabell. Bruker du en avsluttet tabell, si det og oppgi siste periode. Finn etterfølgeren når den finnes.
- **Vis `status`.** Manglende, foreløpige og konfidensielle verdier skal fram i tabellen, ikke skjules. Se `references/troubleshooting.md`.
- **Vis obligatoriske noter.** Er `extension.noteMandatory` satt, har SSB bestemt at noten skal følge tallet. Å utelate den er å presentere tallet uten forbeholdet SSB selv knyttet til det — særlig når forbeholdet gjelder nettopp den beregningen du har gjort. Se Steg 5.
- **Flagg foreløpige tall.** Nasjonalregnskap, KOSTRA (ureviderte tall fra 15. mars, reviderte fra 15. juni, uten `status`-flagg — se `references/kostra.md`) og flere andre serier revideres. Si fra når tallene kan endre seg.

Finner du ikke tallet i Statistikkbanken, er riktig svar at det ikke ble funnet — med forslag til søkeord eller alternativ kilde. Et ærlig «vet ikke» er langt bedre enn et plausibelt tall som ikke stemmer. Feil tall med SSB-kildehenvisning skader tilliten til SSB, ikke bare til svaret.

---

## Ruting til andre skills / verktøy

Alle henvisninger er **ruting, aldri datablanding** — svaret i denne skillen kommenterer kun tall hentet fra SSBs API.

- **v1-API-et.** SSB kjører fortsatt v1 parallelt på `https://data.ssb.no/api/v0/{no|en}/table`. Det dukker opp fordi brukere kommer med gamle POST-bodyer i v1-form (`{"query": […], "response": {…}}`) fra skript og Power BI. Oversett dem ikke ad hoc — rut til `generic-pxweb-v1-skill` hvis den er tilgjengelig i miljøet. Request-siden er genuint forskjellig; kun respons-siden (json-stat2) er felles. Gamle `ssb.no/statbank/sq/{id}`-lenker er derimot v2-stoff — se Steg 6. v1s `navigation`-endepunkt finnes ikke i v2; emnehierarkiet ligger i `paths` på `/tables`-treffene (Steg 2).
- **R-pakken `PxWebApiData` er derimot ikke en grunn til å rute til v1** — den støtter begge API-versjonene (1.9.0, 2026-02-02), med snake_case-grensesnittet `api_data()`/`query_url()`/`meta_frames()` m.fl. for v2 og den eldre camelCase-formen `ApiData()` for v1. Kommer brukeren med R-kode mot v2, hører den hjemme i denne skillen; funksjonsoversikt i README.
- **Sentralbankdata** — styringsrente, valutakurser, NOWA, statsgjeld: `norges-bank-api` (se Steg 1).
- **Historisk statistikk** fra før Statistikkbanken-perioden: `ssb-histstat` (se Fallback).
- **Visualisering** av et hentet uttrekk: `ssb-chart-skill` (se Steg 5).

---

## API-oversikt

PxWebApi v2 har disse endepunktene:

| Endepunkt                       | Metode     | Formål                                                                        |
| ------------------------------- | ---------- | ----------------------------------------------------------------------------- |
| `/tables`                       | GET        | Søk etter tabell når du ikke vet tabell-ID-en                                 |
| `/tables/{id}`                  | GET        | Info om én tabell: `firstPeriod`/`lastPeriod`, `timeUnit`, `discontinued`      |
| `/tables/{id}/metadata`         | GET        | Variabler, koder og kodelister — obligatorisk før datauttrekk                  |
| `/tables/{id}/defaultselection` | GET        | Tabellens forhåndsvalgte seleksjon — utgangspunkt for store tabeller           |
| `/tables/{id}/data`             | GET / POST | Hent data. POST for komplekse spørringer, GET for delbare URL-er              |
| `/codelists/{id}`               | GET        | Slå opp en kodeliste isolert                                                  |
| `/savedqueries`                 | POST       | Opprett en delbar, gjenbrukbar spørring                                       |
| `/savedqueries/{id}`            | GET        | Hent definisjonen av en lagret spørring                                       |
| `/savedqueries/{id}/data`       | GET        | Kjør en lagret spørring og hent data                                          |
| `/savedqueries/{id}/selection`  | GET        | Hent seleksjonen til en lagret spørring                                       |
| `/config`                       | GET        | `maxDataCells`, formater og språk (rate limit står i responsheaderne)          |

Alle endepunkter aksepterer `lang`-parameter (`no`, `en`). Standard er `no`.

SSB-spesifikk driftsinfo — publiseringstider, rate limit-headere, lisens og RSS-feeds for publiseringskalender og nyoppdaterte tabeller: se `references/api-details.md`.

---

## Verktøyvalg / Tool selection

API-et kan nås via to kanaler:

- **MCP-verktøy fra `pxweb-mcp`** (npm: `@jarib/pxweb-mcp`) — bruk disse når de er tilkoblet *og dekker behovet*. Se `references/mcp-tools.md` for verktøytabell og begrensninger.
- **Direkte HTTP** (curl via Bash eller tilsvarende) — bruk URL-strukturen under «Arbeidsflyt». POST-spørringer krever et verktøy med request-body-støtte. Med curl: bruk `-g` (`--globoff`), ellers stopper curl lokalt på hakeparentesene i `valueCodes[Var]` med «bad range in URL».

HTTP er eneste kanal for `/savedqueries`, `/tables/{id}/defaultselection`, `/config` og `outputFormatParams` — disse er ikke eksponert av MCP-serveren.

---

## Språk / Language

SSBs API støtter norsk (`lang=no`) og engelsk (`lang=en`). Alle tabelltitler, variabelnavn og verditekster finnes på begge språk.

**Språkvalg:**

- Hvis brukeren skriver på **norsk**: svar på norsk og bruk `lang=no` i API-kall
- Hvis brukeren skriver på **engelsk**: svar på engelsk og bruk `lang=en` i API-kall
- Tallformat tilpasses brukerens språk: norsk bruker mellomrom som tusenskilletegn og komma som desimalskille (1 234,5); engelsk bruker komma og punktum (1,234.5)
- NB: API-et returnerer alltid desimal punktum uavhengig av språk — formater om ved presentasjon
- Kildehenvisning på norsk: "Kilde: SSB, tabell {id}" / på engelsk: "Source: Statistics Norway, table {id}"

---

## Arbeidsflyt / Workflow

Følg disse stegene i rekkefølge. Hopp aldri over metadata-steget.

### Steg 1: Forstå behovet

Avklar før du kaller noe:

- **Fenomen** — Hva måles? (befolkning, priser, sysselsetting, handel, utdanning, helse)
- **Geografi** — Hele Norge, fylke, kommune, bydel, delområde eller grunnkrets? Nivåene under kommune har egne kodeformer og få tabeller — se «Regionale nivåer under kommune» i `references/codelists-and-filters.md`
- **Tidsperiode** — Siste år, siste 10 år, bestemt intervall?
- **Nedbrytning** — Kjønn, alder, næring, utdanningsnivå?

Hvis brukeren er vag, still **ett** oppfølgingsspørsmål — ikke flere.

Gjelder spørsmålet styringsrente, valutakurser, NOWA, statsgjeld/statsobligasjoner eller annen sentralbankdata: bruk `norges-bank-api`-skillen hvis den er tilgjengelig i miljøet — disse dataene ligger hos Norges Bank, ikke i Statistikkbanken.

Gjelder spørsmålet kommunenes eller fylkeskommunenes tjenester og økonomi — barnehagedekning, pleie og omsorg, netto driftsresultat, sammenligning med «KOSTRA-gruppen» — er svaret som regel en KOSTRA-tabell. De bruker egne variabel-ID-er (`KOKkommuneregion0000`, ikke `Region`), spesialkoder for landet og KOSTRA-gruppene, estimerte landstall, har ureviderte tall fra mars og reviderte fra juni, og strukturen endres når rapporteringskravene endres — hent metadata i samme samtale, gjenbruk aldri koder fra hukommelsen. Les `references/kostra.md` før du søker.

### Steg 2: Søk etter tabell

Bruk `GET /tables` med `query`-parameter.

**Søkeparametre:**

| Parameter             | Type   | Beskrivelse                                  |
| --------------------- | ------ | -------------------------------------------- |
| `query`               | string | Fritekst-søkeord                             |
| `pastDays`            | int    | Begrens til tabeller oppdatert siste N dager |
| `includeDiscontinued` | bool   | Inkluder avsluttede serier (default: false)  |
| `pageNumber`          | int    | Sidenummer for paginering                    |
| `pageSize`            | int    | Antall treff per side                        |

**Tips for gode søk:**

- Bruk norske fagtermer: "konsumprisindeks" (ikke "KPI"), "sysselsatte" (ikke "jobber"), "folkemengde" (ikke "befolkning")
- Søket er case-insensitivt og leter i tabelltitler, variabler og variabelverdier
- Trunkering med `*` (f.eks. `anlegg*`) og feltbegrensning med `title:` er ofte nok
- Bruk `pastDays` for nylig oppdaterte tabeller; sjekk `lastPeriod`, `timeUnit` og `discontinued` i resultatene
- Suffiks i tittelen viser laveste regionale nivå: (F) fylke, (K) kommune, (B) bydel, (G) grunnkrets. Søk på ordet (`grunnkrets`, `bydel`) — `title:"(G)"` treffer også G = grunnbeløp
- Næringstabeller finnes i to parallelle varianter under overgangen SN2007 → SN2025 (fra 2026); tittelen sier hvilken. Søk på `SN2025` eller `SN2007` for å skille dem — se `references/codelists-and-filters.md`
- KOSTRA-tabeller kjennes igjen på stien `os > os01 > kostrahoved` i `paths`, ikke på søkeord (`kostrahoved` gir 0 treff, og «kostra» finner ikke bydelstabellene). Søk `kostra` pluss fagterm — se `references/kostra.md`
- For fuzzy søk, nærhetssøk, boolske operatorer og dato-syntaks: se `references/search-syntax.md`

Presenter de 3–5 mest relevante treffene med tabell-ID, tittel, siste periode, tidsfrekvens og `discontinued`-status. Anbefal den mest passende.

Respons-strukturen for hvert treff inkluderer: `id`, `label`, `description`, `updated`, `firstPeriod`, `lastPeriod`, `timeUnit` (Annual/Quarterly/Monthly/Weekly), `variableNames`, `discontinued`, `subjectCode`, og `paths` (emneplassering i SSBs hierarki — en liste av stier, hver med noder). Tredje node i stien (`paths[0][2].id`) er statistikkens kortnavn, brukt i `ssb.no/<kortnavn>` og i RSS-feedene — se `references/klass-vardok.md`.

Se `references/common-tables.md` for en kurert liste over mye brukte tabeller.

Når brukeren nevner en kommune du ikke kjenner koden til, eller du trenger fylkes-/kommune-aggregeringer (`agg_KommFylker`, `agg_KommSummer` med `F-`/`K-`-prefiks): se `references/codelists-and-filters.md`.

### Steg 3: Utforsk metadata

Bruk `GET /tables/{id}/metadata` for å forstå tabellens struktur.

Metadata returneres i json-stat2-format (Dataset-schema) — full formatreferanse i `references/json-stat2.md`. Fokuser på:

- **`id`-array** — Variabelnavnene (f.eks. `["Region", "Kjonn", "Alder", "ContentsCode", "Tid"]`); `size`-arrayet gir antall verdier per variabel
- **`dimension`-objekt** — Per variabel: koder (`category.index`), lesbare navn (`category.label`), enhet og desimaler (`category.unit`, på ContentsCode), noter per verdi (`category.note`), samt `extension` med `elimination`, `codelists` (tilgjengelige kodelister) og `categoryNoteMandatory`
- **`role`-objekt** — **Start analysen her:** `role.metric` viser hva som måles (antall, prosent, NOK, indeks) — hos SSB heter variabelen "statistikkvariabel" på norsk og `ContentsCode` på engelsk; sjekk `category.unit` for enhet og desimaler. `role.time` er tidsdimensjonen, `role.geo` er geografi — **hvis `role.geo` mangler, anta at dataene gjelder hele Norge**, ikke spør brukeren. Øvrige variabler i `id` er nedbrytningsdimensjoner (kjønn, alder, næring osv.)
- **`note`-array + `extension.noteMandatory` (rot)** — tabellnoter, og hvilke av dem som **skal vises**; `noteMandatory` er nøklet på note-indeks. Se Steg 5 og `references/json-stat2.md`
- **`extension`-objekt (rot)** — `contact`, `discontinued`, `noteMandatory` og PX-metadata under `extension.px` (bl.a. `contents`, den korte tabelltittelen du bygger tittel fra i Steg 5). **`firstPeriod`/`lastPeriod` ligger ikke her**, men på `/tables`-treffet og `GET /tables/{id}` — sammen med `timeUnit`, som er eneste kilde til tidsfrekvens. Se `references/json-stat2.md`
- **`link`-objekter (rot og per variabel)** — `link.describedby` gir URN-er til Klass og VarDok; `link.related` gir ferdige menneskelesbare lenker til statistikksiden, «Om statistikken» og definisjonssidene. Se `references/klass-vardok.md`

**Viktige regler om metadata:**

- Les `elimination` **kun fra metadata** — i en data-respons betyr feltet noe annet og villeder deg. Utelater du en eliminerbar variabel, forsvinner den helt fra responsen (ut av `id` og `dimension`, ikke som en «total»-rad); noter det selv. Metadata skiller ikke tabeller med egen totalkode (`Region` = `0`, «Hele landet») fra dem som summeres på flyet (`Kjonn` i 07459) — se etter «I alt»/«Hele landet» i `category.label`. Detaljer og verifisering: `references/json-stat2.md`
- Variabler med `elimination: false` MÅ inkluderes i query. Tid og ContentsCode er alltid ikke-eliminerbare.
- Detaljer per statistikkvariabel (`measuringType`, `priceType`, `adjustment`, `basePeriod`), obligatoriske noter, `aggregallowed` og status-koder: se `references/json-stat2.md`

**Kodelister og filtrering:**

Se `references/codelists-and-filters.md` for komplett referanse over kodelister (aggregeringer `agg_` og verdimengder `vs_`), filteruttrykk (`top()`, `from()`, `range()`, wildcards), og tidsformater.

Kort oppsummert: Bruk `codelist`-parameter i metadata-oppslag eller data-query for å aktivere en kodeliste, eller slå opp en kodeliste separat med `GET /codelists/{id}`.

**Defaultselection:**

Bruk `GET /tables/{id}/defaultselection` for å hente tabellens forhåndsvalgte seleksjon. Nyttig som utgangspunkt — spesielt for store tabeller der du ikke vet hvilke verdier du bør velge. Returnerer en liste `VariableSelection`-objekter med `variableCode`, `codelist` og `valueCodes`. Høyst to dimensjoner får flere enn én verdi i defaultselection (07459: `Region` 360 verdier, `Tid` og `ContentsCode` én hver, `Alder`/`Kjonn` tomme) — trenger du flere dimensjoner utbrettet, må du angi dem selv.

### Steg 4: Bygg og kjør query

PxWebApi v2 støtter **både GET og POST** for datahenting. Du kan også bruke Statistikkbanken (https://www.ssb.no/statbank) som grafisk spørringsbygger — velg tabell og verdier, trykk "Lagre" for å få ferdig GET-URL og POST-body. Nyttig for å verifisere koder og filtre. NB: velger du bare noen perioder, rammer «Lagre» dem opp som faste verdier — skriv om til `top()`/`from()` før du deler URL-en (verktøy for brukere: https://github.com/janbrus/pxwebapi-skills/blob/main/forenkle_url.html). Velger du alle verdier i en variabel, setter PxWeb inn `*` selv.

#### POST (anbefalt for komplekse spørringer)

```
POST /tables/{id}/data?outputFormat=json-stat2
Content-Type: application/json

{
  "selection": [
    {
      "variableCode": "Region",
      "valueCodes": ["0301"],
      "codelist": null
    },
    {
      "variableCode": "ContentsCode",
      "valueCodes": ["Personer1"]
    },
    {
      "variableCode": "Tid",
      "valueCodes": ["top(5)"]
    }
  ]
}
```

Variabler med `elimination: true` kan utelates fra `selection`-arrayet.

#### GET (enklere spørringer, delbare URL-er)

```
GET /tables/{id}/data?valueCodes[Region]=F-03&codelist[Region]=agg_KommFylker&valueCodes[ContentsCode]=Personer1&valueCodes[Tid]=top(5)&outputFormat=json-stat2
```

GET-varianten er ideell for å lage URL-er som kan deles direkte. En GET helt uten seleksjonsparametre er ikke en feil: da returnerer API-et data for tabellens defaultselection (07459 gir f.eks. 360 celler — ikke hele tabellen). Men angir du filtre, må alle variabler med `elimination: false` (typisk `Tid` og `ContentsCode`) inkluderes — ellers returnerer API-et HTTP 400 "Missing selection for mandantory variable" (sic).

#### Outputformater

Standard er `json-stat2`. Øvrige formater: `csv`, `xlsx`, `html`, `px`, `json-px` og `parquet`. Sjekk `dataFormats` i `GET /config` for gjeldende liste.

`parquet` gir lang-format for pandas/DuckDB — `_symbol`-kolonnene bærer `status`. 

For dette, `outputFormatParams` som `UseCodesAndTexts` og `IncludeTitle`, CSV-separatorer og `heading`/`stub`-pivotering: se `references/output-formats.md`.

#### Filteruttrykk i valueCodes

Viktigste mønstre: `top(N)` = siste N verdier, `from(verdi)` = fra og med, `range(fra,til)` = intervall, `*` = alle verdier. Wildcards `*` og `?` kan brukes for mønstermatching (f.eks. `46*` = alle kommuner i Vestland). Uttrykk kan kombineres med enkeltkoder (`["2015", "top(2)"]`). **I GET må uttrykk som inneholder komma stå i hakeparenteser** — `valueCodes[Tid]=[range(2020,2022)]`, `[top(3,2)]` — ellers deles de på kommaet og gir 400 «Illegal selection expression»; POST trenger ikke dette. **For tid: foretrekk `top()` eller `from()` framfor `range()` og enkeltverdier** — relative filtre fanger nye perioder automatisk, så delbare URL-er og lagrede spørringer holder seg oppdaterte. Se `references/codelists-and-filters.md` for komplett syntaks.

**Viktige begrensninger:**

- API-et har en øvre grense for antall celler per spørring. Sjekk `/config` for `maxDataCells` (typisk 800 000, men kan endre seg). Hos SSB annonseres Rate limit i `x-ratelimit-*`-responsheaderne, ikke i `/config` — se `references/api-details.md`.
- Start smalt — det er lettere å utvide enn å håndtere for mye data.

### Steg 5: Presenter resultatene

- Vis dataene i en ryddig markdown-tabell
- Bygg tittel fra `extension.px.contents` (kort tabelltittel) og utvid med valgte variabler og tidsperiode fra uttrekket — f.eks. "Befolkning i Oslo, 2020–2025" basert på `contents: "07459: Befolkning,"` + valgt region og tidsfilter
- Inkluder **alltid** kildehenvisning med **samtlige tabell-ID-er** som er brukt — er flere tabeller kombinert, list opp alle, ikke utelat noen. Henvisnings- og tallformat: se «Språk»
- Forklar hva tallene betyr i kontekst — på brukerens språk. Kommenter **kun** tallene som er hentet i uttrekket; trenger brukeren tall fra andre kilder, henvis videre i stedet (se «Ruting»)
- Presenter enheter tydelig (antall/count, prosent/percent, indeks/index, NOK). For indekser: oppgi referanseperioden (f.eks. 2015=100)
- **Skill hentede tall fra egne beregninger.** Kildehenvisningen dekker tallene fra API-et. Regner du ut vekst, andeler eller differanser, marker det — f.eks. «Endring i prosent er beregnet fra indeksverdiene over»
- **Gjør uttrekket etterprøvbart.** Vis GET-URL-en eller POST-bodyen, eller tilby en lagret spørring (Steg 6). **Oppgi eksplisitt hvilke dimensjoner du utelot og hvilken kodeliste du brukte** — responsen registrerer ingen av delene, og `agg_KommFylker` og `agg_KommSummer` gir tall som ser like ut og ikke er det
- **Vis obligatoriske noter.** Er `extension.noteMandatory` satt, skal noten fram i svaret — SSB har flagget den fordi tallet trenger forbeholdet. Den følger med i data-responsen, så den koster ingen ekstra kall. På KPI-tabellene treffer forbeholdet nettopp endringstall du regner ut selv — se `references/json-stat2.md`
- **Vis `status`-merkede verdier som de er.** Bruk SSBs standardtegn i tabellen og forklar dem i en fotnote — ikke erstatt dem med tall, nuller eller tomme celler
- Tilby å visualisere dataene — bruk `ssb-chart-skill` hvis den er tilgjengelig i miljøet
- Tilby å laste ned i annet format (csv, xlsx)

### Steg 6: Lagrede spørringer (valgfritt)

For å opprette en delbar, gjenbrukbar spørring:

```
POST /savedqueries
Content-Type: application/json

{
  "tableId": "07459",
  "language": "no",
  "selection": {
    "selection": [
      { "variableCode": "Region", "valueCodes": ["0301"] },
      { "variableCode": "ContentsCode", "valueCodes": ["Personer1"] },
      { "variableCode": "Tid", "valueCodes": ["top(5)"] }
    ]
  },
  "outputFormat": "json-stat2",
  "outputFormatParams": []
}
```

NB: Både `outputFormat` *og* `outputFormatParams` er obligatoriske i savedqueries-bodyen — sett `outputFormatParams: []` hvis du ikke trenger noen. Inkluder også alle ikke-eliminerbare variabler (`Tid`, `ContentsCode`).

Returnerer en ID og lenke. Data kan hentes med:

```
GET /savedqueries/{id}/data
```

Nyttig for rapporter som oppdateres jevnlig — `top(N)` gir alltid de nyeste periodene.

**SSBs forbehold:** til automatisering (Power Query, skript) anbefaler SSB en vanlig API-spørring med `top()`/`from()` framfor en lagret spørring — den kan endres senere og er ikke bundet til en ID. Web-lenken `ssb.no/statbank/sq/{id}` gir i PxWeb v2 kun skjermvisning, ikke csv/xlsx, så Power Query-oppsett som pekte dit fra v1-tiden feiler. API-endepunktene virker fortsatt, også for gamle ID-er: `GET /savedqueries/10119120` viser definisjonen, og `/savedqueries/10119120/data` leverer fila i formatet spørringen ble lagret med (verifisert 2026-09-09). Kommer brukeren med en sq-lenke, er dette veien til dataene.

---

## Fallgruver — gjør aldri

Integritetsreglene øverst gjelder alltid — i tillegg:

- Hent data uten filtre og anta at du får hele tabellen — API-et returnerer defaultselection-uttrekket, og du kontrollerer ikke hva det inneholder; angi alltid eksplisitt seleksjon
- Anta at kommunekoder er stabile over tid (kommunesammenslåinger i 2020!)
- Bland koder fra forskjellige kodelister
- Bland næringskoder fra SN2007 og SN2025 — samme bokstav (K, L, …) er ulik næring i de to standardene; les variabel-ID-en (`NACE2007`/`NACE2025`) fra metadata
- Anta at regionvariabelen heter `Region` eller at landet er `0` — i KOSTRA-tabellene heter den `KOKkommuneregion0000`/`KOKfylkesregion0000`/`KOKbydelsregion0000`, landet er `EAK`, alle dimensjoner er obligatoriske, og nøkkeltall summeres aldri (`aggregallowed: false`)
- Presenter data uten enhet

---

## Eksempler

### "Hvor mange bor i Oslo?"

```
1. GET /tables?query=folkemengde
2. GET /tables/07459/metadata
3. POST /tables/07459/data
   { "selection": [
       { "variableCode": "Region", "valueCodes": ["0301"] },
       { "variableCode": "ContentsCode", "valueCodes": ["Personer1"] },
       { "variableCode": "Tid", "valueCodes": ["top(1)"] }
   ]}
→ "Per 1. januar {år} hadde Oslo {N} innbyggere (Kilde: SSB, tabell 07459)"
```

### "KPI siste 5 år, månedlig"

```
1. GET /tables?query=konsumprisindeks
2. GET /tables/14700/metadata
   → Sjekk ContentsCode: "KpiIndMnd" (indeks 2025=100), "Tolvmanedersendring" (12-mnd endring, prosent), "Manedsendring" (månedsendring, prosent), "KpiVektMnd" (vekter)
3. POST /tables/14700/data
   { "selection": [
       { "variableCode": "ContentsCode", "valueCodes": ["KpiIndMnd"] },
       { "variableCode": "Tid", "valueCodes": ["top(61)"] }
   ]}
→ Tabell med månedlig KPI (2025=100), med kilde. NB: Både 03013 og 03014 er avsluttet — bruk 14700.
```

### "Sammenlign befolkning i alle fylker"

```
1. GET /tables/07459/metadata?codelist[Region]=agg_KommFylker
   → Region-variabelen viser nå fylkeskoder med F-prefiks (F-03, F-11, F-46 osv.)
2. POST /tables/07459/data
   { "selection": [
       { "variableCode": "Region", "codelist": "agg_KommFylker",
         "valueCodes": ["*"] },
       { "variableCode": "ContentsCode", "valueCodes": ["Personer1"] },
       { "variableCode": "Tid", "valueCodes": ["top(1)"] }
   ]}
→ Tabell med folketall per fylke. Kodelisten begrenser * til kun fylkeskodene.
```

### "Lag en delbar URL for Oslos befolkning siste 10 år"

Tidsserier med kommunedata bør bruke kodeliste `agg_KommSummer` for å håndtere kommunesammenslåinger og gi konsistente tall over tid. `agg_KommSummer` krever `K-`-prefiks på koden; **det er kodelisten som aggregerer**.

```
https://data.ssb.no/api/pxwebapi/v2/tables/07459/data?valueCodes[Region]=K-0301&codelist[Region]=agg_KommSummer&valueCodes[ContentsCode]=Personer1&valueCodes[Tid]=top(10)&outputFormat=json-stat2
```

### "Eksporter boligpriser som Excel"

```
POST /tables/07221/data?outputFormat=xlsx&outputFormatParams=UseCodesAndTexts&outputFormatParams=IncludeTitle
{ "selection": [
    { "variableCode": "Boligtype", "valueCodes": ["00"] },
    { "variableCode": "ContentsCode", "valueCodes": ["Boligindeks"] },
    { "variableCode": "Tid", "valueCodes": ["top(20)"] }
]}
→ Excel-fil med boligprisindeks siste 20 kvartaler
```

### "What is the population of Norway?" (English query)

```
1. GET /tables?query=population&lang=en
2. GET /tables/07459/metadata?lang=en
3. POST /tables/07459/data?lang=en
   { "selection": [
       { "variableCode": "Region", "valueCodes": ["0"] },
       { "variableCode": "ContentsCode", "valueCodes": ["Personer1"] },
       { "variableCode": "Tid", "valueCodes": ["top(1)"] }
   ]}
→ "As of 1 January {year}, Norway had {N} inhabitants (Source: Statistics Norway, table 07459)"
```

---

## Fallback

Feilkoder og vanlige problemer (400/403/404/429, cellegrense, tomme søkeresultater, NULL-verdier): se `references/troubleshooting.md`.

Hvis API-et ikke er tilgjengelig:

1. **Si tydelig fra at data ikke kunne hentes.** Fyll aldri tomrommet med tall fra hukommelsen — uten API-tilgang leverer du veiledning, ikke statistikk
2. Henvis til SSBs Statistikkbank: https://www.ssb.no/statbank
3. Foreslå relevante søkeord basert på spørsmålet
4. Gi veiledning for manuelt oppslag (tabellnummer, variabler å se etter)

Trenger brukeren tall fra før Statistikkbanken-perioden (eldre folketellinger, NOS-publikasjoner, tidsserier fra 1800-tallet): bruk `ssb-histstat`-skillen hvis den er tilgjengelig i miljøet.
