#!/usr/bin/env python3
"""tile_guide_render.py — dimetric box-face geometry and single-panel drawing for tile guides."""

TOP_RED     = (230, 30, 30)
BACK_GRAY   = (150, 150, 150)
FRONT_GREEN = (40, 200, 60)
WEST_BLUE   = (50, 90, 230)
EAST_PURPLE = (150, 40, 200)
OUTLINE     = (15, 15, 15)
GRID_LINE   = (245, 245, 245)

# Unit-scale corner offsets (2:1 dimetric — 26.57°). Real pixels = these * s.
_UX, _UY, _UZ = 1.0, 0.5, 1.0


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
    ox = cx + pad - minx * s + (avail_w - (maxx - minx) * s) / 2
    oy = cy + pad - miny * s + (avail_h - (maxy - miny) * s) / 2
    return s, ox, oy


def _quad_grid(draw, uvz_fn, steps_a, steps_b, color, s, ox, oy):
    def scr(a, b):
        u, v, z = uvz_fn(a, b)
        x, y = _corner(u, v, z)
        return ox + x * s, oy + y * s

    poly = [scr(0, 0), scr(steps_a, 0), scr(steps_a, steps_b), scr(0, steps_b)]
    draw.polygon(poly, fill=color, outline=OUTLINE)
    for a in range(1, steps_a):
        draw.line([scr(a, 0), scr(a, steps_b)], fill=GRID_LINE, width=2)
    for b in range(1, steps_b):
        draw.line([scr(0, b), scr(steps_a, b)], fill=GRID_LINE, width=2)


def draw_iso_panel(draw, l, d, h, view, cell_box, pad=18):
    """One 3-face dimetric box view. view in {NW, NE, SW, SE}."""
    s, ox, oy = _origin_for_cell(l, d, h, cell_box, pad)
    north = view in ("NW", "NE")
    west = view in ("NW", "SW")

    if north:
        _quad_grid(draw, lambda a, b: (a, d, b), l, h, BACK_GRAY, s, ox, oy)
    else:
        _quad_grid(draw, lambda a, b: (a, 0, b), l, h, FRONT_GREEN, s, ox, oy)

    if west:
        _quad_grid(draw, lambda a, b: (0, a, b), d, h, WEST_BLUE, s, ox, oy)
    else:
        _quad_grid(draw, lambda a, b: (l, a, b), d, h, EAST_PURPLE, s, ox, oy)

    _quad_grid(draw, lambda a, b: (a, b, h), l, d, TOP_RED, s, ox, oy)


def draw_flat_grid(draw, cols, rows, body_color, top_rows, cell_box, pad=18):
    """Orthographic elevation: cols x rows cells, top `top_rows` rows in TOP_RED."""
    cx, cy, cw, ch = cell_box
    avail_w, avail_h = cw - 2 * pad, ch - 2 * pad
    cell_s = min(avail_w / cols, avail_h / rows)
    grid_w, grid_h = cols * cell_s, rows * cell_s
    ox, oy = cx + (cw - grid_w) / 2, cy + (ch - grid_h) / 2

    for r in range(rows):
        for c in range(cols):
            x0, y0 = ox + c * cell_s, oy + r * cell_s
            fill = TOP_RED if r < top_rows else body_color
            draw.rectangle([x0, y0, x0 + cell_s, y0 + cell_s], fill=fill, outline=OUTLINE)
