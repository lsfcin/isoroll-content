#!/usr/bin/env python3
"""kit_modules.py — the KIT V2 module catalogue: one builder per piece, at world origin (T1).

Faces and the two builders that make them live in `kit_modules_face.py`; the stair's zigzag solid
in `kit_modules_stair.py` (both split out at the size cap, 2026-08-01). All three names are
re-exported here, so `km.Face` / `km.extrude` / `km.from_boxes` still resolve for every caller.

ROUND 3/4 (design/S4-REVIEW-ROUNDS.md): roof_cell/stairs are cover-only at RENDER time; their
enclosure faces (roof gable/soffit; stair envelope/back/floor) are real `Face` geometry
(self-occlusion/silhouette) but `Face.enclosure`-tagged — kept out of render, never painted.
`ordered_faces` filters enclosure out AND (ROUND 4) backface-culls on top, for every module. The
mask depth-composites these enclosure faces with the cover (Lucas 2026-07-18, enclosure_masks.py:
ROUND 4c).
"""

from kit_modules_face import Face, extrude, from_boxes
from kit_modules_stair import STAIR_BACK, STAIR_ENCLOSURE, STAIR_LATERAL, stair_45, stair_half

__all__ = [
    "Face", "extrude", "from_boxes", "MODULES",
    "STAIR_ENCLOSURE", "STAIR_LATERAL", "STAIR_BACK",
    "UNIT_SQUARE", "WALL_H", "THIN", "ROOF_H", "ROOF_RIDGE_V", "SLAB_THICK", "WINDOW_SILL",
]

UNIT_SQUARE = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
WALL_H = 3.0  # module-local wall height (unit cell, yaw not baked)
THIN = 0.12  # top_cap/base z-band thickness
ROOF_H = 0.7  # roof_cell ridge rise
ROOF_RIDGE_V = 0.3  # off-centre on purpose: v=0.5 is mirror-symmetric across
# v (collapses yaw silhouettes, test_kit_module_render.py needs >=4/8
# distinct); ridge runs along u, so the two slopes never coincide at any yaw.
SLAB_THICK = 0.1  # R2-5: standalone door/window slab thickness (module-local
# units) — "10% = 'feet'" per ROUND-1 Q2/Q3; also drives the painter-placement inset metadata (S7).
WINDOW_SILL = 1.0  # voxels of wall under a window — see _window_1x1


def _wall_band():
    return extrude(UNIT_SQUARE, 0.0, WALL_H)


def _top_cap():
    return extrude(UNIT_SQUARE, WALL_H - THIN, THIN)


def _base():
    return extrude(UNIT_SQUARE, 0.0, THIN)


def _slab(w, h, z0=0.0, mat="blank"):
    """Thin standalone slab: w(u) x SLAB_THICK(v) x h(z), based at z0 — R2-5
    door/window OBJECTS (no wall carving; the hole is emergent at assembly,
    S4t). The two v-normal LARGE faces land at side indices 0 (front) and 2
    (back); the two u-normal THIN edges at 1/3 — texture_map.FAMILY tells them
    apart by face normal, not this ordering.

    The slab hugs v = 1, the cell's NEAR edge, because that is the wall face
    the camera sees: backface culling keeps only the +v-normal large face, so a
    slab at v = 0..THIN rendered its face 0.9 of a cell deep inside the wall,
    and the door read as hung on the far side of it (Lucas, 2026-08-01)."""
    footprint = [(0.0, 1.0 - SLAB_THICK), (w, 1.0 - SLAB_THICK), (w, 1.0), (0.0, 1.0)]
    return extrude(footprint, z0, h, mat)


def _door_1x2():
    return _slab(1.0, 2.0)


def _window_1x1():
    """Raised one voxel, so a WALL_H=3 band reads sill / window / lintel — one
    voxel of wall below the opening and one above. z0=0 sat the window on the
    floor; scene_guide_render._draw_openings has always drawn a window at
    z 1..2, so the kit module was the piece that disagreed."""
    return _slab(1.0, 1.0, z0=WINDOW_SILL)


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


MODULES = {
    "wall_band": _wall_band,
    "top_cap": _top_cap,
    "base": _base,
    "door_1x2": _door_1x2,
    "window_1x1": _window_1x1,
    "diag_half": _diag_half,
    "roof_cell": _roof_cell,
    "stair_45": stair_45,
    "stair_half": stair_half,
}
