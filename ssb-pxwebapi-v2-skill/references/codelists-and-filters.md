# Kodelister og filtersyntaks

Kodelister og filteruttrykk i PxWebApi v2. De generelle reglene står først; SSBs egne kodelister for region, næring, alder og KPI kommer etterpå.

**Innhold**

1. Kodelister — prinsipper: `vs_` og `agg_`, ID per tabell, `valueMap`, koder med prefiks, `outputValues`
2. Filteruttrykk i valueCodes: `top()`, `from()`, `range()`, wildcards, hakeparenteser i GET, tidsformater
3. Regionkoder: finne kommunekoder, fylker og kommuner over tid (`F-`/`K-`)
4. Regionale nivåer under kommune: bydel, delområde, grunnkrets
5. Næringskoder: SN2007 → SN2025
6. Andre vanlige kodelister: alder, KPI/COICOP

---

## Kodelister — prinsipper

En kodeliste gir en variabel et annet sett verdier enn tabellens eget. Listene en tabell tilbyr, står per variabel i metadata under `dimension.{Var}.extension.codelists`.

| Type          | Prefiks | Gir                                                          | Eksempel fra 07459                                |
| ------------- | ------- | ------------------------------------------------------------ | ------------------------------------------------- |
| `Valueset`    | `vs_`   | Et utvalg av tabellens egne koder                            | `vs_Fylker`: 41 fylkeskoder, også nedlagte        |
| `Aggregation` | `agg_`  | Grupper med egne koder; `valueMap` viser hva hver består av  | `agg_KommFylker`: 18 fylker summert fra kommunene |

- **Bruk ID-en fra metadata for tabellen du spør mot.** ID-ene varierer mellom tabeller — samme næringsnivå heter `agg_NACE2025nivaa1` i 14729 og `agg_NACE2025niv1` i 14721 — og er case-sensitive. At en kodeliste finnes, betyr ikke at tabellen tilbyr den: `vs_Fylker2024` finnes, men ikke på 07459.
- **Velg på `label`.** «Fylker 2024-» er dagens fylker, «Fylker 2024, sammenslåtte tidsserier» er fylkene summert fra kommunene bakover i tid, «Alle fylker» tar med nedlagte koder. Samme label kan likevel stå på lister med ulik tidsdybde: `agg_KommSummer` (07459) og `agg_KommSummerHist` (06913) heter begge «Kommuner 2024, sammenslåtte tidsserier». `vs_`-labels slutter ofte med mellomrom («Alle fylker ») — trim før du sammenligner.
- **`valueMap` avgjør om lista summerer, ikke prefikset.** Har en kode flere elementer i `valueMap`, summerer API-et dem (`agg_KommFylker`, `agg_KommSummer`, aldersgruppene). Har hver kode ett element, er lista bare et utvalg, som en `vs_`-liste: `agg_Fylker2024`, `agg_GrkretsNy`, `agg_CoiCop2018Kpi011` og KOSTRAs «Uttrekk for …» (verifisert 2026-10-10).
- **Kodelistens egne koder går i `valueCodes`.** Summerende lister har egne koder, ofte med prefiks: `F-03` (`agg_KommFylker`), `K-3103` (`agg_KommSummer`), `F00-04` (`agg_FemAarigGruppering`). Et annet prefiks betyr en annen liste: `K_3103` i `agg_KommSummerHist` (06913) går lenger tilbake enn `K-3103` (se «Fylker og kommuner over tid»). Les kodene, ikke gjett dem. De finnes bare med kodelisten aktivert — uten `codelist[Var]` gir de 400 `Non-existent value`. Koder som også står i tabellens egen verdiliste (`03`, `0301`, KOSTRAs `EAK`), virker med og uten kodeliste (verifisert 2026-10-10). `*` med kodeliste gir alle kodene i lista, ikke alle tabellens verdier.
- **Det er kodelisten som summerer, ikke `outputValues`.** `outputValues[Var]=aggregated|single` er dokumentert, men har ingen effekt hos SSB: `aggregated`, `single`, utelatt og ugyldig `nonsense` gir samme data med HTTP 200 (07459 med `agg_KommSummer` og `agg_KommFylker`, verifisert 2026-08-30). Parameteren er ufarlig, men ingen kontroll — en skrivefeil gir ingen feilmelding.

### Finne, slå opp og bruke en kodeliste

Hver liste i `extension.codelists` har `id`, `label`, `type` (`Aggregation` eller `Valueset`) og en lenke til `/codelists/{id}`. 07459 tilbyr 11 `agg_`- og 3 `vs_`-lister på `Region`. Kodene leses i lista selv, eller i metadata med lista aktivert — da viser `category.index` listens koder:

```
GET /codelists/agg_KommFylker?lang=no
GET /tables/07459/metadata?codelist[Region]=agg_KommFylker
```

Hver kode i `/codelists`-svaret har `label` og `valueMap`. I `agg_KommFylker` har `F-03` «Oslo - Oslove» `["0399", "0301"]`, og `F-46` Vestland 110 gjeldende og nedlagte kommunekoder — derfor henger serien sammen bakover i tid.

I en dataspørring angis kodelisten per variabel, `"codelist"` i POST og `codelist[Var]` i GET:

```
POST /tables/07459/data
{ "selection": [
    { "variableCode": "Region", "codelist": "agg_KommFylker", "valueCodes": ["F-03", "F-11", "F-46"] },
    { "variableCode": "ContentsCode", "valueCodes": ["Personer1"] },
    { "variableCode": "Tid", "valueCodes": ["top(5)"] }
]}
```

```
GET /tables/07459/data?lang=no&valueCodes[ContentsCode]=Personer1&valueCodes[Tid]=top(5)&valueCodes[Region]=F-03,F-11,F-46&codelist[Region]=agg_KommFylker
```

---

## Filteruttrykk i valueCodes

Et uttrykk står som eget element i `valueCodes`-arrayet (POST) eller som verdi i `valueCodes[Var]=` (GET), og virker på alle variabler, ikke bare tid. Koder er strenger, også rent numeriske (`"0301"`, `"2024"`).

| Uttrykk                         | Gir                                                       | Eksempel                                                                   |
| ------------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------- |
| `top(N)`                        | De N siste verdiene                                       | `top(1)` siste periode · `top(13)` 13 måneder, for årsendring              |
| `top(N,offset)`                 | N verdier etter å ha hoppet over de `offset` siste        | `top(3,2)`: de tre før de to nyeste, f.eks. for å utelate foreløpige tall  |
| `bottom(N)`, `bottom(N,offset)` | Det samme fra starten                                     | `bottom(3)`: de tre eldste                                                 |
| `from(x)`, `to(x)`              | Fra og med / til og med `x`                               | `from(2020)`: 2020 og framover                                             |
| `range(a,b)`                    | Fra og med `a` til og med `b`, i rekkefølgen fra metadata | `range(2018,2023)` · `range(07.3,07.4.1)`: de sju COICOP-kodene imellom    |
| `*`                             | Alle verdier — med kodeliste: alle kodene i lista         | `*`                                                                        |
| `*` og `?` inne i en kode       | `*` = null eller flere tegn, `?` = nøyaktig ett tegn      | `46*` koder som starter med 46 · `2024*` alle måneder i 2024 · `??` alle tosifrede |

- **Uttrykk og enkeltkoder kan blandes** (verifisert 2026-09-09): `["2015", "top(2)"]` gir 2015 og de to nyeste årene, i både POST og GET.
- **To funksjoner i samme liste gir unionen, ikke snittet:** `from(2024M01),to(2024M03)` gir 321 perioder i 14700, ikke tre. Bruk `range()` for et intervall (verifisert 2026-10-10).
- **Wildcards matcher koder, ikke labels.** Et kommunenavn må oversettes til kode først — se «Finne kommunekoder».

### Hakeparenteser i GET, ikke i POST

I GET er komma listeskilletegn, så et uttrykk med komma — `range(a,b)`, `top(N,offset)`, `bottom(N,offset)` — deles i to og gir 400 `Illegal selection expression`. URL-koding av kommaet (`%2C`) hjelper ikke; uttrykket må stå i hakeparenteser, slik SSBs egen dokumentasjon gjør. I POST er hvert uttrykk eget element i arrayet, og der gir hakeparenteser 400 `Non-existent value` (verifisert 2026-10-10).

|                        | GET (`valueCodes[Var]=`)                                   | POST (`"valueCodes": […]`)   |
| ---------------------- | ---------------------------------------------------------- | ---------------------------- |
| Uttrykk med komma      | `[range(2020,2022)]`, `[top(3,2)]`                         | `"range(2020,2022)"`         |
| Sammen med enkeltkoder | `2015,[range(2020,2022)]`                                  | `"2015", "range(2020,2022)"` |
| Uttrykk uten komma     | `top(5)`, `from(2020)`, `*`, `46*`                         | `"top(5)"`                   |
| Kode med `+`           | `105%2B` — en rå `+` leses som mellomrom og gir 400        | `"105+"`                     |

### Tidsformater

Formatet må matche tabellens `timeUnit`, og bokstavene er norske uansett `lang`:

| timeUnit  | Format    | Eksempel                     |
| --------- | --------- | ---------------------------- |
| Annual    | `YYYY`    | `2024`                       |
| Monthly   | `YYYYMNN` | `2024M06`                    |
| Quarterly | `YYYYKN`  | `2024K2` — ikke `Q`          |
| Weekly    | `YYYYUNN` | `2026U23` i 03024 — ikke `W` |

### Relativ eller fast periode

For `Tid` er `top()` og `from()` førstevalget (SKILL.md Steg 4): de fanger opp nye perioder, så delbare URL-er holder seg oppdaterte. Faste vinduer — `range()`, `2024*` og enkeltperioder — er riktige når brukeren ber om et bestemt år eller intervall, eller om noen spredte år (folketellingsår).

### Verifiserte eksempler

- `https://data.ssb.no/api/pxwebapi/v2/tables/07459/data?valueCodes[Region]=0301&valueCodes[ContentsCode]=Personer1&valueCodes[Tid]=[range(2020,2022)]` — tre år, hakeparenteser i GET
- `https://data.ssb.no/api/pxwebapi/v2/tables/14700/data?valueCodes[Tid]=2024*&valueCodes[VareTjenesteGrp]=??&valueCodes[ContentsCode]=KpiIndMnd` — eksempelet fra SSBs veiledning: KPI for alle måneder i 2024; `??` gir 14 koder, totalen `00` og de 13 hovedgruppene, uten kodeliste
- `https://data.ssb.no/api/pxwebapi/v2/tables/14700/data?valueCodes[Tid]=top(1)&valueCodes[ContentsCode]=KpiIndMnd&valueCodes[VareTjenesteGrp]=[range(07.3,07.4.1)]` — `range()` på en variabel som ikke er tid
- `https://data.ssb.no/api/pxwebapi/v2/tables/07459/data?lang=no&valueCodes[Region]=0&valueCodes[Alder]=105%2B&valueCodes[ContentsCode]=Personer1&valueCodes[Tid]=top(1)` — aldersgruppen `105+`, skrevet `%2B`

---

## Regionkoder

### Finne kommunekoder

Et kommunenavn må oversettes til kode:

1. Søk på navnet med `/tables?query=…` — søket leter også i variabelverdier og bekrefter at kommunen finnes
2. Hent metadata for en kommunetabell (f.eks. 07459) og let etter navnet i `category.label` på `Region`
3. Eller bruk wildcard på fylkeskoden (`34*` for Innlandet, `345?` for å snevre inn) og les labelene i svaret
4. Klass har hele kommuneinndelingen med historikk: `https://data.ssb.no/api/klass/v1/classifications/131.json` (se `klass-vardok.md`)

### Fylker og kommuner over tid

Regionkoder er ikke stabile: en sammenslått kommune eller et sammenslått fylke får ny kode, og den gamle serien stopper. Valgene i 07459, pluss den lange kommuneserien i 06913 (verifisert 2026-10-11):

| Behov                            | `valueCodes`                     | Kodeliste                            | Merk                                                                                               |
| -------------------------------- | -------------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------- |
| Hele landet                      | `0`                              | —                                    | Gjelder 07459 og mange andre, men ikke alle — sjekk `category.index`. KOSTRA bruker `EAK`           |
| Én eller flere kommuner          | `0301` · `46*` (alle i Vestland) | —                                    | Koden gjelder kommunen slik den var det året                                                       |
| Kommune som sammenhengende serie | `K-3103`                         | `agg_KommSummer`                     | Dagens kommuner summert fra eldre koder, fra 1986: Moss = `0104` + `0136` + `3002` + `3103`        |
| Samme, lengre tilbake            | `K_3103`                         | `agg_KommSummerHist` (06913)         | Går tilbake til den store kommunereformen i 1965 og summerer også kommunene som ble slått sammen da. Fylker: `agg_KommFylkerHist` |
| Dagens fylker                    | `*` eller `31,46`                | `agg_Fylker2024`                     | 16 koder inkl. Svalbard; et utvalg, ingen summering                                                |
| Fylker som sammenhengende serie  | `*` eller `F-03,F-11,F-46`       | `agg_KommFylker`                     | 18 koder (også Jan Mayen og kontinentalsokkelen), summert fra kommunene etter dagens fylkesgrenser |
| Alle koder, også nedlagte        | `*`                              | `vs_Fylker` (41) · `vs_Kommun` (952) | Blander dagens og nedlagte koder i samme uttrekk                                                   |

**En region som ikke fantes et år, gir 0, ikke en tom celle** — uten `status`, både før den ble opprettet og etter at den ble nedlagt: `3002` Moss (2020–2023) gir 0 i 2019 og i 2026, `30` Viken gir 0 i 2026. Ikke presenter 0 som et tall, og ikke summer nedlagte koder med dagens. KOSTRA-tabellene har egen regionvariabel og egne «Uttrekk for …»-lister, se `kostra.md`.

- `https://data.ssb.no/api/pxwebapi/v2/tables/07459/data?lang=no&codelist[Region]=agg_Fylker2024&valueCodes[Region]=*&valueCodes[ContentsCode]=Personer1&valueCodes[Tid]=top(1)` — de 16 fylkene

Moss som sammenhengende serie over sammenslåingen med Rygge i 2020 og kodeskiftet i 2024:

```
GET /tables/07459/data?lang=no&valueCodes[Region]=K-3103&valueCodes[Tid]=*&valueCodes[ContentsCode]=Personer1&codelist[Region]=agg_KommSummer
```

---

## Regionale nivåer under kommune: bydel, delområde, grunnkrets

Tittelsuffikset viser laveste regionale nivå: **(F)** fylke, **(K)** kommune, **(B)** bydel, **(G)** grunnkrets (søketips i SKILL.md Steg 2). Verifisert 2026-09-20:

| Nivå       | Kodeform                                    | Hvor                                                                                                                                                                                         |
| ---------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bydel      | `030101a` (kommune + bydel + `a`)           | Kodeliste `vs_Bydeler4StoreByerNye2` (57 koder: bydeler i Oslo, Stavanger, Bergen og Trondheim, inkl. under de gamle kommunekodene 1201/1601) — i (B)-tabeller som 06944. KOSTRAs bydelstabeller har egne koder, se `kostra.md` |
| Delområde  | `03010100` (kommune + 2 siffer + `00`)      | **Ingen egne delområdetabeller.** Finnes som regionkoder i 06944 (husholdningsinntekt, kodeliste `vs_Delomraader01`, 2 247 delområder) — eneste av de 90 bydel-tabellene som har det (sveip 2026-09-20). I (G)-tabellene finnes koden ikke |
| Grunnkrets | `03010101` (kommune + delområde + 2 siffer) | Fire (G)-tabeller: 04317 (befolkning), 04362 (alder/kjønn), 06198 (areal), 14737 (boligverdi-koeffisienter). Søk `grunnkrets` gir nøyaktig disse fire                                         |

**Grunnkretstabellene (G)** deler samme dimensjon på 34 097 åttesifrede koder — alle gjeldende og historiske kretser (labeler som «Karrestad (t.o.m. 2002)»), pluss `KKKK0000` «Ikke koblet» og `KKKK9999` «Uoppgitt grunnkrets» per kommune. Variabel-ID-en varierer: `Grunnkretser` i 04317 og 14737 (`elimination: false`), `Region` i 04362 og 06198 (`elimination: true`). Klass-klassifikasjon 1 (se `klass-vardok.md`), VarDok 135. Kodelistene er de samme i alle fire, og ingen av dem summerer: `agg_GrkretsNy` gjeldende kretser 2024– (14 513), `agg_Grkrets2020` 2020–2023 (14 467), `agg_GrkretsBydel2002` de fire største byene 2004– (2 517), `agg_GrkretsKomm2002` og `vs_Grunnkretser01` alle 34 097.

**Cellegrensen slår inn fort:** 34 097 kretser × 28 år i 04317 = 954 716 celler > 800 000 → `Too many cells selected`. Ett år for alle kretser (34 097 celler) går fint. Filtrer på kommuneprefiks med wildcard, og husk `ContentsCode` selv om tabellen bare har én statistikkvariabel:

- `https://data.ssb.no/api/pxwebapi/v2/tables/04317/data?lang=no&valueCodes[Grunnkretser]=0301*&valueCodes[ContentsCode]=*&valueCodes[Tid]=top(1)` — 617 Oslo-kretser 2026, 35 historiske med status `.`
- `https://data.ssb.no/api/pxwebapi/v2/tables/04317/data?lang=no&codelist[Grunnkretser]=agg_GrkretsNy&valueCodes[Grunnkretser]=0301*&valueCodes[ContentsCode]=*&valueCodes[Tid]=top(1)` — samme, men kun de 592 gjeldende

**Delområde fra grunnkretstabellene:** wildcard på det sekssifrede prefikset gir kretsene i ett delområde — `valueCodes[Grunnkretser]=030109*` gir de 13 kretsene Majorstuen Rode 1–13 i delområde 03010900 Majorstuen (Oslo). Delområdekoden `03010900` gir derimot 400 `Non-existent value` i 04317. Summen til delområde er *din* beregning (Dataintegritet: merk egne beregninger), og den er ikke alltid lik SSBs eget tall:

- 04317: summen av alle 617 Oslo-kretser 2026 (inkl. `03019999` Uoppgitt) er 728 714 — identisk med kommunetallet i 07459. Her stemmer summering
- 04362: dataset-noten sier at alle 1- og 2-tall er endret til 0 eller 3 av personvernhensyn, og Region-noten at «hvis kretstallene aggregeres til kommunenivå, vil det kunne oppstå avvik». Vis noten når du summerer
- 06198: note om avvik fra kommunetall før 2010

Verifisert:

- `https://data.ssb.no/api/pxwebapi/v2/tables/04317/data?lang=no&valueCodes[Grunnkretser]=030109*&valueCodes[ContentsCode]=*&valueCodes[Tid]=top(1)` — 200, 13 kretser, ingen tomme
- `https://data.ssb.no/api/pxwebapi/v2/tables/06944/data?lang=no&valueCodes[Region]=0301,03010900&valueCodes[HusholdType]=0000&valueCodes[ContentsCode]=*&valueCodes[Tid]=top(1)` — 200, kommune og delområdet Majorstuen side om side; 06944 tar delområdekoden direkte, med eller uten `codelist[Region]=vs_Delomraader01`

Vil brukeren ha delområdetall SSB selv har publisert, er 06944-typen riktig; vil de ha befolkning, areal eller aldersfordeling på delområde, er svaret en merket sum av grunnkretser fra (G)-tabellene.

---

## Næringskoder: SN2007 → SN2025

SSB er i overgang til **SN2025** (Standard for næringsgruppering 2025, norsk utgave av NACE Rev. 2.1). Per 2026-09-20 er 14 tabeller på SN2025 og 331 på SN2007. Overgangen skjer statistikk for statistikk, og **SN2007-tabellene lever videre parallelt** — de er ikke merket `discontinued` og oppdateres fortsatt (10790 og 14729 har begge 2026K2). Tittelen sier hvilken standard tabellen bruker; søk på `SN2025` eller `SN2007` i `/tables?query=` for å skille variantene.

|                     | SN2007-tabeller          | SN2025-tabeller |
| ------------------- | ------------------------ | --------------- |
| Variabel-ID         | `NACE2007`               | `NACE2025`      |
| Næringshovedområder | 21 (A–U)                 | 22 (A–V)        |
| Totalkode           | varierer (`A_U` i 07322) | `_T`            |
| Uoppgitt            | varierer (`00` i 07322)  | `zz5`           |
| 5-sifret kode       | `62.010`                 | `62.100`        |

**Bokstavkodene betyr ikke det samme i de to standardene.** SN2007 J «Informasjon og kommunikasjon» er delt i SN2025 J (utgivelse, kringkasting, innholdsproduksjon) og K (telekommunikasjon, dataprogrammering, IT-tjenester), og alle bokstaver etter J er forskjøvet ett hakk: SN2007 K (finans) = SN2025 L, L (eiendom) = M, M (faglig/teknisk) = N, … U (internasjonale organisasjoner) = V. `valueCodes[NACE2007]=K` gir finans; `valueCodes[NACE2025]=K` gir IT. Les variabel-ID-en fra metadata, og slå alltid opp labelen før du sammenligner bokstavkoder på tvers av tabeller.

Kodelistene på `NACE2025` varierer per tabell: `agg_NACE2025nivaa1` (14729) og `agg_NACE2025niv1` (14721, 14730, 14731) gir begge næringshovedområdene A–V inkl. `_T` (24 koder), `vs_NACE2025niva1og5nn` (14729) gir hovedområder pluss 5-siffer næring (762 koder), og 14758 har ingen. Femsifrede koder inneholder punktum og brukes direkte i GET. Verifisert 2026-09-20:

- `https://data.ssb.no/api/pxwebapi/v2/tables/14758/data?lang=no&valueCodes[NACE2025]=_T,A,K,L&valueCodes[ContentsCode]=ASer&valueCodes[Tid]=2025` — 200, `_T` = 405 436 aksjeselskaper
- `https://data.ssb.no/api/pxwebapi/v2/tables/14729/data?lang=no&valueCodes[Region]=0&valueCodes[NACE2025]=62.100&valueCodes[ContentsCode]=Konkurser&valueCodes[Tid]=top(1)` — 200, punktum i koden trenger ingen encoding
- `https://data.ssb.no/api/pxwebapi/v2/tables/14729/data?lang=no&valueCodes[Region]=0&codelist[NACE2025]=agg_NACE2025nivaa1&valueCodes[NACE2025]=*&valueCodes[ContentsCode]=Konkurser&valueCodes[Tid]=top(1)` — 200, 24 hovedområder

**Overlappsår:** 07322 (SN2007, 2008–2025) og 14758 (SN2025, 2025–) har begge 2025, og totalen `A_U` = `_T` = 405 436. Totalen er den samme fordi alle næringer er alle næringer — bruddet ligger på næringsnivå. Bruk SN2007-tabellen for lange tidsserier, SN2025-tabellen for 2025/2026 og framover, skjøt aldri de to på næringsnivå, og si i svaret hvilken standard tallene bygger på.

Fullstendig kodeverk (Klass ID 6, versjon 3218) og korrespondansetabell SN2025 → SN2007 (ID 2919): se `klass-vardok.md`.

---

## Andre vanlige kodelister

**Alder.** 07459 og mange andre befolkningstabeller tilbyr aldersgrupperinger med egne, summerende koder — de krever `codelist[Alder]`:

| Kodeliste                | Koder                            |
| ------------------------ | -------------------------------- |
| `agg_FemAarigGruppering` | `F00-04`, `F05-09`, … `F100G5+`  |
| `agg_TiAarigGruppering`  | `F00-09`, `F10-19`, … `F100G10+` |

Den siste koden har `+`, så den skrives `%2B` i GET. 07459 har også ferdige grupperinger som `agg_TodeltGrupperingB` (0–17, 18+) og `agg_TredeltGrupperingB2` (0–19, 20–64, 65+); les hele lista fra metadata.

**KPI: klassifikasjon og kodeliste er to ting.** Verdikodene i `VareTjenesteGrp` i 14700 (`00`, `01`, `01.1`, `07.3` …) følger COICOP 2018, en internasjonal klassifikasjon fra FNs statistikkdivisjon (UNSD). Kodelistene er derimot SSBs egne PxWeb-utvalg av de kodene, med ID-er SSB har satt for tabellen:

| Kodeliste                                       | Innhold                                                                        |
| ----------------------------------------------- | ------------------------------------------------------------------------------ |
| `vs_CoiCop2018Kpi01`                            | Alle nivåer av varer og tjenester (336 koder)                                  |
| `agg_CoiCop2018Kpi011`                          | De 13 hovedgruppene `01`–`13` — et utvalg, ingen summering                     |
| `agg_CoiCop2018Kpi010`, `012`–`015`             | Ett nivå hver: totalindeks, gruppe, undergruppe 1 og 2, varer og varegrupper   |

Samme skille gjelder næring: SN2025 er SSBs norske utgave av NACE Rev. 2.1 (se over).
