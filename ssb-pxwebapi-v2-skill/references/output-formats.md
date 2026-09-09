# Outputformater

Standard er `json-stat2`. Velg annet format med `outputFormat`-parameter på `/tables/{id}/data` (og `/savedqueries/{id}/data`).

| Format     | `outputFormat`-verdi | Bruk                                 |
| ---------- | -------------------- | ------------------------------------ |
| json-stat2 | `json-stat2`         | Standard, maskinlesbar, rik metadata |
| CSV        | `csv`                | Enkelt tabulært format               |
| Excel      | `xlsx`               | For sluttbrukere                     |
| HTML       | `html`               | Tabell for visning                   |
| PX         | `px`                 | Tradisjonelt PX-format               |
| JSON-PX    | `json-px`            | JSON-variant av PX                   |
| Parquet    | `parquet`            | Kolonneformat for dataanalyse (pandas, DuckDB) |

Sjekk `dataFormats` i `GET /config` for gjeldende formatliste.

## Parquet

Kolonneformat for dataanalyse — les direkte med pandas eller DuckDB. Returneres som `application/octet-stream`, med lang-format: én rad per observasjon, pluss en `timestamp`-kolonne.

Kolonnenavn avhenger av hvor mange statistikkvariabler uttrekket har:

| Uttrekk                  | Verdikolonne             | Statuskolonne                   |
| ------------------------ | ------------------------ | ------------------------------- |
| Én statistikkvariabel    | `value`                  | `value_symbol`                  |
| Flere statistikkvariabler | `ContentsCode_{kode}`   | `ContentsCode_{kode}_symbol`    |

**`_symbol`-kolonnene bærer `status`-kodene** — les dem, ikke bare verdikolonnen. Manglende, foreløpige og konfidensielle verdier er ellers usynlige i et parquet-uttrekk.

Parquet bruker alltid koder, aldri tekst: `outputFormatParams=UseCodesAndTexts` gir HTTP 400 mot dette formatet.

## OutputFormatParams (kan kombineres)

Gjelder kun `csv`, `html` og `xlsx`. Mot `json-stat2` gir enhver `outputFormatParams` HTTP 400 (verifisert 2026-09-09), og mot `parquet` gir `UseCodesAndTexts` 400 (se over).

- `UseCodes` — koder (standard)
- `UseTexts` — tekster
- `UseCodesAndTexts` — begge, som «kode - tekst» i samme celle
- `IncludeTitle` — tabelltittel som første rad
- `SeparatorTab` / `SeparatorSpace` / `SeparatorSemicolon` — skilletegn for CSV (standard: komma)

Uten parametre får du altså kun koder, ingen tittel og komma som skilletegn. Flere parametre kan gis som gjentatt parameter eller kommaseparert i én — begge former virker, og verdiene er ikke case-sensitive (`separatorsemicolon,usecodesandtexts` i SSBs egne eksempler):

```
POST /tables/07221/data?outputFormat=xlsx&outputFormatParams=UseCodesAndTexts&outputFormatParams=IncludeTitle
```

```
https://data.ssb.no/api/pxwebapi/v2/tables/03024/data?valueCodes[ContentsCode]=*&valueCodes[Varegrupper2]=*&valueCodes[Tid]=top(3)&outputFormat=csv&outputFormatParams=SeparatorSemicolon,UseCodesAndTexts
```

### CSV: tegnsett og desimaler

CSV leveres som `text/csv; charset=iso-8859-1` (Latin-1), ikke UTF-8 — også fra `/savedqueries/{id}/data` (verifisert 2026-09-09). I Python: `pd.read_csv(url, sep=";", encoding="latin-1")`, eller bruk `requests`-responsens `.text`, som leser tegnsettet fra headeren. Desimalskilletegn er alltid punktum, unntatt xlsx på norsk (komma) — se `api-details.md`.

## heading og stub — pivotering

`stub` = variabler i forspalten (rader), `heading` = variabler i tabellhodet (kolonner). Kommaseparert liste av variabelkoder, kun relevant for csv/html/xlsx. Standard er tabellens egen pivotering (`extension.px.heading`/`stub` i metadata), typisk med ContentsCode og Tid i hodet — det gir en bred tabell med én kolonne per periode.

**Pivotvennlig langformat:** legg *alle* variabler i `stub`, så får du én rad per observasjon — formatet Excel-pivot, pandas og Power BI vil ha. SSBs eget eksempel (verifisert 2026-09-09):

```
https://data.ssb.no/api/pxwebapi/v2/tables/03024/data?valueCodes[ContentsCode]=*&valueCodes[Varegrupper2]=*&valueCodes[Tid]=top(3)&stub=Varegrupper2,Tid,ContentsCode&outputFormat=csv&outputFormatParams=SeparatorSemicolon,UseCodesAndTexts
```

Samme uttrekk med `stub=Varegrupper2,Tid&heading=ContentsCode` gir én kolonne per statistikkvariabel i stedet. Rekkefølgen i `stub` styrer kolonnerekkefølgen; SSB anbefaler Tid og ContentsCode sist.

I POST ligger pivoteringen i `placement` ved siden av `selection`:

```json
{
  "selection": [ "…" ],
  "placement": { "heading": [], "stub": ["Varegrupper2", "Tid", "ContentsCode"] }
}
```

### Til Excel via Power Query

SSBs oppskrift (https://www.ssb.no/api/fra-pxwebapi-v2-til-excel): bygg en GET-URL med `outputFormat=csv&outputFormatParams=SeparatorSemicolon,UseTexts` og alle variabler i `stub`; lim den inn i Excel under Data → Fra Internett; bytt desimalpunktum til komma i Power Query; slå på «Oppdater data når filen åpnes». Bruk `top()`/`from()` i URL-en, så følger arbeidsboken nye publiseringer.
