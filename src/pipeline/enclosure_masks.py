#!/usr/bin/env python3
"""enclosure_masks.py — one `enclosure` mask per module+view = the wall-fill
region behind/under a cover piece (stairs, roof) so assembly warps wall
texture into it and the piece reads solid.

Lucas 2026-07-18/19 (design/S4-REVIEW-ROUNDS.md ROUND 4c): the mask polygons
are the piece's OWN enclosure faces — the stair side caps + back wall, the
roof gable ends (kit_modules already carries them as `Face.enclosure`
geometry: the exact stair points + ground losange, so same scale by
construction). The mask is the UNION of those faces that are front-facing at
the view (kit_module_render.ordered_front_faces backface-culls). The cover
(treads/risers, roof slopes) is NOT subtracted: at assembly the cover sprite
composites ON TOP of the wall fill, so underlap is hidden and the sides can
never be eaten by a painter-order misorder against the cover — the failure of
the depth-composite and the earlier lateral-minus-render / air-above attempts.
Called by stage_kit_modules.stage() only for modules with enclosure geometry
(stair_45/stair_half/roof_cell)."""

import numpy as np
from PIL import Image, ImageDraw

import face_masks as fm
import kit_module_render as kmr
import kit_modules as km
from scene_guide_render import Cam

_ENCLOSURE_VALUE = fm.MASK_BASE + fm.MASK_STEP  # the mask's own paint value


def composite_enclosure(ordered_front, size):
    """Union of the FRONT-FACING enclosure faces (stair side caps + back wall,
    roof gables) projected — the wall-fill region for this view. The cover
    faces (treads/risers, roof slopes) are deliberately NOT subtracted: at
    assembly the module's cover sprite composites ON TOP of the wall fill, so
    any underlap is hidden and the sides can never be eaten by a painter-order
    misorder against the cover (which is what happened when we subtracted it).
    Returns a bool ndarray of the union pixels."""
    idmap = Image.new("L", size, 0)
    draw = ImageDraw.Draw(idmap)
    for _fid, _kind, _mat, poly, enc in ordered_front:
        if enc:
            draw.polygon(poly, fill=_ENCLOSURE_VALUE)
    arr = np.asarray(idmap)
    return arr == _ENCLOSURE_VALUE


def save_enclosure_masks(module, view, s, cell_px, pad, origin, masks_path):
    """Write `{module}_{view}_enclosure_facemask.png`/`_faces.json` — the
    depth-composited enclosure region for this view, recomputed from the same
    (view, s, origin) render_module used for the panel so it lands pixel-
    aligned. Writes nothing when no enclosure pixel survives (the cover fully
    occludes it — e.g. TOP and the edge-on yaws)."""
    size = (cell_px, cell_px)
    faces = km.MODULES[module]()
    cam = Cam([], cell_px, cell_px, pad, scale=s, origin=origin)
    ordered_front = kmr.ordered_front_faces(faces, view, cam)
    mask_arr = composite_enclosure(ordered_front, size)
    pixels = int(mask_arr.sum())
    if pixels == 0:
        return
    idmap = Image.fromarray(np.where(mask_arr, _ENCLOSURE_VALUE, 0).astype("uint8"), mode="L")
    bbox = idmap.getbbox()
    meta = {f"{module}:{view}:enclosure": {"color_idx": _ENCLOSURE_VALUE, "bbox": bbox, "pixels": pixels}}
    fm.save_mask(idmap, meta, masks_path / f"{module}_{view}_enclosure")
