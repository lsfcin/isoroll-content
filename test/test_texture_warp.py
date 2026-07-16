#!/usr/bin/env python3
"""test_texture_warp.py — homography/affine texture warp onto a projected
face (T2, C3/C4). Also exercises kit_module_render.project_face (T3, NEW
additive helper) since the corner-correspondence test needs a real yawed
screen_poly and project_face is the pinned public seam for that.

Seam: src/pipeline/texture_warp.py (T2) — does NOT exist yet on this branch,
and kit_module_render.project_face (T3) is additive-only and also does NOT
exist yet. `_tw()`/`_kmr()` import lazily (see test_texture_map.py's header
for the established reason: one clean FAILED per test, not a collection abort).

Seam decisions (documented, not pinned verbatim by 3-arch.md — if Loop 4b's
natural shape differs, raise `RETURN loop=4a reason=test-wrong`, don't
hand-edit these tests): `warp_tiling`/`warp_decal` are assumed to return a
canvas anchored at the SAME absolute coordinate origin as `screen_poly`
(not cropped-and-shifted to (0,0)) — stage_kit_modules' own prose says
paint_panel "warp_tiling; alpha-composite onto cell", which only works
directly if the tile shares the panel's coordinate frame.

World geometry is the REAL south side face of `kit_modules.MODULES["wall_band"]`
(edges emitted north/east/south/west after top/bottom -> index 2 of the
"side" faces is south, v=1) — matches 3-arch.md's own anti-mirror example
("south wall N=+y -> Ah=-x_hat"), independently re-derived by hand
(Ah = z_hat x N = z_hat x y_hat = -x_hat) before being pinned here.
"""

import math

from PIL import Image, ImageDraw

import kit_modules as km

CELL_PX, PAD, ORIGIN, S = 300, 0, (200.0, 200.0), 30.0


def _tw():
    import texture_warp
    return texture_warp


def _kmr():
    import kit_module_render
    return kit_module_render


def _side_faces():
    return [f for f in km.MODULES["wall_band"]() if f.kind == "side"]


def _gable_pts():
    # R2-3 (S4-REVIEW-ROUNDS.md ROUND 2, AMENDED 2026-07-16): roof_cell is
    # cover-only now — it no longer EMITS "gable" faces (gable becomes WALL
    # material composed at assembly, S4t), so no MODULES builder produces a
    # 3-corner face anymore. This synthetic triangle (same shape as the old
    # roof_cell gable end) keeps the AFFINE 3-corner warp path — still a
    # real, general texture_warp capability — under test.
    return [(-0.12, 0.0, 0.0), (-0.12, 1.0, 0.0), (0.0, 0.3, 0.7)]


def _solid_png(color, size=(20, 20)):
    return Image.new("RGBA", size, color + (255,))


def _corner_marked_png(marker=(255, 0, 0), base=(255, 255, 255), size=(40, 40), frac=0.25):
    img = Image.new("RGBA", size, base + (255,))
    mw, mh = int(size[0] * frac), int(size[1] * frac)
    for y in range(mh):
        for x in range(mw):
            img.putpixel((x, y), marker + (255,))
    return img


def _dot(p, axis):
    return sum(a * b for a, b in zip(p, axis))


def _color_dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a[:3], b[:3])) ** 0.5


def _sample_toward(img, poly, k, frac=0.8):
    """Point `frac` from poly's centroid to poly[k] — inside that corner's
    region, clear of rasterization/AA edge noise at the exact vertex."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    px, py = poly[k]
    return img.getpixel((int(round(cx + (px - cx) * frac)), int(round(cy + (py - cy) * frac))))


def _mask_leaks(img, poly):
    """Fraction of pixels where img's alpha disagrees with an independent
    rasterization of poly — near-zero means "fills poly, mask-tight"."""
    ref = Image.new("L", img.size, 0)
    ImageDraw.Draw(ref).polygon(poly, fill=255)
    alpha = img.split()[-1]
    bad = sum(1 for a, m in zip(alpha.getdata(), ref.getdata()) if (a > 0) != bool(m))
    return bad / (img.size[0] * img.size[1])


# ---------------------------------------------------------------------- face_axes anti-mirror (pinned)
def test_face_axes_south_and_north_walls_have_opposite_chirality():
    tw = _tw()
    south, north = _side_faces()[2], _side_faces()[0]
    assert {round(v, 6) for _u, v, _z in south.pts} == {1.0}
    assert {round(v, 6) for _u, v, _z in north.pts} == {0.0}

    Ah_s, Av_s, _dh, _dv = tw.face_axes(south.pts)
    Ah_n, _av, _dh2, _dv2 = tw.face_axes(north.pts)
    assert tuple(round(c, 6) for c in Ah_s) == (-1.0, 0.0, 0.0)
    assert tuple(round(c, 6) for c in Av_s) == (0.0, 0.0, 1.0)
    assert tuple(round(c, 6) for c in Ah_n) == (1.0, 0.0, 0.0), "opposing walls must flip Ah"


# ---------------------------------------------------------------------- warp_tiling: solid fill, mask-tight (C3)
def test_warp_tiling_solid_png_fills_screen_poly_interior_and_leaves_outside_transparent():
    tw, kmr = _tw(), _kmr()
    pts = _side_faces()[2].pts
    poly = kmr.project_face(pts, "y45", S, CELL_PX, PAD, ORIGIN)
    tile = tw.warp_tiling(_solid_png((10, 20, 30)), pts, poly, dims_voxels=[1, 3, 0])
    assert tile.mode == "RGBA"
    assert _mask_leaks(tile, poly) < 0.01  # thin AA rim allowed, not open leakage


# ---------------------------------------------------------------------- warp_tiling: vertical repeat count (C3/C4)
def test_warp_tiling_wall_face_tiles_vertically_three_times_and_rep_count_is_scale_invariant():
    tw, kmr = _tw(), _kmr()
    pts = _side_faces()[2].pts  # WALL_H = 3.0, dims_voxels z-slot 0 -> falls back to 1.0/unit
    stripe = Image.new("RGBA", (10, 10), (255, 255, 255, 255))
    ImageDraw.Draw(stripe).rectangle([0, 0, 9, 4], fill=(0, 0, 0, 255))  # top half dark

    def _transitions(s, cell_px, origin):
        poly = kmr.project_face(pts, "y0", s, cell_px, PAD, origin)
        tile = tw.warp_tiling(stripe, pts, poly, dims_voxels=[1, 1, 0])
        cx = sum(p[0] for p in poly) / len(poly)
        y0, y1 = min(p[1] for p in poly) + 1, max(p[1] for p in poly) - 1
        lums = [0 if sum(tile.getpixel((int(cx), y))[:3]) / 3 < 128 else 1 for y in range(int(y0), int(y1))]
        return sum(1 for a, b in zip(lums, lums[1:]) if a != b)

    t_small = _transitions(S, CELL_PX, ORIGIN)
    t_large = _transitions(S * 2, CELL_PX * 2, (ORIGIN[0] * 2, ORIGIN[1] * 2))
    assert t_small == t_large, (t_small, t_large)
    assert t_small >= 4, "3 vertical repeats of a 2-band stripe must show >=4 light/dark transitions"


# ---------------------------------------------------------------------- warp_tiling: 3-corner AFFINE (gable)
def test_warp_tiling_handles_a_three_corner_gable_face_via_affine():
    tw, kmr = _tw(), _kmr()
    pts = _gable_pts()
    poly = kmr.project_face(pts, "y45", S, CELL_PX, PAD, ORIGIN)
    assert len(poly) == 3
    tile = tw.warp_tiling(_solid_png((5, 6, 7)), pts, poly, dims_voxels=[1, 1, 1])
    assert tile.mode == "RGBA"
    assert any(a > 0 for a in tile.split()[-1].getdata()), "AFFINE warp must paint something"


# ---------------------------------------------------------------------- corner correspondence, not mirrored (C3, the pinned-axes risk)
def test_warp_tiling_marks_the_same_physical_corner_across_two_different_yaws():
    tw, kmr = _tw(), _kmr()
    pts = _side_faces()[2].pts
    Ah, Av, _dh, _dv = tw.face_axes(pts)
    a_vals, b_vals = [_dot(p, Ah) for p in pts], [_dot(p, Av) for p in pts]
    min_a, max_b = min(a_vals), max(b_vals)
    # texture_warp maps this corner to texture-space (sx~=0, sy~=0) per
    # 3-arch.md's _texcoords formula — mark that corner and track it.
    marked_k = next(k for k in range(len(pts)) if math.isclose(a_vals[k], min_a, abs_tol=1e-9)
                     and math.isclose(b_vals[k], max_b, abs_tol=1e-9))

    marker, base = (255, 0, 0), (255, 255, 255)
    tex = _corner_marked_png(marker, base)
    for view in ("y45", "y225"):
        poly = kmr.project_face(pts, view, S, CELL_PX, PAD, ORIGIN)
        tile = tw.warp_tiling(tex, pts, poly, dims_voxels=[1, 3, 0])
        sample = _sample_toward(tile, poly, marked_k, frac=0.8)
        assert _color_dist(sample, marker) < _color_dist(sample, base), (view, sample)


# ---------------------------------------------------------------------- warp_decal: single placement, mask-tight
def test_warp_decal_places_exactly_one_copy_mask_tight_no_tiling():
    tw, kmr = _tw(), _kmr()
    world_quad = [(0.15, 1.0, 0.0), (0.85, 1.0, 0.0), (0.85, 1.0, 2.0), (0.15, 1.0, 2.0)]
    screen_quad = kmr.project_face(world_quad, "y45", S, CELL_PX, PAD, ORIGIN)
    decal = tw.warp_decal(_solid_png((1, 2, 3)), world_quad, screen_quad)
    assert decal.mode == "RGBA"
    assert _mask_leaks(decal, screen_quad) < 0.01
