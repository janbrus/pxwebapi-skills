# MCP-verktøy: pxweb-mcp

[`@jarib/pxweb-mcp`](https://github.com/jarib/pxweb-mcp) (npm) er en MCP-server som wrapper PxWebApi v2. Når verktøyene under er tilgjengelige i økten, bruk dem fremfor håndbygde HTTP-kall for operasjonene de dekker — parametrene er skjemavaliderte, så URL-encoding-feil unngås. Verktøyene er tynne wrappere: responsen er samme rå JSON-tekst (json-stat2 som standard) som HTTP-kanalen, så tolkningen av resultatet er identisk.

Innholdet under er verifisert mot kildekoden i v2.0.0 (sjekket 2026-06-12).

## Verktøy → endepunkt

| Verktøy              | Tilsvarer                  | Hovedparametre                                                                  |
| -------------------- | -------------------------- | ------------------------------------------------------------------------------- |
| `search_tables`      | `GET /tables?query=…`      | `query`, `language`, `include_discontinued`                                      |
| `get_table_info`     | `GET /tables/{id}`         | `table_id`, `language`                                                           |
| `fetch_metadata`     | `GET /tables/{id}/metadata`| `table_id`, `language`                                                           |
| `query_table`        | `GET /tables/{id}/data`    | `table_id`, `value_codes`, `code_list`, `output_values`, `output_format`, `language` |
| `get_code_list`      | `GET /codelists/{id}`      | `code_list_id`, `language`                                                       |
| `list_recent_tables` | `GET /tables?pastDays=N`   | `days`, `language`                                                               |

`query_table` mapper objektene til URL-parametre: `value_codes: { "Region": "0301,4601", "Tid": "top(5)" }` blir `valueCodes[Region]=0301,4601&valueCodes[Tid]=top(5)`, så flere verdier skrives kommaseparert i én streng; `code_list` blir `codelist[Var]` og `output_values` blir `outputValues[Var]`. Filtersyntaks (`top()`, `from()`, `range()`, wildcards) og kodelisteprefikser (`F-`/`K-`) er identiske med GET-kanalen — se `codelists-and-filters.md`.

## Begrensninger — bruk HTTP når

- **Du trenger `/savedqueries`, `/tables/{id}/defaultselection` eller `/config`** — disse er ikke eksponert som verktøy.
- **Du søker tabeller og trenger Steg 2-feltene:** `search_tables` returnerer kun `id` + tittel — `lastPeriod`, `timeUnit`, `discontinued`, `variableNames` og `paths` (kortnavn-utledningen) mangler, og det finnes ingen paginering (`pageNumber`/`pageSize`): du får bare første side (20 treff), uten total. Kall `get_table_info` per kandidat, eller søk via HTTP.
- **Du vil se metadata med kodeliste aktivert:** `fetch_metadata` støtter ikke `codelist[Var]`-parameteren (jf. fylkeseksemplet i SKILL.md) — slå opp kodelisten med `get_code_list` i stedet.
- **Du trenger `outputFormatParams`:** `query_table` eksponerer ikke `UseCodesAndTexts`, `IncludeTitle`, `heading`/`stub` eller CSV-separatorer — formatert eksport (f.eks. xlsx, se `output-formats.md`) krever HTTP.

## Konfigurasjon

Serveren startes med `--url` og kan peke mot enhver PxWebApi v2-instans; default er SSB (`https://data.ssb.no/api/pxwebapi/v2`). Hvis både SSB- og SCB-skills er i bruk: verifiser hvilken base-URL den tilkoblede instansen bruker — verktøynavnene avslører det ikke. NB: `language`-parameteren støtter kun `no`/`en`.

## Andre MCP-tjenester

TRY tilbyr en hostet SSB-MCP-tjeneste (https://tools.try.no/ssb-mcp). Den krever e-postregistrering for et personlig endepunkt og er av TRY selv merket som eksperimentell og ikke kvalitetssikret — ikke verifisert av denne skillen.

`ssb-mcp-server` og `synjan/mcp-ssb` henter fra v0-API-et, og `@pipeworx/mcp-ssb-no` tar v1-spørringer (README-ene, 2026-10-18). v2 vinner alltid — se «Verktøyvalg» i `SKILL.md`.
