#!/usr/bin/env python3
"""texture_warp.py — warp a texture PNG onto a projected face quad/tri (T2,
C3/C4). The geometric core: world-absolute texcoords (never index maps) +
PIL PERSPECTIVE/AFFINE to paint a screen polygon. PINNED AXES per 3-arch.md.

`world_pts` and `screen_poly` are always index-aligned (same corner order —
see kit_module_render.project_face / ordered_faces), so corner
correspondence between texture space and screen space is by INDEX, never a
hand-authored map."""

import math

import numpy as np
from PIL import Image, ImageDraw

import texture_resample as tr


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _normalize(v):
    mag = sum(c * c for c in v) ** 0.5
    if mag < 1e-12:
        return (0.0, 0.0, 0.0)
    return tuple(c / mag for c in v)


def _dot(p, axis):
    return sum(a * b for a, b in zip(p, axis))


def _face_normal(world_pts):
    p0, p1, p2 = world_pts[0], world_pts[1], world_pts[2]
    v1 = tuple(b - a for a, b in zip(p0, p1))
    v2 = tuple(b - a for a, b in zip(p0, p2))
    return _normalize(_cross(v1, v2))


def face_axes(world_pts):
    """(Ah, Av, dims_h, dims_v) — Ah/Av are the pinned world-space texture
    axes (anti-mirror rule, 3-arch.md). `dims_h`/`dims_v` here are 1.0
    placeholders: the REAL per-axis world-units-per-tile only exists once a
    face's actual `dims_voxels` is known, which callers (warp_tiling)
    resolve themselves via `_resolve_dim` — kept as a 4-tuple to match the
    pinned signature."""
    N = _face_normal(world_pts)
    absz = abs(N[2])
    z_hat = (0.0, 0.0, 1.0)

    if absz > 0.9:  # HORIZONTAL: top/bottom/tread/floor
        Ah, Av = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)
    elif absz < 0.1:  # VERTICAL: side/riser/wall
        Av = z_hat
        Ah = _normalize(_cross(z_hat, N))
    else:  # SLOPED: roof slope quads AND gable tris
        Ah = _normalize(_cross(z_hat, N))
        Av = _normalize(_cross(N, Ah))
        if Av[2] < 0:
            Av = tuple(-c for c in Av)

    return Ah, Av, 1.0, 1.0


def _resolve_dim(dims_voxels, axis):
    """dims_voxels[argmax|axis_xyz|] or 1.0 (3-arch.md) — the world-units
    one texture tile spans along `axis`. A 0/falsy slot (the axis the
    texture doesn't numerically constrain) falls back to 1 world-unit/tile."""
    if not dims_voxels:
        return 1.0
    idx = max(range(3), key=lambda i: abs(axis[i]))
    return dims_voxels[idx] or 1.0


def _texcoords(world_pts, Ah, Av, dims_h, dims_v, src_w, src_h):
    """[(sx,sy)] per corner, in pixels of the (to-be-tiled) source canvas.
    Absolute-world `a`/`b` (never face-local) is what gives adjacent voxels
    continuous phase (C3). sx/sy are >=0 by construction."""
    a_vals = [_dot(p, Ah) / dims_h for p in world_pts]
    b_vals = [_dot(p, Av) / dims_v for p in world_pts]
    min_a = math.floor(min(a_vals))
    max_b = math.ceil(max(b_vals))
    return [((a - min_a) * src_w, (max_b - b) * src_h) for a, b in zip(a_vals, b_vals)]


def _decal_texcoords(world_pts, Ah, Av, src_w, src_h):
    """[(sx,sy)] mapping world_pts onto the FULL source image exactly once
    (min/max-normalized within the quad itself) — no tiling, no wrap."""
    a_vals = [_dot(p, Ah) for p in world_pts]
    b_vals = [_dot(p, Av) for p in world_pts]
    min_a, max_a = min(a_vals), max(a_vals)
    min_b, max_b = min(b_vals), max(b_vals)
    span_a = (max_a - min_a) or 1.0
    span_b = (max_b - min_b) or 1.0
    return [(((a - min_a) / span_a) * src_w, ((max_b - b) / span_b) * src_h)
            for a, b in zip(a_vals, b_vals)]


def _perspective_coeffs(dst_pts, src_pts):
    """8 coeffs for Image.transform(..., PERSPECTIVE, coeffs): PIL evaluates
    the coeffs AT the OUTPUT (dst) pixel to find the INPUT (src) pixel to
    sample, so the linear system is built in dst variables with src as the
    RHS — standard 4-point homography solve."""
    matrix = []
    for (x, y), (u, v) in zip(dst_pts, src_pts):
        matrix.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        matrix.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    a = np.array(matrix, dtype=np.float64)
    b = np.array(src_pts, dtype=np.float64).reshape(8)
    # lstsq (not solve): an edge-on/degenerate screen quad (zero-area at some
    # yaw) makes the exact system singular; least-squares still returns a
    # finite best-fit instead of raising — that face just paints ~nothing
    # visible either way (mask-tight to the same near-zero-area poly).
    return tuple(np.linalg.lstsq(a, b, rcond=None)[0])


def _affine_coeffs(dst_pts, src_pts):
    """6 coeffs for Image.transform(..., AFFINE, coeffs) — exact 3-point solve
    (3-corner gable faces, C-arch AFFINE path)."""
    (x0, y0), (x1, y1), (x2, y2) = dst_pts
    (u0, v0), (u1, v1), (u2, v2) = src_pts
    a = np.array([
        [x0, y0, 1, 0, 0, 0],
        [0, 0, 0, x0, y0, 1],
        [x1, y1, 1, 0, 0, 0],
        [0, 0, 0, x1, y1, 1],
        [x2, y2, 1, 0, 0, 0],
        [0, 0, 0, x2, y2, 1],
    ], dtype=np.float64)
    b = np.array([u0, v0, u1, v1, u2, v2], dtype=np.float64)
    return tuple(np.linalg.lstsq(a, b, rcond=None)[0])


def _apply_polygon_mask(img, poly):
    """Alpha = polygon coverage, not blended with the resample's own alpha —
    matches face_masks.py's ImageDraw.polygon rasterization exactly (C7)."""
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).polygon([tuple(p) for p in poly], fill=255)
    img.putalpha(mask)
    return img


def _warp_to_screen(source_img, src_corners, dst_poly):
    """Warp `source_img` so `src_corners[k]` lands at `dst_poly[k]` (index
    correspondence), returned as an RGBA canvas anchored at absolute (0,0) —
    the SAME coordinate frame `dst_poly` itself is already in — masked
    mask-tight to `dst_poly`'s interior. PERSPECTIVE for 4 corners, AFFINE
    for 3 (gable faces). R2-1 (design/S4-REVIEW-ROUNDS.md ROUND 2): routed
    through `tr.supersample_transform` (2x supersample, BICUBIC, then
    LANCZOS-downsample) instead of a single BICUBIC sample at output
    resolution — warp stair-stepping on oblique yaws was the actual
    remaining aliasing source after the P2 resolution/density-guard pass."""
    out_w = int(math.ceil(max(p[0] for p in dst_poly))) + 1
    out_h = int(math.ceil(max(p[1] for p in dst_poly))) + 1
    if len(dst_poly) == 3:
        warped = tr.supersample_transform(source_img, Image.Transform.AFFINE, (out_w, out_h),
                                           _affine_coeffs, dst_poly, src_corners)
    else:
        warped = tr.supersample_transform(source_img, Image.Transform.PERSPECTIVE, (out_w, out_h),
                                           _perspective_coeffs, dst_poly, src_corners)
    return _apply_polygon_mask(warped, dst_poly)


def warp_tiling(tex_img, world_pts, screen_poly, dims_voxels):
    """RGBA cell tile: axes -> texcoords -> tile tex_img -> density-match
    (P2: tr.match_source_density, so the warp never magnifies a too-small
    source) -> map tiled-source corners onto screen_poly (PERSPECTIVE/
    AFFINE) -> mask to screen_poly."""
    tex_img = tex_img.convert("RGBA")
    Ah, Av, _dh, _dv = face_axes(world_pts)
    dims_h = _resolve_dim(dims_voxels, Ah)
    dims_v = _resolve_dim(dims_voxels, Av)
    src_w, src_h = tex_img.size
    texcoords = _texcoords(world_pts, Ah, Av, dims_h, dims_v, src_w, src_h)
    canvas_w = max(1, math.ceil(max(c[0] for c in texcoords)))
    canvas_h = max(1, math.ceil(max(c[1] for c in texcoords)))
    tiled = tr.tile_source(tex_img, canvas_w, canvas_h)
    tiled, texcoords = tr.match_source_density(tiled, texcoords, screen_poly)
    return _warp_to_screen(tiled, texcoords, screen_poly)


def warp_decal(tex_img, world_quad, screen_quad):
    """RGBA: same corner machinery (reuses face_axes for the anti-mirror
    chirality), but `dims_voxels` is the opening's own world extent -> exactly
    1 tile, source NOT tiled/wrapped (outside the source -> transparent).
    Density-matched (P2) same as warp_tiling."""
    tex_img = tex_img.convert("RGBA")
    Ah, Av, _dh, _dv = face_axes(world_quad)
    src_w, src_h = tex_img.size
    texcoords = _decal_texcoords(world_quad, Ah, Av, src_w, src_h)
    tex_img, texcoords = tr.match_source_density(tex_img, texcoords, screen_quad)
    return _warp_to_screen(tex_img, texcoords, screen_quad)
