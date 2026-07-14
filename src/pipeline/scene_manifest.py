#!/usr/bin/env python3
"""scene_manifest.py — build_manifest: layout + kit alignment → scene manifest dict.

Produces {scene, view, pxPerVoxel, tiles[], walls[]} for a given view rotation.
tiles are per-cell (render lane, merge=False); walls are per merged run (export
lane, merge=True). See .loop/export-manifest/3-arch.md for the full contract.
"""

from layout_groups import DIAG
from layout_massing import STAIR_RISE, massing
from layout_parse import DOOR, FLOOR, STAIRS, WALL, WINDOW, load, rotate_cw
from scene_assemble import _piece_for, load_kit_meta
from scene_guide_render import VIEW_TURNS


def _iter_level_grids(layout):
    """(level_index, grid) pairs — v2 layouts stack levels; v1 layouts are one implicit level 0."""
    if layout.levels:
        for lvl in sorted(layout.levels):
            yield lvl, layout.levels[lvl].g
        return
    yield 0, layout.grid


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
        # 3-arch.md Amendment (C4-seam+): GRP boxes place a tile even without a kit sprite yet
        # (e.g. "group") — imageOffset degrades to a neutral [0,0] rather than KeyError-ing.
        piece = manifest["pieces"].get(name)
        ox, oy = piece["origin"] if piece else (0, 0)
        w, h = piece["size"] if piece else (1, 1)
        tiles.append({
            "piece": name,
            "asset": f"{name}.png",
            "facing": view,
            "u": box.u0,
            "v": box.v0,
            "z": box.z0,
            "boundHeight": box.h,
            "imageOffset": [ox / w, oy / h],
            "pxPerVoxel": px_per_unit,
        })

    for lvl, grid in _iter_level_grids(turned):
        for v, row in enumerate(grid):
            for u, ch in enumerate(row):
                if ch in STAIRS:
                    tiles.append({
                        "piece": "stair",
                        "asset": "stair.png",
                        "facing": view,
                        "u": u,
                        "v": v,
                        "z": lvl * turned.wall_h,
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
            "bottomOffset": box.z0,
            "boundHeight": box.h,
            "dir": box.axis,
            "config": {"move": 1, "sense": 1, "sound": 1, "light": 1, "door": 0, "dir": 0},
        })

    return {
        "scene": layout.name,
        "view": view,
        "pxPerVoxel": px_per_unit,
        "tiles": tiles,
        "walls": walls,
    }


def count_hud(layout):
    """v2 (T6, .loop/dsl-v2-python/3-arch.md) — {walls, doors, windows, floors, stairs, roofs} counts.

    rig.frag updateHud (L1073-1084): walls/diags count VOXELS (one per solid cell, not merged
    runs); doors/windows count RUNS (a D whose same-position neighbor one level down is also D is
    not a new run); stairs = stair-group count; roofs = group count - stair count.
    """
    walls = doors = windows = floors = 0
    below = None
    for _lvl, grid in _iter_level_grids(layout):
        for r, row in enumerate(grid):
            below_row = below[r] if below and r < len(below) else None
            for c, ch in enumerate(row):
                if ch == WALL or ch in DIAG:
                    walls += 1
                elif ch == FLOOR:
                    floors += 1
                elif ch in (DOOR, WINDOW):
                    below_ch = below_row[c] if below_row and c < len(below_row) else None
                    if below_ch != ch:
                        doors, windows = (doors + 1, windows) if ch == DOOR else (doors, windows + 1)
        below = grid
    stairs = sum(1 for g in layout.groups if g.kind == "stair")
    return {"walls": walls, "doors": doors, "windows": windows, "floors": floors,
            "stairs": stairs, "roofs": len(layout.groups) - stairs}


if __name__ == "__main__":
    import json
    import sys

    layout = load(sys.argv[1])
    print(json.dumps(build_manifest(layout, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "NW"), indent=2))
