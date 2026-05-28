#!/usr/bin/env bash
# Batch blender-stylize: all 8 isometric directions, frame 0001
# Usage: bash batch_stylize.sh [--frame 0001]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export COMFY_DIR=/home/lucas/ComfyUI

FRAME="${1:-0001}"
PROMPT="dark fantasy rogue, hooded assassin, teal-blue cloak, black leather armor, gold trim, leather boots"
DIRS=(SE E NE N NW W SW S)
RENDERS_ROOT="../chars/rogue/_renders/neutral-idle"
STANCES_ROOT="../chars/rogue/stances/neutral-idle"

cd "$SCRIPT_DIR"

mkdir -p "$STANCES_ROOT"

for DIR in "${DIRS[@]}"; do
  INPUT="$RENDERS_ROOT/frame_${FRAME}_${DIR}.png"
  echo ""
  echo "=== $DIR ==="
  tmpdir=$(mktemp -d)
  python iso-cli.py blender-stylize "$INPUT" \
    --prompt "$PROMPT" \
    --out "$tmpdir"
  for f in "$tmpdir"/*.png; do
    [ -f "$f" ] || continue
    stem=$(basename "$f" .png)
    mv "$f" "$STANCES_ROOT/${stem}_${DIR}.png"
  done
  rm -rf "$tmpdir"
done

echo ""
echo "=== Batch complete ==="
