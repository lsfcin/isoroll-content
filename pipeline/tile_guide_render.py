#!/usr/bin/env python3
"""tile_guide_render.py — dimetric box-face geometry and single-panel drawing for tile guides."""

from PIL import Image, ImageDraw

TOP_RED     = (230, 30, 30)
BACK_GRAY   = (150, 150, 150)
FRONT_GREEN = (40, 200, 60)
WEST_BLUE   = (50, 90, 230)
EAST_PURPLE = (150, 40, 200)
SILHOUETTE  = (255, 255, 255)
GRID_LINE   = (255, 255, 255)
SIL_WIDTH   = 5
GRID_WIDTH  = 2

# Unit-scale corner offsets (2:1 dimetric — 26.57°). Real pixels = these * s.
_UX, _UY, _UZ = 1.0, 0.5, 1.0
# Folded-top row height, relative to a body row: a D- or W-unit folds flat
# using the same _UY that governs it in the iso views, vs. a body row's _UZ.
TOP_FOLD_RATIO = _UY / _UZ


def _corner(u, v, z):
    x = (u - v) * _UX
    y = (u + v) * _UY - z * _UZ
    return x, y


def _bbox(l, d, h):
    xs, ys = [], []
    for u in (0, l):
        for v in (0, d):
            for z in (0, h):
                x, y = _corner(u, v, z)
                xs.append(x)
                ys.append(y)
    return min(xs), max(xs), min(ys), max(ys)


def fit_scale(l, d, h, avail_w, avail_h):
    minx, maxx, miny, maxy = _bbox(l, d, h)
    return min(avail_w / (maxx - minx or 1), avail_h / (maxy - miny or 1))


def _origin_for_cell(l, d, h, cell_box, pad):
    cx, cy, cw, ch = cell_box
    avail_w, avail_h = cw - 2 * pad, ch - 2 * pad
    s = fit_scale(l, d, h, avail_w, avail_h)
    minx, maxx, miny, maxy = _bbox(l, d, h)
    ox = pad - minx * s + (avail_w - (maxx - minx) * s) / 2
    oy = pad - miny * s + (avail_h - (maxy - miny) * s) / 2
    return s, ox, oy


def _quad_grid(draw, uvz_fn, steps_a, steps_b, color, s, ox, oy):
    def scr(a, b):
        u, v, z = uvz_fn(a, b)
        x, y = _corner(u, v, z)
        return ox + x * s, oy + y * s

    poly = [scr(0, 0), scr(steps_a, 0), scr(steps_a, steps_b), scr(0, steps_b)]
    draw.polygon(poly, fill=color)
    draw.line(poly + [poly[0]], fill=SILHOUETTE, width=SIL_WIDTH, joint="curve")
    for a in range(1, steps_a):
        draw.line([scr(a, 0), scr(a, steps_b)], fill=GRID_LINE, width=GRID_WIDTH)
    for b in range(1, steps_b):
        draw.line([scr(0, b), scr(steps_a, b)], fill=GRID_LINE, width=GRID_WIDTH)


def draw_iso_panel(img, l, d, h, view, cell_box, pad=18):
    """One 3-face dimetric box view. view in {NW, NE, SW, SE}.

    The raw formula only tiles into a non-overlapping hexagon for one fixed
    corner (long face at v=d, cap at u=l) — verified numerically (shapely,
    zero pairwise intersection) and against the reference deck. NE and SW
    use that geometry directly (recolored — NE:gray+purple, SW:green+blue,
    same footprint). NW and SE need the mirror image of it (recolored
    gray+blue / green+purple) — done by rendering to a scratch cell and
    flipping, never by re-deriving the geometry, since a horizontal mirror
    of a valid hexagon is always still valid.
    """
    is_north = "N" in view
    is_east = "E" in view
    needs_mirror = is_north != is_east
    long_color = BACK_GRAY if is_north else FRONT_GREEN
    cap_color = EAST_PURPLE if is_east else WEST_BLUE

    cx, cy, cw, ch = cell_box
    scratch = Image.new("RGB", (cw, ch), (0, 0, 0))
    sdraw = ImageDraw.Draw(scratch)
    s, ox, oy = _origin_for_cell(l, d, h, (0, 0, cw, ch), pad)

    _quad_grid(sdraw, lambda a, b: (a, d, b), l, h, long_color, s, ox, oy)
    _quad_grid(sdraw, lambda a, b: (l, a, b), d, h, cap_color, s, ox, oy)
    _quad_grid(sdraw, lambda a, b: (a, b, h), l, d, TOP_RED, s, ox, oy)

    if needs_mirror:
        scratch = scratch.transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(scratch, (cx, cy))


def draw_flat_grid(draw, cols, rows, body_color, top_rows, cell_box, pad=18):
    """Orthographic elevation, unfolded-net style: cols x rows cells, the top
    `top_rows` rows are the TOP face folded flat above the body (TOP_RED),
    drawn shorter than a body row by TOP_FOLD_RATIO (matches the iso views'
    own D/W-unit vs H-unit proportions)."""
    cx, cy, cw, ch = cell_box
    avail_w, avail_h = cw - 2 * pad, ch - 2 * pad
    body_rows = rows - top_rows
    units = cols
    row_units = body_rows + top_rows * TOP_FOLD_RATIO
    cell_s = min(avail_w / units, avail_h / row_units)
    top_row_h = cell_s * TOP_FOLD_RATIO
    grid_w = cols * cell_s
    grid_h = top_rows * top_row_h + body_rows * cell_s
    ox, oy = cx + (cw - grid_w) / 2, cy + (ch - grid_h) / 2

    def row_y(r):
        return oy + (r * top_row_h if r <= top_rows else top_rows * top_row_h + (r - top_rows) * cell_s)

    for r in range(rows):
        y0, y1 = row_y(r), row_y(r + 1)
        for c in range(cols):
            x0 = ox + c * cell_s
            fill = TOP_RED if r < top_rows else body_color
            draw.rectangle([x0, y0, x0 + cell_s, y1], fill=fill)
    for c in range(cols + 1):
        x = ox + c * cell_s
        draw.line([(x, oy), (x, oy + grid_h)], fill=GRID_LINE, width=GRID_WIDTH)
    for r in range(rows + 1):
        y = row_y(r)
        draw.line([(ox, y), (ox + grid_w, y)], fill=GRID_LINE, width=GRID_WIDTH)
    draw.rectangle([ox, oy, ox + grid_w, oy + grid_h], outline=SILHOUETTE, width=SIL_WIDTH)
