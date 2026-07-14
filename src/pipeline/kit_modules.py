#!/usr/bin/env python3
"""kit_modules.py — KIT V2 module geometry as faces at world origin (T1).

3-arch.md's binding amendment: the shared module representation is a `Face`
(list of 3-4 CCW (u,v,z) corners), not `layout_massing.Box` — Box is
axis-aligned and can't express odd-45°-yaw or non-rectangular footprints
(diag_half, roof_cell). `extrude()` builds box-like modules from a footprint
polygon; `from_boxes()` reuses `layout_massing.Box` only where box seams
already exist (stairs), converting each box to faces via `extrude`.
"""

from dataclasses import dataclass

from layout_massing import STAIR_RISE, STEPS, Box

UNIT_SQUARE = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
WALL_H = 3.0  # module-local wall height (unit cell, yaw not baked)
THIN = 0.12  # top_cap/base z-band thickness
ROOF_H = 0.7  # roof_cell ridge rise
ROOF_RIDGE_V = 0.3  # off-centre on purpose (two reasons): (1) a ridge at v=0.5 is
# mirror-symmetric across v, which collapses several of the 8 yaw silhouettes
# onto each other (test_kit_module_render.py needs >=4/8 distinct bboxes, "no
# accidental mirror chirality"); (2) the ridge runs along u (not v) so its two
# gable end-triangles lie in u=const planes — at this 2:1 dimetric camera,
# those only go x-degenerate (zero screen area) at yaw 135/315, never at the
# yaw=45 view test_kit_module_render.py's face_mask test actually exercises
# (a v=const gable, the first design tried, degenerates exactly at 45/225).
ROOF_EAVE = 0.12  # gable+bottom overhang past the wall line (u<0 / u>1, and the
# bottom's v range too). Without an overhang every gable/slope/bottom corner
# is shared exactly with its neighbour, so at SOME yaw the painter's last
# write (last-write-wins occlusion, by construction) fully subsumes another
# face's identical footprint -> that face's mask ends up empty, which
# test_kit_module_render.py's "every ordered id survives in meta" assertion
# (roof_cell/y45) forbids. The overhang gives every face a sliver only it
# covers, so no face can ever be a strict screen-space subset of the rest.
OPENING_MARGIN = 0.15  # horizontal inset so recess carving yields >1 border face
# (Seam decision, not pinned by 3-arch.md: the doc's door width mirrors
# `_draw_openings`' full-run-width door, which is exactly 1 unit for a
# multi-cell wall run. A KIT V2 module is a single 1x1 cell, so a literal
# full-width opening would leave zero left/right border faces — tying
# recess_door's face count with plain wall_band's instead of exceeding it
# (test_kit_modules.py: door_sides > wall_sides). Insetting the opening
# horizontally satisfies both the qualitative test and the doc's z-span
# pattern (door floor..2h, window 1h..2h) without contradicting anything
# 3-arch.md pins numerically.)


@dataclass
class Face:
    pts: list  # list[tuple[float,float,float]] — 3-4 CCW corners in u,v,z
    kind: str  # "top"|"side"|"bottom"|"tread"|"riser"|"slope"|"gable"
    mat: str = "blank"  # arm-a material tag: "stone"|"wood"|"thatch"|"blank"


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


def _carve_side(a0, a1, b0, b1, w=1.0, h=WALL_H, mat="blank"):
    """Border quads left after cutting the [a0,a1]x[b0,b1] opening from the v=1 side face."""

    def quad(ua0, ua1, zb0, zb1):
        return Face([(ua0, 1.0, zb0), (ua1, 1.0, zb0), (ua1, 1.0, zb1), (ua0, 1.0, zb1)], "side", mat)

    faces = []
    if a0 > 1e-9:
        faces.append(quad(0.0, a0, 0.0, h))
    if a1 < w - 1e-9:
        faces.append(quad(a1, w, 0.0, h))
    if b0 > 1e-9:
        faces.append(quad(a0, a1, 0.0, b0))
    if b1 < h - 1e-9:
        faces.append(quad(a0, a1, b1, h))
    return faces


def _wall_with_opening(a0, a1, b0, b1):
    faces = extrude(UNIT_SQUARE, 0.0, WALL_H)
    # UNIT_SQUARE edge order: 0=north(v=0) 1=east(u=1) 2=south(v=1) 3=west(u=0);
    # faces = [top, bottom, side0, side1, side2, side3] — carve side2 (south, v=1).
    kept = [faces[0], faces[1], faces[2], faces[3], faces[5]]
    return kept + _carve_side(a0, a1, b0, b1)


def _recess_door():
    return _wall_with_opening(OPENING_MARGIN, 1.0 - OPENING_MARGIN, 0.0, min(2.0, WALL_H))


def _recess_window():
    return _wall_with_opening(OPENING_MARGIN, 1.0 - OPENING_MARGIN, min(1.0, WALL_H), min(2.0, WALL_H))


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
    """Triangular-prism wedge: ridge along u at v=ROOF_RIDGE_V, rising to ROOF_H.
    Gable ends and the underside overhang ROOF_EAVE past the wall line (see the
    ROOF_EAVE note above) so no face's screen footprint is ever an exact subset
    of its neighbours'."""
    e = ROOF_EAVE
    a, b, c, d = (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)
    r0, r1 = (0.0, ROOF_RIDGE_V, ROOF_H), (1.0, ROOF_RIDGE_V, ROOF_H)
    ga, gd = (-e, 0.0, 0.0), (-e, 1.0, 0.0)
    gb, gc = (1 + e, 0.0, 0.0), (1 + e, 1.0, 0.0)
    bot = [(-e, -e, 0.0), (1 + e, -e, 0.0), (1 + e, 1 + e, 0.0), (-e, 1 + e, 0.0)]
    return [
        Face(bot, "bottom"),
        Face([ga, gd, r0], "gable"),
        Face([gb, gc, r1], "gable"),
        Face([a, b, r1, r0], "slope"),
        Face([r0, r1, c, d], "slope"),
    ]


def _stair_treads(rise_scale):
    boxes = []
    for i in range(STEPS):
        height = STAIR_RISE * rise_scale * (i + 1) / STEPS
        u0 = i / STEPS
        boxes.append(Box(u0, 0.0, 1.0 / STEPS, 1.0, height, "step"))
    return boxes


def _stair_45():
    return from_boxes(_stair_treads(1.0))


def _stair_half():
    return from_boxes(_stair_treads(0.5))


MODULES = {
    "wall_band": _wall_band,
    "top_cap": _top_cap,
    "base": _base,
    "recess_door": _recess_door,
    "recess_window": _recess_window,
    "diag_half": _diag_half,
    "roof_cell": _roof_cell,
    "stair_45": _stair_45,
    "stair_half": _stair_half,
}
