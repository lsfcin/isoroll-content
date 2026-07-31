#!/usr/bin/env python3
"""scene_plan.py — WHERE every sprite goes, as data. The parity ground truth.

`scene_assemble.assemble()` used to compute placements inline and throw them away, keeping only
pixels. That made "does Foundry put the tiles where the renderer does?" an eyeball question — which
is exactly the question this project's hard rule says a model must never answer by looking
(core/skills/iso-visual.md). So the placement pass is here, `assemble` consumes it, and a parity
test consumes the same object: one derivation, two readers, no chance of them drifting apart.

Coordinates are SCENE-IMAGE pixels at the kit's `px_per_unit`, with (0,0) at the top-left of the
assembled image (MARGIN already applied) — the frame the preview PNG is in, so a rect from here can
be drawn straight onto that PNG.
"""

import kit_assets
import view_table
from layout_massing import massing
from layout_parse import rotate_cw
from scene_guide_render import VIEW_TURNS, Cam

MARGIN = 16


def _piece_rows(layout, view, kit_meta, sprite_sizes):
    """One row per placeable box, in painter order, in un-offset camera pixels."""
    from scene_assemble import paint_key, piece_of

    family = view_table.family(view)
    cam = Cam([], 0, 0, 0, scale=kit_meta["px_per_unit"], origin=(0.0, 0.0), family=family)
    turned = rotate_cw(layout, VIEW_TURNS[view])
    boxes = sorted(massing(turned, merge=False), key=lambda box: paint_key(family, box))
    rows = []
    for box in boxes:
        piece, mat, direction = piece_of(box)
        if piece is None:
            continue
        name = kit_assets.resolve(sprite_sizes, piece, mat, direction)
        if name is None:
            continue
        px, py = cam.pt(box.u0, box.v0, box.z0)
        ox, oy = kit_meta["pieces"][name]["origin"]
        width, height = sprite_sizes[name]
        rows.append({
            "piece": piece, "mat": mat, "side": direction, "asset": name,
            "u": box.u0, "v": box.v0, "z": box.z0, "boundHeight": box.h,
            "left": px - ox, "top": py - oy, "width": width, "height": height,
        })
    return rows


def plan(layout, view, kit_meta, sprite_sizes):
    """{view, pxPerVoxel, canvas: {width, height}, tiles: [...]} — every sprite's rect in the
    assembled image. `sprite_sizes`: {asset name -> (w, h)} (PIL images work: they carry .size).

    Painter order is preserved: tiles[i] is composited before tiles[i+1], so the LAST rect covering
    a pixel is the one visible there.
    """
    rows = _piece_rows(layout, view, kit_meta, sprite_sizes)
    xs = [value for row in rows for value in (row["left"], row["left"] + row["width"])]
    ys = [value for row in rows for value in (row["top"], row["top"] + row["height"])]
    dx, dy = MARGIN - min(xs), MARGIN - min(ys)
    for row in rows:
        row["left"] += dx
        row["top"] += dy
    width = int(max(xs) - min(xs)) + 2 * MARGIN
    height = int(max(ys) - min(ys)) + 2 * MARGIN
    return {
        "view": view,
        "pxPerVoxel": kit_meta["px_per_unit"],
        "canvas": {"width": width, "height": height},
        "tiles": rows,
    }


def sizes_of(sprites):
    """{name -> (w, h)} from a dict of PIL images — the shape `plan` wants."""
    return {name: image.size for name, image in sprites.items()}
