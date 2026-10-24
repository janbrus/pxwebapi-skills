# Endringslogg — ssb-pxwebapi-v2

Hva som er annerledes for deg som bruker skillen, nyeste først. Gjeldende versjon står i `SKILL.md`-frontmatter under `metadata.version`; har din kopi ingen `metadata.version`, er den fra før 2026-06-12 — last ned ny.

Hva som er verifisert, hvor og når, står i vedlikeholderens logg, [`DEVLOG.md`](https://github.com/janbrus/pxwebapi-skills/blob/main/ssb-pxwebapi-v2-skill/DEVLOG.md). Den ligger i repoet, ikke i zip-en.

## 1.6.5 — 2026-10-23

- Rådet «Start smalt» er tatt ut av Steg 4. Grensen `maxDataCells` står.
- Regelen om obligatoriske variabler står med vanlige bokstaver og sier hvorfor: mangler en av dem, svarer API-et 400.
- **Rettet:** Skillen sa at tabell-ID-er er permanente. En erstattet tabell kan være fjernet helt (404). Claude slår da opp ny ID på SSBs side over endringer i statistikkbanktabeller.
- Nytt: «Når kommer neste tall?» besvares via statistikkens kortnavn, fra SSBs publiseringskalender eller, lenger fram, fra statistikksiden.
- Nytt: tabellsøket bruker `pageSize=50`, så brede søk ikke kutter bort riktig tabell.
- Dataintegritet i `SKILL.md` er kortere. Punktene har regelen, og detaljene står i referansefilene: prognoser, framskrivinger og ferdige per innbygger-tall i `common-tables.md`, avsluttede og fjernede tabeller i `troubleshooting.md`.
- Nytt: Claude kan slå opp i SSBs Klass hvilke kommunekoder som endret seg når (sammenslåinger, delinger, nye navn, grenseendringer), hvilke koder som gjaldt på en dato, og KOSTRA-gruppe på en dato.
- Klass-oppslag bruker ikke lenger `.json` i URL-en, som SSB har varslet at fjernes.
- **Rettet:** Skillen nevnte bare sammenslåingene i 2020 som grunn til at kommunekoder endrer seg. Fylkesdelingen i 2024 ga også nye koder.
- **Rettet:** Skillen sa at SN2007-tabellene oppdateres parallelt med SN2025. De fleste avsluttes når SN2025-tabellen kommer; bare noen, som konkursene, går på begge.
- Nytt: varsel om at også femsifrede næringskoder kan ha fått nytt innhold i SN2025. En kode som mangler i SSBs korrespondansetabell i Klass, er uendret.

## 1.6.4 — 2026-10-21

- Nytt: Er en MCP-server mot SSB tilkoblet, for eksempel pxweb-mcp, laster Claude skillen før den bruker verktøyene. Da gjelder reglene for tabellvalg, koder, tall og kildehenvisning også der. Uten skillen gikk Claude ofte rett til verktøyene. Dette er målt med servernavn som nevner SSB eller pxweb, så gi serveren et slikt navn, for eksempel `pxweb-ssb`.
- Nytt: v2 vinner. Flere andre MCP-servere mot SSB bruker det gamle v0-API-et. Skillen bruker pxweb-mcp eller HTTP mot v2 når en av dem finnes, og et v0-verktøy bare når ingen v2-kanal finnes.
- Visualiseringsskillen omtales med sitt installerte navn, `ssb-chart`, ikke `ssb-chart-skill`.

## 1.6.3 — 2026-10-13

- **Rettet: søketipset om fagtermer.** «folkemengde» finner ikke 07459, og norske ord gir 0 treff med `lang=en`, fordi søket følger språket. De nye eksemplene er «konsumprisindeks» (ikke «inflasjon») og «brukte boliger» (ikke «boligpriser»), og med `lang=en` søker du på engelsk. Søket leter ikke i emnenavn, og gir 20 treff per side.
- **Rettet: prosentkod æ, ø og å i URL-en.** `curl -g` koder dem ikke, og rå UTF-8 gir 400.
- **Rettet: xlsx anbefales når dataene skal i Excel.** Tallene kommer som ekte tall, og Excel velger desimaltegn selv, uansett `lang` — det er ikke API-et som gir komma. Skal fila pivoteres, er csv bedre, fordi xlsx bare skriver radtekstene på første rad i hver blokk.
- **Rettet:** mot en lagret spørrings `/data` virker bare gjentatte `outputFormatParams`, ikke kommaformen.
- **Rettet: fylkeseksemplet.** `agg_KommFylker` med `*` gir ikke bare fylkene, men også Svalbard, Jan Mayen og «Kontinentalsokkelen og uoppgitt» (med 0 i befolkningstabellen). Ta dem ut før rangering eller diagram.
- Nytt: per innbygger-tall du regner ut selv, deles på middelfolkemengden når størrelsen måles over en periode (BNP, inntekt), og på folketallet samme dato når den måles på et tidspunkt. Skillen sier hvilken nevner den brukte, og bruker SSBs ferdige per innbygger-tall når de finnes, med mindre de mangler serier eller perioder, eller bygger på en eldre revisjon. Middelfolkemengden (03037) står nå i `common-tables.md`.
- Nytt: SSBs prognoser kalles prognoser, og for en framskriving oppgis alternativet. I 12880 er de fire siste årene alltid prognoser (`top(4)`); siste regnskapsår er `[top(1,4)]`.
- Nytt: kildehenvisningen har datoen tabellen sist ble oppdatert: «Kilde: SSB, tabell {id}. Sist oppdatert: {dato}.», som i `ssb-chart-skill`.
- Nytt: AKU-ledighet (13760) hentes som sesongjustert tremåneders glidende gjennomsnitt (`3MGG`); siste måned er `..`, så skillen henter to måneder og oppgir tremånedersperioden.
- Nytt: Forbruksundersøkelsen (14100) i `common-tables.md`. Skillen henter standardfeil eller feilmargin når tabellen har det, før den kaller en forskjell reell, og sier hvilke koder et vagt begrep som «mat» ble til.
- KPI-noten om avrunding behandles som andre obligatoriske noter: den vises, uten egen omtale i skillen.
- `SKILL.md` er rundt en tiendedel kortere. Dobbeltomtale er fjernet, og detaljer står i referansefilene. Det engelske eksempelet er fjernet, fordi søket det viste, ikke fant tabellen.

## 1.6.2 — 2026-10-11

- **Rettet: koder fra en summerende kodeliste virker bare med kodelisten angitt.** `F-03`, `K-3103` og aldersgruppen `F00-04` gir feil uten `codelist[…]`; bare koder fra tabellens egen verdiliste virker uten. Skillen leser kodene fra kodelisten i stedet for å gjette dem.
- Nytt: lange kommuneserier. `agg_KommSummer` (`K-3103`, 07459) går tilbake til 1986; `agg_KommSummerHist` (`K_3103`, 06913) går tilbake til den store kommunereformen i 1965. Begge har samme label, så skillen skiller dem på ID.
- **Rettet: om en tabell er avsluttet, står bare på søketreffet og `GET /tables/{id}`** — og feltet `discontinued` er bare med når svaret er ja. Mangler det, er tabellen aktiv. Metadata og data-responsen sier ingenting om det.
- **Rettet:** kodelistene `agg_RegHFRHF` og `agg_Nace17` finnes ikke og er fjernet. KPI har 13 hovedgrupper, ikke 12. I en POST-body gir hakeparenteser rundt et uttrykk feil.
- Nytt: `agg_` betyr ikke alltid summering — det er `valueMap` som avgjør. En kommune eller et fylke som ikke fantes et år, gir 0 uten statusmerking, og vises ikke som tall. En kode med `+` (`105+`) skrives `%2B` i en GET-URL. `from()` og `to()` i samme liste gir alle periodene i begge, ikke intervallet mellom.
- Lagrede spørringer har egen referansefil, `references/saved-queries.md`. Steg 6 sier nå det SSB anbefaler: en vanlig URL med `top()`/`from()` til automatisering. Skillen tilbyr ikke lenger en lagret spørring av seg selv, og vet at en gammel lagret spørring leveres uten de lagrede formatparameterne (f.eks. semikolon).
- **Rettet: noter per variabel og per verdi er ikke obligatoriske hos SSB.** Bare tabellnotene som `extension.noteMandatory` peker på, skal alltid med i svaret.
- Referansefilene `json-stat2.md`, `codelists-and-filters.md` og `common-tables.md` har fått innholdsliste. `json-stat2.md` har sju regler for å lese et uttrekk først, og PX-nøkkelordet ved hvert felt som kommer fra PX-filen. `codelists-and-filters.md` har generelle regler og filteruttrykk først, og er en tredjedel kortere. `common-tables.md` har fått 12910 (økonomisk struktur etter næring) og 14701 (årlig KPI, erstatter 03014).
- KOSTRA-rutingen nevner også skole. Eksempelet «Hvor mange bor i Oslo?» henter 07459 fra `common-tables.md`, fordi søket `folkemengde` ikke finner tabellen, og KPI-eksempelet velger totalen (`VareTjenesteGrp=00`) i stedet for å utelate varegruppen. Kontrakter som viser til KPI, bruker oftere endringen desember–desember i 14700 enn årsendringen i 14701, og skillen sier det.

## 1.6.1 — 2026-10-02

- **Rettet: `status` betyr ikke alltid at verdien mangler.** En celle med datanote beholder tallet: 09842 har `*` (foreløpig tall) på BNP-tall som finnes. Vis tallet med tegnet, og filtrer aldri bort `null` før indeksering. `-` (null) vises som `-` og regnes ikke som 0.
- **Rettet: kortnavnet til statistikken** (for `ssb.no/<kortnavn>` og RSS) kan ikke alltid leses fra første sti i `paths`. Hører tabellen til flere statistikker, avgjør `extension.metaid` i metadata.
- Nytt i `references/json-stat2.md`: et utregnet indekseringseksempel med to dimensjoner som varierer, at `category.index` følger rekkefølgen i spørringen, og at du itererer over `id`, ikke over `Object.keys(dimension)`.
- Nytt i `references/output-formats.md`: parquet er beta, og kolonnene heter etter variabelens navn på valgt språk.
- Nytt i repoet, ikke i zip-en: `docs/llms.txt` (utkast til `data.ssb.no/llms.txt`) og diagrammer over arbeidsflyten i `docs/`.

## 1.6.0 — 2026-09-20

- **Nytt: SN2025.** SSB går over fra SN2007 til SN2025, og næringstabellene finnes i to parallelle varianter. Bokstavkodene er forskjøvet (SN2007 K er ikke SN2025 K), så skillen sier hvilken standard tallene bygger på og skjøter aldri de to på næringsnivå.
- **Nytt: regionale nivåer under kommune** — bydel, delområde og grunnkrets, med kodeformer og hvilke tabeller som finnes.
- **Nytt: KOSTRA** (`references/kostra.md`): egne variabel-ID-er i stedet for `Region`, spesialkoder for landet og KOSTRA-gruppene, estimerte landstall, og ureviderte tall i mars og reviderte i juni uten `status`-flagg.
- `references/common-tables.md` har fått rader for SN2025, grunnkrets og KOSTRA (rundt 90 tabeller).
- Nytt i repoet, ikke i zip-en: `docs/brukerveiledning.md` og `docs/instruks-kort.md` (kondensert instruks for plattformer uten skill-støtte). README beskriver installasjon i ChatGPT og Codex, og zip-en har MIT-`LICENSE`.

## 1.5.0 — 2026-09-03

- **Rettet: uttrykk med komma må stå i hakeparenteser i en GET-URL** (`[range(2020,2022)]`, `[top(3,2)]`); POST trenger det ikke. Filteruttrykk kan kombineres med enkeltkoder.
- **Rettet:** variabel- og verdikoder er ikke case-sensitive (kodeliste-ID-er er det); 07459 tilbyr ikke `vs_Fylker2024`; standardoperatoren i søk er AND, ikke OR; rate limit står i responsheaderne, ikke i `/config`.
- Nytt: curl trenger `-g`; en gjentatt verdikode gir 500 med tom body; en URL over ca. 2 100 tegn gir 404; CSV leveres som `iso-8859-1`; wildcards virker også på tid og andre dimensjoner (`2024*`, `??`).
- Nytt: lagrede spørringer fra v1-tiden kan hentes via `/savedqueries/{id}`, og «Lagre» i Statistikkbanken låser perioder som må skrives om til `top()`/`from()` før deling.
- Nytt: egen seksjon for ruting til andre skills. `SKILL.md` er kortere; ingenting er fjernet, stoffet er flyttet til `references/`. Eksemplene viser form, ikke tall.

## 1.4.1 — 2026-08-30

- **Nytt: obligatoriske noter** (`noteMandatory`) skal vises. På KPI-tabellene varsler noten at endringstall du regner ut selv, kan avvike fra de publiserte.
- **Rettet:** `elimination` leses bare fra metadata; i en data-respons beskriver feltet uttrekket. `eliminationValueCode` finnes bare i data-responser.
- **Rettet:** `outputValues[Var]` har ingen virkning hos SSB — det er kodelisten som aggregerer. 400-feil diagnostiseres med `title`, ikke `detail`. Dataset-`extension` har ikke `firstPeriod`/`lastPeriod`.
- Nytt: oppgi kodeliste og utelatte dimensjoner i svaret, siden responsen ikke registrerer dem. `aggregallowed: false` er et tolkningssignal, ikke en sperre.
- Nytt: SSB kjører fortsatt v1 på `/api/v0/` (rutes til `generic-pxweb-v1-skill`), og R-pakken `PxWebApiData` støtter begge versjonene.

## 1.4.0 — 2026-08-27

- **Nytt: dataintegritetsregelen.** Oppgi aldri et tall som ikke er hentet fra API-et i samme samtale: ingen tall fra hukommelsen eller andre kilder, ingen interpolering, merk egne beregninger og behold API-ets presisjon.
- Nytt i Steg 5: skill hentede tall fra egne beregninger, vis GET-URL eller POST-body, og vis `status`-merkede verdier som de er.
- **Rettet:** `ContentsCode` for 14700 er `Tolvmanedersendring`. Den avsluttede tabellen 10261 er byttet med 14824 i `references/common-tables.md`.
- Nytt: `parquet` er dokumentert i `SKILL.md`.

## 1.3.1 — 2026-08-05

- **Rettet: rate limit annonseres i responsheaderne** (`x-ratelimit-*`), ikke i `/config`, der feltene er nullstilt. `0` betyr ikke «ingen grense».

## 1.3.0 — 2026-07-29

- Nytt: `link.related` i metadata gir ferdige lenker til statistikksiden, «Om statistikken» og definisjonssidene, og `extension.metaid` gir kortnavnet direkte.

## 1.2.0 — 2026-06-15

- Nytt: foretrekk `top(N)`/`from(verdi)` for tid, så delbare URL-er og lagrede spørringer holder seg oppdatert.
- Nytt: pyjstat (Python) og `PxWebApiData` (R) er dokumentert.

## 1.1.0 — 2026-06-12

- **Nytt: versjonering** — `metadata.version` i `SKILL.md`, og denne loggen.
- Nytt: «Verktøyvalg» med `pxweb-mcp`-verktøyene og begrensningene deres (`references/mcp-tools.md`).
- Nytt: en GET uten seleksjon gir tabellens defaultselection, ikke hele tabellen.
- Nytt: svar kommenterer bare tall fra eget uttrekk; data fra andre kilder hentes aldri inn i samme svar.
- **Rettet:** Excel-eksempelet for 07221 brukte en `ContentsCode` som ikke finnes.

Utgaver før 2026-06-12 var uversjonerte.
