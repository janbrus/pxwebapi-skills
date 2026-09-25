# Feilsøking for PxWebApi v2

Vanlige feilscenarier og løsninger. Feilresponsen ligner RFC 7807, men er ikke en full implementasjon: `type` er en ren streng («Parameter error»), ikke en URI, og `detail` settes som regel ikke. **Diagnosefeltet er `title`.**

---

## HTTP-feilkoder

### 400 Bad Request

Ugyldig forespørsel. **Diagnostiser fra `title`, ikke fra `detail`** — `detail` finnes som regel ikke. Verifiserte former (2026-08-30):

| Situasjon | Payload |
|---|---|
| Ukjent variabel | `{"type":"Parameter error","title":"Non-existent variable","status":400}` |
| Ugyldig verdikode | `… "title":"Non-existent value" …` |
| Manglende obligatorisk variabel | `… "title":"Missing selection for mandantory variable" …` (sic, `mandantory`) |
| For mange celler | `… "title":"Too many cells selected","detail":"Too many cells selected"` |
| Komma-uttrykk i GET uten hakeparenteser | `… "title":"Illegal selection expression" …` |
| Ukjent kodeliste-ID | `… "title":"Non-existent codelist" …` |

`detail` settes kun i «Too many cells»-tilfellet, og gjentar da bare `title`. Formen er identisk hos SCB, så en feilhåndtering skrevet mot SSB virker også der.

**Vanlige årsaker:**

- **Ukjent variabelkode** — `variableCode` i selection matcher ikke metadata. Variabel- og verdikoder er *ikke* case-sensitive (`region`, `contentscode`, `personer1` og `TOP(1)` aksepteres — verifisert 2026-09-09), så feilen skyldes at koden ikke finnes, ikke stor/liten bokstav. `Region` finnes ikke i KOSTRA-tabellene — der heter variabelen `KOKkommuneregion0000`/`KOKfylkesregion0000`/`KOKbydelsregion0000`, se `kostra.md`.
- **Ugyldig verdikode** — Koden finnes ikke i tabellen. Sjekk `category.index` i metadata. I KOSTRA kan en `KOS…`-kode fra i fjor være borte, fordi variablene byttes ut når rapporteringskravene endres — hent metadata på nytt.
- **Feil tidsformat** — Bruker `"2024"` i en månedlig tabell (skal være `"2024M01"`).
- **For mange celler** — Resultatet overstiger `maxDataCells` fra `/config`.
- **Manglende obligatorisk variabel** — Variabel med `elimination: false` mangler fra selection. I KOSTRA-tabellene gjelder det nesten alle dimensjoner — også region (`KOKkommuneregion0000`), funksjon, art og regnskapsomfang.
- **Ugyldig kodeliste-ID** — Kodelisten finnes ikke for denne variabelen. Kodeliste-ID-er *er* case-sensitive: `agg_kommfylker` gir `Non-existent codelist`.
- **`range()`, `top(N, offset)` eller `bottom(N, offset)` i GET uten hakeparenteser** — komma er listeskilletegn i URL-en, så uttrykket deles i to. Skriv `valueCodes[Tid]=[range(2020,2022)]`. Gjelder ikke POST. Se `codelists-and-filters.md`.
- **Manglende `OutputFormatParams` i `POST /savedqueries`** — feltet er obligatorisk i request-bodyen selv om verdien er tom. Send `"outputFormatParams": []` hvis du ikke trenger noen. Symptom: `400 — "The OutputFormatParams field is required."`

**Løsning:** Hent metadata på nytt, sammenlign variabelkoder og verdikoder nøyaktig.

### curl: «bad range in URL» er ikke en API-feil

curl tolker `[` og `]` som sitt eget «globbing»-mønster. En URL med `valueCodes[Region]=…` feiler derfor lokalt, før noe er sendt:

```
curl: (3) bad range in URL position 66:
```

Bruk `curl -g` (`--globoff`), eller URL-kod hakeparentesene som `%5B`/`%5D` — API-et godtar begge. Det samme gjelder `[range(2020,2022)]`-uttrykk. Får du ingen JSON-respons i det hele tatt, sjekk dette først.

### 403 Forbidden

Forespørselen er forstått men nektet.

**Vanlige årsaker:**

- Tabellen er merket som ikke tilgjengelig via API
- Lagret spørring tilhører en annen bruker/sesjon

### 404 Not Found

Ressursen finnes ikke.

**Vanlige årsaker:**

- Feil tabell-ID (skal være et tall som streng, f.eks. `"07459"`)
- Tabellen er fjernet og erstattet av en ny — søk etter temaet
- Feil kodeliste-ID
- Feil saved query-ID
- **URL-en er lengre enn ca. 2 100 tegn** — API-et svarer 404, ikke 400. Grensen er målt 2026-09-09 på 07459: 400 distinkte kommunekoder (2 092 tegn) gir 200, 410 koder (2 142 tegn) gir 404. Bytt lange verdilister mot `*`, `?`, `from()`/`to()`/`[range()]` eller en kodeliste, eller bruk POST, som ikke har lengdegrensen

**Løsning:** Bruk `GET /tables?query=...` for å finne riktig ID. Er URL-en lang, kort den ned før du konkluderer med at ressursen mangler.

### 429 Too Many Requests

Rate-limiting. Du har sendt for mange forespørsler.

**Løsning:** Vent til tidsvinduet nullstilles og prøv igjen. Kjør store spørringer sekvensielt — vent på svaret før neste sendes, ikke parallelt. Grensen står i `x-ratelimit-*`-responsheaderne (ikke lenger i `/config`): `x-ratelimit-policy: 40;w=60s` betyr 40 kall per 60 sekunder, og `x-ratelimit-remaining` viser gjenstående kall i inneværende vindu. Se `api-details.md` for full headeroversikt.

### 500 Internal Server Error

**Gjentatt verdikode.** Oppgir du samme kode to ganger i samme variabel — `valueCodes[Region]=0301,0301`, eller `["0301", "0301"]` i en POST-body — svarer API-et 500 med **tom body**, ikke 400 med forklaring. To like koder er nok. Verifisert 2026-09-09 hos SSB, og samme oppførsel hos SCB og Latvia.

Overlapp mellom et uttrykk og en enkeltkode er derimot uproblematisk: `valueCodes[Tid]=2026,top(1)` gir 200 selv når `top(1)` også er 2026 — det er bare bokstavelig like koder som feiler. Bygger du seleksjonen programmatisk (fra en løkke, en fil eller en union av flere kilder), dedupliser lista før du sender den.

### 503 Service Unavailable

Tjenesten er nede eller under oppdatering. Metadata oppdateres kl. 05.00 og 11.30, og tabellene er utilgjengelige imens; rundt kl. 08.00 er belastningen høy (se `api-details.md`). Vent og prøv igjen. Får du ikke svar, gjelder Fallback i `SKILL.md`: si at data ikke kunne hentes — ikke fyll tomrommet med tall fra hukommelsen.

---

## Vanlige problemer

### For mange celler

**Symptom:** 400-feil med melding om at resultatet overstiger cellegrensen. Grensen teller alle celler i uttrekket, også tomme.

**Beregning:** Antall celler = produktet av antall verdier per variabel. Eksempel:
- 400 kommuner × 2 kjønn × 100 aldre × 40 år = 3 200 000 celler
- 34 097 grunnkretser × 28 år i 04317 = 954 716 celler — ett år går (34 097), alle år ikke. Filtrer på kommuneprefiks (`0301*`) eller bruk `agg_GrkretsNy`; se «Regionale nivåer under kommune» i `codelists-and-filters.md`

**Løsning (i prioritert rekkefølge):**

1. Begrens Tid: `top(5)` i stedet for alle år
2. Begrens Region: velg spesifikke kommuner/fylker, eller bruk kodeliste for fylkesnivå
3. Bruk kodeliste for aldersaggregering: `agg_FemAarigGruppering`
4. Filtrer på ContentsCode: velg kun den måleenheten du trenger
5. Utelat variabler med `elimination: true`

**Tips:** Hent defaultselection først — den er designet for å holde seg innenfor cellegrensen.

### Tomme eller uventede søkeresultater

- Prøv andre søkeord eller synonymer ("folkemengde" vs "befolkning" vs "innbyggere")
- SSB bruker fagtermer: "konsumprisindeks" ikke "KPI", "sysselsatte" ikke "ansatte"
- Bruk `includeDiscontinued=true` hvis du trenger historiske serier
- Bruk `pastDays=30` for å finne nylig oppdaterte tabeller
- Paginering: sjekk `page.totalPages` — det kan finnes flere resultatsider

### Manglende kommuner

Kommunesammenslåinger i 2020 endret mange kommunekoder. For eksempel ble gamle Oppegård (0217) og Ski (0213) til nye Nordre Follo (3020).

**Løsning:**

- Sjekk metadata for gyldige kommunekoder i tabellen
- Bruk kodeliste for "sammenslåtte kommuner" for konsistente tidsserier
- Bruk fylkesaggregering med `agg_KommFylker` for å unngå kommuneproblemer

### NULL-verdier i data

Normalt. Ikke alle kombinasjoner har data. Spesielt vanlig for detaljerte nedbrytninger (kommune × alder × kjønn × næring).

Sjekk `status`-objektet i json-stat2-responsen. SSBs gjeldende standardtegn (fra 2021):
- `"."` = ikke mulig å oppgi tall (kategorien var ikke i bruk)
- `".."` = tallgrunnlag mangler (ikke innkommet eller for usikre til å publiseres)
- `":"` = vises ikke av konfidensialitetshensyn (for å unngå identifisering)

KOSTRA prikker tall som bygger på færre enn 3 enheter (barnevern, sosialhjelp, kvalifiseringsstønad, bolig) eller færre enn 5 brukere (pleie og omsorg), og for enkelte økonomiske nøkkeltall er landsgjennomsnittet *med* Oslo prikket — bruk `EAKUO` (Landet uten Oslo). Se `kostra.md`.

I eldre tabeller (før 2021) kan du også finne: `"..."` = oppgave mangler foreløpig, `"-"` = null, `"*"` = foreløpig tall.

Se https://www.ssb.no/diverse/standardtegn-i-tabeller (engelsk: https://www.ssb.no/en/diverse/standardtegn-i-tabeller)

### Feil tall eller uventede enheter

- Sjekk `ContentsCode` i metadata — tabellen kan ha flere målevarianter
- Sjekk `category.unit` for enhet (f.eks. "personer", "prosent", "1000 kr", "indeks")
- Sjekk om verdiene er indeksert (KPI: 2025=100)
- Sjekk `extension.measuringType` (Stock, Flow, Average)
- Sjekk `extension.priceType` (Current = løpende priser, Fixed = faste priser)
- Sjekk `extension.adjustment` (sesongjustert, arbeidsdagskorrigert)

### Data ser "feil ut" over tid

- Kommunesammenslåinger i 2020 bryter tidsserier på kommunenivå
- Næringsklassifisering: SSB er i overgang fra SN2007 til SN2025 (fra 2026, statistikk for statistikk, begge varianter oppdateres parallelt). Samme bokstavkode er ulik næring i de to standardene — se «Næringskoder: SN2007 → SN2025» i `codelists-and-filters.md`
- KOSTRA: KOSTRA-gruppene (`EKGnn`) ble revidert fra 2020 (brudd 2019/2020, ofte obligatorisk note); tabellene ble omstrukturert i 2015 (eldre serier ligger i avsluttede tabeller); variabler og tabeller byttes ut når rapporteringskravene endres (sosialtjenesten 2015–2021 → nye tabeller fra 2022) — tomme år for en variabel betyr ofte at den ikke fantes; mars-tall er ureviderte til juni uten `status`-flagg; Landet og Landet uten Oslo er estimerte og veide tall — se `kostra.md`
- KPI-basisår endres periodisk (nå 2025=100)
- Nasjonalregnskapet revideres (foreløpige → endelige tall)

---

## Sjekk API-konfigurasjon

Bruk `GET /config` for å se gjeldende grenser:

Full respons, verifisert 2026-08-30:

```json
{
  "apiVersion": "2.3.2",
  "appVersion": "2.5.0+build.30",
  "languages": [{"id": "no", "label": "Norsk"}, {"id": "en", "label": "English"}],
  "defaultLanguage": "no",
  "maxDataCells": 800000,
  "maxCallsPerTimeWindow": 0,
  "timeWindow": 0,
  "license": "https://www.ssb.no/en/diverse/lisens",
  "sourceReferences": [
    {"language": "en", "text": "Source: Statistics Norway"},
    {"language": "no", "text": "Kilde: Statistisk sentralbyrå"}
  ],
  "defaultDataFormat": "json-stat2",
  "dataFormats": ["json-stat2", "csv", "px", "xlsx", "html", "json-px", "parquet"],
  "features": [{"id": "CORS", "params": [{"key": "enabled", "value": "True"}]}]
}
```

`sourceReferences` er verdt å kjenne: det er SSBs egen kildehenvisningsstreng per språk («Kilde: Statistisk sentralbyrå» / «Source: Statistics Norway»), ved siden av kortformen skillen bruker i Steg 5 («Kilde: SSB, tabell {id}»). Merk også at `parquet` ligger i `dataFormats`.

Verdiene kan endre seg — hardkod dem ikke. NB: `maxCallsPerTimeWindow` og `timeWindow` er nullstilt til `0` og ikke lenger i bruk; rate limit leses fra `x-ratelimit-*`-headerne — se `api-details.md`.
