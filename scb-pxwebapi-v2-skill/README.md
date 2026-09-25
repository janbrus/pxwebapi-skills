# Agent Skill: SCB PxWebApi v2 - BETA

En [Agent Skill](https://agentskills.io) — en `SKILL.md` med arbetsflöde och regler plus referensfiler. Den lär AI-verktyg som Claude och ChatGPT att söka, utforska och hämta data från SCB:s Statistikdatabas via PxWebApi v2. Formatet är en öppen standard som stöds av [Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude), [ChatGPT och Codex](https://developers.openai.com/codex/skills/) m.fl.

## Vad skillen gör

- Guidar AI-assistenten genom rätt arbetsflöde: sök → metadata → query → presentera
- Täcker alla endpoints i PxWebApi v2 (tabeller, metadata, kodlistor, sparade frågor, config)
- Hanterar kodlistor och aggregeringar
- Kräver att varje siffra är hämtad från API:et i samma konversation — aldrig ur minnet
- På svenska och engelska

## Filstruktur

```
scb-pxwebapi-v2/
├── SKILL.md                  # Huvudinstruktioner och arbetsflöde
├── README.md                 # Denna fil
├── CHANGELOG.md              # Ändringslogg — gällande version står i SKILL.md-frontmatter (metadata.version)
├── scb-pxwebapi-v2-skill.zip # Färdigpackad skill — ladda upp i Claude.ai, eller packa upp i .agents/skills/ för ChatGPT/Codex
└── references/
    ├── json-stat2.md         # json-stat2 formatspecifikation (Dataset, row-major, statuskoder, extension, noteMandatory — gäller även Eurostat, World Bank)
    ├── mcp-tools.md          # Mappning till @jarib/pxweb-mcp och verktygens begränsningar mot SCB
    └── search-syntax.md      # Lucene-baserad söksyntax för /tables?query=
```

`CLAUDE.md`, `scripts/` och `evals/` i repot är underhållarinterna och ingår inte i paketet.

## Installation

### Claude.ai

1. Ladda ner `scb-pxwebapi-v2-skill.zip`, eller bygg den själv från repot:

   ```bash
   scripts/build_zip.sh
   ```

   Paketet innehåller endast de användarvända filerna (`SKILL.md`, `README.md`, `CHANGELOG.md`, `references/`) plus `LICENSE` under toppmappen `scb-pxwebapi-v2/`.

2. Gå till **Settings > Features > Skills**
3. Ladda upp ZIP-filen

### Claude Code

Installerat namn är `scb-pxwebapi-v2`; mappen i repot heter `scb-pxwebapi-v2-skill`. Från repots rot:

```bash
cp -r scb-pxwebapi-v2-skill ~/.claude/skills/scb-pxwebapi-v2

# eller symlänka ett klonat repo, så håller git pull kopian aktuell
ln -s "$PWD/scb-pxwebapi-v2-skill" ~/.claude/skills/scb-pxwebapi-v2
```

### ChatGPT och Codex

ChatGPT och Codex läser skills i samma format från `.agents/skills/` (enligt [OpenAI:s dokumentation](https://developers.openai.com/codex/skills/); inte testat här). Packa upp ZIP-filen, eller kopiera mappen från repot:

```bash
cp -r scb-pxwebapi-v2-skill ~/.agents/skills/scb-pxwebapi-v2
```

Fristående skills finns i ChatGPT:s skrivbordsapp, Codex CLI och IDE-tillägget; på webb och mobil måste skillen paketeras som plugin.

## MCP-servrar

För att Claude eller ChatGPT faktiskt ska kunna *anropa* API:et behövs ett verktyg:

- **@jarib/pxweb-mcp** (https://www.npmjs.com/package/@jarib/pxweb-mcp) — open source, fungerar med PxWeb-installationer inklusive SCB. Måste startas med `--url https://statistikdatabasen.scb.se/api/v2` (standard är norska SSB) — se `references/mcp-tools.md`
- Egen MCP-server med FastMCP eller liknande
- Utan MCP räcker ett verktyg som kan göra HTTP GET och POST (t.ex. `curl` via Bash)

## Licens

Skillen (`SKILL.md`, `references/` och skripten) är licensierad under [MIT-licensen](https://github.com/janbrus/pxwebapi-skills/blob/main/LICENSE), © 2026 Jan Bruusgaard. Licenstexten ligger i repots rot och följer med i zip-filen som `LICENSE`. MIT gäller skillen, inte datat den hämtar — det har en egen licens, se nedan.

SCB:s statistik publiceras under Creative Commons CC0 1.0 (licens-URL:en finns i `GET /config`, fältet `license`). Skillen behåller ändå källhänvisning som god praxis.
