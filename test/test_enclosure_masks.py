#!/usr/bin/env python3
"""test_enclosure_masks.py — ROUND 3 (design/S4-REVIEW-ROUNDS.md ROUND 3):
stripped stair/roof enclosure faces (never painted in arm_a) still land as
tagged per-view mask PNGs, via enclosure_masks.py + stage_kit_modules.stage.
Split out from test_stage_kit_modules.py to stay under the per-file line
gate (same convention as test_texture_map_slab.py/test_face_edges.py)."""

from PIL import Image


def _skm():
    import stage_kit_modules
    return stage_kit_modules


def test_stage_writes_enclosure_masks_per_view_for_stairs_and_roof_with_nonzero_coverage(tmp_path):
    out = tmp_path / "gen-inbox"
    masks = tmp_path / "masks"
    _skm().stage(out=str(out), out_masks=str(masks))

    for module, tags in (
        ("stair_45", {"stair_enclosure"}),
        ("stair_half", {"stair_enclosure"}),
        ("roof_cell", {"roof_edge", "roof_inset"}),
    ):
        for tag in tags:
            pngs = list(masks.glob(f"{module}_*_{tag}_facemask.png"))
            assert pngs, (module, tag, "no enclosure-mask PNG written for this tag")
            assert any(Image.open(p).getbbox() is not None for p in pngs), (
                module, tag, "no view produced nonzero enclosure-mask coverage")
            jsons = list(masks.glob(f"{module}_*_{tag}_faces.json"))
            assert len(jsons) == len(pngs)


def test_stage_writes_no_enclosure_masks_for_a_module_with_no_enclosure_faces(tmp_path):
    # wall_band has no Face.enclosure geometry at all — nothing tagged.
    out = tmp_path / "gen-inbox"
    masks = tmp_path / "masks"
    _skm().stage(out=str(out), out_masks=str(masks))
    for tag in ("stair_enclosure", "roof_edge", "roof_inset"):
        assert not list(masks.glob(f"wall_band_*_{tag}_facemask.png"))
