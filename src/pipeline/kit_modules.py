#!/usr/bin/env python3
"""kit_modules.py — KIT V2 module geometry as faces at world origin (T1).

3-arch.md's binding amendment: the shared module representation is a `Face`
(list of 3-4 CCW (u,v,z) corners), not `layout_massing.Box` — Box is
axis-aligned and can't express odd-45°-yaw or non-rectangular footprints
(diag_half, roof_cell). `extrude()` builds box-like modules from a footprint
polygon; `from_boxes()` reuses `layout_massing.Box` only where box seams
already exist, converting each box to faces via `extrude` (kept as a public,
independently-tested seam even though no builder below calls it anymore —
R2-4 moved stairs to a per-box `extrude`-and-select shape instead).

R2-3/R2-4 (design/S4-REVIEW-ROUNDS.md ROUND 2): roof_cell/stairs are
cover-only at RENDER time. ROUND 3: their enclosure faces (roof gable ends
+ under-eave soffit; stair side envelope + buried back + floor-under-tread)
are back as real `Face` geometry, tagged mask-only via `Face.enclosure`
instead of struck outright — kit_modules stays their single source of
truth. `kit_module_render.ordered_faces` filters them out of render/paint;
`ordered_enclosure_faces` is the mask-emission counterpart
(stage_kit_modules.stage, via face_masks) that picks them back up, grouped
by kind (`stair_enclosure` / `roof_edge` / `roof_inset`) — Lucas's orange
mask regions, for assembly (S4t) to warp wall texture into directly.
"""

from dataclasses import dataclass

from layout_massing import STAIR_RISE, STEPS

UNIT_SQUARE = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
WALL_H = 3.0  # module-local wall height (unit cell, yaw not baked)
THIN = 0.12  # top_cap/base z-band thickness
ROOF_H = 0.7  # roof_cell ridge rise
ROOF_RIDGE_V = 0.3  # off-centre on purpose (two reasons): (1) a ridge at v=0.5 is
# mirror-symmetric across v, which collapses several of the 8 yaw silhouettes
# onto each other (test_kit_module_render.py needs >=4/8 distinct bboxes, "no
# accidental mirror chirality"); (2) the ridge runs along u (not v), so the
# two cover slopes (front v<RIDGE_V, back v>RIDGE_V) are different sizes and
# never coincide screen-exactly at any yaw.
SLAB_THICK = 0.1  # R2-5: standalone door/window slab thickness (module-local
# units) — "10% = 'feet' measurement system" per ROUND-1 Q2/Q3 answers. Same
# constant drives both the slab's own geometry and the painter-placement
# inset metadata (S7, not this module's concern).


@dataclass
class Face:
    pts: list  # list[tuple[float,float,float]] — 3-4 CCW corners in u,v,z
    kind: str  # "top"|"side"|"bottom"|"tread"|"riser"|"slope"|"gable"
    mat: str = "blank"  # arm-a material tag: "stone"|"wood"|"thatch"|"blank"
    enclosure: str = ""  # ROUND 3: "" = rendered normally; non-empty =
    # mask-only (real geometry, never painted — only emitted as a per-view
    # enclosure-mask PNG, tagged with this string: "stair_enclosure" |
    # "roof_edge" | "roof_inset"). See kit_module_render.ordered_faces /
    # ordered_enclosure_faces and stage_kit_modules.stage.


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
    """Thin standalone slab: w wide (u) x SLAB_THICK deep (v) x h tall (z)
    voxels — R2-5 door/window OBJECTS (no wall carving; the wall-with-a-hole
    is emergent at assembly from column placement, S4t, not this module's
    concern). `extrude`'s edge order for this footprint puts the two
    v-normal LARGE faces at side indices 0 (v=0, "front") and 2
    (v=SLAB_THICK, "back"); the two u-normal THIN edge faces land at indices
    1 (u=w, right) and 3 (u=0, left) — texture_map.FAMILY tells all four
    apart by face normal, not by this ordering."""
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
    sloped cover quads RENDER — the gable end triangles ("roof_edge") and
    the horizontal under-eave soffit ("roof_inset") stay real geometry
    (ROUND 3) but are tagged mask-only. Together the 5 faces form a closed
    watertight shell (every edge matches a different-normal neighbour, no
    accidental coplanar seam) — winding chosen so face_edges.stroke_edges'
    adjacency matching is exact by construction, no eave-overhang hack
    needed (nothing here renders alongside the slopes anymore)."""
    a, b, c, d = (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)
    r0, r1 = (0.0, ROOF_RIDGE_V, ROOF_H), (1.0, ROOF_RIDGE_V, ROOF_H)
    return [
        Face([a, b, r1, r0], "slope"),
        Face([r0, r1, c, d], "slope"),
        Face([a, r0, d], "gable", enclosure="roof_edge"),
        Face([c, r1, b], "gable", enclosure="roof_edge"),
        Face([d, c, b, a], "bottom", enclosure="roof_inset"),
    ]


def _stair_cover(rise_scale):
    """Per step: tread (top) + the uphill riser RENDER; the side envelope
    (v=0/v=1), the back face buried against the next step, and the floor
    patch under the tread (bottom) stay real geometry (ROUND 3) but tagged
    `enclosure="stair_enclosure"` — mask-only, so steps read as floating in
    space instead of a solid vertical box. Reuses `extrude`'s own box
    winding unchanged (already a correctly-wound closed solid — no
    reordering needed for face_edges' adjacency matching, unlike the
    hand-rolled roof). `extrude`'s footprint-edge order for
    [(u0,0),(u1,0),(u1,1),(u0,1)] emits faces = [top, bottom, side0(v=0),
    side1(u=u1,"back"), side2(v=1), side3(u=u0,"riser")]."""
    faces = []
    for i in range(STEPS):
        height = STAIR_RISE * rise_scale * (i + 1) / STEPS
        u0 = i / STEPS
        u1 = u0 + 1.0 / STEPS
        footprint = [(u0, 0.0), (u1, 0.0), (u1, 1.0), (u0, 1.0)]
        top, bottom, side0, side1, side2, riser = extrude(footprint, 0.0, height, "step")
        for f in (bottom, side0, side1, side2):
            f.enclosure = "stair_enclosure"
        faces += [top, bottom, side0, side1, side2, riser]
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
