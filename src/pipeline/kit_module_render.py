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


def _face_normal(pts):
    """Cross of the first two edges, un-normalized — sign only matters here."""
    p0, p1, p2 = pts[0], pts[1], pts[2]
    v1, v2 = tuple(b - a for a, b in zip(p0, p1)), tuple(b - a for a, b in zip(p1, p2))
    return (v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0])


def _front_facing(pts, view):
    """ROUND 4 backface cull: normal of `pts` (already yawed for this view)
    dotted with this fixed dimetric camera's look-toward-viewer axis. Every
    y{deg} view shares ONE camera fixed at the +u+v+z octant looking toward
    the origin (yaw rotates the FACE, not the camera) — matches scene_guide
    _render.Cam/_faces, which only ever draws a box's max-u/max-v/top faces,
    exactly what (1,1,1) picks out. TOP is a straight-down camera, axis
    (0,0,1). Edge-on (dot == 0) counts as back-facing (culled)."""
    n = _face_normal(pts)
    axis = (0.0, 0.0, 1.0) if view == "TOP" else (1.0, 1.0, 1.0)
    return (n[0] * axis[0] + n[1] * axis[1] + n[2] * axis[2]) > 1e-9


def _project(faces, view, cam):
    """Shared per-face projection+sort (R3 split from ordered_faces so both
    it and ordered_enclosure_faces use byte-identical geometry): rotate
    every Face by its yaw about the module centre (0.5,0.5), project through
    the fixed-scale dimetric `cam`, sort far->near by painter key
    (centroid_u+centroid_v, centroid_z) ascending. TOP: orthographic
    (u*s, v*s), sorted by centroid_z ascending. face_id = f"{i}:{kind}" is
    stable across views. Rows carry `f.enclosure` AND (ROUND 4) a
    `front_facing` bool through uncut — callers filter both."""
    rows = []
    if view == "TOP":
        for i, f in enumerate(faces):
            poly = [(cam.ox + u * cam.s, cam.oy + v * cam.s) for u, v, _z in f.pts]
            cz = sum(p[2] for p in f.pts) / len(f.pts)
            rows.append((cz, f"{i}:{f.kind}", f.kind, f.mat, poly, f.enclosure, _front_facing(f.pts, view)))
    else:
        deg = int(view[1:])
        for i, f in enumerate(faces):
            pts = [_yaw(p, deg, 0.5, 0.5) for p in f.pts]
            poly = [cam.pt(u, v, z) for u, v, z in pts]
            cu = sum(p[0] for p in pts) / len(pts)
            cv = sum(p[1] for p in pts) / len(pts)
            cz = sum(p[2] for p in pts) / len(pts)
            row = ((cu + cv, cz), f"{i}:{f.kind}", f.kind, f.mat, poly, f.enclosure, _front_facing(pts, view))
            rows.append(row)
    rows.sort(key=lambda r: r[0])
    return rows


def ordered_faces(faces, view, cam):
    """[(face_id, kind, mat, screen_poly)] — canonical seam consumed by
    render + mask. RENDER-visible: excludes `enclosure`-tagged faces (ROUND
    3) AND (ROUND 4) any face backface-culled at this view, for every
    module — closed boxes lose hidden faces (previously just overpainted);
    open covers (stairs/roofs) lose faces with nothing to overpaint them,
    the actual ROUND 4 bug fix."""
    return [(fid, k, m, poly) for _, fid, k, m, poly, enc, front in _project(faces, view, cam)
            if not enc and front]


def ordered_enclosure_faces(faces, view, cam):
    """[(face_id, kind, mat, screen_poly, enclosure)] — the complementary
    mask-only set ordered_faces excludes (ROUND 3: stair_enclosure/
    roof_edge/roof_inset), same projection/sort. Returns ALL enclosure
    faces regardless of facing (not backface-culled — self-occlusion
    bookkeeping wants the full mask-only geometry). Never consumed by
    paint_panel/render_panel; ROUND 4's mask SOURCE is enclosure_masks.
    voxel_silhouette, not this."""
    return [(fid, k, m, poly, enc) for _, fid, k, m, poly, enc, front in _project(faces, view, cam) if enc]


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


def enclosure_faces(name, s, cell_px, pad, origins):
    """dict[view -> [(face_id, kind, mat, poly, enclosure)]] — ROUND 3
    mask-only faces for every view, projected with the SAME per-view
    `origins` render_module already computed (so a mask lands pixel-aligned
    to the rendered panel it accompanies). `origins`: dict[view -> (ox,oy)],
    e.g. {view: origin for view, (_img, _ordered, origin) in
    render_module(...).items()}."""
    faces = km.MODULES[name]()
    result = {}
    for view in VIEWS:
        cam = Cam([], cell_px, cell_px, pad, scale=s, origin=origins[view])
        result[view] = ordered_enclosure_faces(faces, view, cam)
    return result


def project_face(pts, view, s, cell_px, pad, origin):
    """screen_poly for arbitrary world `pts` (T3, additive-only) — byte-identical
    transform to the per-face step inside `ordered_faces` (same yaw-then-project
    for yN views, same raw orthographic for TOP), so a face's own `ordered` polys
    and a `project_face`-derived poly (e.g. a recess decal's world quad) always
    land in the same screen frame. Does NOT touch ordered_faces/render_panel/
    render_module."""
    if view == "TOP":
        ox, oy = origin
        return [(ox + u * s, oy + v * s) for u, v, _z in pts]
    deg = int(view[1:])
    cam = Cam([], cell_px, cell_px, pad, scale=s, origin=origin)
    return [cam.pt(*_yaw(p, deg, 0.5, 0.5)) for p in pts]


def build_sheet_manifest(panels, s):
    """panels: list[{module, view, bbox, origin}] -> {px_per_voxel: s, panels: [...]}."""
    return {"px_per_voxel": s, "panels": [dict(p) for p in panels]}
