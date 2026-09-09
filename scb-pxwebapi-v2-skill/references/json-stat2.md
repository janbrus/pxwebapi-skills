# json-stat2 — formatreferens

json-stat2 är ett öppet format för statistiska dataset (https://json-stat.org/). Det används av PxWebApi v2 men också av andra leverantörer som Eurostat och World Bank. Den här filen dokumenterar formatet — leverantörsspecifika detaljer (publiceringstider, gränser m.m.) hör hemma i agentens egen referens.

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
  "value": [100, 200, 300, 400, 500],
  "role": { "time": ["Tid"], "geo": ["Region"], "metric": ["ContentsCode"] },
  "status": { "3": ".." }
}
```

### Nyckelelement

- **`id`** — Variabelnamnen i ordning
- **`size`** — Antal värden per variabel (samma ordning som `id`)
- **`value`** — Platt array med alla datavärden, lagrad i **row-major order** (sista dimensionen i `id` varierar snabbast, första varierar långsammast — samma konvention som C/NumPy). För `size = [s₀, s₁, …, sₙ]` och kategoriindex `(i₀, i₁, …, iₙ)` är plattindex = `i₀·(s₁·s₂·…·sₙ) + i₁·(s₂·…·sₙ) + … + iₙ`.
- **`dimension`** — Detaljerad info per variabel: koder (`category.index`), etiketter (`category.label`), enheter (`category.unit`), metadata (`extension`)
- **`role`** — Vilka variabler som har roll som `time`, `geo` eller `metric`. **Börja analysen här:** `role.metric` visar vad som mäts (kontrollera `dimension.{metric}.category.unit` för enhet/decimaler), `role.time` är tidsdimensionen, `role.geo` är geografi. **`role.geo` är valfritt och beror på installation — SSB sätter det, SCB gör det inte** (verifierat 2026-09-07 på TAB638, TAB6471 och TAB5444, alla med en `Region`-dimension och `role: {time, metric}`). Leta därför efter en geografisk variabel i `id` först; bara när ingen sådan finns gäller data hela landet — fråga inte användaren. Variabler som finns i `id` men inte i `role` är nedbrytningsdimensioner.
- **`status`** — Markerar specialvärden. Nyckeln är index i value-arrayen. Vanliga symboler: `"."` (ej tillämpligt), `".."` (uppgift saknas), `":"` (konfidentiellt). Exakta symboler kan variera mellan leverantörer.
- **`extension`** — Leverantörsspecifik metadata, och den finns på **två nivåer** som inte får förväxlas (verifierat mot SCB 2026-08-30):
  - **Dataset-nivå** (`extension` i roten): `px` (PX-filens nyckelord — `decimals`, `heading`/`stub`, `aggregallowed`, `subject-code`), `contact`, samt `noteMandatory` och `discontinued` när de är satta. `firstPeriod`/`lastPeriod` hör **inte** hemma här — de är fält i `/tables`-träffen, inte i datasetet.
  - **Dimensionsnivå** (`dimension.{var}.extension`): `elimination`, `codelists`, `show`, `refperiod`, `measuringType`, `priceType`, `adjustment`, `alternativeText`, `categoryNoteMandatory`. `measuringType`, `priceType` och `adjustment` avgör hur siffran får presenteras (t.ex. fast pris kontra löpande, säsongrensat eller ej) — läs dem innan du beskriver vad talet betyder.
  - **`elimination` svarar på olika frågor i metadata och data.** I metadata är det kontraktet («får variabeln utelämnas?»). I ett data-svar beskriver det uttaget du fick — `true` bara när värdemängden fortfarande innehåller elimineringsvärdet. Läs aldrig eliminerbarhet ur ett data-svar.
  - **`eliminationValueCode` finns bara i data-svar**, aldrig i metadata (TAB638: saknas på alla sex dimensioner i metadata; `Region=00` i ett data-svar ger `eliminationValueCode: "00"`). Metadata skiljer alltså inte en dimension med egen totalkod (`Region` = `00`, «Riket») från en som summeras i farten (`Kon`) — leta efter «Riket»/«Totalt» i `category.label`, eller kör en provfråga med totalen.

- **`note` + `noteMandatory`** — `note` (roten) är en array av tabellnoter. `extension.noteMandatory` är nycklat på index i den arrayen: `{"0": true, "2": true}` betyder att `note[0]` och `note[2]` ska visas för användaren. Samma mekanik per värde: `dimension.{var}.category.note`, styrt av `extension.categoryNoteMandatory`. Obligatoriska noter följer med data-svaret, så att visa dem kostar inget extra anrop. TAB638 har tre obligatoriska (kommunkodsbyte, regional indelning, registrerat partnerskap).
