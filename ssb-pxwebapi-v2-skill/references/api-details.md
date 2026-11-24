# API-detaljer (PxWebApi v2 hos SSB)

Praktisk driftsinformasjon for SSBs PxWebApi v2. For json-stat2-formatet (Dataset-struktur, indeksering, status-koder) — se `json-stat2.md`.

**Innhold**

1. Praktisk driftsinformasjon: publiseringstider, KOSTRA-rytme, cellegrense, rate limit, URL-lengde, lisens
2. Spesifikasjon, veiledning og kontakt: OpenAPI, brukerveiledninger, e-post
3. Rate limit-headere: `x-ratelimit-*`
4. Kall fra nettleseren (CORS): preflight teller, headerne kan ikke leses, GET framfor POST
5. RSS-feeds: publiseringskalender, oppdaterte tabeller, «Når kommer neste tall?»

---

## Praktisk driftsinformasjon

- Nye tall publiseres vanligvis kl. 08.00. Unngå spørringer 07.55–08.15 ved høy belastning.
- Tall som skal revideres kl. 08 vises som 0 eller prikk i tidsrommet 05.00–08.00, og 0 kommer uten `status`. Det gjelder serier der tidligere publiserte tall endres, i hovedsak nasjonalregnskap og sesongjusterte serier. Ellers legges nye tall bare til.
- Metadata oppdateres kl. 05.00 og 11.30 — tabellene er utilgjengelige under oppdatering.
- KOSTRA (385 aktive tabeller under `paths`-noden `kostrahoved`) har egen årsrytme: ureviderte tall for året før 15. mars, reviderte 15. juni; kommunene retter innen 15. april. API-et flagger ikke ureviderte verdier i `status` — `updated` på `/tables/{id}` mot kalenderen avgjør (verifisert 2026-09-20: 321 tabeller oppdatert i juni, 44 i mars). Se `kostra.md`.
- API-grense: 800 000 celler per uttrekk (tomme celler teller med). Rate limit: 40 spørringer per minutt (`x-ratelimit-policy: 40;w=60s`, bekreftet 2026-09-09) — les gjeldende verdi fra `x-ratelimit-*`-responsheaderne (se under), ikke fra `/config`. SSBs brukerveiledning oppgir 30 per minutt; headeren er autoritativ når de to avviker.
- GET-URL kan ikke overstige ca. 2 100 tegn — over det svarer API-et 404. Bruk POST for komplekse spørringer.
- Desimalskilletegn er `.` (punktum) i alle tekstformater. xlsx har ekte tall, og Excel viser desimalskilletegnet etter egen språkinnstilling, uansett `lang`.
- Lisens: Creative Commons CC BY 4.0.
- Strukturelle endringer i tabeller dokumenteres på: https://www.ssb.no/statbank/hvordan-bruke-statistikkbanken/endringer-i-statistikkbanktabeller
- `navigation`-endepunktet fra v1 er tatt bort i v2 (gir 404). Emnehierarkiet leses i stedet fra `paths` på hvert `/tables`-treff — se `klass-vardok.md` for kortnavn-utledning.

---

## Spesifikasjon, veiledning og kontakt

| Ressurs                                   | URL                                                                  |
| ----------------------------------------- | -------------------------------------------------------------------- |
| SSBs brukerveiledning (norsk / engelsk)   | https://www.ssb.no/api/pxwebapiv2 · https://www.ssb.no/en/api/pxwebapiv2 |
| OpenAPI-spesifikasjon (interaktiv)        | https://data.ssb.no/api/pxwebapi/v2/index.html                       |
| PxApiSpecs (YAML, felles for PxWeb-miljøet) | https://github.com/PxTools/PxApiSpecs/blob/master/PxAPI-2.yml      |
| PxTools' generelle brukerguide            | https://www.pxtools.net/PxWebApi/documentation/user-guide/ · Markdown-kilden: https://raw.githubusercontent.com/PxTools/pxtools.github.io/main/docs/PxWebApi/documentation/user-guide.md |
| Kodeeksempler (Python, R, JS) og skillene | https://github.com/janbrus/pxwebapi-skills (SSBs veiledning lenker til det gamle navnet `ssb-api-v2-examples`, som redirecter hit) |
| Spørsmål om tabeller eller API-et         | statistikkbanken@ssb.no                                              |
| Feil og forslag til API-et                | https://github.com/PxTools/PxApiSpecs · https://github.com/PxTools/PxWebApi |

Den engelske veiledningen dekker kun SSB-spesifikke forhold (grenser, publiseringstider, standardtegn, lagrede spørringer) og delegerer resten til PxTools-guiden. Den norske er komplett.

---

## Rate limit-headere

Rate limiting annonseres i HTTP-responsheadere. Feltene `maxCallsPerTimeWindow`/`timeWindow` står fortsatt i `/config`-responsen, men er nullstilt til `0` og ikke lenger i bruk — `0` betyr **ikke** «ingen grense». Eksempel fra en respons:

| Header                  | Eksempelverdi | Betydning                                        |
| ----------------------- | ------------- | ------------------------------------------------ |
| `x-ratelimit-limit`     | `40`          | Maks antall kall i tidsvinduet                   |
| `x-ratelimit-policy`    | `40;w=60s`    | Grense + vinduslengde: 40 kall per 60 sekunder   |
| `x-ratelimit-remaining` | `39`          | Gjenstående kall i inneværende vindu             |
| `x-ratelimit-resource`  | `SB_API_1MIN` | Grense-ressursen kallet telles mot               |

Les `x-ratelimit-remaining` fra svarene du likevel får, og send aldri kall bare for å sjekke den. Ved mange kall: hold deg til omtrent halve grensen med et vindu som teller hvert kall, ikke en fast pause mellom kallene. Ved 429: se `troubleshooting.md`. Verdiene kan endres av SSB — les headerne, hardkod dem ikke (fra en nettleser går ikke det, se under).

---

## Kall fra nettleseren (CORS)

API-et svarer `access-control-allow-origin: *`, så en nettside kan kalle det direkte. Men nettleseren gjør regnestykket annerledes:

- **Grensen kan ikke leses.** SSB sender ingen `access-control-expose-headers`, så JavaScript ser ikke `x-ratelimit-*`, og `/config` har 0. Hardkod 40 kall per 60 s (per 2026-11-10) og tell kallene selv.
- **Preflighten teller.** En JSON-POST sender først en `OPTIONS`-preflight, og den telles som et kall (`x-ratelimit-remaining` 39 → 38 → 37 over GET, OPTIONS, GET; målt 2026-11-09 og 2026-11-10). SSB sender ingen `access-control-max-age`, så nettleseren gjenbruker preflighten i høyst 5 sekunder og bare for samme URL. I praksis koster en JSON-POST 2 kall. En GET med bare `Accept`-header sender ingen preflight og koster 1.

Fra nettleseren: bruk GET så lenge URL-en holder seg under ca. 2 100 tegn, og POST først når den blir for lang.

---

## RSS-feeds

Komplement til `/tables?pastDays=…` når du vil overvåke publiseringer uten å polle API-et:

| Feed                                         | Innhold                                                                                                                                                                                                                   |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `https://www.ssb.no/rss/statkal`             | Planlagte publiseringer, ca. fire uker fram (publiseringskalender). Tittel: «dd.mm.åååå: Statistikk, Tall for <periode>»                                                                                                   |
| `https://www.ssb.no/rss/`                    | Publiserte statistikker og artikler fra de siste dagene. Artiklene har tomt kortnavn                                                                                                                                      |
| `https://www.ssb.no/rss/statbank`            | Oppdaterte tabeller fra de siste ca. 5 dagene, med `<ssbrss:tableid>`                                                                                                                                                     |
| `https://www.ssb.no/rss/statbank/{kortnavn}` | Siste oppdatering per tabell i én statistikk, siste 90 dager. Månedstabeller viser bare siste måned, og tabeller som ikke er oppdatert på 90 dager, mangler — ingen fullstendig tabelliste. Ukjent kortnavn gir 200 og tom feed, ikke 404 |

Feedene er vinduer, ikke arkiver: det som faller ut, er borte. Alle tar `?lang=en`.

`{kortnavn}` er statistikkens kortnavn — står som `KORTNAVN:<kortnavn>` i `link.related[].extension.metaid` i metadata og er som regel 3. nivå i `paths` fra `/tables`-respons (krysslistede tabeller: se `klass-vardok.md`), siste ledd i `ssb.no/<kortnavn>`-URL-er, og verdien av `<ssbrss:shortname>`-elementet i RSS-itemene (f.eks. `arblonn`, `kpi`).

Bruksområder:

- **«Når kommer neste tall for X?»** API-et har ingen publiseringskalender. Finn kortnavnet (tredje node i `paths`, eller `link.related[0].extension.metaid`), hent `rss/statkal` og velg postene med samme `<ssbrss:shortname>`. Datoen står i `<ssbrss:date>`, og perioden etter siste komma i tittelen («Tall for oktober 2026»). Mangler kortnavnet, er det ingen publisering innen vinduet: hent `https://www.ssb.no/<kortnavn>` og les datoen etter «Neste oppdatering:» (siden er server-rendret og rekker lenger fram). Ikke si at det ikke kommer flere tall.
- `statbank/{kortnavn}`-feeden: overvåk en spesifikk statistikk uten å bygge polling-logikk
- Rot-feeden: vis hva som er publisert nylig på tvers av temaer. Artikler har tomt kortnavn: ligger lenken under en statistikkside (`…/statistikk/<side>/artikler/…`), hører artikkelen til den statistikken; ellers hører den til et emne (`…/<emne>/artikler/…`)
