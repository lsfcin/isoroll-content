#!/usr/bin/env python3
"""test_enclosure_masks.py — ROUND 4 (design/S4-REVIEW-ROUNDS.md ROUND 4):
one `enclosure` mask per module+view = voxel_silhouette minus the module's
own rendered alpha (drops the old ROUND-3 stair_enclosure/roof_edge/
roof_inset per-Face-tag split). Split out from test_stage_kit_modules.py to
stay under the per-file line gate (same convention as
test_texture_map_slab.py/test_face_edges.py). Also carries the ROUND-4
mandatory invariant test (rendered UNION enclosure == voxel_silhouette
exactly, zero gap/overlap) and the "behind-view stair paints a near-zero
sliver" contract."""

from PIL import Image


def _skm():
    import stage_kit_modules
    return stage_kit_modules


def test_stage_writes_enclosure_masks_per_view_for_stairs_and_roof_with_nonzero_coverage(tmp_path):
    out = tmp_path / "gen-inbox"
    masks = tmp_path / "masks"
    _skm().stage(out=str(out), out_masks=str(masks))

    for module in ("stair_45", "stair_half", "roof_cell"):
        pngs = list(masks.glob(f"{module}_*_enclosure_facemask.png"))
        assert pngs, (module, "no enclosure-mask PNG written")
        assert any(Image.open(p).getbbox() is not None for p in pngs), (
            module, "no view produced nonzero enclosure-mask coverage")
        jsons = list(masks.glob(f"{module}_*_enclosure_faces.json"))
        assert len(jsons) == len(pngs)


def test_stage_writes_no_enclosure_masks_for_a_module_with_no_enclosure_faces(tmp_path):
    # wall_band has no Face.enclosure geometry at all — nothing tagged,
    # stage() never even calls save_enclosure_masks for it (ROUND 4 gate).
    out = tmp_path / "gen-inbox"
    masks = tmp_path / "masks"
    _skm().stage(out=str(out), out_masks=str(masks))
    assert not list(masks.glob("wall_band_*_enclosure_facemask.png"))


def test_round4_rendered_union_enclosure_equals_voxel_silhouette_exactly(tmp_path):
    # ROUND 4 MANDATORY INVARIANT (S4-REVIEW-ROUNDS.md ROUND 4): per view,
    # for every stair/roof module, rendered_alpha UNION enclosure_mask ==
    # voxel_silhouette EXACTLY (zero gap pixels, zero overlap) and no
    # rendered pixel ever lies outside the voxel silhouette. Makes the
    # ROUND-3-generation bug class (masks that didn't cover the true gap)
    # unshippable blind.
    import enclosure_masks as em
    import face_masks as fm
    import kit_module_render as kmr
    import kit_modules as km

    skm = _skm()
    masks = tmp_path / "masks"
    skm.stage(out=str(tmp_path / "gen-inbox"), out_masks=str(masks))

    names = list(km.MODULES)
    s = kmr.shared_scale(names, cell_px=skm.CELL_PX, pad=skm.PAD)

    for module in ("stair_45", "stair_half", "roof_cell"):
        for view, (img, ordered, origin) in kmr.render_module(module, s, skm.CELL_PX, skm.PAD).items():
            voxel = em.voxel_silhouette(view, s, skm.CELL_PX, skm.PAD, origin)
            idmap, _meta = fm.face_mask(ordered, img.size)
            rendered_sil = idmap.point(lambda p: 255 if p > 0 else 0)

            leaks = sum(1 for r, v in zip(rendered_sil.getdata(), voxel.getdata()) if r and not v)
            assert leaks == 0, (module, view, "rendered pixel lies outside the voxel silhouette")

            path = masks / f"{module}_{view}_enclosure_facemask.png"
            if path.exists():
                enc = Image.open(path).convert("L").point(lambda p: 255 if p > 0 else 0)
            else:
                enc = Image.new("L", voxel.size, 0)  # no gap at this view

            union = [255 if (r or e) else 0 for r, e in zip(rendered_sil.getdata(), enc.getdata())]
            assert union == list(voxel.getdata()), (module, view, "union != voxel_silhouette")
            overlap = sum(1 for r, e in zip(rendered_sil.getdata(), enc.getdata()) if r and e)
            assert overlap == 0, (module, view, "rendered/enclosure overlap")


def test_stair_behind_view_paints_a_near_zero_sliver_relative_to_the_front_view():
    # ROUND 4: a face seen from behind must not paint (backface culling) —
    # for stairs the risers vanish entirely from whichever views look from
    # the up-stair end, leaving only the thin tread strips. Relative
    # comparison (min view vs max view), not a hardcoded absolute pixel
    # count, so it doesn't depend on CELL_PX/test fixture scale.
    import face_masks as fm
    import kit_module_render as kmr
    import kit_modules as km

    skm = _skm()
    names = list(km.MODULES)
    s = kmr.shared_scale(names, cell_px=skm.CELL_PX, pad=skm.PAD)
    rendered = kmr.render_module("stair_45", s, skm.CELL_PX, skm.PAD)

    areas = {}
    for view, (img, ordered, origin) in rendered.items():
        if view == "TOP":
            continue
        idmap, _meta = fm.face_mask(ordered, img.size)
        areas[view] = sum(1 for p in idmap.getdata() if p > 0)

    assert min(areas.values()) < 0.3 * max(areas.values()), areas
