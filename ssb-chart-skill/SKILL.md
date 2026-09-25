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
  version: "1.1"
  source: https://github.com/janbrus/pxwebapi-skills/tree/main/ssb-chart-skill
---

# SSB Data Visualization

Denne skillen styrer visuell presentasjon av norsk offentlig statistikk fra SSB. Den sørger for at diagrammer, tabeller og dashboards følger SSBs designsystem og best practice for statistisk datavisualisering.

---

## Kjerneprinsipper

1. **Én innsikt per diagram.** Hvert diagram formidler én tydelig observasjon. Flere historier → flere diagrammer.

2. **Statistisk integritet.** SSB-data er offentlig statistikk — presisjon er avgjørende. Y-aksen på søylediagrammer starter ALLTID på 0. Tidsserier skal ha jevne intervaller. Enheter og måleperiode må alltid synliggjøres.

3. **SSBs visuelle identitet.** Bruk SSBs offisielle farger, typografi og formspråk. Se `references/color-system.md` for komplett fargespesifikasjon.

4. **Tilgjengelighet (WCAG AA).** Ikke-tekstelementer: ≥3:1 kontrast. Tekst: ≥4.5:1 (≥3:1 for stor tekst). Aldri stol på farge alene — bruk form, mønster eller direkte merking som supplement.

5. **Kildeangivelse.** Hvert diagram skal inneholde kilde og tidsperiode. Se «Tekst og merking» → «Kilde» for fullstendig flerspråklig formulering.

6. **Datakvalitet synliggjøres, ikke skjules.** Manglende verdier (status-koder `"."`, `".."`, `":"` — se `ssb-pxwebapi-v2`-skillen for full liste) rendres som visuelle hull (`null` i datasettet, ingen linje mellom kjente punkter). Aldri interpoler, drop, eller gjenta naboverdier for å «fylle» dataene — statistisk integritet veier mer enn visuell glatthet. For tabeller: vis statussymbolet (`..`, `:`) i cellen, ikke `0`.

---

## Avhengigheter til datakilden

Denne skillen forutsetter at du har en JSON-Stat2-respons fra SSBs PxWebApi v2. **Dataintegritet-grunnregelen i `ssb-pxwebapi-v2` gjelder også her:** visualiser aldri et tall som ikke er hentet fra API-et i samme samtale. Et diagram gir tall mer autoritet enn en tabell gjør — en akse og en kildelinje får et husket tall til å se etterprøvbart ut. Kjerneprinsipp 2 og 6 dekker hvordan tallene skal *behandles*; grunnregelen dekker hvorvidt du har lov til å tegne dem i det hele tatt. For format-detaljer — row-major value-array, `role.time` / `role.metric` / `role.geo`, `dimension.{var}.category.index` og `category.unit.decimals`, status-koder `"."` / `".."` / `":"`, `extension.px.contents` — se `ssb-pxwebapi-v2`-skillens `references/json-stat2.md`. Ikke restate disse detaljene her; pek på dem.

Selve oppskriften for å gå fra JSON-Stat2-respons til et chart-config (labels, datasets, decimals, status-koder som hull) ligger i `references/jsonstat-to-chart.md`.

---

## Rendringsmål: widget vs. frittstående leveranse

Denne skillen brukes i to helt ulike rendringskontekster, og de deler IKKE samme stilregler. Avgjør rendringsmål før du velger farger, typografi eller layout — ikke etterpå.

**A. Inline chat-widget** (f.eks. `visualize:show_widget` / tilsvarende verktøy som rendrer direkte i samtalen)

Disse verktøyene har sitt eget vertsdesignsystem (layout, CSS-variabler, typografi, mørk modus) som SSB-stilen ikke skal overstyre i sin helhet. Kun dette er SSB-styrt i en widget:

- **Data-blekk** — alt som koder en verdi: datalinjer, søyler, punkter, kartflater og heatmap-celler bruker SSB-paletten (`#1A9D49`, `#1D9DE2`, `#C78800` osv.), hardkodet som hex. Canvas-baserte biblioteker (Chart.js m.fl.) kan uansett ikke lese CSS-variabler, så hardkodet hex her er riktig og nødvendig, ikke et unntak fra prinsippet om å ikke finne opp farger.

Alt annet følger vertens konvensjoner, ikke tabellene lenger ned i denne skillen:

- **Akser, rutenett, bakgrunn, generell tekst** — bruk vertens fargetoken/design (f.eks. `getComputedStyle` mot `--text-muted`, `--border` osv. der verten støtter det), ikke de hardkodede SSB-hex-verdiene fra «Tekst og merking» → «Akser».
- **Mørk modus** — obligatorisk. Vertens tokens løser dette automatisk; hardkodede lys-modus-farger som `#274247` eller `#C3DCDC` skal ikke skrives direkte inn i widget-DOM-en.
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
| **Data-blekk** — linjer, søyler, punkter, kartflater, heatmap-celler         | **Begge rendringsmål** — alltid SSB-farger, hardkodet som hex     |
| **Chrome** — akser, rutenett, bakgrunn, tekst, tooltip, kort                 | **Kun frittstående leveranse** — i widget: vertens tokens         |

Dette gjelder alle palettene under, også den sekvensielle rampen, den divergerende paletten og utheving-/semantikkfargene: fyller de en kartflate eller en heatmap-celle, er de data-blekk og gjelder begge rendringsmål; toner de et kort eller en bakgrunn, er de chrome og gjelder kun frittstående. Rekkefølgen og maks-antall-reglene under gjelder alltid, uavhengig av rendringsmål.

I widget må lyse trinn kontrastsjekkes mot vertens bakgrunn (mørk modus): `#ECFEED` og nøytralpolen `#F0F8F9` er lys-modus-farger. Se `references/color-system.md` for konkrete varianter.

### Kategorisk palett (bruk i denne rekkefølgen)

| Rang | Navn           | Hex       | Rolle              |
| ---- | -------------- | --------- | ------------------ |
| 1    | SSB Grønn      | `#1A9D49` | Primær dataserie   |
| 2    | SSB Blå        | `#1D9DE2` | Sekundær dataserie |
| 3    | SSB Gull       | `#C78800` | Tertiær dataserie  |
| 4    | SSB Rosa       | `#C775A7` | Fjerde serie       |
| 5    | SSB Mørk Grønn | `#075745` | Femte serie        |
| 6    | SSB Mørk Blå   | `#0F2080` | Sjette serie       |
| 7    | SSB Mørk Rosa  | `#A3136C` | Syvende serie      |
| 8    | SSB Mørk Brun  | `#471F00` | Åttende serie      |
| 9    | SSB Grå        | `#909090` | "Annet" / nedtonet |

**Regler:**

- Maks 6–7 kategorier for søyler/ringdiagram. For **linjediagram er grensen lavere — maks 5 linjer** (flere overlapper og blir uleselige; bruk small multiples i stedet). Detaljer per diagramtype i `references/chart-selection.md`.
- For interaktive visninger (apper, ikke statiske rapporter) der brukeren velger fritt: vis advarsel ved overskridelse, men render likevel. Grensen er en anbefaling for lesbarhet, ikke en hard begrensning på funksjonalitet.
- Grupper det som faller utenfor som "Andre" med SSB Grå (for statiske visualiseringer).
- SSB Grønn er alltid den viktigste serien.
- Hold farge-til-kategori-mapping konsistent på tvers av alle diagrammer i en rapport.
- For 2 serier: rang 1+2. For 3: rang 1+2+3. Osv.

### Sekvensielt (lav → høy)

5-trinns grønn rampe for heatmaps og intensitet:

`#ECFEED` → `#B6E8B8` → `#1A9D49` → `#075745` → `#274247`

### Divergerende (negativ ← nøytral → positiv)

- Negativ: `#A3136C` (mørk rosa)
- Nøytral: `#F0F8F9` (lys)
- Positiv: `#1A9D49` (grønn)

### Utheving

- Fokus: `#1A9D49` (SSB Grønn) eller `#00824D` (SSB Grønn 4)
- Nedtonet: `#C3DCDC` (SSB Mørk 2)

Brukt på dataserier er begge data-blekk og gjelder begge rendringsmål. Men `#C3DCDC` er en lys-modus-farge: i widget med mørk bakgrunn blir nedtonede serier nesten usynlige — bruk vertens dempede tekstfarge, eller nedtone med opasitet på SSB-fargen i stedet.

### Semantiske farger

| Betydning       | Farge         | Hex       | Tillegg          |
| --------------- | ------------- | --------- | ---------------- |
| Positiv/vekst   | SSB Grønn     | `#1A9D49` | Alltid par med ▲ |
| Negativ/nedgang | SSB Mørk Rosa | `#A3136C` | Alltid par med ▼ |
| Nøytral         | SSB Grå       | `#909090` | —                |

Gjelder begge rendringsmål når fargen ligger på selve datamerket (søyle, pil, ikon). På tall og tekst i scorecards — også i widget — er kravet kontrast, ikke nøyaktig hex: sjekk ≥4.5:1 mot vertens bakgrunn og juster lysheten om nødvendig. `▲`/`▼` er obligatorisk uansett, slik at betydningen ikke hviler på farge alene.

---

## Typografi

**Gjelder frittstående leveranse.** I en inline chat-widget bruker du vertens typografitokens (heading-nivåer, brødtekststørrelse osv.) i stedet for tabellen under — se «Rendringsmål».

| Element         | Font             | Størrelse | Vekt    | Farge                  |
| --------------- | ---------------- | --------- | ------- | ---------------------- |
| Diagramtittel   | Roboto Condensed | 20px      | Bold    | `#274247`              |
| Aksetittel      | Open Sans        | 14px      | Regular | `#274247`              |
| Akselabels      | Open Sans        | 12px      | Regular | `#274247`              |
| Kilde/fotnote   | Open Sans        | 11px      | Regular | `#909090`              |
| Direkte merking | Open Sans        | 12px      | Bold    | Seriens farge          |
| Tabell-header   | Roboto Condensed | 18px      | Bold    | `#FFFFFF` på `#274247` |
| Tabellceller    | Open Sans        | 16px      | Regular | `#162327`              |

**Fallback-fonter:** Arial, Helvetica, sans-serif

---

## Diagramvalg

Se `references/chart-selection.md` for detaljert beslutningsmatrise. Hurtigguide:

| Mål                    | Bruk                                     | Unngå                               |
| ---------------------- | ---------------------------------------- | ----------------------------------- |
| Trend over tid         | Linjediagram                             | Kakediagram, søyler med >8 perioder |
| Sammenligne kategorier | Horisontale søyler (sortert)             | Kakediagram, 3D-søyler              |
| Del av helhet          | Ringdiagram (maks 5 segmenter)           | Kakediagram med >6 segmenter        |
| Rangering              | Horisontale søyler (sortert etter verdi) | Usorterte søyler                    |
| Fordeling              | Histogram                                | Kakediagram                         |
| Geografi               | Kartdiagram (choropleth)                 | Tabell med 400 kommuner             |
| KPI / enkelttall       | Scorecard (stort tall)                   | Diagram der ett tall holder         |
| Korrelasjon            | Spredningsdiagram                        | Dobbel y-akse                       |

**Alltid unngå:** 3D-effekter, doble y-akser, kakediagrammer (bruk ringdiagram), avkortet y-akse på søyler, bakgrunnsbilder bak diagrammer, tunge rutenett.

**Spesielt for SSB-data:**

- Tidsserier → linjediagram, ikke søyler (med mindre det er få perioder)
- Kommunesammenligninger → kart eller horisontale søyler, aldri vertikale med 400+ navn
- Befolkningspyramider → horisontalt speilet søylediagram (menn venstre, kvinner høyre)
- Indekserte serier (KPI, boligpris) → vis basisår tydelig med annotasjon

---

## Tekst og merking

**Deklarative titler** — Oppsummer innsikten, ikke beskriv diagrammet:

- Nei: "Befolkningsutvikling i Norge 2015–2025"
- Ja: "Norges befolkning passerte 5.6 millioner i 2025"

**Bygg tittel fra `extension.px.contents`.** SSB returnerer en kort tabelltittel her (f.eks. `"07459: Befolkning,"`). Bruk den som utgangspunkt, men rens først:

- Strip ledende `\d+:\s*` — tabell-ID dupliserer kildelinjen som allerede inneholder `tabell 07459`.
- Strip etterstilt komma/kolon — SSB-konvensjon: de forventer at man legger til valgte variabler.
- Utvid med valgte hoveddimensjoner og tidsperiode for å bli deklarativ. Eksempel: `"07459: Befolkning,"` + valgt region + valgt tidsspenn → `"Befolkning i Oslo, 2015–2025"`.

Hvis du ikke kan utvide deklarativt fra konteksten, bruk minimum den rensede contents-strengen som tittel og la annotasjonen gjøre observasjonen.

**Direkte merking** — Merk dataserier direkte på diagrammet. Bruk legend kun når direkte merking skaper overlapp. Plasser legend over eller til høyre — aldri under.

**Akser:**

- Merk begge akser med enheter (gjelder alltid, begge rendringsmål)
- Bruk forkortelser: k, mill., mrd.
- Frittstående leveranse: rutenett lett stiplet `#C3DCDC` eller ingen, akselinjer tynn `#274247`
- Inline widget: bruk vertens gridline-/akselinjetokens i stedet for disse hex-verdiene — se «Rendringsmål»

**Kilde** — Kilde og siste oppdateringsdato skal alltid følge med, men plasseringen avhenger av rendringsmål:

- **Frittstående leveranse:** skrives nederst i selve diagrammet/dokumentet i `#909090`, som beskrevet under.
- **Inline widget:** skrives i chat-svarteksten rett under/over widget-kallet, ikke inni widget-koden — se «Rendringsmål».

Formulering (gjelder begge):

- Norsk: `Kilde: SSB, tabell {id}. Sist oppdatert: {YYYY-MM-DD}.`
- English: `Source: Statistics Norway, table {id}. Last updated: {YYYY-MM-DD}.`
- Flere tabeller kombinert: `Kilde: SSB, tabellene {id1}, {id2}, …` (list opp alle — utelat ingen).
- For andre språk (sv, dk osv.): følg samme struktur og oversett `Kilde` / `Sist oppdatert`. Ikke oversett navnet `SSB` / `Statistics Norway`.

Velg språk basert på `lang`-parameteren som ble brukt mot API-et (`lang=no` → norsk, `lang=en` → engelsk). Se `ssb-pxwebapi-v2`-skillens språk-seksjon for fullstendig regel.

Eksempel:

```
Kilde: SSB, tabell 07459. Sist oppdatert: 2026-02-27.
```

**Annotasjoner** — Korte notater direkte på diagrammet for anomalier eller vendepunkter. Tekst i `#909090`, koblet til data med tynn `#C3DCDC` linje. Maks 2–3 per diagram.

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
- [ ] Y-aksen starter på 0 for søylediagrammer
- [ ] Data-blekk (serier, kartflater, heatmap-celler) i riktig kategorisk rekkefølge (SSB-paletten) — gjelder begge rendringsmål
- [ ] Fargetilordning konsistent på tvers av alle diagrammer
- [ ] Direkte merking brukt der mulig
- [ ] Akser merket med enheter
- [ ] Rutenett/akselinjer: SSB-hex kun for frittstående leveranse; vertens tokens i widget
- [ ] Kilde og tidsperiode synlig — i diagrammet (frittstående) eller i chat-teksten (widget)
- [ ] WCAG AA: ≥3:1 ikke-tekst, ≥4.5:1 tekst
- [ ] Diagrammet fungerer uten farge (form/label-backup)
- [ ] Mørk modus fungerer — vertens tokens i widget; sjekk kontrast manuelt i frittstående HTML/PDF
- [ ] Ingen dekorative elementer (3D, skygger, rammer)
- [ ] Maks 6–7 kategorier (rest gruppert som "Andre")
- [ ] Én tydelig innsikt per diagram
- [ ] Norsk tallformat (mellomrom som tusenskilletegn)
- [ ] Fonter: Roboto Condensed + Open Sans kun for frittstående leveranse; vertens typografi i widget
- [ ] Tabeller: markdown i chat-tekst for widget; SSB-tabellstil kun for frittstående leveranse

------

Inspirert av Try sin ssb-datawiz skill
