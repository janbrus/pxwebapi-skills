# Eval-scenarier — generic-pxweb-v1-skill

Seks scenarier som treffer nøyaktig de avsnittene v0.12.0 kortet ned, siden det er
der beslutningene bor: `?config`-regelen (Steg 1), elimination (Steg 4), hyfenerte
formatnavn (Steg 4) og «les variabelkodene, aldri anta dem» (Steg 3) — det siste
dekket to ganger, av et ikke-nordisk oppsett (Finland) og av en norsk installasjon
som *ikke* følger SSBs konvensjoner (Oslo kommune).

Kjøres via `skill-creator` ved større endringer i `SKILL.md` eller `references/`.
Vedlikeholder-internt — ikke med i distribusjons-zip eller README-filtreet.

**Fasit beskriver form og valg, aldri en konkret tallverdi.** Et scenario som
asserterer et bestemt folketall belønner et tall gjengitt fra hukommelsen framfor et
hentet tall — stikk i strid med skillens egen integritetsregel. Samme grunn til at
ingen `?config`-verdi står som fasit under: verdiene endres, feltnavnene ikke.

**Kjør dem som faktiske kjøringer**, ikke som gjennomlesning. En modell som *leser*
SKILL.md svarer riktig på alt her; poenget er hva den gjør når den har verktøyene.

Endepunkter og responsformer verifisert live 2026-09-03. Feiler et scenario, sjekk
først om installasjonen har endret koder eller struktur før du antar at skillen er
problemet — Finlands geografivariabel bærer en klassifikasjonsdato i selve koden og
skifter navn mellom tabellversjoner.

---

## 1. «Hvor mange bor i Finland?» — les kodene, ikke konvensjonen

Det ikke-SSB/SCB-scenarioet. CLAUDE.md krever minst ett eksempel som beviser at
`Region`/`ContentsCode`/`Tid` ikke er universelle; dette er det.

- **Installasjon:** Statistics Finland, `https://pxdata.stat.fi/PXWeb/api/v1/en/StatFin/11ra.px`
- **Sekvens:** `GET …/en/?config` → GET tabell-URL (metadata) → POST samme URL
- **Nøkkelvalg:** variabelkodene er `alue_23_20260101`, `contentscode` og `timeperiod_y`,
  lest ordrett fra `variables[].code`. Landstotalen er `SSS`. `timeperiod_y` tar
  `{"filter":"top","values":["3"]}`
- **Suksess:**
  - Modellen henter kodene fra metadata i stedet for å sende `Region`/`ContentsCode`/`Tid`
  - `"response":{"format":"json-stat2"}` er satt eksplisitt — ikke utelatt (default er PX)
  - Svaret oppgir enhet. Den finnes kun i *data*-responsen
    (`dimension.contentscode.category.unit`), ikke i metadata
  - Kilde oppgitt med tabell-id
- **Feilmodus å fange:** koder gjettet fra nordisk konvensjon → 400 med
  `The request for variable '…' has an error`, eller — verre — at modellen bytter til
  en SSB-tabell fordi Finland «ikke virket»

## 2. `?config` før alt annet — mot en installasjon med avvikende grenser

- **Oppgave:** «Hent hele befolkningstabellen for alle finske kommuner og alle år»
  (et uttrekk som er stort nok til at grensen betyr noe)
- **Suksess:**
  - Modellen kaller `GET {host}/{APINAME}/{APIVERSION}/{LANGUAGE}/?config` **først**, og
    leser `maxCells`/`maxValues`/`maxCalls` derfra
  - Den bruker verdiene den fikk tilbake — ikke tall fra Statistikkfinlands egen
    hjelpeside, ikke fra R-pakka `pxweb`, og ikke fra et annet byrå den nettopp har
    snakket med. Alle tre avviker fra `?config` i praksis
  - Uttrekket deles opp eller avgrenses hvis produktet av valgte verdier overstiger
    `maxCells`; 403 tolkes som cellegrense, ikke som «tabellen finnes ikke»
- **Feilmodus å fange:** `/config` som *sti* i stedet for `?config` som spørringsparameter.
  Stiformen gir 400, og det er nettopp den feilen som en gang fikk denne skillen til å
  påstå at v1 ikke har noe config-endepunkt

## 3. Elimination — sier svaret fra om hva som forsvant?

- **Installasjon:** samme finske tabell
- **Oppgave:** «Hva er folketallet i Finland totalt?» — altså uten geografisk oppdeling
- **Nøkkelvalg:** `alue_23_20260101` har `elimination: true` og utelates fra `"query"`
- **Suksess:**
  - Responsen kommer tilbake **uten** geografidimensjonen i `id` og `dimension` — ikke
    med størrelse 1. Modellen skal si eksplisitt at tallet gjelder hele landet, siden
    responsen ikke registrerer det selv
  - Motprøven i samme scenario: utelates `contentscode` i stedet (`elimination`
    fraværende → `false`), kommer **alle** dens verdier tilbake. Modellen skal forutse
    det, ikke oppdage det ved at svaret plutselig har titalls rader
- **Feilmodus å fange:** at en utelatt variabel antas summert uansett flagg. Det er
  regel 3 som biter, og den biter stille

## 4. Hyfenert formatnavn

- **Oppgave:** hvilket som helst uttrekk der modellen selv velger format
- **Suksess:** `json-stat2`, ikke spesifikasjonens `jsonstat2`. Verifisert 2026-09-03:
  den uhyfenerte formen gir 400 også hos Statistikkfinland, ikke bare hos SSB og SCB
- **Suksess (utvidet):** `"response"` settes alltid eksplisitt. Merk at fasiten her
  *ikke* er «default er PX» — det var påstanden dette scenarioet felte da det ble kjørt
  første gang. Målt på alle sju verifiserte installasjoner 2026-09-04 finnes det **tre**
  defaults: json-stat2 (SSB, Finland, Estland), PX (SCB, Grønland) og PX-JSON
  (Færøyene, Island). Suksesskriteriet er at modellen ikke *stoler* på defaulten i noen
  retning — ikke at den kjenner tabellen over
- **Feilmodus å fange, nummer to:** at modellen sjekker «fikk jeg JSON?» og går videre.
  PX-JSON *er* JSON, bare uten `value`, `dimension`, `id` og `role` — så den sjekken
  passerer på Færøyene og Island og feiler først når feltene skal leses
- **Feilmodus å fange:** at modellen «retter» seg til spesifikasjonens skrivemåte fordi
  den kjenner PxWeb 1.0-spesifikasjonen bedre enn den kjenner denne skillen. Samme
  mekanisme som gjorde default-påstanden feil: spesifikasjonen og de levende
  installasjonene er ikke samme kilde

## 5. `aggregallowed` — en aggregering som ikke får lov

- **Installasjon:** SSB v1, `https://data.ssb.no/api/v0/no/table/14700` (KPI etter
  vare- og tjenestegruppe)
- **Oppgave:** «Vis KPI på hovedgruppenivå» — altså en aggregering av `VareTjenesteGrp`
- **Fasit:** `agg:`-kallet **skal** feile med 400. Tabellen har
  `extension.px.aggregallowed: false`, og hos SSBs v1 er det en teknisk sperre
  (verifisert 2026-09-03 på 14700 og 11342)
- **Suksess:**
  - Modellen leser `extension.px.aggregallowed` fra en liten prøvespørring i stedet for
    å prøve seg fram blindt, **eller** tolker 400-en riktig når den kommer
  - Den melder fra at aggregeringen ikke er tillatt på denne tabellen — den finner ikke
    på et tall, og den bytter ikke stilltiende til en annen tabell
  - `vs:` på samme variabel virker fortsatt, og er det riktige alternativet hvis
    brukeren egentlig ba om et nivå i klassifikasjonen
- **Feilmodus å fange:** at modellen henter aggregeringsnavnet fra v2 (der samme
  aggregering svarer 200 med data) og konkluderer at v1-kallet «burde» virke. Flagget
  betyr forskjellige ting i de to API-ene — det er hele poenget med scenarioet
- **Bonuspoeng:** at modellen ser at `01`, `02`, `03` allerede finnes som vanlige
  item-koder i `VareTjenesteGrp` (klassifikasjonen bærer nivåene i selve koden:
  `00` → `01` → `01.1` → `01.1.1`) og henter hovedgruppene med `item` i stedet for å
  gi opp. Kjøringen 2026-09-04 fant dette selv; det er nå dokumentert i Steg 4
- **Delfeil å se etter:** at modellen skriver `agg:agg_CoiCop2018Kpi011` med `agg_`-
  prefikset beholdt. Det gir `{"error":"Parameter error"}` — en annen feil enn den
  `aggregallowed` gir (`The request for variable '…' has an error`), og en modell som
  får den første har egentlig ikke testet det scenarioet påstår at den testet

## 6. Oslo kommune — samme land og språk som SSB, ingen felles konvensjoner

Scenarioet som fanger antakelsen «norsk installasjon ⇒ SSBs koder».

- **Installasjon:** `https://statistikkbanken.oslo.kommune.no/statbank/api/v1/no`, database `db1`
- **Oppgave:** «Folkemengden i Oslo etter bydel, siste år — hvilken bydel er størst?»
- **Nøkkelvalg:** variabelkodene er `bosted`, `kjønn`, `alder` og `år` — små bokstaver, norske ord,
  med `ø`/`å`. `Region`/`Kjonn`/`Alder`/`Tid` gir 400. Kroppen må sendes som UTF-8
- **Suksess:**
  - Modellen leser kodene fra metadata i stedet for å gjenbruke SSBs
  - Den oppdager at `år` har **løpenummer** som koder (`"36"` = 2026) og at årstallet kun finnes i
    `valueTexts` — `top(1)` er riktig verktøy, `item` med `"2026"` er feil
  - Nivå-ID-ene i stien prosentkodes (mellomrom, komma, `ø`/`å`)
  - Svaret oppgir kilde og at tallene er Oslos publisering av SSB-data
- **Feilmodus å fange:** at modellen antar `?config`-grensene ligner SSBs. Oslo har `maxValues`
  1 000 mot `maxCells` 550 000 — det største spriket mellom takene i hele inventaret, så et
  uttrekk kan ligge langt under cellebudsjettet og likevel avvises for å navngi for mange verdier
- **Svakhet ved dette scenarioet, vær klar over den:** `references/installations.md` inneholder nå
  en detaljert Oslo-oppføring med tabellnavn og løpenummer-kvirken. Scenarioet tester derfor
  «leser modellen referansefila og verifiserer den mot API-et?» og ikke «klarer den en kald
  probe?». Skal det siste testes, må Oslo-avsnittet midlertidig fjernes — eller scenarioet peke
  på en annen installasjon som ikke står i inventaret

---

## Generell regel som gjelder alle scenariene

Presentasjonen kommenterer kun tall fra det hentede uttrekket. Feiler kallet, sier
modellen det — ingen estimater, ingen «omtrent», ingen tall fra en tredjepartskatalog.
I v1 er dette skarpere enn i v2: flere installasjoner svarer bare `Bad Request` uten
diagnose, og på spansk `Solicitud incorrecta`, så en mislykket spørring er lett å
forveksle med et tomt resultat.
