#!/usr/bin/env python3
"""scene_assemble.py — tinyglade-style deterministic assembly: kit sprites pasted per cell in painter order."""

import argparse
import json
from pathlib import Path

from PIL import Image

from layout_massing import massing
from layout_parse import load as load_layout
from layout_parse import rotate_cw
from scene_guide_render import VIEW_TURNS, Cam

MARGIN = 16


def _piece_for(box):
    result = None
    if box.kind == "floor":
        result = "floor"
    elif box.kind == "wall":
        if box.openings:
            result = f"{box.openings[0].kind}_{box.axis}"
        else:
            result = "wall"
    return result  # steps: unsupported in assembly v1


def load_kit_meta(kit_dir):
    """Read kit.json only — no PIL, no requirement that piece PNGs exist on disk.

    Used by manifest building (scene_manifest.build_manifest), which is
    metadata-only by construction: asset EXISTENCE is validated later by
    wall_schema.validate_manifest, not eagerly here.
    """
    kit = Path(kit_dir)
    return json.loads((kit / "kit.json").read_text())


def load_kit(kit_dir):
    kit = Path(kit_dir)
    manifest = load_kit_meta(kit_dir)
    sprites = {}
    for name in manifest["pieces"]:
        sprites[name] = Image.open(kit / f"{name}.png").convert("RGBA")
    return manifest, sprites


def assemble(layout, view, kit_dir):
    """One assembled scene view (RGB on black). Geometry exact by construction — no generation involved."""
    manifest, sprites = load_kit(kit_dir)
    cam = Cam([], 0, 0, 0, scale=manifest["px_per_unit"], origin=(0.0, 0.0))
    turned = rotate_cw(layout, VIEW_TURNS[view])
    boxes = sorted(massing(turned, merge=False), key=lambda b: (b.h > 0, b.u0 + b.v0))
    placements, xs, ys = [], [], []
    for box in boxes:
        name = _piece_for(box)
        if name is None or name not in sprites:
            continue
        px, py = cam.pt(box.u0, box.v0, 0)
        ox, oy = manifest["pieces"][name]["origin"]
        left, top = px - ox, py - oy
        w, h = sprites[name].size
        placements.append((name, left, top))
        xs.extend([left, left + w])
        ys.extend([top, top + h])
    width = int(max(xs) - min(xs)) + 2 * MARGIN
    height = int(max(ys) - min(ys)) + 2 * MARGIN
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    dx, dy = MARGIN - min(xs), MARGIN - min(ys)
    for name, left, top in placements:
        canvas.alpha_composite(sprites[name], (int(left + dx), int(top + dy)))
    return canvas.convert("RGB")


def main():
    parser = argparse.ArgumentParser(description="Assemble a scene from a layout + kit sprites.")
    parser.add_argument("--layout", required=True, type=Path)
    parser.add_argument("--kit", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--views", default="NW,NE,SW,SE")
    args = parser.parse_args()
    layout = load_layout(args.layout)
    if layout.errors:
        raise SystemExit("layout errors:\n" + "\n".join(layout.errors))
    args.outdir.mkdir(parents=True, exist_ok=True)
    for view in args.views.split(","):
        img = assemble(layout, view.strip(), args.kit)
        out = args.outdir / f"{layout.name}_{view.strip()}.png"
        img.save(out)
        print(f"Saved: {out}  ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
