#!/usr/bin/env python3
"""enclosure_masks.py — ROUND 4 mask redefinition (design/S4-REVIEW-
ROUNDS.md ROUND 4): one `enclosure` mask per module+view = the silhouette
of a full-height wall voxel occupying the module's footprint, at the SAME
projection/scale/origin as the module's own render, MINUS the module's own
rendered silhouette (both post-backface-cull, via kit_module_render.
ordered_faces — the same polygon-fill rasterisation face_masks.py already
uses for the render-visible masks, so this is exact, not an approximation).
Drops the old per-Face-tag emission (stair_enclosure/roof_edge/roof_inset
split) — `Face.enclosure` geometry stays real (self-occlusion/silhouette)
but is no longer the mask SOURCE. Only called by stage_kit_modules.stage()
for modules that have `Face.enclosure` geometry at all (stair_45/
stair_half/roof_cell); wall_band/base/... never call this."""

from PIL import ImageChops

import face_masks as fm
import kit_module_render as kmr
import kit_modules as km
from scene_guide_render import Cam

_ENCLOSURE_VALUE = fm.MASK_BASE + fm.MASK_STEP  # one undifferentiated group


def _wall_voxel_faces():
    return km.extrude(km.UNIT_SQUARE, 0.0, km.WALL_H)


def _silhouette(ordered, size):
    idmap, _meta = fm.face_mask(ordered, size)
    return idmap.point(lambda p: 255 if p > 0 else 0)


def voxel_silhouette(view, s, cell_px, pad, origin):
    """Binary "L" silhouette of a full-height wall voxel at (view, s,
    origin) — the SAME projection a module's own panel was rendered with,
    so it lands pixel-aligned. Public: the ROUND-4 invariant test compares
    against it directly."""
    cam = Cam([], cell_px, cell_px, pad, scale=s, origin=origin)
    ordered = kmr.ordered_faces(_wall_voxel_faces(), view, cam)
    return _silhouette(ordered, (cell_px, cell_px))


def save_enclosure_masks(module, view, ordered, s, cell_px, pad, origin, masks_path):
    """Write `{module}_{view}_enclosure_facemask.png` / `_faces.json` — the
    gap between `voxel_silhouette` and this module's own render (`ordered`:
    its ordered_faces(...) output for `view`, post backface-cull). Writes
    nothing if the gap is empty (the module's own render already fills the
    whole voxel footprint at this view)."""
    size = (cell_px, cell_px)
    voxel = voxel_silhouette(view, s, cell_px, pad, origin)
    rendered = _silhouette(ordered, size)
    gap = ImageChops.subtract(voxel, rendered)  # binary images: voxel AND NOT rendered
    bbox = gap.getbbox()
    if bbox is None:
        return
    idmap = gap.point(lambda p: _ENCLOSURE_VALUE if p else 0)
    pixels = sum(1 for v in gap.getdata() if v)
    meta = {f"{module}:{view}:enclosure": {"color_idx": _ENCLOSURE_VALUE, "bbox": bbox, "pixels": pixels}}
    fm.save_mask(idmap, meta, masks_path / f"{module}_{view}_enclosure")
