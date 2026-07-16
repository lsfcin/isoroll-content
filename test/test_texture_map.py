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


def test_face_texture_roof_slope_and_gable_are_roof_shingle():
    tm = _tm()
    for kind in ("slope", "gable"):
        face = _faces("roof_cell", kind)[0]
        assert _family(tm.face_texture("roof_cell", kind, face.pts, "blank")["id"]) == "roof_shingle"


def test_face_texture_roof_bottom_is_floor_stone():
    tm = _tm()
    bottom = _faces("roof_cell", "bottom")[0]
    assert _family(tm.face_texture("roof_cell", "bottom", bottom.pts, "blank")["id"]) == "floor_stone"


def test_face_texture_stair_top_is_stair_tread_and_bottom_is_floor_stone():
    tm = _tm()
    top = _faces("stair_45", "top")[0]
    bottom = _faces("stair_45", "bottom")[0]
    assert _family(tm.face_texture("stair_45", "top", top.pts, "blank")["id"]) == "stair_tread"
    assert _family(tm.face_texture("stair_45", "bottom", bottom.pts, "blank")["id"]) == "floor_stone"


def test_face_texture_stair_sides_split_between_riser_and_wall_stone_side():
    # Stair side faces come in two physical orientations: the narrow ‖±u
    # riser faces and the ‖±v/back faces. Rather than hand-pick which real
    # face.pts is which (risking a winding-order mistake), assert over ALL
    # of stair_45's side faces that both families appear and nothing else does.
    tm = _tm()
    families = {
        _family(tm.face_texture("stair_45", "side", f.pts, "blank")["id"])
        for f in _faces("stair_45", "side")
    }
    assert families == {"stair_riser", "wall_stone_side"}, families


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


# ---------------------------------------------------------------------- recess_decals
def test_recess_decals_door_is_the_pinned_id_and_quad():
    quad = _tm().recess_decals("recess_door")
    assert quad == [("door_1x2x0", [(0.15, 1.0, 0.0), (0.85, 1.0, 0.0), (0.85, 1.0, 2.0), (0.15, 1.0, 2.0)])]


def test_recess_decals_window_is_the_pinned_id_and_quad():
    quad = _tm().recess_decals("recess_window")
    assert quad == [("window_1x1x0", [(0.15, 1.0, 1.0), (0.85, 1.0, 1.0), (0.85, 1.0, 2.0), (0.15, 1.0, 2.0)])]


def test_recess_decals_is_empty_for_a_module_with_no_opening():
    assert _tm().recess_decals("wall_band") == []


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
