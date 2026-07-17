#!/usr/bin/env python3
"""test_kit_modules.py — KIT V2 module geometry as faces (C1).

Seam: kit_modules.py (T1) — does NOT exist yet on this branch. `_km()` below
imports it lazily *inside* each test's call phase (not at module top level):
a top-level `import kit_modules` would raise ModuleNotFoundError during
pytest collection and abort the whole session (verified locally — it swallows
even the unrelated, already-green 53-test baseline). Deferring the import
into the call phase instead makes every test in this file report a normal,
isolated FAILED — the correct "red" signal for a module that's genuinely
missing (not a test-authoring bug) — while leaving collection, and the rest
of the suite, untouched. Once kit_modules.py exists, every test below
exercises real behavior (face kinds/counts per builder — 3-arch.md's binding
amendment: Face replaces Box as the shared module representation).
"""

from collections import Counter

import pytest

from layout_massing import STEPS, Box

UNIT_SQUARE = [(0, 0), (1, 0), (1, 1), (0, 1)]
# R2-5 (S4-REVIEW-ROUNDS.md ROUND 2, AMENDED 2026-07-16): recess_door/
# recess_window (wall-carve openings) are replaced by standalone slab
# objects door_1x2/window_1x1 — the wall-with-a-hole is emergent at
# assembly (S4t), not this module's concern.
EXPECTED_MODULES = {
    "wall_band", "top_cap", "base", "door_1x2", "window_1x1",
    "diag_half", "roof_cell", "stair_45", "stair_half",
}


def _km():
    import kit_modules
    return kit_modules


# ------------------------------------------------------------------ extrude
def test_extrude_unit_square_emits_top_bottom_and_four_sides():
    faces = _km().extrude(UNIT_SQUARE, z0=0.0, h=1.0)
    kinds = Counter(f.kind for f in faces)
    assert kinds == {"top": 1, "bottom": 1, "side": 4}
    assert len(faces) == 6


def test_extrude_faces_are_valid_polygons():
    for f in _km().extrude(UNIT_SQUARE, z0=0.0, h=1.0):
        assert 3 <= len(f.pts) <= 4
        assert all(len(p) == 3 for p in f.pts)


def test_extrude_mat_is_tagged_on_every_face():
    km = _km()
    faces = km.extrude(UNIT_SQUARE, z0=0.0, h=1.0, mat="stone")
    assert all(f.mat == "stone" for f in faces)
    assert all(f.mat == "blank" for f in km.extrude(UNIT_SQUARE, z0=0.0, h=1.0))


# --------------------------------------------------------------- from_boxes
def test_from_boxes_wraps_a_layout_massing_box():
    faces = _km().from_boxes([Box(0, 0, 1, 1, 2, "wall")])
    kinds = Counter(f.kind for f in faces)
    assert kinds == {"top": 1, "bottom": 1, "side": 4}


def test_from_boxes_concatenates_multiple_boxes_without_sharing_faces():
    boxes = [Box(0, 0, 1, 1, 1, "step"), Box(1, 0, 1, 1, 1, "step")]
    assert len(_km().from_boxes(boxes)) == 12  # 6 faces/box, no face merging


# ------------------------------------------------------------------ MODULES
def test_modules_has_exactly_the_nine_named_builders():
    assert set(_km().MODULES) == EXPECTED_MODULES


def test_every_builder_returns_nonempty_deterministic_face_list():
    km = _km()
    for name, builder in km.MODULES.items():
        a, b = builder(), builder()
        assert isinstance(a, list) and len(a) > 0, name
        assert all(isinstance(f, km.Face) for f in a), name
        assert [(f.kind, f.mat, f.pts) for f in a] == [(f.kind, f.mat, f.pts) for f in b], name


# ------------------------------------------------------- shape-specific (C1)
def test_top_cap_and_base_are_thinner_than_wall_band():
    def zspan(faces):
        zs = [p[2] for f in faces for p in f.pts]
        return max(zs) - min(zs)

    MODULES = _km().MODULES
    wall_span = zspan(MODULES["wall_band"]())
    assert zspan(MODULES["top_cap"]()) < wall_span
    assert zspan(MODULES["base"]()) < wall_span


def test_door_and_window_are_standalone_thin_slabs():
    # R2-5 (ROUND 2, AMENDED 2026-07-16): recess_door/recess_window (wall
    # carvings) are replaced by standalone slab OBJECTS — a plain extrude of
    # a w x SLAB_THICK footprint (top, bottom, 2 LARGE front/back faces + 2
    # THIN left/right edge faces). No relation to wall_band's own face
    # count anymore (that comparison was the old carve-contract).
    MODULES = _km().MODULES
    for name in ("door_1x2", "window_1x1"):
        faces = MODULES[name]()
        assert len(faces) == 6, name
        assert Counter(f.kind for f in faces) == {"top": 1, "bottom": 1, "side": 4}, name


def test_door_1x2_and_window_1x1_are_geometrically_distinct():
    MODULES = _km().MODULES
    door = [(f.kind, f.pts) for f in MODULES["door_1x2"]()]
    window = [(f.kind, f.pts) for f in MODULES["window_1x1"]()]
    assert door != window


def test_slab_thickness_matches_the_shared_slab_thick_constant():
    # SLAB_THICK ("10% = 'feet'", ROUND-1 Q2/Q3 answers) drives the slab's
    # own v-extent, shared with the (future, S7) painter-placement inset.
    km = _km()
    for name in ("door_1x2", "window_1x1"):
        vs = [p[1] for f in km.MODULES[name]() for p in f.pts]
        assert max(vs) - min(vs) == pytest.approx(km.SLAB_THICK), name


def test_diag_half_is_a_thin_rotated_quad_extrusion():
    kinds = Counter(f.kind for f in _km().MODULES["diag_half"]())
    assert kinds == {"top": 1, "bottom": 1, "side": 4}


def test_roof_cell_renders_only_the_two_slopes_gable_and_bottom_are_mask_only():
    # ROUND 3 (AMENDED 2026-07-17, S4-REVIEW-ROUNDS.md ROUND 3): the gable
    # end triangles ("roof_edge") and the underside soffit ("roof_inset")
    # are back as real geometry — kit_modules is their source of truth for
    # the enclosure mask — but tagged Face.enclosure so they never render.
    faces = _km().MODULES["roof_cell"]()
    assert Counter(f.kind for f in faces) == {"slope": 2, "gable": 2, "bottom": 1}
    assert len(faces) == 5
    rendered = {f.kind for f in faces if not f.enclosure}
    assert rendered == {"slope"}
    assert {f.enclosure for f in faces if f.kind == "gable"} == {"roof_edge"}
    assert {f.enclosure for f in faces if f.kind == "bottom"} == {"roof_inset"}


def test_stair_45_and_stair_half_are_one_zigzag_solid_tread_riser_render_only():
    # ROUND 4 (S4-REVIEW-ROUNDS.md ROUND 4): each stair is ONE zigzag
    # profile polygon (2D step outline) extruded across width, not STEPS
    # stacked boxes. 2*STEPS+4 faces total: STEPS risers + STEPS treads
    # RENDER; the two profile envelope caps (v=0/v=1), the back wall, and
    # the floor-under-tread stay real geometry (self-occlusion/silhouette),
    # never rendered. ROUND 4b: the two envelope caps are the mask SOURCE
    # (enclosure_masks.lateral_faces), tagged "stair_lateral"; back wall +
    # floor stay "stair_enclosure" — self-occlusion only, never masked.
    MODULES = _km().MODULES
    for name in ("stair_45", "stair_half"):
        faces = MODULES[name]()
        assert len(faces) == 2 * STEPS + 4, name
        rendered = [f for f in faces if not f.enclosure]
        assert len(rendered) == STEPS * 2, name
        assert Counter(f.kind for f in rendered) == {"top": STEPS, "side": STEPS}, name
        enclosure = [f for f in faces if f.enclosure]
        assert len(enclosure) == 4, name
        assert Counter(f.enclosure for f in enclosure) == {"stair_lateral": 2, "stair_enclosure": 2}, name


def test_stair_half_rises_to_half_the_height_of_stair_45():
    def max_z(faces):
        return max(p[2] for f in faces for p in f.pts)

    MODULES = _km().MODULES
    assert max_z(MODULES["stair_half"]()) == pytest.approx(max_z(MODULES["stair_45"]()) / 2)
