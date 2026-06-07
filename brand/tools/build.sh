#!/usr/bin/env bash
# RTAM brand build: regenerate the asset tree from brand.json and prove fidelity.
#   generate (live-text source SVGs) -> outline (distribution masters) -> parity
#   gate (3 checks: coord-parity 0, renderer-independence <=150px, position <=4px).
# Exits nonzero on any gate failure. Pass --write to apply; default is a dry-run
# verify (safe to run anytime; touches nothing without --write).
set -euo pipefail
cd "$(dirname "$0")"
WRITE="${1:-}"

echo "== brand.json =="
python3 -c "import json,sys; json.load(open('../spec/brand.json')); print('  valid JSON')"

echo "== parity gate (generator + outliner vs committed design) =="
python3 parity.py

if [ "$WRITE" = "--write" ]; then
  echo "== generate live-text sources (--write) =="
  python3 generate.py --write
  echo "== outline distribution masters (--write) =="
  python3 outline.py --write
  echo "== re-verify after write =="
  python3 parity.py
  echo "BUILD OK (written + verified)"
else
  echo "== generate (dry-run) =="; python3 generate.py
  echo "== outline (dry-run) =="; python3 outline.py
  echo "BUILD OK (dry-run; pass --write to apply)"
fi
