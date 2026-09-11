---
name: scb-pxwebapi-v2
description: >
  Svensk offentlig statistik från SCB via PxWebApi v2. Använd ALLTID när någon frågar om
  svenska siffror, statistik, befolkning, KPI, inflation, arbetslöshet, löner, priser,
  BNP, ekonomi, handel, export, import, utbildning, hälsa, bostäder, kommun- eller
  länsdata, eller nämner SCB, Statistiska centralbyrån eller Statistikdatabasen.
  Trigger på "hitta siffror på", "hur många bor i", "KPI senaste året", "befolkningsökning",
  "prisindex", "bostadspriser" och liknande. Also trigger on "Swedish statistics",
  "population of Sweden", "Statistics Sweden", "SCB data", "Sweden GDP",
  "inflation in Sweden", "housing prices Sweden" or similar. Använd denna framför
  websökning när svaret finns i svensk offentlig statistik. Täcker kodlistor,
  sparade frågor och outputformat (json-stat2, csv, xlsx).
metadata:
  version: "0.11.0"
---

# SCB PxWebApi v2 — Komplett guide

Denna skill guidar dig genom korrekt användning av SCB:s PxWebApi v2 för att söka, utforska och hämta svensk offentlig statistik. API:ets bas-URL är:

```
https://statistikdatabasen.scb.se/api/v2
```

## Dataintegritet — grundregeln

SCB är Sveriges officiella statistikproducent. Förtroendet för siffrorna är själva produkten. Denna regel går före allt annat i skillen:

**Ange aldrig en siffra du inte har hämtat från API:et i denna konversation.**

- **Inga siffror ur minnet.** Har du inte kört frågan har du inte siffran — det gäller även siffror du är säker på. Folkmängd, prisindex och arbetslöshetstal ändras, och träningsdata har ett brytdatum.
- **Inga siffror från andra källor i samma svar.** Hänvisa vidare i stället för att blanda.
- **Fallerar API:et, säg det.** Inga uppskattningar, inget "ungefär". Se Fallback.
- **Ingen interpolering eller framskrivning.** Saknas en period i uttaget saknas den i svaret.
- **Märk dina egna beräkningar.** Tillväxttal, andelar och summor är dina, inte SCB:s — visa vilka hämtade siffror de bygger på, och behåll API:ets decimaler (`category.unit.decimals`).
- **Visa `status`-värden som de är.** Saknade, preliminära och konfidentiella värden hör hemma i tabellen, inte dolda eller ersatta med noll.
- **Visa obligatoriska noter.** Är `extension.noteMandatory` satt har SCB bestämt att noten ska följa siffran. Att utelämna den är att presentera siffran utan det förbehåll SCB själv knutit till den. Se Steg 5.
- **Kontrollera `discontinued` och `lastPeriod`.** Tabeller avslutas och serien fortsätter ofta i en ny tabell. Använder du en avslutad tabell, säg det och ange sista perioden.

Att inte hitta siffran är ett giltigt svar. Ett ärligt "hittade inte", med förslag på sökord, är bättre än en rimlig siffra som är fel.

---

## API-översikt

PxWebApi v2 har följande endpoints:

| Endpoint                        | Metod      | Syfte                                                                          |
| ------------------------------- | ---------- | ------------------------------------------------------------------------------ |
| `/tables`                       | GET        | Sök efter tabell när du inte vet tabell-ID                                     |
| `/tables/{id}`                  | GET        | Info om en tabell: `firstPeriod`/`lastPeriod`, `timeUnit`, `discontinued`      |
| `/tables/{id}/metadata`         | GET        | Variabler, koder och kodlistor — obligatoriskt före datahämtning               |
| `/tables/{id}/defaultselection` | GET        | Tabellens förvalda selektion — utgångspunkt för stora tabeller                 |
| `/tables/{id}/data`             | GET / POST | Hämta data. POST för komplexa frågor, GET för delbara URL:er                   |
| `/codelists/{id}`               | GET        | Slå upp en kodlista isolerat                                                   |
| `/savedqueries`                 | POST       | Skapa en delbar, återanvändbar fråga                                           |
| `/savedqueries/{id}`            | GET        | Hämta definitionen av en sparad fråga                                          |
| `/savedqueries/{id}/data`       | GET        | Kör en sparad fråga och hämta data                                             |
| `/savedqueries/{id}/selection`  | GET        | Hämta selektionen för en sparad fråga                                          |
| `/config`                       | GET        | `maxDataCells`, rate limit (`maxCallsPerTimeWindow`/`timeWindow`), format, språk, licens |

Alla endpoints accepterar `lang`-parameter (`sv`, `en`). Standard är `sv`.

---

## Verktygsval / Tool selection

API:et kan nås via två kanaler:

- **MCP-verktyg från `pxweb-mcp`** (npm: `@jarib/pxweb-mcp`) — använd dessa när de är anslutna *och täcker behovet*. Verktygstabell och begränsningar i `references/mcp-tools.md`.
- **Direkta HTTP-anrop** (curl via Bash eller motsvarande) — använd URL-strukturen under «Arbetsflöde». POST kräver ett verktyg med stöd för request-body. Med curl: använd `-g` (`--globoff`), annars stannar curl lokalt på hakparenteserna i `valueCodes[Var]` med «bad range in URL» — det är inget API-fel.

**OBS:** `pxweb-mcp` pekar som standard mot norska SSB. Mot SCB måste servern startas med `--url https://statistikdatabasen.scb.se/api/v2` — verifiera vilken instans den anslutna servern använder (verktygsbeskrivningarna nämner "Statistics Norway" oavsett konfiguration).

HTTP är enda kanalen för `/savedqueries`, `/tables/{id}/defaultselection`, `/config`, `outputFormatParams` och svenska texter (`lang=sv`) — inget av detta exponeras av MCP-servern.

---

## Språk / Language

SCB:s API stödjer svenska (`lang=sv`) och engelska (`lang=en`). Tabelltitlar, variabelnamn och värdetexter finns på båda språken.

**Språkval:**

- Om användaren skriver på **svenska**: svara på svenska och använd `lang=sv` i API-anrop
- Om användaren skriver på **engelska**: svara på engelska och använd `lang=en`
- Talformat: svenska använder mellanslag som tusentalsavgränsare och komma som decimaltecken (1 234,5); engelska använder komma och punkt (1,234.5)
- OBS: API:et returnerar alltid decimalpunkt oavsett språk — formatera om vid presentation
- Källhänvisning på svenska: "Källa: SCB, tabell {id}" / på engelska: "Source: Statistics Sweden, table {id}"

---

## Arbetsflöde / Workflow

Följ stegen i ordning. Hoppa aldrig över metadata-steget.

### Steg 1: Förstå behovet

Klargör innan du anropar något:

- **Fenomen** — Vad mäts? (befolkning, priser, sysselsättning, handel, utbildning, hälsa)
- **Geografi** — Hela Sverige, län, kommun, församling?
- **Tidsperiod** — Senaste året, senaste 10 åren, bestämt intervall?
- **Nedbrytning** — Kön, ålder, näringsgren, utbildningsnivå?

Om användaren är vag, ställ **en** följdfråga — inte flera.

### Steg 2: Sök efter tabell

Använd `GET /tables` med `query`-parameter.

**Sökparametrar:**

| Parameter             | Typ    | Beskrivning                                        |
| --------------------- | ------ | -------------------------------------------------- |
| `query`               | string | Fritextsökord                                      |
| `pastDays`            | int    | Begränsa till tabeller uppdaterade senaste N dagar |
| `includeDiscontinued` | bool   | Inkludera avslutade serier (default: false)        |
| `pageNumber`          | int    | Sidnummer för paginering                           |
| `pageSize`            | int    | Antal träffar per sida (default: 20)               |

**Tips för bra sökningar:**

- Använd svenska fackord: "konsumentprisindex" (inte "KPI"), "sysselsatta" (inte "jobb"), "folkmängd" (inte "befolkning" — det ordet hittar inte befolkningstabellerna). Lägg till ett ord ur tabelltiteln när träfflistan blir lång: "folkmängden efter region"
- Sökningen är case-insensitiv och letar i tabelltitlar, variabler och variabelvärden
- Trunkering med `*` (t.ex. `anlägg*`) och fältbegränsning med `title:` räcker ofta
- Använd `pastDays` för nyligen uppdaterade tabeller; kontrollera `lastPeriod`, `timeUnit` och `discontinued` i resultaten
- **`discontinued` är inget tillförlitligt aktualitetstest — jämför alltid `lastPeriod` med dagens datum.** SCB fryser regelbundet en tabell och fortsätter serien i en ny, utan att sätta flaggan. TAB638 (folkmängd efter region, civilstånd, ålder och kön) slutar på 2024 med `discontinued: null`; fortsättningen ligger i TAB5557 (år 2025) och TAB6471 (månad, 2025M01–). Samma sak för KPI: TAB5737 slutar 2025M12, TAB6596 fortsätter. Ligger `lastPeriod` längre bak än tabellens frekvens borde tillåta, sök efter efterföljaren innan du svarar
- För fuzzy-sökning, närhetssökning, booleska operatorer och datumsyntax: se `references/search-syntax.md`

Presentera de 3–5 mest relevanta träffarna med tabell-ID, titel, senaste period, tidsfrekvens och `discontinued`-status. Rekommendera den mest passande.

Responsstrukturen för varje träff inkluderar: `id`, `label`, `description`, `updated`, `firstPeriod`, `lastPeriod`, `timeUnit` (Annual/Quarterly/Monthly/Weekly), `variableNames`, `discontinued`, `subjectCode`, och `paths` (ämnesplacering i SCB:s hierarki).

**Hitta kommunkoder:**

När användaren nämner en kommun du inte kan koden till — wildcards i valueCodes matchar bara *koder*, inte kommunnamn. Strategi:

1. Sök efter kommunnamnet i API:et — sökningen letar i variabelvärden och bekräftar att kommunen finns
2. Hämta metadata för en aktuell tabell med Region-dimension (t.ex. TAB6471) — scanna `category.label` i Region-dimensionen för kommunnamnet och hitta koden
3. Alternativt: använd wildcard på länskoden (t.ex. `01*` för Stockholms län) och identifiera kommunen i resultaten
4. SCB:s standardkoder för kommuner/län följer SKR:s 4-siffriga kommunkoder (de två första = länskod)

### Steg 3: Utforska metadata

Använd `GET /tables/{id}/metadata` för att förstå tabellens struktur.

Metadata returneras i json-stat2-format (Dataset-schema) — se `references/json-stat2.md` för full struktur, row-major-indexering och status-koder. Fokusera på:

- **`id`-array** — Variabelnamnen (t.ex. `["Region", "Kon", "Alder", "ContentsCode", "Tid"]`); `size`-arrayen ger antal värden per variabel
- **`dimension`-objekt** — Per variabel: koder (`category.index`), läsbara namn (`category.label`), enhet och decimaler (`category.unit`, på ContentsCode), samt `extension` med `elimination` och `codelists` (tillgängliga kodlistor)
- **`role`-objekt** — **Börja analysen här:** `role.metric` visar vad som mäts (antal, procent, SEK, index) — hos SCB är det `ContentsCode`; kontrollera `category.unit` för enhet och decimaler. `role.time` är tidsdimensionen. **SCB sätter inte `role.geo`** — geografin hittar du som en variabel i `id` (oftast `Region`; `variableNames` i sökträffen räcker för att se den). Saknas en geografisk variabel helt gäller data hela Sverige — fråga inte användaren. Övriga variabler i `id` är nedbrytningsdimensioner (kön, ålder, näringsgren m.m.)
- **`note`-array + `extension.noteMandatory` (rot)** — tabellnoter, och vilka av dem som **ska visas**; `noteMandatory` är nycklat på index i `note`. Se Steg 5
- **`extension`-objekt (rot)** — `noteMandatory`, `contact`, PX-metadata under `extension.px`, samt `discontinued` när det är satt. **`firstPeriod`/`lastPeriod` ligger inte här** utan på `/tables`-träffen och `GET /tables/{id}` — tillsammans med `timeUnit`, som är enda källan till tidsfrekvens

**Viktiga regler om metadata:**

- Läs `elimination` **enbart från metadata** — i ett data-svar betyder fältet något annat och vilseleder dig. Utelämnar du en eliminerbar variabel försvinner den helt ur svaret (ur `id` och `dimension`, inte som en totalrad); notera det själv. Metadata skiljer inte tabeller med egen totalkod (`Region` = `00`, «Riket») från dem som summeras i farten (`Kon`) — leta efter «Riket»/«Totalt» i `category.label`. `eliminationValueCode` finns bara i data-svar som innehåller totalen (TAB6471 Region=`00` → `"00"`), aldrig i metadata. Detaljer: `references/json-stat2.md`
- Variabler med `elimination: false` MÅSTE inkluderas i query. Tid och ContentsCode är alltid icke-elimineringsbara (felet du annars får står i Steg 4)

**Kodlistor och filtrering:**

Använd `codelist`-parameter i metadata-uppslag eller data-query för att aktivera en kodlista, eller slå upp en kodlista separat med `GET /codelists/{id}`. Aggregeringar (`agg_`) definierar nya aggregatkoder; värdemängder (`vs_`) är delmängder av originalkoder. Kodlistans egna koder (t.ex. `2023_A1` i `agg_RegionKommungrupp2023-`) är de som gäller i `valueCodes` — läs dem från `GET /codelists/{id}`, inte från tabellens ordinarie koder.

**Defaultselection:**

Använd `GET /tables/{id}/defaultselection` för att hämta tabellens förvalda selektion. Användbart som utgångspunkt — särskilt för stora tabeller.

**Ett `GET /data`-anrop utan selektionsparametrar är inget fel, och ger inte hela tabellen** — det returnerar tyst tabellens förvalda selektion.

Det farliga är vad som försvinner. Verifierat 2026-09-07 på `TAB6471`: anropet ger HTTP 200 och `size [3, 1, 1, 1]` — tre tal. **Region finns inte kvar i svaret alls**, eftersom förvalet har en tom värdelista för den dimensionen. Du får rikssiffror uppdelade på kön, utan att något i svaret säger att geografin är borta. Elimineringsbara dimensioner utanför förvalet summeras bort oannonserat. Bygg alltid selektionen själv.

### Steg 4: Bygg och kör query

PxWebApi v2 stödjer **både GET och POST** för datahämtning. Du kan också använda Statistikdatabasen (https://www.statistikdatabasen.scb.se) som grafisk frågebyggare — välj tabell och värden och exportera som API-fråga för att få färdig GET-URL eller POST-body. Användbart för att verifiera koder och filter.

#### POST (rekommenderat för komplexa frågor)

```
POST /tables/{id}/data?outputFormat=json-stat2
Content-Type: application/json

{
  "selection": [
    {
      "variableCode": "Region",
      "valueCodes": ["0180"],
      "codelist": null
    },
    {
      "variableCode": "ContentsCode",
      "valueCodes": ["000007SF"]
    },
    {
      "variableCode": "Tid",
      "valueCodes": ["top(5)"]
    }
  ]
}
```

Variabler med `elimination: true` kan uteslutas från `selection`-arrayen.

#### GET (enklare frågor, delbara URL:er)

```
GET /tables/{id}/data?valueCodes[Region]=0180&valueCodes[ContentsCode]=000007SF&valueCodes[Tid]=top(5)&outputFormat=json-stat2
```

OBS: Variabler med `elimination: false` (typiskt `Tid` och `ContentsCode`) måste alltid inkluderas — annars returnerar API:et HTTP 400. Felmeddelandet innehåller ett stavfel i API:et och lyder ordagrant `"Missing selection for mandantory variable"` (sic, `mandantory`) — samma stavfel som hos SSB. Citera det som det är, annars matchar inte en sökning i loggar.

#### Outputformat

Standard är `json-stat2`. Övriga: `csv`, `xlsx`, `html`, `px`, `json-px` — `dataFormats` i `GET /config` är facit (SCB serverar **inte** `parquet`). `outputFormatParams` gäller bara csv/html/xlsx — skickade tillsammans med json-stat2 ger de 400. De kan kombineras, antingen som upprepad parameter eller kommaseparerade i en (`outputFormatParams=SeparatorSemicolon,UseCodesAndTexts`): `UseCodes` (standard) / `UseTexts` / `UseCodesAndTexts`, `IncludeTitle`, `SeparatorTab` / `SeparatorSpace` / `SeparatorSemicolon` (standard: komma). CSV levereras som `text/csv; charset=iso-8859-1`, inte UTF-8 — `encoding="latin-1"` i pandas (verifierat 2026-09-09). Styr pivoteringen med `heading` (kolumner) och `stub` (rader) — listor av variabelnamn; alla variabler i `stub` ger en rad per observation, det format pivottabeller och pandas vill ha.

#### Filteruttryck i valueCodes

Viktigaste mönster: `top(N)` = senaste N värdena, `bottom(N)` = äldsta N, `from(värde)` = från och med, `to(värde)` = till och med, `*` = alla värden. Wildcards `*` och `?` för mönstermatchning (t.ex. `01*` = alla kommuner i Stockholms län), explicita listor (`2024M01,2024M02` i GET), och `range(från,till)` = slutet intervall. **I en GET-URL måste uttryck med komma stå inom hakparenteser** — `valueCodes[Tid]=[range(2024M01,2024M03)]`, `[top(3,2)]` — eftersom komma annars är listavgränsare; utan hakparenteser svarar API:et `400 "Illegal selection expression"`. I en POST-body skrivs uttrycket utan hakparenteser (`"range(2024M01,2024M03)"`). Uttryck och enskilda koder kan blandas i samma `valueCodes` — `2015,top(2)` ger 2015 plus de två senaste åren (TAB1267). Variabel- och värdekoder är inte skiftlägeskänsliga (`tid`, `contentscode` accepteras); kodlist-ID:n är det hos SSB (inte testat hos SCB). Allt verifierat 2026-09-09.

**För tidsdimensionen: föredra `top(N)`/`from(värde)` framför explicita perioder.** Relativa filter fångar upp nya perioder automatiskt, så delbara URL:er och sparade frågor fortsätter ge aktuella siffror i stället för att frysa på de perioder som råkade vara senast när frågan skrevs. Detta gäller särskilt `/savedqueries`, vars hela syfte är att köras om senare.

**Viktiga begränsningar:**

- API:et har en övre gräns för antal celler per query. Kontrollera `/config` för `maxDataCells`.
- Rate limiting: `/config` visar `maxCallsPerTimeWindow` och `timeWindow` (30 anrop per 10 sekunder i skrivande stund — läs `/config`, inte denna text). Varje svar bär dessutom `X-Rate-Limit-Remaining` och `X-Rate-Limit-Reset` — läs dem före en serie anrop. Vid 429: kör stora frågor sekventiellt, vänta på svaret innan nästa skickas.
- En GET-URL över ca 2 100 tecken ger **404**, inte 400 (gränsen mätt hos SSB 2026-09-09: 2 092 tecken svarar, 2 142 gör det inte). Ersätt långa värdelistor med `*`, `?`, `from()`/`to()`/`[range()]` eller en kodlista, eller använd POST — korta URL:en innan du drar slutsatsen att tabellen saknas.
- **Upprepad värdekod ger 500 med tom body**, inte 400: `valueCodes[Tid]=2023,2023` räcker, i både GET och POST (verifierat mot TAB1267 2026-09-09; samma hos SSB och Lettland). Överlapp mellan ett uttryck och en enskild kod är däremot okej — `2026,top(1)` svarar. Deduplicera listan om du bygger selektionen programmatiskt.
- 503 betyder att tjänsten är nere eller laddar om. Vänta och försök igen; kommer den inte tillbaka gäller Fallback — säg att data inte kunde hämtas.
- Börja smalt — lättare att utvidga än att hantera för mycket data.

### Steg 5: Presentera resultaten

- Visa data i en snygg markdown-tabell
- Inkludera **alltid** källhänvisning med **samtliga tabell-ID:n** som använts (lista alla om flera tabeller kombinerats — utelämna ingen). Format för tal och källhänvisning: se «Språk»
- Förklara vad siffrorna betyder i kontext — på användarens språk. Kommentera **endast** det hämtade uttaget — se Dataintegritet
- Presentera enheter tydligt (antal/count, procent/percent, index, SEK). För index: ange basperioden (t.ex. 2020=100)
- **Visa obligatoriska noter.** `extension.noteMandatory` är nycklat på index i `note`-arrayen och följer med data-svaret — det kostar inget extra anrop. TAB6471 har fyra, TAB6596 fyra
- **Noten kan begränsa din egen aritmetik.** Från referensår 2025 lägger SCB in en kontrollerad slumpmässig osäkerhet i befolkningsstatistiken (Cell Key Method) — **redovisade totaler är därför inte alltid lika med summan av delarna, och osäkerheten adderas när du summerar själv.** Det står i en obligatorisk not. Summerar du hämtade värden till en ny total: säg att den är din egen och att den bär mer osäkerhet än ett enskilt publicerat tal
- **Gör uttaget reproducerbart.** Ange vilka dimensioner du utelämnade och vilken kodlista du använde — svaret registrerar ingetdera. Visa GET-URL:en eller POST-bodyn, eller erbjud en sparad fråga (Steg 6)
- Erbjud att visualisera data
- Erbjud nedladdning i annat format (csv, xlsx)

### Steg 6: Sparade frågor (valfritt)

För att skapa en delbar, återanvändbar fråga:

```
POST /savedqueries
Content-Type: application/json

{
  "tableId": "TAB6471",
  "language": "sv",
  "selection": {
    "selection": [
      { "variableCode": "Region", "valueCodes": ["0180"] },
      { "variableCode": "Alder", "valueCodes": ["TotSA"] },
      { "variableCode": "ContentsCode", "valueCodes": ["000007SF"] },
      { "variableCode": "Tid", "valueCodes": ["top(5)"] }
    ]
  },
  "outputFormat": "json-stat2",
  "outputFormatParams": []
}
```

OBS: Både `outputFormat` *och* `outputFormatParams` är obligatoriska i savedqueries-bodyn — sätt `outputFormatParams: []` om du inte behöver några. Inkludera även alla icke-elimineringsbara variabler — vilka de är varierar per tabell (`Tid` och `ContentsCode` alltid, i TAB6471 dessutom `Alder`).

Returnerar ett ID. Data hämtas med `GET /savedqueries/{id}/data`.

Användbart för rapporter som uppdateras regelbundet — `top(N)` ger alltid de senaste perioderna.

---

## Fallgropar — gör aldrig

Integritetsreglerna överst gäller alltid — dessutom:

- Hämta data utan filter och anta att du fick hela tabellen — du får förvalet, HTTP 200, med eliminerbara dimensioner bortsummerade utan att svaret säger det (se Steg 3); ange alltid explicit selektion
- Anta att kommunkoder är stabila över tid (kommunsammanslagningar och länsbyten förekommer — Heby 1917 → 0331 år 2007)
- Blanda koder från olika kodlistor
- Presentera data utan enhet

---

## Licens

SCB:s statistik publiceras under **Creative Commons CC0 1.0** (public domain — fri att använda, även kommersiellt, utan attributionskrav). Den exakta licens-URL:en exponeras via `GET /config` i fältet `license`. Behåll ändå källhänvisning ("Källa: SCB, tabell {id}") som god praxis och för spårbarhet.

---

## Exempel

### "Hur många bor i Stockholm?"

```
1. GET /tables?query=folkmängden+per+månad
2. GET /tables/TAB6471/metadata
   → Alder har elimination: false i denna tabell — totalen är koden TotSA.
     Kon är eliminerbar (totalkod TotSa — annan versalisering, lätt att förväxla).
3. POST /tables/TAB6471/data
   { "selection": [
       { "variableCode": "Region", "valueCodes": ["0180"] },
       { "variableCode": "Alder", "valueCodes": ["TotSA"] },
       { "variableCode": "ContentsCode", "valueCodes": ["000007SF"] },
       { "variableCode": "Tid", "valueCodes": ["top(1)"] }
   ]}
→ "Den {sista dagen i månaden} {månad år} hade Stockholm {N} invånare (Källa: SCB, tabell TAB6471)"
  — följt av tabellens fyra obligatoriska noter, och med Kon angiven som utelämnad dimension
```

Utelämnas `Alder` här blir svaret `400 "Missing selection for mandantory variable"` — samma variabel är eliminerbar i den äldre TAB638. Eliminerbarhet är en egenskap hos tabellen, inte hos variabelnamnet.

### "KPI senaste 5 åren, månadsvis"

```
1. GET /tables?query=konsumentprisindex+totalt
2. GET /tables/TAB6596/metadata
   → ContentsCode: "00000808" (KPI fastställda tal, 2020=100),
     "00000804" (Årsförändring i procent)
3. POST /tables/TAB6596/data
   { "selection": [
       { "variableCode": "ContentsCode", "valueCodes": ["00000808"] },
       { "variableCode": "Tid", "valueCodes": ["top(60)"] }
   ]}
→ Tabell med månatlig KPI (2020=100) senaste 60 månaderna, med källa.
  TAB6596 är den löpande totala KPI-serien; TAB5737 är äldre serie (1980=100, uppdateras ej efter 2025M12 — `discontinued` är inte satt, titeln är enda signalen).
```

### "What is the population of Sweden?" (English query)

```
1. GET /tables?query=title:population AND title:month&lang=en
2. GET /tables/TAB6471/metadata?lang=en
3. POST /tables/TAB6471/data?lang=en
   { "selection": [
       { "variableCode": "Region", "valueCodes": ["00"] },
       { "variableCode": "Alder", "valueCodes": ["TotSA"] },
       { "variableCode": "ContentsCode", "valueCodes": ["000007SF"] },
       { "variableCode": "Tid", "valueCodes": ["top(1)"] }
   ]}
→ "At the end of {month year}, Sweden had {N} inhabitants (Source: Statistics Sweden, table TAB6471)"
```

Region `00` är «Riket». Behöver du en lång årsserie i stället, är TAB4365 (riket efter kön, 1749–) rätt tabell.

---

## Fallback

Om API:et inte är tillgängligt:

1. **Säg tydligt att data inte kunde hämtas.** Fyll aldrig tomrummet med siffror ur minnet — utan API-åtkomst levererar du vägledning, inte statistik
2. Hänvisa till SCB:s Statistikdatabas: https://www.statistikdatabasen.scb.se
3. Föreslå relevanta sökord baserat på frågan
4. Ge vägledning för manuell uppslagning (tabellnamn, variabler att leta efter)
