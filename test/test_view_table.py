#!/usr/bin/env python3
"""test_view_table.py — invariants of the 8+1 view table (view_table.py).

These are the code oracles for the "cardinal is one table entry" claim (ROADMAP D2): the derivation
in view_table's docstring is pinned here so nobody re-derives the signs by eye.
"""

import view_table as vt
from scene_guide_render import _proj

_UNIT_CELL = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)]


def _projected_area(view):
    """Shoelace area of the unit ground cell as this view projects it."""
    pts = [vt.project(vt.family(view), u, v, z) for u, v, z in _UNIT_CELL]
    total = 0.0
    for i, (x0, y0) in enumerate(pts):
        x1, y1 = pts[(i + 1) % len(pts)]
        total += x0 * y1 - x1 * y0
    return abs(total) / 2


def test_table_covers_the_nine_facings_as_four_dimetric_four_cardinal_and_top():
    assert set(vt.VIEWS) == set(vt.VIEW_TABLE)
    assert len(vt.VIEWS) == 9
    families = [vt.family(view) for view in vt.VIEWS]
    assert families.count("dimetric") == 4
    assert families.count("cardinal") == 4
    assert families.count("top") == 1


def test_every_family_uses_each_of_the_four_grid_turns_exactly_once():
    for name in ("dimetric", "cardinal"):
        turns = sorted(t for view, (fam, t) in vt.VIEW_TABLE.items() if fam == name)
        assert turns == [0, 1, 2, 3], f"{name} turns: {turns}"
    assert vt.VIEW_TABLE["TOP"] == ("top", 0)


def test_dimetric_projection_is_byte_identical_to_the_legacy_scene_camera():
    """The frozen dimetric camera must not move: scene_guide_render._proj is the pre-existing one."""
    for u, v, z in [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (3.5, -2.25, 1.75), (7, 4, 3)]:
        assert vt.project("dimetric", u, v, z) == _proj(u, v, z)


def test_a_unit_ground_cell_projects_to_the_same_screen_area_in_every_view():
    """Apparent size must not change when the view switches — the cross-view scale invariant."""
    areas = {view: _projected_area(view) for view in vt.VIEWS}
    for view, area in areas.items():
        assert abs(area - 1.0) < 1e-9, f"{view} projects the unit cell to area {area}"


def test_cardinal_sees_walls_face_on_and_dimetric_does_not():
    """Face-on = the run axis perpendicular to the camera has zero screen-y extent."""
    cardinal_dy = vt.project("cardinal", 1, 0, 0)[1] - vt.project("cardinal", 0, 0, 0)[1]
    cardinal_dx = vt.project("cardinal", 0, 1, 0)[0] - vt.project("cardinal", 0, 0, 0)[0]
    assert abs(cardinal_dx) > 0.5 and abs(vt.project("cardinal", 0, 1, 0)[1]) < 1e-9
    assert abs(cardinal_dy) > 0.5, "cardinal must still foreshorten depth, not collapse it"
    for view in ("SW", "SE", "NE", "NW"):
        assert abs(vt.project(vt.family(view), 0, 1, 0)[1]) > 1e-9, f"{view} is not face-on by construction"


def test_cull_axis_is_the_camera_depth_direction_plus_up():
    for view in vt.VIEWS:
        (_ux, uy), (_vx, vy), _zrow = vt.matrix(vt.family(view))
        axis = vt.cull_axis(vt.family(view))
        assert axis[2] == 1.0
        if vt.family(view) != "top":
            assert (axis[0] > 0) == (uy > 0), f"{view} u cull sign disagrees with the projection"
            assert (axis[1] > 0) == (vy > 0), f"{view} v cull sign disagrees with the projection"


def test_height_reads_upward_in_every_view_except_top():
    for view in vt.VIEWS:
        _urow, _vrow, (zx, zy) = vt.matrix(vt.family(view))
        assert zx == 0.0
        assert zy == (0.0 if vt.family(view) == "top" else -1.0)
