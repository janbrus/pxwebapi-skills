# Outputformat

Standard är `json-stat2`. Välj annat format med `outputFormat` på `/tables/{id}/data`. Vilka format som finns: Steg 4 i `SKILL.md` och `dataFormats` i `GET /config`.

**Innehåll**

1. Till Excel
2. CSV: teckenkodning och decimaler
3. `outputFormatParams`: koder och texter, titel, avgränsare
4. `heading` och `stub`: pivotering, långt format, `placement` i POST

---

## Till Excel

Hämta csv med semikolon och texter, och ange Latin-1 och punkt som decimaltecken vid importen:

```
https://statistikdatabasen.scb.se/api/v2/tables/TAB6471/data?valueCodes[Region]=0180&valueCodes[Alder]=TotSA&valueCodes[Kon]=1,2&valueCodes[ContentsCode]=000007SF&valueCodes[Tid]=top(2)&outputFormat=csv&outputFormatParams=SeparatorSemicolon,UseTexts
```

Ska tabellen pivoteras i Excel: lägg alla variabler i `stub`, se «`heading` och `stub`».

## CSV: teckenkodning och decimaler

CSV kommer som `text/csv; charset=iso-8859-1` (Latin-1), inte UTF-8, och html likaså. Decimaltecknet är alltid punkt, oavsett `lang`. I Python: `pd.read_csv(url, sep=";", encoding="latin-1")` med `SeparatorSemicolon`, eller `requests`-svarets `.text`, som läser teckenkodningen ur headern.

## `outputFormatParams`: koder och texter, titel, avgränsare

Gäller bara `csv`, `html` och `xlsx`. Tillsammans med `json-stat2` ger de 400 `Unsupported output format`.

- `UseCodes` — koder (standard)
- `UseTexts` — texter, även i kolumnrubrikerna
- `UseCodesAndTexts` — båda, som «kod - text» i samma cell
- `IncludeTitle` — tabelltiteln som första rad
- `SeparatorTab` / `SeparatorSpace` / `SeparatorSemicolon` — avgränsare (standard: komma)

Utan parametrar blir det alltså koder, ingen titel och komma. Flera parametrar ges som upprepad parameter eller kommaseparerade i en, och skiftläget spelar ingen roll. SCB:s regiontexter har redan koden (`0180 Stockholm`), så `UseCodesAndTexts` ger `0180 - 0180 Stockholm`. För `Region` räcker `UseTexts`.

## `heading` och `stub`: pivotering, långt format, `placement` i POST

`stub` är variablerna i förspalten (rader), `heading` variablerna i tabellhuvudet (kolumner), som kommaseparerade variabelkoder. Standard är tabellens egen pivotering (`extension.px.heading`/`stub`). I TAB6471 står `ContentsCode` och `Tid` i huvudet, alltså en kolumn per månad.

**Långt format:** lägg *alla* variabler i `stub`, så blir det en rad per observation, det format pivottabeller och pandas vill ha. Ordningen i `stub` styr både kolumnernas ordning och radernas sortering:

```
https://statistikdatabasen.scb.se/api/v2/tables/TAB6471/data?valueCodes[Region]=0180&valueCodes[Alder]=TotSA&valueCodes[Kon]=1,2&valueCodes[ContentsCode]=000007SF&valueCodes[Tid]=top(2)&stub=Region,Alder,Kon,ContentsCode,Tid&outputFormat=csv
```

Med `heading=Kon` och resten i `stub` blir det i stället en kolumn per kön.

I POST ligger pivoteringen i `placement` bredvid `selection`:

```
POST /tables/TAB6471/data?outputFormat=csv&outputFormatParams=SeparatorSemicolon,UseTexts
Content-Type: application/json

{
  "selection": [
    {"variableCode": "Region", "valueCodes": ["0180"]},
    {"variableCode": "Alder", "valueCodes": ["TotSA"]},
    {"variableCode": "Kon", "valueCodes": ["1", "2"]},
    {"variableCode": "ContentsCode", "valueCodes": ["000007SF"]},
    {"variableCode": "Tid", "valueCodes": ["top(2)"]}
  ],
  "placement": {
    "heading": [],
    "stub": ["Region", "Alder", "Kon", "ContentsCode", "Tid"]
  }
}
```
