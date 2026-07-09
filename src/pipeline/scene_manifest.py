#!/usr/bin/env python3
"""scene_manifest.py — build_manifest: layout + kit alignment → scene manifest dict.

Produces {scene, view, pxPerVoxel, tiles[], walls[]} for a given view rotation.
tiles are per-cell (render lane, merge=False); walls are per merged run (export
lane, merge=True). See .loop/export-manifest/3-arch.md for the full contract.
"""

from layout_massing import STAIR_RISE, massing
from layout_parse import STAIRS, load, rotate_cw
from scene_assemble import _piece_for, load_kit_meta
from scene_guide_render import VIEW_TURNS


def build_manifest(layout, kit_dir, view="NW"):
    turned = rotate_cw(layout, VIEW_TURNS[view])
    cols, rows = turned.cols, turned.rows
    manifest = load_kit_meta(kit_dir)
    px_per_unit = manifest["px_per_unit"]

    tiles = []
    for box in massing(turned, merge=False):
        name = _piece_for(box)
        if name is None:
            continue
        piece = manifest["pieces"][name]
        ox, oy = piece["origin"]
        w, h = piece["size"]
        tiles.append({
            "piece": name,
            "asset": f"{name}.png",
            "facing": view,
            "u": box.u0,
            "v": box.v0,
            "boundHeight": box.h,
            "imageOffset": [ox / w, oy / h],
            "pxPerVoxel": px_per_unit,
        })

    for v in range(rows):
        for u in range(cols):
            if turned.kind(u, v) in STAIRS:
                tiles.append({
                    "piece": "stair",
                    "asset": "stair.png",
                    "facing": view,
                    "u": u,
                    "v": v,
                    "boundHeight": float(STAIR_RISE),
                    "imageOffset": [0.0, 0.0],
                    "pxPerVoxel": px_per_unit,
                })

    walls = []
    for box in massing(turned, merge=True):
        if box.kind != "wall":
            continue
        walls.append({
            "ax": box.u0 / cols,
            "ay": box.v0 / rows,
            "bx": (box.u0 + box.l) / cols,
            "by": (box.v0 + box.d) / rows,
            "topOffset": box.h,
            "bottomOffset": 0,
            "config": {"move": 1, "sense": 1, "sound": 1, "light": 1, "door": 0, "dir": 0},
        })

    return {
        "scene": layout.name,
        "view": view,
        "pxPerVoxel": px_per_unit,
        "tiles": tiles,
        "walls": walls,
    }


if __name__ == "__main__":
    import json
    import sys

    layout = load(sys.argv[1])
    print(json.dumps(build_manifest(layout, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "NW"), indent=2))
