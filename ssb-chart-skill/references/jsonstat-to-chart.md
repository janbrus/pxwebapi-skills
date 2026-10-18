# JSON-stat2 → diagram-config — oppskrift

Hvordan gå fra en JSON-stat2-respons fra SSBs PxWebApi v2 til et chart-bibliotek-config (Chart.js, Recharts, matplotlib …). Selve dataformatet er dokumentert i `ssb-pxwebapi-v2`-skillens `references/json-stat2.md` — denne filen handler kun om mappingen til chart-data.

---

## Steg 1 — Velg akse-dimensjon

For tidsserier (linjediagram) er x-aksen alltid tidsdimensjonen:

```js
const timeDim = data.role?.time?.[0];  // f.eks. "Tid"
if (!timeDim) {
  // Ingen tidsdimensjon → ikke en tidsserie. Bytt til søyle/horisontal eller scorecard.
}
```

Hvis dataene ikke har `role.time`, ikke prøv å lage en linjediagram-tilfelle ut av en non-time dim. Vurder horisontal søyle (rangering) eller scorecard (enkelttall) i stedet.

---

## Steg 2 — Bygg x-akse-labels i riktig rekkefølge

`dimension[timeDim].category.index` mapper kode → numerisk index. **Sorter etter index-verdien**, ikke alfabetisk:

```js
const timeDimObj = data.dimension[timeDim];
const timeCodes = Object.keys(timeDimObj.category.index)
  .sort((a, b) => timeDimObj.category.index[a] - timeDimObj.category.index[b]);
const xLabels = timeCodes.map(code => timeDimObj.category.label?.[code] || code);
```

**Hvorfor ikke alfabetisk:** `"2020M2"` og `"2020M10"` sorterer feil alfabetisk (M10 før M2). SSB returnerer alltid riktig index — bruk den.

**Men index følger rekkefølgen i *spørringen*:** API-et sorterer ikke. `valueCodes[Tid]=2026,2024,2025` gir x-aksen 2026, 2024, 2025, mens `top(n)` og `from(x)` gir stigende rekkefølge (verifisert 2026-10-02). Skriver du en eksplisitt liste med tidskoder, skriv den stigende.

---

## Steg 3 — Bygg datasets (serier) fra øvrige dimensjoner

Hver kombinasjon av non-time dimensjonsverdier blir én serie (linje). Beregn flat-index inn i `data.value`-arrayet med formelen i `json-stat2.md` (row-major, `id` + `size` + `category.index`): hver posisjon ganges med dimensjonens stride, produktet av `size` for alle senere dimensjoner i `data.id`. Iterer alltid over `data.id`, aldri over `Object.keys(data.dimension)`.

```js
// Kodene i en dimensjon, i category.index-rekkefølge (objektform hos SSB)
function codesInOrder(data, dim) {
  const idx = data.dimension[dim].category.index;
  return Object.keys(idx).sort((a, b) => idx[a] - idx[b]);
}

// codes: én kode per dimensjon, i samme rekkefølge som data.id
function calculateFlatIndex(data, codes) {
  let flatIdx = 0, stride = 1;
  for (let k = data.id.length - 1; k >= 0; k--) {   // siste dimensjon varierer raskest
    flatIdx += data.dimension[data.id[k]].category.index[codes[k]] * stride;
    stride *= data.size[k];
  }
  return flatIdx;
}

// Kartesisk produkt av dimensjonene, i category.index-rekkefølge
function* allCombinations(dims, data) {
  if (dims.length === 0) { yield { codes: [] }; return; }
  const [first, ...rest] = dims;
  for (const code of codesInOrder(data, first))
    for (const tail of allCombinations(rest, data)) yield { codes: [code, ...tail.codes] };
}

const nonTimeDims = data.id.filter(d => d !== timeDim);
const datasets = [];

for (const combo of allCombinations(nonTimeDims, data)) {
  const values = [], flags = [];
  for (const timeCode of timeCodes) {
    // Kodene i data.id-rekkefølge: tidskoden der tidsdimensjonen står, ellers fra combo
    const codes = data.id.map(d => d === timeDim ? timeCode : combo.codes[nonTimeDims.indexOf(d)]);
    const flatIdx = calculateFlatIndex(data, codes);
    values.push(readValue(data, flatIdx));   // Steg 5: null → hull
    flags.push(readStatus(data, flatIdx));   // Steg 5: status på et tall → flagg
  }
  datasets.push({ label: /* steg 4 */, data: values, flags });
}
```

Verifisert 2026-10-02 i node mot 07459 (2 regioner × 3 år, sammenlignet med samme uttrekk som csv) og 09842 (flagg på foreløpige tall).

---

## Steg 4 — Lag serielabels

Slå sammen `category.label[code]` for hver dim i kombinasjonen med ` · ` (mellomrom-punkt-mellomrom) som joiner:

```js
const labelParts = combo.codes.map((code, i) => {
  const dim = data.dimension[nonTimeDims[i]];
  return dim.category.label?.[code] || code;  // fall tilbake til kode hvis label mangler
});
const seriesLabel = labelParts.join(' · ');
// Eksempel: "Hele landet · Menn · 2 år · Personer"
```

**Én-serie-tilfelle:** Hvis det ikke finnes non-time dimensjoner (eller alle har størrelse 1), blir labelen tom. Fall tilbake til renset `data.extension?.px?.contents` (se SKILL.md → «Bygg tittel fra `extension.px.contents`») slik at legenden ikke står tom.

**Aktive kodelister:** Hvis brukeren har valgt `agg_KommFylker`, vil `dimension[Region].category.label` inneholde fylkesnavn (ikke kommunenavn). Bruk samme oppslag — kodelistene reflekteres i `category.label` allerede.

---

## Steg 5 — Status: hull eller flagg

`data.value` og `data.status` er to kanaler. Les dem hver for seg:

- **`value` er `null`** → hull. Status-koden (`"."`, `".."`, `":"`, `"-"` — se `json-stat2.md` og `troubleshooting.md` for full liste) forklarer hvorfor. Vis aldri hullet som 0.
- **`value` har tall og `status` er satt** → flagg, ikke hull. 09842 (BNP per innbygger) har `"*"` = foreløpig tall på 2023–2024, og tallene står i `value`. Tegn punktet og merk det.

```js
function readValue(data, flatIdx) {
  const v = data.value[flatIdx];
  return (v == null || !Number.isFinite(v)) ? null : v;   // hull bare når tallet mangler
}

function readStatus(data, flatIdx) {
  return data.status?.[String(flatIdx)] ?? null;          // flagg, f.eks. "*" = foreløpig tall
}
```

I Chart.js: sett `spanGaps: false` på datasettet slik at `null` faktisk lager hull i stedet for å trekke linjer mellom kjente punkter. Flaggene ligger i `dataset.flags` (Steg 3). Bruk dem i en scriptable `pointStyle` (f.eks. hult punkt der `ctx.dataset.flags[ctx.dataIndex]` er satt) og i tooltip-callbacken, og forklar tegnet i en fotnote under diagrammet. SSB forklarer tegnet i tabellens `note` (09842: «* = Foreløpig tall»).

**Foreløpige tall som bare står i noten.** Noen tabeller har ingen `status`, men sier i datasettets `note` hvilke perioder som er foreløpige (09189: «Tallene etter år 2023 (basisåret) er foreløpige.»). Merk de periodene som flagg på samme måte, og siter noten i fotnoten. Gå ikke ut over det noten sier, og spriker notene, si det i fotnoten.

**Hvorfor:** Statistisk integritet. Antall innbyggere kan ikke interpoleres — at vi *ikke vet* tallet er en observasjon i seg selv. Aldri drop, interpoler, eller gjenta nabopunkter for å «fylle» dataene. Det motsatte er like galt: å blanke et foreløpig tall fordi cellen har en status, kaster et publisert tall. Tidligere versjoner av `readValue` gjorde nettopp det.

---

## Steg 6 — Desimaler og enhet per metric

Hardkod aldri antall desimaler eller enheten. SSB oppgir begge per ContentsCode-verdi, i `category.unit`:

```js
const metricDim = data.role?.metric?.[0];          // f.eks. "ContentsCode"
const metricCode = /* hvilken kode fra combo som tilhører metricDim */;
const unitInfo = data.dimension[metricDim]?.category.unit?.[metricCode];
const decimals = unitInfo?.decimals
              ?? data.extension?.px?.decimals       // dataset-default
              ?? 0;                                 // siste utvei
const unit = unitInfo?.base ?? '';                  // benevningen, på språket fra lang
```

Lagre begge på datasettet (custom-properties — Chart.js bevarer ukjente felter):

```js
datasets.push({ label, data: values, flags, decimals, unit });
```

`base` er skrevet ut og følger `lang`: `prosent`/`per cent`, `mill. kr`/`NOK million`, `kr per innbygger`/`NOK per capita`, `indeks`/`index`, `antall`/`number`. Benevningen over y-aksen er `base` med stor forbokstav (endre bare første tegn — `NOK million` skal ikke bli «Nok million»). For indekser hører basisåret med («2025=100») — det står i serielabelen, ikke i `base`. Én tabell kan ha flere enheter (14700: indeks, prosent og promille): serier med ulik enhet hører ikke på samme y-akse, så lag ett diagram per enhet (aldri to y-akser).

**Egne beregninger** (per innbygger, andeler, endringer) har verken `base` eller `decimals` i dataene: sett `unit` og `decimals` på serien selv, ut fra hva tallet er. Arv dem ikke fra kildetallene — BNP i `mill. kr` (0 desimaler) delt på folketall er `kr per innbygger` (0 desimaler), og endringen i den er `prosent` med 1 desimal, som SSBs egne endringstall.

Bruk det i tooltip-callback og som y-akse-presisjon:

```js
plugins.tooltip.callbacks.label = (ctx) =>
  `${ctx.dataset.label}: ${formatNumber(ctx.parsed.y, ctx.dataset.decimals)}`;

// Y-akse: hvis flere serier har ulik presisjon, bruk maks av dem
const yAxisDecimals = Math.max(...datasets.map(d => d.decimals));
scales.y.ticks.callback = (v) => formatNumber(v, yAxisDecimals);
```

**Edge case — `agg_`-kodeliste på metric:** En aggregert kode finnes ikke i `unit{}`. Slå opp kodelistens `valueMap` for å finne underliggende original-koder; bruk maks desimaler blant dem (eller første — i praksis deler de presisjon). Dokumenter valget med én linje kommentar.

**Eksempler på faktiske desimaler:**
- `Personer1` (befolkning) → `0`
- `KpiIndMnd` (KPI-indeks) → `1`
- `KvPris` (kvadratmeterpris) → `0`
- Valutakurser → `4`

Hardkoding av 2 desimaler gir tooltip som `Personer1: 31 108,00` — feil, og brudd på SSBs presisjons-konvensjon.

---

## Helhetlig eksempel (Chart.js v4)

Se `format-guidelines.md` → seksjonen «Vanilla JS + Chart.js» for et komplett eksempel som setter alle stegene over sammen med SSB-paletten, kildelinje og tittel-rensing.
