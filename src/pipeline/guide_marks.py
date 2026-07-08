#!/usr/bin/env python3
"""guide_marks.py — registration-mark post-pass over guide sheets (muralist technique, A/B parameterized)."""

import math
from dataclasses import dataclass, field

from PIL import Image, ImageChops, ImageDraw

CYAN = (0, 255, 255)  # key color like magenta: NB is told to ignore it, postproc can detect residue
BG_MAX = 12  # channel value at or below which a pixel counts as background


@dataclass
class MarkParams:
    scheme: str = "columns"  # "columns" (repeated per column) | "varied" (unique per anchor)
    back_mode: str = "occluded"  # "occluded" (only over background) | "faded" (alpha over everything)
    opacity: float = 0.85
    n_cols: int = 4
    radius_frac: float = 0.05
    stroke: int = 3
    back_views: set = field(default_factory=lambda: {"N", "NW", "NE"})
    skip_views: set = field(default_factory=lambda: {"CAPTION"})


def _pts(cx, cy, r, angles, scale=1.0):
    return [(cx + r * scale * math.sin(a), cy - r * scale * math.cos(a)) for a in angles]


def _sym_triangle(d, cx, cy, r, c, w):
    d.polygon(_pts(cx, cy, r, [0, 2.094, 4.189]), outline=c, width=w)


def _sym_circle(d, cx, cy, r, c, w):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=w)


def _sym_square(d, cx, cy, r, c, w):
    k = r * 0.85
    d.rectangle([cx - k, cy - k, cx + k, cy + k], outline=c, width=w)


def _sym_diamond(d, cx, cy, r, c, w):
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], outline=c, width=w)


def _sym_chevron(d, cx, cy, r, c, w):
    d.line([(cx - r, cy - r * 0.7), (cx, cy + r * 0.7), (cx + r, cy - r * 0.7)], fill=c, width=w, joint="curve")


def _sym_cross(d, cx, cy, r, c, w):
    k = r * 0.8
    d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=c, width=w)
    d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=c, width=w)


def _sym_star(d, cx, cy, r, c, w):
    angles = [i * math.pi / 5 for i in range(10)]
    pts = [_pts(cx, cy, r, [a], 1.0 if i % 2 == 0 else 0.45)[0] for i, a in enumerate(angles)]
    d.polygon(pts, outline=c, width=w)


SYMBOLS = [_sym_triangle, _sym_circle, _sym_square, _sym_diamond, _sym_chevron, _sym_cross, _sym_star]


def _symbol_layer(w, h, params):
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = max(6, int(min(w, h) * params.radius_frac))
    step_y = int(r * 2.6)
    xs = [int((i + 0.5) * w / params.n_cols) for i in range(params.n_cols)]
    for i, x in enumerate(xs):
        for j, y in enumerate(range(step_y, h - r, step_y)):
            idx = i if params.scheme == "columns" else (i + j * params.n_cols)
            SYMBOLS[idx % len(SYMBOLS)](d, x, y, r, CYAN + (255,), params.stroke)
    return layer


def _panel_alpha(layer, region, view, params):
    alpha = layer.getchannel("A")
    if view in params.back_views:
        alpha = alpha.point(lambda a: int(a * params.opacity))
        if params.back_mode == "occluded":
            bg_mask = region.convert("L").point(lambda p: 255 if p <= BG_MAX else 0)
            alpha = ImageChops.multiply(alpha, bg_mask)
    return alpha


def apply_marks(img, panels, params=None):
    """panels: iterable of (view, (x, y, w, h)) in sheet pixels. Returns a new RGB sheet."""
    params = params or MarkParams()
    out = img.convert("RGB")
    for view, (x, y, w, h) in panels:
        if view in params.skip_views:
            continue
        region = out.crop((x, y, x + w, y + h))
        layer = _symbol_layer(w, h, params)
        layer.putalpha(_panel_alpha(layer, region, view, params))
        merged = Image.alpha_composite(region.convert("RGBA"), layer).convert("RGB")
        out.paste(merged, (x, y))
    return out


def residue_count(img, tol=60):
    """QC: pixels still close to CYAN in an NB output (marks that leaked through)."""
    px = img.convert("RGB")
    r, g, b = px.split()
    near = lambda ch, target: ch.point(lambda p: 255 if abs(p - target) <= tol else 0)
    mask = ImageChops.multiply(ImageChops.multiply(near(r, 0), near(g, 255)), near(b, 255))
    return mask.histogram()[255]


def tile_panels(img, layout_name):
    """(view, box) list for a make_tile_guide sheet, derived from its LAYOUTS grid."""
    from make_tile_guide import LAYOUTS
    rows_kinds = LAYOUTS[layout_name]
    rows, cols = len(rows_kinds), len(rows_kinds[0])
    cw, ch = img.width // cols, img.height // rows
    return [(kind, (c * cw, r * ch, cw, ch))
            for r, row in enumerate(rows_kinds) for c, kind in enumerate(row)]


def main():
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description="Overlay registration marks on an existing tile-guide sheet.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--layout", default="6cell", help="make_tile_guide layout name")
    parser.add_argument("--scheme", choices=["columns", "varied"], default="columns")
    parser.add_argument("--back-mode", choices=["occluded", "faded"], default="occluded")
    parser.add_argument("--opacity", type=float, default=0.85)
    parser.add_argument("--n-cols", type=int, default=4)
    args = parser.parse_args()
    img = Image.open(args.input)
    params = MarkParams(scheme=args.scheme, back_mode=args.back_mode,
                        opacity=args.opacity, n_cols=args.n_cols)
    out = apply_marks(img, tile_panels(img, args.layout), params)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.save(args.output)
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
