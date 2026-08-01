#!/usr/bin/env python3
"""kit_modules_face.py — what a kit face IS, and the two ways to build one.

Split out of kit_modules.py at the size cap (2026-08-01) so the stair builder can reach `Face`
without importing the catalogue that imports IT. Nothing was copied: kit_modules re-exports these
three names, so `km.Face` / `km.extrude` / `km.from_boxes` keep working for every caller.

3-arch.md: the shared module representation is a `Face` (3-4 CCW (u,v,z) corners), not
`layout_massing.Box` — Box is axis-aligned and cannot express odd-45-degree yaw or non-rectangular
footprints (diag_half, roof_cell). `extrude()` builds box-like modules from a footprint polygon;
`from_boxes()` reuses `layout_massing.Box` only where box seams already exist (public,
independently-tested seam — no builder calls it anymore).
"""

from dataclasses import dataclass


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
