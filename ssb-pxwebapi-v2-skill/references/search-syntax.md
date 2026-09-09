# Søkesyntaks for /tables?query=

API-et søker i tabelltitler, variabler og variabelverdier (case-insensitivt). Søkemotoren er **Lucene** (via Lucene.Net i PxWebApi), så `query`-parameteren tolkes etter [Lucene Query Parser-syntaks](https://lucene.apache.org/core/2_9_4/queryparsersyntax.html) — feltbegrensning (`felt:verdi`), wildcards (`*`, `?`), fuzzy (`~N`), nærhet (`"…"~N`), intervaller (`[a TO b]`) og boolske operatorer (`AND`, `OR`, `NOT`) virker derfor som i andre Lucene-baserte søk (Elasticsearch, Solr). Følgende mønstre er bekreftet i PxWebApi v2:

## Feltbegrensning

- `title:barn` — begrens søket til tittelfeltet
- `updated:20250908*` — søk etter oppdateringsdato
- `updated:[20250908 TO 20250912*]` — datointervall

## Mønstermatching

- `anlegg*` — trunkering, matcher alt som starter med "anlegg". NB: wildcard matcher den *stemmede* indekstermen, ikke ordet slik det står i tittelen — på den engelske indeksen gir `population*` 0 treff mens `popul*` gir treff (verifisert av `generic-pxweb-v2-skill` 2026-09-08). Trunker før endelsen, eller søk hele ordet uten `*`
- `konsumpris~1` — fuzzy søk, `~N` tillater N tegns avvik
- `"varenummer hs" ~5` — nærhetssøk, finner ordene innen 5 ord fra hverandre

## Boolske operatorer

- `trend AND anlegg*` — begge må matche
- `title:foretak AND title:(F)` — fylkesnivå-tabeller om foretak
- **Standard mellom ord er AND hos SSB** (verifisert 2026-09-09: `folkemengde region` = `folkemengde AND region` = 17 treff; `folkemengde OR region` = 1 414). Et lengre søkeord gir altså *færre* treff — bra for å snevre inn, men ett ord som ikke står i tabellen nuller lista. Standarden er ikke lik overalt (Latvias installasjon bruker OR), så skriv `AND`/`OR` eksplisitt i spørringer som skal deles

(Fagtermer og synonymvalg: se Steg 2 i `SKILL.md`. De ikke-Lucene-parametrene `pastDays` og `includeDiscontinued` står i søkeparametertabellen samme sted.)
