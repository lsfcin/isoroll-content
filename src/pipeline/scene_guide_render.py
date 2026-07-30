#!/usr/bin/env python3
"""scene_guide_render.py — one guide panel of a whole scene: dimetric view of the massing boxes, or TOP plan."""

from PIL import Image, ImageDraw

from layout_massing import massing
from layout_parse import DOOR, FLOOR, SOLID, STAIRS, VOID, WINDOW, rotate_cw
from tile_guide_render import FACE_CAP, FACE_LONG, FACE_TOP, GRID_WIDTH, MAGENTA, SIL_WIDTH

# True rotation per view: the single-tile mirror trick would mirror the floor
# plan itself, so scenes re-run massing on a clockwise-rotated grid instead.
VIEW_TURNS = {"SW": 0, "SE": 1, "NE": 2, "NW": 3}
_UX, _UY, _UZ = 1.0, 0.5, 1.0  # 2:1 dimetric, same camera as tile_guide_render


def _proj(u, v, z):
    return (u - v) * _UX, (u + v) * _UY - z * _UZ


def _fit(boxes, avail_w, avail_h):
    if not boxes:
        # 3-arch.md Amendment (C5-seam+): defense for an all-void scene (no wall/floor/GRP boxes
        # at all) — min()/max() over an empty list would raise ValueError otherwise.
        return 1.0, avail_w / 2, avail_h / 2
    xs, ys = [], []
    for b in boxes:
        for u in (b.u0, b.u0 + b.l):
            for v in (b.v0, b.v0 + b.d):
                for z in (b.z0, b.z0 + b.h):
                    x, y = _proj(u, v, z)
                    xs.append(x)
                    ys.append(y)
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    s = min(avail_w / (maxx - minx or 1), avail_h / (maxy - miny or 1))
    ox = -minx * s + (avail_w - (maxx - minx) * s) / 2
    oy = -miny * s + (avail_h - (maxy - miny) * s) / 2
    return s, ox, oy


class Cam:
    """Dimetric camera: fit-to-panel by default, or fixed scale+origin for kit/assembly alignment."""

    def __init__(self, boxes, avail_w, avail_h, pad, scale=None, origin=None):
        if scale is None:
            self.s, ox, oy = _fit(boxes, avail_w - 2 * pad, avail_h - 2 * pad)
            self.ox, self.oy = ox + pad, oy + pad
        else:
            self.s = scale
            self.ox, self.oy = origin

    def pt(self, u, v, z):
        x, y = _proj(u, v, z)
        return self.ox + x * self.s, self.oy + y * self.s


def scene_cam(turned_layout, size, pad=24):
    """Fitted camera for a rotated layout — shared by panel render and anchor projection."""
    boxes = massing(turned_layout, merge=False)
    return Cam(boxes, size, size, pad)


def _quad(cam, fn, a0, a1, b0, b1):
    return [cam.pt(*fn(a0, b0)), cam.pt(*fn(a1, b0)), cam.pt(*fn(a1, b1)), cam.pt(*fn(a0, b1))]


def _faces(box):
    """Visible faces with this fixed camera: TOP, LONG (v=v0+d), CAP (u=u0+l).

    v2: z0 (base elevation, e.g. level_index * wall_h) offsets every z coordinate so stacked
    levels render at their real height instead of collapsing onto level 0 (T7)."""
    u0, v0, l, d, h, z0 = box.u0, box.v0, box.l, box.d, box.h, box.z0
    if l > 0 and d > 0:
        yield "top", (lambda a, b: (u0 + a, v0 + b, z0 + h)), l, d, FACE_TOP
    if l > 0 and h > 0:
        yield "long", (lambda a, b: (u0 + a, v0 + d, z0 + b)), l, h, FACE_LONG
    if d > 0 and h > 0:
        yield "cap", (lambda a, b: (u0 + l, v0 + a, z0 + b)), d, h, FACE_CAP


def _draw_openings(draw, cam, box, fn, face):
    """Exact-voxel through-holes on the run-axis face: door 1w x 2h from the floor, window 1x1 at z 1..2."""
    run_face = "long" if box.axis == "u" else "cap"
    if face != run_face:
        return
    for op in box.openings:
        a = op.offset
        if op.kind == "door":
            a0, a1, b0, b1 = a, a + 1, 0.0, min(2.0, box.h)
        else:
            a0, a1, b0, b1 = a, a + 1, min(1.0, box.h), min(2.0, box.h)
        poly = _quad(cam, fn, a0, a1, b0, b1)
        draw.polygon(poly, fill=(0, 0, 0))
        draw.line(poly + [poly[0]], fill=MAGENTA, width=GRID_WIDTH + 1, joint="curve")


def _stroke(draw, cam, fn, sa, sb, width):
    poly = _quad(cam, fn, 0, sa, 0, sb)
    draw.line(poly + [poly[0]], fill=MAGENTA, width=width, joint="curve")
    for a in range(1, int(sa) if sa == int(sa) else 0):
        draw.line([cam.pt(*fn(a, 0)), cam.pt(*fn(a, sb))], fill=MAGENTA, width=GRID_WIDTH)
    for b in range(1, int(sb) if sb == int(sb) else 0):
        draw.line([cam.pt(*fn(0, b)), cam.pt(*fn(sa, b))], fill=MAGENTA, width=GRID_WIDTH)


def render_boxes(boxes, size, pad=24, cam=None):
    """RGB panel on black from explicit boxes, painter-ordered by the caller's sort or here."""
    ordered = sorted(boxes, key=lambda b: (b.h > 0, b.u0 + b.v0))
    img = Image.new("RGB", (size[0], size[1]) if isinstance(size, tuple) else (size, size), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    if cam is None:
        cam = Cam(ordered, img.width, img.height, pad)
    for box in ordered:
        width = GRID_WIDTH if box.kind == "step" else SIL_WIDTH
        for face, fn, sa, sb, color in _faces(box):
            draw.polygon(_quad(cam, fn, 0, sa, 0, sb), fill=color)
            if box.kind == "wall":
                _draw_openings(draw, cam, box, fn, face)
            _stroke(draw, cam, fn, sa, sb, width)
    return img


def render_scene_panel(layout, view, size, pad=24):
    """Dimetric scene view (NW/NE/SW/SE) as an RGB image on black.

    Per-cell boxes + ground-first: exact painter's order on a grid (merged
    runs extending past a nearer flat produced cover-through slivers)."""
    turned = rotate_cw(layout, VIEW_TURNS[view])
    return render_boxes(massing(turned, merge=False), size, pad)


_PLAN_STAIR_RAMP = (110, 140, 170, 200)  # light toward the ascent


def render_plan_panel(layout, size, pad=24):
    """Orthographic TOP plan: floor light, walls mid, openings magenta-marked."""
    img = Image.new("RGB", (size, size), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    avail = size - 2 * pad
    cell = min(avail / max(layout.cols, 1), avail / max(layout.rows, 1))
    ox = (size - cell * layout.cols) / 2
    oy = (size - cell * layout.rows) / 2

    def rect(u, v, du=1.0, dv=1.0):
        return [ox + u * cell, oy + v * cell, ox + (u + du) * cell, oy + (v + dv) * cell]

    for v in range(layout.rows):
        for u in range(layout.cols):
            ch = layout.kind(u, v)
            if ch == VOID:
                continue
            if ch == FLOOR:
                draw.rectangle(rect(u, v), fill=FACE_TOP)
            elif ch in STAIRS:
                horizontal = ch in "<>"
                for i, tone in enumerate(_PLAN_STAIR_RAMP):
                    band = i if ch in ">v" else 3 - i
                    box = rect(u + band / 4, v, 0.25, 1) if horizontal else rect(u, v + band / 4, 1, 0.25)
                    draw.rectangle(box, fill=(tone, tone, tone))
            elif ch in SOLID:
                draw.rectangle(rect(u, v), fill=FACE_LONG)
                if ch == DOOR:
                    draw.rectangle(rect(u + 0.15, v + 0.15, 0.7, 0.7), fill=FACE_TOP, outline=MAGENTA, width=GRID_WIDTH)
                elif ch == WINDOW:
                    draw.rectangle(rect(u + 0.3, v + 0.3, 0.4, 0.4), outline=MAGENTA, width=GRID_WIDTH)
            draw.rectangle(rect(u, v), outline=MAGENTA, width=GRID_WIDTH)
    return img
