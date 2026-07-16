#!/usr/bin/env python3
"""test_texture_map.py — face(kind,mat) -> texture family/variant lookup (T1, C2, C8).

Seam: src/pipeline/texture_map.py — does NOT exist yet on this branch.
`_tm()` imports it lazily inside each test's call phase (not at module top
level) so a missing module reports one clean FAILED per test instead of
aborting collection for the whole session (established convention, see
test_kit_module_render.py's header). `kit_modules` already exists on this
branch, so it's imported normally at the top (same convention).

Seam decisions (3-arch.md names `FAMILY(module, kind, normal) -> family_str`
as an internal table function, but the mat-dependent branches — "blank/thatch
mat->stone", "wall_{mat}_top" — clearly need `mat` too, which the stated
3-arg signature omits. Rather than pin FAMILY's own ambiguous signature,
these tests drive the fully-specified PUBLIC seam instead:
`face_texture(module, kind, world_pts, mat) -> {id, type, dims_voxels}`.
If Loop 4b's FAMILY signature differs internally, that's fine — only
face_texture/variant/recess_decals/load_textures are asserted here.

World geometry for every face-kind test below comes from the REAL
`kit_modules.MODULES[...]()` faces (never hand-rolled world_pts), so normals
are correct by construction instead of by manual cross-product arithmetic.
"""

import re

import kit_modules as km

TEXTURES_JSON = "assets/textures/textures.json"


def _tm():
    import texture_map
    return texture_map


def _family(texture_id):
    return re.sub(r"_v\d+$", "", texture_id)


def _faces(module, kind):
    return [f for f in km.MODULES[module]() if f.kind == kind]


# ---------------------------------------------------------------------- load_textures
def test_load_textures_parses_the_real_textures_json_with_known_families():
    textures = _tm().load_textures()
    assert "floor_stone_v1" in textures
    assert textures["floor_stone_v1"]["type"] == "tiling"
    assert textures["floor_stone_v1"]["dims_voxels"] == [1, 0, 1]
    assert "door_1x2x0" in textures and textures["door_1x2x0"]["type"] == "decal"


# ---------------------------------------------------------------------- face_texture: FAMILY table (C2)
def test_face_texture_wall_band_top_uses_wall_mat_top_family():
    tm = _tm()
    top = _faces("wall_band", "top")[0]
    assert _family(tm.face_texture("wall_band", "top", top.pts, "wood")["id"]) == "wall_wood_top"
    assert _family(tm.face_texture("wall_band", "top", top.pts, "stone")["id"]) == "wall_stone_top"


def test_face_texture_blank_and_thatch_mat_default_to_stone():
    tm = _tm()
    top = _faces("top_cap", "top")[0]
    for mat in ("blank", "thatch"):
        assert _family(tm.face_texture("top_cap", "top", top.pts, mat)["id"]) == "wall_stone_top"


def test_face_texture_base_top_is_always_floor_stone_regardless_of_mat():
    tm = _tm()
    top = _faces("base", "top")[0]
    for mat in ("blank", "wood", "stone", "thatch"):
        assert _family(tm.face_texture("base", "top", top.pts, mat)["id"]) == "floor_stone"


def test_face_texture_any_side_face_uses_wall_mat_side_family():
    tm = _tm()
    side = _faces("wall_band", "side")[0]
    assert _family(tm.face_texture("wall_band", "side", side.pts, "wood")["id"]) == "wall_wood_side"
    assert _family(tm.face_texture("wall_band", "side", side.pts, "stone")["id"]) == "wall_stone_side"


def test_face_texture_roof_slope_is_roof_shingle():
    tm = _tm()
    face = _faces("roof_cell", "slope")[0]
    assert _family(tm.face_texture("roof_cell", "slope", face.pts, "blank")["id"]) == "roof_shingle"


def test_face_texture_gable_kind_still_maps_to_roof_shingle():
    # R2-3 (ROUND 2, AMENDED 2026-07-16): roof_cell is cover-only now and no
    # longer EMITS "gable" faces itself (gable becomes WALL material at
    # assembly, S4t) — the FAMILY table's kind=="gable" rule is still a
    # general, valid mapping, exercised with a synthetic triangle instead of
    # through roof_cell's own output. Roof "bottom" is gone the same way;
    # the generic kind=="bottom"->floor_stone rule stays covered via stairs
    # below.
    tm = _tm()
    pts = [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.5, 0.5, 1.0)]
    assert _family(tm.face_texture("roof_cell", "gable", pts, "blank")["id"]) == "roof_shingle"


def test_face_texture_stair_top_is_stair_tread_and_bottom_is_floor_stone():
    tm = _tm()
    top = _faces("stair_45", "top")[0]
    bottom = _faces("stair_45", "bottom")[0]
    assert _family(tm.face_texture("stair_45", "top", top.pts, "blank")["id"]) == "stair_tread"
    assert _family(tm.face_texture("stair_45", "bottom", bottom.pts, "blank")["id"]) == "floor_stone"


def test_face_texture_stair_sides_are_all_riser_after_r2_4_cover_only():
    # R2-4 (ROUND 2, AMENDED 2026-07-16): stair builders are cover-only now
    # — only the uphill riser side survives per step; the side-triangle
    # envelope + the back face buried against the next step are struck
    # (become WALL material at assembly). wall_stone_side no longer appears
    # among stair_45's own side faces — still covered generically by
    # test_face_texture_any_side_face_uses_wall_mat_side_family above.
    tm = _tm()
    families = {
        _family(tm.face_texture("stair_45", "side", f.pts, "blank")["id"])
        for f in _faces("stair_45", "side")
    }
    assert families == {"stair_riser"}, families


def test_face_texture_never_raises_for_an_unmapped_module():
    tm = _tm()
    quad = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)]
    spec = tm.face_texture("totally_unmapped_module_xyz", "top", quad, "blank")
    assert spec["id"] in _tm().load_textures()


def test_face_texture_id_type_and_dims_agree_with_textures_json():
    tm = _tm()
    top = _faces("wall_band", "top")[0]
    spec = tm.face_texture("wall_band", "top", top.pts, "wood")
    textures = tm.load_textures()
    assert spec["id"] in textures
    assert spec["type"] == textures[spec["id"]]["type"]
    assert spec["dims_voxels"] == textures[spec["id"]]["dims_voxels"]


# recess_decals (wall-carve opening decals) is GONE — R2-5 (ROUND 2,
# AMENDED 2026-07-16) replaced recess_door/recess_window with standalone
# door_1x2/window_1x1 slab OBJECTS. Its coverage (door/window decal id
# resolution, plus the new back-face flip_h contract) moved to
# test_texture_map_slab.py.


# ---------------------------------------------------------------------- variant (C8)
def test_variant_depends_only_on_world_column_not_z_view_invariance():
    tm = _tm()
    v1 = tm.variant("floor_stone", [(0.3, 0.4, 0.0)])
    v2 = tm.variant("floor_stone", [(0.3, 0.4, 5.0)])  # same u,v, different z
    assert v1 == v2


def test_variant_shows_at_least_two_distinct_ids_across_many_world_columns():
    tm = _tm()
    seen = {tm.variant("floor_stone", [(col * 0.25, 0.0, 0.0)]) for col in range(12)}
    assert len(seen) >= 2, seen


def test_variant_id_is_a_real_textures_json_key_in_its_own_family():
    tm = _tm()
    vid = tm.variant("wall_stone_side", [(0.0, 0.0, 0.0)])
    assert vid in tm.load_textures()
    assert _family(vid) == "wall_stone_side"
