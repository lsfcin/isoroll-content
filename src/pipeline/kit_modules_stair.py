#!/usr/bin/env python3
"""kit_modules_stair.py — the stair module's zigzag solid, as faces at world origin.

Split out of kit_modules.py at the size cap (2026-08-01): every other module there is a
one-expression call to `extrude`, while the stair carries its own profile geometry and its own
enclosure-tag vocabulary. Nothing else moved, and nothing was copied — kit_modules imports the two
builders back into MODULES.

ROUND 4 (design/S4-REVIEW-ROUNDS.md): ONE zigzag profile polygon (the step outline in the u-z rise
plane) extruded across the width — treads and risers are strips of one connected solid, not stacked
boxes.
"""

from layout_massing import STAIR_RISE, STEPS

from kit_modules_face import Face

# Enclosure tags only keep faces OUT of render; the mask itself is geometric
# (enclosure_masks.py) and tag-blind.
STAIR_ENCLOSURE, STAIR_LATERAL, STAIR_BACK = "stair_enclosure", "stair_lateral", "stair_back"


def _profile(rise_scale):
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


def cover(rise_scale):
    """ONE zigzag solid, not STEPS stacked boxes: extrude `_profile` across
    width (v: 0->1). The two profile copies (v=0/v=1) are the envelope caps,
    tagged STAIR_LATERAL (enclosure — kept out of render); each profile EDGE
    becomes one v-spanning strip — risers/treads RENDER; back wall = STAIR_BACK
    (masked, backs onto wall); floor = STAIR_ENCLOSURE (z=0 ground, never
    masked). Connectivity by construction."""
    profile = _profile(rise_scale)
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
            faces.append(Face(pts, "side", "step", enclosure=STAIR_BACK))  # back wall — masked (stair backs onto wall)
        else:
            faces.append(Face(pts, "bottom", "step", enclosure=STAIR_ENCLOSURE))  # floor
    return faces


def stair_45():
    return cover(1.0)


def stair_half():
    return cover(0.5)
