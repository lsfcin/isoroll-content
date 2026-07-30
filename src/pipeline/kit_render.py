#!/usr/bin/env python3
"""kit_render.py — camera-fixed guide kit: one sprite per piece type (wall/door/window/floor) + alignment manifest."""

import argparse
import json
from pathlib import Path

from layout_massing import Box, Opening
from scene_guide_render import Cam, render_boxes

PX_PER_UNIT = 96
MARGIN = 8
PIECES = ["floor", "wall", "door_u", "door_v", "window_u", "window_v"]


def piece_boxes(name, wall_h=3):
    """Boxes for one kit piece at the world origin. Rotation is handled by cell remapping, never by the sprite."""
    if name == "floor":
        return [Box(0, 0, 1, 1, 0, "floor")]
    openings = []
    if name.startswith("door"):
        openings = [Opening("door", 0)]
    elif name.startswith("window"):
        openings = [Opening("window", 0)]
    axis = "v" if name.endswith("_v") else "u"
    return [Box(0, 0, 1, 1, wall_h, "wall", openings, axis)]


def _bbox(boxes, scale):
    cam = Cam([], 0, 0, 0, scale=scale, origin=(0.0, 0.0))
    xs, ys = [], []
    for b in boxes:
        for u in (b.u0, b.u0 + b.l):
            for v in (b.v0, b.v0 + b.d):
                for z in (0, b.h):
                    x, y = cam.pt(u, v, z)
                    xs.append(x)
                    ys.append(y)
    return min(xs), max(xs), min(ys), max(ys)


def _black_to_alpha(img):
    rgba = img.convert("RGBA")
    gray = img.convert("L")
    mask = gray.point(lambda p: 0 if p <= 8 else 255)
    rgba.putalpha(mask)
    return rgba


def render_piece(name, wall_h=3, px=PX_PER_UNIT):
    """(sprite RGBA, origin px of world (0,0,0)) — origin is what the assembler aligns to the cell corner."""
    boxes = piece_boxes(name, wall_h)
    minx, maxx, miny, maxy = _bbox(boxes, px)
    width = int(maxx - minx) + 2 * MARGIN
    height = int(maxy - miny) + 2 * MARGIN
    origin = (MARGIN - minx, MARGIN - miny)
    cam = Cam(boxes, width, height, 0, scale=px, origin=origin)
    img = render_boxes(boxes, (width, height), cam=cam)
    return _black_to_alpha(img), origin


def build_kit(out_dir, wall_h=3, px=PX_PER_UNIT):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"px_per_unit": px, "wall_h": wall_h, "pieces": {}}
    for name in PIECES:
        sprite, origin = render_piece(name, wall_h, px)
        sprite.save(out / f"{name}.png")
        manifest["pieces"][name] = {"origin": list(origin), "size": list(sprite.size)}
    (out / "kit.json").write_text(json.dumps(manifest, indent=2))
    print(f"Kit: {len(PIECES)} pieces → {out}")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render the guide kit sprites + manifest.")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--wall-h", type=int, default=3)
    parser.add_argument("--px", type=int, default=PX_PER_UNIT)
    args = parser.parse_args()
    build_kit(args.out, args.wall_h, args.px)
