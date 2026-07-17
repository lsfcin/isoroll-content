#!/usr/bin/env python3
"""test_enclosure_masks.py — ROUND 4b (design/S4-REVIEW-ROUNDS.md ROUND 4b):
one `enclosure` mask per module+view = this module's projected LATERAL
faces (stair profile-cap sides / roof gable ends, enclosure_masks.
lateral_faces) minus its own rendered silhouette — supersedes ROUND 4's
synthetic-wall-voxel-minus-render definition (which painted air regions
orange in some views since roof_cell/stairs don't fill the full WALL_H
voxel). Split out from test_stage_kit_modules.py to stay under the
per-file line gate (same convention as test_texture_map_slab.py/
test_face_edges.py). Carries the ROUND-4b mandatory invariants: (a) the
written mask equals an independently-recomputed lateral-minus-render
rasterization (end-to-end wiring check); (b) render and mask never overlap
beyond edge-stroke tolerance; (c) render UNION mask is always contained in
the module's own solid silhouette (no air ever painted). Also carries the
"behind-view stair paints a near-zero sliver" render contract (unchanged
by ROUND 4b — it's about backface culling, not masks)."""

from PIL import Image, ImageChops, ImageFilter


def _skm():
    import stage_kit_modules
    return stage_kit_modules


def _binary(idmap):
    return idmap.point(lambda p: 255 if p > 0 else 0)


def _staged(tmp_path):
    """stage() into tmp_path, return (stage_kit_modules module, masks dir,
    shared scale s) — shared setup for the ROUND-4b invariant tests below."""
    import kit_module_render as kmr
    import kit_modules as km
    skm = _skm()
    masks = tmp_path / "masks"
    skm.stage(out=str(tmp_path / "gen-inbox"), out_masks=str(masks))
    s = kmr.shared_scale(list(km.MODULES), cell_px=skm.CELL_PX, pad=skm.PAD)
    return skm, masks, s


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
    # stage() never even calls save_enclosure_masks for it (ROUND 4 gate,
    # unchanged by ROUND 4b).
    out = tmp_path / "gen-inbox"
    masks = tmp_path / "masks"
    _skm().stage(out=str(out), out_masks=str(masks))
    assert not list(masks.glob("wall_band_*_enclosure_facemask.png"))


def test_round4b_enclosure_mask_equals_the_lateral_minus_render_rasterization_by_construction(tmp_path):
    # (a) Recompute the mask independently — this module's projected
    # LATERAL faces (enclosure_masks.lateral_faces) minus its own rendered
    # silhouette, both rasterised fresh via face_masks.face_mask — and
    # compare pixel-for-pixel against the actual PNG stage() wrote. An
    # end-to-end wiring check, not a tautological re-run of the same code.
    import enclosure_masks as em
    import face_masks as fm
    import kit_module_render as kmr

    skm, masks, s = _staged(tmp_path)

    for module in ("stair_45", "stair_half", "roof_cell"):
        for view, (img, ordered, origin) in kmr.render_module(module, s, skm.CELL_PX, skm.PAD).items():
            path = masks / f"{module}_{view}_enclosure_facemask.png"
            lateral = em.lateral_faces(module, view, s, skm.CELL_PX, skm.PAD, origin)
            if not lateral:
                assert not path.exists(), (module, view, "no lateral faces but a mask was written")
                continue
            lat_sil = _binary(fm.face_mask(lateral, img.size)[0])
            render_sil = _binary(fm.face_mask(ordered, img.size)[0])
            expected = _binary(ImageChops.subtract(lat_sil, render_sil))
            if expected.getbbox() is None:
                assert not path.exists(), (module, view, "expected empty gap but a mask was written")
                continue
            actual = _binary(Image.open(path).convert("L"))
            assert list(actual.getdata()) == list(expected.getdata()), (module, view)


def test_round4b_render_and_enclosure_mask_do_not_overlap_beyond_stroke_tolerance(tmp_path):
    # (b) render ∩ mask ≈ ∅: the mask must never bleed into the DEEP
    # interior of the render silhouette (eroded inward by the edge-stroke
    # width) — only a thin boundary band, if any, is tolerated. Checked
    # against the real files stage() wrote, not a fresh recomputation.
    import face_edges as fe
    import face_masks as fm
    import kit_module_render as kmr

    skm, masks, s = _staged(tmp_path)
    width = fe.edge_width(skm.CELL_PX)

    for module in ("stair_45", "stair_half", "roof_cell"):
        for view, (img, ordered, origin) in kmr.render_module(module, s, skm.CELL_PX, skm.PAD).items():
            path = masks / f"{module}_{view}_enclosure_facemask.png"
            if not path.exists():
                continue
            mask_bin = _binary(Image.open(path).convert("L"))
            render_bin = _binary(fm.face_mask(ordered, img.size)[0])
            render_core = render_bin.filter(ImageFilter.MinFilter(2 * width + 1))
            deep_overlap = sum(1 for c, m in zip(render_core.getdata(), mask_bin.getdata()) if c and m)
            assert deep_overlap == 0, (module, view, deep_overlap)


def test_round4b_render_union_enclosure_mask_is_contained_in_the_solid_silhouette(tmp_path):
    # (c) render ∪ mask ⊆ solid silhouette: "solid silhouette" = EVERY face
    # of the module projected with no filtering at all (neither backface
    # cull nor render/enclosure split) — the true physical boundary of the
    # object, via the public project_face seam (byte-identical transform to
    # ordered_faces' own). Pins the ROUND-4b fix directly: a mask can never
    # paint air outside the real solid.
    import face_masks as fm
    import kit_module_render as kmr
    import kit_modules as km

    skm, masks, s = _staged(tmp_path)

    for module in ("stair_45", "stair_half", "roof_cell"):
        faces = km.MODULES[module]()
        for view, (img, ordered, origin) in kmr.render_module(module, s, skm.CELL_PX, skm.PAD).items():
            solid_ordered = [
                (f"{i}:{f.kind}", f.kind, f.mat, kmr.project_face(f.pts, view, s, skm.CELL_PX, skm.PAD, origin))
                for i, f in enumerate(faces)
            ]
            solid_bin = _binary(fm.face_mask(solid_ordered, img.size)[0])
            render_bin = _binary(fm.face_mask(ordered, img.size)[0])

            path = masks / f"{module}_{view}_enclosure_facemask.png"
            mask_bin = _binary(Image.open(path).convert("L")) if path.exists() else Image.new("L", img.size, 0)

            leaks = sum(
                1 for r, m, sol in zip(render_bin.getdata(), mask_bin.getdata(), solid_bin.getdata())
                if (r or m) and not sol)
            assert leaks == 0, (module, view, "render/mask pixel lies outside the solid silhouette")


def test_stair_behind_view_paints_a_near_zero_sliver_relative_to_the_front_view():
    # ROUND 4: a face seen from behind must not paint (backface culling) —
    # for stairs the risers vanish entirely from whichever views look from
    # the up-stair end, leaving only the thin tread strips. Relative
    # comparison (min view vs max view), not a hardcoded absolute pixel
    # count, so it doesn't depend on CELL_PX/test fixture scale. Unaffected
    # by ROUND 4b (this is a render, not a mask, contract).
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
