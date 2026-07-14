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
EXPECTED_MODULES = {
    "wall_band", "top_cap", "base", "recess_door", "recess_window",
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


def test_recess_builders_split_the_opening_side_into_more_faces_than_plain_wall():
    MODULES = _km().MODULES
    wall_sides = sum(1 for f in MODULES["wall_band"]() if f.kind == "side")
    door_sides = sum(1 for f in MODULES["recess_door"]() if f.kind == "side")
    window_sides = sum(1 for f in MODULES["recess_window"]() if f.kind == "side")
    assert door_sides > wall_sides
    assert window_sides > wall_sides


def test_recess_door_and_recess_window_are_geometrically_distinct():
    MODULES = _km().MODULES
    door = [(f.kind, f.pts) for f in MODULES["recess_door"]()]
    window = [(f.kind, f.pts) for f in MODULES["recess_window"]()]
    assert door != window


def test_diag_half_is_a_thin_rotated_quad_extrusion():
    kinds = Counter(f.kind for f in _km().MODULES["diag_half"]())
    assert kinds == {"top": 1, "bottom": 1, "side": 4}


def test_roof_cell_is_a_triangular_prism_wedge():
    faces = _km().MODULES["roof_cell"]()
    kinds = Counter(f.kind for f in faces)
    assert kinds == {"gable": 2, "slope": 2, "bottom": 1}
    assert len(faces) == 5


def test_stair_45_and_stair_half_are_built_from_steps_worth_of_boxes():
    MODULES = _km().MODULES
    # from_boxes emits 6 faces/box (no face-sharing); STEPS sub-boxes per stair cell (arch T1).
    assert len(MODULES["stair_45"]()) == STEPS * 6
    assert len(MODULES["stair_half"]()) == STEPS * 6


def test_stair_half_rises_to_half_the_height_of_stair_45():
    def max_z(faces):
        return max(p[2] for f in faces for p in f.pts)

    MODULES = _km().MODULES
    assert max_z(MODULES["stair_half"]()) == pytest.approx(max_z(MODULES["stair_45"]()) / 2)
