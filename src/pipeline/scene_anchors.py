#!/usr/bin/env python3
"""scene_anchors.py — stable 3D anchors on layout geometry, projected per view; attached registration marks."""

from PIL import Image, ImageDraw

from guide_marks import CYAN, MarkParams, SYMBOLS
from layout_parse import DOOR, SOLID, STAIRS, WINDOW, rotate_cw, rotate_point
from scene_guide_render import VIEW_TURNS, scene_cam

RUN_EVERY = 3  # one mid-run anchor every N straight wall cells


def _solid(layout, u, v):
    return layout.kind(u, v) in SOLID


def _is_corner(layout, u, v):
    """Corner/joint cell: solid neighbors on both axes (L-join) or on neither (pillar)."""
    horizontal = _solid(layout, u - 1, v) or _solid(layout, u + 1, v)
    vertical = _solid(layout, u, v - 1) or _solid(layout, u, v + 1)
    return horizontal == vertical


def anchors(layout):
    """[(id, u, v, z)] in layout coords (z in voxels). Same physical point in every view."""
    pts = []
    run_count = 0
    for v in range(layout.rows):
        for u in range(layout.cols):
            ch = layout.kind(u, v)
            if ch == DOOR:
                pts.append((f"door{u}-{v}", u + 0.5, v + 0.5, 1.0))
            elif ch == WINDOW:
                pts.append((f"win{u}-{v}", u + 0.5, v + 0.5, 1.5))
            elif ch in STAIRS:
                pts.append((f"stair{u}-{v}", u + 0.5, v + 0.5, 1.0))
            elif ch in SOLID and _is_corner(layout, u, v):
                pts.append((f"cor{u}-{v}", u + 0.5, v + 0.5, float(layout.wall_h)))
            elif ch in SOLID:
                run_count += 1
                if run_count % RUN_EVERY == 0:
                    pts.append((f"run{u}-{v}", u + 0.5, v + 0.5, float(layout.wall_h)))
    return pts


def project(layout, view, size, pad=24):
    """Anchor screen positions inside one iso panel: [(id, x, y)], panel-local pixels."""
    turns = VIEW_TURNS[view]
    turned = rotate_cw(layout, turns)
    cam = scene_cam(turned, size, pad)
    out = []
    for aid, u, v, z in anchors(layout):
        ru, rv = rotate_point(u, v, layout.rows, layout.cols, turns)
        x, y = cam.pt(ru, rv, z)
        out.append((aid, x, y))
    return out


def _stable_symbols(ids):
    ordered = sorted(set(ids))
    return {aid: SYMBOLS[i % len(SYMBOLS)] for i, aid in enumerate(ordered)}


def apply_anchored(img, panel_specs, params=None):
    """panel_specs: [(view, (x0, y0, w, h), [(id, px, py)])] — same id gets the same symbol in every panel."""
    params = params or MarkParams()
    all_ids = [aid for _v, _b, pts in panel_specs for aid, _x, _y in pts]
    sym_of = _stable_symbols(all_ids)
    out = img.convert("RGB")
    for view, (x0, y0, w, h), pts in panel_specs:
        if view in params.skip_views or not pts:
            continue
        region = out.crop((x0, y0, x0 + w, y0 + h))
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        radius = max(6, int(min(w, h) * params.radius_frac * 0.6))
        for aid, px, py in pts:
            sym_of[aid](draw, px, py, radius, CYAN + (255,), params.stroke)
        alpha = layer.getchannel("A")
        faded = alpha.point(lambda a: int(a * params.opacity))
        layer.putalpha(faded)
        merged = Image.alpha_composite(region.convert("RGBA"), layer).convert("RGB")
        out.paste(merged, (x0, y0))
    return out
