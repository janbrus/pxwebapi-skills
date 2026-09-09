# Eval-scenarier — scb-pxwebapi-v2

Fyra scenarier som träffar exakt de avsnitt v0.11.0 kortade ner eller rättade, eftersom det är där besluten bor: obligatoriska noter (Dataintegritet/Steg 5), `role.geo`-rättelsen (Steg 3), kodlistor (Steg 3) och avslutade serier utan `discontinued`-flagga (Steg 2).

Körs via `skill-creator` vid större ändringar i `SKILL.md` eller `references/`. Underhållarinternt — ingår inte i distributions-zip eller README:s filträd.

**Facit beskriver form och val, aldrig ett konkret talvärde.** Ett scenario som asserterar en viss folkmängd belönar en siffra ur minnet framför en hämtad — tvärtemot skillens egen integritetsregel.

**Kör dem som faktiska körningar**, inte som genomläsning. En modell som *läser* SKILL.md svarar rätt på allt här; poängen är vad den gör när den har verktygen.

Endpoints, koder och svarsformer verifierade live 2026-09-07 och 2026-09-08. Fallerar ett scenario, kör `scripts/check_examples.py` först — tabellen kan ha ändrats, inte skillen.

---

## 1. «Hur många bor i Stockholm?» — aktualitet och obligatoriska noter

Det scenario som fällde v0.11.0:s första utkast: SKILL.md pekade på TAB638, som slutar
2024 med `discontinued: null`. Två oberoende körningar upptäckte det via `pastDays`.

- **Förväntad tabell:** TAB6471 (månad, 2025M01–). **Inte** TAB638 (fryst på 2024) och inte TAB5444 (fryst på 2024M12)
- **Sekvens:** (`GET /tables?query=folkmängden+per+månad` om okänd — 2 träffar, TAB6471 först) → `GET /tables/TAB6471/metadata` → `POST /tables/TAB6471/data`
- **Nyckelval:** `Region=0180`, `Alder=TotSA`, `ContentsCode=000007SF`, `Tid=top(1)`
- **Succé:**
  - Modellen kontrollerar `lastPeriod` och väljer inte en tabell vars senaste period ligger långt bak, även om `discontinued` inte är satt
  - `Alder` är med i selektionen. Den har `elimination: false` här (till skillnad från i TAB638) — utelämnas den blir svaret `400 "Missing selection for mandantory variable"`
  - Ett tal med period och «Källa: SCB, tabell TAB6471»; `Kon` anges som utelämnad dimension
  - **Svaret återger de obligatoriska noterna.** TAB6471 har `noteMandatory: {"0": true, "1": true, "2": true, "3": true}` — fyra stycken, varav den första är CKM-bruset
  - Summerar modellen något själv, säger den att CKM gör totalen osäkrare än delarna
  - Svenskt talformat (mellanslag som tusentalsavgränsare)

## 2. «KPI senaste året» — avslutad serie utan flagga

- **Förväntad tabell:** TAB6596 (2020=100), **inte** TAB5737 (1980=100, uppdateras ej efter 2025M12)
- **Sekvens:** sök (`konsumentprisindex totalt` ger TAB6596 på plats 1) → metadata → data
- **Nyckelval:** `ContentsCode=00000808` (index) eller `00000804` (årsförändring), `Tid=top(13)`
- **Succé:**
  - Modellen väljer TAB6596. TAB5737 har `discontinued: null` — det enda som avslöjar att serien stannat är titeln («uppdateras ej efter 2025M12») och `lastPeriod`. Skillen ska få modellen att läsa `lastPeriod`, inte bara flaggan
  - Basperioden (2020=100) anges i svaret

## 3. «Befolkning per kommungrupp» — kodlista, och `Region` utan `role.geo`

- **Förväntad tabell:** TAB638 med `codelist[Region]=agg_RegionKommungrupp2023-`
- **Nyckelval:** kodlistans egna koder (`2023_A1`, `2023_A2`, `2023_B3` …) hämtade från `GET /codelists/agg_RegionKommungrupp2023-` — **inte** ordinarie kommunkoder, som ger `400 Non-existent value`. `valueCodes[Region]=*` fungerar också
- **Succé:**
  - Svaret anger vilken kodlista som använts — svaret registrerar det inte självt (Region-`extension` är bara `{elimination: false, show: code_value}`)
  - Modellen hittar geografin som `Region` i `id` trots att `role.geo` saknas, och frågar **inte** användaren om geografi
  - Ingen `outputValues`-parameter krävs; skulle den sättas ändrar den inget

## 4. «What is the population of Sweden?» (engelska)

- **Förväntad tabell:** TAB6471 med `lang=en` (eller TAB6473/TAB4365 — alla tre är aktuella och godtas; TAB638 gör det inte)
- **Sekvens:** `GET /tables?query=title:population AND title:month&lang=en` (13 träffar, TAB6471 på plats 3) → metadata → data
- **Nyckelval:** `Region=00` («Riket»/«Sweden»), `Alder=TotSA`, `ContentsCode=000007SF`, `Tid=top(1)`
- **Succé:** svar på engelska, engelskt talformat (komma som tusentalsavgränsare), «Source: Statistics Sweden, table {id}», och den valda tabellens `lastPeriod` ligger inom det senaste året. Facit är *formen*, inte värdet — ingen bestämd folkmängd ska stå här


---

## Körningar

**2026-09-08, mot v0.11.0.** Alla fyra körda som faktiska körningar av färska agenter som bara
hade `SKILL.md` + `references/` och `curl`.

| # | Utfall | Kommentar |
|---|---|---|
| 1 | **Fällde skillen** | Agenten vägrade TAB638 efter att ha sett `lastPeriod: 2024`, sökte med `pastDays` och hittade TAB6471. Fyndet är inarbetat i v0.11.0 — scenariot ovan är omskrivet efter det |
| 2 | Passerade | Valde TAB6596, inte TAB5737. Visade `..` som `..`, alla fyra obligatoriska noterna, och märkte inget som hämtat ur minnet |
| 3 | Passerade | Hittade `Region` i `id` utan `role.geo`, frågade inte användaren. Hämtade kodlistans egna koder från `/codelists/`. Angav kodlista och utelämnade dimensioner, och märkte sin egen summering |
| 4 | **Fällde skillen** | Samma TAB638-fynd som 1, oberoende. Valde TAB4365 + TAB6473 i stället |

Scenario 1 och 4 fann samma fel oberoende av varandra, vilket är det starkaste argumentet för
att köra evalen som körningar: `check_examples.py` gav grönt på TAB638 hela tiden, eftersom
tabellen svarar 200 och saknar `discontinued`. Sedan dess har kontrollskriptet en
aktualitetssjekk som hade fångat det.