#!/usr/bin/env bash
# [OBSOLETE-MESH] s3_batch.sh — S3 full pipeline: TripoSR mesh → Blender renders → ComfyUI style pass
#
# Usage:
#   bash content/pipeline/s3_batch.sh <character> [state] [--frames N-M] [--no-triposr]
#
# Steps this script runs:
#   1. TripoSR: concept art → mesh OBJ  (skipped with --no-triposr)
#   2. MANUAL pause: upload OBJ to Mixamo, download rigged FBX
#   3. Blender: FBX → 8-direction renders × all frames
#   4. ComfyUI: blender renders → stylized sprites (batch_stylize.sh logic)
#   5. rembg: style pass outputs → transparent sprites
#
# Requires:
#   - content/chars/{character}/concept/{character}_concept_clean.png
#   - After step 2: content/chars/{character}/rig/{character}_{state}.fbx
#   - COMFY_DIR=/home/lucas/ComfyUI
#
# Example:
#   bash content/pipeline/s3_batch.sh rogue
#   bash content/pipeline/s3_batch.sh rogue idle --frames 1-3 --no-triposr

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
export COMFY_DIR=/home/lucas/ComfyUI

CHARACTER="${1:-rogue}"
STATE="${2:-idle}"
FRAMES_ARG=""
NO_TRIPOSR=false
TEXTURE_MODE="no-materials"   # "no-materials" = use TripoSR baked texture; "tpose" = use T-pose UV projection

# Parse optional flags
shift 2 2>/dev/null || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --frames)    FRAMES_ARG="$2"; shift 2 ;;
    --no-triposr) NO_TRIPOSR=true; shift ;;
    --tpose)     TEXTURE_MODE="tpose"; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

CHAR_DIR="$REPO_ROOT/content/chars/$CHARACTER"
CONCEPT_IMG="$CHAR_DIR/concept/${CHARACTER}_concept_clean.png"
MESH_OBJ="$CHAR_DIR/mesh/mesh.obj"
FBX_PATH="$CHAR_DIR/rig/${CHARACTER}_${STATE}.fbx"
FRONT_TPOSE="$CHAR_DIR/concept/${CHARACTER}_front_tpose.png"
BACK_TPOSE="$CHAR_DIR/concept/${CHARACTER}_back_tpose.png"
STANCES_ROOT="$CHAR_DIR/stances/$STATE"
RENDERS_ROOT="$CHAR_DIR/_renders/$STATE"

echo ""
echo "═══════════════════════════════════════"
echo " S3 pipeline: $CHARACTER / $STATE"
echo "═══════════════════════════════════════"

# ── Step 1: TripoSR mesh generation ───────────────────────────────────────────

if [ "$NO_TRIPOSR" = false ]; then
  echo ""
  echo "── Step 1: TripoSR mesh generation"

  # Prefer T-pose image — Mixamo auto-rigger needs T-pose mesh
  TRIPOSR_IMG="$FRONT_TPOSE"
  if [ ! -f "$TRIPOSR_IMG" ]; then
    TRIPOSR_IMG="$CONCEPT_IMG"
  fi
  if [ ! -f "$TRIPOSR_IMG" ]; then
    echo "  Error: neither T-pose nor concept image found for $CHARACTER"
    exit 1
  fi
  echo "  TripoSR input: $TRIPOSR_IMG"

  cd "$REPO_ROOT"
  python content/pipeline/triposr_mesh.py \
    --image "$TRIPOSR_IMG" \
    --character "$CHARACTER" \
    --resolution 128

  echo ""
  echo "══════════════════════════════════════════════════════════════"
  echo " MANUAL STEP REQUIRED — Mixamo rigging"
  echo "══════════════════════════════════════════════════════════════"
  echo " 1. Open https://www.mixamo.com"
  echo " 2. Upload: $MESH_OBJ"
  echo " 3. Mixamo auto-rigs the mesh"
  echo " 4. Select animation: $STATE"
  echo " 5. Download as FBX (With Skin)"
  echo " 6. Save to: $FBX_PATH"
  echo "══════════════════════════════════════════════════════════════"
  echo ""
  read -p "Press ENTER when FBX is saved to $FBX_PATH ..."
fi

# ── Step 2: Validate FBX ──────────────────────────────────────────────────────

echo ""
echo "── Step 2: Validate inputs"

if [ ! -f "$FBX_PATH" ]; then
  echo "  Error: rigged FBX not found: $FBX_PATH"
  echo "  Upload mesh.obj to Mixamo, download rigged FBX, save it there."
  exit 1
fi

echo "  FBX: $FBX_PATH ✓"

# ── Step 3: Blender render ────────────────────────────────────────────────────

echo ""
echo "── Step 3: Blender render (8 directions)"

BLENDER_ARGS=(
  --fbx "$FBX_PATH"
  --state "$STATE"
  --output-dir "$CHAR_DIR"
  --ortho-scale 0.015
  --shift-y 0.3
  --no-depth
  --no-top
)

if [ -n "$FRAMES_ARG" ]; then
  START=$(echo "$FRAMES_ARG" | cut -d- -f1)
  END=$(echo "$FRAMES_ARG" | cut -d- -f2)
  BLENDER_ARGS+=(--start-frame "$START" --end-frame "$END")
fi

if [ "$TEXTURE_MODE" = "tpose" ]; then
  if [ ! -f "$FRONT_TPOSE" ]; then
    echo "  Error: front T-pose not found: $FRONT_TPOSE"
    echo "  Generate with GPT-4o and save there, or use default mode (no --tpose flag)."
    exit 1
  fi
  BLENDER_ARGS+=(--front-image "$FRONT_TPOSE")
  [ -f "$BACK_TPOSE" ] && BLENDER_ARGS+=(--back-image "$BACK_TPOSE")
  echo "  Texture mode: T-pose UV projection"
else
  BLENDER_ARGS+=(--no-materials)
  echo "  Texture mode: TripoSR baked (--no-materials)"
fi

cd "$REPO_ROOT"
blender --background --python content/pipeline/blender_iso_rig.py -- "${BLENDER_ARGS[@]}"

# ── Step 4: ComfyUI style pass ────────────────────────────────────────────────

echo ""
echo "── Step 4: ComfyUI style pass"

DIRS=(SE E NE N NW W SW S)
mkdir -p "$STANCES_ROOT"
for DIR in "${DIRS[@]}"; do
  # Process all frames for this direction (flat naming: frame_{n:04d}_{DIR}.png)
  for FRAME_IMG in "$RENDERS_ROOT"/frame_*_${DIR}.png; do
    [ -f "$FRAME_IMG" ] || continue
    [[ "$FRAME_IMG" == *_depth_* ]] && continue

    FRAME_BASE=$(basename "$FRAME_IMG" .png)
    echo "  stylize $FRAME_BASE"
    cd "$REPO_ROOT/content/cli"
    tmpdir=$(mktemp -d)
    python iso-cli.py blender-ipadapter "$FRAME_IMG" \
      --concept "$CONCEPT_IMG" \
      --prompt "dark fantasy rogue, hooded assassin, teal-blue cloak, black leather armor, gold trim, leather boots" \
      --out "$tmpdir"
    for f in "$tmpdir"/*.png; do
      [ -f "$f" ] || continue
      stem=$(basename "$f" .png)
      mv "$f" "$STANCES_ROOT/${stem}_${DIR}.png"
    done
    rm -rf "$tmpdir"
    cd "$REPO_ROOT"
  done
done

# ── Step 5: Upscale + rembg ───────────────────────────────────────────────────

echo ""
echo "── Step 5: Upscale + rembg"

for DIR in "${DIRS[@]}"; do
  for SPRITE in "$STANCES_ROOT"/pathA_*_${DIR}.png; do
    [ -f "$SPRITE" ] || continue
    echo "  rembg $(basename "$SPRITE")"
    cd "$REPO_ROOT/content/cli"
    tmpdir=$(mktemp -d)
    python iso-cli.py detail-image "$SPRITE" \
      --size character \
      --rembg \
      --out "$tmpdir"
    for f in "$tmpdir"/*.png; do
      [ -f "$f" ] || continue
      stem=$(basename "$f" .png)
      mv "$f" "$STANCES_ROOT/${stem}_${DIR}.png"
    done
    rm -rf "$tmpdir"
    cd "$REPO_ROOT"
  done
done

echo ""
echo "═══════════════════════════════════════"
echo " S3 pipeline complete"
echo " Stances → $STANCES_ROOT"
echo "═══════════════════════════════════════"
