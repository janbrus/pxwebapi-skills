# json-stat2 — formatreferens

json-stat2 är ett öppet format för statistiska dataset (https://json-stat.org/). Det används av PxWebApi v2 men också av andra leverantörer som Eurostat och World Bank — Eurostat skickar dock `value` och `status` som objekt nycklade på position, inte som array. Den här filen dokumenterar formatet — leverantörsspecifika detaljer (publiceringstider, gränser m.m.) hör hemma i agentens egen referens.

---

## Dataset-struktur

Både metadata (`/tables/{id}/metadata`) och data (`/tables/{id}/data`) returneras som json-stat2 Dataset:

```json
{
  "version": "2.0",
  "class": "dataset",
  "label": "Tabelltitel",
  "source": "Statistikmyndigheten SCB",
  "updated": "2024-02-22",
  "id": ["Region", "Kon", "Alder", "ContentsCode", "Tid"],
  "size": [1, 1, 1, 1, 5],
  "dimension": { ... },
  "value": [100, 200, 300, null, 500],
  "role": { "time": ["Tid"], "geo": ["Region"], "metric": ["ContentsCode"] },
  "status": { "3": ".." }
}
```

### Nyckelelement

- **`id`** — Variabelnamnen i ordning. Det är den här ordningen som styr indexeringen: iterera över `id`, aldrig över `Object.keys(dimension)`. De sammanfaller hos SCB (13 tabeller, verifierat 2026-10-02), men specifikationen lovar det inte
- **`size`** — Antal värden per variabel (samma ordning som `id`)
- **`value`** — Platt array med alla datavärden, lagrad i **row-major order** (sista dimensionen i `id` varierar snabbast, första varierar långsammast — samma konvention som C/NumPy). För `size = [s₀, s₁, …, sₙ]` och kategoriindex `(i₀, i₁, …, iₙ)` är plattindex = `i₀·(s₁·s₂·…·sₙ) + i₁·(s₂·…·sₙ) + … + iₙ` — varje position gånger dimensionens *stride*, produkten av `size` för alla senare dimensioner. Se räkneexemplet nedan.
- **`dimension`** — Detaljerad info per variabel: koder (`category.index`), etiketter (`category.label`), enheter (`category.unit`), metadata (`extension`)
- **`role`** — Vilka variabler som har roll som `time`, `geo` eller `metric`. **Börja analysen här:** `role.metric` visar vad som mäts (kontrollera `dimension.{metric}.category.unit` för enhet/decimaler), `role.time` är tidsdimensionen, `role.geo` är geografi. **`role.geo` är valfritt och beror på installation — SSB sätter det, SCB gör det inte** (verifierat 2026-09-07 på TAB638, TAB6471 och TAB5444, alla med en `Region`-dimension och `role: {time, metric}`). Leta därför efter en geografisk variabel i `id` först; bara när ingen sådan finns gäller data hela landet — fråga inte användaren. Variabler som finns i `id` men inte i `role` är nedbrytningsdimensioner.
- **`status`** — Flaggor på enskilda celler; nyckeln är index i value-arrayen. **Läs `status` och `value` var för sig.** Är `value` `null` saknas siffran, och symbolen säger varför: `"."` (ej tillämpligt), `".."` (uppgift saknas), `":"` (konfidentiellt). Men en status kan också stå på en cell som **har** ett tal. Då är den en flagga (preliminärt, skattat, en cellnot), och talet ska visas *med* flaggan, inte blankas. PxWebs serializer gör så för celler med datanot (`DATANOTECELL`; källa: `PxTools/PCAxis.Serializers`, `JsonStat2Serializer.GetValueAndStatus`), medan en datasymbol alltid ger `null`. Hos SCB är det inte observerat: i 13 tabeller (2026-10-02) var `..` den enda symbolen, och den stod alltid på `null`. Hos SSB förekommer det (tabell 09842, `*` = preliminärt tal). `null` behåller sin plats i `value`, så filtrera aldrig bort null före indexering. Exakta symboler kan variera mellan leverantörer.
- **`extension`** — Leverantörsspecifik metadata, och den finns på **två nivåer** som inte får förväxlas (verifierat mot SCB 2026-08-30):
  - **Dataset-nivå** (`extension` i roten): `px` (PX-filens nyckelord — `decimals`, `heading`/`stub`, `aggregallowed`, `subject-code`), `contact`, samt `noteMandatory` och `discontinued` när de är satta. `firstPeriod`/`lastPeriod` hör **inte** hemma här — de är fält i `/tables`-träffen, inte i datasetet.
  - **Dimensionsnivå** (`dimension.{var}.extension`): `elimination`, `codelists`, `show`, `refperiod`, `measuringType`, `priceType`, `adjustment`, `alternativeText`, `categoryNoteMandatory`. `measuringType`, `priceType` och `adjustment` avgör hur siffran får presenteras (t.ex. fast pris kontra löpande, säsongrensat eller ej) — läs dem innan du beskriver vad talet betyder.
  - **`elimination` svarar på olika frågor i metadata och data.** I metadata är det kontraktet («får variabeln utelämnas?»). I ett data-svar beskriver det uttaget du fick — `true` bara när värdemängden fortfarande innehåller elimineringsvärdet. Läs aldrig eliminerbarhet ur ett data-svar.
  - **`eliminationValueCode` finns bara i data-svar**, aldrig i metadata (TAB638: saknas på alla sex dimensioner i metadata; `Region=00` i ett data-svar ger `eliminationValueCode: "00"`). Metadata skiljer alltså inte en dimension med egen totalkod (`Region` = `00`, «Riket») från en som summeras i farten (`Kon`) — leta efter «Riket»/«Totalt» i `category.label`, eller kör en provfråga med totalen.

- **`note` + `noteMandatory`** — `note` (roten) är en array av tabellnoter. `extension.noteMandatory` är nycklat på index i den arrayen: `{"0": true, "2": true}` betyder att `note[0]` och `note[2]` ska visas för användaren. Samma mekanik per värde: `dimension.{var}.category.note`, styrt av `extension.categoryNoteMandatory`. Obligatoriska noter följer med data-svaret, så att visa dem kostar inget extra anrop. TAB638 har tre obligatoriska (kommunkodsbyte, regional indelning, registrerat partnerskap).

### Räkneexempel: två dimensioner som varierar

Exemplet ovan har bara en dimension som varierar, så ordningen kan inte bli fel. Med två regioner blir den synlig:

```
GET /tables/TAB6471/data?valueCodes[Region]=0180,1480&valueCodes[Alder]=TotSA&valueCodes[ContentsCode]=000007SF&valueCodes[Tid]=2026M05,2026M06,2026M07
```

ger `id = ["Region", "Alder", "ContentsCode", "Tid"]` och `size = [2, 1, 1, 3]`, med `Region` `{"0180": 0, "1480": 1}` och `Tid` i den ordning frågan angav. API:et sorterar inte: `valueCodes[Tid]=2026M07,2026M05,2026M06` ger `{"2026M07": 0, "2026M05": 1, "2026M06": 2}` (verifierat 2026-10-02). Slå därför alltid upp positionen i `category.index`, och anta aldrig att tiden stiger.

Stride: `Region` 1·1·3 = 3, `Alder` 3, `ContentsCode` 3, `Tid` 1.

| Position i `value` | `Region` | `Tid` |
|---|---|---|
| 0, 1, 2 | `0180` Stockholm | `2026M05`, `2026M06`, `2026M07` |
| 3, 4, 5 | `1480` Göteborg | `2026M05`, `2026M06`, `2026M07` |

Göteborg (index 1) i `2026M07` (index 2) är `1·3 + 0·3 + 0·3 + 2·1 = 5`, alltså `value[5]`. En dimension med storlek 1 har en stride men bidrar alltid med 0. Verifierat 2026-10-02 mot samma fråga som `outputFormat=csv`.

För att testa egen kod: https://json-stat.org/samples/order.json, där varje värde är en text som namnger sin egen position (`A2B1C3`), och `category.index` står i listform. Position 11 i den filen innehåller `A1B1C4` där det borde stå `A2B1C4` (skrivfel, kontrollerat 2026-10-02). Korrekt kod ”misslyckas” alltså just där.

---

## Verktyg

**Idescats JSON-stat-skill** (https://www.idescat.cat/dev/api/taules/jsonstat/SKILL.md, CC BY 4.0) — en kort, leverantörsneutral guide till att läsa ett dataset.
