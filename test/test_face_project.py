#!/usr/bin/env python3
"""test_face_project.py — the projection seam after the family parameter replaced the TOP branches.

Pins the two things the refactor could have broken silently: TOP still projects orthographically and
sorts purely by height (its old hand-written branches), and the cardinal camera culls the faces it
sees edge-on instead of painting them as slivers.
"""

import face_project as fp
import kit_modules as km

S, CELL_PX, PAD = 100.0, 512, 4
ORIGIN = (60.0, 70.0)


def _cam(view, family=fp.DIMETRIC):
    return fp.panel_cam(view, S, CELL_PX, PAD, ORIGIN, family)


def test_top_projection_is_the_plain_orthographic_one_the_old_branch_hand_wrote():
    pts = [(0.0, 0.0, 0.0), (1.0, 0.25, 3.0), (0.5, 1.0, -2.0)]
    expected = [(ORIGIN[0] + u * S, ORIGIN[1] + v * S) for u, v, _z in pts]
    assert fp.project_face(pts, "TOP", S, CELL_PX, PAD, ORIGIN) == expected


def test_top_ignores_the_panel_family_it_is_handed():
    """"TOP" is a camera, not a yaw — asking for it under any family must give the plan view."""
    for family in ("dimetric", "cardinal", "top"):
        assert fp.panel_family("TOP", family) == "top"
        assert fp.yaw_deg("TOP") == 0


def test_top_orders_faces_purely_by_height():
    faces = km.MODULES["stair_45"]()
    ordered = fp.ordered_front_faces(faces, "TOP", _cam("TOP"))
    heights = []
    for fid, _k, _m, _poly, _enc in ordered:
        index = int(fid.split(":")[0])
        pts = faces[index].pts
        heights.append(sum(p[2] for p in pts) / len(pts))
    assert heights == sorted(heights), heights


def test_a_yaw_token_projects_the_same_under_the_dimetric_camera_as_the_frozen_engine():
    """Regression guard on the pre-existing dimetric path: yaw the face, then project."""
    pts = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 2.0)]
    cam = _cam("y0")
    assert fp.project_face(pts, "y0", S, CELL_PX, PAD, ORIGIN) == [cam.pt(*p) for p in pts]


def test_cardinal_culls_the_wall_faces_it_sees_edge_on_and_keeps_the_face_on_one():
    """A cardinal camera looks along +u, so u-normal faces render and v-normal faces are edge-on."""
    faces = km.MODULES["wall_band"]()
    dimetric = fp.ordered_faces(faces, "y0", _cam("y0", "dimetric"))
    cardinal = fp.ordered_faces(faces, "y0", _cam("y0", "cardinal"))
    assert len(cardinal) < len(dimetric), "cardinal must cull more than the dimetric octant camera"
    assert cardinal, "cardinal must still render the face-on wall"
    for _fid, _k, _m, poly in cardinal:
        xs = {round(x, 6) for x, _y in poly}
        ys = {round(y, 6) for _x, y in poly}
        assert len(xs) > 1 and len(ys) > 1, "no zero-area sliver may survive the cull"


def test_every_family_renders_at_least_one_face_of_every_module_at_every_view():
    """Loose-end guard: a family/view/module combo that renders nothing would silently drop a cell."""
    for name, builder in km.MODULES.items():
        faces = builder()
        for family in ("dimetric", "cardinal"):
            for view in ("y0", "y45", "y90", "y135", "y180", "y225", "y270", "y315"):
                ordered = fp.ordered_faces(faces, view, _cam(view, family))
                assert ordered, (name, family, view, "renders no face at all")
