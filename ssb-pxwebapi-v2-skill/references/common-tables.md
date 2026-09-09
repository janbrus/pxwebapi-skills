# Vanlige SSB-tabeller

Kurert liste over mye etterspurte tabeller, basert på faktisk bruk. Bruk alltid `GET /tables?query=...` for å bekrefte at tabellen er oppdatert — tabell-IDer kan endre seg.

---

## Befolkning

| ID    | Tittel                                                                  | Frekvens    | Typisk bruk                                                 |
| ----- | ----------------------------------------------------------------------- | ----------- | ----------------------------------------------------------- |
| 07459 | Alders- og kjønnsfordeling i kommuner, fylker og hele landet            | Årlig       | Folketall, aldersfordeling, kommunesammenligninger          |
| 01222 | Endringar i befolkninga i løpet av kvartalet, kommuner/fylker           | Kvartalsvis | Befolkningsendringer per kvartal                            |
| 06913 | Endringer i kommuner, fylker og hele landets befolkning                 | Årlig       | Fødte, døde, inn/utvandring, historisk fra 1951             |
| 05184 | Innvandrere, etter kjønn og landbakgrunn                                | Årlig       | Innvandrerbefolkning etter kjønn og landbakgrunn (fra 1970) |
| 06076 | Privathusholdninger og personer i privathusholdninger                   | Årlig       | Husholdningsstruktur, fylkesnivå                            |
| 11342 | Areal og befolkning i kommuner, fylker og hele landet                   | Årlig       | Befolkningstetthet, areal per kommune                       |
| 14746 | Framskrevet folkemengde kommuner, fylker og hele landet, 9 alternativer | Årlig       | Befolkningsprognoser til 2050                               |
| 05375 | Forventet gjenstående levetid, etter kjønn og alder                     | Årlig       | Levealder, forventet gjenstående levetid                    |
| 07995 | Døde, etter kjønn, alder og uke (foreløpige tall)                       | Ukentlig    | Overdødelighet, ukentlig dødsstatistikk                     |
| 10467 | Fødte, etter jentenavn og guttenavn                                     | Årlig       | Navnestatistikk for nyfødte                                 |
| 10501 | Personer, etter jentenavn og guttenavn                                  | Årlig       | Navnestatistikk for hele befolkningen                       |
| 12891 | Etternavn brukt av 200 personer eller flere                             | Årlig       | Etternavnstatistikk                                         |

Tabell 07459 er den mest brukte befolkningstabellen. Den dekker alle kommuner, fylker og hele landet. Bruk kodeliste `agg_KommFylker` for fylkesaggregering, `agg_KommSummer` for konsistente tidsserier over kommunesammenslåinger.

---

## Priser og inflasjon

| ID    | Tittel                                                | Frekvens    | Typisk bruk                                                                       |
| ----- | ----------------------------------------------------- | ----------- | --------------------------------------------------------------------------------- |
| 14700 | Konsumprisindeks (KPI), etter vare- og tjenestegruppe | Månedlig    | Total KPI og prisvekst per varegruppe (erstatter 03013/03014)                     |
| 14702 | KPI, KPI-JA og KPI-JAE, etter leveringssektor         | Månedlig    | KPI fordelt på leveringssektor                                                    |
| 14704 | Justert KPI (KPI, KPI-JA og KPI-JAE), hovedgrupper    | Månedlig    | Kjerneinflasjon - underliggende prisvekst — Norges Banks foretrukne inflasjonsmål |
| 09654 | Priser på drivstoff                                   | Månedlig    | Bensin- og dieselpriser per liter                                                 |
| 09387 | Kraftpris, nettleie og avgifter for husholdninger     | Kvartalsvis | Strømpriser for husholdninger                                                     |

KPI (14700): Basisår 2025=100. `ContentsCode` "KpiIndMnd" = indeks, "Tolvmanedersendring" = 12-måneders endring. Både 03013 og 03014 er avsluttet. KPI-JAE (14704) er populært kalt kjerneinflasjon og brukes mye i pengepolitisk analyse.

---

## Arbeid og lønn

| ID    | Tittel                                                                        | Frekvens       | Typisk bruk                                                               |
| ----- | ----------------------------------------------------------------------------- | -------------- | ------------------------------------------------------------------------- |
| 11658 | Yrkes- (4-siffer), kjønns- og aldersfordeling for lønnstakere, jobber og lønn | Kvartalsvis    | Lønn og sysselsetting per yrke, kjønn og alder (4-siffer NYK)             |
| 11418 | Yrkesfordelt månedslønn, etter sektor og kjønn                                | Årlig          | Lønnsnivå per yrke, lønnsforskjeller                                      |
| 11419 | Yrkesfordelt månedslønn, etter sektor og næring                               | Årlig          | Lønn per yrke og næring kombinert                                         |
| 11420 | Utdanningsfordelt månedslønn, etter sektor og næring                          | Årlig          | Lønn etter utdanningsnivå                                                 |
| 11421 | Aldersfordelt månedslønn, etter sektor og næring                              | Årlig          | Lønn etter aldersgruppe                                                   |
| 14378 | Utdanningsfordelt månedslønn, etter fullført utdanning                        | Årlig          | Lønn etter type fullført utdanning                                        |
| 11654 | Lønnstakere, jobber, lønn og lønnsindeks, etter næring                        | Kvartalsvis    | Lønnsforhandling, lønnsutvikling                                          |
| 11587 | Ledige stillinger, etter næring (sesongjustert)                               | Kvartalsvis    | Etterspørsel etter arbeidskraft                                           |
| 13979 | Lønnstakere og jobber i utleie av arbeidskraft (næring 78.2)                  | Kvartalsvis    | Bemanningsbransjen, etter yrke og arbeidssted, fylkesnivå                 |
| 05111 | Personer, etter arbeidsstyrkestatus, kjønn og alder                           | Årlig          | Sysselsatte, arbeidsledige og personer utenfor arbeidsstyrken (fra 1972-) |
| 13760 | Arbeidsledige og sysselsatte, personer og prosent                             | Månedlig       | Arbeidsstyrken og arbeidsledighet, AKU, sesongjusert                      |
| 13470 | Næringsfordeling  blant sysselsatte                                           | Årlig (4. kv.) | Sysselsatte per næring (NACE 5-siffer) og kommune/fylke                   |

---

## Nasjonalregnskap og makroøkonomi

| ID    | Tittel                                                   | Frekvens                       | Typisk bruk                                                                    |
| ----- | -------------------------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------ |
| 09190 | Makroøkonomiske hovedstørrelser (ujustert/sesongjustert) | Kvartalsvis                    | BNP, konsum, investeringer, eksport/import (mest brukte)                       |
| 09189 | Makroøkonomiske hovedstørrelser                          | Årlig                          | BNP, konsum, investeringer (årlig, fra 1970-)                                  |
| 09842 | BNP og andre hovedstørrelser, per innbygger              | Årlig                          | BNP per innbygger, velstandsmål                                                |
| 12880 | Konjunkturtendensene — regnskap og prognoser             | Årlig, Kvartalsvis oppdatering | Prognoser for BNP, sysselsetting, renter m.m. 4 år frem, tall tilbake til 1991 |
| 09672 | Drifts- og kapitalregnskap, løpende priser               | Kvartalsvis                    | Utenriksregnskap, driftsbalanse, kapitalstrømmer                               |
| 10701 | NIBOR og Norges Banks foliorente                         | Månedlig                       | Pengemarkedsrenter, styringsrente                                              |
| 10748 | Renter på nye boliglån, etter utlånstype og bindingstid  | Månedlig                       | Boliglånsrenter, utvalg banker/kredittforetak                                  |
| 07200 | Renter på utestående utlån, etter långiver og sektor     | Kvartalsvis                    | Utlånsrenter totaltelling, historisk fra 1979-                                 |

Tabell 12880 er unik fordi den inneholder SSBs egne prognoser for makroøkonomiske størrelser fire år fremover.

---

## Inntekt og skatt

| ID    | Tittel                                                                | Frekvens | Typisk bruk                                                                                      |
| ----- | --------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------ |
| 03068 | Skattepliktig inntekt, fradrag og skatt, bosatte 17+ år, gjennomsnitt | Årlig    | Gjennomsnittlig bruttoinntekt, lønn, fradrag og skatt for personer per kommune/fylke (fra 1993-) |

---

## Utenrikshandel

| ID    | Tittel                                                        | Frekvens | Typisk bruk                                                             |
| ----- | ------------------------------------------------------------- | -------- | ----------------------------------------------------------------------- |
| 08799 | Utenrikshandel med varer, etter varenummer (HS) og land       | Månedlig | Eksport/import per vare og land, detaljert                              |
| 08800 | Utenrikshandel med varer, etter varenummer (HS) og land       | Årlig    | Eksport/import per vare og land, detaljert. Oppdateres i februar og mai |
| 08804 | Utenrikshandel med varer, hovedtall, etter land/handelsområde | Årlig    | Eksport/import hovedtall per land og verdensdel                         |

---

## Bolig og eiendom

| ID    | Tittel                                                   | Frekvens    | Typisk bruk                                         |
| ----- | -------------------------------------------------------- | ----------- | --------------------------------------------------- |
| 07221 | Prisindeks for brukte boliger, etter boligtype og region | Kvartalsvis | Boligprisutvikling per region og type (kvartalsvis) |
| 07230 | Prisindeks for brukte boliger, etter boligtype og region | Årlig       | Boligprisutvikling (årlig)                          |
| 14545 | Gjennomsnittlig kvadratmeterpris og antall omsetninger   | Årlig       | Faktiske boligpriser per kvm, kommunenivå           |
| 06265 | Boliger, etter bygningstype                              | Årlig       | Boligmasse per kommune                              |
| 03723 | Byggeareal, boliger og bruksareal                        | Månedlig    | Igangsatte boliger, nybygg-aktivitet, fylkesnivå    |
| 09897 | Predikert månedlig leie, etter prissone og rom           | Årlig       | Leieprisnivå                                        |
| 11574 | Næringseiendomutleie                                     | Årlig       | Utleie av næringseiendom                            |

---

## Byggekostnader

| ID    | Tittel                                           | Frekvens    | Typisk bruk                                       |
| ----- | ------------------------------------------------ | ----------- | ------------------------------------------------- |
| 08651 | Byggekostnadsindeks for bustader i alt           | Månedlig    | Samlet byggekostnadsutvikling                     |
| 08653 | Byggekostnadsindeks for einebustad av tre        | Månedlig    | Byggekostnader eneboliger                         |
| 08655 | Byggekostnadsindeks for bustadblokk              | Månedlig    | Byggekostnader boligblokk                         |
| 04534 | Byggekostnadsindeks for røyrleggjararbeid        | Månedlig    | Rørleggerarbeid, kontor/forretningsbygg           |
| 08662 | Byggekostnadsindeks for veganlegg                | Kvartalsvis | Byggekostnader veibygging                         |
| 08663 | Kostnadsindeks for drift og vedlikehold av veger | Kvartalsvis | Drifts- og vedlikeholdskostnader vei, snøbrøyting |

---

## Energi og petroleum

| ID    | Tittel                                                    | Frekvens    | Typisk bruk                                    |
| ----- | --------------------------------------------------------- | ----------- | ---------------------------------------------- |
| 14091 | Elektrisitetsbalanse                                      | Månedlig    | Produksjon, forbruk og eksport/import av strøm |
| 11561 | Energibalanse — tilgang og anvendelse                     | Årlig       | Samlet energiregnskap                          |
| 08205 | Energibruk, energikostnader og priser i industrien        | Årlig       | Energibruk per næring                          |
| 09602 | Påløpte investeringer, utvinning og rørtransport          | Kvartalsvis | Oljeinvesteringer per kvartal                  |
| 07154 | Investeringsstatistikk, utvinning/bergverk/industri/kraft | Kvartalsvis | Industriinvesteringer bredt                    |

---

## Transport og reiseliv

| ID    | Tittel                                                         | Frekvens    | Typisk bruk                                  |
| ----- | -------------------------------------------------------------- | ----------- | -------------------------------------------- |
| 14162 | Overnattingar, etter innkvarteringstype og gjestens bustadland | Månedlig    | Turiststatistikk, hotell/camping, fylkesnivå |
| 12535 | Totalkostnadsindeks for vare- og lastebiltransport             | Kvartalsvis | Transportkostnader                           |

---

## Utdanning

| ID    | Tittel                             | Frekvens | Typisk bruk                 |
| ----- | ---------------------------------- | -------- | --------------------------- |
| 12255 | Utvalgte nøkkeltall for grunnskole | Årlig    | Elever, lærere, kommunenivå |

---

## Næringsliv

| ID    | Tittel                                             | Frekvens | Typisk bruk                  |
| ----- | -------------------------------------------------- | -------- | ---------------------------- |
| 07091 | Bedrifter, etter næring og antall ansatte          | Årlig    | Bedriftsstruktur per kommune |
| 07218 | Føretakskonkursar, personlege konkursar, tvangssal | Månedlig | Konkurs- og tvangsstatistikk |

---

## Kriminalitet

| ID    | Tittel                        | Frekvens | Typisk bruk             |
| ----- | ----------------------------- | -------- | ----------------------- |
| 08484 | Anmeldte lovbrudd, etter type | Årlig    | Kriminalitetsstatistikk |

---

## Klima og miljø

| ID    | Tittel                                                  | Frekvens | Typisk bruk                     |
| ----- | ------------------------------------------------------- | -------- | ------------------------------- |
| 13931 | Klimagasser, etter utslippskilde og energiprodukt (AR5) | Årlig    | Klimagassutslipp, Paris-avtalen |

---

## Religion og livssyn

| ID    | Tittel                                           | Frekvens | Typisk bruk              |
| ----- | ------------------------------------------------ | -------- | ------------------------ |
| 06326 | Medlemmer i trus- og livssynssamfunn utanfor Dnk | Årlig    | Tros- og livssynssamfunn |

---

## Medier og kultur

| ID    | Tittel                                     | Frekvens | Typisk bruk |
| ----- | ------------------------------------------ | -------- | ----------- |
| 12947 | Bruk av ulike medier, etter kjønn og alder | Årlig    | Mediebruk   |

* * *

## Offentlig sektor

| ID    | Tittel                                      | Frekvens | Typisk bruk                                   |
| ----- | ------------------------------------------- | -------- | --------------------------------------------- |
| 13542 | Kommuneregnskap, nøkkeltall, KOSTRA         | Årlig    | Driftsresultat underskudd kommuner, ROBEK     |
| 14668 | Offentlig forvaltning inntekter og utgifter | Årlig    | Stat og kommune, skatt, inntekter og utgifter |

---

### Helse

| ID    | Tittel                                                               | Frekvens | Typisk bruk                           |
| ----- | -------------------------------------------------------------------- | -------- | --------------------------------------|
| 14824 | Pasienter, behandlinger og oppholdsdøgn, somatisk, diagnose og aktør | Årlig    | Bruk av sykehus etter diagnosegrupper |
