#!/usr/bin/env python3
"""kit_module_render.py — shared projected-face seam, flat render, one shared
px-per-voxel scale across a sheet (T2/T3).

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

import math

from PIL import Image, ImageDraw

import kit_modules as km
from kit_render import _black_to_alpha
from scene_guide_render import Cam
from tile_guide_render import FACE_CAP, FACE_LONG, FACE_TOP

YAWS = [0, 45, 90, 135, 180, 225, 270, 315]
VIEWS = [f"y{yaw}" for yaw in YAWS] + ["TOP"]

_COLOR = {
    "top": FACE_TOP,
    "side": FACE_LONG, "slope": FACE_LONG, "gable": FACE_LONG,
    "tread": FACE_LONG, "riser": FACE_LONG,
    "bottom": FACE_CAP,
}


def _yaw(pt, deg, cu, cv):
    u, v, z = pt
    rad = math.radians(deg)
    du, dv = u - cu, v - cv
    ca, sa = math.cos(rad), math.sin(rad)
    return (cu + du * ca - dv * sa, cv + du * sa + dv * ca, z)


def ordered_faces(faces, view, cam):
    """[(face_id, kind, mat, screen_poly)] — canonical seam consumed by render + mask.

    Yaw views: rotate every Face by its yaw about the module centre (0.5,0.5),
    project through the fixed-scale dimetric `cam`, sort far->near by painter
    key (centroid_u+centroid_v, centroid_z) ascending. TOP: orthographic
    (u*s, v*s) through the same cam's scale+origin, sorted by centroid_z
    ascending. face_id = f"{i}:{kind}" (i = builder face index) is stable
    across views since it's assigned before sorting."""
    rows = []
    if view == "TOP":
        for i, f in enumerate(faces):
            poly = [(cam.ox + u * cam.s, cam.oy + v * cam.s) for u, v, _z in f.pts]
            cz = sum(p[2] for p in f.pts) / len(f.pts)
            rows.append((cz, f"{i}:{f.kind}", f.kind, f.mat, poly))
    else:
        deg = int(view[1:])
        for i, f in enumerate(faces):
            pts = [_yaw(p, deg, 0.5, 0.5) for p in f.pts]
            poly = [cam.pt(u, v, z) for u, v, z in pts]
            cu = sum(p[0] for p in pts) / len(pts)
            cv = sum(p[1] for p in pts) / len(pts)
            cz = sum(p[2] for p in pts) / len(pts)
            rows.append(((cu + cv, cz), f"{i}:{f.kind}", f.kind, f.mat, poly))
    rows.sort(key=lambda r: r[0])
    return [(face_id, kind, mat, poly) for _, face_id, kind, mat, poly in rows]


def panel_extent(faces, view, s=1.0):
    """Projected (w, h) bbox of one panel at scale s — no centring, origin (0,0)."""
    cam = Cam([], 0, 0, 0, scale=s, origin=(0.0, 0.0))
    ordered = ordered_faces(faces, view, cam)
    xs = [p[0] for _fid, _k, _m, poly in ordered for p in poly]
    ys = [p[1] for _fid, _k, _m, poly in ordered for p in poly]
    return (max(xs) - min(xs), max(ys) - min(ys))


def shared_scale(module_names, cell_px, pad):
    """One s that fits the largest panel (by w, and separately by h) across ALL
    module x view combos — P3: one scale per sheet, never per-cell."""
    avail = cell_px - 2 * pad
    max_w = max_h = 0.0
    for name in module_names:
        faces = km.MODULES[name]()
        for view in VIEWS:
            w, h = panel_extent(faces, view, s=1.0)
            max_w = max(max_w, w)
            max_h = max(max_h, h)
    return min(avail / (max_w or 1.0), avail / (max_h or 1.0))


def render_panel(faces, view, s, cell_px, pad):
    """(RGBA, ordered, origin) — fixed-scale Cam centring this panel's bbox in the cell."""
    avail = cell_px - 2 * pad
    raw_cam = Cam([], 0, 0, 0, scale=s, origin=(0.0, 0.0))
    raw = ordered_faces(faces, view, raw_cam)
    xs = [p[0] for _fid, _k, _m, poly in raw for p in poly]
    ys = [p[1] for _fid, _k, _m, poly in raw for p in poly]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    ox = -minx + pad + (avail - (maxx - minx)) / 2
    oy = -miny + pad + (avail - (maxy - miny)) / 2
    cam = Cam([], cell_px, cell_px, pad, scale=s, origin=(ox, oy))
    ordered = ordered_faces(faces, view, cam)

    img = Image.new("RGB", (cell_px, cell_px), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    for _face_id, kind, _mat, poly in ordered:
        draw.polygon(poly, fill=_COLOR.get(kind, FACE_LONG))
    rgba = _black_to_alpha(img)
    return rgba, ordered, (ox, oy)


def render_module(name, s, cell_px, pad):
    """dict[view -> (RGBA, ordered, origin)] — 9 entries (VIEWS)."""
    faces = km.MODULES[name]()
    return {view: render_panel(faces, view, s, cell_px, pad) for view in VIEWS}


def build_sheet_manifest(panels, s):
    """panels: list[{module, view, bbox, origin}] -> {px_per_voxel: s, panels: [...]}."""
    return {"px_per_voxel": s, "panels": [dict(p) for p in panels]}
