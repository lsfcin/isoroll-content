#!/usr/bin/env python3
"""texture_resample.py — resampling/density policy for texture_warp.py (P2,
design/S4-REVIEW-ROUNDS.md): BICUBIC everywhere the geometric transform
samples, plus a source-density guard so the perspective/affine warp is never
forced to magnify a too-small source (>=1 source px per destination px —
that's what read as noise on the old 64px-cell sheets). Split out of
texture_warp.py to stay under the per-file line gate; `tile_source` (source
tiling) lives here too since it's the thing the density guard operates on.

`supersample_transform` is the escalation path (2x supersample then LANCZOS
downsample) for when BICUBIC alone still shows visible stair-stepping on an
oblique yaw — wired in by texture_warp.py only where the P2 self-check
render actually needed it."""

from PIL import Image

RESAMPLE = Image.Resampling.BICUBIC
SUPERSAMPLE = 2


def tile_source(tex_img, canvas_w, canvas_h):
    """Repeat `tex_img` across a (canvas_w, canvas_h) RGBA canvas — the
    to-be-warped tiled source for warp_tiling."""
    src_w, src_h = tex_img.size
    canvas = Image.new("RGBA", (canvas_w, canvas_h))
    for y in range(0, canvas_h, src_h):
        for x in range(0, canvas_w, src_w):
            canvas.paste(tex_img, (x, y))
    return canvas


def match_source_density(source_img, texcoords, dst_poly):
    """Upscale `source_img` (BICUBIC) so it carries >=1 source px per output
    px along both extents of `dst_poly`'s screen footprint, rescaling
    `texcoords` to match. No-op (returned unchanged) if already dense
    enough — this only ever grows the source, never shrinks it here."""
    src_w, src_h = source_img.size
    dst_w = max(p[0] for p in dst_poly) - min(p[0] for p in dst_poly)
    dst_h = max(p[1] for p in dst_poly) - min(p[1] for p in dst_poly)
    scale = max(1.0, dst_w / max(src_w, 1), dst_h / max(src_h, 1))
    if scale <= 1.0:
        return source_img, texcoords
    new_size = (max(1, round(src_w * scale)), max(1, round(src_h * scale)))
    return source_img.resize(new_size, RESAMPLE), [(x * scale, y * scale) for x, y in texcoords]


def supersample_transform(source_img, method, size, coeffs_fn, dst_poly, src_pts):
    """Render `source_img.transform` at SUPERSAMPLE x resolution (BICUBIC)
    then LANCZOS-downsample to `size` — a stronger anti-alias pass than a
    single BICUBIC sample for faces at oblique yaws."""
    out_w, out_h = size
    big_size = (out_w * SUPERSAMPLE, out_h * SUPERSAMPLE)
    big_dst = [(x * SUPERSAMPLE, y * SUPERSAMPLE) for x, y in dst_poly]
    coeffs = coeffs_fn(big_dst, src_pts)
    warped = source_img.transform(big_size, method, coeffs, resample=RESAMPLE)
    return warped.resize(size, Image.Resampling.LANCZOS)
