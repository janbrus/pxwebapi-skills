#!/usr/bin/env bash
# Bygg generic-pxweb-v1-skill.zip — distribusjonspakken med toppmappe generic-pxweb-v1-skill/.
#
# Kun brukervendte filer pakkes: SKILL.md, README.md, CHANGELOG.md, references/
# og LICENSE. LICENSE (MIT) ligger i repo-roten og gjelder hele repoet; MIT krever
# at lisensteksten følger med i kopier, og zip-en er kopien som deles ut.
# CLAUDE.md, scripts/, evals/ og .github/ er repo-interne og holdes utenfor. Den
# håndbygde zip-en før v0.12.0 inneholdt CLAUDE.md og hadde ingen toppmappe;
# begge deler er rettet her, etter mønster fra ssb-pxwebapi-v2-skill.
#
# Toppmappa er frontmatter-navnet (`generic-pxweb-v1-skill`), ikke mappenavnet i
# repoet (`pxwebapi-v1-generic-skill`) — det er frontmatter-navnet som gjelder når
# pakken lastes opp til claude.ai.
#
# references/-lista er dynamisk (glob), slik at CI-synksjekken
# (.github/workflows/check-v1-zip.yaml) fanger en utdatert zip i stedet for at
# nye referansefiler stille faller utenfor.
#
# Bruk:  scripts/build_zip.sh [ut.zip]
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out="${1:-$root/generic-pxweb-v1-skill.zip}"
case "$out" in /*) ;; *) out="$PWD/$out" ;; esac

files=(README.md SKILL.md CHANGELOG.md)
for f in "$root"/references/*.md; do
  files+=("${f#"$root"/}")
done

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
for f in "${files[@]}"; do
  mkdir -p "$tmp/generic-pxweb-v1-skill/$(dirname "$f")"
  cp "$root/$f" "$tmp/generic-pxweb-v1-skill/$f"
done
cp "$root/../LICENSE" "$tmp/generic-pxweb-v1-skill/LICENSE"
files+=(LICENSE)

# Normaliser linjeslutt til LF. Filene kopieres fra disken, ikke fra git, og en
# fil lagret med CRLF (f.eks. fra en Windows-editor) ville ellers gi en zip som
# avviker fra CI-bygget — CI sjekker ut med LF (.gitattributes eol=lf).
find "$tmp" -type f \( -name '*.md' -o -name LICENSE \) -exec sed -i 's/\r$//' {} +

rm -f "$out"
(cd "$tmp" && zip -X -q -r "$out" generic-pxweb-v1-skill)
echo "Bygget $out (${#files[@]} filer)"
