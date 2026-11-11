# Felsökning för PxWebApi v2 hos SCB

API:et svarar med två former av felsvar. API-fel har `"type":"Parameter error"` och diagnosen i `title`; `detail` upprepar i så fall bara titeln. Ogiltiga parametervärden ger `application/problem+json` med `title` «One or more validation errors occurred.», `type` som URI och `errors`, som namnger parametern. En HTML-sida eller en tom body bär ingen diagnos — se avsnitten utan `title`.

**Innehåll**

1. HTTP-felkoder: fel med `title` (400, 404), 404 med HTML-sida, curl «bad range in URL», 429, 500, 503
2. För många celler: räkna celler, minska urvalet, CKM-tabellernas egna grupper

---

## HTTP-felkoder

### Fel med `title`

| `title` | HTTP | Orsak och åtgärd |
|---|---|---|
| `Non-existent variable` | 400 | Variabelkoden finns inte i tabellen — jämför med `id` i metadata. Skiftläget spelar ingen roll: variabel- och värdekoder accepteras i gemener (`tid`, `contentscode`, `totsa`) |
| `Non-existent value` | 400 | Koden finns inte i tabellen eller kodlistan. Vanligt: tabellens kod i stället för kodlistans (`2023_A1`, inte `0180`, i `agg_RegionKommungrupp2023-`), fel tidsformat (`2024M01` i en månadstabell, vecka `2026V30`), eller `+` som blivit mellanslag i GET (skriv `100%2B`, inte `100+`) |
| `Non-existent codelist` | 400 | Kodlistan finns inte för variabeln, eller skiftläget är fel: i datafrågan är kodlist-ID:t skiftlägeskänsligt (`VS_CKM02L%C3%A4n` ger felet). Rå å, ä och ö ger också felet. Kopiera ID:t från `extension.codelists` i metadata och procentkoda det (`vs_CKM02L%C3%A4n`) |
| `Missing selection for mandantory variable` (sic) | 400 | En variabel med `elimination: false` saknas. Vilka det är varierar per tabell (Steg 3). Citera titeln ordagrant, med stavfelet |
| `Illegal selection expression` | 400 | Uttryck med komma i GET utan hakparenteser: skriv `valueCodes[Tid]=[range(2025M01,2025M03)]` (Steg 4) |
| `Too many cells selected` | 400 | Se «För många celler» |
| `Unsupported output format` | 400 | `outputFormatParams` tillsammans med `json-stat2`, eller ett format SCB inte serverar (`parquet`). Se `output-formats.md` |
| `One or more validation errors occurred.` | 400 | Ogiltigt parametervärde (`outputFormat=nonsense`, `pageSize=abc`). Läs `errors`, som namnger parametern |
| `Non-existent table` | 404, men **400** från `/data` | Okänt tabell-ID, eller ett v1-namn som `BefolkningNy` — alla v2-ID:n är `TAB` + siffror. Sök efter tabellen med ämnesord (Steg 2). En v1-fråga översätts till v2 med https://pxapiconverter.scb.se/ |
| `Saved query not found` | 404 | Fel ID för sparad fråga. Obligatoriska fält när du skapar en: Steg 6 |

### 404 med HTML-sida: för lång URL

En GET-URL över ca 2 100 tecken ger 404 med webbserverns HTML-sida «404 - File or directory not found», inte API:ets JSON. JSON med `Non-existent table` betyder att tabellen saknas; HTML betyder att URL:en är för lång. Ersätt långa värdelistor med `*`, `?`, `from()`/`to()`/`[range()]` eller en kodlista, eller använd POST, som inte har gränsen. Korta URL:en innan du drar slutsatsen att tabellen saknas.

### curl: «bad range in URL» är inget API-fel

curl tolkar `[` och `]` som ett eget mönster, så en URL med `valueCodes[Region]=…` stannar lokalt med `curl: (3) bad range in URL` innan något har skickats. Använd `curl -g` (`--globoff`) eller koda hakparenteserna som `%5B`/`%5D`. Rå å, ä och ö: se Verktygsval i `SKILL.md`.

### 429 Too Many Requests

Gränsen är 30 anrop per 10 sekunder i skrivande stund, och den gäller **per IP-adress**: kollegor på samma arbetsplats delar kvoten (https://www.scb.se/vara-tjanster/oppna-data/pxwebapi/). `/config` har `maxCallsPerTimeWindow` och `timeWindow`. Varje svar bär dessutom:

| Header | Innehåll |
|---|---|
| `X-Rate-Limit-Limit` | Tidsfönstret (`10s`), inte antalet anrop |
| `X-Rate-Limit-Remaining` | Anrop kvar i fönstret |
| `X-Rate-Limit-Reset` | När fönstret nollställs, ISO 8601 i UTC |

Vänta till `X-Rate-Limit-Reset` och kör sedan anropen ett i taget — vänta på svaret innan nästa skickas. Vid många anrop: håll dig till ungefär halva gränsen, 15 anrop per 10 sekunder, eftersom kvoten delas per IP-adress.

**Från en webbläsare.** API:et svarar `Access-Control-Allow-Origin: *`, men exponerar inte `X-Rate-Limit-*` (ingen `Access-Control-Expose-Headers`), så JavaScript kan inte läsa headrarna. Läs gränsen från `/config`. En preflight (`OPTIONS`, svar 204) räknas **inte**, till skillnad från hos SSB (uppmätt 2026-11-10). `Access-Control-Max-Age` saknas, men det kostar alltså inga extra anrop.

### 500 med tom body

- **Upprepad värdekod** kan ge 500 med tom body, inte 400: `valueCodes[Tid]=2025M01,2025M01` räcker, i både GET och POST (samma hos SSB och Lettland). Överlapp mellan ett uttryck och en enskild kod är däremot okej — `2026M08,top(1)` svarar. Deduplicera listan om du bygger selektionen programmatiskt.
- **Okänt ID i `GET /codelists/{id}`** ger 500 med tom body, inte 404. Skiftläget spelar ingen roll där, till skillnad från i datafrågan.

### 503 Service Unavailable

Tjänsten är nere eller laddar om. Vänta och försök igen; kommer den inte tillbaka gäller Fallback i `SKILL.md` — säg att data inte kunde hämtas.

---

## För många celler

`Too many cells selected` betyder att uttaget överstiger `maxDataCells` i `/config`. Antalet celler är produkten av antalet värden per variabel. Exempel med TAB6471 (Region × Alder × Kon × ContentsCode × Tid, per 2026-10-28, gräns 150 000):

- en månad, alla regioner, åldrar och kön: 312 × 134 × 3 × 1 × 1 = 125 424 celler — svarar
- två månader: 250 848 celler — 400
- två månader med `codelist[Alder]=vs_CKM035%C3%A5rN` (21 femårsklasser): 312 × 21 × 3 × 1 × 2 = 39 312 celler — svarar

**Minska urvalet, i den här ordningen:**

1. `Tid`: `top(N)` i stället för alla perioder
2. `Region`: färre koder, `01*` (Stockholms län med kommuner) eller kodlistan `vs_CKM02L%C3%A4n` för länsnivå
3. Ålder: tabellens egna grupper (`vs_CKM035%C3%A5rN`) i stället för ettårsklasser. I CKM-tabellerna är de också säkrare än att summera själv, eftersom osäkerheten adderas (Steg 5)
4. `ContentsCode`: bara den du behöver
5. Utelämna variabler med `elimination: true` (Steg 3)
