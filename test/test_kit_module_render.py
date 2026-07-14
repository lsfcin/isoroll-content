#!/usr/bin/env python3
"""test_kit_module_render.py — shared projected-face seam, flat render, one
shared px-per-voxel scale (C1/C2), and per-face occlusion masks (C3).

Seam: kit_module_render.py + face_masks.py (T2/T3/T4) — do NOT exist yet on
this branch. `_kmr()`/`_km()`/`_fm()` import them lazily inside each test's
call phase (not at module top level) so a missing module reports one clean
FAILED per test instead of aborting collection for the whole session (see
test_kit_modules.py's header for the verified reason). sheet_qc already
exists, so it's imported normally at the top.

NOTE for Loop 4b (documented seam decision, not pinned by 3-arch.md):
`build_sheet_manifest(panels, s)`'s input `panels` is a list of dicts with
keys {module, view, bbox, origin} — mirroring the output shape 1:1, since the
architecture only fixes the output schema. If Loop 4b's natural call
convention differs, raise `RETURN loop=4a reason=test-wrong`, don't hand-edit
this test.

Also note: 3-arch.md gives `render_panel(...) -> (RGBA, origin, ordered)` but
`render_module(...) -> dict[view -> (RGBA, ordered, origin)]` — the tuple
order is inconsistent between the two lines in the architecture doc. Tests
below follow render_module's own stated order exactly (the only one directly
exercised here); Loop 4b should reconcile the two to agree.
"""

from PIL import Image

import sheet_qc as qc

CELL_PX = 160
PAD = 6


def _kmr():
    import kit_module_render
    return kit_module_render


def _km():
    import kit_modules
    return kit_modules


def _fm():
    import face_masks
    return face_masks


def _panels_for(name, s=8.0):
    return _kmr().render_module(name, s, CELL_PX, PAD)


# ---------------------------------------------------------------------- C1
def test_yaws_and_views_are_the_documented_nine():
    kmr = _kmr()
    assert kmr.YAWS == [0, 45, 90, 135, 180, 225, 270, 315]
    assert len(kmr.VIEWS) == 9
    assert kmr.VIEWS[-1] == "TOP"


def test_render_module_yields_all_nine_views_as_rgba():
    panels = _panels_for("wall_band")
    assert set(panels) == set(_kmr().VIEWS)
    for view in _kmr().VIEWS:
        img, ordered, origin = panels[view]
        assert isinstance(img, Image.Image) and img.mode == "RGBA"
        assert len(ordered) > 0


def test_render_module_is_deterministic():
    a, b = _panels_for("roof_cell"), _panels_for("roof_cell")
    for view in _kmr().VIEWS:
        assert list(a[view][0].getdata()) == list(b[view][0].getdata()), view


def test_silhouette_bbox_differs_across_at_least_four_of_eight_yaws():
    kmr = _kmr()
    panels = _panels_for("roof_cell")  # asymmetric module: no accidental mirror symmetry
    bboxes = [qc.silhouette_mask(panels[f"y{yaw}"][0]).getbbox() for yaw in kmr.YAWS]
    assert len(set(bboxes)) >= 4, bboxes


def test_ordered_faces_ids_are_stable_and_uniquely_formatted_per_panel():
    _, ordered, _ = _panels_for("wall_band")["y0"]
    ids = [face_id for face_id, kind, mat, poly in ordered]
    assert len(ids) == len(set(ids))
    assert all(":" in i for i in ids)


# ---------------------------------------------------------------------- C2
def test_shared_scale_is_one_value_that_fits_every_panel_of_every_module():
    kmr, km = _kmr(), _km()
    names = ["wall_band", "top_cap", "roof_cell", "stair_45"]
    s = kmr.shared_scale(names, cell_px=CELL_PX, pad=PAD)
    assert s > 0
    avail = CELL_PX - 2 * PAD
    for name in names:
        faces = km.MODULES[name]()
        for view in kmr.VIEWS:
            w, h = kmr.panel_extent(faces, view, s=s)
            assert w <= avail + 1e-6 and h <= avail + 1e-6, (name, view, w, h)


def test_build_sheet_manifest_records_scale_once_at_sheet_level_not_per_panel():
    kmr, km = _kmr(), _km()
    names = ["wall_band", "roof_cell"]
    s = kmr.shared_scale(names, cell_px=CELL_PX, pad=PAD)
    panels = []
    for name in names:
        faces = km.MODULES[name]()
        rendered = kmr.render_module(name, s, CELL_PX, PAD)
        for view, (img, ordered, origin) in rendered.items():
            bbox = kmr.panel_extent(faces, view, s=s)
            panels.append({"module": name, "view": view, "bbox": bbox, "origin": origin})

    manifest = kmr.build_sheet_manifest(panels, s)

    assert manifest["px_per_voxel"] == s
    assert len(manifest["panels"]) == len(panels)
    assert all("px_per_voxel" not in p for p in manifest["panels"]), (
        "C2: one shared scale per sheet, never a per-panel override")


# ---------------------------------------------------------------------- C3
def test_face_mask_regions_are_single_valued_and_within_the_render_silhouette():
    img, ordered, origin = _panels_for("roof_cell")["y45"]
    idmap, meta = _fm().face_mask(ordered, img.size)
    assert idmap.mode == "L" and idmap.size == img.size

    sil = qc.silhouette_mask(img)
    painted = idmap.point(lambda p: 255 if p > 0 else 0)
    leaks = sum(1 for p, s in zip(painted.getdata(), sil.getdata()) if p and not s)
    assert leaks == 0

    assert set(meta.keys()) == {face_id for face_id, *_ in ordered}


def test_face_mask_meta_records_bbox_and_positive_pixel_count_per_face():
    img, ordered, origin = _panels_for("wall_band")["TOP"]
    _, meta = _fm().face_mask(ordered, img.size)
    for face_id, info in meta.items():
        assert "bbox" in info and "pixels" in info, face_id
        assert info["pixels"] > 0, face_id


def test_save_mask_writes_the_documented_png_and_json_pair(tmp_path):
    img, ordered, origin = _panels_for("wall_band")["TOP"]
    idmap, meta = _fm().face_mask(ordered, img.size)
    _fm().save_mask(idmap, meta, tmp_path / "wall_band_TOP")
    assert (tmp_path / "wall_band_TOP_facemask.png").exists()
    assert (tmp_path / "wall_band_TOP_faces.json").exists()
