# Endringslogg — ssb-histstat

Gjeldende versjon står i `SKILL.md`-frontmatter under `metadata.version`.
Har din kopi ingen `metadata.version`, er den fra før 2026-08-30 — last ned ny.
Versjoner under 1.0.0 markerer at skillen ikke har noen publisert distribusjon ennå.

## 0.9.0 — 2026-08-30

- Tillegg 2026-09-09, ingen versjonsendring: **skillen har fått distribusjons-zip, `scripts/build_zip.sh` og en CI-workflow** (`.github/workflows/check-histstat-zip.yaml`). Den hadde ingen pakke i det hele tatt, og README-en ba brukeren zippe mappen selv — det ville lagt `CLAUDE.md` inn i pakken. `ssb-histstat-skill.zip` inneholder nå `SKILL.md`, `README.md`, `CHANGELOG.md` og `references/` under toppmappa `ssb-histstat/` (frontmatter-navnet), slik søskenskillene pakker. Filtreet i README manglet dessuten `CHANGELOG.md` og oppga mappenavnet feil
- Tillegg 2026-09-09, ingen versjonsendring: installasjonskommandoene i `README.md` brukte det installerte navnet `ssb-histstat` som kildemappe (mappen heter `ssb-histstat-skill`); nå riktig mappe pluss symlenke-alternativ
- **Versjonering innført** (`metadata.version` i `SKILL.md`-frontmatter + denne loggen). En bruker med en gammel kopi hadde tidligere ingen måte å se det på. `CLAUDE.md` sier nå at URL-rettelser teller som innholdsendringer og skal bumpe versjonen — en foreldet URL er den viktigste måten denne skillen forfaller på
- **Nytt kulepunkt under «Hva denne skillen IKKE gjør»:** gjengi aldri et historisk tall fra hukommelsen. Skillen returnerer kilde-URL-er og leser ikke PDF-ene, så et tall i et svar kan bare ha kommet fra hukommelsen — det er den ene feilmåten som ville satt et oppdiktet tall under en SSB-henvisning. Punktet er kortformen av «Dataintegritet — grunnregelen» i `ssb-pxwebapi-v2`; den skillen eier regelen, denne peker på den

  Bevisst **ingen egen integritetsliste** her. Skillen leverer ikke tall, den leverer lenker, så én setning dekker risikoen.
- Søskenskiller: `ssb-pxwebapi-v2` 1.4.1, `scb-pxwebapi-v2` 0.10.0, `ssb-chart-skill` 1.1, `generic-pxweb-v2-skill` 0.10.0 og `generic-pxweb-v1-skill` 0.9.0 ble sluppet samtidig, alle med den samme integritetsregelen i den formen som passer skillen
- Tillegg 2026-09-23, ingen versjonsendring: **README omskrevet til den åpne [Agent Skills](https://agentskills.io)-standarden.** ChatGPT og Codex leser nå skills i samme format, så «Claude Skill» er byttet til «Agent Skill», ingressen nevner både Claude og ChatGPT, og installasjonsavsnittet har fått en egen blokk for `.agents/skills/` (etter OpenAIs dokumentasjon <https://developers.openai.com/codex/skills/>, lest 2026-09-23 — ikke testet her). Kun README; `SKILL.md` er uendret, men zip-en er bygd på nytt fordi README ligger i den
- Tillegg 2026-09-24, ingen versjonsendring: **MIT-lisens.** Repoet har fått `LICENSE` (MIT, © 2026 Jan Bruusgaard) i roten, og `scripts/build_zip.sh` legger den i zip-en — MIT krever at lisensteksten følger med i kopier. README-ens lisensavsnitt skiller nå mellom skillen (MIT) og dataene den henter (byråets egen lisens). `CLAUDE.md` og CI-workflowens `paths:` er oppdatert. `SKILL.md`-frontmatter har fått `license: MIT. LICENSE has complete terms` (det valgfrie `license`-feltet i Agent Skills-spesifikasjonen); brødteksten er uendret
