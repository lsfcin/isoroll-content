#!/usr/bin/env python3
"""face_masks.py — id-indexed occlusion masks from the SAME ordered faces
`render_panel` produced (T4, C3). Consumers (Foundry-lighting, arm-a) get
faces known by construction: no recompute, guaranteed pixel alignment with
the render."""

import json

from PIL import Image, ImageDraw

# Human-visible id encoding: pixel value = MASK_BASE + MASK_STEP * paint index
# (1-based). Background stays 0; faces span 48..248, so regions read to the
# eye instead of looking like a black frame. Decode goes through
# meta["color_idx"] (which stores the painted VALUE), never this formula.
MASK_BASE = 40
MASK_STEP = 8


def _paint_value(idx):
    return MASK_BASE + MASK_STEP * idx


def face_mask(ordered, size):
    """(idmap "L", meta) — rasterise each ordered poly IN ORDER, fill =
    MASK_BASE + MASK_STEP * 1-based paint index; last write wins, so
    occluded/degenerate faces (zero pixels surviving) are simply left out of
    `meta` rather than reported as visible with an empty region."""
    assert _paint_value(len(ordered)) <= 255, (
        f"{len(ordered)} faces exceed the uint8 id encoding "
        f"(base {MASK_BASE}, step {MASK_STEP})")
    idmap = Image.new("L", size, 0)
    draw = ImageDraw.Draw(idmap)
    for idx, (_face_id, _kind, _mat, poly) in enumerate(ordered, start=1):
        draw.polygon(poly, fill=_paint_value(idx))

    w, h = size
    counts = {}
    bboxes = {}
    for pos, val in enumerate(idmap.getdata()):
        if not val:
            continue
        counts[val] = counts.get(val, 0) + 1
        x, y = pos % w, pos // w
        if val not in bboxes:
            bboxes[val] = [x, y, x, y]
        else:
            b = bboxes[val]
            b[0], b[1] = min(b[0], x), min(b[1], y)
            b[2], b[3] = max(b[2], x), max(b[3], y)

    meta = {}
    for idx, (face_id, _kind, _mat, _poly) in enumerate(ordered, start=1):
        val = _paint_value(idx)
        if val not in counts:
            continue
        x0, y0, x1, y1 = bboxes[val]
        meta[face_id] = {"color_idx": val, "bbox": (x0, y0, x1 + 1, y1 + 1), "pixels": counts[val]}
    return idmap, meta


def save_mask(idmap, meta, path):
    """Write `<path>_facemask.png` + `<path>_faces.json`."""
    path = str(path)
    idmap.save(f"{path}_facemask.png")
    with open(f"{path}_faces.json", "w") as fh:
        json.dump(meta, fh, indent=2)
