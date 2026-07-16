#!/usr/bin/env python3
"""linework_doors.py — door decals for the /linework set (Lucas's door-sheet
vocabulary: 1x1x0, 1x2x0, 1x3x0, 2x2x0, 2x3x0).

Lucas 2026-07-15 feedback baked in:
- Handle + keyhole sit at ~5 feet (= 1 voxel = T px from the door base);
  height-1 doors keep them in the upper third instead.
- Keyhole = circle partially occluding a thin triangle below it.
- Frame is twice as wide (hardware lives in the frame band, never conflicts
  with the panel boards).
- Chirality: hinges ALWAYS on the left edge of a leaf; double doors hinge on
  both outer edges, hardware at the center split.
"""

from linework import T, INK, STROKE, _head, _line

FRAME = 20


def _boards(x0, x1, y0, y1, n=5):
    s = [f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}" fill="white" stroke="{INK}" stroke-width="{STROKE}"/>']
    step = (x1 - x0) / n
    for i in range(1, n):
        s.append(_line(x0 + i * step, y0, x0 + i * step, y1))
    return s


def _hardware_y(h):
    """Vertical center of handle+keyhole: 5 feet (T px) above the base;
    upper third for height-1 doors."""
    return T * 0.3 if h <= T else h - T


def _hardware(kx, ky):
    """Handle (open circle) above a keyhole (circle occluding a thin
    triangle below it). Triangle first, circle drawn on top."""
    s = [f'<circle cx="{kx:.1f}" cy="{ky-12:.1f}" r="5" fill="white" stroke="{INK}" stroke-width="{STROKE}"/>',
         f'<polygon points="{kx-3.5:.1f},{ky+15.8:.1f} {kx+3.5:.1f},{ky+15.8:.1f} {kx:.1f},{ky+1.8:.1f}" fill="{INK}"/>',
         f'<circle cx="{kx:.1f}" cy="{ky+6:.1f}" r="4" fill="{INK}"/>']
    return s


def _leaf(x0, x1, h, hinge_left):
    """One door leaf: wide frame, panel groups of vertical boards, hinges,
    handle+keyhole centered in the frame band."""
    s = [f'<rect x="{x0:.1f}" y="0" width="{x1-x0:.1f}" height="{h}" fill="white" stroke="{INK}" stroke-width="2.5"/>']
    pad, gap = FRAME + 4, 18
    n_panels = max(2, round(h / T))
    panel_h = (h - 2 * pad - (n_panels - 1) * gap) / n_panels
    for i in range(n_panels):
        y0 = pad + i * (panel_h + gap)
        s += _boards(x0 + pad, x1 - pad, y0, y0 + panel_h)
    hx = x0 + 1.5 if hinge_left else x1 - 1.5
    for fy in (0.15, 0.5, 0.85):
        s.append(f'<rect x="{hx-3:.1f}" y="{h*fy-7:.1f}" width="6" height="14" fill="{INK}"/>')
    kx = x1 - pad / 2 if hinge_left else x0 + pad / 2
    s += _hardware(kx, _hardware_y(h))
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
