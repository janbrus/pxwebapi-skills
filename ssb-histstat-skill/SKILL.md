---
name: ssb-histstat
description: Norsk historisk statistikk fra SSB (1828-2010) — digitaliserte publikasjoner under ssb.no/a/histstat/. Bruk når brukeren spør om historiske norske tall fra før Statistikkbanken-perioden, eldre folketellinger, NOS-publikasjoner (Norges offisielle statistikk), Statistisk årbok, "Historisk statistikk"-utgavene, eller tidsserier som strekker seg lenger tilbake enn ssb-pxwebapi-v2 dekker. Trigger på "historisk statistikk", "NOS", "Norges offisielle statistikk", "folketelling 1769/1801/1865/...", "Statistisk årbok", "tall fra 1800-tallet", årstall før 1980 kombinert med statistikkbegreper (befolkning, lønn, priser, handel, jordbruk, fiske, industri, skole, fattigvesen), eller når ssb-pxwebapi-v2 ikke har data så langt tilbake. Also trigger on "Norwegian historical statistics", "Statistics Norway historical", "Norway 19th century data".
license: MIT. LICENSE has complete terms
metadata:
  version: "0.9.0"
---

# SSB Historisk statistikk

Naviger og søk i SSBs digitaliserte historiske publikasjoner (1828–2010). **Start alltid på huben `https://www.ssb.no/a/histstat/publikasjoner/`** — SSBs egen, autoritative katalog som `curl` henter komplett (~190 lenker) og som koder hele beslutningstreet (organisert *Etter emne* og *Etter serie*). PDF-ene, NOS-indeksen og alle serie-/emneindekser er stabile og `curl | grep`-bare.

**Felle (viktigst):** rot-stiene `/a/histstat/histemne-NN.html` og `/a/histstat/ereg77-96.html` returnerer en tom skall-side (~22 KB, 0 PDF-lenker) via **både `curl` og WebFetch** — innholdet er ikke der. De innholdsbærende eksemplarene ligger under huben: `/a/histstat/publikasjoner/histemne-NN.html` og `/a/histstat/publikasjoner/ereg77-96.html` (hundrevis av PDF-lenker hver). WebFetch *rendrer ikke* disse sidene; bruk alltid hub-stien, ikke rot-stien.

## Når du skal bruke denne skillen

- Brukeren spør om norske statistikktall fra **før ca. 1980** (Statistikkbanken har begrenset historisk dekning)
- Brukeren nevner NOS, Historisk statistikk, Statistisk årbok, folketellinger, eller eldre publikasjonsserier
- `ssb-pxwebapi-v2` ikke har dataen så langt tilbake — sjekk da `statbank-histu.html` (se under) før du gir opp

## Hvilken inngang når?

**Default startpunkt: huben `https://www.ssb.no/a/histstat/publikasjoner/`** — hent den for å se hele katalogen organisert *Etter emne* (1828–1976 + 1977–1996) og *Etter serie* (serier + periodika), og rut derfra:

- Bredt spørsmål, lang tidsserie (befolkning, økonomi, sosiale forhold) → Historisk statistikk-utgave (start med **hs1978** + **hs1968**, evt. **hs1994** for nyere tall)
- Tidsserie som fortsatt publiseres → sjekk `statbank-histu.html` først, deleger så til `ssb-pxwebapi-v2` for live tall
- Folketelling → `https://www.ssb.no/a/folketellinger/main.html` (per-telling-indeks 1769–1990; landings-URL `/a/folketellinger/` er bare et frameset-skall), evt. konkret NOS I c1-publikasjon
- Spesifikt fagtema (lønn, priser, jordbruk osv.) → emnesiden under huben: `https://www.ssb.no/a/histstat/publikasjoner/histemne-NN.html` (1828–1976) eller `…/publikasjoner/ereg77-96.html#KODE` (1977–1996) — se `references/structure.md` for koder. Ekte HTML med PDF-lenker, så `curl … | grep` fungerer
- Spesifikk publikasjonsserie (NOS, sos, rapp, dp…) → serieindeks under `/a/histstat/<kode>/` (alle rike og `grep`-bare)
- Hurtigsøk i NOS-katalogen → `curl https://www.ssb.no/a/histstat/nos/ | grep -i <term>` (~1,1 MB inline HTML)
- Bibliografisk dekning → `fortegnelse.pdf` (1828–1976) eller `publikasjonsoversikt_1977-1996.pdf`

## Førstevalg: Historisk statistikk-oversikten

Når spørsmålet er bredt (befolkning, økonomi, sosiale forhold over lang tid), pek på en utgave av *Historisk statistikk* (HS):

| Utgave | URL | Status |
|---|---|---|
| 1978 | https://www.ssb.no/a/histstat/hs1978/ | **Foretrukket** — mest komplette tabeller og tidsserier |
| 1968 | https://www.ssb.no/a/histstat/hs1968.pdf | **Foretrukket** — best for 1800-tallet og tidlig 1900-tall |
| 1994 | https://www.ssb.no/a/histstat/hs1994.html | Supplement for nyere tall (frem til ca. 1990) |
| 1958 | https://www.ssb.no/a/histstat/hs1958.pdf | |
| 1948 | https://www.ssb.no/a/histstat/hs1948.pdf | |
| 1926 | https://www.ssb.no/a/histstat/hs1926.pdf | |
| 1914 | https://www.ssb.no/a/histstat/hs1914.pdf | |
| 1875 | https://www.ssb.no/a/histstat/aarbok/annuaire_1875.pdf | Eldste oversikt |

**Standardanbefaling:** start med hs1978 + hs1968. Bruk hs1994 hvis nyere tall trengs.

## Bro til Statistikkbanken

Mange historiske tidsserier er videreført i Statistikkbanken med startår før 1980. Sjekk **alltid** denne siden når en tidsserie etterspørres:

`https://www.ssb.no/a/histstat/statbank-histu.html` — *Tidsserier med startår før 1980 i Statistikkbanken*

Hvis det finnes en match: foreslå at brukeren henter tallene live via **`ssb-pxwebapi-v2`-skillen** i stedet for (eller i tillegg til) PDF-publikasjonen. WebFetch siden for å finne tabell-IDer.

## Søk på tema og serie

For spesifikke spørsmål, bruk `references/structure.md`. Den inneholder:

- Alle 25 emnesider 1828–1976 (`publikasjoner/histemne-01.html` … `histemne-25.html`)
- Emnegruppene 1977–1996 (`publikasjoner/ereg77-96.html#XX`)
- Alle 12 serier (NOS, sos, rapp, dp, …) + `diverse.html`, med indeks-URL
- Alle 9 periodika (Statistisk månedshefte, Økonomiske analyser, …)
- De to bibliografi-PDF-ene
- Filnavn-konvensjoner

### Arbeidsflyt

1. **Hent huben** `https://www.ssb.no/a/histstat/publikasjoner/` (eller slå opp riktig kode i `references/structure.md`) for å identifisere tema/serie
2. **`curl … | grep` emnesiden eller serieindeksen** for å hente listen over publikasjoner:
   - Emne: `curl https://www.ssb.no/a/histstat/publikasjoner/histemne-NN.html | grep -i <term>`
   - Serie/NOS: `curl https://www.ssb.no/a/histstat/<kode>/ | grep -i <term>` (NOS-indeksen er ~1,1 MB)
   - **Merk:** bruk hub-stien (`/publikasjoner/histemne-NN.html`), ikke rot-stien `/a/histstat/histemne-NN.html` — sistnevnte er en tom skall-side, og WebFetch hjelper ikke
3. **Returner full URL** til PDF/HTML + kort kontekst (serie, år, tema)
4. Hvis match i `statbank-histu.html`: nevn også `ssb-pxwebapi-v2`

## Filnavn-konvensjoner

Se `references/structure.md` for komplett tabell med mønstre, eksempler og kataloger. **Hovedfeller å huske:** NOS-publikasjoner og st-filer ligger *begge* under `/a/histstat/nos/` — `st_<nr>r_<år>.pdf`-filer (pre-NOS-serien 1828–1860) er ikke på `/a/histstat/`-rot.

## Hva denne skillen IKKE gjør

- Ikke parsing av PDF til tabelldata — returner URL, så åpner brukeren PDF selv
- Ikke moderne tall — bruk `ssb-pxwebapi-v2` for det
- Ikke svensk/dansk statistikk — bruk `scb-pxwebapi-v2` for SCB
- **Ikke gjengi et historisk tall fra hukommelsen.** Denne skillen returnerer kilde-URL-er; den leser ikke PDF-ene. Har du ikke lest tallet i publikasjonen, oppgi det ikke — pek på siden og la brukeren lese det selv. Et tall du «husker» fra 1801-tellingen er et tall uten kilde, og et feil tall med SSB-henvisning skader tilliten til SSB, ikke bare til svaret

## Eksempler

**«Hva var Norges folkemengde i 1801?»**
→ Den autoritative kilden er NOS I c1 1801-25: `https://www.ssb.no/a/histstat/nos/nos_i_c1_1801-25.pdf` ("Tabeller vedkommende Folketællingerne i Aarene 1801 og 1825"). Folketellingsarkivet: `https://www.ssb.no/a/folketellinger/main.html` (per-telling-indeks 1769–1990; landings-URL `/a/folketellinger/` er bare et frameset). Nevn også hs1978 for tidsserie tilbake til 1769. Sjekk `statbank-histu.html` for moderne befolkningstabell.

**«Lønn i industrien 1930-tallet»**
→ Emne 15 (Lønninger): `https://www.ssb.no/a/histstat/publikasjoner/histemne-15.html` — `curl … | grep -i industri` for liste; ellers hs1978 kapittel om lønn.

**«NOS-publikasjon om fattigstatistikk fra 1870-tallet»**
→ `curl https://www.ssb.no/a/histstat/nos/ | grep -i fattig` for å finne `nos_i_a2_187X.pdf`-serien.
