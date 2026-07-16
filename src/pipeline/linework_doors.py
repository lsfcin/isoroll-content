#!/usr/bin/env python3
"""linework_doors.py — door decals for the /linework set (Lucas's door-sheet
vocabulary: 1x1x0, 1x2x0, 1x3x0, 2x2x0, 2x3x0).

Chirality: hinges ALWAYS on the left edge of a leaf (orientation-band rule);
double doors hinge on both outer edges, knobs at the center split."""

from linework import T, INK, STROKE, _head, _line

FRAME = 10


def _boards(x0, x1, y0, y1, n=5):
    s = [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="white" stroke="{INK}" stroke-width="{STROKE}"/>']
    step = (x1 - x0) / n
    for i in range(1, n):
        s.append(_line(x0 + i * step, y0, x0 + i * step, y1))
    return s


def _leaf(x0, x1, h, hinge_left):
    """One door leaf: frame, panel groups of vertical boards, hinges, knob."""
    s = [f'<rect x="{x0}" y="0" width="{x1-x0}" height="{h}" fill="white" stroke="{INK}" stroke-width="2.5"/>']
    n_panels = max(2, round(h / T))
    pad, gap = 14, 18
    panel_h = (h - 2 * pad - (n_panels - 1) * gap) / n_panels
    for i in range(n_panels):
        y0 = pad + i * (panel_h + gap)
        s += _boards(x0 + pad, x1 - pad, y0, y0 + panel_h)
    hx = x0 + 1.5 if hinge_left else x1 - 1.5
    for fy in (0.15, 0.5, 0.85):
        s.append(f'<rect x="{hx-3:.1f}" y="{h*fy-7:.1f}" width="6" height="14" fill="{INK}"/>')
    kx = x1 - pad + 4 if hinge_left else x0 + pad - 4
    ky = h * 0.52
    s.append(f'<circle cx="{kx:.1f}" cy="{ky-10:.1f}" r="4.5" fill="white" stroke="{INK}" stroke-width="{STROKE}"/>')
    s.append(f'<circle cx="{kx:.1f}" cy="{ky+4:.1f}" r="3.5" fill="{INK}"/>')
    return s


def door(w_vox, h_vox):
    w, h = w_vox * T, h_vox * T
    s = [_head(w, h)]
    if w_vox == 1:
        s += _leaf(0, w, h, hinge_left=True)
    else:
        s += _leaf(0, w / 2, h, hinge_left=True)
        s += _leaf(w / 2, w, h, hinge_left=False)
    return "".join(s) + "</svg>"


DOORS = {
    f"door_{w}x{h}x0": ((lambda w=w, h=h: door(w, h)), "decal", (w, h, 0))
    for w, h in ((1, 1), (1, 2), (1, 3), (2, 2), (2, 3))
}
