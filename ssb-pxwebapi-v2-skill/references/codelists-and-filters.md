# Kodelister og filtersyntaks

Komplett referanse for kodelister og filteruttrykk i PxWebApi v2.

---

## Finne kommunekoder

Når brukeren nevner en kommune du ikke kjenner koden til — wildcards i `valueCodes` matcher bare *koder*, ikke kommunenavn. Strategi:

1. Søk etter kommunenavnet med `/tables?query=…` — API-et søker i variabelverdier og bekrefter at kommunen finnes
2. Hent metadata for en relevant tabell (f.eks. 07459) — scan `category.label` i Region-dimensjonen for kommunenavnet og finn koden
3. Alternativt: bruk wildcard på fylkeskoden (f.eks. `34*` for Innlandet, `345?` for å snevre inn) og identifiser kommunen i resultatene
4. Klass API har komplett kommuneklassifikasjon: `https://data.ssb.no/api/klass/v1/classifications/131.json`

---

## Kodelister

### To typer kodelister

| Type            | Prefix | Beskrivelse                         | Eksempel                             |
| --------------- | ------ | ----------------------------------- | ------------------------------------ |
| **Aggregation** | `agg_` | Slår sammen verdier til høyere nivå | `agg_KommFylker` (kommuner → fylker) |
| **Valueset**    | `vs_`  | Viser et alternativt verdisett      | `vs_Fylker` (kun fylkeskoder)        |

Forskjellen: En **aggregering** mapper mange-til-én (flere kommuner → ett fylke). Et **valueset** er bare et annet utvalg av verdier (f.eks. kun fylkeskoder i stedet for alle regioner).

### Finne tilgjengelige kodelister

Kodelister er listet i metadata under `dimension.{variabel}.extension.codelists`. Utdrag fra 07459 (verifisert 2026-09-09 — `Region` tilbyr 11 `agg_`-lister og 3 `vs_`-lister):

```json
{
  "extension": {
    "codelists": [
      {
        "id": "agg_KommFylker",
        "label": "Fylker 2024, sammenslåtte tidsserier",
        "type": "Aggregation",
        "links": [{ "rel": "metadata", "hreflang": "no", "href": "https://data.ssb.no/api/pxwebapi/v2/codeLists/agg_KommFylker?lang=no" }]
      },
      {
        "id": "agg_Fylker2024",
        "label": "Fylker 2024-",
        "type": "Aggregation",
        "links": [{ "rel": "metadata", "hreflang": "no", "href": "https://data.ssb.no/api/pxwebapi/v2/codeLists/agg_Fylker2024?lang=no" }]
      },
      {
        "id": "vs_Fylker",
        "label": "Alle fylker ",
        "type": "Valueset",
        "links": [{ "rel": "metadata", "hreflang": "no", "href": "https://data.ssb.no/api/pxwebapi/v2/codeLists/vs_Fylker?lang=no" }]
      }
    ]
  }
}
```

Merk at `vs_Fylker` («Alle fylker», 41 koder) inneholder både gjeldende og historiske fylkeskoder — vil du ha kun gjeldende inndeling, bruk `agg_Fylker2024` («Fylker 2024-», 16 koder inkl. Svalbard). Kodelisten `vs_Fylker2024` finnes også, men tilbys ikke på 07459 — bruk alltid ID-ene fra den aktuelle tabellens metadata.

### Bruke kodeliste i metadata-oppslag

Hent metadata med kodeliste ferdig aktivert:

```
GET /tables/07459/metadata?codelist[Region]=agg_KommFylker
```

Da viser Region-variabelen aggregerte koder (fylkene) i stedet for alle kommuner.

### Bruke kodeliste i data-query

**POST:**

```json
{
  "selection": [
    {
      "variableCode": "Region",
      "codelist": "agg_KommFylker",
      "valueCodes": ["F-03", "F-11", "F-46"]
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

**GET:**

```
GET /tables/07459/data?lang=no&valueCodes[ContentsCode]=Personer1&valueCodes[Tid]=top(5)&valueCodes[Region]=F-03,F-11,F-46&codelist[Region]=agg_KommFylker
```

Husk: `ContentsCode` og `Tid` er aldri eliminerbare og må alltid være med i spørringen. Dette er en endring fra API v1 der Tid kunne utelates.

**Uten kodeliste** — du kan også spørre etter enkeltverdier som finnes i en kodeliste uten å angi kodelisten eksplisitt. API-et finner riktig kode automatisk.

### Viktig om kodeprefiks i grupperinger

Aggregeringskodelister bruker prefiks på kodene:

- `agg_KommFylker` bruker **`F-`**-prefiks: `F-03` (Oslo), `F-11` (Rogaland), `F-46` (Vestland)
- `agg_KommSummer` bruker **`K-`**-prefiks: `K-0301` (Oslo), `K-3103` (Moss)

`agg_KommFylker` og `agg_KommSummer` gir begge konsistente tidsserier over kommune- og fylkesendringer. `agg_KommFylker` aggregerer til fylkesnivå, `agg_KommSummer` gir summerte kommunetall.

### Slå opp kodelistens innhold

```
GET /codelists/agg_KommFylker?lang=no
```

Returnerer:

```json
{
  "id": "agg_KommFylker",
  "label": "Fylker 2024, sammenslåtte tidsserier",
  "language": "no",
  "type": "Aggregation",
  "values": [
    { "code": "F-31", "label": "Østfold", "valueMap": ["0101", "3124", "0103", ...] },
    { "code": "F-32", "label": "Akershus", "valueMap": ["3232", "3234", ...] },
    { "code": "F-03", "label": "Oslo - Oslove", "valueMap": ["0399", "0301"] },
    { "code": "F-34", "label": "Innlandet", "valueMap": ["3419", "3420", ...] },
    ...
  ]
}
```

`valueMap` viser hvilke opprinnelige kommunekoder (historiske og gjeldende) som aggregeres inn i fylkeskoden. Labelen `"Fylker 2024, sammenslåtte tidsserier"` betyr at kodelisten gir konsistente tidsserier bakover ved å samle alle historiske kommunekoder under gjeldende fylkesstruktur.

### Vanlige kodelister

| Kodeliste-ID             | Variabel        | Beskrivelse                                                                                    |
| ------------------------ | --------------- | ---------------------------------------------------------------------------------------------- |
| `agg_KommFylker`         | Region          | Kommuner aggregert til fylker (gjeldende grenser)                                              |
| `agg_KommSummer`         | Region          | Kommuner summert med gjeldende grenser — gir konsistente tidsserier over kommunesammenslåinger |
| `agg_Fylker2024`         | Region          | Gjeldende fylkesinndeling (2024-), kun dagens fylker                                            |
| `vs_Fylker`              | Region          | Alle fylkeskoder, gjeldende og historiske                                                      |
| `vs_Kommun`              | Region          | Alle kommunekoder, gjeldende og historiske                                                     |
| `agg_FemAarigGruppering` | Alder           | 5-årige aldersgrupper (0-4, 5-9, ...)                                                          |
| `agg_TiAarigGruppering`  | Alder           | 10-årige aldersgrupper (0-9, 10-19, ...)                                                       |
| `agg_RegHFRHF`           | Region          | Helseforetaksregioner                                                                          |
| `agg_Nace17`             | NACE            | 17 næringsgrupper                                                                              |
| `vs_CoiCop2018Kpi01`     | VareTjenesteGrp | KPI: alle nivåer av varer og tjenester (COICOP 2018) — brukes i tabell 14700                   |
| `agg_CoiCop2018Kpi011`   | VareTjenesteGrp | KPI: hovedgruppenivå i COICOP 2018 (12 hovedgrupper) — brukes i tabell 14700                   |

NB: Kodeliste-IDer varierer mellom tabeller og er case-sensitive — bruk alltid nøyaktig ID fra metadata for den aktuelle tabellen.

### outputValues-parameter — ikke bærende hos SSB

Parameteren `outputValues[variabel]` er dokumentert slik:

| Verdi        | Dokumentert betydning                                | Typisk bruk                                            |
| ------------ | ---------------------------------------------------- | ------------------------------------------------------ |
| `aggregated` | Returner aggregerte (summerte) verdier               | `agg_KommSummer` for sammenslåtte kommunetall over tid |
| `single`     | Returner enkeltverdier fra kodelisten uten summering | `agg_Fylker2024` for å velge ut kun gjeldende fylker   |

**Men den har ingen observerbar effekt hos SSB.** Verifisert 2026-08-30:

| Test | Resultat |
|---|---|
| 07459 + `agg_KommSummer`, `K-0301`, `aggregated` / `single` / utelatt | identisk, `[717710, 724290, 728714]` |
| 07459 + `agg_KommFylker`, `*`, `aggregated` / `single` / utelatt | identisk, 18 fylkeskoder |
| `outputValues[Region]=nonsense` | **HTTP 200**, samme data |

**Det er kodelisten som aggregerer.** To praktiske konsekvenser:

- Utelater du parameteren, får du de samme tallene. Den er ufarlig å ha med, men ikke nødvendig — og den bør ikke forklares som forutsetningen for å få summerte verdier.
- **En ugyldig verdi aksepteres stilltiende med HTTP 200.** En skrivefeil her gir ingen feilmelding og ingen endring i dataene, så den er usynlig. Ikke bruk parameteren som en kontroll du tror virker.

Testen er kjørt mot SSB. Om SCB oppfører seg likt er **ikke** verifisert — sjekk før `scb-pxwebapi-v2` endres.

Eksempel — sammenslåtte kommunetall for Moss over tid (parameteren beholdt, men den er ikke det som gjør jobben):

```
GET /tables/07459/data?valueCodes[Region]=K-3103&valueCodes[Tid]=*&valueCodes[ContentsCode]=Personer1&codelist[Region]=agg_KommSummer&outputValues[Region]=aggregated
```

---

## Filteruttrykk i valueCodes

Disse uttrykkene kan brukes i `valueCodes`-arrayet (POST) eller som verdier i `valueCodes`-parameteren (GET).

### Funksjonsbaserte filtre

| Uttrykk            | Beskrivelse                                  | Typisk bruk                                                                                   |
| ------------------ | -------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `top(N)`           | Siste N verdier (nyeste)                     | `["top(1)"]` siste periode · `["top(5)"]` siste 5 år · `["top(13)"]` årsendring, 13 måneder   |
| `top(N, offset)`   | Siste N verdier, etter å ha hoppet over `offset` nyeste | `["top(3,2)"]` de 3 periodene før de 2 nyeste — f.eks. for å utelate foreløpige tall  |
| `bottom(N)`        | Første N verdier (eldste)                    | `["bottom(3)"]` de 3 eldste periodene                                                         |
| `bottom(N, offset)`| Første N verdier, etter å ha hoppet over `offset` eldste | `["bottom(5,1)"]`                                                                    |
| `from(verdi)`      | Fra og med (inklusivt)                       | `["from(2020)"]` 2020 og fremover                                                             |
| `to(verdi)`        | Til og med (inklusivt)                       | `["to(2022)"]` opp til og med 2022                                                            |
| `range(fra,til)`   | Intervall (inklusivt begge)                  | `["range(2018,2023)"]` bevisst fast historisk vindu                                           |

Uttrykk og enkeltkoder kan blandes i samme `valueCodes` (verifisert 2026-09-09): `["2015", "top(2)"]` gir 2015 pluss de to nyeste årene, i både POST og GET. Enkeltverdier oppgis direkte: `["2018", "2020", "2022"]` for utvalgte år, `["2024M06"]` for én måned, `["*"]` for alle verdier. Alle koder er strenger, også rent numeriske (`"0301"`, `"2024"`).

#### Komma i GET-uttrykk krever hakeparenteser

I GET er komma listeskilletegn i `valueCodes[Var]=a,b,c`. Uttrykk som selv inneholder komma — `range(fra,til)`, `top(N, offset)`, `bottom(N, offset)` — blir derfor delt i to og avvist med HTTP 400 `"Illegal selection expression"`. URL-koding av kommaet (`%2C`) hjelper ikke. Løsningen er å sette uttrykket i hakeparenteser, slik SSBs egen dokumentasjon gjør:

```
https://data.ssb.no/api/pxwebapi/v2/tables/07459/data?valueCodes[Region]=0301&valueCodes[ContentsCode]=Personer1&valueCodes[Tid]=[range(2020,2022)]
```

Hakeparentesene kan kombineres med enkeltkoder i samme liste: `valueCodes[Tid]=2015,[range(2020,2022)]`. Uttrykk uten komma (`top(5)`, `from(2020)`, `*`, `46*`) trenger dem ikke. I POST ligger hvert uttrykk som eget element i JSON-arrayet, så der trengs ingen hakeparenteser:

```json
{ "variableCode": "Tid", "valueCodes": ["range(2020,2022)"] }
```

Regelen er lik hos SCB (verifisert 2026-09-09). Bruker du curl, husk `-g` — se `troubleshooting.md`.

> **Foretrekk relative tidsfiltre.** For `role.time`/`Tid`: bruk `top(N)` eller `from(verdi)` framfor `range(fra,til)` og eksplisitte enkeltverdier. `top()`/`from()` er åpne og fanger automatisk opp nye perioder — delbare URL-er og lagrede spørringer holder seg oppdaterte. `range()` og enkeltår er statiske og blir utdaterte. Unntak: et bevisst fast historisk vindu, eller noen få ikke-sammenhengende år (f.eks. folketellingsår).

### Wildcard-filtre

| Uttrykk | Beskrivelse                                       | Eksempel                                                          |
| ------- | ------------------------------------------------- | ----------------------------------------------------------------- |
| `*`     | Alle verdier, eller matcher null eller flere tegn | `*` alene = alle verdier; `03*` = alle koder som starter med "03" |
| `?`     | Matcher nøyaktig ett tegn                         | `??` = alle tosifrede koder                                       |

`*` alene i valueCodes betyr "velg alle verdier for denne variabelen". Kombinert med en kodeliste betyr det "alle verdier i kodelisten".

Wildcards kan kombineres med eksplisitte koder i samme valueCodes-array:

```json
{ "variableCode": "Region", "valueCodes": ["0301", "46*"] }
```

→ Oslo + alle kommuner i Vestland fylke.

Wildcards virker også på tid og på koder i andre dimensjoner, ikke bare region (verifisert 2026-09-09):

| Behov                                             | valueCodes                         | Resultat                                                       |
| ------------------------------------------------- | ---------------------------------- | -------------------------------------------------------------- |
| Alle måneder i 2024 (14700)                       | `valueCodes[Tid]=2024*`            | 12 perioder, `2024M01`–`2024M12`                               |
| KPI for alle tosifrede COICOP-grupper (14700)     | `valueCodes[VareTjenesteGrp]=??`   | 14 koder — totalen `00` og hovedgruppene — uten kodeliste      |

Eksempelet fra SSBs egen veiledning kombinerer begge — KPI-indeksen for alle hovedgrupper, alle måneder i 2024:

```
https://data.ssb.no/api/pxwebapi/v2/tables/14700/data?valueCodes[Tid]=2024*&valueCodes[VareTjenesteGrp]=??&valueCodes[ContentsCode]=KpiIndMnd
```

`Tid=2024*` er et fast vindu på linje med `range()` — bruk det når brukeren ber om et bestemt år, ellers `top()`/`from()`.

`range()` følger på samme måte rekkefølgen i metadata og virker på alle variabler, ikke bare tid. `[range(07.3,07.4.1)]` på `VareTjenesteGrp` gir de sju COICOP-kodene fra 07.3 til og med 07.4.1:

```
https://data.ssb.no/api/pxwebapi/v2/tables/14700/data?valueCodes[Tid]=top(1)&valueCodes[ContentsCode]=KpiIndMnd&valueCodes[VareTjenesteGrp]=[range(07.3,07.4.1)]
```

### Tidsformater

Formatet i valueCodes må matche tabellens `timeUnit`:

| timeUnit  | Format    | Eksempel                  |
| --------- | --------- | ------------------------- |
| Annual    | `YYYY`    | `"2024"`                  |
| Monthly   | `YYYYMNN` | `"2024M06"` (juni 2024)   |
| Quarterly | `YYYYKN`  | `"2024K2"` (Q2 2024)      |
| Weekly    | `YYYYUNN` | `"2024U01"` (uke 1, 2024) |

NB: Tidskodene bruker norske bokstaver uavhengig av `lang`-parameter: `K` for kvartal og `U` for uke — ikke Q/W. Eksempel: tabell 03024 (ukentlig lakseeksport) har perioder som `2026U23`.

### Geografiske filtre

| Behov             | valueCodes                                                | Kommentar                                                                                                |
| ----------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Hele landet       | `["0"]`                                                   | Gjelder 07459 og mange andre tabeller, men er ikke universell — sjekk alltid `category.index` i metadata |
| Oslo kommune      | `["0301"]`                                                |                                                                                                          |
| Bergen kommune    | `["4601"]`                                                |                                                                                                          |
| Alle i Vestland   | `["46*"]`                                                 | Wildcard                                                                                                 |
| Alle fylker       | `["*"]` med `codelist: "agg_KommFylker"`                  | Kodelisten begrenser * til fylker                                                                        |
| Spesifikke fylker | `["F-03","F-11","F-46"]` med `codelist: "agg_KommFylker"` | NB: F-prefiks                                                                                            |
