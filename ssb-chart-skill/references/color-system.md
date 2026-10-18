# SSB Fargesystem — Komplett referanse

Alle farger i SSBs designsystem for datavisualisering, med verdier i relevante formater.

Basert på SSBs Plotly Template og designsystem.

**Verdiene under er standardpaletten, ikke et krav.** Ber brukeren om egne farger, eller har rapporten en egen palett, bruk dem. Standardpaletten er kontrollert for kontrast (WCAG) og skillbarhet for fargeblinde; egne farger må sjekkes på samme måte, mot både lys og mørk bakgrunn når visningen kan vises i mørk modus.

**Skillet mellom data-blekk og chrome avgjør rendringsmål.** Selve fargeverdiene under er rendringsmål-uavhengige *data* — det er hva du bruker dem på som avgjør (se SKILL.md → «Rendringsmål»):

- **Data-blekk** — linjer, søyler, punkter, kartflater, heatmap-celler. Styrt av skillen (SSB-paletten som standard), hardkodet som hex, i **begge rendringsmål**. Canvas-biblioteker kan ikke lese CSS-variabler, så hardkodet hex er riktig her, ikke et unntak.
- **Chrome** — akser, rutenett, bakgrunn, tekst, tooltip, fonter, kort. SSB-verdiene under (`#274247`, `#D9DFE0`, `#899597`, `#FFFFFF`, `#F0F8F9`) gjelder **kun frittstående leveranse**. I en inline chat-widget styres chrome av vertens tokens, ellers brytes mørk modus.

De ferdige tema-objektene nederst (Recharts, Chart.js, matplotlib) blander begge deler i ett objekt. Bruk dem derfor ikke rått i widget — se delingen i hver seksjon.

---

## Primærfarger (identitet)

**Chrome-farger — gjelder kun frittstående leveranse.** Fargene i denne seksjonen brukes til tekst, akser, rutenett, rammer og bakgrunner. I en inline chat-widget erstattes de av vertens tokens; skriv dem ikke inn i widget-DOM-en. Unntak: brukt på selve dataserien er utheving data-blekk og gjelder begge rendringsmål — `#00824D` (SSB Grønn 4) som fokusfarge, `#C3DCDC` (SSB Mørk 2) som nedtoning. Merk at `#C3DCDC` er lys: mot mørk vert-bakgrunn forsvinner nedtonede serier, så nedtone heller med opasitet på seriefargen. Se SKILL.md → «Utheving».

### SSB Mørk 5
Tekst, akser, rammer, header-bakgrunn.

- Hex: `#274247`
- RGB: 39, 66, 71
- CSS: `--ssb-dark-5: #274247;`
- JS: `ssbDark5: '#274247'`
- Python: `ssb_dark_5 = '#274247'`
- openpyxl: `PatternFill(start_color='274247', fill_type='solid')`

### SSB Grønn 4
Primær aksent.

- Hex: `#00824D`
- RGB: 0, 130, 77
- CSS: `--ssb-green-4: #00824D;`
- JS: `ssbGreen4: '#00824D'`
- Python: `ssb_green_4 = '#00824D'`
- openpyxl: `PatternFill(start_color='00824D', fill_type='solid')`

### SSB Hvit
Bakgrunn.

- Hex: `#FFFFFF`
- CSS: `--ssb-white: #FFFFFF;`

### SSB Mørk 1
Lys bakgrunn, dashbordflate (diagrammene på hvite kort), zebra-rader (alternativ).

- Hex: `#F0F8F9`
- RGB: 240, 248, 249
- CSS: `--ssb-dark-1: #F0F8F9;`
- JS: `ssbDark1: '#F0F8F9'`
- Python: `ssb_dark_1 = '#F0F8F9'`
- openpyxl: `PatternFill(start_color='F0F8F9', fill_type='solid')`

### SSB Mørk 2
Nedtonede elementer.

- Hex: `#C3DCDC`
- RGB: 195, 220, 220
- CSS: `--ssb-dark-2: #C3DCDC;`
- JS: `ssbDark2: '#C3DCDC'`
- Python: `ssb_dark_2 = '#C3DCDC'`

### Rutenett
Heltrukne støttelinjer, som på ssb.no. Dekorativt (1,35:1 mot hvitt) — informasjonen ligger i aksetallene. Stiplet er forbeholdt prognoser og brudd.

- Hex: `#D9DFE0`
- RGB: 217, 223, 224
- CSS: `--ssb-grid: #D9DFE0;`
- JS: `ssbGrid: '#D9DFE0'`
- Python: `ssb_grid = '#D9DFE0'`

### Nullinje
Nullinje og akselinjer. 3,08:1 mot hvitt (≥3:1 for ikke-tekst).

- Hex: `#899597`
- RGB: 137, 149, 151
- CSS: `--ssb-zero-line: #899597;`
- JS: `ssbZeroLine: '#899597'`
- Python: `ssb_zero_line = '#899597'`

---

## Kategorisk palett

**Data-blekk — gjelder begge rendringsmål.** Dette er den delen av fargesystemet som skillen styrer også i en inline chat-widget der alt annet følger verten.

Bruk i denne rekkefølgen. For N serier, bruk rang 1 til N.

**Mørk bakgrunn:** rang 5–8 (`#075745`, `#0F2080`, `#A3136C`, `#471F00`) har bare 1,0–2,6:1 mot typiske mørke bakgrunner (`#121212`–`#30302E`), og `#00824D` faller til ca. 3:1 på de lyseste av dem. Rang 2–4 og Grå holder ≥4:1. I mørk modus: bruk rang 1–4 + Grå, og sjekk `#00824D` mot den faktiske bakgrunnen.

### 1. SSB Grønn (primær dataserie)
Samme farge som SSB Grønn 4. Fra og med versjon 1.3 av skillen erstatter den `#1A9D49`, som var nesten lik SSB Gull for protanope (avstand 3,4 i OKLab, mot 9,7 med `#00824D`).
- Hex: `#00824D`
- RGB: 0, 130, 77
- CSS: `--ssb-cat-1: #00824D;`
- JS: `ssbGreen: '#00824D'`
- Python: `ssb_green = '#00824D'`
- openpyxl: `PatternFill(start_color='00824D', fill_type='solid')`

### 2. SSB Blå (sekundær)
- Hex: `#1D9DE2`
- RGB: 29, 157, 226
- CSS: `--ssb-cat-2: #1D9DE2;`
- JS: `ssbBlue: '#1D9DE2'`
- Python: `ssb_blue = '#1D9DE2'`
- openpyxl: `PatternFill(start_color='1D9DE2', fill_type='solid')`

### 3. SSB Gull (tertiær)
- Hex: `#C78800`
- RGB: 199, 136, 0
- CSS: `--ssb-cat-3: #C78800;`
- JS: `ssbGold: '#C78800'`
- Python: `ssb_gold = '#C78800'`
- openpyxl: `PatternFill(start_color='C78800', fill_type='solid')`

### 4. SSB Rosa
- Hex: `#C775A7`
- RGB: 199, 117, 167
- CSS: `--ssb-cat-4: #C775A7;`
- JS: `ssbPink: '#C775A7'`
- Python: `ssb_pink = '#C775A7'`
- openpyxl: `PatternFill(start_color='C775A7', fill_type='solid')`

### 5. SSB Mørk Grønn
- Hex: `#075745`
- RGB: 7, 87, 69
- CSS: `--ssb-cat-5: #075745;`
- JS: `ssbDarkGreen: '#075745'`
- Python: `ssb_dark_green = '#075745'`
- openpyxl: `PatternFill(start_color='075745', fill_type='solid')`

### 6. SSB Mørk Blå
- Hex: `#0F2080`
- RGB: 15, 32, 128
- CSS: `--ssb-cat-6: #0F2080;`
- JS: `ssbDarkBlue: '#0F2080'`
- Python: `ssb_dark_blue = '#0F2080'`
- openpyxl: `PatternFill(start_color='0F2080', fill_type='solid')`

### 7. SSB Mørk Rosa
- Hex: `#A3136C`
- RGB: 163, 19, 108
- CSS: `--ssb-cat-7: #A3136C;`
- JS: `ssbDarkPink: '#A3136C'`
- Python: `ssb_dark_pink = '#A3136C'`
- openpyxl: `PatternFill(start_color='A3136C', fill_type='solid')`

### 8. SSB Mørk Brun
- Hex: `#471F00`
- RGB: 71, 31, 0
- CSS: `--ssb-cat-8: #471F00;`
- JS: `ssbDarkBrown: '#471F00'`
- Python: `ssb_dark_brown = '#471F00'`
- openpyxl: `PatternFill(start_color='471F00', fill_type='solid')`

### 9. SSB Grå ("Annet")
- Hex: `#909090`
- RGB: 144, 144, 144
- CSS: `--ssb-cat-9: #909090;`
- JS: `ssbGray: '#909090'`
- Python: `ssb_gray = '#909090'`
- openpyxl: `PatternFill(start_color='909090', fill_type='solid')`

---

## Palett som arrays/lister

**Gjelder begge rendringsmål** (CSS-variant kun der verten tillater egne custom properties — i widget er hardkodet hex fra JS-arrayet det trygge valget).

### JavaScript / TypeScript
```js
const SSB_CATEGORICAL = [
  '#00824D', '#1D9DE2', '#C78800', '#C775A7',
  '#075745', '#0F2080', '#A3136C', '#471F00', '#909090'
];
```

### Python
```python
SSB_CATEGORICAL = [
    '#00824D', '#1D9DE2', '#C78800', '#C775A7',
    '#075745', '#0F2080', '#A3136C', '#471F00', '#909090'
]
```

### CSS Custom Properties
```css
:root {
  --ssb-cat-1: #00824D;
  --ssb-cat-2: #1D9DE2;
  --ssb-cat-3: #C78800;
  --ssb-cat-4: #C775A7;
  --ssb-cat-5: #075745;
  --ssb-cat-6: #0F2080;
  --ssb-cat-7: #A3136C;
  --ssb-cat-8: #471F00;
  --ssb-cat-9: #909090;
}
```

---

## Sekvensielt (grønn rampe)

**Som data-blekk (choropleth-flater, heatmap-celler): begge rendringsmål** — rampen koder da en verdi og styres av skillen på samme måte som en seriefarge. **Som chrome (kort-bakgrunner, seksjonstoning): kun frittstående leveranse**, jf. SKILL.md → «Rendringsmål». Sjekk begge ender mot den faktiske bakgrunnen: trinn 1 (`#ECFEED`) er nær hvit og forsvinner mot lys bakgrunn (start eventuelt på trinn 2), mens trinn 5 (`#075745`) har under 2,2:1 mot mørk bakgrunn — i mørk modus, la rampen slutte på trinn 4.

5-trinns gradient for heatmaps, choropleths og intensitetsskalaer. Jevne lyshetstrinn (ca. 0,15 i OKLab, avstand 13–15 mellom nabotrinn også for fargeblinde). Trinn 2 og 3 er interpolert i OKLab mellom SSB Grønn 1 og SSB Grønn 4.

| Trinn | Hex | RGB |
|---|---|---|
| 1 (lysest) | `#ECFEED` | 236, 254, 237 |
| 2 | `#A9D4B5` | 169, 212, 181 |
| 3 (midt) | `#66AB80` | 102, 171, 128 |
| 4 | `#00824D` | 0, 130, 77 |
| 5 (mørkest) | `#075745` | 7, 87, 69 |

### Python matplotlib colormap
```python
from matplotlib.colors import LinearSegmentedColormap

ssb_sequential = LinearSegmentedColormap.from_list('ssb_green', [
    '#ECFEED', '#A9D4B5', '#66AB80', '#00824D', '#075745'
])
```

### JavaScript array
```js
const SSB_SEQUENTIAL = ['#ECFEED', '#A9D4B5', '#66AB80', '#00824D', '#075745'];
```

---

## Divergerende (negativ–nøytral–positiv)

**Samme regel som den sekvensielle rampen:** data-blekk i begge rendringsmål, chrome kun frittstående. Nøytralpolen `#F0F8F9` er en lys bakgrunnsfarge og forsvinner mot lys vert-bakgrunn — i widget bør nøytral heller være vertens bakgrunnsfarge eller en transparent celle, slik at bare polene er SSB-farger. Mot mørk bakgrunn er det motsatt: de mørke ytterpolene (`#0F2080`, `#471F00`) har bare 1,1–1,4:1, så de sterkeste avvikene blir minst synlige. I mørk modus, bruk bare de tre midterste trinnene.

For avvik fra gjennomsnitt, referanseverdier eller null. Blå under, oker over referansen. Polene har lik lyshet per trinn, slik at ingen side ser sterkere ut, og ingen av dem leses som «bra» eller «dårlig» slik grønn og rosa gjør. Når retningen faktisk er god eller dårlig, bruk de semantiske fargene med ▲/▼ (SKILL.md → «Semantiske farger»).

| Trinn | Navn | Hex | RGB |
|---|---|---|---|
| Sterkt under | SSB Mørk Blå | `#0F2080` | 15, 32, 128 |
| Under | SSB Blå | `#1D9DE2` | 29, 157, 226 |
| Nøytral | SSB Mørk 1 | `#F0F8F9` | 240, 248, 249 |
| Over | SSB Gull | `#C78800` | 199, 136, 0 |
| Sterkt over | SSB Mørk Brun | `#471F00` | 71, 31, 0 |

### Python matplotlib colormap
```python
from matplotlib.colors import LinearSegmentedColormap

ssb_diverging = LinearSegmentedColormap.from_list('ssb_diverging', [
    '#0F2080', '#1D9DE2', '#F0F8F9', '#C78800', '#471F00'
])
```

---

## Recharts tema-objekt

Objektet er delt i to slik at widget-bruk kan plukke bare den delen som skillen styrer i begge rendringsmål.

```jsx
// Data-blekk — gjelder BEGGE rendringsmål
const SSB_SERIES = [
  '#00824D', '#1D9DE2', '#C78800', '#C775A7',
  '#075745', '#0F2080', '#A3136C', '#471F00', '#909090',
];

// Chrome — KUN frittstående leveranse (lys modus innebygd)
const SSB_CHROME = {
  page: '#F0F8F9',        // dashbordflate; hvert diagram på hvitt kort
  background: '#FFFFFF',
  text: '#274247',
  grid: '#D9DFE0',
  zeroLine: '#899597',
  tooltip: {
    background: '#FFFFFF',
    border: '#899597',
    text: '#274247',
    borderRadius: 4,
  },
  fonts: {
    title: "'Open Sans', Arial, sans-serif",
    body: "'Open Sans', Arial, sans-serif",
  },
};

// Frittstående leveranse: bruk hele temaet
const SSB_THEME = { colors: SSB_SERIES, ...SSB_CHROME };
```

**I inline chat-widget:** bruk `SSB_SERIES` alene og la `SSB_CHROME` ligge. Verten styler container, tekst og bakgrunn selv, og arver mørk modus automatisk. Der en komponent krever en eksplisitt farge, les vertens token i stedet:

```js
const css = getComputedStyle(document.documentElement);
const textColor = css.getPropertyValue('--text-muted').trim();
const gridColor = css.getPropertyValue('--border').trim();
```

Tokennavnene varierer med verten — sjekk hvilke som faktisk finnes før du bruker dem, og ha en nøytral fallback (f.eks. `|| 'currentColor'`) i stedet for å falle tilbake på SSB-hex.

---

## Chart.js konfigurasjon

Felles styling — diagram-type-spesifikke felter (særlig `beginAtZero` på y-aksen) settes per diagram.

**Gjelder frittstående leveranse.** Alt utenom `backgroundColor`-arrayet er chrome med innebygd lys modus. Chart.js tegner på canvas og arver ingenting fra vertens CSS, så i widget må chrome settes eksplisitt fra vertens tokens — se widget-varianten under konfigurasjonen.

```js
// Tekstfarge og fontrekkefølge må settes globalt: på rotnivå i options når de ikke akser,
// legend og kildelinje i Chart.js 4.4.1. Open Sans brukes hvis den er installert, ellers Arial
// — fontene lastes ikke fra nett.
Chart.defaults.color = '#274247';
Chart.defaults.font.family = "'Open Sans', Arial, sans-serif";

const SSB_CHARTJS_DEFAULTS = {
  backgroundColor: [
    '#00824D', '#1D9DE2', '#C78800', '#C775A7',
    '#075745', '#0F2080', '#A3136C', '#471F00', '#909090'
  ],
  borderColor: '#899597',
  plugins: {
    title: { align: 'start', font: { family: "'Open Sans', Arial, sans-serif", size: 20, weight: 'bold' } },
    tooltip: {
      backgroundColor: '#FFFFFF', borderColor: '#899597', borderWidth: 1,
      titleColor: '#274247', bodyColor: '#274247',  // standard er hvit tekst — usynlig på hvit flate
      titleFont: { size: 14 }, bodyFont: { size: 12 },
    },
    legend: { labels: { font: { size: 12 } } },  // posisjon settes per diagram (se under)
  },
  scales: {
    // Heltrukket rutenett, nullinje og akselinje i #899597. Stiplet er forbeholdt prognoser og brudd.
    x: { grid: { color: '#D9DFE0' }, border: { color: '#899597' }, ticks: { color: '#274247' } },
    y: {
      grid: { color: (ctx) => (ctx.tick?.value === 0 ? '#899597' : '#D9DFE0') },
      border: { color: '#899597' },
      ticks: { color: '#274247' },
    },
    // beginAtZero settes per chart-type — se under
  },
};
```

**Per diagram-type:**

- **Søyle- og arealdiagram:** `scales.y.beginAtZero = true` (alltid — SSB-prinsipp 2). Søyler: `scales.x.grid.display = false` (ingen støttelinjer langs kategoriaksen), og `categoryPercentage: 0.67, barPercentage: 1` gir luft på halve søylebredden.
- **Linjediagram:** `scales.y.beginAtZero = true` som utgangspunkt. `false` er greit når endringen er budskapet og startverdien står synlig på aksen; for indekser (f.eks. KPI med basis 100), marker basisår tydelig med annotasjon. Loddrette støttelinjer (`scales.x.grid`) beholdes.
- **Legend-posisjon:** `top` eller `right` — aldri `bottom`. Under diagrammet kolliderer legend med kildelinjen og blir lest som en del av den (SKILL.md → «Tekst og merking»). Foretrekk uansett direkte merking av seriene, og bruk legend først når direkte merking gir overlapp.
- **Kildelinje (frittstående leveranse):** bruk `plugins.subtitle` med `position: 'bottom'` og `color: '#274247'` (lever i canvas, følger med ved PNG-eksport). Se `format-guidelines.md` → «Vanilla JS + Chart.js v4». **I widget:** `display: false` — tittel og kilde skrives i chat-svarteksten.

**Widget-variant:** behold `backgroundColor`-arrayet uendret og overstyr chrome med vertens tokens:

```js
const css = getComputedStyle(document.documentElement);
const text = css.getPropertyValue('--text-muted').trim() || 'currentColor';
const grid = css.getPropertyValue('--border').trim() || 'rgba(128,128,128,.25)';

// Global tekstfarge og font fra verten, ikke SSB-verdiene over:
Chart.defaults.color = text;
Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;

const widgetOptions = {
  ...SSB_CHARTJS_DEFAULTS,
  borderColor: grid,
  plugins: {
    title: { display: false },     // tittel hører til chat-teksten
    subtitle: { display: false },  // kildelinjen hører til chat-teksten
    legend: { position: 'top', labels: { color: text } },
    tooltip: {},                   // vertens default, ikke SSB-hvit med #274247-tekst
  },
  scales: {
    x: { grid: { color: grid }, ticks: { color: text } },
    y: { grid: { color: grid }, ticks: { color: text } },
  },
};
```

`beginAtZero`, `spanGaps: false` og desimalhåndtering settes likt i begge rendringsmål — statistisk integritet er ikke rendringsmål-avhengig.

---

## Python matplotlib theme

**Gjelder kun frittstående leveranse.** Temaet brenner hvit bakgrunn og `#274247`-tekst inn i en bildefil (PNG/PDF) som ikke kan følge vertens mørk modus. Matplotlib er derfor ikke et widget-format — trenger du et diagram i chat-svaret, bruk et DOM-/canvas-bibliotek med vertens tokens i stedet.

```python
def apply_ssb_theme():
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Open Sans', 'Arial', 'Helvetica', 'DejaVu Sans'],  # DejaVu følger med matplotlib
        'axes.titleweight': 'bold',
        'axes.titlesize': 20,
        'axes.titlelocation': 'left',
        'axes.titlepad': 28,              # plass til benevningen over y-aksen
        'axes.labelsize': 14,
        'axes.labelcolor': '#274247',
        'axes.edgecolor': '#899597',
        'axes.facecolor': '#FFFFFF',
        'axes.grid': True,                # kake og kart: ax.grid(False)
        'axes.prop_cycle': plt.cycler(color=[
            '#00824D', '#1D9DE2', '#C78800', '#C775A7',
            '#075745', '#0F2080', '#A3136C', '#471F00', '#909090'
        ]),
        'grid.color': '#D9DFE0',
        'grid.linewidth': 0.8,
        'grid.linestyle': '-',            # stiplet er forbeholdt prognoser og brudd
        'xtick.color': '#274247',
        'ytick.color': '#274247',
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'figure.facecolor': '#FFFFFF',
        'text.color': '#274247',
        'legend.fontsize': 12,
        'legend.frameon': False,
    })
```
