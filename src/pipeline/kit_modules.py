#!/usr/bin/env python3
"""kit_modules.py — KIT V2 module geometry as faces at world origin (T1).

3-arch.md: the shared module representation is a `Face` (3-4 CCW (u,v,z)
corners), not `layout_massing.Box` — Box is axis-aligned and can't express
odd-45°-yaw or non-rectangular footprints (diag_half, roof_cell). `extrude()`
builds box-like modules from a footprint polygon; `from_boxes()` reuses
`layout_massing.Box` only where box seams already exist (public,
independently-tested seam — no builder below calls it anymore).

ROUND 3/4 (design/S4-REVIEW-ROUNDS.md): roof_cell/stairs are cover-only at
RENDER time; their enclosure faces (roof gable/soffit; stair envelope/back/
floor) are real `Face` geometry (self-occlusion/silhouette) but `Face.
enclosure`-tagged — mask-only, never painted. `ordered_faces` filters
enclosure out AND (ROUND 4) backface-culls on top, for every module. ROUND
4b's mask SOURCE is `enclosure_masks.lateral_faces` (profile-cap/gable faces),
not this tag generally. ROUND 4 stairs: `_stair_cover` builds ONE zigzag profile
polygon (step outline in the u-z rise plane) extruded across width —
treads/risers are strips of one connected solid, not stacked boxes.
"""

from dataclasses import dataclass

from layout_massing import STAIR_RISE, STEPS

UNIT_SQUARE = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
WALL_H = 3.0  # module-local wall height (unit cell, yaw not baked)
THIN = 0.12  # top_cap/base z-band thickness
ROOF_H = 0.7  # roof_cell ridge rise
STAIR_ENCLOSURE, STAIR_LATERAL = "stair_enclosure", "stair_lateral"  # back-wall/floor unmasked; profile-cap sides = ROUND 4b mask source
ROOF_RIDGE_V = 0.3  # off-centre on purpose: v=0.5 is mirror-symmetric across
# v (collapses yaw silhouettes, test_kit_module_render.py needs >=4/8
# distinct); ridge runs along u, so the two slopes never coincide at any yaw.
SLAB_THICK = 0.1  # R2-5: standalone door/window slab thickness (module-local
# units) — "10% = 'feet'" per ROUND-1 Q2/Q3; also drives the painter-placement inset metadata (S7).


@dataclass
class Face:
    pts: list  # list[tuple[float,float,float]] — 3-4 CCW corners in u,v,z
    kind: str  # "top"|"side"|"bottom"|"slope"|"gable"
    mat: str = "blank"  # arm-a material tag: "stone"|"wood"|"thatch"|"blank"
    enclosure: str = ""  # ROUND 3: "" = rendered (subject to ROUND 4 backface
    # culling too); non-empty = mask-only, never painted regardless of
    # facing: "stair_enclosure"|"stair_lateral"|"roof_edge"|"roof_inset". See kit_module_
    # render.ordered_faces/ordered_enclosure_faces, enclosure_masks.py.


def extrude(footprint, z0, h, mat="blank"):
    """footprint: list[(u,v)], any polygon (CCW). Emits top/bottom + one side per edge."""
    n = len(footprint)
    top = [(u, v, z0 + h) for u, v in footprint]
    bottom = [(u, v, z0) for u, v in reversed(footprint)]
    faces = [Face(top, "top", mat), Face(bottom, "bottom", mat)]
    for i in range(n):
        u0, v0 = footprint[i]
        u1, v1 = footprint[(i + 1) % n]
        pts = [(u0, v0, z0), (u1, v1, z0), (u1, v1, z0 + h), (u0, v0, z0 + h)]
        faces.append(Face(pts, "side", mat))
    return faces


def from_boxes(boxes, mat="blank"):
    """Convert `layout_massing.Box` rectangles via `extrude` — no face sharing between boxes."""
    faces = []
    for b in boxes:
        footprint = [(b.u0, b.v0), (b.u0 + b.l, b.v0), (b.u0 + b.l, b.v0 + b.d), (b.u0, b.v0 + b.d)]
        faces.extend(extrude(footprint, b.z0, b.h, mat))
    return faces


def _wall_band():
    return extrude(UNIT_SQUARE, 0.0, WALL_H)


def _top_cap():
    return extrude(UNIT_SQUARE, WALL_H - THIN, THIN)


def _base():
    return extrude(UNIT_SQUARE, 0.0, THIN)


def _slab(w, h, mat="blank"):
    """Thin standalone slab: w(u) x SLAB_THICK(v) x h(z) — R2-5 door/window
    OBJECTS (no wall carving; the hole is emergent at assembly, S4t). The
    two v-normal LARGE faces land at side indices 0 (front) and 2 (back);
    the two u-normal THIN edges at 1/3 — texture_map.FAMILY tells them
    apart by face normal, not this ordering."""
    footprint = [(0.0, 0.0), (w, 0.0), (w, SLAB_THICK), (0.0, SLAB_THICK)]
    return extrude(footprint, 0.0, h, mat)


def _door_1x2():
    return _slab(1.0, 2.0)


def _window_1x1():
    return _slab(1.0, 1.0)


def _diag_half():
    """Thin rotated quad, corner (0,0) -> corner (1,1), 45 deg in the module's own frame."""
    t = 0.08
    nx, ny = -(2 ** -0.5), 2 ** -0.5  # unit normal to the diagonal
    p0, p1 = (0.0, 0.0), (1.0, 1.0)
    footprint = [
        (p0[0] + nx * t / 2, p0[1] + ny * t / 2),
        (p1[0] + nx * t / 2, p1[1] + ny * t / 2),
        (p1[0] - nx * t / 2, p1[1] - ny * t / 2),
        (p0[0] - nx * t / 2, p0[1] - ny * t / 2),
    ]
    return extrude(footprint, 0.0, WALL_H)


def _roof_cell():
    """Ridge along u at v=ROOF_RIDGE_V, rising to ROOF_H. Only the two
    sloped cover quads RENDER — gable ends ("roof_edge") and the under-eave
    soffit ("roof_inset") stay real geometry but mask-only. The 5 faces
    form a closed watertight shell (every edge matches a different-normal
    neighbour) — winding chosen so face_edges.stroke_edges' adjacency
    matching is exact by construction."""
    a, b, c, d = (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)
    r0, r1 = (0.0, ROOF_RIDGE_V, ROOF_H), (1.0, ROOF_RIDGE_V, ROOF_H)
    return [
        Face([a, b, r1, r0], "slope"),
        Face([r0, r1, c, d], "slope"),
        Face([a, r0, d], "gable", enclosure="roof_edge"),
        Face([c, r1, b], "gable", enclosure="roof_edge"),
        Face([d, c, b, a], "bottom", enclosure="roof_inset"),
    ]


def _stair_profile(rise_scale):
    """Zigzag outline in the (u,z) rise plane: STEPS risers (vertical) alt.
    STEPS treads (horizontal), (0,0)->(1,total_rise), closed by a back edge
    (u=1, down to z=0), bottom implicit on wrap. CCW matches `extrude`'s
    convention (normal = edge dir rotated -90 in-plane): risers point
    down-stair (-u), treads up (+z), back up-stair (+u), bottom down (-z)."""
    rise = STAIR_RISE * rise_scale
    pts = [(0.0, 0.0)]
    for i in range(STEPS):
        u = (i + 1) / STEPS
        z = rise * (i + 1) / STEPS
        pts.append((pts[-1][0], z))  # riser i: straight up to this step's height
        pts.append((u, z))  # tread i: straight across to the next riser
    pts.append((1.0, 0.0))  # back: straight down (bottom closes the wrap)
    return pts


def _stair_cover(rise_scale):
    """ONE zigzag solid (ROUND 4), not STEPS stacked boxes: extrude
    `_stair_profile` across width (v: 0->1). The two profile copies (v=0/
    v=1) are mask-only envelope caps, tagged `STAIR_LATERAL` (ROUND 4b mask
    source); each profile EDGE becomes one v-spanning strip — risers/treads
    RENDER, back/bottom stay `STAIR_ENCLOSURE` (self-occlusion only, never
    masked). Edge-to-edge connectivity between steps is by construction."""
    profile = _stair_profile(rise_scale)
    n = len(profile)
    n_step_edges = 2 * STEPS  # STEPS risers + STEPS treads
    faces = [
        Face([(u, 0.0, z) for u, z in profile], "side", "step", enclosure=STAIR_LATERAL),
        Face([(u, 1.0, z) for u, z in reversed(profile)], "side", "step", enclosure=STAIR_LATERAL),
    ]
    for i in range(n):
        u0, z0 = profile[i]
        u1, z1 = profile[(i + 1) % n]
        pts = [(u0, 0.0, z0), (u1, 0.0, z1), (u1, 1.0, z1), (u0, 1.0, z0)]
        if i < n_step_edges and i % 2 == 0:
            faces.append(Face(pts, "side", "step"))  # riser, renders
        elif i < n_step_edges:
            faces.append(Face(pts, "top", "step"))  # tread, renders
        elif i == n_step_edges:
            faces.append(Face(pts, "side", "step", enclosure=STAIR_ENCLOSURE))  # back wall
        else:
            faces.append(Face(pts, "bottom", "step", enclosure=STAIR_ENCLOSURE))  # floor
    return faces


def _stair_45():
    return _stair_cover(1.0)


def _stair_half():
    return _stair_cover(0.5)


MODULES = {
    "wall_band": _wall_band,
    "top_cap": _top_cap,
    "base": _base,
    "door_1x2": _door_1x2,
    "window_1x1": _window_1x1,
    "diag_half": _diag_half,
    "roof_cell": _roof_cell,
    "stair_45": _stair_45,
    "stair_half": _stair_half,
}
