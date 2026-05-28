#!/usr/bin/env bash
# Batch detail-image --rembg on all 8 stylized direction outputs
# Picks the newest pathA_*.png in each dir
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export COMFY_DIR=/home/lucas/ComfyUI

DIRS=(SE E NE N NW W SW S)
STANCES_ROOT="../chars/rogue/stances/neutral-idle"

cd "$SCRIPT_DIR"

for DIR in "${DIRS[@]}"; do
  INPUT=$(ls -t "$STANCES_ROOT/"pathA_*_${DIR}.png 2>/dev/null | head -1)
  if [ -z "$INPUT" ]; then
    echo "=== $DIR: no pathA_*_${DIR}.png found, skipping ==="
    continue
  fi
  echo ""
  echo "=== $DIR: $INPUT ==="
  tmpdir=$(mktemp -d)
  python iso-cli.py detail-image "$INPUT" \
    --size character \
    --rembg \
    --out "$tmpdir"
  for f in "$tmpdir"/*.png; do
    [ -f "$f" ] || continue
    stem=$(basename "$f" .png)
    mv "$f" "$STANCES_ROOT/${stem}_${DIR}.png"
  done
  rm -rf "$tmpdir"
done

echo ""
echo "=== Rembg batch complete ==="
