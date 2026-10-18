---
name: ssb-chart
description: >
  Visualiser norsk statistikk i SSBs offisielle stil. Bruk denne skillen ALLTID når
  SSB-data skal presenteres som diagram, graf, chart, tabell, dashboard eller visuell
  fremstilling. Trigger på fraser som "vis dette som graf", "lag et diagram", "lag en figur"
  "visualiser SSB-dataene", "plot befolkningsutviklingen", "lag en tidsserie",
  "vis dette som søylediagram", "dashboard med SSB-tall", "kakediagram over",
  eller når SSB-data allerede er hentet og brukeren ber om visuell presentasjon.
  Bruk sammen med `ssb-pxwebapi-v2`-skillen for å hente data; denne skillen styrer
  hvordan dataene presenteres. Bruk IKKE denne skillen for visualisering av andre
  datakilder — da er en annen dataviz-skill riktig valg.
license: MIT. LICENSE has complete terms
metadata:
  version: "1.3"
  source: https://github.com/janbrus/pxwebapi-skills/tree/main/ssb-chart-skill
---

# SSB Data Visualization

Denne skillen styrer visuell presentasjon av norsk offentlig statistikk fra SSB. Den sørger for at diagrammer, tabeller og dashboards følger SSBs designsystem og best practice for statistisk datavisualisering.

---

## Kjerneprinsipper

1. **Én innsikt per diagram.** Hvert diagram formidler én tydelig observasjon. Flere historier → flere diagrammer.

2. **Statistisk integritet.** SSB-data er offentlig statistikk — presisjon er avgjørende. Y-aksen på søyle- og arealdiagrammer starter ALLTID på 0. Linjediagram kan avkortes når endringen er budskapet og startverdien står synlig på aksen. Tidsserier skal ha jevne intervaller. Enheter og måleperiode må alltid synliggjøres.

3. **SSBs visuelle identitet som standard.** SSBs farger, typografi og formspråk er standardvalget. Ber brukeren om egne farger, eller har rapporten en egen palett, bruk dem — men kontrastkravene i prinsipp 4, skillbarhet for fargeblinde og fast farge per kategori gjelder fortsatt. Se `references/color-system.md` for komplett fargespesifikasjon.

4. **Tilgjengelighet (WCAG AA).** Ikke-tekstelementer: ≥3:1 kontrast. Tekst: ≥4.5:1 (≥3:1 for stor tekst). Aldri stol på farge alene — bruk form, mønster eller direkte merking som supplement.

5. **Kildeangivelse.** Hvert diagram skal inneholde kilde og tidsperiode. Se «Tekst og merking» → «Kilde» for fullstendig flerspråklig formulering.

6. **Datakvalitet synliggjøres, ikke skjules.** Manglende verdier (`null` i `value`, med status-koder `"."`, `".."`, `":"` — se `ssb-pxwebapi-v2`-skillen for full liste) rendres som visuelle hull (`null` i datasettet, ingen linje mellom kjente punkter). Aldri interpoler, drop, eller gjenta naboverdier for å «fylle» dataene — statistisk integritet veier mer enn visuell glatthet. **En status på en celle som har tall** (f.eks. `"*"` = foreløpig tall) er et flagg, ikke et hull: tegn punktet, merk det og forklar tegnet i en fotnote. For tabeller: vis statussymbolet (`..`, `:`) i cellen, ikke `0`; et flagget tall vises med tegnet etter tallet.

---

## Avhengigheter til datakilden

Denne skillen forutsetter at du har en JSON-stat2-respons fra SSBs PxWebApi v2. **Dataintegritet-grunnregelen i `ssb-pxwebapi-v2` gjelder også her:** visualiser aldri et tall som ikke er hentet fra API-et i samme samtale. Et diagram gir tall mer autoritet enn en tabell gjør — en akse og en kildelinje får et husket tall til å se etterprøvbart ut. Kjerneprinsipp 2 og 6 dekker hvordan tallene skal *behandles*; grunnregelen dekker hvorvidt du har lov til å tegne dem i det hele tatt. For format-detaljer — row-major value-array, `role.time` / `role.metric` / `role.geo`, `dimension.{var}.category.index` og `category.unit.decimals`, status-koder `"."` / `".."` / `":"`, `extension.px.contents` — se `ssb-pxwebapi-v2`-skillens `references/json-stat2.md`. Ikke restate disse detaljene her; pek på dem.

Selve oppskriften for å gå fra JSON-stat2-respons til et chart-config (labels, datasets, decimals, status som hull eller flagg) ligger i `references/jsonstat-to-chart.md`.

---

## Rendringsmål: widget vs. frittstående leveranse

Denne skillen brukes i to helt ulike rendringskontekster, og de deler IKKE samme stilregler. Avgjør rendringsmål før du velger farger, typografi eller layout — ikke etterpå.

**A. Inline chat-widget** (f.eks. `visualize:show_widget` / tilsvarende verktøy som rendrer direkte i samtalen)

Disse verktøyene har sitt eget vertsdesignsystem (layout, CSS-variabler, typografi, mørk modus) som SSB-stilen ikke skal overstyre i sin helhet. Kun dette styrer skillen i en widget:

- **Data-blekk** — alt som koder en verdi: datalinjer, søyler, punkter, kartflater og heatmap-celler bruker SSB-paletten som standard (`#00824D`, `#1D9DE2`, `#C78800` osv.), hardkodet som hex. Canvas-baserte biblioteker (Chart.js m.fl.) kan uansett ikke lese CSS-variabler, så hardkodet hex her er riktig og nødvendig.

Alt annet følger vertens konvensjoner, ikke tabellene lenger ned i denne skillen:

- **Akser, rutenett, bakgrunn, generell tekst** — bruk vertens fargetoken/design (f.eks. `getComputedStyle` mot `--text-muted`, `--border` osv. der verten støtter det), ikke de hardkodede SSB-hex-verdiene fra «Tekst og merking» → «Akser».
- **Mørk modus** — obligatorisk. Vertens tokens løser dette automatisk; hardkodede lys-modus-farger som `#274247` eller `#D9DFE0` skal ikke skrives direkte inn i widget-DOM-en.
- **Tittel og kilde** — skrives IKKE inn i widgeten. Verten krever ofte at forklarende tekst ligger i selve chat-svaret, ikke i widget-koden. Skriv deklarativ tittel og kildelinje (jf. «Tekst og merking» → «Kilde») i svarteksten rundt widget-kallet i stedet.
- **Tabeller** — rendres IKKE med SSB-tabellstilen i en widget. Bruk vanlig markdown-tabell i chat-svaret. Seksjonen «Tabellformatering» lenger ned gjelder ikke her.

**B. Frittstående leveranse** (nedlastbar HTML-fil, PDF-rapport, Excel-dashboard, eller annen artefakt brukeren laster ned/åpner utenfor selve samtalen)

Her gjelder resten av denne skillen uavkortet: full SSB-fargepalett (kategorisk, sekvensiell, divergerende), SSB-typografi (Roboto Condensed/Open Sans), tittel og kilde skrevet inn i selve diagrammet/dokumentet, og SSB-tabellstilen fra «Tabellformatering».

**Usikker på hvilken kategori du er i?** Spør deg selv: forsvinner visningen når samtalen lukkes (widget), eller er den ment å leve videre som fil (frittstående)? Er du fortsatt usikker, ikke gjett — spør brukeren.

---

## Fargesystem (hurtigoversikt)

Se `references/color-system.md` for komplett spesifikasjon med koder i alle formater.

**Rendringsmålet avgjøres av hva fargen brukes på, ikke av hvilken palett den kommer fra:**

| Brukt på                                                                    | Gjelder                                                          |
| --------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| **Data-blekk** — linjer, søyler, punkter, kartflater, heatmap-celler         | **Begge rendringsmål** — SSB-paletten som standard, hardkodet som hex |
| **Chrome** — akser, rutenett, bakgrunn, tekst, tooltip, kort                 | **Kun frittstående leveranse** — i widget: vertens tokens         |

Dette gjelder alle palettene under, også den sekvensielle rampen, den divergerende paletten og utheving-/semantikkfargene: fyller de en kartflate eller en heatmap-celle, er de data-blekk og gjelder begge rendringsmål; toner de et kort eller en bakgrunn, er de chrome og gjelder kun frittstående. Rekkefølgen og maks-antall-reglene under gjelder alltid, uavhengig av rendringsmål.

Data-blekket må kontrastsjekkes mot den faktiske bakgrunnen (≥3:1). Mot hvitt forsvinner de lyseste trinnene (`#ECFEED`, nøytralpolen `#F0F8F9`); mot mørk bakgrunn forsvinner de mørke fargene (rang 5–8, de mørke endene av rampene), og `#00824D` ligger rundt 3:1. I mørk modus: bruk rang 1–4 + Grå, og la rampene slutte der kontrasten holder. Det samme gjelder brukerens egne farger. Se `references/color-system.md`.

### Kategorisk palett (bruk i denne rekkefølgen)

| Rang | Navn           | Hex       | Rolle              |
| ---- | -------------- | --------- | ------------------ |
| 1    | SSB Grønn      | `#00824D` | Primær dataserie   |
| 2    | SSB Blå        | `#1D9DE2` | Sekundær dataserie |
| 3    | SSB Gull       | `#C78800` | Tertiær dataserie  |
| 4    | SSB Rosa       | `#C775A7` | Fjerde serie       |
| 5    | SSB Mørk Grønn | `#075745` | Femte serie        |
| 6    | SSB Mørk Blå   | `#0F2080` | Sjette serie       |
| 7    | SSB Mørk Rosa  | `#A3136C` | Syvende serie      |
| 8    | SSB Mørk Brun  | `#471F00` | Åttende serie      |
| 9    | SSB Grå        | `#909090` | "Annet" / nedtonet |

**Regler:**

- Maks 6–7 kategorier for søyler (kake og ring: maks 5). For **linjediagram er grensen lavere — maks 5 linjer** (flere overlapper og blir uleselige; bruk small multiples i stedet). Detaljer per diagramtype i `references/chart-selection.md`.
- For interaktive visninger (apper, ikke statiske rapporter) der brukeren velger fritt: vis advarsel ved overskridelse, men render likevel. Grensen er en anbefaling for lesbarhet, ikke en hard begrensning på funksjonalitet.
- Grupper det som faller utenfor som "Andre" med SSB Grå (for statiske visualiseringer).
- Rang 1 er den viktigste serien.
- Hold farge-til-kategori-mapping konsistent på tvers av alle diagrammer i en rapport.
- For 2 serier: rang 1+2. For 3: rang 1+2+3. Osv.

### Sekvensielt (lav → høy)

5-trinns grønn rampe for heatmaps og intensitet:

`#ECFEED` → `#A9D4B5` → `#66AB80` → `#00824D` → `#075745`

### Divergerende (negativ ← nøytral → positiv)

`#0F2080` → `#1D9DE2` → `#F0F8F9` → `#C78800` → `#471F00`

Blå under, oker over referansen, med lik lyshet per trinn. Skalaen er for avvik uten verdiladning (over/under gjennomsnitt); grønn leses lett som «bra». Når retningen faktisk er god eller dårlig, bruk de semantiske fargene med ▲/▼.

### Utheving

- Fokus: `#00824D` (SSB Grønn)
- Nedtonet: `#C3DCDC` (SSB Mørk 2)

Brukt på dataserier er begge data-blekk og gjelder begge rendringsmål. Men `#C3DCDC` er en lys-modus-farge: i widget med mørk bakgrunn blir nedtonede serier nesten usynlige — bruk vertens dempede tekstfarge, eller nedtone med opasitet på SSB-fargen i stedet.

### Semantiske farger

| Betydning       | Farge         | Hex       | Tillegg          |
| --------------- | ------------- | --------- | ---------------- |
| Positiv/vekst   | SSB Grønn     | `#00824D` | Alltid par med ▲ |
| Negativ/nedgang | SSB Mørk Rosa | `#A3136C` | Alltid par med ▼ |
| Nøytral         | SSB Grå       | `#909090` | —                |

Gjelder begge rendringsmål når fargen ligger på selve datamerket (søyle, pil, ikon). På tall og tekst i scorecards — også i widget — er kravet kontrast, ikke nøyaktig hex: sjekk ≥4.5:1 mot vertens bakgrunn og juster lysheten om nødvendig. `▲`/`▼` er obligatorisk uansett, slik at betydningen ikke hviler på farge alene.

---

## Typografi

**Gjelder frittstående leveranse.** I en inline chat-widget bruker du vertens typografitokens (heading-nivåer, brødtekststørrelse osv.) i stedet for tabellen under — se «Rendringsmål».

| Element         | Font             | Størrelse | Vekt    | Farge                  |
| --------------- | ---------------- | --------- | ------- | ---------------------- |
| Diagramtittel   | Open Sans        | 20px      | Bold    | `#274247`              |
| Benevning       | Open Sans        | 14px      | Regular | `#274247`              |
| Akselabels      | Open Sans        | 12px      | Regular | `#274247`              |
| Kilde/fotnote   | Open Sans        | 11px      | Regular | `#274247`              |
| Direkte merking | Open Sans        | 12px      | Bold    | `#274247`              |
| Tabell-header   | Roboto Condensed | 18px      | Bold    | `#FFFFFF` på `#274247` |
| Tabellceller    | Open Sans        | 16px      | Regular | `#162327`              |

**Fontene lastes ikke fra nett.** Bruk rekkefølgen `'Open Sans', Arial, sans-serif`: Open Sans hvis den er installert hos brukeren, ellers Arial.

---

## Diagramvalg

Se `references/chart-selection.md` for detaljert beslutningsmatrise. Hurtigguide:

| Mål                    | Bruk                                     | Unngå                               |
| ---------------------- | ---------------------------------------- | ----------------------------------- |
| Trend over tid         | Linjediagram                             | Kakediagram, søyler med >8 perioder |
| Sammenligne kategorier | Horisontale søyler (sortert)             | Kakediagram, 3D-søyler              |
| Del av helhet          | Kake- eller ringdiagram (maks 5 deler)   | Over 5 deler, 3D                    |
| Rangering              | Horisontale søyler (sortert etter verdi) | Usorterte søyler                    |
| Fordeling              | Histogram                                | Kakediagram                         |
| Geografi               | Kartdiagram (choropleth)                 | Tabell med 400 kommuner             |
| KPI / enkelttall       | Scorecard (stort tall)                   | Diagram der ett tall holder         |
| Korrelasjon            | Spredningsdiagram                        | Dobbel y-akse                       |

**Alltid unngå:** 3D-effekter, doble y-akser, avkortet y-akse på søyler og areal, bakgrunnsbilder bak diagrammer, tunge rutenett.

**Spesielt for SSB-data:**

- Tidsserier → linjediagram, ikke søyler (med mindre det er få perioder)
- Kommunesammenligninger → kart eller horisontale søyler, aldri vertikale med 400+ navn
- Befolkningspyramider → horisontalt speilet søylediagram (menn venstre, kvinner høyre)
- Indekserte serier (KPI, boligpris) → vis basisår tydelig med annotasjon

---

## Tekst og merking

**Deklarative titler** — Oppsummer innsikten, ikke beskriv diagrammet:

- Nei: "Befolkningsutvikling i Norge 2015–2025"
- Ja: "Norges befolkning passerte 5,6 millioner i 2025"

**Bygg tittel fra `extension.px.contents`.** SSB returnerer en kort tabelltittel her (f.eks. `"07459: Befolkning,"`). Bruk den som utgangspunkt, men rens først:

- Strip ledende `\d+:\s*` — tabell-ID dupliserer kildelinjen som allerede inneholder `tabell 07459`.
- Strip etterstilt komma/kolon — SSB-konvensjon: de forventer at man legger til valgte variabler.
- Utvid med valgte hoveddimensjoner og tidsperiode for å bli deklarativ. Eksempel: `"07459: Befolkning,"` + valgt region + valgt tidsspenn → `"Befolkning i Oslo, 2015–2025"`.

Hvis du ikke kan utvide deklarativt fra konteksten, bruk minimum den rensede contents-strengen som tittel og la annotasjonen gjøre observasjonen.

**Direkte merking** — Merk dataserier direkte på diagrammet. Bruk legend kun når direkte merking skaper overlapp. Plasser legend over eller til høyre — aldri under.

**Akser:**

- Merk aksene med enhet (gjelder alltid, begge rendringsmål). Y-aksens benevning står vannrett i fast posisjon over aksen, ikke rotert langs den. Ta enheten fra dataene (`category.unit[kode].base`, samme sted som desimalene) — den er skrevet ut og følger `lang`: «Prosent», «Mill. kr», «Antall». Ved egne beregninger setter du enheten og antall desimaler selv, ut fra hva tallet er — arv dem ikke fra kildetallene. Serier med ulik enhet hører ikke på samme akse.
- Bruk forkortelser: k, mill., mrd.
- Frittstående leveranse: rutenett heltrukket lys grå `#D9DFE0`, også loddrett i linjediagram; nullinje og akselinje tynn `#899597`. Stiplet er forbeholdt prognoser og brudd.
- Inline widget: bruk vertens gridline-/akselinjetokens i stedet for disse hex-verdiene — se «Rendringsmål»

**Kilde** — Kilde og siste oppdateringsdato skal alltid følge med, men plasseringen avhenger av rendringsmål:

- **Frittstående leveranse:** skrives nederst i selve diagrammet/dokumentet i `#274247`, som beskrevet under.
- **Inline widget:** skrives i chat-svarteksten rett under/over widget-kallet, ikke inni widget-koden — se «Rendringsmål».

Formulering (gjelder begge):

- Norsk: `Kilde: SSB, tabell {id}. Sist oppdatert: {YYYY-MM-DD}.`
- English: `Source: Statistics Norway, table {id}. Last updated: {YYYY-MM-DD}.`
- Flere tabeller kombinert: list opp alle — utelat ingen — med datoen per tabell når de er oppdatert ulike dager: `Kilde: SSB, tabellene {id1} og {id2}. Sist oppdatert: {dato1} ({id1}) og {dato2} ({id2}).` / `Source: Statistics Norway, tables {id1} and {id2}. Last updated: {date1} ({id1}) and {date2} ({id2}).` Samme dato for alle: oppgi den én gang.
- For andre språk (sv, dk osv.): følg samme struktur og oversett `Kilde` / `Sist oppdatert`. Ikke oversett navnet `SSB` / `Statistics Norway`.

Velg språk basert på `lang`-parameteren som ble brukt mot API-et (`lang=no` → norsk, `lang=en` → engelsk). Se `ssb-pxwebapi-v2`-skillens språk-seksjon for fullstendig regel.

Eksempel:

```
Kilde: SSB, tabell 07459. Sist oppdatert: 2026-02-27.
```

**Annotasjoner** — Korte notater direkte på diagrammet for anomalier eller vendepunkter. Tekst i `#274247`, koblet til data med tynn `#899597` linje. Maks 2–3 per diagram.

---

## Tabellformatering

**Gjelder frittstående leveranse** (HTML-fil, PDF, Excel). **Gjelder ikke inline chat-widget** — der skal tabeller ut som vanlig markdown i chat-svaret, ikke som stilsatt HTML inni widgeten. Se «Rendringsmål».

| Egenskap        | Verdi                                               |
| --------------- | --------------------------------------------------- |
| Header-bakgrunn | `#274247` (SSB Mørk 5)                              |
| Header-tekst    | `#FFFFFF`, Roboto Condensed Bold 18px               |
| Zebra-rader     | Annenhver rad `#ECFEED` (SSB Grønn 1)               |
| Celletekst      | `#162327`, Open Sans 16px                           |
| Cellepadding    | 12px horisontalt, 8px vertikalt                     |
| Tall            | Høyrejustert med tusenskilletegn (norsk: mellomrom) |
| Radhøyde        | 40px                                                |

---

## Datastorytelling

Når du bygger en serie av visualiseringer, følg denne buen:

1. **Kontekst** — Hva er situasjonen? (Scorecard med nøkkeltall)
2. **Endring** — Hva har skjedd? (Trend + annotasjon)
3. **Innsikt** — Hva forklarer det? (Sammenligning, nedbrytning)
4. **Konsekvens** — Hva betyr det? (Oppsummering, framskriving)

Bruk **utheving-paletten** for å styre oppmerksomhet: SSB Grønn på nøkkelserien, grå på resten. Gi alltid kontekst for tall (vs. forrige periode, vs. landsgjennomsnitt, vs. mål).

---

## Pre-leveranse sjekkliste

Før du leverer en visualisering, verifiser:

- [ ] Rendringsmål avklart FØRST: inline widget eller frittstående leveranse? (se «Rendringsmål»)
- [ ] Deklarativ tittel som oppsummerer innsikten — i widget: i chat-teksten, ikke inni widget-koden
- [ ] Riktig diagramtype for data og budskap
- [ ] Y-aksen starter på 0 for søyle- og arealdiagram
- [ ] Data-blekk (serier, kartflater, heatmap-celler) i riktig kategorisk rekkefølge (SSB-paletten eller brukerens farger) — gjelder begge rendringsmål
- [ ] Fargetilordning konsistent på tvers av alle diagrammer
- [ ] Direkte merking brukt der mulig
- [ ] Akser merket med enheter
- [ ] Rutenett/akselinjer: SSB-hex kun for frittstående leveranse; vertens tokens i widget
- [ ] Kilde og tidsperiode synlig — i diagrammet (frittstående) eller i chat-teksten (widget)
- [ ] WCAG AA: ≥3:1 ikke-tekst, ≥4.5:1 tekst
- [ ] Diagrammet fungerer uten farge (form/label-backup)
- [ ] Mørk modus fungerer — vertens tokens i widget; sjekk kontrast manuelt i frittstående HTML/PDF
- [ ] Ingen dekorative elementer (3D, skygger, rammer)
- [ ] Maks 6–7 kategorier i søyler og 5 deler i kake/ring (rest gruppert som "Andre"); maks 5 linjer (ellers small multiples)
- [ ] Én tydelig innsikt per diagram
- [ ] Tallformat etter `lang`: `1 234,5` (no), `1,234.5` (en)
- [ ] Fonter: Roboto Condensed + Open Sans kun for frittstående leveranse; vertens typografi i widget
- [ ] Tabeller: markdown i chat-tekst for widget; SSB-tabellstil kun for frittstående leveranse

------

Inspirert av Try sin ssb-datawiz skill
