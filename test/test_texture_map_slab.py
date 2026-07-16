#!/usr/bin/env python3
"""test_texture_map_slab.py — R2-5 door_1x2/window_1x1 slab FAMILY/flip_h
contract (design/S4-REVIEW-ROUNDS.md ROUND 2, AMENDED 2026-07-16), split out
of test_texture_map.py to stay under the per-file line gate.

Split from recess_decals coverage: R2-5 replaced recess_door/recess_window
(wall-carve openings) with standalone slab OBJECTS — the wall-with-a-hole is
emergent at assembly (S4t), not texture_map's concern anymore. What survives
here is the slab's own face->texture resolution (front/back LARGE faces get
the object's own decal, thin edges get plain wood) plus the back-face
`flip_h` contract (ROUND-1 Q2 answer): the back face's texture is mirrored
so real-world hardware (handle/keyhole) sits on the same physical edge seen
from either side — code-asserted decal placement, never eyeballed
(iso-visual HARD RULE)."""

import kit_modules as km


def _tm():
    import texture_map
    return texture_map


def _large_and_thin(module):
    """(front, back, [thin edges]) — front/back are the two v-constant LARGE
    side faces (v=0 / v=SLAB_THICK), thin are the two u-constant edge faces.
    Split by inspecting `.pts` directly, same pattern
    test_texture_warp.py's face_axes tests already use."""
    sides = [f for f in km.MODULES[module]() if f.kind == "side"]
    front = next(f for f in sides if {round(v, 6) for _u, v, _z in f.pts} == {0.0})
    back = next(f for f in sides if {round(v, 6) for _u, v, _z in f.pts} == {round(km.SLAB_THICK, 6)})
    thin = [f for f in sides if f not in (front, back)]
    return front, back, thin


def test_door_front_and_back_use_the_pinned_decal_id():
    tm = _tm()
    front, back, _thin = _large_and_thin("door_1x2")
    for f in (front, back):
        spec = tm.face_texture("door_1x2", "side", f.pts, "blank")
        assert spec["id"] == "door_1x2x0" and spec["type"] == "decal"


def test_window_front_and_back_use_the_pinned_decal_id():
    tm = _tm()
    front, back, _thin = _large_and_thin("window_1x1")
    for f in (front, back):
        assert tm.face_texture("window_1x1", "side", f.pts, "blank")["id"] == "window_1x1x0"


def test_door_thin_edges_and_caps_are_plain_wood_not_the_decal():
    tm = _tm()
    _front, _back, thin = _large_and_thin("door_1x2")
    caps = [f for f in km.MODULES["door_1x2"]() if f.kind in ("top", "bottom")]
    for f in thin + caps:
        spec = tm.face_texture("door_1x2", f.kind, f.pts, "blank")
        assert spec["id"] != "door_1x2x0", f.kind


def test_flip_h_is_true_only_on_a_slabs_back_face():
    tm = _tm()
    front, back, thin = _large_and_thin("door_1x2")
    assert tm.face_texture("door_1x2", "side", front.pts, "blank")["flip_h"] is False
    assert tm.face_texture("door_1x2", "side", back.pts, "blank")["flip_h"] is True
    for f in thin:
        assert tm.face_texture("door_1x2", "side", f.pts, "blank")["flip_h"] is False


def test_flip_h_is_false_for_every_non_slab_face():
    tm = _tm()
    top = [f for f in km.MODULES["wall_band"]() if f.kind == "top"][0]
    assert tm.face_texture("wall_band", "top", top.pts, "wood")["flip_h"] is False
