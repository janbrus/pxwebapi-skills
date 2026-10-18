# json-stat2 — formatreferens

json-stat2 är ett öppet format för statistiska dataset (https://json-stat.org/). PxWebApi v2, Eurostat och World Bank använder det, men Eurostat skickar `value` och `status` som objekt nycklade på position, inte som listor. Filen beskriver formatet så som SCB levererar det. Gränser och rate limit står i `SKILL.md`.

**Innehåll**

1. Så läser du ett uttag
2. Dataset-struktur och indexering
3. Fälten i datasetet
4. `dimension` och `extension` per variabel
5. `extension` på rotnivå och `extension.px`
6. `status`, `note` och `link`
7. Det json-stat2 inte bär
8. Verktyg

---

## Så läser du ett uttag

1. **Leta upp geografin i `id`.** SCB sätter inte `role.geo`, bara `metric` (det som mäts) och `time`. Geografin är en variabel i `id`, oftast `Region`. Bara när ingen sådan finns gäller talen hela Sverige. Fråga inte användaren. (SKILL.md Steg 3)
2. **`value` är row-major:** sista dimensionen i `id` varierar snabbast. Positionen är summan av `category.index` × stride, där stride är produkten av `size` för de senare dimensionerna. Iterera över `id`, inte över `Object.keys(dimension)`. Anta aldrig att tiden är sorterad, och filtrera aldrig bort `null`. (Se «Dataset-struktur och indexering»)
3. **Läs `value` och `status` var för sig.** Är cellen `null`, visa symbolen, aldrig 0. Har den ett tal, visa talet med flaggan. (SKILL.md Steg 5, och `status`)
4. **Visa obligatoriska noter på alla tre nivåerna:** tabellen (`extension.noteMandatory`), variabeln (`dimension.{var}.extension.noteMandatory`) och värdet (`dimension.{var}.extension.categoryNoteMandatory`). (SKILL.md Steg 5, och `note`)
5. **Läs `elimination` bara från metadata.** Totalkoden hittar du via `category.label`, eller som `eliminationValueCode` i ett data-svar. (Se `elimination`)
6. **Står `aggregallowed: false`, ska talen varken summeras eller medelvärdesberäknas.** Gör du det ändå, märk det. Fältet stoppar ingen fråga. (Se `extension.px`)
7. **Ange själv kodlistan, de utelämnade dimensionerna och `timeUnit`.** Svaret registrerar inget av dem. (SKILL.md Steg 5, och «Det json-stat2 inte bär»)

---

## Dataset-struktur och indexering

Både metadata (`/tables/{id}/metadata`) och data (`/tables/{id}/data`) är ett json-stat2 Dataset. Schematiskt:

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
  "role": { "time": ["Tid"], "metric": ["ContentsCode"] },
  "status": { "3": ".." }
}
```

`value` är row-major, som i C och NumPy. För `size = [s₀, s₁, …, sₙ]` och kategoriindex `(i₀, i₁, …, iₙ)` är positionen `i₀·(s₁·…·sₙ) + i₁·(s₂·…·sₙ) + … + iₙ`. Ovan varierar bara `Tid`, så ordningen kan inte bli fel. Med två regioner blir den synlig:

```
GET /tables/TAB6471/data?valueCodes[Region]=0180,1480&valueCodes[Alder]=TotSA&valueCodes[ContentsCode]=000007SF&valueCodes[Tid]=2026M05,2026M06,2026M07
```

Svaret har `id = ["Region", "Alder", "ContentsCode", "Tid"]` och `size = [2, 1, 1, 3]`, med `Region` `{"0180": 0, "1480": 1}`.

Stride: `Region` 1·1·3 = 3, `Alder` 3, `ContentsCode` 3, `Tid` 1.

| Position i `value` | `Region` | `Tid` |
|---|---|---|
| 0, 1, 2 | `0180` Stockholm | `2026M05`, `2026M06`, `2026M07` |
| 3, 4, 5 | `1480` Göteborg | `2026M05`, `2026M06`, `2026M07` |

Göteborg (index 1) i `2026M07` (index 2) är `1·3 + 0·3 + 0·3 + 2·1 = 5`, alltså `value[5]`. En dimension med storlek 1 bidrar alltid med 0.

`category.index` följer ordningen i frågan. `valueCodes[Tid]=2026M07,2026M05,2026M06` ger `{"2026M07": 0, "2026M05": 1, "2026M06": 2}`. Hos SCB står nycklarna i `dimension` i samma ordning som `id`, men specifikationen lovar det inte.

---

## Fälten i datasetet

| Fält | Vad det är |
|---|---|
| `id`, `size` | Variablerna i den ordning som styr indexeringen, och antal värden per variabel |
| `value` | Talen som en platt lista, med `null` där talet saknas |
| `status` | Flaggor per cell, nycklade på positionen i `value`. Saknas när ingen cell har flagga |
| `dimension` | Per variabel: koder, namn, enhet, noter, `extension` och `link` |
| `role` | `time` och `metric`. SCB sätter inte `geo`. De andra variablerna i `id` är nedbrytningar |
| `note` | Tabellnoter |
| `extension`, `link` | SCB:s egna fält och länkar, se nedan |
| `label`, `source`, `updated` | Titel, källa och senaste uppdatering |

---

## `dimension` och `extension` per variabel

`dimension.{var}` har `category.index` (kod → position) och `category.label` (kod → namn). `ContentsCode` har också `category.unit` med enhet och decimaler per statistikvariabel, t.ex. `{"000007SF": {"base": "antal", "decimals": 0}}` i TAB6471. Noter står per variabel (`note`, en lista) och per värde (`category.note`, värdekod → lista). I TAB638 har `Region` `0140` en not om att Nykvarn bildades av delar av Södertälje 1999.

`dimension.{var}.extension` har dessa fält. PX-nyckelordet fältet kommer från står inom parentes:

| Fält | Betydelse |
|---|---|
| `elimination` (`ELIMINATION`) | Om variabeln får utelämnas. Bara metadata svarar på det, se nedan |
| `eliminationValueCode` (`ELIMINATION`) | Totalkoden. Står bara i ett data-svar som har totalen med, t.ex. `"00"` för `Region` |
| `show` (`PRESTEXT`) | `code`, `value` eller `code_value` |
| `codelists` | Kodlistorna (`agg_`/`vs_`) tabellen erbjuder för variabeln |
| `noteMandatory` (`NOTEX`) | Vilka av variabelns noter som ska visas, nycklat på index i `dimension.{var}.note`. TAB6471 `Alder`: `{"0": true}` |
| `categoryNoteMandatory` (`VALUENOTEX`) | Vilka värdenoter som ska visas: värdekod → index i `category.note`. TAB638 `Region`: `{"0140": {"1": true}}` |
| `measuringType` (`STOCKFA`) | `Stock`, `Flow`, `Average` eller `Other` |
| `priceType` (`CFPRICES`) | `Current`, `Fixed` eller `NotApplicable` |
| `adjustment` (`DAYADJ`, `SEASADJ`) | `SesOnly` (säsongrensat), `WorkAndSes` (kalender- och säsongrensat) eller `None` |
| `basePeriod` (`BASEPERIOD`) | Basperioden för ett index, t.ex. `2020` i TAB6596 |
| `refperiod` (`REFPERIOD`) | Referenstidpunkten |
| `alternativeText` | Ett längre namn, t.ex. «KPI, fastställda tal» |

De sex sista står bara på `ContentsCode`, med ett värde per statistikvariabel. `noteMandatory` och `categoryNoteMandatory` står bara på variabler som har obligatoriska noter.

### `elimination`

I metadata svarar fältet på om variabeln får utelämnas. I ett data-svar beskriver det uttaget: `true` bara när värdena du fick innehåller elimineringsvärdet. Väljer du en kommun eller använder en kodlista, står det `false` om `Region`, fast variabeln får utelämnas.

PX har två former. `ELIMINATION("<variabel>")=YES` betyder att det inte finns något totalvärde, och att API:et summerar när du utelämnar variabeln (`Kon` i TAB638, som bara har `1` och `2`). `ELIMINATION("<variabel>")="<värdenamn>"` betyder att totalen finns som värde (`Region`, `00` = «Riket»). Formen hör till tabellen, inte till variabelnamnet: i TAB6471 har `Kon` totalkoden `TotSa`. I metadata är båda `elimination: true`, utan `eliminationValueCode`. Det fältet kommer först i ett data-svar som har totalen med.

---

## `extension` på rotnivå och `extension.px`

Rot-`extension` har `contact` (kontaktpersonerna) och `px`, och `noteMandatory` (`NOTEX`) när tabellen har obligatoriska noter. `discontinued` är aldrig satt: fältet saknas i metadata och är `null` i data-svaret.

`extension.px` har samma 14 nycklar i SCB:s tabeller. Varje nyckel är ett nyckelord i PX-filen tabellen är gjord från, med små bokstäver (`AGGREGALLOWED` blir `aggregallowed`). SCB beskriver formatet på https://www.scb.se/en/services/statistical-programs-for-px-files/px-file-format/.

| Nyckel | Betydelse |
|---|---|
| `contents` | Kort titel, t.ex. `"Folkmängden per månad"` (TAB6471) |
| `heading`, `stub` | Standardpivoteringen: variablerna i kolumnhuvudet och i förspalten |
| `decimals` | Antal decimaler i tabellen |
| `aggregallowed` | `false` om talen inte får summeras. Sätts också för antal: TAB6471 (folkmängd per månad, med CKM-brus) har `false`, TAB638 `true`. En tolkningssignal, ingen spärr |
| `tableid`, `matrix` | Tabell-ID:t |
| `subject-code`, `subject-area` | Ämnet, t.ex. `BE` och «Befolkning» |
| `infofile` | Produktkoden, t.ex. `BE0101`. Samma kod som i `link.related` |
| `language` | Språket, som följer `lang` |
| `official-statistics`, `copyright`, `descriptiondefault` | Flaggor från PX-filen: officiell statistik, upphovsrätt, och om beskrivningen visas i stället för titeln |

---

## `status`, `note` och `link`

### `status`

En datasymbol (`DATASYMBOL1`–`6`, `DATASYMBOLSUM`, `DATASYMBOLNIL`) ger `null` i `value` och symbolen i `status`. `{"3": ".."}` betyder att `value[3]` saknas, och `..` säger varför. En datanot (`DATANOTECELL`) behåller talet, och symbolen är då en flagga. Hos SCB har bara `..` på `null` observerats; hos SSB förekommer tal med flagga (`*` = preliminärt tal). Symbolerna: `.` (ej tillämpligt), `..` (uppgift saknas), `:` (konfidentiellt).

### `note`

Obligatoriska noter finns på tre nivåer, och alla tre följer med data-svaret:

| Nivå | Noterna | Vilka som ska visas |
|---|---|---|
| Tabell | `note` (rot, lista) | `extension.noteMandatory`, nycklat på index: `{"0": true, "2": true}` betyder `note[0]` och `note[2]` |
| Variabel | `dimension.{var}.note` (lista) | `dimension.{var}.extension.noteMandatory`, nycklat på index. TAB6471 `Alder` `{"0": true}` |
| Värde | `dimension.{var}.category.note` (värdekod → lista) | `dimension.{var}.extension.categoryNoteMandatory`, värdekod → index. TAB638 `Region` `{"0140": {"1": true}}` betyder `category.note["0140"][1]` |

Noter per värde följer bara med för de värden du har valt. TAB6471 har fyra obligatoriska tabellnoter och en på `Alder`.

### `link`

`link.related` på rotnivå pekar på statistiksidan (`https://www.scb.se/BE0101`, med `metaid` `PRODUCTCODE:BE0101`). Det står i både metadata och data-svaret. `link.describedby` per variabel har klartext, t.ex. `{"Kon": "Kön"}` i TAB638, inte en URN.

---

## Det json-stat2 inte bär

- **Tidsfrekvens.** PX-filen har den (`TIMEVAL(...)=TLIST(A1|H1|Q1|M1|W1)`), json-stat2 har inget fält för den. `role.time` säger bara vilken dimension som är tid. Enda källan är `timeUnit` på `/tables`-träffen.
- **`firstPeriod`, `lastPeriod` och `discontinued`.** De står bara på `/tables`-träffen och i `GET /tables/{id}`. `discontinued` står bara där när den är `true`, och SCB fryser ofta en tabell utan att sätta den (SKILL.md Steg 2).
- **Aggregeringen.** En utelämnad dimension försvinner ur `id` och `dimension`, utan spår av att den summerades bort.
- **Kodlistan.** Med `codelist[Region]=vs_CKM02Län` blir `Region.extension` `{"elimination": false, "show": "code_value"}`, utan namnet på listan.

---

## Verktyg

- **pyjstat** (https://pypi.org/project/pyjstat/): gör om json-stat till en pandas DataFrame och tillbaka.
- **JSON-stat Toolkit** (https://jsonstat.com/): referensimplementationen i JavaScript.
- **Idescats JSON-stat-skill** (https://www.idescat.cat/dev/api/taules/jsonstat/SKILL.md, CC BY 4.0): en kort, leverantörsneutral guide till att läsa ett dataset.
