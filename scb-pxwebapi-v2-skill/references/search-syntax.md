# Söksyntax för /tables?query=

API:et söker i tabelltitlar, variabler och variabelvärden (case-insensitivt). Sökmotorn är **Lucene** (via Lucene.Net i PxWebApi), så `query`-parametern tolkas enligt [Lucene Query Parser-syntax](https://lucene.apache.org/core/2_9_4/queryparsersyntax.html) — fältbegränsning (`fält:värde`), wildcards (`*`, `?`), fuzzy (`~N`), närhet (`"…"~N`), intervall (`[a TO b]`) och booleska operatorer (`AND`, `OR`, `NOT`) fungerar därför som i andra Lucene-baserade sökningar (Elasticsearch, Solr). Följande mönster är bekräftade mot SCB (HTTP 200, 2026-09-07):

## Fältbegränsning

- `title:barn` — begränsa sökningen till titelfältet
- `updated:20250908*` — sök på uppdateringsdatum
- `updated:[20250908 TO 20250912*]` — datumintervall

## Mönstermatchning

- `anlägg*` — trunkering, matchar allt som börjar med "anlägg". **Trunkera kort:** wildcards matchar den *stammade* indextermen, inte ordet i titeln. `folkmängd*` ger 0 träffar, `folkmäng*` ger 117 (verifierat 2026-09-08). Skriv hela ordet utan `*`, eller kapa före ändelsen
- `konsumentpris~1` — fuzzy-sökning, `~N` tillåter N teckens avvikelse
- `"folkmängd region" ~5` — närhetssökning, hittar orden inom 5 ord från varandra

## Booleska operatorer

- `trend AND anlägg*` — båda måste matcha
- **Standard mellan ord är AND hos SCB** (verifierat 2026-09-08: `folkmängd region` = `folkmängd AND region` = 53 träffar; `folkmängd OR region` = 1 599). Ett längre sökord ger alltså *färre* träffar — bra för att snäva in, men ett ord som inte står i tabellen nollar listan. Standarden är inte densamma överallt (Lettlands installation använder OR), så skriv `AND`/`OR` explicit i frågor som ska delas

## Sidstorlek

Default `pageSize` är 20. En tabell på plats 47 syns aldrig utan `pageSize=100` eller `pageNumber=3` — kontrollera `page.totalElements` innan du drar slutsatsen att tabellen inte finns.

(Fackord och synonymval: se Steg 2 i `SKILL.md`. De icke-Lucene-parametrarna `pastDays` och `includeDiscontinued` står i sökparametertabellen på samma ställe.)
