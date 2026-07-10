#!/usr/bin/env python3
"""tile_guide_render.py — dimetric box-face geometry and single-panel drawing for tile guides."""

from PIL import Image, ImageDraw

from panel_geometry import (  # noqa: F401 — re-exported for callers/tests (tgr.*)
    MIN_THICK, TOP_FOLD_RATIO, PAD,
    _corner, _bbox, fit_scale, content_extent, panel_fit_scale,
)

# Grayscale value ramp by screen face-role (top / long / cap): a box shaded this
# way reads as lit-from-above, so any value that bleeds into NB output reinforces
# lighting. Front=back=FACE_LONG, both caps=FACE_CAP — identity is by label, not hue.
FACE_TOP    = (215, 215, 215)
FACE_LONG   = (140, 140, 140)
FACE_CAP    = (60, 60, 60)
# All layout linework is magenta — a non-gray key NB ignores and postproc keys out.
MAGENTA     = (255, 0, 255)
SILHOUETTE  = MAGENTA
GRID_LINE   = MAGENTA
SIL_WIDTH   = 5
GRID_WIDTH  = 2
# Orientation cue: dark band this wide (fraction of object width) on the pivot
# edge of a chiral tile, so its handedness is visible and NB stops mirror-flipping.
HINGE_BAND_FRAC = 0.16


def _origin_for_cell(l, d, h, cell_box, pad=PAD, s=None):
    cx, cy, cw, ch = cell_box
    avail_w, avail_h = cw - 2 * pad, ch - 2 * pad
    if s is None:
        s = fit_scale(l, d, h, avail_w, avail_h)
    minx, maxx, miny, maxy = _bbox(l, d, h)
    ox = pad - minx * s + (avail_w - (maxx - minx) * s) / 2
    oy = pad - miny * s + (avail_h - (maxy - miny) * s) / 2
    return s, ox, oy


def _scr(uvz_fn, a, b, s, ox, oy):
    u, v, z = uvz_fn(a, b)
    x, y = _corner(u, v, z)
    return ox + x * s, oy + y * s


def _quad_poly(uvz_fn, sa, sb, s, ox, oy):
    return [_scr(uvz_fn, 0, 0, s, ox, oy), _scr(uvz_fn, sa, 0, s, ox, oy),
            _scr(uvz_fn, sa, sb, s, ox, oy), _scr(uvz_fn, 0, sb, s, ox, oy)]


def _quad_fill(draw, uvz_fn, sa, sb, color, s, ox, oy):
    draw.polygon(_quad_poly(uvz_fn, sa, sb, s, ox, oy), fill=color)


def _quad_stroke(draw, uvz_fn, sa, sb, s, ox, oy):
    poly = _quad_poly(uvz_fn, sa, sb, s, ox, oy)
    draw.line(poly + [poly[0]], fill=SILHOUETTE, width=SIL_WIDTH, joint="curve")
    for a in range(1, sa):
        draw.line([_scr(uvz_fn, a, 0, s, ox, oy), _scr(uvz_fn, a, sb, s, ox, oy)], fill=GRID_LINE, width=GRID_WIDTH)
    for b in range(1, sb):
        draw.line([_scr(uvz_fn, 0, b, s, ox, oy), _scr(uvz_fn, sa, b, s, ox, oy)], fill=GRID_LINE, width=GRID_WIDTH)


def _draw_band(draw, l, d, h, is_east, s, ox, oy):
    du = HINGE_BAND_FRAC * l
    u0 = (l - du) if is_east else 0.0
    poly = []
    for u, z in ((u0, 0), (u0 + du, 0), (u0 + du, h), (u0, h)):
        x, y = _corner(u, d, z)
        poly.append((ox + x * s, oy + y * s))
    draw.polygon(poly, fill=FACE_CAP)


def draw_iso_panel(img, l, d, h, view, cell_box, pad=PAD, mark_edge=False, s=None):
    """One dimetric box view (NW/NE/SW/SE). NE/SW use the base geometry; NW/SE
    h-flip it (mirror of a valid hexagon stays valid). A zero dim leaves a single
    flat quad (leaf). Faces fill first, then the optional orientation band, then
    magenta strokes on top — so layout linework stays crisp over the band. With
    mark_edge, the band marks the pivot edge (screen-left front / -right back).
    s=None autofits (byte-identical to the legacy path); otherwise draws at the
    forced px-per-voxel scale. Returns the content's GEOMETRIC px-bbox (polygon
    extremes, not silhouette-stroke pixels), sheet-absolute."""
    is_north = "N" in view
    is_east = "E" in view
    needs_mirror = is_north != is_east
    cx, cy, cw, ch = cell_box
    scratch = Image.new("RGB", (cw, ch), (0, 0, 0))
    sdraw = ImageDraw.Draw(scratch)
    s, ox, oy = _origin_for_cell(l, d, h, (0, 0, cw, ch), pad, s)

    faces = []
    if l > 0 and h > 0:
        faces.append((lambda a, b: (a, d, b), l, h, FACE_LONG))
    if d > 0 and h > 0:
        faces.append((lambda a, b: (l, a, b), d, h, FACE_CAP))
    if l > 0 and d > 0:
        faces.append((lambda a, b: (a, b, h), l, d, FACE_TOP))
    for fn, sa, sb, color in faces:
        _quad_fill(sdraw, fn, sa, sb, color, s, ox, oy)
    if mark_edge and l > 0 and h > 0:
        _draw_band(sdraw, l, d, h, is_east, s, ox, oy)
    for fn, sa, sb, _color in faces:
        _quad_stroke(sdraw, fn, sa, sb, s, ox, oy)

    minx, maxx, miny, maxy = _bbox(l, d, h)
    x0, y0, x1, y1 = ox + minx * s, oy + miny * s, ox + maxx * s, oy + maxy * s

    if needs_mirror:
        scratch = scratch.transpose(Image.FLIP_LEFT_RIGHT)
        x0, x1 = cw - x1, cw - x0
    img.paste(scratch, (cx, cy))
    return (x0 + cx, y0 + cy, x1 + cx, y1 + cy)


def draw_square_grid(draw, cols, rows, color, cell_box, pad=PAD, s=None):
    """Orthographic plan view (TOP, straight down); each cell a square. A zero on
    either axis renders a thin MIN_THICK bar instead of collapsing to a line, so a
    flat plane (door leaf, shutter) keeps a minimal visible thickness from above.
    s=None autofits; otherwise draws at the forced px-per-voxel scale. Returns the
    sheet-absolute content px-bbox."""
    cx, cy, cw, ch = cell_box
    avail_w, avail_h = cw - 2 * pad, ch - 2 * pad
    cols_u = cols if cols > 0 else MIN_THICK
    rows_u = rows if rows > 0 else MIN_THICK
    cell_s = s if s is not None else min(avail_w / cols_u, avail_h / rows_u)
    grid_w, grid_h = cols_u * cell_s, rows_u * cell_s
    ox = cx + (cw - grid_w) / 2
    oy = cy + (ch - grid_h) / 2

    draw.rectangle([ox, oy, ox + grid_w, oy + grid_h], fill=color)
    for c in range(1, cols):
        x = ox + c * cell_s
        draw.line([(x, oy), (x, oy + grid_h)], fill=GRID_LINE, width=GRID_WIDTH)
    for r in range(1, rows):
        y = oy + r * cell_s
        draw.line([(ox, y), (ox + grid_w, y)], fill=GRID_LINE, width=GRID_WIDTH)
    draw.rectangle([ox, oy, ox + grid_w, oy + grid_h], outline=SILHOUETTE, width=SIL_WIDTH)
    return (ox, oy, ox + grid_w, oy + grid_h)


def draw_flat_grid(draw, cols, rows, body_color, top_rows, cell_box, pad=PAD, s=None):
    """Orthographic elevation, unfolded-net style: the top `top_rows` rows are the
    TOP face folded flat above the body (FACE_TOP), shorter by TOP_FOLD_RATIO.
    s=None autofits; otherwise draws at the forced px-per-voxel scale. Returns the
    sheet-absolute content px-bbox."""
    cx, cy, cw, ch = cell_box
    avail_w, avail_h = cw - 2 * pad, ch - 2 * pad
    body_rows = rows - top_rows
    row_units = body_rows + top_rows * TOP_FOLD_RATIO
    cell_s = s if s is not None else min(avail_w / cols, avail_h / row_units)
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
            fill = FACE_TOP if r < top_rows else body_color
            draw.rectangle([x0, y0, x0 + cell_s, y1], fill=fill)
    for c in range(cols + 1):
        x = ox + c * cell_s
        draw.line([(x, oy), (x, oy + grid_h)], fill=GRID_LINE, width=GRID_WIDTH)
    for r in range(rows + 1):
        y = row_y(r)
        draw.line([(ox, y), (ox + grid_w, y)], fill=GRID_LINE, width=GRID_WIDTH)
    draw.rectangle([ox, oy, ox + grid_w, oy + grid_h], outline=SILHOUETTE, width=SIL_WIDTH)
    return (ox, oy, ox + grid_w, oy + grid_h)
