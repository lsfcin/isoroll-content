#!/usr/bin/env python3
"""test_arm_a_texture.py — arm_a paints every projected face with a warped
texture, no flat MAT_COLORS fills remain (C1); code-verified full face-mask
coverage (C7) — geometry by code, never model eyes (iso-visual HARD RULE).

Seam: stage_kit_modules.paint_panel(module, view, ordered, s, cell_px, pad,
origin) -> RGBA (T4, named in 3-arch.md's Architecture prose: "for each
(face_id,kind,mat,poly) in ordered: ... warp_tiling; alpha-composite onto
cell") — does NOT exist yet on this branch (arm_a currently fills flat
MAT_COLORS; this whole module is what T4 replaces). `_skm()` imports lazily
(see test_texture_map.py's header for the established reason).

Deliberately tests `paint_panel` (one cell_px x cell_px panel) rather than a
fully-assembled per-module sheet: `paint_panel` shares its exact
(ordered, origin, s, cell_px, pad) inputs with `face_masks.face_mask`, so the
two are pixel-aligned by construction with zero grid/gutter-offset guessing
— the same pattern test_kit_module_render.py already uses for its C3
face-mask-alignment test. Sheet-level assembly (per-module grid, magenta
separators, stem-pair file naming) is covered separately in
test_stage_kit_modules.py.
"""

from PIL import Image

import face_masks as fm
import kit_modules as km

CELL_PX, PAD = 160, 6
# R2-5 (S4-REVIEW-ROUNDS.md ROUND 2): recess_door/recess_window are gone —
# door_1x2 is the standalone slab replacement, still a good decal+edge-ink
# fixture (front/back LARGE decal faces + THIN wood-tone edge faces).
FIXTURES = ["wall_band", "roof_cell", "stair_45", "door_1x2"]


def _kmr():
    import kit_module_render
    return kit_module_render


def _skm():
    import stage_kit_modules
    return stage_kit_modules


def _panel(module, view, s=8.0):
    kmr = _kmr()
    faces = km.MODULES[module]()
    img, ordered, origin = kmr.render_panel(faces, view, s, CELL_PX, PAD)
    return ordered, origin, img.size


def _paint(module, view, s=8.0):
    ordered, origin, _size = _panel(module, view, s)
    return _skm().paint_panel(module, view, ordered, s, CELL_PX, PAD, origin), ordered


# ---------------------------------------------------------------------- C1: no flat MAT_COLORS fills remain
def test_arm_a_paints_every_ordered_face_and_never_a_flat_mat_colors_fill():
    skm = _skm()
    flat_colors = set(skm.MAT_COLORS.values())
    for module in FIXTURES:
        painted, ordered = _paint(module, "y45")
        assert painted.mode == "RGBA"
        for face_id, _kind, _mat, poly in ordered:
            cx = int(sum(p[0] for p in poly) / len(poly))
            cy = int(sum(p[1] for p in poly) / len(poly))
            r, g, b, a = painted.getpixel((cx, cy))
            assert a > 0, (module, face_id, "centroid pixel is transparent/unpainted")
            assert (r, g, b) not in flat_colors, (module, face_id, "still a flat MAT_COLORS fill")


def test_arm_a_paints_every_view_not_just_one():
    skm = _skm()
    kmr = _kmr()
    flat_colors = set(skm.MAT_COLORS.values())
    for view in kmr.VIEWS:
        painted, ordered = _paint("wall_band", view)
        for face_id, _kind, _mat, poly in ordered:
            cx = int(sum(p[0] for p in poly) / len(poly))
            cy = int(sum(p[1] for p in poly) / len(poly))
            r, g, b, a = painted.getpixel((cx, cy))
            assert a > 0, (view, face_id)
            assert (r, g, b) not in flat_colors, (view, face_id)


# ---------------------------------------------------------------------- C7: code-verified full face-mask coverage
def test_arm_a_leaves_no_unpainted_pixel_inside_any_face_mask_region():
    for module in FIXTURES:
        ordered, origin, size = _panel(module, "y45")
        idmap, meta = fm.face_mask(ordered, size)
        assert meta, module  # sanity: fixture actually produced masked faces
        painted, _ordered2 = _paint(module, "y45")

        alpha = painted.split()[-1]
        leaks = sum(1 for idval, a in zip(idmap.getdata(), alpha.getdata()) if idval > 0 and a == 0)
        assert leaks == 0, (module, leaks)


def test_arm_a_leaves_no_unpainted_pixel_across_multiple_views():
    for view in ("y0", "y135", "TOP"):
        ordered, origin, size = _panel("roof_cell", view)
        idmap, _meta = fm.face_mask(ordered, size)
        painted, _ordered2 = _paint("roof_cell", view)
        alpha = painted.split()[-1]
        leaks = sum(1 for idval, a in zip(idmap.getdata(), alpha.getdata()) if idval > 0 and a == 0)
        assert leaks == 0, (view, leaks)
