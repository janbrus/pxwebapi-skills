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

## Regionale nivåer under kommune: bydel, delområde, grunnkrets

Suffikset i tabelltittelen viser laveste regionale nivå: **(F)** fylke, **(K)** kommune, **(B)** bydel, **(G)** grunnkrets. Verifisert 2026-09-20:

| Nivå        | Kodeform                                   | Hvor                                                                                                                                                                                                          |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kommune     | `0301` (4 siffer)                          | De fleste regionale tabeller                                                                                                                                                                                  |
| Bydel       | `030101a` (kommune + bydel + `a`)          | Kodeliste `vs_Bydeler4StoreByerNye2` (57 koder: bydeler i Oslo, Stavanger, Bergen og Trondheim, inkl. under de gamle kommunekodene 1201/1601) — i (B)-tabeller som 06944. KOSTRAs bydelstabeller bruker i stedet `KOKbydelsregion0000` med 6-sifrede koder (`030101`) og `EAB` for alle bydeler, se `kostra.md` |
| Delområde   | `03010100` (kommune + 2 siffer + `00`)     | **Ingen egne delområdetabeller.** Finnes som regionkoder i 06944 (husholdningsinntekt, kodeliste `vs_Delomraader01`, 2 247 delområder) — eneste av de 90 bydel-tabellene som har det (sveip 2026-09-20). I (G)-tabellene finnes koden ikke |
| Grunnkrets  | `03010101` (kommune + delområde + 2 siffer) | Fire (G)-tabeller: 04317 (befolkning), 04362 (alder/kjønn), 06198 (areal), 14737 (boligverdi-koeffisienter). Søk `grunnkrets` gir nøyaktig disse fire; `title:"(G)"` treffer også G = grunnbeløp             |

**Grunnkretstabellene (G)** deler samme dimensjon på 34 097 åttesifrede koder — alle gjeldende og historiske kretser (labeler som «Karrestad (t.o.m. 2002)»), pluss `KKKK0000` «Ikke koblet» og `KKKK9999` «Uoppgitt grunnkrets» per kommune. Variabel-ID-en varierer: `Grunnkretser` i 04317 og 14737 (`elimination: false`), `Region` i 04362 og 06198 (`elimination: true`). Klass-klassifikasjon 1 «Standard for delområde- og grunnkretsinndeling», VarDok 135.

Kodelistene er like på alle fire — og **ingen av dem aggregerer**: hver kode har `valueMap` med ett element, så `agg_`-listene er undermengder, ikke summer.

| Kodeliste-ID           | Innhold                                              |
| ---------------------- | ---------------------------------------------------- |
| `agg_GrkretsNy`        | Gjeldende grunnkretser 2024– (14 513)                |
| `agg_Grkrets2020`      | Grunnkretser 2020–2023 (14 467)                      |
| `agg_GrkretsBydel2002` | Grunnkretser i de fire største byene 2004– (2 517)   |
| `agg_GrkretsKomm2002`  | Alle 34 097, gruppert kommunevis (samme som `vs_`)   |
| `vs_Grunnkretser01`    | Alle 34 097                                          |

**Cellegrensen slår inn fort:** 34 097 kretser × 28 år i 04317 = 954 716 celler > 800 000 → `Too many cells selected`. Ett år for alle kretser (34 097 celler) går fint. Filtrer på kommuneprefiks med wildcard, og husk `ContentsCode` selv om tabellen bare har én statistikkvariabel:

- `https://data.ssb.no/api/pxwebapi/v2/tables/04317/data?lang=no&valueCodes[Grunnkretser]=0301*&valueCodes[ContentsCode]=*&valueCodes[Tid]=top(1)` — 617 Oslo-kretser 2026, 35 historiske med status `.`
- `https://data.ssb.no/api/pxwebapi/v2/tables/04317/data?lang=no&codelist[Grunnkretser]=agg_GrkretsNy&valueCodes[Grunnkretser]=0301*&valueCodes[ContentsCode]=*&valueCodes[Tid]=top(1)` — samme, men kun de 592 gjeldende

**Delområde fra grunnkretstabellene:** wildcard på det sekssifrede prefikset gir kretsene i ett delområde — `valueCodes[Grunnkretser]=030109*` gir de 13 kretsene Majorstuen Rode 1–13 i delområde 03010900 Majorstuen (Oslo). Delområdekoden `03010900` gir derimot 400 `Non-existent value` i 04317. Summen til delområde er *din* beregning (Dataintegritet: merk egne beregninger), og den er ikke alltid lik SSBs eget tall:

- 04317: summen av alle 617 Oslo-kretser 2026 (inkl. `03019999` Uoppgitt) er 728 714 — identisk med kommunetallet i 07459. Her stemmer summering
- 04362: dataset-note sier at alle 1- og 2-tall er endret til 0 eller 3 av personvernhensyn, og Region-noten at «hvis kretstallene aggregeres til kommunenivå, vil det kunne oppstå avvik». Vis noten når du summerer
- 06198: note om avvik fra kommunetall før 2010

- `https://data.ssb.no/api/pxwebapi/v2/tables/04317/data?lang=no&valueCodes[Grunnkretser]=030109*&valueCodes[ContentsCode]=*&valueCodes[Tid]=top(1)` — 200, 13 kretser, ingen tomme
- `https://data.ssb.no/api/pxwebapi/v2/tables/06944/data?lang=no&valueCodes[Region]=0301,03010900&valueCodes[HusholdType]=0000&valueCodes[ContentsCode]=*&valueCodes[Tid]=top(1)` — 200, kommune og delområdet Majorstuen side om side; 06944 tar delområdekoden direkte, med eller uten `codelist[Region]=vs_Delomraader01`

Vil brukeren ha delområdetall SSB selv har publisert, er 06944-typen riktig; vil de ha befolkning, areal eller aldersfordeling på delområde, er svaret en merket sum av grunnkretser fra (G)-tabellene.

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
| `vs_Bydeler4StoreByerNye2` | Region        | Bydeler i de fire største byene (57 koder, form `030101a`) — brukes i 06944                    |
| `vs_Delomraader01`       | Region          | Delområder (2 247 koder, form `03010100`) — brukes i 06944; finnes ikke i (G)-tabellene        |
| `agg_GrkretsNy`          | Grunnkretser/Region | Gjeldende grunnkretser 2024– (14 513) — undermengde, aggregerer ikke; se «Regionale nivåer under kommune» |
| `agg_KOGkommuneregion0000…` | KOKkommuneregion0000 | KOSTRA: «Uttrekk for …»-lister (Landet, Alle kommuner, Kommuner 2024-, KOSTRA-grupperinger m.fl.) — ID varierer per tabell, velg på label; undermengder, aggregerer ikke. Se `kostra.md` |
| `agg_FemAarigGruppering` | Alder           | 5-årige aldersgrupper (0-4, 5-9, ...)                                                          |
| `agg_TiAarigGruppering`  | Alder           | 10-årige aldersgrupper (0-9, 10-19, ...)                                                       |
| `agg_RegHFRHF`           | Region          | Helseforetaksregioner                                                                          |
| `agg_Nace17`             | NACE2007        | 17 næringsgrupper (SN2007-tabeller)                                                            |
| `agg_NACE2025nivaa1`     | NACE2025        | Næringshovedområder A–V inkl. `_T` (24 koder) — brukes i tabell 14729                          |
| `agg_NACE2025niv1`       | NACE2025        | Samme nivå, annen ID — brukes i 14721, 14730, 14731                                             |
| `vs_NACE2025niva1og5nn`  | NACE2025        | Hovedområder + 5-siffer næring, 762 koder — brukes i 14729                                     |
| `vs_CoiCop2018Kpi01`     | VareTjenesteGrp | KPI: alle nivåer av varer og tjenester (COICOP 2018) — brukes i tabell 14700                   |
| `agg_CoiCop2018Kpi011`   | VareTjenesteGrp | KPI: hovedgruppenivå i COICOP 2018 (12 hovedgrupper) — brukes i tabell 14700                   |

NB: Kodeliste-IDer varierer mellom tabeller og er case-sensitive — bruk alltid nøyaktig ID fra metadata for den aktuelle tabellen.

### Næringskoder: SN2007 → SN2025

SSB er i overgang til **SN2025** (Standard for næringsgruppering 2025, norsk utgave av NACE Rev. 2.1). Per 2026-09-20 er 14 tabeller på SN2025 og 331 på SN2007. Overgangen skjer statistikk for statistikk, og **SN2007-tabellene lever videre parallelt** — de er ikke merket `discontinued` og oppdateres fortsatt (10790 og 14729 har begge 2026K2). Tittelen sier hvilken standard tabellen bruker; søk på `SN2025` eller `SN2007` i `/tables?query=` for å skille variantene.

|                      | SN2007-tabeller            | SN2025-tabeller |
| -------------------- | -------------------------- | --------------- |
| Variabel-ID          | `NACE2007`                 | `NACE2025`      |
| Næringshovedområder  | 21 (A–U)                   | 22 (A–V)        |
| Totalkode            | varierer (`A_U` i 07322)   | `_T`            |
| Uoppgitt             | varierer (`00` i 07322)    | `zz5`           |
| 5-sifret kode        | `62.010`                   | `62.100`        |

**Bokstavkodene betyr ikke det samme i de to standardene.** SN2007 J «Informasjon og kommunikasjon» er delt i SN2025 J (utgivelse, kringkasting, innholdsproduksjon) og K (telekommunikasjon, dataprogrammering, IT-tjenester), og alle bokstaver etter J er forskjøvet ett hakk: SN2007 K (finans) = SN2025 L, L (eiendom) = M, M (faglig/teknisk) = N, … U (internasjonale organisasjoner) = V. `valueCodes[NACE2007]=K` gir finans; `valueCodes[NACE2025]=K` gir IT. Les variabel-ID-en fra metadata, og slå alltid opp labelen før du sammenligner bokstavkoder på tvers av tabeller.

Femsifrede koder inneholder punktum og brukes direkte i GET. Kodelistene på `NACE2025` varierer per tabell (se tabellen over; 14758 har ingen). Verifisert 2026-09-20:

- `https://data.ssb.no/api/pxwebapi/v2/tables/14758/data?lang=no&valueCodes[NACE2025]=_T,A,K,L&valueCodes[ContentsCode]=ASer&valueCodes[Tid]=2025` — 200, `_T` = 405 436 aksjeselskaper
- `https://data.ssb.no/api/pxwebapi/v2/tables/14729/data?lang=no&valueCodes[Region]=0&valueCodes[NACE2025]=62.100&valueCodes[ContentsCode]=Konkurser&valueCodes[Tid]=top(1)` — 200, punktum i koden trenger ingen encoding
- `https://data.ssb.no/api/pxwebapi/v2/tables/14729/data?lang=no&valueCodes[Region]=0&codelist[NACE2025]=agg_NACE2025nivaa1&valueCodes[NACE2025]=*&valueCodes[ContentsCode]=Konkurser&valueCodes[Tid]=top(1)` — 200, 24 hovedområder

**Overlappsår:** 07322 (SN2007, 2008–2025) og 14758 (SN2025, 2025–) har begge 2025, og totalen `A_U` = `_T` = 405 436. Totalen er den samme fordi alle næringer er alle næringer — bruddet ligger på næringsnivå. Bruk SN2007-tabellen for lange tidsserier, SN2025-tabellen for 2025/2026 og framover, skjøt aldri de to på næringsnivå, og si i svaret hvilken standard tallene bygger på.

Fullstendig kodeverk (Klass ID 6, versjon 3218) og korrespondansetabell SN2025 → SN2007 (ID 2919): se `klass-vardok.md`.

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
