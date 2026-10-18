# Lagrede spørringer

En lagret spørring er en seleksjon SSB lagrer under en ID, slik at den kan kjøres igjen. Endepunktene står under.

## Førstevalget er en vanlig URL

Til automatisering (Power Query, skript) anbefaler SSB en vanlig API-spørring med `top()`/`from()` framfor en lagret spørring: URL-en kan endres senere og er ikke bundet til en ID. Gi brukeren GET-URL-en fra uttrekket (SKILL.md Steg 5) som førstevalg. Opprett en lagret spørring bare når brukeren ber om det — den blir liggende hos SSB.

## Opprette

```
POST /savedqueries
Content-Type: application/json

{
  "tableId": "07459",
  "language": "no",
  "selection": {
    "selection": [
      { "variableCode": "Region", "valueCodes": ["0301"] },
      { "variableCode": "ContentsCode", "valueCodes": ["Personer1"] },
      { "variableCode": "Tid", "valueCodes": ["top(5)"] }
    ]
  },
  "outputFormat": "json-stat2",
  "outputFormatParams": []
}
```

Både `outputFormat` og `outputFormatParams` er obligatoriske — send `"outputFormatParams": []` hvis du ikke trenger noen, ellers svarer API-et 400 «The OutputFormatParams field is required.». Ta med alle ikke-eliminerbare variabler (`Tid`, `ContentsCode`), og bruk `top(N)`/`from()` for tid, så spørringen gir de nyeste periodene hver gang den kjøres. Svaret inneholder ID og lenke.

## Hente

| Endepunkt                          | Gir                                                                                                                                                       |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /savedqueries/{id}`           | Definisjonen: tabell, språk, seleksjon og format                                                                                                          |
| `GET /savedqueries/{id}/data`      | Dataene, i formatet spørringen ble lagret med (`outputFormat`), men **uten** de lagrede `outputFormatParams` — send dem selv. `outputFormat=…` overstyrer formatet; CSV kommer som ISO-8859-1, se `output-formats.md` |
| `GET /savedqueries/{id}/selection` | Bare seleksjonen                                                                                                                                          |

## Gamle sq-lenker fra Statistikkbanken

Lenker på formen `ssb.no/statbank/sq/{id}` hører til v2, ikke v1. Web-lenken gir i PxWeb v2 bare skjermvisning, ikke csv/xlsx, så Power Query-oppsett som pekte dit fra v1-tiden, feiler. API-endepunktene virker fortsatt for gamle ID-er (verifisert 2026-10-10):

```
GET /savedqueries/10119120
GET /savedqueries/10119120/data
```

Den første viser definisjonen (tabell 08655), den andre leverer fila. 10119120 er lagret som `csv` med `SeparatorSemicolon` og `IncludeTitle`, men `/data` gir komma og ingen tittelrad. Med `?outputFormat=csv&outputFormatParams=SeparatorSemicolon&outputFormatParams=IncludeTitle` kommer begge med. Kommaformen (`SeparatorSemicolon,IncludeTitle`) gir her bare semikolon, selv om den virker mot `/tables/{id}/data` (verifisert 2026-10-14). Et Power Query-oppsett som venter semikolon, kan derfor feile selv om ID-en virker. Hent dataene herfra, og tilby en vanlig GET-URL med `top()`/`from()` og eksplisitte `outputFormatParams` som brukeren kan legge inn i Power Query i stedet.

Feilkoder (400 uten `outputFormatParams`, 404 for feil ID): se `troubleshooting.md`.
