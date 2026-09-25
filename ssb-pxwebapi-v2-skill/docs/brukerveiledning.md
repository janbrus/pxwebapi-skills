# Brukerveiledning: SSB PxWebApi v2 Skill i Claude

Denne veiledningen forklarer hvordan du bruker Claude-skillen for SSBs Statistikkbank.

Skillen vedlikeholdes på <https://github.com/janbrus/pxwebapi-skills/tree/main/ssb-pxwebapi-v2-skill>; denne veiledningen ligger i `docs/` der. Denne veiledningen dekker **v1.6.0**. Sjekk repoet for nyere versjon og endringslogg.

## Forutsetninger

Du trenger:

1. **Claude Pro, Max, Team eller Enterprise** — skills krever betalt plan
2. **Skillen installert** — lastet opp som ZIP under Settings > Capabilities > Skills
3. **Code execution aktivert** — under Settings > Capabilities
4. **`*.ssb.no` tillatt i nettverksinnstillingene** — se under

Valgfritt, men anbefalt:

- **En MCP-server** koblet til som connector — `@jarib/pxweb-mcp` er anbefalt. Da kan Claude kalle API-et direkte. Se «Koble til MCP-server» nederst
- **`ssb-chart`-skillen** — for visualisering i SSBs offisielle stil
- **`norges-bank-api`-skillen** — for styringsrente, valutakurser og annen sentralbankdata, som ikke ligger i Statistikkbanken

### Nettverkstilgang: `*.ssb.no` må være tillatt

Claude når bare domener som står på organisasjonens tillatelsesliste. Står ikke SSB der, kan skillen ikke hente data. Da går den tilbake til å foreslå tabeller og gi deg en URL du må åpne selv.

Skillen bruker to verter:

| Vert | Brukes til |
| --- | --- |
| `data.ssb.no` | PxWebApi v2 og Klass — all datahenting. Kritisk |
| `www.ssb.no` | RSS-feeder (publiseringskalender), VarDok-definisjoner, «Om statistikken»-sider |

`*.ssb.no` dekker begge. Må du begrense strengt, er `data.ssb.no` den som ikke kan utelates.

I Team og Enterprise styrer administrator dette under Admin settings > Capabilities. Bekreft syntaksen for jokertegn der. Det er ikke alltid '*'.

**Dette gjelder bare når skillen henter data selv.** Bruker du en lokal MCP-server gjennom Claude Desktop, går kallet fra din egen maskin, og tillatelseslista i Claude er ikke involvert. Det forklarer et forvirrende symptom: samme spørsmål virker i Claude Desktop, men ikke på claude.ai.

## Dataintegritet: hva skillen garanterer

Dette er skillens viktigste egenskap, og den er verdt å forstå før du bruker den.

**Skillen oppgir aldri et tall den ikke har hentet fra API-et i samme samtale.**

Uten en slik regel vil en språkmodell gjerne svare «Oslo har omtrent 710 000 innbyggere» fra treningsdata. Tallet høres riktig ut, det er omtrent riktig, og det er umulig å skille fra et hentet tall. Med en SSB-kildehenvisning under blir det verre, ikke bedre — feilen tilskrives SSB.

I praksis betyr regelen at skillen:

- ikke gjetter variabelkoder, men leser dem fra metadata i samme samtale
- ikke fyller hull i en tidsserie med interpolering eller framskriving
- ikke blander inn tall fra Norges Bank, Eurostat, OECD eller websøk i samme svar
- merker egne beregninger — vekstrater, andeler og summer er skillens, ikke SSBs
- sier tydelig fra når API-et ikke svarer, i stedet for å anslå

**Konsekvensen for deg:** får du «jeg fant ikke tallet», er det et ærlig svar, ikke en feil. Be heller om andre søkeord eller en annen tabell.

## Slik fungerer det

Skillen trigger automatisk når du stiller spørsmål om norsk statistikk. Du trenger ikke nevne den. Claude gjenkjenner spørsmålet og aktiverer skillen i bakgrunnen.

### Arbeidsflyten bak kulissene

Når du spør «Hvor mange bor i Oslo?», skjer dette:

1. **Forstå behovet** — fenomen, geografi, tidsperiode, nedbrytning. Er spørsmålet vagt, stiller Claude *ett* oppfølgingsspørsmål
2. **Søk** — `GET /tables?query=folkemengde` finner kandidattabeller
3. **Metadata** — `GET /tables/07459/metadata` gir variabler, koder, kodelister og enheter. Dette steget hoppes aldri over
4. **Query** — data hentes med eksplisitt seleksjon
5. **Presenter** — tabell, kilde med tabellnummer, enhet og kontekst

Steg 3 er grunnen til at skillen bruker noen sekunder ekstra. Det er også grunnen til at den treffer riktig kode.

### Uten MCP-server

Skillen fungerer også uten MCP-server, men da kan ikke Claude hente data direkte. I stedet vil Claude:

- foreslå riktig tabell og variabler fra den kurerte tabellista (~90 tabeller)
- vise deg en ferdig API-URL du kan åpne i nettleseren
- gi veiledning for manuelt oppslag i Statistikkbanken

## Eksempler på spørsmål

### Enkle oppslag

- «Hvor mange bor i Oslo?»
- «Hva er KPI nå?»
- «Vis befolkningen i alle fylker»
- «Hva er arbeidsledigheten?»
- «What is Norway's GDP?»

### Med tidsperiode

- «Vis KPI siste 5 år, månedlig»
- «Befolkningsutviklingen i Bergen fra 2010»
- «Boligprisindeksen siste 20 kvartaler»

### Med geografisk spesifisering

- «Hvor mange bor i Nord-Aurdal kommune?»
- «Sammenlign folketallet i alle fylker»
- «Vis arbeidsledigheten i Rogaland»
- «Hvor mange bor i grunnkretsene på Majorstuen?»

### Med nedbrytning

- «Vis befolkningen i Oslo fordelt på alder og kjønn»
- «Gjennomsnittlig årslønn per næring»
- «KPI fordelt på vare- og tjenestegruppe»

### Kommunal tjenesteproduksjon og økonomi (KOSTRA)

KOSTRA-tabellene har egen struktur, egne regionkoder og egen publiseringsrytme. Skillen håndterer det, men det er nyttig å vite at disse spørsmålene går en annen vei enn resten:

- «Hva er netto driftsresultat i Bergen sammenlignet med KOSTRA-gruppen og landet uten Oslo?»
- «Vis barnehagedekningen i kommunene i Innlandet»
- «Hvor mye bruker Trondheim på administrasjon per innbygger?»

### Næring

- «Hvor mange konkurser var det i IT-bransjen forrige kvartal?»
- «Antall aksjeselskaper per næring»

Merk at SSB er i overgang fra SN2007 til SN2025. Skillen sier hvilken standard tallene bygger på, og skjøter aldri de to på næringsnivå.

### Avanserte spørsmål

- «Gi meg en konsistent tidsserie for Moss kommune over de siste 20 årene, inkludert kommunesammenslåingen»
- «Hva er SSBs prognoser for BNP de neste 4 årene?» (tabell 12880)
- «Vis eksport av fisk til EU-land siste 3 år»
- «Lag en delbar URL for boligprisindeksen i Oslo»
- «Eksporter dette som Excel»

### På engelsk

- «What is the population of Norway?»
- «Show me the consumer price index for the last year»
- «Compare unemployment across Norwegian counties»

Claude tilpasser automatisk språk i API-kall (`lang=no` eller `lang=en`), tallformat og kildehenvisning etter hvilket språk du skriver på.

## Hva du vil se i svarene

Skillen presenterer data på en fast måte. Noen av elementene er lette å overse:

**Kilde med tabellnummer.** «Kilde: SSB, tabell 07459». Er flere tabeller brukt, listes alle.

**Enhet.** Antall, prosent, indeks eller kroner. For indekser oppgis referanseperioden, f.eks. 2025=100.

**Standardtegn i stedet for tall.** SSB bruker tre symboler, og skillen viser dem som de er i stedet for å skjule dem eller sette inn null:

| Tegn | Betyr |
| --- | --- |
| `.` | Ikke mulig å oppgi tall — kategorien var ikke i bruk |
| `..` | Tallgrunnlag mangler — ikke innkommet, eller for usikkert til publisering |
| `:` | Vises ikke av konfidensialitetshensyn |

**Obligatoriske noter.** Noen tabeller har noter SSB har bestemt skal følge tallet. KPI-tabellene har for eksempel en note om at referanseåret ble 2025=100 fra 2026, og at endringstall beregnet fra disse seriene kan avvike fra publiserte endringstall. Når du ser en slik note, er den der fordi SSB har flagget den.

**Merking av egne beregninger.** Ber du om vekst i prosent, andeler eller en sum, vil skillen si at beregningen er dens egen og vise hvilke hentede tall den bygger på.

**Foreløpige tall.** Nasjonalregnskapet revideres. KOSTRA publiseres urevidert 15. mars og revidert 15. juni, uten at API-et flagger forskjellen — skillen leser publiseringsdatoen og sier hvilken utgave du har fått.

**Etterprøvbarhet.** Skillen viser GET-URL-en eller POST-bodyen den brukte, og oppgir hvilken kodeliste den valgte og hvilke dimensjoner den utelot. Dette står ikke i API-responsen, så uten det kan ikke uttrekket gjenskapes.

## Når skillen sender deg videre

Noen spørsmål hører ikke hjemme i Statistikkbanken. Skillen henviser i stedet for å gjette, og blander aldri kilder i samme svar:

| Spørsmål om | Hvor det ligger |
| --- | --- |
| Styringsrente, valutakurser, NOWA, statsgjeld, statsobligasjoner | Norges Bank — bruk `norges-bank-api`-skillen |
| Folketellinger og tidsserier fra før Statistikkbanken | SSBs historiske statistikk — `ssb-histstat`-skillen |
| Gamle POST-bodyer i v1-form, eller andre PxWeb-installasjoner | `generic-pxweb-v1-skill` eller `generic-pxweb-v2-skill` |
| Svensk statistikk | `scb-pxwebapi-v2`-skillen |

Gamle lenker på formen `ssb.no/statbank/sq/{id}` er derimot v2-stoff. De gir bare skjermvisning i nettleseren nå, men API-et leverer fortsatt dataene — be Claude hente dem.

## Tips for best mulig resultat

### Vær spesifikk om tidsperiode

Skillen filtrerer alltid på tid, men du får mer relevante resultater ved å si «siste 5 år» eller «fra 2020» enn bare «vis meg data».

### Nevn geografi om det er relevant

«Hele Norge», «per fylke», «for Oslo». Dette hjelper Claude å velge riktig nivå og riktig kodeliste. Tabelltitlene har suffikser som viser laveste nivå: **(F)** fylke, **(K)** kommune, **(B)** bydel, **(G)** grunnkrets.

### Be om delbar URL — og be om at den holder seg oppdatert

Si «lag en delbar URL for denne spørringen». Be samtidig om relative tidsfiltre: en URL med `top(12)` eller `from(2020)` henter automatisk nye perioder, mens faste årstall blir utdaterte.

Bygger du uttrekket selv i Statistikkbanken og trykker «Lagre», rammes de valgte periodene opp som faste verdier. Verktøyet <https://github.com/janbrus/pxwebapi-skills/blob/main/forenkle_url.html> skriver dem om til relative filtre.

### Spør om metadata

«Vis meg metadata for tabell 14700» — nyttig for å se hvilke variabler, koder og kodelister som finnes. Statistikkvariabelen heter `ContentsCode` i API-et og «statistikkvariabel» på norsk.

### Spør om visualisering

Etter at data er hentet: «vis dette som graf» eller «lag et diagram». Med `ssb-chart`-skillen installert bruker Claude SSBs offisielle stil.

### Be om annet filformat

«Eksporter dette som Excel» eller «gi meg dette som CSV». Merk at CSV fra SSB leveres i tegnsettet ISO-8859-1, ikke UTF-8 — relevant hvis du leser fila i Python eller R.

## Hva gjør du hvis noe ikke fungerer?

### Claude finner ikke riktig tabell

Bruk norske fagtermer. SSB skriver «konsumprisindeks» (ikke «KPI»), «folkemengde» (ikke «befolkning»), «sysselsatte» (ikke «ansatte»).

To ting er verdt å vite om søket:

- **Standardoperatoren er AND.** Flere ord gir *færre* treff, ikke flere. Ett ord som ikke står i tabellen nuller lista
- **Søket treffer SSBs egne labels bokstavelig, også skrivefeil.** «kostra driftsresultat» finner ikke tabell 12134, fordi variabelen der heter «Netto driftresultat …» uten s

Kjenner du tabellnummeret, oppgi det direkte.

### Claude bruker feil kommunekode

Kommunekodene endret seg ved sammenslåingene i 2020. Be Claude søke etter kommunenavnet, eller bruke kodelista `agg_KommSummer` for en konsistent tidsserie over sammenslåingen. Wildcards matcher bare koder, ikke kommunenavn.

### Dataene ser rare ut

Be Claude sjekke enheten — tabellen kan ha flere målevariabler (antall, prosent, indeks). Si «hva er enheten?» eller «vis meg statistikkvariablene for denne tabellen».

Tre vanlige årsaker til at en serie ser merkelig ut over tid:

- kommunesammenslåingene i 2020 bryter tidsserier på kommunenivå
- KPI-basisåret endres periodisk (nå 2025=100)
- næringskodene: samme bokstav betyr ulik næring i SN2007 og SN2025

### Skillen trigger ikke

Vær mer eksplisitt: «Bruk SSB-skillen til å finne …» eller «Hent tall fra Statistikkbanken for …».

### Claude foreslår tabeller, men henter aldri tall

Typisk symptom på at `*.ssb.no` mangler i nettverksinnstillingene. Claude finner riktig tabell fra den kurerte lista, gir deg en ferdig URL — og stopper der.

Test det raskt: be Claude hente `https://data.ssb.no/api/pxwebapi/v2/config`. Kommer det en JSON-respons med `maxDataCells`, er nettverket i orden, og årsaken ligger et annet sted. Blokkeres kallet, se «Nettverkstilgang» under Forutsetninger.

### MCP-serveren svarer ikke

Claude faller tilbake til veiledning for manuelt oppslag. Du kan også gå direkte til Statistikkbanken: <https://www.ssb.no/statbank>

### Du får en feilmelding fra API-et

De vanligste:

| Feil | Årsak |
| --- | --- |
| `Missing selection for mandantory variable` | En obligatorisk variabel mangler. Tid og statistikkvariabel er alltid obligatoriske (skrivefeilen er SSBs egen) |
| `Non-existent value` | Koden finnes ikke i tabellen. I KOSTRA kan en kode fra i fjor være fjernet |
| `Too many cells selected` | Uttrekket overstiger 800 000 celler. Filtrer mer |
| `404` på en lang URL | GET-URL over ca. 2 100 tegn gir 404. Be Claude bruke POST |

## Viktige begrensninger

- **Skillen gir ikke sanntidsdata.** SSBs data oppdateres på faste tidspunkter
- **Grense på 800 000 celler per uttrekk.** Tomme celler teller med
- **40 spørringer per minutt.** Gjeldende grense står i `x-ratelimit-*`-responsheaderne. Feltene `maxCallsPerTimeWindow` og `timeWindow` i `/config` er nullstilt til 0 og ikke lenger i bruk
- **Nye tall publiseres kl. 08.00.** Data under revisjon kan vise 0 eller prikk mellom kl. 05 og 08. Metadata oppdateres kl. 05.00 og 11.30, og tabellene er utilgjengelige imens
- **Kommunekoder er ikke stabile over tid.** Bruk kodelister for konsistente tidsserier
- **Tabell-ID-er er derimot permanente.** Bare `discontinued`-statusen endres når en tabell avsluttes
- **KOSTRA-strukturen endres** når rapporteringskravene endres. Variabler kommer til og faller bort, og tabeller erstattes av nye med nytt nummer

Lisens på dataene: Creative Commons CC BY 4.0.

## Koble til MCP-server

For at Claude skal kunne hente data direkte, trenger du en MCP-connector.

### @jarib/pxweb-mcp (open source)

En generisk MCP-server som fungerer mot alle PxWebApi v2-installasjoner. Kildekode: <https://github.com/jarib/pxweb-mcp>

Serveren eksponerer seks verktøy:

| Verktøy | Tilsvarer |
| --- | --- |
| `search_tables` | `GET /tables?query=…` |
| `get_table_info` | `GET /tables/{id}` |
| `fetch_metadata` | `GET /tables/{id}/metadata` |
| `query_table` | `GET /tables/{id}/data` |
| `get_code_list` | `GET /codelists/{id}` |
| `list_recent_tables` | `GET /tables?pastDays=N` |

**Når Claude går utenom MCP-serveren.** Fire operasjoner er ikke dekket, og da bruker skillen vanlige HTTP-kall i stedet:

- lagrede spørringer, `defaultselection` og `/config` er ikke eksponert som verktøy
- `search_tables` returnerer kun ID og tittel — `lastPeriod`, `timeUnit` og `discontinued` mangler
- `fetch_metadata` støtter ikke kodeliste-parameteren
- formatert eksport (Excel med tittel, CSV med semikolon) krever HTTP

Dette er ikke en feil. Skillen velger kanal etter hva operasjonen krever.

**Bruk med Claude Desktop:**

Legg til i config-filen:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pxweb-ssb": {
      "command": "npx",
      "args": ["-y", "@jarib/pxweb-mcp"]
    }
  }
}
```

For SCB (Sverige):

```json
{
  "mcpServers": {
    "pxweb-scb": {
      "command": "npx",
      "args": ["-y", "@jarib/pxweb-mcp", "--url", "https://statistikdatabasen.scb.se/api/v2"]
    }
  }
}
```

Du kan ha begge konfigurert samtidig med ulike navn. Merk at verktøynavnene er like uansett hvilken instans serveren peker mot — navnet du gir serveren i configen er eneste holdepunkt.

**Bruk med Claude Code:**

```bash
claude mcp add pxweb-ssb -- npx -y @jarib/pxweb-mcp
```

**Som HTTP-server (for andre MCP-klienter):**

```bash
npx -y @jarib/pxweb-mcp --transport streamable-http --port 3000
```

Koble til med:

```json
{
  "mcpServers": {
    "pxweb": {
      "type": "http",
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

**Krav:** Node.js må være installert. `npx` laster ned og kjører pakken automatisk.

## Uten Claude Pro

Skills krever betalt Claude-plan. Domenekunnskapen er likevel ikke låst til Claude:

- **MCP er ikke Claude-spesifikt.** `@jarib/pxweb-mcp` fungerer mot enhver MCP-klient — VS Code med Copilot, Cursor, Windsurf og andre
- **Arbeidsflyten kan limes inn.** En kondensert versjon av `SKILL.md` fungerer som systemprompt eller prosjektinstruksjon i de fleste chatgrensesnitt
- **Statistikkbanken har en grafisk spørringsbygger.** Velg tabell og verdier på <https://www.ssb.no/statbank>, trykk «Lagre», og du får ferdig GET-URL og POST-body uten å skrive dem selv. Du kan også benytte det alternativet grensesnittet statistikkportalen.no.

## Rapportere feil

- Feil eller mangler i skillen: <https://github.com/janbrus/pxwebapi-skills>
- Spørsmål om tabeller eller API-et: <statistikkbanken@ssb.no>

SSBs egen brukerveiledning for PxWebApi v2: <https://www.ssb.no/api/pxwebapiv2>
