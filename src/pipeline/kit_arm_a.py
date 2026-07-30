#!/usr/bin/env python3
"""kit_arm_a.py — arm A's cell sprites: one textured sprite per assembly piece, per camera family.

This is implementation A behind the frozen seam (SCENE-CREATION.md § The seam): a reusable sprite
per piece type, pasted at every cell that wants it. Pixels come from the arm-A painter
(paint_faces.paint_panel — real linework textures + edge ink), not from the flat guide kit that
kit_render.py builds, and the geometry comes from kit_modules.MODULES, so stairs, roofs and
diagonals have pieces at all (the guide kit only had wall/floor/door/window).

Two things are deliberately shared across the whole bake:
  - ONE px-per-voxel `s`, fitted across every module x view x family, so a piece never changes size
    when the view switches (kit_module_render.shared_scale).
  - ONE sprite set per FAMILY, not per view: the 4 dimetric views are cell remaps of the same art,
    and so are the 4 cardinal ones (SCENE-CREATION.md § 8+1 views). 3 sets cover all 9 views.

Orientation is baked as a module yaw, never as a mirror (mirroring flips chirality — kill-log).
"""

import json
from pathlib import Path

import kit_module_render as kmr
import kit_modules as km
import view_table
from face_project import DIMETRIC
from paint_faces import paint_panel

CELL_PX = 512  # the supersampled arm-A cell (R2-1)
PAD = 4
WALL_MATS = ("stone", "wood")

# Ascent/facing side -> module yaw. kit_modules yaws +u toward +v at 90 degrees, and the DSL's E
# arrow is +u (layout_massing._ASCENT), so E is the un-yawed orientation. Pinned by
# test_kit_arm_a.py::test_a_stair_piece_rises_toward_the_side_it_is_named_for.
YAW_FOR_SIDE = {"E": "y0", "S": "y90", "W": "y180", "N": "y270"}


def piece_specs():
    """piece name -> (module, yaw token, material). The assembly vocabulary, in one place."""
    specs = {
        "floor": ("base", "y0", "stone"),
        "door_u": ("door_1x2", "y0", "wood"),
        "door_v": ("door_1x2", "y90", "wood"),
        "window_u": ("window_1x1", "y0", "wood"),
        "window_v": ("window_1x1", "y90", "wood"),
        "diag_u": ("diag_half", "y0", "stone"),
        "diag_v": ("diag_half", "y90", "stone"),
    }
    for mat in WALL_MATS:
        specs[f"wall__{mat}"] = ("wall_band", "y0", mat)
    for side, yaw in YAW_FOR_SIDE.items():
        specs[f"roof_{side}"] = ("roof_cell", yaw, "thatch")
        specs[f"stair_{side}"] = ("stair_45", yaw, "stone")
    return specs


def shared_px_per_voxel(cell_px=CELL_PX, pad=PAD):
    """The one scale every family and every piece is rendered at."""
    families = tuple(view_table.FAMILIES)
    return kmr.shared_scale(list(km.MODULES), cell_px, pad, families)


def _with_material(ordered, mat):
    """Override the mat column of `ordered` — how one module yields per-material variants."""
    return [(face_id, kind, mat, poly) for face_id, kind, _mat, poly in ordered]


def _crop_to_content(sprite, origin):
    """Trim transparent margin; the world-(0,0,0) origin moves with the crop so placement is exact."""
    box = sprite.getbbox()
    if box is None:
        return sprite, origin
    cropped = sprite.crop(box)
    return cropped, (origin[0] - box[0], origin[1] - box[1])


def render_piece(module, view, mat, s, family=DIMETRIC, cell_px=CELL_PX, pad=PAD):
    """(sprite RGBA cropped to content, origin px of world (0,0,0) inside it)."""
    faces = km.MODULES[module]()
    _img, ordered, origin = kmr.render_panel(faces, view, s, cell_px, pad, family)
    recolored = _with_material(ordered, mat)
    painted = paint_panel(module, view, recolored, s, cell_px, pad, origin, family)
    return _crop_to_content(painted, origin)


def build_kit(out_dir, family=DIMETRIC, cell_px=CELL_PX, pad=PAD, s=None):
    """Write one family's sprite set + kit.json into `out_dir`. Returns the manifest dict.

    kit.json keeps the schema scene_assemble.load_kit_meta already reads (px_per_unit, wall_h,
    pieces{name: {origin, size}}) and adds the provenance every piece was built from.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    scale = s if s is not None else shared_px_per_voxel(cell_px, pad)
    manifest = {"px_per_unit": scale, "wall_h": km.WALL_H, "family": family, "arm": "a", "pieces": {}}
    for name, (module, view, mat) in piece_specs().items():
        sprite, origin = render_piece(module, view, mat, scale, family, cell_px, pad)
        sprite.save(out / f"{name}.png")
        manifest["pieces"][name] = {"origin": list(origin), "size": list(sprite.size),
                                    "module": module, "yaw": view, "mat": mat}
    (out / "kit.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def build_all(out_root, cell_px=CELL_PX, pad=PAD):
    """One sprite set per family under `out_root/{family}/` — everything the 9 views need."""
    scale = shared_px_per_voxel(cell_px, pad)
    manifests = {}
    for family in view_table.FAMILIES:
        manifests[family] = build_kit(Path(out_root) / family, family, cell_px, pad, scale)
    return manifests
