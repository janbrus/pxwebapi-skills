# Stilregler per output-format

SSB-tilpassede regler for hvert leveranseformat.

**Innhold**

1. Tallformat — språk-bundet: `1 234,5` (no) / `1,234.5` (en), `Intl.NumberFormat` i JS, `format_number` i Python
2. React / HTML: widget-avvik, dashbord-layout, tooltip, hover, fonter, kilde-footer
3. Vanilla JS + Chart.js v4: komplett linjediagram med tittel, benevning over y-aksen, nullinje, tooltip og kildelinje; status som hull
4. PowerPoint (.pptx): slide-layout, diagrammer, tekst
5. Excel (.xlsx): header, datarader, tallformat, betinget formatering, kildeinfo
6. Python / Matplotlib: tema, kildelinje, benevning, figur, akser
7. Markdown-tabeller: formatering, lange tabeller, kilde

**Avklar rendringsmål før du bruker denne filen.** Seksjonene under er organisert etter *teknologi*, ikke etter rendringsmål, og kodeeksemplene er som utgangspunkt skrevet for **frittstående leveranse** (se SKILL.md → «Rendringsmål»): de hardkoder SSB-chrome som `#274247`-tekst, `#D9DFE0`-rutenett, Open Sans-titler og kildelinje inne i selve diagrammet. Kopieres de rått inn i en **inline chat-widget**, overstyrer de vertens designsystem og bryter mørk modus.

| Seksjon                  | Gjelder                                                        |
| ------------------------ | -------------------------------------------------------------- |
| Tallformat               | Begge rendringsmål                                              |
| React / HTML             | Begge — widget krever avvikene som er listet i seksjonen        |
| Vanilla JS + Chart.js v4 | Begge — widget krever avvikene som er listet i seksjonen        |
| PowerPoint               | Kun frittstående leveranse                                      |
| Excel                    | Kun frittstående leveranse                                      |
| Python / Matplotlib      | Kun frittstående leveranse                                      |
| Markdown-tabeller        | Begge — og eneste tillatte tabellform i widget                  |

Uavhengig av rendringsmål: fast seriefarge per kategori med kontrast ≥3:1 (SSB-paletten som standard), `beginAtZero` på søyler og areal, manglende verdier som hull (og flaggede tall som merkede punkter) og desimaler fra data er alltid påkrevd.

---

## Tallformat — språk-bundet

**Gjelder begge rendringsmål.**

Tallformat følger språkvalget (samme regel som i `ssb-pxwebapi-v2`):

- Norsk (`lang=no`): mellomrom som tusenskilletegn, komma som desimaltegn → `1 234,5`
- Engelsk (`lang=en`): komma som tusenskilletegn, punktum som desimaltegn → `1,234.5`

API-et returnerer alltid desimal-punktum uavhengig av språk — formater om ved presentasjon. I JS: `Intl.NumberFormat('nb-NO')` / `Intl.NumberFormat('en-GB')`. I Python:

```python
from decimal import Decimal, ROUND_HALF_UP

def format_number(value, decimals, lang='no'):
    # Vanlig avrunding (halvveis bort fra null), som Intl.NumberFormat i Chart.js: 2,5 → 3.
    # f'{value:.0f}' alene runder halvveis til partall (2,5 → 2). str() gir samme siffer som JS.
    q = Decimal(str(value)).quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    s = f'{q:,.{decimals}f}'  # '1,234.5'
    if lang == 'en':
        return s
    # Som Intl.NumberFormat('nb-NO'): hardt mellomrom, desimalkomma og ekte minustegn
    return s.replace(',', '\u00a0').replace('.', ',').replace('-', '\u2212')  # '1 234,5'
```

`decimals` kommer fra dataene (se `jsonstat-to-chart.md`), aldri hardkodet.

---

## React / HTML (Recharts, D3.js, Chart.js)

**Gjelder begge rendringsmål, men reglene under er skrevet for frittstående leveranse.** I en inline chat-widget gjelder disse avvikene (se SKILL.md → «Rendringsmål»):

- **Tooltip, hover og layout** — følg vertens tokens og konvensjoner. Den hvite tooltipen og dashbordflaten under er lys-modus-farger og bryter mørk modus.
- **Fonter** — bruk vertens typografi, ikke SSB-fontrekkefølgen.
- **Kilde-footer** — `<p>`-elementet under skal ikke rendres inne i widgeten; kildelinjen hører hjemme i chat-svarteksten. Selve strengbyggingen (språkvalget) er fortsatt riktig og gjenbrukes der.
- **Seriefarger** — uendret: hardkodet som hex (SSB-paletten som standard).

**Layout:**
- Dashboard: Scorecard-kort øverst, detaljdiagrammer i 2–3 kolonne grid under
- Dashbordflate `#F0F8F9` (SSB Mørk 1); hvert diagram på hvitt kort uten skygge, 24px mellom kortene
- Diagrammer skalerer med container, minimum 300px bredde
- Responsive breakpoints: 1 kolonne under 768px, 2–3 over

**Tooltip** (som på ssb.no):
- Bakgrunn: `#FFFFFF`
- Ramme: 1px `#899597`
- Tekst: `#274247`
- Border-radius: 4px
- Padding: 8px 12px

**Hover:**
- 70% opacity på ikke-hovrede elementer
- Smooth transition: 150ms

**Fonter:**
- Fontrekkefølgen `'Open Sans', Arial, sans-serif` (tabell-header: `'Roboto Condensed', Arial, sans-serif`), uten nedlasting. Er Open Sans installert hos brukeren, brukes den, ellers Arial. Det gir ingen nettkall og ingen venting

**Kilde-footer:**
```jsx
// Velg språk basert på `lang`-parameteren som ble brukt mot API-et
// (se ssb-pxwebapi-v2-skillens språk-seksjon).
const sourceLine = lang === 'en'
  ? `Source: Statistics Norway, table ${tableId}. Last updated: ${updated}.`
  : `Kilde: SSB, tabell ${tableId}. Sist oppdatert: ${updated}.`;
<p style={{ fontSize: '11px', color: '#274247', marginTop: '8px' }}>{sourceLine}</p>
```

---

## Vanilla JS + Chart.js v4

For apper uten React/Vue/build-step. Forutsetter at `formatNumber(value, decimals)` og en JSON-stat2-til-datasets-funksjon er tilgjengelig (se `jsonstat-to-chart.md` for sistnevnte).

**Gjelder begge rendringsmål, men konfigurasjonen under er skrevet for frittstående leveranse.** Chart.js tegner på canvas og kan ikke lese CSS-variabler selv. I en inline chat-widget må du derfor hente vertens tokens eksplisitt i JS — f.eks. `getComputedStyle(document.documentElement).getPropertyValue('--text-muted')` — og sette dem inn der eksempelet hardkoder `#274247` / `#D9DFE0` / `#899597`. Dette er grunnen til at hardkodet hex er riktig for *seriefarger* også i widget, men feil for chrome. Avvik i widget:

- `plugins.title` og `plugins.subtitle` (kildelinjen): sett `display: false`. Tittel og kilde skrives i chat-svarteksten, ikke inn i canvas.
- `scales.*.ticks.color`, `scales.*.grid.color` og `scales.*.border.color`: vertens tokens, ikke SSB-hex. `plugins.unitLabel.color`: vertens teksttoken — benevningen vises også i widget.
- `plugins.tooltip`: fjern fargene, slik at vertens default gjelder.
- `Chart.defaults.font.family`: vertens font, f.eks. `getComputedStyle(document.body).fontFamily`, ikke Open Sans.
- `datasets[].borderColor` / `backgroundColor`: uendret seriefarge-hex (SSB-paletten som standard).
- `beginAtZero`, `spanGaps: false` og desimalhåndtering: uendret. Statistisk integritet er ikke rendringsmål-avhengig.

Last Chart.js med låst versjon. Snutten er testet med 4.4.1, og benevningsboksen bruker et udokumentert grensesnitt som kan endre seg mellom versjoner:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
```

```js
// Fontrekkefølge for all tekst i diagrammet: Open Sans hvis den er installert, ellers Arial.
// Må settes globalt — font i options på rotnivå når ikke akser, legend og kildelinje i Chart.js 4.4.1.
Chart.defaults.font.family = "'Open Sans', Arial, sans-serif";

// Tittel + kildelinje bygget fra JSON-stat2-responsen
const chartTitle = cleanContents(data.extension?.px?.contents);  // strip "<id>:" + trailing ","
const sourceLine = lang === 'en'
  ? `Source: Statistics Norway, table ${tableId}. Last updated: ${updated}.`
  : `Kilde: SSB, tabell ${tableId}. Sist oppdatert: ${updated}.`;

// Datasets med per-serie decimals og unit (se jsonstat-to-chart.md, steg 6)
const yAxisDecimals = datasets.reduce((m, d) => Math.max(m, d.decimals || 0), 0);

// Benevning fra dataene (category.unit[kode].base), aldri hardkodet: 'prosent' → 'Prosent'.
// Egne beregninger har verken base eller decimals: sett d.unit og d.decimals selv, ut fra hva
// tallet er (jsonstat-to-chart.md steg 6).
// Ulike enheter hører ikke på samme y-akse — da vises ingen benevning: lag ett diagram per enhet.
const units = [...new Set(datasets.map((d) => d.unit).filter(Boolean))];
if (units.length > 1) console.warn('Seriene har ulike enheter, lag ett diagram per enhet:', units);
const unit = units.length === 1 ? units[0].charAt(0).toUpperCase() + units[0].slice(1) : '';

// Benevning vannrett over y-aksen, i en egen layout-boks rett over plottet.
// Lav weight = nærmest plottområdet (legend har 1000, tittel 2000).
// Layout-boksen er et udokumentert grensesnitt, testet med Chart.js 4.4.1 —
// se reserven nederst, som tegner diagrammet uten benevning hvis boksen feiler.
const unitLabel = {
  id: 'unitLabel',
  beforeInit(chart, _args, opts) {
    Chart.layouts.addBox(chart, {
      position: 'top', weight: 0, fullSize: true,
      options: {},  // påkrevd: Chart.js leser options.stack fra hver layout-boks
      isHorizontal: () => true,
      update(maxWidth) { this.width = maxWidth; this.height = 24; },
      draw() {
        const { ctx } = chart;
        const y = chart.scales.y;
        if (!y || !opts.text) return;  // ingen y-akse (kake/ring) eller ingen benevning
        ctx.save();
        ctx.font = "14px 'Open Sans', Arial, sans-serif";
        ctx.fillStyle = opts.color || '#274247';
        ctx.textBaseline = 'bottom';
        ctx.fillText(opts.text, y.left, this.bottom - 6);
        ctx.restore();
      },
    });
  },
};

const config = {
  type: 'line',
  data: { labels, datasets },
  plugins: [unitLabel],
  options: {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      title: {
        display: true, text: chartTitle, position: 'top', align: 'start',  // venstrestilt
        color: '#274247', font: { family: "'Open Sans', Arial, sans-serif", size: 20, weight: 'bold' },
      },
      subtitle: {  // mandatorisk kildelinje (frittstående) — lever i canvas så den følger med ved
                   // PNG-eksport. I widget: display: false, kildelinjen i chat-teksten i stedet.
        display: true, text: sourceLine, position: 'bottom',
        color: '#274247', font: { size: 11 },
      },
      unitLabel: { text: unit },
      legend: { position: 'top', labels: { color: '#274247' } },
      tooltip: {
        // Hvit flate, tynn grå ramme, mørk tekst (som på ssb.no). Standard er hvit tekst — sett den.
        backgroundColor: '#FFFFFF', borderColor: '#899597', borderWidth: 1,
        titleColor: '#274247', bodyColor: '#274247',
        callbacks: {
          // ctx.dataset.decimals settes per serie i datasets-byggeren — IKKE hardkod
          label: (ctx) => `${ctx.dataset.label}: ${formatNumber(ctx.parsed.y, ctx.dataset.decimals ?? 0)}`,
        },
      },
    },
    scales: {
      // Heltrukket rutenett; loddrette støttelinjer i linjediagram (søylediagram: x.grid.display = false).
      x: { grid: { color: '#D9DFE0' }, border: { color: '#899597' }, ticks: { color: '#274247' } },
      y: {
        // Søyle- og arealdiagram: { beginAtZero: true } uten unntak.
        // Linjediagram: true som utgangspunkt; false er greit når endringen er budskapet
        // og startverdien står synlig på aksen (indekser: annoter basisåret).
        beginAtZero: false,
        grid: { color: (ctx) => (ctx.tick?.value === 0 ? '#899597' : '#D9DFE0') },  // nullinje
        border: { color: '#899597' },
        ticks: { color: '#274247', callback: (v) => formatNumber(v, yAxisDecimals) },
      },
    },
  },
};

// Reserve: feiler benevningsboksen (f.eks. i en annen Chart.js-versjon), skjer det inne i
// new Chart() og gir et tomt lerret. Tegn da diagrammet uten benevning i stedet.
// Fjern bare unitLabel — andre plugins (f.eks. direkte merking av seriene) skal bli.
let chart;
try {
  chart = new Chart(canvas, config);
} catch (err) {
  console.warn('Benevningen over y-aksen feilet; diagrammet tegnes uten:', err);
  Chart.getChart(canvas)?.destroy();
  chart = new Chart(canvas, { ...config, plugins: config.plugins.filter((p) => p !== unitLabel) });
}
```

**Status-koder som hull:** `spanGaps: false` på hver dataset slik at `null`-verdier (fra status-koder, se `jsonstat-to-chart.md`) faktisk vises som hull, ikke som rette linjer mellom kjente punkter. En status på et tall (f.eks. `*` = foreløpig) er et flagg, ikke et hull — se `jsonstat-to-chart.md` Steg 5.

**Embedded i en eksisterende app:** Hvis appen allerede har sin egen typografi (header, knapper), behold appens fonter i diagrammet i stedet for å overstyre med Open Sans. Kildelinjen og beginAtZero-reglene er fortsatt obligatoriske; fonter og farger er fleksible, men kontrastkravene gjelder også for appens farger. Dropp `Chart.defaults`-linjene (font og farge): de gjelder alle Chart.js-diagrammer på siden, også appens egne. Sett i stedet appens font og farge på hvert element — `plugins.title.font`, `plugins.subtitle.font`, `plugins.legend.labels.font`, `plugins.tooltip.titleFont`/`bodyFont`/`footerFont`, `scales.*.ticks.font` og fontstrengen i `unitLabel`. Uten `footerFont` tegner tooltipen fortsatt med Chart.js' standardfont.

---

## PowerPoint (.pptx)

**Gjelder kun frittstående leveranse.**

**Slide-layout:**
- Tittel: 20pt Open Sans Bold, `#274247`, øverst til venstre
- Diagram fyller ~70% av slide-høyde
- Kilde: bottom-left, 10pt, `#274247`
- Bakgrunn: hvit (#FFFFFF)

**Diagrammer:**
- Solid fills — ingen gradienter i søyler
- Bruk SSB kategorisk palett i rekkefølge
- Fjern unødvendige rutenett og rammer
- Direkte merking fremfor legend der mulig

**Tekst:**
- Maksimalt 3 bullet points per slide
- Bruk tall fra diagrammet i teksten for å forsterke budskapet

---

## Excel (.xlsx)

**Gjelder kun frittstående leveranse.**

**Generelt:**
- Fjern default Excel rutenett og rammer
- Fryse øverste rad (header)

**Header-rad:**
- Bakgrunn: `#274247`
- Tekst: hvit (#FFFFFF), bold
- Font: Calibri 11pt (Excel-standard, nært Open Sans)

**Datarad:**
- Annenhver rad: `#ECFEED` bakgrunn
- Tekst: `#162327`
- Font: Calibri 11pt

**Tallformat:**
- Norsk standard: mellomrom som tusenskilletegn, komma som desimaltegn
- Format-streng: `#\u00A0##0` (non-breaking space)
- Prosent: `0,0 %`
- Indeks: `0,0`

**Betinget formatering:**
- Heatmaps: sekvensielt grønt (#ECFEED → #075745, se `color-system.md`)
- Positiv/negativ: `#00824D` med ▲ / `#A3136C` med ▼
- Databars: `#00824D`

**Kildeinfo:**
- Plasser i rad under dataene, slått sammen
- Font: 9pt, vanlig skrift (ikke kursiv), `#274247`
- Tekst (følg `lang`-valget fra API-kallet):
  - Norsk: `Kilde: SSB, tabell {id}. Sist oppdatert: {dato}.`
  - English: `Source: Statistics Norway, table {id}. Last updated: {date}.`

---

## Python / Matplotlib

**Gjelder kun frittstående leveranse.** Matplotlib produserer bildefiler (PNG/PDF) med innbrent lys-modus-bakgrunn, og egner seg derfor ikke til inline widget-rendring.

**Tema:**
```python
apply_ssb_theme()  # Se color-system.md for implementasjon
```

**Kilde** (velg språk basert på `lang`-parameteren som ble brukt mot API-et):
```python
if lang == 'en':
    source_line = f'Source: Statistics Norway, table {table_id}. Last updated: {updated}.'
else:
    source_line = f'Kilde: SSB, tabell {table_id}. Sist oppdatert: {updated}.'
fig.text(0.01, 0.01, source_line, fontsize=11, color='#274247')  # vanlig skrift, ikke kursiv
```

**Benevning** vannrett over y-aksen, ikke rotert (temaet gir tittelen `titlepad` til dette):
```python
# Benevning fra dataene (category.unit[kode].base, se jsonstat-to-chart.md steg 6), aldri hardkodet.
# data = JSON-stat2-responsen, codes = ContentsCode-ene som er tegnet.
# Egne beregninger har verken base eller decimals: sett unit og decimals selv, ut fra hva tallet er,
# i stedet for linjene under.
metric = data['role']['metric'][0]
units = {data['dimension'][metric]['category']['unit'][c]['base'] for c in codes}
unit = next(iter(units)) if len(units) == 1 else ''  # ulike enheter: ett diagram per enhet
unit = unit[:1].upper() + unit[1:]                   # 'mill. kr' → 'Mill. kr', 'NOK million' uendret
ax.text(0, 1.02, unit, transform=ax.transAxes, ha='left', va='bottom',
        fontsize=14, color='#274247')
```

**Figur:**
- `figsize=(10, 6)` som standard
- `tight_layout(rect=(0, 0.04, 1, 1))` alltid — `rect` holder av plass nederst til kildelinjen, som `tight_layout()` ellers legger oppå aksetallene
- `dpi=150` for skjerm, `dpi=300` for print
- Sett `plt.rcParams['font.sans-serif']` for Open Sans med Arial som fallback, og `DejaVu Sans` sist — den følger med matplotlib, så det blir ingen fontadvarsler der verken Open Sans eller Arial er installert

**Akser:**
- Fjern topp- og høyre-spines: `ax.spines['top'].set_visible(False)`
- Rutenett: heltrukket `#D9DFE0`, linewidth 0.8 (stiplet er forbeholdt prognoser og brudd)
- Akselinjer og nullinje: `#899597`, linewidth 0.8 — `ax.axhline(0, color='#899597', linewidth=0.8)` når aksen krysser 0
- Tallene på aksen etter `lang`: `ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: format_number(v, decimals, lang)))` (`format_number` under «Tallformat», `FuncFormatter` fra `matplotlib.ticker`)

---

## Markdown-tabeller

**Gjelder begge rendringsmål — og er den eneste tillatte tabellformen i inline chat-widget.** Den stilsatte SSB-tabellen (SKILL.md → «Tabellformatering») gjelder kun frittstående leveranse; i widget-kontekst skrives tabellen som vanlig markdown i chat-svaret, ikke som HTML inne i widgeten.

**Formatering:**
- Høyrejuster tall-kolonner med `---:` i header-separator
- Bruk tusenskilletegn (mellomrom): `5 609 000`
- Desimaltall med komma: `3,2 %`
- Bruk forkortelser for store tall: `720 k`, `1,2 mill.`, `3,4 mrd.`

**Lange tabeller (>20 rader):**
- Vis topp 10 og bunn 10 med `...` mellom
- Inkluder total/gjennomsnitt som siste rad
- Eller: vis kun topp/bunn med note om fullstendige data

**Kilde** (velg språk basert på `lang`-parameteren som ble brukt mot API-et):
```markdown
*Kilde: SSB, tabell 07459. Sist oppdatert: 2026-02-25.*
*Source: Statistics Norway, table 07459. Last updated: 2026-02-25.*
```

**Eksempel:**
```markdown
| Fylke | Innbyggere | Endring |
|---|---:|---:|
| Oslo | 728 714 | +1,3 % |
| Viken | 1 278 432 | +0,8 % |
| ... | | |
| **Norge** | **5 609 000** | **+0,7 %** |

*Kilde: SSB, tabell 07459. Sist oppdatert: 2026-02-25.*
```
