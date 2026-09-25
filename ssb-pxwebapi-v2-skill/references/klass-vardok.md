# Klass og VarDok — SSBs metadata-systemer

Metadata-responsen fra `/tables/{id}/metadata` kobler tabellen og variablene til SSBs metadata-systemer via `link`-objekter, med to relasjonstyper:

- **`link.describedby`** — maskinlesbare URN-er, for oppslag mot Klass API
- **`link.related`** — ferdige, menneskelesbare lenker med label, for henvisning og videre lesning

`link` finnes på både rot-nivå (om statistikken) og variabel-nivå (om den enkelte dimensjonen). Data-responser (`/tables/{id}/data`) inneholder kun `describedby` — `related` finnes bare i metadata-responsen.

## Kortnavn før du har metadata

I søkefasen (Steg 2) har du bare `/tables`-treffet, ikke metadata — og dermed ingen `link.related`. Kortnavnet kan likevel leses ut av `paths`.

`paths` er en **liste av stier**, der hver sti er en liste av noder med `id` og `label`. Statistikkens kortnavn er tredje node i stien, `paths[0][2].id`:

| Tabell | `paths[0]` (id-er)                           | Kortnavn      |
| ------ | -------------------------------------------  | ------------- |
| 07459  | `be` → `be01` → `folkemengde` → `SBMENU6924` | `folkemengde` |
| 14700  | `if` → `if01` → `kpi` → `SBMENU12005`        | `kpi`         |
| 07221  | `bb` → `bb01` → `bpi` → `SBMENU4008`         | `bpi`         |

Kortnavnet gir tre ting uten flere API-kall:

- Statistikksiden: `https://www.ssb.no/<kortnavn>`
- «Om statistikken» med definisjoner og forklaringer: `https://www.ssb.no/<kortnavn>#om-statistikken` (engelsk: `https://www.ssb.no/en/<kortnavn>#om-statistikken`) — f.eks. `https://www.ssb.no/arblonn#om-statistikken`
- RSS-feeden for statistikken: `https://www.ssb.no/rss/statbank/<kortnavn>` (se `api-details.md`)

Har du først hentet metadata, trengs ikke utledningen: `<root>.link.related` gir de to første lenkene ferdig, og `extension.metaid` (`KORTNAVN:<kortnavn>`) gir kortnavnet direkte — se under.

En tabell kan ha **flere stier**. KOSTRA-tabellene ligger både under sin fagstatistikk og under `os` → `os01` → `kostrahoved` (12134: `paths[0]` = `kommregnko`, `paths[1]` = `kostrahoved`), og et mindretall har bare kostrahoved-stien. Begge er gyldige kortnavn — `https://www.ssb.no/kostrahoved` redirecter til KOSTRA-siden — men fagstatistikkens kortnavn gir den mest spesifikke «Om statistikken». Se `kostra.md`.

## Rot-nivå: statistikkside og «Om statistikken»

`<root>.link.related` gir ferdige lenker til statistikken tabellen tilhører:

```json
"link": {
  "related": [
    {
      "extension": { "relation": "statistics-homepage", "metaid": "KORTNAVN:folkemengde" },
      "href": "https://www.ssb.no/folkemengde",
      "label": "Statistikkside",
      "type": "text/html"
    },
    {
      "extension": { "relation": "about-statistics", "metaid": "KORTNAVN:folkemengde" },
      "href": "https://www.ssb.no/folkemengde#om-statistikken",
      "label": "Definisjoner og forklaringer",
      "type": "text/html"
    }
  ]
}
```

- `relation: "statistics-homepage"` → statistikksiden (`ssb.no/<kortnavn>`)
- `relation: "about-statistics"` → «Om statistikken»-siden med definisjoner og forklaringer
- `extension.metaid` = `KORTNAVN:<kortnavn>` — gir statistikkens kortnavn direkte, uten å utlede det fra `paths` (utledningen over trengs kun i søkefasen, før du har hentet metadata)
- Lenker og labels følger `lang`-parameteren: `lang=en` gir `/en/`-URL-er og engelske labels («Statistics page», «Definitions and explanations»)

## Variabel-nivå: definisjoner per variabel

`dimension.{var}.link.related` gir én lenke per klassifikasjon/variabeldefinisjon, med `relation: "definitions"` og `metaid` lik URN-en fra `describedby`:

```json
"dimension": {
  "Kjonn": {
    "link": {
      "describedby": [
        { "extension": { "Kjonn": "urn:ssb:classification:klass:2" } }
      ],
      "related": [
        {
          "extension": { "relation": "definitions", "metaid": "urn:ssb:classification:klass:2" },
          "href": "https://www.ssb.no/klass/klassifikasjoner/2",
          "label": "Standard for kjønn",
          "type": "text/html"
        }
      ]
    }
  }
}
```

Labelen forteller hva lenken er — Klass-lenker heter «Standard for …» (f.eks. «Standard for kommuneinndeling»), VarDok-lenker «Variabeldefinisjon av …» (f.eks. «Variabeldefinisjon av Månedslønn (kr)»). Bruk disse ferdige lenkene når du henviser brukeren til definisjoner — URN-omskriving trengs bare for maskinlesbare oppslag (under).

I `describedby` er `extension`-nøkkelen enten variabelnavnet (URN-er som gjelder hele variabelen, evt. flere adskilt med mellomrom) eller en enkeltverdi-kode (URN som definerer akkurat den verdien — vanlig for `ContentsCode`, der hver statistikkvariabel kan ha sin egen VarDok-definisjon).

## Klassifikasjoner (Klass)

URN-er på formen `"urn:ssb:classification:klass:131"` peker til SSBs system for klassifikasjoner og kodelister. Tallet til slutt er klassifikasjons-ID. Omskrives til Klass API for maskinlesbart oppslag:

- `https://data.ssb.no/api/klass/v1/classifications/131.json`

Eksempel: `"urn:ssb:classification:klass:691"` → `https://data.ssb.no/api/klass/v1/classifications/691.json`

(Menneskelesbar side: `https://www.ssb.no/klass/klassifikasjoner/131` — samme URL som `link.related` gir ferdig.)

Klass er nyttig for:

- Fullstendige kodeverk med historikk
- Korrespondansetabeller (gammel→ny kommunestruktur)
- Gyldighetsperioder for koder

Komplett kommuneklassifikasjon ligger på ID 131.

KOSTRA-kommunegruppene (`EKG01`–`EKG17`, brukt som regionkoder i KOSTRA-tabellene) er klassifikasjon 112 «Kodeliste for KOSTRA - kommunegruppering», versjon 1450 = 2020-grupperingen (eldre: 423 for 2004-06–2019, 1288 for 2019). Hvilken gruppe en kommune tilhører leses fra korrespondansetabellen gruppering → kommuneinndeling for riktig år — gjeldende er 2840 (2026; Bergen 4601 → `EKG12`, Oslo 0301 → `EKG13`), eldre 1358 (2024), 1483 (2023), 1482 (2022), 978 (2020). Fylkeskommunegruppene (`EAFK01`–`EAFK06`) er klassifikasjon 152, korrespondanse 1310. Verifisert 2026-09-20:

- `https://data.ssb.no/api/klass/v1/classifications/112.json`
- `https://data.ssb.no/api/klass/v1/correspondencetables/2840.json`
- `https://data.ssb.no/api/klass/v1/classifications/152.json`

Hva gruppene er og hvordan de brukes i spørringer: se `kostra.md`.

Delområder og grunnkretser ligger på ID 1, «Standard for delområde- og grunnkretsinndeling», med årlige versjoner (2026-utgaven er versjon 3306: 1 906 delområder på nivå 1 med koder `KKKKDD00`, 14 487 grunnkretser på nivå 2 med `parentCode` til delområdet). Grunnkretstabellene i PxWeb peker hit via `link.related` (`https://www.ssb.no/klass/klassifikasjoner/1`), men har bare grunnkretsnivået — delområdekodene fra Klass finnes ikke som verdier der. Verifisert 2026-09-20:

- `https://data.ssb.no/api/klass/v1/classifications/1.json`
- `https://data.ssb.no/api/klass/v1/versions/3306.json`

Hva det betyr i praksis (wildcard på delområdeprefiks, hvilke tabeller som har delområder): se «Regionale nivåer under kommune» i `codelists-and-filters.md`.

Standard for næringsgruppering (SN) ligger på ID 6, med SN2007 som versjon 30 (gyldig 2009-01-01 til 2025-01-01) og SN2025 som versjon 3218 (gyldig fra 2025-01-01, 1 785 koder på fem nivåer). Korrespondansetabellen SN2025 → SN2007 er ID 2919 — 1 034 rader, kun på 5-siffernivå (f.eks. `62.100` → `62.010`), så bokstav- og tosiffernivå må kobles via labelene. Alle tre verifisert 2026-09-20:

- `https://data.ssb.no/api/klass/v1/classifications/6.json`
- `https://data.ssb.no/api/klass/v1/versions/3218.json`
- `https://data.ssb.no/api/klass/v1/correspondencetables/2919.json`

Hva overgangen betyr i PxWebApi (variabel-ID `NACE2025`, forskjøvne bokstavkoder, parallelle tabeller): se «Næringskoder: SN2007 → SN2025» i `codelists-and-filters.md`.

## Variabeldefinisjoner (VarDok)

URN-er på formen `"urn:ssb:conceptvariable:vardok:3380"` peker til SSBs variabeldefinisjoner. Tallet til slutt er variabel-ID. Omskrives til:

- Norsk: `https://www.ssb.no/a/metadata/conceptvariable/vardok/3380/nb`
- Engelsk: `https://www.ssb.no/a/metadata/conceptvariable/vardok/3380/en`

(Samme URL-er som `link.related` gir ferdig, med språk etter `lang`-parameteren.)

VarDok gir definisjoner, avgrensninger og bakgrunnsinformasjon for statistiske begreper.
