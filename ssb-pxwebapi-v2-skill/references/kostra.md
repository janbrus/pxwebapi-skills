# KOSTRA — kommune-stat-rapportering i Statistikkbanken

KOSTRA (KOmmune-STat-RApportering) er SSBs informasjonssystem om kommunal og fylkeskommunal virksomhet: økonomi, skoler, helse, kultur, miljø, sosiale tjenester, boliger, tekniske tjenester og samferdsel. 

Kommunene rapporterer elektronisk til SSB (prosjekt fra 1995, alle kommuner med fra 2001, tall publisert fra 1999), og SSB kobler rapporteringen med registre (NAV, BASIL, GSI, VIGO, KPR, Husbanken, NVDB m.fl.) og annen SSB-statistikk. Tabellene avviker fra resten av Statistikkbanken på nesten alle punkter som betyr noe for en spørring — variabel-ID-er, regionkoder, kodelister, eliminering, publiseringsrytme og stabilitet. Verifisert mot live API og SSBs dokumentasjonsside 2026-09-20.

Dokumentasjon: https://www.ssb.no/offentlig-sektor/kostra/statistikk/kostra-kommune-stat-rapportering/om-kostra/dokumentasjon-av-kostra

## To nivåer av tall, grunnlagsdata og nøkkeltall

*Grunnlagsdata* er absolutte tall (antall enheter, beløp); *nøkkeltall/indikatorer* er forholdstall der grunnlagsdata settes i forhold til hverandre eller til målgrupper. Nøkkeltallene er ordnet i fire typer: **prioriteringer** (andel av kommunens frie inntekter til formålet), **dekningsgrader** (andel av målgruppen som mottar tjenesten), **produktivitet/enhetskostnader** (kostnad per enhet) og **utdypende tjenesteindikatorer**. SSB advarer selv mot å tolke høye enhetskostnader som lav produktivitet — det kan like gjerne være høy kvalitet, tung brukergruppe eller smådriftsulemper. Formidle tallet; ikke tolk det.

---

## Kjenne igjen en KOSTRA-tabell

KOSTRA er en tverrgående meny under emnet Offentlig sektor: hver KOSTRA-tabell har en sti `os` → `os01` → `kostrahoved` → `SBMENU…` i `paths` på `/tables`-treffet, i tillegg til stien under sin egen fagstatistikk (fysplan, barneverng, kommregnko, soshjelpk, barnehager, utgrs, pleie, helsetjko, tannhelse, kultur_kostra, vann_kostra, avfkomm, kirke_kostra, brann_kostra, eiendom_kostra, kombolig_kostra, miljo_kostra, vgu, kofola, kommregnfy m.fl.).

- **`paths` er eneste sikre kjennetegn.** `query=kostrahoved` gir 0 treff — node-ID-en er ikke søkbar. `query=kostra` gir 322 treff, men finner ikke Oslo-bydelstabellene («kostra» står ikke i tittel eller verdier der). Et sveip av hele katalogen (7 763 tabeller, 2026-09-20) gir **385 aktive KOSTRA-tabeller** — 232 (K), 96 (F), 52 (B), 5 uten suffiks — pluss 24 avsluttede. Sjekk `paths[*][2].id == "kostrahoved"`.
- **Andre kjennetegn i metadata:** variabel-ID-er som begynner på `KOK` og statistikkvariabler som begynner på `KOS` (se under). Titler som «KOSTRA-nøkkeltall for …», «Utvalgte nøkkeltall for …» og «… grunnlagstall …».
- **Søkeoppskrift:** `kostra` pluss fagterm (`kostra barnehage`, `kostra kommuneregnskap`, `kostra administrasjon`), eller `nøkkeltall` (67 treff) / `grunnlagstall` (10). Søket treffer SSBs egne labels bokstavelig: `kostra driftsresultat` finner *ikke* 12134, fordi statistikkvariabelen der heter «Netto **driftresultat** i prosent av brutto driftsinntekter» (SSBs skrivefeil, uten s). Får du ikke treff på en fagterm, prøv tabellens emne (`kommuneregnskap`) eller en trunkert form (`driftresultat*`). MCP-verktøyet `search_tables` dropper `paths` — bruk HTTP for søket eller `GET /tables/{id}` per kandidat (se `mcp-tools.md`).
- **Årlige.** 381 av 385 har `timeUnit: Annual` (de fire om lokale folkeavstemninger har periodeintervaller som `1970-2024`). Suffiks (K) kommune, (F) fylkeskommune, (B) Oslo-bydel. 317 av 385 starter i 2015 (omleggingen av KOSTRA-tabellene) — eldre serier ligger i avsluttede tabeller (`includeDiscontinued=true`). 372 har `lastPeriod` 2025; tre har inneværende år (14674 eiendomsskatt, 12842/12303 gebyrsatser per 1.1.). Noen få er i praksis døde uten `discontinued`-merke (12404, 12149: sist oppdatert 2018–2019, `lastPeriod` 2016) — sjekk `lastPeriod` og `updated`, ikke bare flagget.
- **Tre tabellfamilier:** «nøkkeltall» (forholdstall — 13526 «KOSTRA-nøkkeltall for miljøforvaltning (K)», 12134 «Utvalgte nøkkeltall for kommuneregnskap, kommunekonsern (K)», 14019, 12255), «grunnlagstall» (absolutte tall — 12292 «Omsorgstjenester - supplerende grunnlagstall (K)» med 49 statistikkvariabler), og temaspesifikke tabeller (13277 Husbanken, 13551 økonomisk oversikt drift etter art, 12367 detaljerte regnskapstall etter regnskapsomfang, funksjon og art). Sammenligning mellom kommuner → nøkkeltall; absolutte størrelser → grunnlagstall.
- **Kortnavn:** `paths[0][2].id`-regelen i `klass-vardok.md` gir fagstatistikkens kortnavn når den står først (12134: `kommregnko`, deretter `kostrahoved`); 29 tabeller har kostrahoved-stien først og 9 har bare den. `https://www.ssb.no/kostrahoved` redirecter til KOSTRA-siden, så begge er gyldige.

## Ureviderte tall 15. mars, reviderte 15. juni

SSB publiserer KOSTRA i to omganger for året før: **ureviderte (foreløpige) tall 15. mars** og **reviderte tall 15. juni**. Kommunene rapporterer innen 15. januar (helse/omsorg, sosialhjelp, barnevern), 15. februar (øvrige tjenestedata) og 22. februar (regnskap), og kan rette feil fram til 15. april. SSB: «De foreløpige nøkkeltallene per 15. mars kan være beheftet med feil.»

- **API-et flagger ikke ureviderte tall.** `status` er tomt for slike verdier, og tidsetiketten er bare årstallet. Det som skiller utgavene er `updated` på `/tables/{id}`: ligger den mellom 15. mars og 15. juni, har du ureviderte tall for siste år; etter 15. juni, reviderte. Verifisert 2026-09-20: 321 av 385 aktive tabeller har `updated` i juni 2026 (12134: `2026-06-15T06:00:00Z`), 44 i mars, 12 i juli–august.
- **Si det i svaret:** «Tallene for {år} er ureviderte/reviderte (publisert {dato fra updated})». Dataintegritet-regelen «Flagg foreløpige tall» i `SKILL.md` gjelder.
- Kommende publiseringer: `https://www.ssb.no/rss/statkal` og `/tables?pastDays=…` (se `api-details.md`). Feeden `https://www.ssb.no/rss/statbank/kostrahoved` svarer 200, men var tom 2026-09-20 (97 dager etter juni-publiseringen, utenfor 90-dagersvinduet) — om den bærer items i mars/juni er ikke verifisert.

## Variabel-ID-er: `KOK…` og `KOS…`

| Dimensjon                         | Variabel-ID                                                                                        | Merknad                                                                                                                                                                                                                                                                                                        |
| --------------------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Region, kommunetabeller (K)       | `KOKkommuneregion0000`                                                                             | **Ikke `Region`.** Kommunekoder + spesialkoder (under). 377 av 385 tabeller har en `KOK…region`-variabel (229 K, 96 F, 52 B); unntakene er eldre tabeller hektet på KOSTRA-menyen — tre med vanlig `Region` (07548, 07565 lokale folkeavstemninger, 12767 avstand til brannstasjon) og fem uten regionvariabel |
| Region, fylkeskommunetabeller (F) | `KOKfylkesregion0000`                                                                              | Fylkeskommunekoder + `EAFK…`                                                                                                                                                                                                                                                                                   |
| Region, Oslo-bydelstabeller (B)   | `KOKbydelsregion0000`                                                                              | 6-sifrede bydelskoder (`030101` Gamle Oslo) + `EAB` Alle bydeler i Oslo                                                                                                                                                                                                                                        |
| Statistikkvariabel                | `ContentsCode` med koder `KOS…0000`                                                                | `KOSbygsokrestrik0000`, `KOSAGD230000`, `KOSbelop0000` — fra 1 til 49 per tabell (median 5). Les labelen; kodene er ikke gjettbare                                                                                                                                                                             |
| Funksjon (tjenesteområde)         | `KOKfunksjon0000`                                                                                  | Opptil 97 koder: `100` Politisk styring, `120` Administrasjon, …                                                                                                                                                                                                                                               |
| Art (utgifts-/inntektsart)        | `KOKart0000`                                                                                       | `AGD10` Brutto driftsutgifter, `AGD2` Netto driftsutgifter, `A710` Sykelønnsrefusjon, …                                                                                                                                                                                                                        |
| Regnskapsbegrep                   | `KOKartkap0000`                                                                                    | Hovedtall i økonomisk oversikt                                                                                                                                                                                                                                                                                 |
| Regnskapsomfang                   | `KOKregnskapsomfa0000`                                                                             | `A` (Fylkes-)Kommunekonsern, `B` (Fylkes-)Kommunekasse                                                                                                                                                                                                                                                         |
| Balansedata                       | `KOKkapittel0000`                                                                                  | Balanseposter (13202)                                                                                                                                                                                                                                                                                          |
| Andre nedbrytninger               | `KOKalder0000`, `KOKeierforhold0000`, `KOKkjoenn0000`, `KOKtiltakstype0000`, `KOKheldeltid0000`, … | Varierer per tabell — over 100 ulike `KOK…`-ID-er i katalogen                                                                                                                                                                                                                                                  |
| Tid                               | `Tid`                                                                                              | Årstall                                                                                                                                                                                                                                                                                                        |

**Regionen og regnskapsdimensjonene må alltid velges.** Sveip av alle 385 tabeller: `elimination: false` på regionvariabelen i samtlige 377 som har den, på `KOKart0000` (23 av 23), `KOKartkap0000` (22 av 22), `KOKregnskapsomfa0000` (18 av 18), `KOKalder0000` (17 av 18) og `KOKfunksjon0000` (34 av 42). Eliminerbare er som regel bare rene nedbrytninger — `KOKeierforhold0000` (10 av 12), `KOKkjoenn0000` (8 av 8), `KOKtiltakstype0000`, `KOKheldeltid0000`. Les `elimination` per dimensjon; utelater du region, svarer API-et 400 `Missing selection for mandantory variable` — samme feilmelding som for `Tid`/`ContentsCode` ellers. På regnskapstabellene (funksjon × art × 360 kommuner × år) er defaultselection det trygge utgangspunktet; `*` på flere dimensjoner nærmer seg cellegrensen.

`role.geo` er satt på `KOKkommuneregion0000`, så Steg 3-heuristikkene i `SKILL.md` virker som normalt.

## Regionkoder — og hva landstallene er

| Kode                | Betydning                                                                                       | Finnes i |
| ------------------- | ----------------------------------------------------------------------------------------------- | -------- |
| `0301`, `4601`, …   | Kommuner, gjeldende og historiske (839 koder i 13526, inkl. sammenslåtte)                       | K        |
| `EAK`               | Landet                                                                                          | K        |
| `EAKUO`             | Landet uten Oslo                                                                                | K        |
| `EKA31`, `EKA32`, … | Fylker, med historiske varianter merket «(-2019)» og «(2020-2023)»                              | K        |
| `EKG01`–`EKG17`     | KOSTRA-grupper (kommunegrupper)                                                                 | K        |
| `EAFK`, `EAFKUO`    | Landet / Landet uten Oslo for fylkeskommunene                                                   | F        |
| `EAFK01`–`EAFK06`   | Fylkeskommune-regioner (Øst-Norge, Sør-Norge, Vest-Norge, Midt-Norge, Nord-Norge, Oslo kommune) | F        |
| `EAB`               | Alle bydeler i Oslo (47 av de 52 bydelstabellene)                                               | B        |

**Landet og Landet uten Oslo er estimerte tall, ikke rene summer.** Fra 2008 beregner SSB verdier for kommuner som ikke har rapportert, og gjennomsnittene for kommunegrupper, fylker og landet er *veide* etter innbyggertall for de fleste indikatorer (aritmetiske for indikatorer i absolutte tall; ingen for ja/nei-indikatorer). «Landet uten Oslo» finnes fordi Oslo-regnskapet dekker både kommune- og fylkeskommunefunksjoner — for enkelte økonomiske nøkkeltall er landsgjennomsnittet *med* Oslo prikket, så bruk `EAKUO` når du sammenligner kommuneøkonomi. Unntak: barnehager, grunnskole og samferdsel er fulltelling; gebyrer, saksbehandlingstid og lovanvendelse bruker aritmetisk snitt av rapporterende kommuner. Si i svaret at gruppe- og landstall er SSBs egne (estimerte, veide) tall — ikke lag egne summer eller snitt.

**KOSTRA-gruppene** deler kommunene i 17 grupper etter folkemengde, bundne kostnader per innbygger og frie disponible inntekter per innbygger, slik at kommuner sammenlignes med kommuner som ligner (Oslo og de åtte rikeste kommunene i egne grupper). Grupperingen oppdateres om lag hvert femte år; data fra og med 2020 bruker 2020-grupperingen, og tabellene bærer noten «brudd i tidsserien for KOSTRA-gruppene mellom 2019 og 2020» — på 12134 er den `noteMandatory` (`{"1": true}`) og skal vises. Hvilken gruppe en kommune tilhører står i Klass: klassifikasjon 112, korrespondansetabell gruppering → kommuneinndeling (gjeldende 2840 for 2026: Bergen 4601 → `EKG12`, Oslo 0301 → `EKG13`). Fylkeskommunegruppene er klassifikasjon 152 (korrespondanse 1310). Se `klass-vardok.md`. Gjett aldri gruppen — slå den opp, eller spør brukeren.

Sammenslåtte kommuner: de historiske kodene ligger i samme dimensjon som de gjeldende, og det finnes ingen `agg_KommSummer`-ekvivalent — velg gammel og ny kode og vis dem hver for seg.

## Kodelister: velg på label, ikke ID

Regionvariabelen har en fast familie kodelister med **stabile labels men tabellavhengige ID-er**: `agg_KOGkommuneregion0000NNNNN`, der suffikset følger tabellens region-valueset (13526, 12134 og 12367 bruker `…054xx`, 13277 `…029xx`). Verifisert på 13526:

| Label                                                            | Innhold                                                |
| ---------------------------------------------------------------- | ------------------------------------------------------ |
| Uttrekk for Landet                                               | `EAK`, `EAKUO`                                         |
| Uttrekk for Alle kommuner                                        | 841 koder, gjeldende og historiske                     |
| Uttrekk for Kommuner 2024-                                       | 360 gjeldende kommuner                                 |
| Uttrekk for Kommuner 2020-2023                                   | Kommuneinndelingen 2020–2023                           |
| Uttrekk for Alle fylker                                          | 35 koder: fylker inkl. historiske, pluss `EAK`/`EAKUO` |
| Uttrekk for Fylker 2024-                                         | 17 koder: 15 fylker pluss `EAK`/`EAKUO`                |
| Uttrekk for Fylker 2020-2023                                     | Fylkesinndelingen 2020–2023                            |
| Uttrekk for KOSTRA-grupperinger                                  | `EKG01`–`EKG17` pluss `EAK`/`EAKUO` (19)               |
| Kodeliste for KOSTRA-kommuner med tilhørende regionsgrupperinger | `vs_`-lista med alt (891)                              |

Fylkeskommunetabellene har «Uttrekk for Alle fylkeskommuner», «… Fylkeskommuner 2024-», «… 2020-2023» og «… -2019», og noen få har varianter «(uten aggregerte regioner)». Bydelstabellene har ingen kodelister. Sveip av alle 385: «Uttrekk for Landet» finnes på 298, kommunesettet på 213, fylkeskommunesettet på 85.

- **Ingen av dem aggregerer.** Hver kode har `valueMap` med ett element — «uttrekk» betyr undermengde. Summene for landet, fylker og grupper er egne koder (`EAK`, `EKAnn`, `EKGnn`) som SSB har beregnet, ikke noe kodelisten lager.
- **Hardkod aldri ID-en.** Hent `GET /tables/{id}/metadata`, les `dimension.KOKkommuneregion0000.extension.codelists` og velg listen med riktig `label`. Samme label kan ha ulik ID i neste tabell, og en feil ID gir 400 `Non-existent codelist`.
- Du trenger som regel ikke kodelisten: spesialkodene kan brukes direkte i `valueCodes` uten `codelist[…]` (eksemplene under gjør det).

## Regnskapstabellene

Regnskapstall publiseres for **kommunekonsern** (kommunen + kommunale foretak, interkommunale selskaper og samarbeid), og i enkelte tabeller også for **kommunekasse** (kommunen som juridisk enhet) og **konsolidert** regnskap. I API-et er det dimensjonen `KOKregnskapsomfa0000` (`A` konsern, `B` kasse) — 12367 og 13542 har den, 12134 og 13551 er konsern-only.

- 12367 «Detaljerte regnskapstall driftsregnskapet …» er grunnlagstabellen: regnskapsomfang × 97 funksjoner × 35 arter × kommune × år, én statistikkvariabel `KOSbelop0000` (1000 kr). 12362 gir utgifter per tjenesteområde (funksjon × art), 13551/13552 økonomisk oversikt drift/investering etter art, 13202 balansen (`KOKkapittel0000`), 12134/13542 de ni utvalgte nøkkeltallene (netto driftsresultat i prosent av brutto driftsinntekter, arbeidskapital, gjeld, …).
- **`extension.px.aggregallowed` er `false`** på 382 av 385 KOSTRA-tabeller (unntak: 09311 avløp og to folkeavstemningstabeller). Nøkkeltall er forholdstall og skal ikke summeres på tvers av kommuner eller grupper — bruk `EAK`, `EKGnn` eller fylkeskodene for SSBs egne aggregater. Beløp i kroner kan du summere, men da er summen din (Dataintegritet: merk egne beregninger).

## Konfidensialitet, noter og brudd

- **Prikking:** barnevern, sosialhjelp, kvalifiseringsstønad og bolig prikkes ved færre enn 3 enheter; pleie og omsorg ved færre enn 5 brukere. Landsgjennomsnitt med Oslo kan være prikket for økonomiske nøkkeltall. Vis `status`-symbolene (`.`, `..`, `:`) — se `troubleshooting.md`.
- **Obligatoriske noter** er vanlige (27 av 385 tabeller har `noteMandatory`), særlig bruddnoten for KOSTRA-gruppene og forklaringer av enkeltkommuners avvik («Kommune 1867 Bø har trukket sine innrapporterte regnskapstall for 2022»). Vis dem.
- **Brudd:** større brudd står i «Om statistikken» for delområdet (`https://www.ssb.no/<kortnavn>#om-statistikken`), mindre i informasjonsknappen per nøkkeltall i Statistikkbanken; kommunereformen 2020 har egen side. Kommunesammenslåinger gir tomme celler for gamle koder etter og nye koder før sammenslåingen.

## Strukturen endrer seg når rapporteringskravene endres

KOSTRA-tabellene er mindre stabile enn resten av Statistikkbanken: hva kommunene skal rapportere på endres (skjema, indikatorsett, lovkrav), og da endres tabellene. Statistikkvariabler kommer til og faller bort, og hele tabeller avsluttes og erstattes av nye med nytt ID. Verifisert 2026-09-20: 24 avsluttede KOSTRA-tabeller — 17 fra strukturen før 2015 (behovsprofil, «utvalgte nøkkeltall nivå 1», sysselsetting; avsluttet 2016) og hele sosialtjeneste-settet 12210, 13138, 12203, 12213, 12266, 12204, 12201 «(avslutta serie) 2015–2021», erstattet av 14019 m.fl. fra 2022 — og 61 aktive tabeller startet *etter* 2015-omleggingen (26 i 2020, 10 i 2021, 9 i 2022, 3 i 2024). SSBs egen dokumentasjon: «en god del endringer i statistikkopplegget, noe som har medført en del brudd i tidsserier».

Konsekvenser:

- Hent metadata i *denne* samtalen før hver spørring. En `KOS…`-kode eller tabell-ID fra en tidligere samtale eller et tidligere år kan være borte — det gir 400 `Non-existent value` eller 404.
- Sjekk `discontinued` på treffet og «(avslutta serie)» i tittelen; finn etterfølgeren ved å søke på fagtermen, ikke på det gamle ID-et.
- Tomme celler for de første årene av en variabel betyr som regel at den ikke fantes da — ikke at kommunen manglet.
- Strukturelle endringer dokumenteres på SSBs endringsside (lenke i `api-details.md`); definisjonene for tabeller avsluttet før 2018 ligger i et eget dokument lenket fra dokumentasjonssiden.

## Verifiserte eksempler

- `https://data.ssb.no/api/pxwebapi/v2/tables/13526/data?lang=no&valueCodes[KOKkommuneregion0000]=EAK,EAKUO,EKG12,0301&valueCodes[ContentsCode]=KOSbygsokrestrik0000&valueCodes[Tid]=top(1)` — andel innvilgede byggesøknader i restriksjonsområder 2025: landet 50.3, landet uten Oslo 50.3, KOSTRA-gruppe 12 47.5 prosent (1 desimal fra `category.unit`); Oslo har `status` `..` og skal vises som manglende, ikke droppes
- `https://data.ssb.no/api/pxwebapi/v2/tables/12134/data?lang=no&valueCodes[KOKkommuneregion0000]=4601,EKG12,EAKUO&valueCodes[ContentsCode]=KOSAGD230000&valueCodes[Tid]=top(3)` — netto driftsresultat i prosent av brutto driftsinntekter 2023–2025: Bergen 0.7 / -2.4 / 1.0, KOSTRA-gruppe 12 1.6 / 0.1 / 3.2, landet uten Oslo 1.0 / -0.3 / 2.1. Responsen har `noteMandatory` på bruddnoten
- `https://data.ssb.no/api/klass/v1/correspondencetables/2840.json` — gruppetilhørighet per kommune, 2026-inndelingen (357 rader)

Utelates `valueCodes[KOKkommuneregion0000]` fra den første URL-en, svarer API-et 400 `Missing selection for mandantory variable`.

## Sjekkliste før du svarer

1. Er tabellen KOSTRA? (`kostrahoved` i `paths`, `KOK…`-variabler)
2. Region-ID lest fra metadata (`KOKkommuneregion0000` / `KOKfylkesregion0000` / `KOKbydelsregion0000`), og alle dimensjoner angitt
3. Kodeliste valgt på label, ikke ID — eller spesialkodene brukt direkte
4. KOSTRA-gruppe slått opp i Klass, ikke gjettet
5. `updated` sjekket mot 15. mars / 15. juni — urevidert eller revidert oppgitt
6. Obligatoriske noter og `status` vist; landstall omtalt som SSBs estimerte, veide tall
7. Nøkkeltall ikke summert; egne beregninger merket
8. Koder lest fra dagens metadata, ikke fra hukommelsen — strukturen endres
