#!/usr/bin/env bash
# Refresh examples/figures/ from the manual. The scans are committed, so this
# is only needed to re-pull or replace them, using scripts/lemon.py.
set -euo pipefail
cd "$(dirname "$0")"

LEMON="$(cd .. && pwd)/scripts/lemon.py"
mkdir -p figures

grep -oh 'figures/[A-Z][A-Z0-9]*\.\(png\|jpg\)' *.md \
  | sed 's|figures/||' | sort -u | while read -r file; do
    id="${file%.*}"
    path=$(python3 "$LEMON" pic "https://lemon-manuals.la/images25/$id/" | tail -1)
    cp "$path" "figures/$file"
    echo "figures/$file"
done

echo "done: $(ls -1 figures | wc -l) figures"
