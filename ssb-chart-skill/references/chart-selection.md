# Diagramvalg — Beslutningsmatrise

Detaljerte regler for valg og utforming av diagramtyper for SSB-data.

---

## Linjediagram

**Når:** Trend over tid, 3+ tidsperioder.

**Akser:**
- Tid på x-aksen, verdi på y-aksen
- Y-aksen starter på 0 som utgangspunkt. Avkortet akse er lov når endringen er budskapet og startverdien står synlig på aksen
- For indekser (KPI, boligpris) kan y-aksen starte på en annen verdi, men marker basisverdi tydelig
- Arealdiagram starter alltid på 0 — flaten koder mengde, som en søyle

**Serier:**
- Maks 5 linjer per diagram (strengere enn den generelle maks-6–7-regelen i SKILL.md, fordi overlappende linjer blir uleselige raskere enn separate søyler). Bruk small multiples hvis du trenger å vise flere.
- For interaktive visninger der brukeren selv velger serier: vis advarsel ved overskridelse, men render likevel.
- Bruk utheving-paletten for fokusserie (SSB Grønn for nøkkelserie, grå for resten)
- Linjestil: 2px solid
- Markører bare ved <10 datapunkter — flaggede punkter (f.eks. foreløpige tall) merkes alltid

**SSB-spesifikt:**
- Vis basisår for indekser med annotasjon (f.eks. "2015=100")
- Marker prognoser/framskrivninger med stiplet linje
- Marker brudd i tidsserier (f.eks. kommunesammenslåinger) med vertikal stiplet linje og annotasjon

**Vanlige feil:**
- For mange linjer — bruk small multiples i stedet
- Manglende markering av basisår for indekser
- Avkortet y-akse uten at startverdien er tydelig, eller der budskapet er nivå og ikke endring

---

## Horisontale søyler

**Når:** Sammenligning av kategorier, rangering.

**Regler:**
- Sorter alltid etter verdi (høyest → lavest eller lavest → høyest)
- Y-aksen starter alltid på 0
- Luft mellom søylene ≈ halve søylebredden (søylen tar ⅔ av plassen: Chart.js `categoryPercentage: 0.67, barPercentage: 1`; matplotlib `width=0.67`)
- Direkte merking med verdier på enden av hver søyle
- Maks 15–20 søyler per diagram

**SSB-spesifikt:**
- For kommunesammenligninger: vis topp/bunn 10 i stedet for alle 400
- Marker landsgjennomsnitt med vertikal referanselinje i `#909090`
- Bruk SSB Grønn for enkelt-serie, kategorisk palett for grupperte søyler

**Vanlige feil:**
- Usorterte søyler — gjør det vanskelig å sammenligne
- For mange søyler — grupper eller filtrer
- Vertikale søyler med lange kategori-labels — bruk horisontale i stedet

---

## Grupperte / stablede søyler

**Når:** Sammenligne kategorier med underkategorier.

**Grupperte:**
- Maks 4 grupper per kategori
- Bruk kategorisk palett i rekkefølge
- Plasser legend over diagrammet

**Stablede:**
- Maks 5 segmenter per stabel
- Plasser det viktigste segmentet nederst
- Vis totalen på toppen av stabelen
- Bruk 100% stablet for del-av-helhet over tid

---

## Kake- og ringdiagram

**Når:** Del av helhet, inntil 5 deler. Kake og ring er likestilt; ssb.no bruker kake.

**Regler:**
- Maks 5 deler: de fire største og "Andre" (SSB Grå) for resten. "Andre" står sist før nest største, uansett størrelse
- Blir "Andre" større enn den største enkeltdelen, passer ikke kake: bruk sorterte liggende søyler, som viser alle kategoriene. Ber brukeren likevel om kake, list det som ligger i "Andre" ved siden av og nevn søylealternativet
- Største del starter kl. 12 og går med klokken; nest største starter kl. 12 og går mot klokken, så begge kan måles mot loddlinjen. Chart.js har ingen innstilling for dette: legg dataene i rekkefølgen største, 3., 4., …, "Andre", nest største
- Direkte merking med prosent OG absolutt tall
- Ring: hull 50 % av radius, og vis totalen i midten

**Vanlige feil:**
- For mange deler (>5) — vanskelig å lese
- Kake der "Andre" dominerer — da er det søylediagram som viser fordelingen

---

## Kart (choropleth)

**Når:** Geografisk variasjon på kommune- eller fylkesnivå.

**Forutsetning:** `data.role.geo` finnes i responsen. **Hvis `role.geo` mangler**, ikke prøv å rendre kart — dataene er typisk allerede aggregerte til hele Norge. Vis dem som linje (tidsserie), horisontal søyle (rangering) eller scorecard (KPI) i stedet. Ikke spør brukeren om geografi når API-et ikke har levert det.

**Regler:**
- Bruk sekvensielt grønn fra `#ECFEED` til `#075745` (se `color-system.md`); for avvik fra et snitt, den divergerende blå–oker-skalaen
- 5 kvantilgrupper er standard
- Tooltip med navn, verdi og rang
- Inkluder legend med verdiskala

**SSB-spesifikt:**
- Bruk gjeldende kommunegrenser (2024-standard)
- Vis landsgjennomsnitt i legend som referanse
- For kommunekart: vurder om fylkesnivå gir bedre oversikt
- Svalbard og Jan Mayen: inkluder kun hvis relevant data finnes

**Vanlige feil:**
- Feil kommunegrenser (bruk alltid gjeldende grenser)
- For mange fargetrinn — 5 er nok for de fleste kart
- Manglende referanseverdi (landsgjennomsnitt)

---

## Scorecard

**Når:** Enkelttall, KPI, nøkkelmetrikk.

**Regler:**
- Stort tall: 32px+ bold
- Undertekst med kontekst: periode, enhet
- Vis endring med ▲/▼ og semantisk farge (grønn/rosa)
- Bruk kortformat for store tall: 5,6 mill., 720 k

**SSB-spesifikt:**
- Vis alltid sammenligningsperiode: "5 609 000 innbyggere (+1,2 % fra 2024)"
- For indekser: vis både indeksverdi og endring

---

## Spredningsdiagram (scatter)

**Når:** Korrelasjon mellom to variabler.

**Regler:**
- Aldri bruk dobbel y-akse — bruk scatter i stedet
- Merk akser tydelig med enheter
- Bruk farge for tredje dimensjon (maks 5 kategorier)
- Inkluder trend-/regresjonslinje kun hvis statistisk meningsfull

---

## Histogram

**Når:** Fordeling av verdier.

**Regler:**
- Ingen gap mellom søyler (kontinuerlig fordeling)
- Merk x-aksen med intervallgrenser
- Inkluder gjennomsnitt/median som vertikal referanselinje

---

## Small multiples

**Når:** Samme mål for mange kategorier (f.eks. befolkningsutvikling per fylke).

**Regler:**
- Alle deldiagrammer har samme skala
- Bruk en enkel diagramtype (linje eller søyle)
- Maks 3×4 grid (12 deldiagrammer)
- Konsistent farge (SSB Grønn for alle)
- Tittel per deldiagram med kategorinavn
