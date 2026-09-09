# MCP-verktyg — `pxweb-mcp` mot SCB

Mappning mellan verktygen i `@jarib/pxweb-mcp` (npm) och PxWebApi v2-endpoints, samt vad verktygen *inte* täcker. Verifierat mot `@jarib/pxweb-mcp` v2.0.0, 2026-06-12; `outputValues`-fyndet verifierat mot SCB 2026-09-07. Fakta här är versionsbundna — kontrollera paketets källa när det kommer en ny major-version.

## Konfiguration

`pxweb-mcp` pekar som standard mot norska SSB. Mot SCB måste servern startas med:

```
--url https://statistikdatabasen.scb.se/api/v2
```

Verifiera vilken instans den anslutna servern använder — verktygsbeskrivningarna nämner "Statistics Norway" oavsett konfiguration. Ett snabbt test: `get_table_info` med `table_id: "TAB638"` ska lyckas mot SCB och ge 404 mot SSB.

## Verktygstabell

| Verktyg              | Motsvarar                   | Huvudparametrar                                                                  |
| -------------------- | --------------------------- | -------------------------------------------------------------------------------- |
| `search_tables`      | `GET /tables?query=…`       | `query`, `language`, `include_discontinued`                                       |
| `get_table_info`     | `GET /tables/{id}`          | `table_id`, `language`                                                            |
| `fetch_metadata`     | `GET /tables/{id}/metadata` | `table_id`, `language`                                                            |
| `query_table`        | `GET /tables/{id}/data`     | `table_id`, `value_codes`, `code_list`, `output_values`, `output_format`, `language` |
| `get_code_list`      | `GET /codelists/{id}`       | `code_list_id`, `language`                                                        |
| `list_recent_tables` | `GET /tables?pastDays=N`    | `days`, `language`                                                                |

`query_table` mappar objekten till URL-parametrar (`value_codes` → `valueCodes[Var]`, `code_list` → `codelist[Var]`, `output_values` → `outputValues[Var]`) med samma filtersyntax (`top()`, `from()`, wildcards) som GET-kanalen.

**`output_values` gör ingenting hos SCB.** `outputValues[Var]` finns i specifikationen, men mot TAB638 med `codelist[Region]=agg_RegionKommungrupp2023-` ger `aggregated`, `single`, utelämnad parameter och det ogiltiga värdet `nonsense` identiska data, alla med HTTP 200 — värdet valideras inte. Det är kodlistan (`code_list`) som aggregerar. Samma fynd hos SSB (2026-08-30). Lita inte på parametern, och läs inte ett 200-svar som bekräftelse på att den verkade.

## Begränsningar — använd HTTP när

- Du behöver `/savedqueries`, `/tables/{id}/defaultselection` eller `/config` — de exponeras inte som verktyg.
- Du behöver svenska texter: verktygens `language`-parameter stödjer endast `no`/`en`. Använd `language: "en"` mot SCB, eller HTTP med `lang=sv`.
- Du söker tabeller och behöver Steg 2-fälten: `search_tables` returnerar endast `id` + titel (utan `lastPeriod`, `timeUnit`, `discontinued`, `variableNames`) och saknar paginering — anropa `get_table_info` per kandidat, eller sök via HTTP.
- Du vill se metadata med en kodlista applicerad: `fetch_metadata` stödjer inte `codelist[Var]`-parametern — använd `get_code_list` i stället.
- Du behöver `outputFormatParams` (`UseCodesAndTexts`, `IncludeTitle`, `heading`/`stub`) — `query_table` exponerar dem inte.
