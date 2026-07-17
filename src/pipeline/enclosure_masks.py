#!/usr/bin/env python3
"""enclosure_masks.py — ROUND 4b mask redefinition (design/S4-REVIEW-
ROUNDS.md ROUND 4b, Lucas mid-run clarification): one `enclosure` mask per
module+view = the module's own LATERAL faces (stair profile-cap sides /
roof gable ends) projected at the SAME projection/scale/origin as the
module's own render, MINUS the module's own rendered silhouette (both
rasterised via face_masks.face_mask). The subtraction still matters even
though the lateral faces are real solid geometry: in an oblique dimetric
view the lateral faces' raw 2D footprint substantially overlaps the
render's own footprint (different 3D depths collapse onto the same screen
pixels), so plain projection alone would violate the "render ∩ mask ≈ ∅"
invariant. ROUND 4's bug was using a SYNTHETIC full-height wall-voxel
silhouette as the subtraction minuend (over-covers roof_cell/stairs, which
don't fill WALL_H, painting air in some views); ROUND 4b fixes that by
using the solid's own real lateral faces (`kit_modules.STAIR_LATERAL`/
"roof_edge") instead — a mask can never extend beyond the real solid.
Lateral faces are projected via kit_module_render.ordered_enclosure_faces
— deliberately NOT backface-culled (a lateral face contributes from both
sides by design; edge-on views correctly yield a near-empty mask). Only
called by stage_kit_modules.stage() for modules that have `Face.enclosure`
geometry at all (stair_45/stair_half/roof_cell)."""

from PIL import ImageChops

import face_masks as fm
import kit_module_render as kmr
import kit_modules as km
from scene_guide_render import Cam

LATERAL_TAGS = {km.STAIR_LATERAL, "roof_edge"}  # mask SOURCE tags — NOT
# kit_modules.STAIR_ENCLOSURE (stair back-wall/floor) or "roof_inset"
# (soffit): those stay real self-occlusion geometry but are never masked.
_ENCLOSURE_VALUE = fm.MASK_BASE + fm.MASK_STEP  # one undifferentiated group


def lateral_faces(module, view, s, cell_px, pad, origin):
    """[(face_id, kind, mat, screen_poly)] — this module's LATERAL faces
    only (the ROUND 4b mask source), projected at (view, s, origin) — the
    SAME per-view origin render_module already computed, so the mask lands
    pixel-aligned to the rendered panel. NOT backface-culled (`ordered_
    enclosure_faces` never culls) — a lateral face contributes from both
    sides by design."""
    faces = km.MODULES[module]()
    cam = Cam([], cell_px, cell_px, pad, scale=s, origin=origin)
    enc = kmr.ordered_enclosure_faces(faces, view, cam)
    return [(fid, k, m, poly) for fid, k, m, poly, tag in enc if tag in LATERAL_TAGS]


def _silhouette(ordered, size):
    idmap, _meta = fm.face_mask(ordered, size)
    return idmap.point(lambda p: 255 if p > 0 else 0)


def save_enclosure_masks(module, view, ordered, s, cell_px, pad, origin, masks_path):
    """Write `{module}_{view}_enclosure_facemask.png`/`_faces.json` — the
    gap between this module's projected LATERAL faces (ROUND 4b mask
    source) and its own render (`ordered`: its ordered_faces(...) output
    for `view`, post backface-cull). Writes nothing if there are no
    lateral faces at this view, or the gap is empty (render already covers
    the whole lateral footprint at this view — correct, not a bug)."""
    lateral = lateral_faces(module, view, s, cell_px, pad, origin)
    if not lateral:
        return
    size = (cell_px, cell_px)
    lat_sil = _silhouette(lateral, size)
    rendered = _silhouette(ordered, size)
    gap = ImageChops.subtract(lat_sil, rendered)  # binary images: lateral AND NOT rendered
    bbox = gap.getbbox()
    if bbox is None:
        return
    idmap = gap.point(lambda p: _ENCLOSURE_VALUE if p else 0)
    pixels = sum(1 for v in gap.getdata() if v)
    meta = {f"{module}:{view}:enclosure": {"color_idx": _ENCLOSURE_VALUE, "bbox": bbox, "pixels": pixels}}
    fm.save_mask(idmap, meta, masks_path / f"{module}_{view}_enclosure")
