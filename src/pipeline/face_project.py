#!/usr/bin/env python3
"""face_project.py — the projected-face seam: yaw a module's faces, project them through a camera
family, backface-cull, and sort far->near.

Extracted verbatim-in-behaviour from kit_module_render.py (which re-exports every name here, so
callers and tests keep using `kmr.ordered_faces` / `kmr.project_face`). What changed in the move:
the camera family (view_table.FAMILIES) is now a parameter instead of a hard-coded dimetric camera
with a TOP special-case, so the SAME code renders the 4 dimetric, the 4 cardinal and the TOP view
of the 8+1 table. TOP's old hand-written branches (orthographic (u*s, v*s), sort by centroid_z, cull
axis (0,0,1)) all fall out of the general path under family "top" — verified byte-identical by
test/test_face_project.py.

Panel token vs camera: `view` is the MODULE YAW token ("y0".."y315", or "TOP" for the un-yawed
plan); `family` is the CAMERA. Yaw rotates the face, never the camera.
"""

import math

import view_table
from scene_guide_render import Cam

DIMETRIC = view_table.DIMETRIC


def panel_family(view, family=DIMETRIC):
    """Camera family a panel token renders under — the one place the "TOP" token is resolved."""
    return "top" if view == "TOP" else family


def yaw_deg(view):
    """Panel token -> module yaw in degrees. TOP is un-yawed (its camera does the work)."""
    return 0 if view == "TOP" else int(view[1:])


def panel_cam(view, s, cell_px, pad, origin, family=DIMETRIC):
    """Fixed-scale camera for one panel of `view` in `family`."""
    fam = panel_family(view, family)
    return Cam([], cell_px, cell_px, pad, scale=s, origin=origin, family=fam)


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


def _front_facing(pts, family):
    """ROUND 4 backface cull: normal of `pts` (already yawed) dotted with the camera's
    look-toward-viewer axis (view_table.cull_axis). Dimetric's (1,1,1) matches scene_guide_render's
    _faces, which only ever draws a box's max-u/max-v/top faces. Edge-on (dot == 0) counts as
    back-facing — which is exactly what makes a cardinal camera drop the faces it sees edge-on."""
    n = _face_normal(pts)
    axis = view_table.cull_axis(family)
    return (n[0] * axis[0] + n[1] * axis[1] + n[2] * axis[2]) > 1e-9


def _project(faces, view, cam):
    """Shared per-face projection+sort (R3 split from ordered_faces so both it and
    ordered_enclosure_faces use byte-identical geometry): yaw every Face about the module centre
    (0.5,0.5), project through the fixed-scale `cam`, sort far->near by view_table.depth_key
    ascending. The family comes off `cam`, so a caller switches projection by handing in a
    differently-built Cam and nothing else. face_id = f"{i}:{kind}" is stable across views. Rows
    carry `f.enclosure` AND (ROUND 4) a `front_facing` bool through uncut — callers filter both."""
    rows = []
    deg = yaw_deg(view)
    for i, f in enumerate(faces):
        pts = [_yaw(p, deg, 0.5, 0.5) for p in f.pts]
        poly = [cam.pt(u, v, z) for u, v, z in pts]
        cu = sum(p[0] for p in pts) / len(pts)
        cv = sum(p[1] for p in pts) / len(pts)
        cz = sum(p[2] for p in pts) / len(pts)
        key = view_table.depth_key(cam.family, cu, cv, cz)
        front = _front_facing(pts, cam.family)
        rows.append((key, f"{i}:{f.kind}", f.kind, f.mat, poly, f.enclosure, front))
    rows.sort(key=lambda r: r[0])
    return rows


def ordered_front_faces(faces, view, cam):
    """ALL front-facing faces (enclosure INCLUDED), painter order, tagged enc.
    enclosure_masks depth-composites this; ordered_faces filters to visible."""
    return [(fid, k, m, poly, enc) for _, fid, k, m, poly, enc, front in _project(faces, view, cam) if front]


def ordered_faces(faces, view, cam):
    """Render-visible seam: front-facing, not enclosure-tagged (ROUND 3/4)."""
    return [(fid, k, m, poly) for fid, k, m, poly, enc in ordered_front_faces(faces, view, cam) if not enc]


def ordered_enclosure_faces(faces, view, cam):
    """[(face_id, kind, mat, screen_poly, enclosure)] — the complementary
    mask-only set ordered_faces excludes (ROUND 3: stair_enclosure/
    roof_edge/roof_inset), same projection/sort. Returns ALL enclosure
    faces regardless of facing (not backface-culled — self-occlusion
    bookkeeping wants the full mask-only geometry). Never consumed by
    paint_panel/render_panel; the enclosure MASK is geometric now
    (enclosure_masks.py: solid minus render minus air-above), not from here."""
    return [(fid, k, m, poly, enc) for _, fid, k, m, poly, enc, front in _project(faces, view, cam) if enc]


def project_face(pts, view, s, cell_px, pad, origin, family=DIMETRIC):
    """screen_poly for arbitrary world `pts` (T3, additive-only) — byte-identical transform to the
    per-face step inside `ordered_faces` (same yaw-then-project), so a face's own `ordered` polys
    and a `project_face`-derived poly (e.g. a recess decal's world quad) always land in the same
    screen frame. Does NOT touch ordered_faces/render_panel/render_module."""
    cam = panel_cam(view, s, cell_px, pad, origin, family)
    deg = yaw_deg(view)
    return [cam.pt(*_yaw(p, deg, 0.5, 0.5)) for p in pts]
