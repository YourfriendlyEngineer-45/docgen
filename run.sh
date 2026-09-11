#!/bin/sh
# DOCGEN — single entry point.
#
# Pipeline:
#   Python  →  reads CSV + JSON, builds invoice
#   Python  →  spawns Lua to compute discounts, VAT, totals
#   Python  →  spawns Ruby to render HTML
#   Python  →  writes out/INV-XXXX.html
#
# Usage:
#   ./run.sh                                    (uses sample/ files)
#   ./run.sh <items.csv> <customer.json> <out>  (custom paths)

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# ---- argument defaults ----
ITEMS="${1:-sample/invoices.csv}"
CUSTOMER="${2:-sample/customer.json}"
OUT="${3:-out}"

# ---- check every language is present ----
missing=""
command -v python3 >/dev/null 2>&1 || missing="$missing python3"

if ! command -v lua5.4 >/dev/null 2>&1 \
   && ! command -v lua5.3 >/dev/null 2>&1 \
   && ! command -v lua54  >/dev/null 2>&1 \
   && ! command -v lua53  >/dev/null 2>&1 \
   && ! command -v lua    >/dev/null 2>&1; then
  missing="$missing lua54"
fi

command -v ruby >/dev/null 2>&1 || missing="$missing ruby"

if [ -n "$missing" ]; then
  echo "error: missing language(s):$missing" >&2
  echo "" >&2
  echo "Termux:   pkg install python lua54 ruby" >&2
  echo "Ubuntu:   apt install python3 lua5.4 ruby" >&2
  exit 1
fi

# ---- check the three source files exist ----
for f in docgen.py custom.lua render.rb; do
  if [ ! -f "$f" ]; then
    echo "error: required file not found: $f" >&2
    exit 1
  fi
done

# ---- check the two input files exist ----
for f in "$ITEMS" "$CUSTOMER"; do
  if [ ! -f "$f" ]; then
    echo "error: input file not found: $f" >&2
    exit 1
  fi
done

# ---- run ----
src/python3 docgen.py "$ITEMS" "$CUSTOMER" "$OUT"
