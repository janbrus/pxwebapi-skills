# Ändringslogg — scb-pxwebapi-v2

Vad som är annorlunda för den som använder skillen, nyast först. Gällande version står i `SKILL.md`-frontmatter under `metadata.version`; saknar din kopia `metadata.version` är den från före 2026-06-12 — hämta ny. Versioner under 1.0.0 markerar beta-status (se README).

Vad som verifierats, var och när, står i underhållarens logg, [`DEVLOG.md`](https://github.com/janbrus/pxwebapi-skills/blob/main/scb-pxwebapi-v2-skill/DEVLOG.md). Den finns i repot, inte i zip:en.

## 0.11.1 — 2026-10-02 (beta)

- **Rättat: `status` betyder inte alltid att värdet saknas.** En cell med datanot behåller sitt tal. Läs `value` och `status` var för sig, visa ett flaggat tal med flaggan och filtrera aldrig bort `null` före indexering. Hos SCB är det inte observerat: i 13 kontrollerade tabeller står `..` alltid på `null`.
- **Rättat:** strukturexemplet i `references/json-stat2.md` hade ett tal i en cell vars status sa att värdet saknades.
- Nytt i `references/json-stat2.md`: ett räkneexempel med två dimensioner som varierar (TAB6471), att API:et inte sorterar (`category.index` följer ordningen i frågan), och att man itererar över `id`, aldrig över `Object.keys(dimension)`.
- Nytt: `SKILL.md` länkar SCB:s handbok för PxWebApi v2, och README har fått en sektion **Dokumentation** med handboken, OpenAPI, PxApiSpecs och v1→v2-konverteraren.

## 0.11.0 — 2026-09-07 (beta)

- **Rättat: exemplens huvudtabell hade slutat uppdateras.** TAB638 stannade 2024 utan `discontinued`-flagga; exemplen använder nu TAB6471. Ny regel: `discontinued` är inget aktualitetstest — jämför `lastPeriod` med dagens datum.
- **Rättat: `role.geo` finns inte hos SCB.** Leta efter en geografisk variabel i `id` innan du antar att data gäller hela Sverige.
- **Rättat:** `eliminationValueCode` och `firstPeriod`/`lastPeriod` är inga metadatafält; exemplens sökord hittar nu tabellen de använder; standardoperatorn i sökningen är AND, och wildcards matchar den stammade termen (`folkmäng*`, inte `folkmängd*`).
- **Rättat: `range()` och andra uttryck med komma ska stå inom hakparenteser i en GET-URL** (`[range(2024M01,2024M03)]`); i POST skrivs de utan.
- Nytt: obligatoriska noter ska visas; CKM-bruset från referensår 2025 (redovisade totaler är inte alltid summan av delarna); eliminerbarhet är en egenskap hos tabellen; kodlistans egna koder gäller i `valueCodes`; SCB skickar `X-Rate-Limit-*`-headers.
- Nytt: curl behöver `-g`; uttryck och koder kan blandas; csv levereras som `iso-8859-1`; en GET-URL över ca 2 100 tecken ger 404; en upprepad värdekod ger 500 med tom body.
- `SKILL.md` är kortare; ingenting är borttaget, materialet ligger i `references/` (två nya filer: `mcp-tools.md` och `search-syntax.md`). Zip:en heter nu `scb-pxwebapi-v2-skill.zip` och har toppmapp, README, denna logg och MIT-`LICENSE`. README beskriver installation i ChatGPT och Codex.

## 0.10.0 — 2026-08-30 (beta)

- **Nytt: dataintegritetsregeln.** Ange aldrig en siffra som inte hämtats från API:et i samtalet, ta inga siffror ur minnet eller från andra källor, och säg ifrån när API:et fallerar.
- **Rättat:** felmeddelandet citeras nu exakt, med SCB:s egen stavning `"Missing selection for mandantory variable"`.
- **Rättat:** `extension` i `references/json-stat2.md` listade `/tables`-fält som `firstPeriod`/`lastPeriod`; nu den faktiska strukturen.
- Nytt: ett `GET /data` utan urval ger tabellens förval, som kan summera bort dimensioner utan att säga det. Föredra `top(N)`/`from(värde)` för tid.

## 0.9.0 — 2026-06-12 (beta)

- **Nytt: versionering** — `metadata.version` i `SKILL.md`, och denna logg.
- Nytt: «Verktygsval» med pxweb-mcp-verktygen och deras begränsningar — `language` stödjer bara `no`/`en`, och servern måste startas med SCB:s `--url` (standard är SSB).
- Nytt: svar kommenterar bara siffror från det egna uttaget; data från andra källor hämtas aldrig in i samma svar.

Utgåvor före 2026-06-12 saknade versionsnummer.
