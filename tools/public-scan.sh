#!/bin/sh
# public-scan.sh — refuse content that must not be published.
#
#   tools/public-scan.sh            scan the files staged for commit (what the pre-commit hook runs)
#   tools/public-scan.sh --all      scan every tracked file
#   tools/public-scan.sh PATH...    scan the given files or directories
#
# Patterns come from a denylist kept OUTSIDE this repo (the names on it are themselves non-public):
#   $LEARNING_KITS_DENYLIST, default ~/.config/learning-kits/denylist.txt
# one case-insensitive extended regex per line, '#' comments allowed.
# Lines matching a regex in .public-scan-allow (repo root) are ignored: known false positives only.
# Binary files are skipped. Exit 1 on any hit, 2 if the denylist is missing (fail closed; set
# LEARNING_KITS_SCAN=skip to bypass once, e.g. on a machine that has no denylist).
set -u
root=$(git rev-parse --show-toplevel 2>/dev/null) || root=$(pwd)
cd "$root" || exit 2
list=${LEARNING_KITS_DENYLIST:-"$HOME/.config/learning-kits/denylist.txt"}
if [ "${LEARNING_KITS_SCAN:-}" = skip ]; then echo "public-scan: skipped (LEARNING_KITS_SCAN=skip)"; exit 0; fi
if [ ! -r "$list" ]; then
  echo "public-scan: denylist not found at $list (set LEARNING_KITS_DENYLIST, or LEARNING_KITS_SCAN=skip to bypass)"; exit 2
fi
pat=$(grep -v '^[[:space:]]*#' "$list" | grep -v '^[[:space:]]*$' | paste -sd '|' -)
[ -n "$pat" ] || { echo "public-scan: denylist is empty"; exit 2; }
allow=.public-scan-allow
tmp=$(mktemp); trap 'rm -f "$tmp"' EXIT

case "${1:-}" in
  "")    git diff --cached --name-only -z --diff-filter=ACMR > "$tmp" ;;
  --all) git ls-files -z > "$tmp" ;;
  *)     for p in "$@"; do
           if [ -d "$p" ]; then find "$p" -type f -not -path '*/.git/*' -not -path '*/node_modules/*' -print0
           else printf '%s\0' "$p"; fi
         done > "$tmp" ;;
esac
[ -s "$tmp" ] || { echo "public-scan: nothing to scan"; exit 0; }

hits=$(xargs -0 grep -I -i -n -E -e "$pat" < "$tmp" 2>/dev/null)
if [ -n "$hits" ] && [ -r "$allow" ]; then
  apat=$(grep -v '^[[:space:]]*#' "$allow" | grep -v '^[[:space:]]*$' | paste -sd '|' -)
  [ -n "$apat" ] && hits=$(printf '%s\n' "$hits" | grep -v -E -e "$apat")
fi
if [ -n "$hits" ]; then
  n=$(printf '%s\n' "$hits" | wc -l | tr -d ' ')
  echo "public-scan: $n line(s) match the denylist:"; printf '%s\n' "$hits" | cut -c1-220
  echo "public-scan: rewrite the content, or add a false-positive regex to .public-scan-allow with a comment."
  exit 1
fi
echo "public-scan: clean ($(tr -cd '\0' < "$tmp" | wc -c | tr -d ' ') files)"
