#!/usr/bin/env python3
"""sheet_grid.py — Grid-line detection and cleanup for NB tile-sheets.

The tile guides draw all layout linework and labels in pure magenta, but NB
sometimes reproduces the lines white / near-white instead. Detection therefore
projects a combined magenta-or-white mask to find the real cell boundaries (NB
drifts them a few px from a perfect division). Cleanup strips magenta anywhere
(safe chroma-key) and near-white only in a band along the cell edges, where
linework lives — never in the cell body, where light stone highlights would
be false positives.
"""

from __future__ import annotations

from PIL import Image, ImageChops, ImageDraw

# Magenta-ish classification: R and B high, G low.
RB_MIN = 170
G_MAX = 100
# Near-white classification: all channels at least this bright.
WHITE_MIN = 232
# Width (px) of the edge band where near-white pixels are stripped as linework.
EDGE_BAND = 12
# A projected line counts as detected when its mean mask value beats this
# (0-255 scale); below it we fall back to the even-division position.
LINE_STRENGTH_MIN = 24
# Search window around each expected boundary, as a fraction of one cell.
SEARCH_FRAC = 0.25


def magenta_mask(img: Image.Image) -> Image.Image:
    """Binary L mask (255 = magenta-ish pixel)."""
    rgb = img.convert("RGB")
    r, g, b = rgb.split()
    r_hi = r.point(lambda v: 255 if v >= RB_MIN else 0)
    b_hi = b.point(lambda v: 255 if v >= RB_MIN else 0)
    g_lo = g.point(lambda v: 255 if v <= G_MAX else 0)
    rb = ImageChops.multiply(r_hi, b_hi)
    return ImageChops.multiply(rb, g_lo)


def white_mask(img: Image.Image) -> Image.Image:
    """Binary L mask (255 = near-white pixel)."""
    rgb = img.convert("RGB")
    r, g, b = rgb.split()
    r_hi = r.point(lambda v: 255 if v >= WHITE_MIN else 0)
    g_hi = g.point(lambda v: 255 if v >= WHITE_MIN else 0)
    b_hi = b.point(lambda v: 255 if v >= WHITE_MIN else 0)
    rg = ImageChops.multiply(r_hi, g_hi)
    return ImageChops.multiply(rg, b_hi)


def line_mask(img: Image.Image) -> Image.Image:
    """Mask of anything that can be guide linework: magenta or near-white."""
    return ImageChops.lighter(magenta_mask(img), white_mask(img))


def _profile(mask: Image.Image, axis: int) -> list[int]:
    """Mean mask value per column (axis=0) or per row (axis=1)."""
    w, h = mask.size
    size = (w, 1) if axis == 0 else (1, h)
    line = mask.resize(size, Image.BOX)
    return list(line.getdata())


def _best_boundary(profile: list[int], expected: int, window: int) -> int:
    lo = max(1, expected - window)
    hi = min(len(profile) - 1, expected + window)
    best_pos = expected
    best_val = -1
    for pos in range(lo, hi):
        if profile[pos] > best_val:
            best_val = profile[pos]
            best_pos = pos
    result = best_pos if best_val >= LINE_STRENGTH_MIN else expected
    return result


def detect_boundaries(mask: Image.Image, count: int, axis: int) -> list[int]:
    """Positions of `count` cells' boundaries along an axis (len = count+1).

    Interior boundaries snap to the strongest magenta line near the even
    division; outer edges stay at 0 and size.
    """
    size = mask.size[axis]
    profile = _profile(mask, axis)
    window = max(2, int(size / count * SEARCH_FRAC))
    bounds = [0]
    for k in range(1, count):
        expected = round(size * k / count)
        bounds.append(_best_boundary(profile, expected, window))
    bounds.append(size)
    return bounds


def detect_grid(img: Image.Image, rows: int, cols: int) -> tuple[list[int], list[int]]:
    """(xs, ys) cell boundary positions detected from the guide linework."""
    mask = line_mask(img)
    xs = detect_boundaries(mask, cols, axis=0)
    ys = detect_boundaries(mask, rows, axis=1)
    return xs, ys


def _edge_band_mask(size: tuple[int, int], band: int) -> Image.Image:
    """L mask that is 255 within `band` px of the image border, 0 inside."""
    mask = Image.new("L", size, 255)
    draw = ImageDraw.Draw(mask)
    draw.rectangle((band, band, size[0] - 1 - band, size[1] - 1 - band), fill=0)
    return mask


def _blank_where(rgba: Image.Image, mask: Image.Image) -> Image.Image:
    """RGB to black and alpha to 0 wherever mask is set."""
    keep = mask.point(lambda v: 0 if v else 255)
    r, g, b, a = rgba.split()
    r = ImageChops.multiply(r, keep)
    g = ImageChops.multiply(g, keep)
    b = ImageChops.multiply(b, keep)
    a = ImageChops.multiply(a, keep)
    return Image.merge("RGBA", (r, g, b, a))


def strip_linework(img: Image.Image, band: int = EDGE_BAND) -> Image.Image:
    """Blank guide linework in a cut cell.

    Magenta goes anywhere (safe chroma-key). Near-white goes only within
    `band` px of the cell border — a white grid line lands there, while a
    bright stone highlight in the cell body does not.
    """
    rgba = img.convert("RGBA")
    white_edges = ImageChops.multiply(white_mask(rgba), _edge_band_mask(rgba.size, band))
    combined = ImageChops.lighter(magenta_mask(rgba), white_edges)
    return _blank_where(rgba, combined)
