#!/usr/bin/env bash
# Populate examples/figures/ from the manual. Figures are OEM scans and are not
# committed; this pulls them on demand using scripts/lemon.py.
set -euo pipefail
cd "$(dirname "$0")"

LEMON="$(cd .. && pwd)/scripts/lemon.py"
mkdir -p figures

grep -o 'figures/GM[0-9]*\.png' 2007-pontiac-g6-3.9l-valve-cover-gaskets.md \
  | sed 's|figures/||; s|\.png$||' | sort -u | while read -r id; do
    path=$(python3 "$LEMON" pic "https://lemon-manuals.la/images25/$id/" | tail -1)
    cp "$path" "figures/$id.png"
    echo "figures/$id.png"
done

echo "done: $(ls -1 figures | wc -l) figures"
