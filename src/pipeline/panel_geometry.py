#!/usr/bin/env python3
"""panel_geometry.py — pure dimetric/orthographic geometry math shared by
tile_guide_render.py (drawing) and sheet_qc.py (QC): unit-scale corner
offsets, content bbox, and per-panel content extent / autofit scale. No PIL
here on purpose — split out of tile_guide_render.py to stay under the repo's
per-file size gate as scale-consistency (T2-T6) grows both modules.
"""

# Unit-scale corner offsets (2:1 dimetric — 26.57°). Real pixels = these * s.
_UX, _UY, _UZ = 1.0, 0.5, 1.0

# Flat object (one zero dim) keeps this thickness (fraction of a cell) in TOP view.
MIN_THICK = 0.18
TOP_FOLD_RATIO = _UY / _UZ

# Default cell padding (px), shared by every panel's autofit + forced-scale path.
PAD = 18


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


def content_extent(orientation, w, d, h):
    """Voxel-unit content dims (w_u, h_u) for one panel — single source shared
    by draw (autofit) and QC (expected-extent) sides. Dispatch mirrors
    draw_panel's w/d/h -> cols/rows mapping in tile_guide_matrix — do NOT
    swap N/S vs W/E."""
    if orientation in ("NW", "NE", "SW", "SE"):
        minx, maxx, miny, maxy = _bbox(w, d, h)
        return maxx - minx, maxy - miny
    if orientation == "TOP":
        return (w or MIN_THICK), (d or MIN_THICK)
    if orientation in ("N", "S"):
        return w, h + d * TOP_FOLD_RATIO
    if orientation in ("W", "E"):
        return d, h + w * TOP_FOLD_RATIO
    raise ValueError(f"content_extent: unsupported orientation {orientation!r}")


def panel_fit_scale(orientation, w, d, h, cell_px, pad=PAD):
    """Autofit px-per-voxel scale for one panel at cell_px, using content_extent."""
    w_u, h_u = content_extent(orientation, w, d, h)
    avail = cell_px - 2 * pad
    return min(avail / (w_u or 1), avail / (h_u or 1))
