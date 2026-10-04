#!/usr/bin/env bash
# Run the test suites, then build and package dashboards. Used by CI and releases.
#   scripts/check.sh            every dashboard
#   scripts/check.sh <id>...    only the named dashboards (generator and scripts tests always run)
set -euo pipefail
cd "$(dirname "$0")/.."

if [ $# -gt 0 ]; then
  dirs=()
  for id in "$@"; do
    if [ ! -f "dashboards/$id/dashboard.json" ]; then
      echo "unknown dashboard: $id" >&2
      exit 1
    fi
    dirs+=("dashboards/$id")
  done
else
  dirs=(dashboards/*/)
fi

python3 -m unittest discover -s generator -t generator
for dir in "${dirs[@]}"; do
  dir="${dir%/}"
  id="$(basename "$dir")"
  python3 -m unittest discover -s "$dir" -t "$dir"
  python3 "$dir/build.py"
  python3 scripts/package.py "$id" 0.0.0-ci
done
python3 -m unittest discover -s scripts -t scripts
