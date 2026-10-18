# Eval-scenarier — ssb-pxwebapi-v2

Typiske brukerspørsmål med fasit (forventet tabell-ID + endepunktsekvens).
Kjøres via `skill-creator` ved større endringer i SKILL.md eller references/.
Vedlikeholder-internt — ikke med i distribusjons-zip eller README-filtreet.

Fasitverdier verifisert mot live API 2026-06-12. Hvis et scenario feiler, sjekk
først om tabellen har endret koder/struktur (kjør `scripts/check_examples.py`)
før du antar at skillen er problemet.

## 1. «Hvor mange bor i Oslo?»

- **Forventet tabell:** 07459
- **Sekvens:** (07459 fra `common-tables.md`; søket finner den ikke på første side) → `GET /tables/07459/metadata` → `POST /tables/07459/data`
- **Nøkkelvalg:** `Region=0301`, `ContentsCode=Personer1`, `Tid=top(1)`
- **Suksess:** Ett tall med årstall og «Kilde: SSB, tabell 07459. Sist oppdatert: {dato}.»

## 2. «KPI siste år»

- **Forventet tabell:** 14700, eller 14701 hvis svaret gir årstall (IKKE 03013/03014 — begge avsluttet)
- **Sekvens:** metadata → data
- **Nøkkelvalg:** `ContentsCode=KpiIndMnd` (indeks) eller `Tolvmanedersendring` (12-mnd endring), `Tid=top(13)`
- **Suksess:** Månedlig serie med enhet (indeks 2025=100 / prosent), kilde

## 3. «Folketall i Moss over tid»

- **Forventet tabell:** 07459 med kodeliste `agg_KommSummer`
- **Nøkkelvalg:** `codelist[Region]=agg_KommSummer`, `valueCodes[Region]=K-3103` (K-prefiks!). `outputValues[Region]=aggregated` er valgfri — den har ingen observerbar effekt (verifisert 2026-08-30), så scenarioet skal **ikke** kreve den
- **Suksess:** Konsistent tidsserie over kommunesammenslåingene (K-3103 aggregerer 0104/0136/3002/3103); ingen 400-feil pga. manglende prefiks. Svaret oppgir hvilken kodeliste som er brukt — responsen registrerer det ikke selv

## 4. «Arbeidsledighet nå»

- **Forventet tabell:** 13760 (AKU månedlig)
- **Sekvens:** søk («arbeidsledige» / AKU) → metadata → data
- **Nøkkelvalg:** riktig ContentsCode for arbeidsledige; `Justering=3MGG`; `Tid=top(2)` (siste måned er `..`)
- **Suksess:** Siste tilgjengelige 3MGG-tall med tremånedersperioden oppgitt, enhet tydelig (prosent av arbeidsstyrken vs. antall i 1000)

## 5. «Lakseeksport denne uka»

- **Forventet tabell:** 03024
- **Nøkkelvalg:** `Tid=top(1)` — ukeformat er `ÅÅÅÅUnn` (f.eks. `2026U23`), IKKE `W`
- **Suksess:** Kilopris og tonn for siste uke, ukenummer riktig gjengitt

## 6. «Sammenlign befolkningen i fylkene»

- **Forventet tabell:** 07459 med kodeliste `agg_KommFylker`
- **Nøkkelvalg:** `codelist[Region]=agg_KommFylker`, `valueCodes[Region]=*` (eller F-koder med F-prefiks), `Tid=top(1)`
- **Suksess:** Én rad per fylke, ikke per kommune

## 7. «Eksporter boligprisindeksen til Excel»

- **Forventet tabell:** 07221
- **Nøkkelvalg:** `outputFormat=xlsx` med `outputFormatParams` fra `output-formats.md` (`UseTexts` eller `UseCodesAndTexts`); `ContentsCode=Boligindeks` (IKKE `KvPris` — finnes ikke i 07221)
- **Suksess:** Gyldig xlsx-fil levert

## 8. «What is the population of Norway?» (engelsk)

- **Forventet tabell:** 07459 med `lang=en`
- **Nøkkelvalg:** `Region=0`, `ContentsCode=Personer1`, `Tid=top(1)`
- **Suksess:** Svar på engelsk, engelsk tallformat (komma som tusenskilletegn), «Source: Statistics Norway, table 07459. Last updated: {date}.». Fasiten er *formen*, ikke verdien — et bestemt folketall skal ikke stå her, for da belønner scenarioet et tall gjengitt fra hukommelsen i stedet for et hentet tall

## 9. «Folketallet i Norge i 1875»

- **Forventet atferd:** Ikke pxwebapi-kall som primærsvar — historiske tall fra før Statistikkbanken-perioden skal rutes til `ssb-histstat`-skillen (hvis tilgjengelig), ellers veiledning per Fallback-seksjonen
- **Suksess:** Skillen forsøker ikke å presse spørsmålet inn i moderne tabeller med feil tidsdekning

## 10. «Hva er styringsrenten?»

- **Forventet atferd:** Rutes til `norges-bank-api`-skillen (hvis tilgjengelig) — Norges Bank er primærkilden; Statistikkbanken har bare foliorenten som månedsserie (10701), som kommer senere
- **Suksess:** Ingen forsøk på å besvare med SSB-uttrekk. Generell regel som også gjelder alle scenariene over: presentasjonen kommenterer kun tall fra det hentede uttrekket — aldri innblandede tall fra andre kilder

## 11. «Lag en delbar URL for folketallet i Oslo 2020–2022»

- **Forventet tabell:** 07459
- **Nøkkelvalg:** GET-URL med `valueCodes[Tid]=[range(2020,2022)]` — hakeparentesene er obligatoriske i GET fordi komma er listeskilletegn (verifisert 2026-09-09). Kjøres URL-en med curl, skal `-g` være med
- **Suksess:** URL-en gir HTTP 200 med tre perioder; ingen `Illegal selection expression`, ingen lokal curl-feil «bad range in URL». Svaret nevner at `range()` er et fast vindu valgt bevisst (brukeren ba om et bestemt intervall), ikke et brudd på `top()`/`from()`-regelen

## 12. «KPI for alle hovedgrupper, hver måned i 2024, som csv til Excel»

- **Forventet tabell:** 14700
- **Nøkkelvalg:** `valueCodes[Tid]=2024*` (ikke 12 oppramsede måneder), `valueCodes[VareTjenesteGrp]=??` eller `codelist[VareTjenesteGrp]=agg_CoiCop2018Kpi011`, `ContentsCode=KpiIndMnd`, `outputFormat=csv&outputFormatParams=SeparatorSemicolon,UseTexts` og alle variabler i `stub` (pivotvennlig)
- **Suksess:** Én GET-URL som gir 200; svaret sier at csv er Latin-1 og at desimalpunktum må byttes i Power Query; anbefaler xlsx hvis fila skal åpnes i Excel; obligatorisk note fra 14700 om referanseår vises

## 13. «Her er en gammel lagret spørring: https://www.ssb.no/statbank/sq/10119120 — kan du hente dataene?»

- **Forventet atferd:** `GET /savedqueries/10119120` for definisjonen (tabell 08655), deretter `/savedqueries/10119120/data` — ikke avvisning som «v1-stoff», ikke websøk
- **Suksess:** Data levert; svaret opplyser at web-sq-lenken kun gir skjermvisning i PxWeb v2, og tilbyr en ekvivalent API-GET-URL med `from()`/`top()` som brukeren kan bruke i Power Query i stedet

## 14. «Hvor mange konkurser var det i IT-bransjen i 2. kvartal 2026?»

- **Forventet tabell:** 14729 eller 14727/14728 (SN2025-variantene) — ikke SN2007-forgjengeren 10790, som også har 2026K2
- **Nøkkelvalg:** variabel-ID `NACE2025`; IT er hovedområde `K` i SN2025 (var del av `J` i SN2007, der `K` er finans) — labelen leses fra metadata, ikke antas fra bokstaven
- **Suksess:** Tall fra `valueCodes[NACE2025]=K`; svaret sier at tabellen bruker SN2025 og at serien ikke kan skjøtes med SN2007-tabellene på næringsnivå

## 15. «Hvor mange bor i delområde 03010900 Majorstuen i Oslo?»

- **Forventet tabell:** 04317 (grunnkretsbefolkning, (G)) — ikke 07459, som stopper på kommune, og ikke 06944, som har Majorstuen som delområdekode men gir husholdningsinntekt, ikke folketall
- **Nøkkelvalg:** delområdekoden `03010900` finnes ikke i 04317 (400 `Non-existent value`); `valueCodes[Grunnkretser]=030109*` gir de 13 grunnkretsene Majorstuen Rode 1–13, med `valueCodes[ContentsCode]=*` selv om tabellen har én statistikkvariabel. Summen til delområde er egen beregning og merkes slik (Dataintegritet)
- **Suksess:** Tall per grunnkrets vist, summen merket som egen beregning bygd på de 13 hentede tallene, og svaret sier at SSB ikke publiserer folketall på delområdenivå — delområdet er avledet fra kodeprefikset

## 16. «Netto driftsresultat i prosent for Bergen siste 5 år, sammenlignet med KOSTRA-gruppen og landet»

- **Forventet tabell:** 12134 (Utvalgte nøkkeltall for kommuneregnskap, kommunekonsern (K)) — kjennes igjen på `kostrahoved` i `paths`; ikke 07459-logikk med `Region`
- **Sekvens:** (`GET /tables?query=kostra kommuneregnskap` hvis ID ukjent) → `GET /tables/12134/metadata` → Klass-oppslag av Bergens gruppe (`correspondencetables/2840`: 4601 → `EKG12`, ikke gjettet) → data
- **Nøkkelvalg:** `valueCodes[KOKkommuneregion0000]=4601,EKG12,EAKUO` (landet *uten* Oslo for økonominøkkeltall), `ContentsCode` valgt etter label «netto driftsresultat i prosent …» fra metadata (`KOSAGD230000` per 2026-09-20 — leses, ikke huskes), `Tid=top(5)`; ingen dimensjon utelatt
- **Suksess:** fem årsverdier med enhet prosent og desimaler fra `category.unit.decimals`; den obligatoriske noten om brudd i KOSTRA-gruppene 2019/2020 vist; svaret sier at tallene er reviderte (juni-utgave) ut fra `updated`, at gruppe- og landstall er SSBs egne veide gjennomsnitt (ikke egen sum), og «Kilde: SSB, tabell 12134. Sist oppdatert: {dato}.». Brukes en `KOS…`-kode uten forutgående metadata-kall i samme samtale, er scenarioet feilet

## 17. «Hvor mye bruker kommunen min på administrasjon per innbygger?»

- **Forventet tabell:** en KOSTRA-nøkkeltallstabell funnet via `kostra` + fagterm — ikke egen summering fra 12367 (`aggregallowed: false`)
- **Nøkkelvalg:** kommunekode fra brukeren eller metadata; `KOK…`-variabler og `KOS…`-kode lest fra metadata *i samtalen* (KOSTRA-variabler byttes ut når rapporteringskravene endres); region aldri utelatt; kodeliste «Uttrekk for KOSTRA-grupperinger» valgt på label hvis gruppen skal med
- **Suksess:** forholdstallet vist med enhet, urevidert/revidert oppgitt, og svaret formidler tallet uten å tolke «høyt» som «lav produktivitet» — SSBs egen advarsel (kan skyldes kvalitet, behov, smådriftsulemper)

## 18. «Hvor mange er 90–99 år, og hvor mange er 100 år eller eldre i Norge?»

- **Forventet tabell:** 07459 med kodeliste `agg_TiAarigGruppering` på `Alder` (lagt til i 1.6.2, verifisert 2026-10-11)
- **Nøkkelvalg:** `codelist[Alder]=agg_TiAarigGruppering` med kodelistens egne koder `F90-99` og `F100G10+`, lest fra `GET /codelists/agg_TiAarigGruppering` eller metadata — ikke `90-99`, og ikke uten kodeliste (begge gir 400 `Non-existent value`). I en GET-URL skrives `+` som `%2B` (`F100G10%2B`); i POST går `"F100G10+"` rett. Alternativet uten kodeliste er å summere enkeltaldrene selv, med `105+` som `%2B` i GET, og merke summen som egen beregning. `Region=0`, `Tid=top(1)`
- **Suksess:** to tall for siste år med enhet personer og «Kilde: SSB, tabell 07459. Sist oppdatert: {dato}.»; svaret oppgir kodelisten og at kjønn er utelatt (summert over begge kjønn). Ingen 400 på grunn av rå `+` i URL-en

## 19. «Hvor mye bruker en husholdning på transport i forhold til mat?»

- **Forventet tabell:** 14100 (Forbruksundersøkelsen, fra `common-tables.md`), valgt med begrunnelse — ikke en KPI-tabell
- **Nøkkelvalg:** `VareTjenesteGruppe` med koder lest fra metadata for «mat» og «transport» (f.eks. `01` eller `01.1`, og `07`), `ContentsCode` = `Utgift` og/eller `AndForbrUtg` **og** `Standardfeil`, `Tid=2022`
- **Suksess:** svaret sier hvilke koder «mat» og «transport» ble til, viser standardfeilen før det kaller forskjellen reell, merker forholdstallet som egen beregning, og oppgir at siste periode er 2022 (utvalgsundersøkelse, minst hvert femte år). Ingen tall i fasiten
