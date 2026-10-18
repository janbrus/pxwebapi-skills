# json-stat2 — formatreferanse

json-stat2 er et åpent format for statistiske datasett (https://json-stat.org/). PxWebApi v2, Eurostat og World Bank bruker det, men Eurostat sender `value` og `status` som objekter nøklet på posisjon, ikke som lister. Fila beskriver formatet slik SSB leverer det. Driftsinformasjon står i `api-details.md`.

**Innhold**

1. Slik leser du et uttrekk
2. Dataset-struktur og indeksering
3. Feltene i datasettet
4. `dimension` og `extension` per variabel
5. `extension` på rotnivå og `extension.px`
6. `status`, `note` og `link`
7. Det json-stat2 ikke bærer
8. Verktøy

---

## Slik leser du et uttrekk

1. **Start med `role`.** `metric` er det som måles, `time` er tiden og `geo` geografien. Mangler `role.geo`, gjelder tallene hele landet. Ikke spør brukeren. (SKILL.md Steg 3)
2. **`value` er row-major:** siste dimensjon i `id` varierer raskest. Posisjonen er summen av `category.index` × stride, der stride er produktet av `size` for de senere dimensjonene. Iterer over `id`, ikke over `Object.keys(dimension)`. Anta aldri at tiden er sortert, og filtrer aldri bort `null`. (Se «Dataset-struktur og indeksering»)
3. **Les `value` og `status` hver for seg.** Er cellen `null`, vis symbolet, aldri 0. Har den et tall, vis tallet med flagget. (SKILL.md Steg 5, og `status`)
4. **Vis obligatoriske noter.** `extension.noteMandatory` sier hvilke. (SKILL.md Dataintegritet, og `note`)
5. **Les `elimination` bare fra metadata.** Totalkoden finner du via `category.label`, eller som `eliminationValueCode` i en data-respons. (Se `elimination`)
6. **Står `aggregallowed: false`, skal tallene verken summeres eller gjennomsnittes.** Gjør du det likevel, merk det. Feltet stopper ingen spørring. (Se `extension.px`)
7. **Oppgi selv kodelisten, de utelatte dimensjonene og `timeUnit`**, og send `timeUnit` videre til `ssb-chart-skill`. (SKILL.md Steg 5, og «Det json-stat2 ikke bærer»)

---

## Dataset-struktur og indeksering

Både metadata (`/tables/{id}/metadata`) og data (`/tables/{id}/data`) er et json-stat2 Dataset:

```
GET /tables/07459/data?valueCodes[Region]=0301&valueCodes[ContentsCode]=Personer1&valueCodes[Tid]=top(5)
```

```json
{
  "label": "07459: Befolkning, etter region og år",
  "updated": "2026-02-25T07:00:00Z",
  "id": ["Region", "ContentsCode", "Tid"],
  "size": [1, 1, 5],
  "dimension": { ... },
  "value": [699827, 709037, 717710, 724290, 728714],
  "role": { "time": ["Tid"], "geo": ["Region"], "metric": ["ContentsCode"] }
}
```

`value` er row-major, som i C og NumPy. For `size = [s₀, s₁, …, sₙ]` og kategoriindekser `(i₀, i₁, …, iₙ)` er posisjonen `i₀·(s₁·…·sₙ) + i₁·(s₂·…·sₙ) + … + iₙ`. Over varierer bare `Tid`, så rekkefølgen kan ikke gå galt. Med to regioner blir den synlig:

```
GET /tables/07459/data?valueCodes[Region]=0301,4601&valueCodes[ContentsCode]=Personer1&valueCodes[Tid]=2024,2025,2026
```

```json
{
  "id": ["Region", "ContentsCode", "Tid"],
  "size": [2, 1, 3],
  "dimension": {
    "Region":       { "category": { "index": { "0301": 0, "4601": 1 } } },
    "ContentsCode": { "category": { "index": { "Personer1": 0 } } },
    "Tid":          { "category": { "index": { "2024": 0, "2025": 1, "2026": 2 } } }
  },
  "value": [717710, 724290, 728714, 291940, 293709, 294860]
}
```

Stride: `Region` 1·3 = 3, `ContentsCode` 3, `Tid` 1. Bergen (`4601`, indeks 1) i 2026 (indeks 2) er `1·3 + 0·3 + 2·1 = 5`, altså `value[5]`. En dimensjon med størrelse 1 bidrar alltid med 0.

`category.index` følger rekkefølgen i spørringen. `valueCodes[Tid]=2026,2024,2025` gir `{"2026": 0, "2024": 1, "2025": 2}`, mens `top(n)` og `from(x)` gir stigende rekkefølge. Hos SSB står nøklene i `dimension` i samme rekkefølge som `id`, men spesifikasjonen lover det ikke.

---

## Feltene i datasettet

| Felt | Hva det er |
|---|---|
| `id`, `size` | Variablene i den rekkefølgen som styrer indekseringen, og antall verdier per variabel |
| `value` | Tallene som én flat liste, med `null` der tallet mangler |
| `status` | Flagg per celle, nøklet på posisjonen i `value`. Mangler når ingen celle har flagg |
| `dimension` | Per variabel: koder, navn, enhet, noter, `extension` og `link` |
| `role` | `time`, `geo` og `metric`. De andre variablene i `id` er nedbrytninger |
| `note` | Tabellnoter: basisårsskifter, rettelser, etterfølgertabeller |
| `extension`, `link` | SSBs egne felter og lenker, se under |
| `label`, `source`, `updated` | Tittel, kilde og siste oppdatering |

---

## `dimension` og `extension` per variabel

`dimension.{var}` har `category.index` (kode → posisjon) og `category.label` (kode → navn). `ContentsCode` har også `category.unit` med enhet og desimaler per statistikkvariabel, f.eks. `{"Personer1": {"base": "antall", "decimals": 0}}`. Noter står per variabel (`note`) og per verdi (`category.note`). På 07459 har fylkene `15` og `50` en note om at Rindal ble flyttet til Trøndelag i 2019. Det er nettopp det `troubleshooting.md` advarer om under «Data ser "feil ut" over tid».

`dimension.{var}.extension` har disse feltene. PX-nøkkelordet feltet kommer fra, står i parentes:

| Felt | Betydning |
|---|---|
| `elimination` (`ELIMINATION`) | Om variabelen kan utelates. Bare metadata svarer på det, se under |
| `eliminationValueCode` (`ELIMINATION`) | Totalkoden. Står bare i en data-respons som har totalen med |
| `show` (`PRESTEXT`) | `code`, `value` eller `code_value` |
| `codelists` | Kodelistene (`agg_`/`vs_`) tabellen tilbyr for variabelen |
| `measuringType` (`STOCKFA`) | `Stock`, `Flow`, `Average` eller `Other` |
| `priceType` (`CFPRICES`) | `Current`, `Fixed` eller `NotApplicable` |
| `adjustment` (`DAYADJ`, `SEASADJ`) | `SesOnly` er sesongjustert (07221), `WorkAndSes` kalender- og sesongjustert (09190), `None` ujustert |
| `basePeriod` (`BASEPERIOD`) | Basisperioden for en indeks, f.eks. `2025` i 14700 |
| `refperiod` (`REFPERIOD`) | Referansetidspunktet, f.eks. `1.1.` i 07459 |
| `alternativeText` | Et lengre navn, f.eks. «Konsumprisindeks (2025=100)» |

De seks siste står bare på `ContentsCode`, med én verdi per statistikkvariabel. Har tabellen en egen justeringsdimensjon, er det den som sier hvilken serie du fikk: 13760 har `adjustment: WorkAndSes` også når du velger `Justering=IS` (ikke sesongjustert).

### `elimination`

I metadata svarer feltet på om variabelen kan utelates. I en data-respons beskriver det uttrekket: `true` bare når verdiene du fikk, inneholder elimineringsverdien. Velger du én kommune eller bruker en kodeliste, står det `false` om `Region`, selv om variabelen kan utelates.

PX har to former. `ELIMINATION("<variabel>")=YES` betyr at det ikke finnes noen totalverdi, og at API-et summerer når du utelater variabelen (`Kjonn` i 07459). `ELIMINATION("<variabel>")="<verdinavn>"` betyr at totalen finnes som verdi (`Region` i 07459, `0` = «Hele landet»). I metadata er begge `elimination: true`, uten `eliminationValueCode`. Det feltet kommer først i en data-respons som har totalen med, som `"eliminationValueCode": "0"`.

---

## `extension` på rotnivå og `extension.px`

Rot-`extension` har `contact` (kontaktpersonene) og `px`, og `noteMandatory` (`NOTEX`) når tabellen har obligatoriske noter. `discontinued` er aldri satt: feltet mangler i metadata og er `null` i data-responsen, også for den avsluttede 03013.

`extension.px` har de samme 14 nøklene i alle SSB-tabeller. Hver nøkkel er et nøkkelord i PX-filen tabellen er lagd fra, med små bokstaver (`AGGREGALLOWED` blir `aggregallowed`). SCB beskriver formatet på https://www.scb.se/en/services/statistical-programs-for-px-files/px-file-format/.

| Nøkkel | Betydning |
|---|---|
| `contents` | Kort tittel, f.eks. `"07459: Befolkning,"`. Grunnlaget for tittelen i Steg 5 |
| `heading`, `stub` | Standardpivoteringen: variablene i kolonnehodet og i forspalten |
| `decimals` | Antall desimaler i tabellen |
| `aggregallowed` | `false` for tall som ikke kan summeres, som indekser og gjennomsnitt (14700, 14710, 03013, 07221). Et tolkningssignal, ingen sperre: kodelistene svarer 200 likevel |
| `tableid`, `matrix` | Tabellnummeret |
| `subject-code`, `subject-area` | Emnet, f.eks. `be` og «Befolkning» |
| `language` | Språket, som følger `lang` |
| `official-statistics`, `copyright`, `descriptiondefault`, `infofile` | Like i alle SSB-tabeller, også KOSTRA: `true`, `false`, `false` og `"None"` |

---

## `status`, `note` og `link`

### `status`

Et datasymbol (`DATASYMBOL1`–`6`, `DATASYMBOLSUM`, `DATASYMBOLNIL`) gir `null` i `value` og symbolet i `status`. `{"3": ".."}` betyr at `value[3]` mangler, og `..` sier hvorfor. En datanote (`DATANOTECELL`) beholder tallet, og symbolet er da et flagg. Her har 2023 og 2024 både tall og `*` (foreløpig tall), forklart i tabellens `note`:

https://data.ssb.no/api/pxwebapi/v2/tables/09842/data?valueCodes[ContentsCode]=BNP&valueCodes[Tid]=2022,2023,2024

SSBs standardtegn, også de eldre fra før 2021, står i `troubleshooting.md` under «NULL-verdier i data».

### `note`

`extension.noteMandatory` er nøklet på indeksen i `note`: `{"1": true}` (14700) betyr at `note[1]` skal vises. Indeksen varierer, 14710 har `{"0": true}` og 03013 `{"2": true, "3": true}`, så slå den opp. Noten følger med i data-responsen.

Noter per variabel og per verdi er ikke obligatoriske hos SSB. Spesifikasjonen har `noteMandatory` og `categoryNoteMandatory` i `dimension.{var}.extension` til det, men SSB setter dem ikke.

### `link`

`link.related` har ferdige lenker: på rotnivå til statistikksiden og «Om statistikken», per variabel til sidene om klassifikasjoner og definisjoner. Det står bare i metadata. `link.describedby` per variabel har URN-er til Klass og VarDok, også i data-responsen. Se `klass-vardok.md`.

---

## Det json-stat2 ikke bærer

- **Tidsfrekvens.** PX-filen har den (`TIMEVAL(...)=TLIST(A1|H1|Q1|M1|W1)`), json-stat2 har ikke noe felt for den. `role.time` sier bare hvilken dimensjon som er tid. Eneste kilde er `timeUnit` på `/tables`-treffet.
- **`firstPeriod`, `lastPeriod` og `discontinued`.** De står bare på `/tables`-treffet og i `GET /tables/{id}`. Det finnes ikke noe `nextUpdate`.
- **Aggregeringen.** En utelatt dimensjon forsvinner fra `id` og `dimension`, uten spor av at den ble summert bort.
- **Kodelisten.** Med `codelist[Region]=agg_Fylker2024` blir `Region.extension` `{"elimination": false, "show": "code_value"}`, uten navnet på lista. `agg_KommFylker` og `agg_KommSummer` gir ulike tall, og responsen skiller dem ikke.

---

## Verktøy

- **pyjstat** (https://pypi.org/project/pyjstat/): gjør json-stat om til pandas DataFrame og tilbake.
- **JSON-stat Toolkit** (https://jsonstat.com/): referanseimplementasjonen i JavaScript. **JSON-stat Explorer** (http://jsonstat.com/explorer/) viser indekseringen på en konkret respons.
- **PxWebApiData** (https://cran.r-project.org/package=PxWebApiData): SSBs R-pakke for PxWeb-data.
- **Idescats JSON-stat-skill** (https://www.idescat.cat/dev/api/taules/jsonstat/SKILL.md, CC BY 4.0): en kort, leverandørnøytral veiledning i å lese et datasett.
