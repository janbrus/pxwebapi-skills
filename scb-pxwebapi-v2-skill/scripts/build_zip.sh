#!/usr/bin/env bash
# Bygg scb-pxwebapi-v2-skill.zip — distribusjonspakken med toppmappe scb-pxwebapi-v2/.
#
# Kun brukervendte filer pakkes: SKILL.md, README.md, CHANGELOG.md, references/
# og LICENSE. LICENSE (MIT) ligger i repo-roten og gjelder hele repoet; MIT krever
# at lisensteksten følger med i kopier, og zip-en er kopien som deles ut.
# CLAUDE.md, scripts/, evals/ og .github/ er repo-interne og holdes utenfor. Den
# håndbygde zip-en før v0.11.0 (scb-pxwebapi-v2.zip) manglet README.md og
# CHANGELOG.md og hadde ingen toppmappe; begge deler er rettet her, etter mønster
# fra ssb-pxwebapi-v2-skill.
#
# Toppmappa er frontmatter-navnet (`scb-pxwebapi-v2`), ikke mappenavnet i
# repoet (`scb-pxwebapi-v2-skill`) — det er frontmatter-navnet som gjelder når
# pakken lastes opp til claude.ai.
#
# references/-lista er dynamisk (glob), slik at CI-synksjekken
# (.github/workflows/check-scb-examples.yaml) fanger en utdatert zip i stedet for at
# nye referansefiler stille faller utenfor.
#
# Bruk:  scripts/build_zip.sh [ut.zip]
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out="${1:-$root/scb-pxwebapi-v2-skill.zip}"
case "$out" in /*) ;; *) out="$PWD/$out" ;; esac

files=(README.md SKILL.md CHANGELOG.md)
for f in "$root"/references/*.md; do
  files+=("${f#"$root"/}")
done

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
for f in "${files[@]}"; do
  mkdir -p "$tmp/scb-pxwebapi-v2/$(dirname "$f")"
  cp "$root/$f" "$tmp/scb-pxwebapi-v2/$f"
done
cp "$root/../LICENSE" "$tmp/scb-pxwebapi-v2/LICENSE"
files+=(LICENSE)

rm -f "$out"
(cd "$tmp" && zip -X -q -r "$out" scb-pxwebapi-v2)
echo "Bygget $out (${#files[@]} filer)"
