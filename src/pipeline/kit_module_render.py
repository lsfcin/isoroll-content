#!/usr/bin/env python3
"""kit_module_render.py — flat panel render + one shared px-per-voxel scale across a sheet (T2/T3).

The projected-face seam itself (yaw, backface cull, painter sort, project_face) moved to
face_project.py when the camera family became a parameter; the names are re-exported here, so
`kmr.ordered_faces` / `kmr.project_face` still resolve for every existing caller and test. Every
panel function below takes the same optional `family` (view_table.FAMILIES: dimetric | cardinal |
top) and defaults to the frozen dimetric camera.

Standardized tuple order (Loop 4b, resolving 3-arch.md's own inconsistency
between its `render_panel(...) -> (RGBA, origin, ordered)` line and its
`render_module(...) -> dict[view -> (RGBA, ordered, origin)]` line): BOTH
functions return `(RGBA, ordered, origin)`. `render_module`'s order is the
one test/test_kit_module_render.py actually exercises (`img, ordered, origin
= panels[view]`) and tests can't be hand-edited, so it's the binding one;
`render_panel` — never called directly by any test — is made to agree with
it rather than leaving the two seams disagree, since `render_module` is a
thin per-view wrapper around `render_panel` and forwards its return value
unchanged.
"""

from PIL import Image, ImageDraw

import kit_modules as km
from face_project import (DIMETRIC, ordered_enclosure_faces, ordered_faces,  # noqa: F401
                          ordered_front_faces, panel_cam, project_face)
from kit_render import _black_to_alpha
from tile_guide_render import FACE_CAP, FACE_LONG, FACE_TOP

YAWS = [0, 45, 90, 135, 180, 225, 270, 315]
VIEWS = [f"y{yaw}" for yaw in YAWS] + ["TOP"]

_COLOR = {
    "top": FACE_TOP,
    "side": FACE_LONG, "slope": FACE_LONG, "gable": FACE_LONG,
    "tread": FACE_LONG, "riser": FACE_LONG,
    "bottom": FACE_CAP,
}


def panel_extent(faces, view, s=1.0, family=DIMETRIC):
    """Projected (w, h) bbox of one panel at scale s — no centring, origin (0,0)."""
    cam = panel_cam(view, s, 0, 0, (0.0, 0.0), family)
    ordered = ordered_faces(faces, view, cam)
    xs = [p[0] for _fid, _k, _m, poly in ordered for p in poly]
    ys = [p[1] for _fid, _k, _m, poly in ordered for p in poly]
    return (max(xs) - min(xs), max(ys) - min(ys))


def shared_scale(module_names, cell_px, pad, families=(DIMETRIC,)):
    """One s that fits the largest panel (by w, and separately by h) across ALL
    module x view combos — P3: one scale per sheet, never per-cell. Passing every
    family keeps ONE s across the whole 8+1 bake, so a piece never changes size
    when the view switches (view_table's equal-cell-area property is about the
    projection; this is about the fitted scale)."""
    avail = cell_px - 2 * pad
    max_w = max_h = 0.0
    for name in module_names:
        faces = km.MODULES[name]()
        for family in families:
            for view in VIEWS:
                w, h = panel_extent(faces, view, 1.0, family)
                max_w = max(max_w, w)
                max_h = max(max_h, h)
    return min(avail / (max_w or 1.0), avail / (max_h or 1.0))


def render_panel(faces, view, s, cell_px, pad, family=DIMETRIC):
    """(RGBA, ordered, origin) — fixed-scale Cam centring this panel's bbox in the cell."""
    avail = cell_px - 2 * pad
    raw_cam = panel_cam(view, s, 0, 0, (0.0, 0.0), family)
    raw = ordered_faces(faces, view, raw_cam)
    xs = [p[0] for _fid, _k, _m, poly in raw for p in poly]
    ys = [p[1] for _fid, _k, _m, poly in raw for p in poly]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    ox = -minx + pad + (avail - (maxx - minx)) / 2
    oy = -miny + pad + (avail - (maxy - miny)) / 2
    cam = panel_cam(view, s, cell_px, pad, (ox, oy), family)
    ordered = ordered_faces(faces, view, cam)

    img = Image.new("RGB", (cell_px, cell_px), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    for _face_id, kind, _mat, poly in ordered:
        draw.polygon(poly, fill=_COLOR.get(kind, FACE_LONG))
    rgba = _black_to_alpha(img)
    return rgba, ordered, (ox, oy)


def render_module(name, s, cell_px, pad, family=DIMETRIC):
    """dict[view -> (RGBA, ordered, origin)] — 9 entries (VIEWS)."""
    faces = km.MODULES[name]()
    return {view: render_panel(faces, view, s, cell_px, pad, family) for view in VIEWS}


def enclosure_faces(name, s, cell_px, pad, origins, family=DIMETRIC):
    """dict[view -> [(face_id, kind, mat, poly, enclosure)]] — ROUND 3
    mask-only faces for every view, projected with the SAME per-view
    `origins` render_module already computed (so a mask lands pixel-aligned
    to the rendered panel it accompanies). `origins`: dict[view -> (ox,oy)],
    e.g. {view: origin for view, (_img, _ordered, origin) in
    render_module(...).items()}."""
    faces = km.MODULES[name]()
    result = {}
    for view in VIEWS:
        cam = panel_cam(view, s, cell_px, pad, origins[view], family)
        result[view] = ordered_enclosure_faces(faces, view, cam)
    return result


def build_sheet_manifest(panels, s):
    """panels: list[{module, view, bbox, origin}] -> {px_per_voxel: s, panels: [...]}."""
    return {"px_per_voxel": s, "panels": [dict(p) for p in panels]}
