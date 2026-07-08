#!/usr/bin/env python3
"""fixtures.py — synthetic PIL image builders shared by the postproc test suite."""

from PIL import Image, ImageDraw

_BLOB_COLORS = [
    (200, 120, 60, 255), (60, 160, 200, 255), (160, 200, 60, 255),
    (200, 60, 160, 255), (100, 100, 220, 255), (220, 180, 60, 255),
]


def magenta_grid_sheet(rows, cols, cell=100, drift=None):
    """RGBA synthetic tile sheet: magenta 1px interior grid lines over a
    neutral-gray background, with a solid colored blob inset in each cell.

    `drift` maps ("x"|"y", interior_index) -> px offset applied to that
    interior boundary line (index 0 = first interior boundary on that axis),
    simulating NB's few-px drift from an even division.

    Returns (img, true_xs, true_ys): boundary positions (len rows/cols + 1)
    with drift applied, i.e. the ground truth detect_grid should recover.
    """
    drift = drift or {}
    w, h = cols * cell, rows * cell
    bg = (180, 180, 180, 255)  # neutral gray: not magenta, not near-white
    img = Image.new("RGBA", (w, h), bg)
    draw = ImageDraw.Draw(img)

    true_xs = [round(w * k / cols) for k in range(cols + 1)]
    true_ys = [round(h * k / rows) for k in range(rows + 1)]
    for j in range(cols - 1):
        true_xs[j + 1] += drift.get(("x", j), 0)
    for j in range(rows - 1):
        true_ys[j + 1] += drift.get(("y", j), 0)

    pad = 20
    for r in range(rows):
        for c in range(cols):
            x1, x2 = true_xs[c], true_xs[c + 1]
            y1, y2 = true_ys[r], true_ys[r + 1]
            color = _BLOB_COLORS[(r * cols + c) % len(_BLOB_COLORS)]
            draw.rectangle((x1 + pad, y1 + pad, x2 - pad, y2 - pad), fill=color)

    for x in true_xs[1:-1]:
        draw.line([(x, 0), (x, h - 1)], fill=(255, 0, 255, 255), width=1)
    for y in true_ys[1:-1]:
        draw.line([(0, y), (w - 1, y)], fill=(255, 0, 255, 255), width=1)

    return img, true_xs, true_ys


def cyan_squares(n, side=10, bg=(0, 0, 0)):
    """RGB image with `n` disjoint solid (no-AA) cyan squares — exactly
    n*side*side cyan pixels."""
    margin = 10
    w = n * (side + margin) + margin
    h = side + 2 * margin
    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)
    for i in range(n):
        x1 = margin + i * (side + margin)
        y1 = margin
        draw.rectangle((x1, y1, x1 + side - 1, y1 + side - 1), fill=(0, 255, 255))
    return img


def clean_image():
    """RGB image with no cyan pixels."""
    return Image.new("RGB", (64, 64), (128, 128, 128))


def filled_mask(size, box):
    """L mask, 255 inside `box` (inclusive), 0 elsewhere."""
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle(box, fill=255)
    return mask


def alpha_blob(size, box):
    """RGBA image: opaque colored blob inside `box`, transparent elsewhere."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle(box, fill=(200, 120, 60, 255))
    return img
