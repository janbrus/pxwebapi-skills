#!/usr/bin/env bash
# Bygg ssb-chart-skill.zip — distribusjonspakken med toppmappe ssb-chart/.
#
# Kun brukervendte filer pakkes: SKILL.md, README.md, CHANGELOG.md, references/
# og LICENSE. LICENSE (MIT) ligger i repo-roten og gjelder hele repoet; MIT krever
# at lisensteksten følger med i kopier, og zip-en er kopien som deles ut.
# CLAUDE.md, scripts/ og .github/ er repo-interne og holdes utenfor. Fram til
# 2026-09-09 ble zip-en bygd for hånd; skriptet gjør pakkingen reproduserbar og
# lar CI-synksjekken (.github/workflows/check-chart-zip.yaml) fange en utdatert zip.
#
# Toppmappa er frontmatter-navnet (`ssb-chart`), ikke mappenavnet i repoet
# (`ssb-chart-skill`) — det er frontmatter-navnet som gjelder når pakken lastes
# opp til claude.ai, og det er slik den håndbygde zip-en allerede var pakket.
#
# references/-lista er dynamisk (glob), slik at nye referansefiler ikke stille
# faller utenfor pakken.
#
# Bruk:  scripts/build_zip.sh [ut.zip]
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out="${1:-$root/ssb-chart-skill.zip}"
case "$out" in /*) ;; *) out="$PWD/$out" ;; esac

files=(README.md SKILL.md CHANGELOG.md)
for f in "$root"/references/*.md; do
  files+=("${f#"$root"/}")
done

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
for f in "${files[@]}"; do
  mkdir -p "$tmp/ssb-chart/$(dirname "$f")"
  cp "$root/$f" "$tmp/ssb-chart/$f"
done
cp "$root/../LICENSE" "$tmp/ssb-chart/LICENSE"
files+=(LICENSE)

rm -f "$out"
(cd "$tmp" && zip -X -q -r "$out" ssb-chart)
echo "Bygget $out (${#files[@]} filer)"
