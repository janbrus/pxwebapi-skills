#!/usr/bin/env bash
# Bygg ssb-pxwebapi-v2-skill.zip — distribusjonspakken med toppmappe ssb-pxwebapi-v2/.
#
# Kun brukervendte filer pakkes: SKILL.md, README.md, CHANGELOG.md, references/
# og LICENSE. LICENSE (MIT) ligger i repo-roten og gjelder hele repoet; MIT krever
# at lisensteksten følger med i kopier, og zip-en er kopien som deles ut.
# CLAUDE.md, scripts/, .github/, PLAN.md og evals/ er repo-interne og holdes utenfor.
# docs/ er brukervendt, men holdes også utenfor: brukerveiledningen er for mennesker,
# og instruks-kort.md er for plattformer som ikke laster skills i det hele tatt.
# references/-listen er dynamisk (glob), slik at CI-synksjekken
# (.github/workflows/check-tables.yaml) fanger en utdatert zip i stedet for
# at nye referansefiler stille faller utenfor.
#
# Bruk:  scripts/build_zip.sh [ut.zip]
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out="${1:-$root/ssb-pxwebapi-v2-skill.zip}"
case "$out" in /*) ;; *) out="$PWD/$out" ;; esac

files=(README.md SKILL.md CHANGELOG.md)
for f in "$root"/references/*.md; do
  files+=("${f#"$root"/}")
done

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
for f in "${files[@]}"; do
  mkdir -p "$tmp/ssb-pxwebapi-v2/$(dirname "$f")"
  cp "$root/$f" "$tmp/ssb-pxwebapi-v2/$f"
done
cp "$root/../LICENSE" "$tmp/ssb-pxwebapi-v2/LICENSE"
files+=(LICENSE)

rm -f "$out"
(cd "$tmp" && zip -X -q -r "$out" ssb-pxwebapi-v2)
echo "Bygget $out (${#files[@]} filer)"
