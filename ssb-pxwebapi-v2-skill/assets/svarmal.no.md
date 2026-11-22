# Svarmal — norsk

Oppsettet for et svar med tall fra SSB. Reglene bak står i `SKILL.md` (Dataintegritet, «Språk» og Steg 5). Engelsk: `svarmal.en.md`.

- Fyll inn `{…}` fra data-responsen og metadata. Stryk en blokk som ikke gjelder uttrekket, aldri en som gjelder.
- Tall: mellomrom som tusenskille og komma som desimaltegn (1 234,5), med desimalene fra `category.unit.decimals`.
- Perioder i kolonnene når det er flere serier og få perioder. Er det én serie eller mange perioder, står periodene i radene.
- Ett tall: svar med en setning, uten tabell. Resten gjelder fortsatt: tegnet og fotnoten, notene, kilden og «Slik ble tallene hentet».
- Celler med `status`: hent tegnet fra `status` for akkurat den cellen. En `null` vises som tegnet, og et tall med flagg som tallet med tegnet etter (`{tall} {tegn}`). Aldri 0 eller tom celle.
- Fotnoten tar med bare tegnene som står i tabellen, med teksten under `no` i `standardtegn.json`. Forklarer tabellens `note` et tegn, bruk SSBs ordlyd derfra. Står tegnet verken i fila eller i noten, si at det ikke er forklart. Ikke gjett.

````markdown
{Én eller to setninger som svarer på spørsmålet: tallet, enheten og perioden.}

**{Tittel: extension.px.contents utvidet med utvalg og periode, f.eks. «Befolkning i Oslo og Bergen, 2022–2026»}** ({enhet; for en indeks også basisperioden, f.eks. 2025=100})

| {Variabel} | {periode} | {periode} | {periode} |
|---|--:|--:|--:|
| {verditekst} | {tall} | {tall} | {tall} {tegn} |
| {verditekst} | {tall} | {tegn} | {tall} |

Tegn i tabellen: `{tegn}` {tekst}, `{tegn}` {tekst}.

{For hver note i extension.noteMandatory:} Note fra SSB: {noten}

{Når tallene kan bli revidert:} Tallene for {periode} er foreløpige og kan bli endret.

Kilde: SSB, tabell [{id}](https://www.ssb.no/statbank/table/{id}). Sist oppdatert: {YYYY-MM-DD}.

**Slik ble tallene hentet**

- Utvalg: {hva et vagt begrep ble til, f.eks. «mat» = {kode} {tekst}}
- Ikke valgt, så tallene gjelder alle verdier samlet: {variabel, …}
- Kodeliste: {ID og hva den gjør, f.eks. agg_KommSummer: dagens kommuner summert fra eldre koder}
- Egne beregninger: {hva, og fra hvilke tall over}. Beregningene er ikke SSBs.
- Spørringen som ble kjørt:

```
{GET-URL-en. POST-bodyen bare når URL-en blir for lang}
```

Vil du ha tallene som diagram eller som Excel-fil?
````

**Flere tabeller:** «Kilde: SSB, tabellene [{id1}](https://www.ssb.no/statbank/table/{id1}) og [{id2}](https://www.ssb.no/statbank/table/{id2}). Sist oppdatert: {dato1} ({id1}) og {dato2} ({id2}).» Er datoen den samme for alle, oppgi den én gang.
