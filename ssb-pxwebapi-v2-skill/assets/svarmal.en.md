# Answer template — English

Layout for an answer with figures from Statistics Norway. The rules behind it are in `SKILL.md` (Dataintegritet, «Språk» and Steg 5). Norwegian: `svarmal.no.md`.

- Fill in `{…}` from the data response and the metadata, fetched with `lang=en`. Delete a block that does not apply to the extract, never one that does.
- Numbers: comma as thousands separator and point as decimal mark (1,234.5), with the decimals from `category.unit.decimals`.
- Periods in the columns when there are several series and few periods. With one series or many periods, the periods go in the rows.
- A single figure: answer with a sentence, without a table. The rest still applies: the symbol and its footnote, the notes, the source and "How the numbers were retrieved".
- Cells with `status`: take the symbol from `status` for that very cell. A `null` is shown as the symbol, and a number with a flag as the number followed by the symbol (`{figure} {symbol}`). Never 0 or an empty cell.
- The footnote lists only the symbols in the table, with the text under `en` in `standardtegn.json`. If the table's `note` explains a symbol, use SSB's wording from it. If a symbol is in neither the file nor the note, say it is not explained. Do not guess.

````markdown
{One or two sentences that answer the question: the figure, the unit and the period.}

**{Title: extension.px.contents extended with the selection and period, e.g. "Population of Oslo and Bergen, 2022–2026"}** ({unit; for an index also the base period, e.g. 2025=100})

| {Variable} | {period} | {period} | {period} |
|---|--:|--:|--:|
| {value label} | {figure} | {figure} | {figure} {symbol} |
| {value label} | {figure} | {symbol} | {figure} |

Symbols in the table: `{symbol}` {text}, `{symbol}` {text}.

{For each note in extension.noteMandatory:} Note from Statistics Norway: {the note}

{When the figures may be revised:} The figures for {period} are preliminary and may be revised.

Source: Statistics Norway, table [{id}](https://www.ssb.no/en/statbank/table/{id}). Last updated: {YYYY-MM-DD}.

**How the numbers were retrieved**

- Selection: {what a vague term became, e.g. "food" = {code} {text}}
- Not selected, so the figures cover all values combined: {variable, …}
- Codelist: {ID and what it does, e.g. agg_KommSummer: today's municipalities summed from older codes}
- Own calculations: {what, and from which figures above}. The calculations are not Statistics Norway's.
- The query that was run:

```
{the GET URL, or the POST body}
```

Would you like the figures as a chart or as an Excel file?
````

**Several tables:** "Source: Statistics Norway, tables [{id1}](https://www.ssb.no/en/statbank/table/{id1}) and [{id2}](https://www.ssb.no/en/statbank/table/{id2}). Last updated: {date1} ({id1}) and {date2} ({id2})." If the date is the same for all, give it once.
