#!/usr/bin/env python3
"""layout_groups.py — pure geometry helpers for sloped-surface GROUPS (roofs/stairs), ported from
design/feel-rig/rig.frag (L184-199 vocab, L365-372 diagSolid, L423-443 grpBaseData/grpCellVoxels).

T1 (.loop/dsl-v2-python/3-arch.md) — ported from rig.frag. No PIL, no I/O — pure functions only.
"""

import math
from dataclasses import dataclass
from typing import Callable

NLVL = 10

WALLISH = {"#", "D", "W"}
DIAG = {"/", "\\"}
STAIRS = {"^", ">", "v", "<"}
ARROW_CW = {"^": ">", ">": "v", "v": "<", "<": "^"}
DIAG_CW = {"/": "\\", "\\": "/"}
ASCENT = {"^": (0, -1), ">": (1, 0), "v": (0, 1), "<": (-1, 0)}
SIDE_NAME = {"^": "N", ">": "E", "v": "S", "<": "W"}
ROOF_FORMS = ["flat", "shed1", "shed2"]
STAIR_TYPES = ["solid", "thin"]
ENCLOSE = ["none", "edge", "inset"]
TYPES = {"#": ["stone", "wood"], ".": ["stone", "grass", "road"], "D": ["wood", "iron"], "W": ["bars", "glass"]}


def diag_solid(grid, r, c, ch):
    """rig.frag L365-372 — which triangle (NE/NW/SE/SW) a derived diagonal at (r,c) fills, or None.

    grid: list[str] rows. ch: "/" or "\\". Looks at WALLISH neighbors N/S/E/W of (r,c).
    """
    rows = len(grid)
    cols = len(grid[0]) if grid else 0

    def solid(rr, cc):
        return 0 <= rr < rows and 0 <= cc < cols and grid[rr][cc] in WALLISH

    n, s, w, e = solid(r - 1, c), solid(r + 1, c), solid(r, c - 1), solid(r, c + 1)
    if ch == "\\":
        if n and e and not solid(r - 1, c + 1):
            return "NE"
        if s and w and not solid(r + 1, c - 1):
            return "SW"
    else:
        if n and w and not solid(r - 1, c - 1):
            return "NW"
        if s and e and not solid(r + 1, c + 1):
            return "SE"
    return None


@dataclass
class _BaseData:
    """Object returned by grp_base_data — see that function's docstring for field meaning."""

    aOf: Callable[[float, float], float]
    aLow: float
    aHigh: float
    rise: float
    form: str
    hAt: Callable[[float, float], float]


def _ascent_projector(direction):
    """aOf(r,c) per rig.frag grpBaseData L425 — projection onto the group's ascent axis."""
    if direction == ">":
        return lambda r, c: c
    if direction == "<":
        return lambda r, c: -c
    if direction == "v":
        return lambda r, c: r
    return lambda r, c: -r  # "^"


def grp_base_data(group):
    """rig.frag L423-435 (grpBaseData) — base-frame geometry for one Group.

    Returns an object exposing: aOf(r,c), aLow, aHigh, rise, form, hAt(r,c).
    `group` has .kind ("roof"|"stair"), .cells (list[(r,c)]), .form (index), .dir (arrow char),
    .incl (ft/cell), .z (base height, voxels). rise = incl/5. form: stairs always use "shed1"
    for hAt regardless of STAIR_TYPES[group.form] (that only affects rendering/name).
    """
    a_of = _ascent_projector(group.dir)
    a_low, a_high = math.inf, -math.inf
    along_uv = group.dir in (">", "<")
    for (r, c) in group.cells:
        for d in (0, 1):
            a = a_of(0, c + d) if along_uv else a_of(r + d, 0)
            a_low = min(a_low, a)
            a_high = max(a_high, a)
    form = "shed1" if group.kind == "stair" else ROOF_FORMS[group.form]

    def h_at(r, c):
        if form == "flat":
            return group.z
        a = a_of(r, c)
        if form == "shed1":
            return group.z + (a - a_low) * group.incl / 5
        return group.z + min(a - a_low, a_high - a) * group.incl / 5

    return _BaseData(a_of, a_low, a_high, group.incl / 5, form, h_at)


def grp_cell_voxels(base_data, group, r, c):
    """rig.frag L437-443 (grpCellVoxels) — [voxLo, voxHi) the surface passes through over cell (r,c).

    hs = base_data.hAt at the 4 corners of the cell; lo/hi = min/max; voxLo = floor(lo+eps) clamped
    to [0, NLVL); voxHi = max(voxLo+1, ceil(hi-eps)) clamped to NLVL.
    """
    eps = 1e-9
    hs = [base_data.hAt(r, c), base_data.hAt(r + 1, c), base_data.hAt(r, c + 1), base_data.hAt(r + 1, c + 1)]
    lo, hi = min(hs), max(hs)
    vox_lo = max(0, math.floor(lo + eps))
    vox_hi = min(NLVL, max(vox_lo + 1, math.ceil(hi - eps)))
    return (vox_lo, vox_hi)
