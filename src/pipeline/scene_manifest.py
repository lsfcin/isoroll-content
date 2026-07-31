#!/usr/bin/env python3
"""scene_manifest.py — build_manifest: layout + kit alignment → scene manifest dict.

Produces {scene, view, pxPerVoxel, tiles[], walls[]} for a given view rotation.
tiles are per-cell (render lane, merge=False); walls are per merged run (export
lane, merge=True). See .loop/export-manifest/3-arch.md for the full contract.
"""

import kit_assets
from layout_groups import DIAG
from layout_massing import STAIR_RISE, massing
from layout_parse import DOOR, FLOOR, STAIRS, WALL, WINDOW, load, rotate_cw
from scene_assemble import load_kit_meta, piece_of
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
        name, mat, direction = piece_of(box)
        if name is None:
            continue
        # 3-arch.md Amendment (C4-seam+): a box places a tile even when this kit has no sprite for
        # it yet — imageOffset degrades to a neutral [0,0] rather than KeyError-ing.
        resolved = kit_assets.resolve(manifest["pieces"], name, mat, direction)
        piece = manifest["pieces"].get(resolved) if resolved else None
        origin = list(piece["origin"]) if piece else [0.0, 0.0]
        size = list(piece["size"]) if piece else [1, 1]
        tiles.append({
            "piece": name,
            "mat": mat,
            "side": direction,
            "asset": kit_assets.asset_name(manifest["pieces"], name, mat, direction),
            "facing": view,
            "u": box.u0,
            "v": box.v0,
            "z": box.z0,
            # Footprint in cells. merge=False is per-cell for walls but NOT for floors — a floor
            # strip is one box spanning l cells — so (u,v) alone does not say how much ground a
            # tile covers. The module needs it for the tile's VOLUME (its document width/height);
            # without it every piece imports as a 1x1 cell and a 6-cell floor strip carries a
            # one-cell box. Added 2026-07-31, CP-3.
            "cells": [box.l, box.d],
            "boundHeight": box.h,
            # The module defines imageOffset as a WORLD displacement normalized by gridSize
            # (isoroll-module/src/transform/CONTEXT.md: mesh.x = baseCenterWorld.x + imgOff.x *
            # gridSize) — an artist nudge away from where the module's own box/anchor model puts
            # the sprite. NEUTRAL here on purpose: this exporter used to emit origin_px / size_px,
            # which is not that quantity in any unit and pushed values out of [0,1] as soon as
            # sprites were cropped (caught live — the module's validator rejected the import).
            # Per-piece alignment is calibrated against live Foundry, not guessed; the raw data
            # that calibration needs is originPx/sizePx below.
            "imageOffset": [0.0, 0.0],
            "originPx": origin,
            "sizePx": size,
            "pxPerVoxel": px_per_unit,
        })

    for lvl, grid in _iter_level_grids(turned):
        for v, row in enumerate(grid):
            for u, ch in enumerate(row):
                if ch in STAIRS:
                    tiles.append({
                        "piece": "stair",
                        "mat": "",
                        "side": "",
                        "asset": "stair.png",
                        "facing": view,
                        "u": u,
                        "v": v,
                        "z": lvl * turned.wall_h,
                        "cells": [1, 1],
                        "boundHeight": float(STAIR_RISE),
                        "imageOffset": [0.0, 0.0],
                        "originPx": [0.0, 0.0],
                        "sizePx": [1, 1],
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
        # D7 guard: unique-pixel memory scales with map area x views, so chunking and per-view lazy
        # bake must stay reachable WITHOUT a format break. This manifest is chunk (0,0) covering the
        # whole grid; a chunked bake changes only these numbers, never the shape of the file.
        "chunk": {"index": [0, 0], "cols": cols, "rows": rows},
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
