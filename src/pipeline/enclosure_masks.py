#!/usr/bin/env python3
"""enclosure_masks.py — ROUND 3 mask-only face emission (design/S4-REVIEW-
ROUNDS.md ROUND 3): stripped stair/roof enclosure faces (stair_enclosure /
roof_edge / roof_inset) are never painted but stay real kit_modules
geometry — this module groups kit_module_render.ordered_enclosure_faces'
output by tag and emits one facemask PNG/JSON pair per (module, view, tag)
through the existing face_masks machinery, staged alongside the
render-visible masks stage_kit_modules.stage already writes."""

import face_masks as fm


def save_enclosure_masks(module, view, enc_ordered, cell_px, masks_path):
    """Group `enc_ordered` ([(face_id, kind, mat, poly, enclosure)], from
    kit_module_render.ordered_enclosure_faces) by its trailing `enclosure`
    tag and write `{module}_{view}_{tag}_facemask.png` / `_faces.json` for
    each non-empty group — Lucas's orange enclosure regions, one mask set
    per kind, for assembly (S4t) to warp wall texture into directly.
    Modules with no enclosure faces (wall_band, base, ...) write nothing."""
    by_tag = {}
    for face_id, kind, mat, poly, tag in enc_ordered:
        by_tag.setdefault(tag, []).append((face_id, kind, mat, poly))
    for tag, group in by_tag.items():
        idmap, meta = fm.face_mask(group, (cell_px, cell_px))
        fm.save_mask(idmap, meta, masks_path / f"{module}_{view}_{tag}")
