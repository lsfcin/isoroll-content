#!/usr/bin/env python3
"""test_enclosure_masks.py — Lucas 2026-07-19 union enclosure mask
(design/S4-REVIEW-ROUNDS.md ROUND 4c): one `enclosure` mask per module+view =
the UNION of the piece's OWN front-facing enclosure faces (stair side caps +
back wall, roof gable ends). The cover (treads/risers, roof slopes) is NOT
subtracted — at assembly the cover sprite composites on top, so underlap is
hidden and the sides can never be eaten by a painter-order misorder against
the cover (which is exactly what the earlier depth-composite / lateral-minus-
render / air-above attempts did). Split from test_stage_kit_modules.py for the
per-file line gate.

Invariants: (a) the written mask equals an independently rebuilt union of the
front-facing enclosure faces (end-to-end wiring, not a re-run of
composite_enclosure); (b) every front-facing enclosure face is FULLY inside
the mask — the regression guard that would have caught the eaten sides; (c)
the mask lies inside the module's own solid silhouette (no wall outside the
solid). Plus the "behind-view stair paints a near-zero sliver" render contract
(backface culling, unrelated to masks)."""

import numpy as np
from PIL import Image, ImageDraw


def _skm():
    import stage_kit_modules
    return stage_kit_modules


def _bool(idmap):
    binary = idmap.point(lambda p: 255 if p > 0 else 0)
    return np.asarray(binary, dtype=bool)


def _front(module, view, s, cell_px, pad, origin):
    import kit_module_render as kmr
    import kit_modules as km
    from scene_guide_render import Cam
    faces = km.MODULES[module]()
    cam = Cam([], cell_px, cell_px, pad, scale=s, origin=origin)
    return kmr.ordered_front_faces(faces, view, cam)


def _fill(polys, size):
    im = Image.new("L", size, 0)
    draw = ImageDraw.Draw(im)
    for poly in polys:
        draw.polygon(poly, fill=255)
    return np.asarray(im) > 0


def _staged(tmp_path):
    """stage() into tmp_path, return (stage_kit_modules module, masks dir,
    shared scale s) — shared setup for the invariant tests below."""
    import kit_module_render as kmr
    import kit_modules as km
    skm = _skm()
    masks = tmp_path / "masks"
    skm.stage(out=str(tmp_path / "gen-inbox"), out_masks=str(masks))
    s = kmr.shared_scale(list(km.MODULES), cell_px=skm.CELL_PX, pad=skm.PAD)
    return skm, masks, s


COVER_MODULES = ("stair_45", "stair_half", "roof_cell")


def test_stage_writes_enclosure_masks_per_view_for_stairs_and_roof_with_nonzero_coverage(tmp_path):
    out = tmp_path / "gen-inbox"
    masks = tmp_path / "masks"
    _skm().stage(out=str(out), out_masks=str(masks))

    for module in COVER_MODULES:
        pngs = list(masks.glob(f"{module}_*_enclosure_facemask.png"))
        assert pngs, (module, "no enclosure-mask PNG written")
        assert any(Image.open(p).getbbox() is not None for p in pngs), (
            module, "no view produced nonzero enclosure-mask coverage")
        jsons = list(masks.glob(f"{module}_*_enclosure_faces.json"))
        assert len(jsons) == len(pngs)


def test_stage_writes_no_enclosure_masks_for_a_module_with_no_enclosure_faces(tmp_path):
    # wall_band has no Face.enclosure geometry at all — stage() never even
    # calls save_enclosure_masks for it (gate unchanged since ROUND 4).
    out = tmp_path / "gen-inbox"
    masks = tmp_path / "masks"
    _skm().stage(out=str(out), out_masks=str(masks))
    assert not list(masks.glob("wall_band_*_enclosure_facemask.png"))


def test_enclosure_mask_equals_the_union_of_the_front_facing_enclosure_faces(tmp_path):
    # (a) Rebuild the union independently — fill every front-facing enclosure
    # face (enc != "") flat — and compare pixel-for-pixel against the actual
    # PNG stage() wrote (or its absence). Does NOT call composite_enclosure.
    import kit_module_render as kmr

    skm, masks, s = _staged(tmp_path)

    for module in COVER_MODULES:
        for view, (img, ordered, origin) in kmr.render_module(module, s, skm.CELL_PX, skm.PAD).items():
            path = masks / f"{module}_{view}_enclosure_facemask.png"
            enc_polys = [poly for _f, _k, _m, poly, enc in _front(module, view, s, skm.CELL_PX, skm.PAD, origin) if enc]
            expected = _fill(enc_polys, img.size)
            if not expected.any():
                assert not path.exists(), (module, view, "expected empty mask but a PNG was written")
                continue
            actual = _bool(Image.open(path).convert("L"))
            assert np.array_equal(actual, expected), (module, view)


def test_every_front_facing_enclosure_face_is_fully_inside_the_mask(tmp_path):
    # (b) the regression guard for the eaten sides: because the mask is a plain
    # union with no cover subtraction, every front-facing enclosure face — each
    # side cap AND the back wall — must lie entirely within the written mask.
    import kit_module_render as kmr

    skm, masks, s = _staged(tmp_path)

    for module in COVER_MODULES:
        for view, (img, ordered, origin) in kmr.render_module(module, s, skm.CELL_PX, skm.PAD).items():
            path = masks / f"{module}_{view}_enclosure_facemask.png"
            if not path.exists():
                continue
            mask = _bool(Image.open(path).convert("L"))
            for fid, _k, _m, poly, enc in _front(module, view, s, skm.CELL_PX, skm.PAD, origin):
                if not enc:
                    continue
                face = _fill([poly], img.size)
                missing = int((face & ~mask).sum())
                assert missing == 0, (module, view, fid, "enclosure face not fully in mask")


def test_enclosure_mask_is_contained_in_the_solid_silhouette(tmp_path):
    # (c) mask ⊆ solid silhouette (every face projected unfiltered) — no wall
    # painted outside the real solid.
    import kit_module_render as kmr
    import kit_modules as km

    skm, masks, s = _staged(tmp_path)

    for module in COVER_MODULES:
        faces = km.MODULES[module]()
        for view, (img, ordered, origin) in kmr.render_module(module, s, skm.CELL_PX, skm.PAD).items():
            path = masks / f"{module}_{view}_enclosure_facemask.png"
            if not path.exists():
                continue
            mask = _bool(Image.open(path).convert("L"))
            solid_polys = [kmr.project_face(f.pts, view, s, skm.CELL_PX, skm.PAD, origin) for f in faces]
            solid = _fill(solid_polys, img.size)
            leaks = int((mask & ~solid).sum())
            assert leaks == 0, (module, view, "mask pixel lies outside the solid silhouette")


def test_stair_behind_view_paints_a_near_zero_sliver_relative_to_the_front_view():
    # ROUND 4: a face seen from behind must not paint (backface culling) — for
    # stairs the risers vanish from views that look from the up-stair end,
    # leaving only the thin tread strips. Relative comparison (min vs max
    # view), not a hardcoded pixel count. A render contract, not a mask one.
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
