#!/usr/bin/env python3
"""linework_extra.py — remaining painter-vocabulary materials for /linework:
wood floors, roof shingles, stair strips (Lucas 2026-07-15).

Stairs strategy: the homography mapper is per-face, and stair modules in
kit_modules.py are already decomposed into flat quads (treads, risers, sides,
back). So stairs need no special geometry — just strip textures:
- stair_tread: one step's walking surface (T × T/2), closed borders (the
  step edges), no-cross joints, stitchable along the step run.
- stair_riser: the vertical strip between steps (T × T/4), sparse joints.
- Sides/back reuse wall_stone_side (the face polygon clips the fill).
"""

import random

from linework import (T, EDGE_MARGIN, _head, _line, _joints, PLANK_STEP)

TREAD_H = T // 2
RISER_H = T // 4


def floor_wood(seed):
    """Wood floor tile: lengthwise planks, floor grammar (closed horizontal
    borders, open vertical edges)."""
    r = random.Random(f"floorwood:{seed}")
    s = [_head(), _line(0, 0, T, 0, 2.0), _line(0, T, T, T, 2.0)]
    for y in range(PLANK_STEP, T, PLANK_STEP):
        s.append(_line(0, y, T, y, 1.2))
    for y0 in range(0, T, PLANK_STEP):
        if r.random() < 0.5:
            x = r.uniform(EDGE_MARGIN + 2, T - EDGE_MARGIN - 2)
            s.append(_line(x, y0, x, y0 + PLANK_STEP))
    return "".join(s) + "</svg>"


def roof_shingle(seed):
    """Shingle courses with half-phase staggered ticks; horizontal continuity
    along the roof run, closed borders at the eave/ridge edges."""
    r = random.Random(f"roof:{seed}")
    step = 16
    s = [_head(), _line(0, 0, T, 0, 2.0), _line(0, T, T, T, 2.0)]
    for y in range(step, T, step):
        s.append(_line(0, y, T, y, 1.4))
    for row, y0 in enumerate(range(0, T, step)):
        phase = (step if row % 2 else 0)
        x = phase + r.uniform(-3, 3)
        while x < T - EDGE_MARGIN:
            if x > EDGE_MARGIN:
                s.append(_line(x, y0, x, y0 + step))
            x += 2 * step + r.uniform(-4, 4)
    return "".join(s) + "</svg>"


def stair_tread(seed):
    r = random.Random(f"tread:{seed}")
    s = [_head(T, TREAD_H), _line(0, 0, T, 0, 2.0), _line(0, TREAD_H, T, TREAD_H, 2.5)]
    s += _joints(r, 0, TREAD_H, lo=34, hi=70, slant_p=0.2)
    return "".join(s) + "</svg>"


def stair_riser(seed):
    r = random.Random(f"riser:{seed}")
    s = [_head(T, RISER_H), _line(0, 0, T, 0, 2.0), _line(0, RISER_H, T, RISER_H, 2.0)]
    s += _joints(r, 0, RISER_H, lo=44, hi=84, slant_p=0.15)
    return "".join(s) + "</svg>"


def grass(seed):
    """Ground grass: tuft scatter, NO border lines — omnidirectional
    continuity (no slab seams on organic ground). Transitions to other
    ground materials happen via boundary MASKS at assembly (S6), never
    via per-pair transition textures."""
    r = random.Random(f"grass:{seed}")
    s = [_head()]
    for _ in range(26):
        x = r.uniform(EDGE_MARGIN, T - EDGE_MARGIN)
        y = r.uniform(EDGE_MARGIN, T - EDGE_MARGIN)
        h = r.uniform(5, 9)
        s.append(_line(x, y, x - h * 0.5, y - h, 1.2))
        s.append(_line(x, y, x, y - h * 1.15, 1.2))
        s.append(_line(x, y, x + h * 0.5, y - h * 0.85, 1.2))
    return "".join(s) + "</svg>"


def road_cobble(seed):
    """Cobble road: small dense stones; ALL course lines drawn including the
    tile boundary (0 and T) so vertically stacked tiles coincide — a
    continuous field, borderless like grass. Curbs/edges come from S6
    boundary masks."""
    r = random.Random(f"road:{seed}")
    step = 16
    s = [_head()]
    for y in range(0, T + 1, step):
        s.append(_line(0, y, T, y, 1.2))
    for y0 in range(0, T, step):
        s += _joints(r, y0, y0 + step, lo=14, hi=30, slant_p=0.15)
    return "".join(s) + "</svg>"


EXTRA = {
    **{f"floor_wood_v{i}": (lambda i=i: floor_wood(i), "tiling", (1, 0, 1)) for i in range(1, 5)},
    **{f"roof_shingle_v{i}": (lambda i=i: roof_shingle(i), "tiling", (1, 1, 1)) for i in range(1, 5)},
    **{f"stair_tread_v{i}": (lambda i=i: stair_tread(i), "tiling", (1, 0, 1)) for i in range(1, 5)},
    **{f"stair_riser_v{i}": (lambda i=i: stair_riser(i), "tiling", (1, 1, 0)) for i in range(1, 3)},
    **{f"grass_v{i}": (lambda i=i: grass(i), "tiling", (1, 0, 1)) for i in range(1, 5)},
    **{f"road_cobble_v{i}": (lambda i=i: road_cobble(i), "tiling", (1, 0, 1)) for i in range(1, 5)},
}
