# scripts/lib.sh — shared bash helpers, sourced by the verify_*.sh acceptance scripts.
# shellcheck shell=bash

if [ -t 1 ]; then _B=$'\e[1m'; _G=$'\e[32m'; _Y=$'\e[33m'; _R=$'\e[31m'; _N=$'\e[0m'
else _B=''; _G=''; _Y=''; _R=''; _N=''; fi

log()  { printf '%s==>%s %s\n' "$_B" "$_N" "$*"; }
ok()   { printf '%s PASS %s %s\n' "$_G" "$_N" "$*"; }
warn() { printf '%s warn %s %s\n' "$_Y" "$_N" "$*" >&2; }
die()  { printf '%s FAIL %s %s\n' "$_R" "$_N" "$*" >&2; exit 1; }

# assert_file_contains <file> <ERE-pattern> <human message>
assert_file_contains() {
  grep -qE "$2" "$1" || die "$3 — expected /$2/ in $1"
  ok "$3"
}

# assert_file_count <file> <ERE-pattern> <min-count> <human message>
assert_file_min_count() {
  local n; n="$(grep -cE "$2" "$1" 2>/dev/null || echo 0)"
  [ "$n" -ge "$3" ] || die "$4 — found $n match(es) of /$2/ in $1, need >= $3"
  ok "$4 ($n match(es))"
}

# wait_for_file <path> <timeout-sec>
wait_for_file() {
  local f=$1 t=${2:-30}
  while [ "$t" -gt 0 ]; do [ -s "$f" ] && return 0; sleep 1; t=$((t-1)); done
  die "timeout waiting for non-empty $f"
}
