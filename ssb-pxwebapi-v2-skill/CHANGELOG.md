# Endringslogg — ssb-pxwebapi-v2

Hva som er annerledes for deg som bruker skillen, nyeste først. Gjeldende versjon står i `SKILL.md`-frontmatter under `metadata.version`; har din kopi ingen `metadata.version`, er den fra før 2026-06-12 — last ned ny.

Hva som er verifisert, hvor og når, står i vedlikeholderens logg, [`DEVLOG.md`](https://github.com/janbrus/pxwebapi-skills/blob/main/ssb-pxwebapi-v2-skill/DEVLOG.md). Den ligger i repoet, ikke i zip-en.

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
