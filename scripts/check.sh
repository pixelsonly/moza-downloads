#!/usr/bin/env bash
# Run every test suite, then build and package each dashboard. Used by CI and releases.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m unittest discover -s generator -t generator
for dir in dashboards/*/; do
  dir="${dir%/}"
  id="$(basename "$dir")"
  python3 -m unittest discover -s "$dir" -t "$dir"
  python3 "$dir/build.py"
  python3 scripts/package.py "$id" 0.0.0-ci
done
python3 -m unittest discover -s scripts -t scripts
