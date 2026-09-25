#!/usr/bin/env bash
# Bygg ssb-histstat-skill.zip — distribusjonspakken med toppmappe ssb-histstat/.
#
# Kun brukervendte filer pakkes: SKILL.md, README.md, CHANGELOG.md, references/
# og LICENSE. LICENSE (MIT) ligger i repo-roten og gjelder hele repoet; MIT krever
# at lisensteksten følger med i kopier, og zip-en er kopien som deles ut.
# CLAUDE.md, scripts/ og .github/ er repo-interne og holdes utenfor. Skillen hadde
# ingen zip fram til 2026-09-09; README-en ba brukeren pakke mappen selv, noe som
# ville tatt med CLAUDE.md.
#
# Toppmappa er frontmatter-navnet (`ssb-histstat`), ikke mappenavnet i repoet
# (`ssb-histstat-skill`) — det er frontmatter-navnet som gjelder når pakken lastes
# opp til claude.ai, slik søskenskillene også pakker.
#
# references/-lista er dynamisk (glob), slik at nye referansefiler ikke stille
# faller utenfor pakken.
#
# Bruk:  scripts/build_zip.sh [ut.zip]
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out="${1:-$root/ssb-histstat-skill.zip}"
case "$out" in /*) ;; *) out="$PWD/$out" ;; esac

files=(README.md SKILL.md CHANGELOG.md)
for f in "$root"/references/*.md; do
  files+=("${f#"$root"/}")
done

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
for f in "${files[@]}"; do
  mkdir -p "$tmp/ssb-histstat/$(dirname "$f")"
  cp "$root/$f" "$tmp/ssb-histstat/$f"
done
cp "$root/../LICENSE" "$tmp/ssb-histstat/LICENSE"
files+=(LICENSE)

# Normaliser linjeslutt til LF. Filene kopieres fra disken, ikke fra git, og en
# fil lagret med CRLF (f.eks. fra en Windows-editor) ville ellers gi en zip som
# avviker fra CI-bygget — CI sjekker ut med LF (.gitattributes eol=lf).
find "$tmp" -type f \( -name '*.md' -o -name LICENSE \) -exec sed -i 's/\r$//' {} +

rm -f "$out"
(cd "$tmp" && zip -X -q -r "$out" ssb-histstat)
echo "Bygget $out (${#files[@]} filer)"
