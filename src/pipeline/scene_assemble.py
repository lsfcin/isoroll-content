#!/usr/bin/env python3
"""scene_assemble.py — tinyglade-style deterministic assembly: kit sprites pasted per cell in painter order."""

import argparse
import json
from pathlib import Path

from PIL import Image

import kit_assets
import view_table
from layout_massing import massing
from layout_parse import load as load_layout
from layout_parse import rotate_cw
from scene_guide_render import VIEW_TURNS, Cam

MARGIN = 16


def piece_of(box):
    """(piece, material, direction) for a box — the SEMANTIC tile identity, kit-independent.

    Which sprite file that becomes is kit_assets' job: a kit may carry one "wall", or a "wall__stone"
    and a "wall__wood", or oriented "roof_N".."roof_W", and the layout must not have to know which.
    """
    if box.kind == "floor":
        return ("floor", box.mat, "")
    if box.kind == "wall":
        piece = f"{box.openings[0].kind}_{box.axis}" if box.openings else "wall"
        return (piece, box.mat, "")
    if box.kind == "GRP":
        kind, _sep, direction = box.grp.partition(":")
        return (kind or "group", "", direction)
    return (None, "", "")  # steps: unsupported in assembly v1


def _piece_for(box):
    """Piece name only — the pre-existing seam, kept for callers that don't resolve assets."""
    return piece_of(box)[0]


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


def paint_key(family, box):
    """Painter order, far -> near: ground flats first, then the family's own depth key.

    The flats-first flag is pre-existing (merged runs extending past a nearer flat produced
    cover-through slivers); what is new is that depth comes from view_table, so a cardinal view
    sorts by its own camera axis instead of the dimetric u+v, and z0 finally participates — a
    second-storey wall is nearer the viewer than the ground it stands over.
    """
    return (box.h > 0, view_table.depth_key(family, box.u0, box.v0, box.z0))


def assemble(layout, view, kit_dir):
    """One assembled scene view (RGB on black). Geometry exact by construction — no generation involved."""
    manifest, sprites = load_kit(kit_dir)
    family = view_table.family(view)
    cam = Cam([], 0, 0, 0, scale=manifest["px_per_unit"], origin=(0.0, 0.0), family=family)
    turned = rotate_cw(layout, VIEW_TURNS[view])
    boxes = sorted(massing(turned, merge=False), key=lambda box: paint_key(family, box))
    placements, xs, ys = [], [], []
    for box in boxes:
        piece, mat, direction = piece_of(box)
        if piece is None:
            continue
        name = kit_assets.resolve(sprites, piece, mat, direction)
        if name is None:
            continue
        px, py = cam.pt(box.u0, box.v0, box.z0)
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
