#!/usr/bin/env python3
"""linework.py — seeded SVG texture generator in the technical-linework
language of Lucas's hand sheets (S3, ROADMAP-content-gen 'Plano refinado').

Grammar rules (Lucas 2026-07-15):
- FLOOR: closed horizontal borders (line at tile top/bottom — division between
  adjacent floor sprites in that direction); NO vertical joints at the left/
  right edges — stones continue horizontally across any variant pair.
- Variants share global course heights, so any variant stitches next to any
  other by construction.
- Chirality: door hinges are drawn on the LEFT edge only (orientation band
  rule — rotation is cell remapping, never mirroring).
"""

import json
import random
from pathlib import Path

T = 128          # px per voxel face edge (SVG is resolution-independent)
INK = "#3a3a3a"
STROKE = 1.6
EDGE_MARGIN = 8  # no vertical joints closer than this to a tiling edge

FLOOR_COURSES = [0, 30, 56, 90, 114, 128]
WALL_STONE_COURSES = [0, 26, 52, 78, 104, 128]
PLANK_STEP = 8


def _head(w=T, h=T):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"'
            f' viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="white"/>')


def _line(x1, y1, x2, y2, w=STROKE):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"'
            f' stroke="{INK}" stroke-width="{w}"/>')


def _joints(r, y0, y1, lo=26, hi=58, slant_p=0.35):
    """Vertical joints for one course, never inside the edge margins."""
    out, x = [], 0.0
    while True:
        x += r.uniform(lo, hi)
        if x >= T - EDGE_MARGIN:
            break
        if x < EDGE_MARGIN:
            continue
        slant = r.uniform(-4, 4) if r.random() < slant_p else 0
        out.append(_line(x, y0, x + slant, y1))
    return out


def floor_stone(seed):
    r = random.Random(f"floor:{seed}")
    s = [_head(), _line(0, 0, T, 0, 2.0), _line(0, T, T, T, 2.0)]
    for y in FLOOR_COURSES[1:-1]:
        s.append(_line(0, y, T, y, 2.0))
    for y0, y1 in zip(FLOOR_COURSES, FLOOR_COURSES[1:]):
        s += _joints(r, y0, y1)
        if r.random() < 0.3:
            xm = r.uniform(20, T - 20)
            s.append(_line(xm, y0, xm + r.uniform(10, 24), y1))
    return "".join(s) + "</svg>"


def wall_wood_side(seed):
    r = random.Random(f"wood:{seed}")
    s = [_head()]
    for y in range(PLANK_STEP, T, PLANK_STEP):
        s.append(_line(0, y, T, y, 1.2))
    for y0 in range(0, T, PLANK_STEP):
        if r.random() < 0.55:
            x = r.uniform(EDGE_MARGIN + 2, T - EDGE_MARGIN - 2)
            s.append(_line(x, y0, x, y0 + PLANK_STEP))
    return "".join(s) + "</svg>"


def wall_wood_top(seed):
    """Top face of a wood wall: lengthwise planks, closed borders."""
    r = random.Random(f"woodtop:{seed}")
    s = [_head(), _line(0, 0, T, 0, 2.0), _line(0, T, T, T, 2.0)]
    for y in range(PLANK_STEP, T, PLANK_STEP):
        s.append(_line(0, y, T, y, 1.2))
    for y0 in range(0, T, PLANK_STEP):
        if r.random() < 0.4:
            x = r.uniform(EDGE_MARGIN + 2, T - EDGE_MARGIN - 2)
            s.append(_line(x, y0, x, y0 + PLANK_STEP))
    return "".join(s) + "</svg>"


def wall_stone_side(seed):
    r = random.Random(f"stone:{seed}")
    s = [_head(), _line(0, 0, T, 0, 2.0), _line(0, T, T, T, 2.0)]
    for y in WALL_STONE_COURSES[1:-1]:
        s.append(_line(0, y, T, y, 2.0))
    for y0, y1 in zip(WALL_STONE_COURSES, WALL_STONE_COURSES[1:]):
        s += _joints(r, y0, y1, lo=30, hi=64, slant_p=0.25)
    return "".join(s) + "</svg>"


def wall_stone_top(seed):
    r = random.Random(f"stonetop:{seed}")
    s = [_head(), _line(0, 0, T, 0, 2.0), _line(0, T, T, T, 2.0), _line(0, T / 2, T, T / 2, 2.0)]
    for y0, y1 in ((0, T / 2), (T / 2, T)):
        s += _joints(r, y0, y1, lo=34, hi=70, slant_p=0.2)
    return "".join(s) + "</svg>"


def window_1x1():
    m, c = 14, T / 2
    s = [_head(),
         f'<rect x="{m}" y="{m}" width="{T-2*m}" height="{T-2*m}" fill="white" stroke="{INK}" stroke-width="3"/>',
         f'<rect x="{m+8}" y="{m+8}" width="{T-2*m-16}" height="{T-2*m-16}" fill="white" stroke="{INK}" stroke-width="{STROKE}"/>',
         _line(c, m + 8, c, T - m - 8), _line(m + 8, c, T - m - 8, c)]
    return "".join(s) + "</svg>"


SET = {
    **{f"floor_stone_v{i}": (lambda i=i: floor_stone(i), "tiling", (1, 0, 1)) for i in range(1, 9)},
    **{f"wall_wood_side_v{i}": (lambda i=i: wall_wood_side(i), "tiling", (1, 1, 0)) for i in range(1, 5)},
    "wall_wood_top": (lambda: wall_wood_top(1), "tiling", (1, 0, 1)),
    **{f"wall_stone_side_v{i}": (lambda i=i: wall_stone_side(i), "tiling", (1, 1, 0)) for i in range(1, 5)},
    "wall_stone_top": (lambda: wall_stone_top(1), "tiling", (1, 0, 1)),
    "window_1x1x0": (window_1x1, "decal", (1, 1, 0)),
}


def build_set(out_dir="assets/textures"):
    """Write every SVG + PNG + textures.json manifest. Doors come from
    linework_doors (kept in a sibling module)."""
    import cairosvg
    from linework_doors import DOORS
    out = Path(out_dir)
    (out / "svg").mkdir(parents=True, exist_ok=True)
    (out / "png").mkdir(parents=True, exist_ok=True)
    entries = dict(SET)
    entries.update(DOORS)
    manifest = {}
    for name, (maker, kind, dims) in entries.items():
        svg = maker()
        (out / "svg" / f"{name}.svg").write_text(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(out / "png" / f"{name}.png"))
        manifest[name] = {"svg": f"svg/{name}.svg", "png": f"png/{name}.png",
                          "type": kind, "dims_voxels": dims,
                          "continuity": "horizontal" if kind == "tiling" else None}
    (out / "textures.json").write_text(json.dumps(manifest, indent=2))
    return sorted(manifest)


if __name__ == "__main__":
    names = build_set()
    print(f"{len(names)} textures → assets/textures/")
