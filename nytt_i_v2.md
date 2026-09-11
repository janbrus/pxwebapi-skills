# Nytt i PxWebApi versjon 2

## GET URL-støtte
Viktigst er innføringen av GET URL-støtte. Det gjør API-et enklere å integrere.

**Merk:** Versjon 2 er ikke bakoverkompatibel med versjon 1. Spørringen har en helt ny form — `valueCodes[variabel]` og `codelist[variabel]` i stedet for v1-bodyen `{"query": […], "response": {…}}` — så gamle skript må skrives om, ikke justeres. Begge versjonene kjører fortsatt parallelt hos SSB.

---

## Forbedrede filtre og søkemuligheter

**Bedre maskeringstegn:**
Du kan nå maskere ett og ett tegn med `?`, i tillegg til det eksisterende `*` for flere tegn. Wildcards virker også på tid: `2024*` gir alle månedene i 2024.

**Nye filtre:** 
- `from(verdi)` – hent data fra og med et startpunkt
- `to(verdi)` – til og med (inklusivt)
- `range(fra,til)` – definer et spesifikt intervall, f.eks. fra kommuneliste
- `bottom(n)` – motsatt av det eksisterende `top(n)`
- `top(n, offset)` og `bottom(n, offset)` – hopp over de `offset` første/siste verdiene, f.eks. `top(3,2)` for de tre periodene før de to nyeste

**NB om komma i GET-URL-er:** komma skiller verdier i `valueCodes[variabel]=a,b,c`, så et uttrykk som selv inneholder komma må stå i hakeparenteser. `valueCodes[Tid]=range(2020,2022)` blir delt i to og avvist med `400 "Illegal selection expression"`; riktig form er `valueCodes[Tid]=[range(2020,2022)]`. Det samme gjelder `[top(3,2)]`. I en POST-body trengs ingen hakeparenteser, siden hvert uttrykk allerede er sitt eget element. Uttrykk kan for øvrig kombineres med enkeltkoder: `2015,top(2)` gir 2015 pluss de to nyeste periodene.

---

## Mer fleksibel henting av data

- Hent forhåndsdefinerte datasett uten å spesifisere parametere
- Flere metadata i JSON-stat2, bl.a. fotnoter (gjelder også versjon 1)
- Metadata i API vises nå som JSON-stat2 
- Kodelister i metadata. Tilgjengelig via `Codelists` (kan gi komplekse URL-er)

---

## Layout styring for CSV, XLSX og HTML

**Nye parametere gir full kontroll og fleksibilitet:**

**Visningsalternativer:**
- `UseCodes` – vis kun koder
- `UseTexts` – vis kun tekst
- `UseCodesAndTexts` – vis både koder og tekst
- `IncludeTitle` – inkluder tabelltittel

**Strukturkontroll:**
- `stub` – bestem hvilke variabler som vises i forspalten
- `heading` – bestem hvilke variabler som vises i tabellhodet
- **Tips:** Plasser alle variabler i `stub` for å få en pivotvennlig tabell

**CSV-skilletegn:**
- `SeparatorTab` – tabulator
- `SeparatorSpace` – mellomrom
- `SeparatorSemicolon` – semikolon

**Eksempel:**

```
outputformat=csv
outputformatparams=separatorsemicolon,usecodesandtexts
heading=ContentsCode
stub=VareGrupper2,Tid
```

**HTML format** er nytt. Norsk har tusenskille mellomrom, engelsk komma. Kan stiles, f.eks. :

```
	<style type="text/css">
	    th[scope="col"] {
	        text-align: center;
	    }
	    th[scope="row"] {
	        text-align: left;
	    }
	    td {
	        text-align: right;
	    }
	    caption {
	    	font-weight: bold;
	    }
	</style>
```

## Annet nytt
Det er mer metadata i JSON-stat2, slik som fotnoter. Dette gjelder også for API v1.
Det er også nytt format for bruk av HTTP POST.
Det er også kjekt å vite at URL-ene ikke ser ut til å være sensitive for store og små bokstaver: både parameternavn, variabelkoder og verdikoder godtas i vilkårlig skrivemåte (`valuecodes[tid]`, `personer1`, `TOP(1)`). Ett unntak: **kodeliste-ID-er er case-sensitive** — `agg_kommfylker` gir `400 "Non-existent codelist"`, mens `agg_KommFylker` virker.

---

## Kjente begrensninger

### 1. Statiske URL-er fra Statistikkbanken

URL-er generert i Statistikkbanken er statiske og inkluderer ikke automatisk fremtidige tall. Dette gjør dem:

- Uoversiktlige og vanskelige å vedlikeholde
- Nødvendig å redigere manuelt for å få oppdaterte tall, ved å legge inn filtrene from() og top().

Jeg har laget et optimaliseringsverktøy: [forenkle_url.html](forenkle_url.html), også hostet på https://nesa.no/ssb/forenkle_url.html

### 2. URL begrensning på lengde

- Maksimal lengde: ~2100 tegn. Målt 2026-09-09 på tabell 07459: 400 kommunekoder (2 092 tegn) gir svar, 410 koder (2 142 tegn) gjør det ikke
- Over grensen svarer API-et **404**, ikke 400 — det ser altså ut som om tabellen ikke finnes. Kort ned URL-en før du konkluderer
- Kan være problematisk for korttidsstatistikker med lange tidsserier. For månedsstatistikker går grensen litt før Finanskrisen, om de ikke rettes
- Løsningen er `*`, `?`, `from()`/`to()`/`[range()]` eller en kodeliste i stedet for lange verdilister — eller POST, som ikke har lengdegrensen

### 3. Gjentatt verdikode gir 500

Oppgir du den samme verdikoden to ganger i samme variabel, svarer API-et **500** med tom body — ikke 400 med forklaring. `valueCodes[Region]=0301,0301` er nok. Det gjelder både GET og POST, og er verifisert 2026-09-09 hos SSB, SCB og Latvias CSP. Overlapp mellom et uttrykk og en enkeltkode er derimot greit: `valueCodes[Tid]=2026,top(1)` gir svar selv om `top(1)` også er 2026. Bygger du valgkoder programmatisk, dedupliser lista først.

---
Se også [SSBs brukerveiledning til API v2](https://www.ssb.no/api/pxwebapiv2) (engelsk: [Statbank Norway API user guide](https://www.ssb.no/en/api/pxwebapiv2)) og den felles [PxWebApi 2 User Guide](https://www.pxtools.net/PxWebApi/documentation/user-guide/) fra PxTools.

SSBs R pakke [PxWebApiData](https://cran.r-project.org/package=PxWebApiData) er også oppdatert til å håndtere V2 URLer.

Detaljene over — og en del til — er bygget inn i AI-skillene i dette repoet; se [README](README.md) og skillenes egne endringslogger for hva som er verifisert mot live API, og når.
