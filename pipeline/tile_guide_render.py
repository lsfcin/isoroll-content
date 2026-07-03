#!/usr/bin/env python3
"""tile_guide_render.py — dimetric box-face geometry and single-panel drawing for tile guides."""

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
# uz = 2*uy on purpose (standard "full tile height" convention) — this is only
# safe because draw_iso_panel mirrors u/v per view (see _view_axes); the naive
# single-quadrant formula makes opposite box corners coincide otherwise.
_UX, _UY, _UZ = 1.0, 0.5, 1.0


def _corner(u, v, z):
    x = (u - v) * _UX
    y = (u + v) * _UY - z * _UZ
    return x, y


def _view_axes(view, l, d):
    """Mirror u/v per diagonal view so the visible side faces always sit at
    the 'max' end of their local axis — the only configuration this
    projection renders without the two side faces overlapping (verified
    numerically: north+east is clean, the other 3 raw combos are not)."""
    flip_u = "W" in view
    flip_v = "S" in view

    def tr(u, v):
        return (l - u if flip_u else u), (d - v if flip_v else v)

    return tr


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
    draw.polygon(poly, fill=color)
    draw.line(poly + [poly[0]], fill=SILHOUETTE, width=SIL_WIDTH, joint="curve")
    for a in range(1, steps_a):
        draw.line([scr(a, 0), scr(a, steps_b)], fill=GRID_LINE, width=GRID_WIDTH)
    for b in range(1, steps_b):
        draw.line([scr(0, b), scr(steps_a, b)], fill=GRID_LINE, width=GRID_WIDTH)


def draw_iso_panel(draw, l, d, h, view, cell_box, pad=18):
    """One 3-face dimetric box view. view in {NW, NE, SW, SE}."""
    s, ox, oy = _origin_for_cell(l, d, h, cell_box, pad)
    tr = _view_axes(view, l, d)
    north = view in ("NW", "NE")
    west = view in ("NW", "SW")
    ns_color = BACK_GRAY if north else FRONT_GREEN
    ew_color = WEST_BLUE if west else EAST_PURPLE
    ns_v = d if north else 0
    ew_u = 0 if west else l

    def ns_uvz(a, b):
        u, v = tr(a, ns_v)
        return u, v, b

    def ew_uvz(a, b):
        u, v = tr(ew_u, a)
        return u, v, b

    def top_uvz(a, b):
        u, v = tr(a, b)
        return u, v, h

    _quad_grid(draw, ns_uvz, l, h, ns_color, s, ox, oy)
    _quad_grid(draw, ew_uvz, d, h, ew_color, s, ox, oy)
    _quad_grid(draw, top_uvz, l, d, TOP_RED, s, ox, oy)


def draw_flat_grid(draw, cols, rows, body_color, top_rows, cell_box, pad=18):
    """Orthographic elevation, unfolded-net style: cols x rows cells, the top
    `top_rows` rows are the TOP face folded flat above the body (TOP_RED)."""
    cx, cy, cw, ch = cell_box
    avail_w, avail_h = cw - 2 * pad, ch - 2 * pad
    cell_s = min(avail_w / cols, avail_h / rows)
    grid_w, grid_h = cols * cell_s, rows * cell_s
    ox, oy = cx + (cw - grid_w) / 2, cy + (ch - grid_h) / 2

    for r in range(rows):
        for c in range(cols):
            x0, y0 = ox + c * cell_s, oy + r * cell_s
            fill = TOP_RED if r < top_rows else body_color
            draw.rectangle([x0, y0, x0 + cell_s, y0 + cell_s], fill=fill)
    for c in range(cols + 1):
        x = ox + c * cell_s
        draw.line([(x, oy), (x, oy + grid_h)], fill=GRID_LINE, width=GRID_WIDTH)
    for r in range(rows + 1):
        y = oy + r * cell_s
        draw.line([(ox, y), (ox + grid_w, y)], fill=GRID_LINE, width=GRID_WIDTH)
    draw.rectangle([ox, oy, ox + grid_w, oy + grid_h], outline=SILHOUETTE, width=SIL_WIDTH)
