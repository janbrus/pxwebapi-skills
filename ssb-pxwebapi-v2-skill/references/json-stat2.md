# json-stat2 — formatreferanse

json-stat2 er et åpent format for statistiske datasett (https://json-stat.org/). Det brukes av PxWebApi v2, men også av andre statistikkleverandører som Eurostat og World Bank. Denne referansen dokumenterer formatet selv — leverandørspesifikke detaljer (publiseringstider, grenser osv.) ligger i `api-details.md`.

---

## Dataset-struktur

Både metadata (`/tables/{id}/metadata`) og data (`/tables/{id}/data`) returneres som json-stat2 Dataset. Eksempel — faktisk respons fra `GET /tables/07459/data?valueCodes[Region]=0301&valueCodes[ContentsCode]=Personer1&valueCodes[Tid]=top(5)` (forkortet):

```json
{
  "version": "2.0",
  "class": "dataset",
  "label": "07459: Befolkning, etter region og år",
  "source": "Statistisk sentralbyrå",
  "updated": "2026-02-25T07:00:00Z",
  "id": ["Region", "ContentsCode", "Tid"],
  "size": [1, 1, 5],
  "dimension": { ... },
  "value": [699827, 709037, 717710, 724290, 728714],
  "role": { "time": ["Tid"], "geo": ["Region"], "metric": ["ContentsCode"] }
}
```

### Nøkkelelementer

- **`id`** — Variabelnavnene i rekkefølge
- **`size`** — Antall verdier per variabel (i samme rekkefølge som `id`)
- **`value`** — Flat array med alle dataverdier lagret i **row-major order** (siste dimensjon i `id` varierer raskest, første varierer saktest — samme konvensjon som C/NumPy). Indeksen beregnes fra `id`, `size` og `dimension.{var}.category.index`: for `size = [s₀, s₁, …, sₙ]` og kategori-indekser `(i₀, i₁, …, iₙ)` er flat-indeksen `i₀·(s₁·s₂·…·sₙ) + i₁·(s₂·…·sₙ) + … + iₙ`.
- **`dimension`** — Detaljert info per variabel med koder (`category.index`), navn (`category.label`), enheter (`category.unit`) og metadata (`extension`)
- **`role`** — Hvilke variabler som har rolle som `time`, `geo` eller `metric`. **Start analyse her:** `role.metric` viser hva som måles (sjekk `dimension.{metric}.category.unit` for enhet/desimaler), `role.time` er tidsdimensjonen, `role.geo` er geografi. Hvis `role.geo` mangler, gjelder dataene typisk hele landet/totalen — ikke spør brukeren. Variabler som er i `id` men ikke i `role` er nedbrytningsdimensjoner.
- **`status`** — Markerer spesielle verdier. Nøkkelen er indeks i value-arrayet, f.eks. `"status": { "3": ".." }` betyr at `value[3]` mangler tallgrunnlag. Feltet utelates når alle verdier er ordinære. Symbolene er leverandørspesifikke — SSBs standardtegn, inkludert de eldre som forekommer i tabeller fra før 2021, står i `troubleshooting.md` under «NULL-verdier i data».
- **`link`** — Standard json-stat2-mekanisme for relaterte ressurser, gruppert per relasjonstype. Kan i likhet med `extension` forekomme på både rot- og variabel-nivå. Hos SSB (kun i metadata-responser, ikke i data-responser): `link.describedby` med URN-er til Klass/VarDok, og `link.related` med ferdige menneskelesbare lenker — på rot-nivå til statistikksiden og «Om statistikken», på variabel-nivå til klassifikasjons-/definisjonssider med label. Se `klass-vardok.md`.
- **`note`** — **Array** med tabellnoter. Finnes på de aller fleste tabeller (11 av 12 stikkprøvde) og skal leses før en serie tolkes: basisårsskifter, rettelser og etterfølgertabeller står her. Noen av dem er obligatoriske å vise — se «Obligatoriske noter» under.
- **`extension`** — Leverandørspesifikk metadata. I json-stat2 kan `extension` forekomme på **to nivåer**:
  - **Dataset/rot-nivå** (`<root>.extension`) — metadata om hele tabellen. Hos SSB (verifisert 2026-08-30): `px`, `contact`, samt `noteMandatory` og `discontinued` når de er satt. **`firstPeriod` og `lastPeriod` ligger ikke her** — de er felter på `/tables`-treffet og `GET /tables/{id}`, ikke i datasettet. Det finnes ikke noe `nextUpdate`-felt.
  - **`extension.px`** — PX-filens nøkkelord: `subject-code`, `subject-area`, `decimals`, `heading`/`stub` (default-pivotering), `contents` (kort tabelltittel, f.eks. "07459: Befolkning,"), `tableid`, `matrix`, `official-statistics`, `copyright`, `language`, `infofile`, `descriptiondefault` — og **`aggregallowed`**, se under.
  - **Variabel-nivå** (`dimension.{var}.extension`) — metadata om den enkelte dimensjonen. Hos SSB: `elimination` (se fellen under), `eliminationValueCode` (kun i data-responser, se under), `show`, `codelists` (tilgjengelige `agg_`/`vs_`-kodelister), `noteMandatory`, `categoryNoteMandatory`. For statistikkvariabelen (`ContentsCode`) i tillegg: `measuringType` (Stock/Flow/Average), `priceType` (Current/Fixed/NotApplicable), `adjustment` (sesongjustering), `basePeriod` (basisperiode for indekser), `refperiod` (referansetidspunkt) og `alternativeText` — alle indeksert per ContentsCode-verdi.

---

## Obligatoriske noter

`extension.noteMandatory` er **nøklet på note-indeks**: `{"1": true}` betyr at `note[1]` skal vises for brukeren. Indeksen varierer per tabell — 14700 har `{"1": true}`, 14710 har `{"0": true}`, 03013 har `{"2": true, "3": true}` — så slå den opp, ikke anta den første noten.

Dette treffer skillens egne flaggskip-eksempler. KPI-tabellene **14700**, **14710** og **03013** har alle obligatorisk note, og noten på 14700 og 14710 sier ordrett:

> «F.o.m. 2026 er referanseår 2025=100. Endringstall beregnet fra serier med 2025=100 kan avvike fra endringstall publisert før 2026 med annet referanseår.»

Steg 5 ber deg regne ut endringstall og merke dem som dine egne. Dette er SSBs eget varsel om at nettopp de endringstallene kan avvike fra publiserte tall — det hører med i svaret. Noten følger med i **data**-responsen også, så det koster ingen ekstra kall å vise den.

Tilsvarende finnes **`category.note` per verdi**, styrt av `categoryNoteMandatory`. På 07459 bærer `Region` kommuneflyttinger («1.1.2019 ble kommunen 1567 Rindal flyttet fra Møre og Romsdal til Trøndelag …») — altså presis dokumentasjon av akkurat det `troubleshooting.md` advarer om generelt under «Data ser rare ut over tid».

---

## `aggregallowed` — kan tabellen summeres i det hele tatt?

`extension.px.aggregallowed` sier om summering av tabellen er meningsfull. **8 av 12 stikkprøvde tabeller har `false`** — inkludert 14700, 14710, 03013 og 07221, altså fire av skillens egne eksempler. Det er som forventet: å legge sammen indekspoeng gir tull.

**Viktig nyanse, verifisert:** `false` er et tolkningssignal, **ikke en teknisk sperre**. Det blokkerer ikke kodelister og gir ingen feilmelding i v2 hos SSB — 14700 tilbyr sju `agg_`/`vs_`-kodelister og svarer HTTP 200 på dem. (Den strengere påstanden om at `agg:` da ikke virker gjelder v1-installasjoner, ikke SSB på v2.) Bruk feltet til å vurdere om en sum er meningsfull, ikke til å forutsi en feil.

---

## Felle: `elimination` betyr forskjellige ting i metadata og data

Verifisert 2026-08-30. `dimension.{var}.extension.elimination` svarer på **ulike spørsmål** i de to responstypene:

- **I en metadata-respons** er det kontrakten: *kan denne variabelen utelates fra en spørring?* Det er denne du vil ha.
- **I en data-respons** beskriver det uttrekket du fikk: `true` bare når verdimengden som kom tilbake fortsatt inneholder elimineringsverdien, ellers `false`. Velg én vanlig kommune, og `Region` leser `false`. Bruk en kodeliste, og den leser `false`. Ingen av delene sier noe om hvorvidt variabelen er eliminerbar.

**Les aldri eliminerbarhet av en data-respons.** Hent metadata på nytt.

`eliminationValueCode` går motsatt vei, og det forenkler ikke slik man skulle tro. PX har to elimineringsformer:

- `ELIMINATION=YES` — det finnes ingen totalverdi; API-et summerer på flyet når du utelater variabelen. `Kjonn` i 07459 er slik: kategoriene er kun `{Kvinner, Menn}`.
- `ELIMINATION("<verdi>")` — en forhåndsdefinert totalkode finnes allerede i verdimengden. `Region` i 07459 er slik: kode `0` = «Hele landet».

**I metadata ser begge like ut** — bare `elimination: true`. En sveip over 50 SSB-tabeller fant `eliminationValueCode` på null dimensjoner i metadata. Feltet dukker opp i en **data**-respons som inkluderer totalen, som `"eliminationValueCode": "0"`. Skal du vite hvilken form en dimensjon har, er den proben veien — eller se etter en «Hele landet»/«I alt»-oppføring i `category.label`.

---

## Det json-stat2 ikke bærer

- **Tidsfrekvens.** PX deklarerer den eksplisitt (`TIMEVAL(...)=TLIST(A1|H1|Q1|M1|W1)`), men json-stat2 har ikke noe felt for det. `role.time` navngir tidsdimensjonen og sier ingenting om frekvensen. Eneste kilde i v2 er **`timeUnit` på `/tables`-treffet, utenfor json-stat2-dokumentet**. Relevant når et uttrekk sendes videre til `ssb-chart-skill`, som må vite om aksen er måned eller kvartal — bær `timeUnit` med deg selv, datasettet gjør det ikke.
- **Hvilken aggregering som ga tallet.** En utelatt dimensjon forsvinner helt fra `id` og `dimension`; datasettet registrerer ikke at den ble summert bort, eller over hva.
- **Hvilken kodeliste koden kom fra.** Verifisert: et uttrekk med `codelist[Region]=agg_Fylker2024` kommer tilbake med `Region.extension = {"elimination": false, "show": "code_value"}` — ingen `codelists`, ingenting som navngir grupperingen. Det gjør `agg_KommFylker` og `agg_KommSummer` umulige å skille fra responsen alene, selv om de gir ulike tall. Oppgi kodelisten i svaret; responsen gjør det ikke.

---

## Verktøy / biblioteker

**pyjstat** (https://pypi.org/project/pyjstat/) — Python-bibliotek for å lese og skrive json-stat. Konverterer mellom json-stat(2) og pandas DataFrame, nyttig for å ta et SSB-uttrekk videre til analyse i Python.

**JSON-stat Toolkit** (https://jsonstat.com/) — referanseimplementasjonen i JavaScript, med **JSON-stat Explorer** (http://jsonstat.com/explorer/) for å bla i et datasett interaktivt — nyttig når du vil forstå `id`/`size`/`value`-indekseringen på en konkret respons. Toolkiten har også kommandolinjeverktøy (https://github.com/jsonstat/conv/, krever node.js): `jsonstat2csv` (bedre tilpasset CSV enn API-ets eget csv-format), `jsonstat2arrow`, `jsonstat2array`/`jsonstat2arrobj`/`jsonstat2objarr` (ulike JS-strukturer), `jsonstatdice` (lag et nytt json-stat-datasett fra et utsnitt), `csv2jsonstat` og `sdmx2jsonstat` (OECD, UN, IMF → json-stat). Eksempler: https://observablehq.com/@jsonstat.

For R finnes PxWebApiData, en API-klient som henter PxWeb-data direkte inn i R — se README.
