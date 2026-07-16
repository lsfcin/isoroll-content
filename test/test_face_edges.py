#!/usr/bin/env python3
"""test_face_edges.py — R2-2 edge-ink contract (design/S4-REVIEW-ROUNDS.md
ROUND 2): thin dark ink strokes along face-polygon edges shared by
different-normal faces, plus the module silhouette. Edges are derived from
face geometry (kit_modules.Face.pts), never pixel/silhouette detection —
`stroke_edges` is tested directly against hand-built and real MODULES
geometry; the last test verifies the actual painted pixel, code-asserted
(iso-visual HARD RULE: geometry verified by code, never model eyes)."""

import kit_modules as km
from kit_modules import Face

CELL_PX, PAD, S = 160, 6, 8.0


def _fe():
    import face_edges
    return face_edges


def _kmr():
    import kit_module_render
    return kit_module_render


def _skm():
    import stage_kit_modules
    return stage_kit_modules


# ---------------------------------------------------------------------- stroke_edges (pure geometry)
def test_closed_box_strokes_every_edge_of_every_face():
    # wall_band: top/bottom differ in normal from every side, and adjacent
    # sides differ in normal from each other (a real corner) — every edge
    # of every face qualifies, so nothing is suppressed.
    faces = km.MODULES["wall_band"]()
    edges = _fe().stroke_edges(faces)
    total_edges = sum(len(f.pts) for f in faces)
    total_stroked = sum(len(v) for v in edges.values())
    assert total_stroked == total_edges


def test_open_cover_strokes_the_shared_ridge_plus_the_unmatched_silhouette():
    # roof_cell (R2-3 cover-only): 2 slope faces share the ridge edge at a
    # different normal (kept) AND each has 3 more edges with no neighbour at
    # all (gable/bottom were struck — open mesh) which must count as
    # silhouette (kept too) — so, same as the closed-box case, every edge
    # survives, just for a different reason (unmatched vs different-normal).
    faces = km.MODULES["roof_cell"]()
    edges = _fe().stroke_edges(faces)
    total_edges = sum(len(f.pts) for f in faces)
    total_stroked = sum(len(v) for v in edges.values())
    assert total_stroked == total_edges


def test_a_shared_edge_between_same_normal_faces_is_not_stroked():
    # Two coplanar quads sharing a seam (no visible fold) — face_edges must
    # NOT draw a line through a flat, uninterrupted surface. Hand-built
    # (kit_modules has no such seam among its own current builders — every
    # real module is either a closed solid or fully open — so this exercises
    # the suppression branch directly).
    left = Face([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], "top")
    right = Face([(1, 0, 0), (2, 0, 0), (2, 1, 0), (1, 1, 0)], "top")
    edges = _fe().stroke_edges([left, right])
    shared = ((1, 0, 0), (1, 1, 0))
    assert shared not in edges[0] and tuple(reversed(shared)) not in edges[0]
    assert len(edges[0]) == 3  # the other 3 edges of `left` are unmatched (silhouette)
    assert len(edges[1]) == 3


# ---------------------------------------------------------------------- edge_width scaling
def test_edge_width_is_about_2px_at_512_and_scales_down_with_cell():
    fe = _fe()
    assert fe.edge_width(512) == 2
    assert fe.edge_width(256) == 1
    assert fe.edge_width(64) >= 1  # never zero-width (invisible)


# ---------------------------------------------------------------------- integration: real painted pixel
def test_paint_panel_draws_dark_ink_at_a_known_different_normal_boundary():
    """Code-verified (not eyeballed): the midpoint of a real top/side shared
    edge of a painted wall_band panel lands on ink-colored pixels."""
    fe, kmr, skm = _fe(), _kmr(), _skm()
    faces = km.MODULES["wall_band"]()
    top_i = next(i for i, f in enumerate(faces) if f.kind == "top")
    p0, p1 = fe.stroke_edges(faces)[top_i][0]
    mid = tuple((a + b) / 2 for a, b in zip(p0, p1))

    view = "y45"
    _img, ordered, origin = kmr.render_panel(faces, view, S, CELL_PX, PAD)
    painted = skm.paint_panel("wall_band", view, ordered, S, CELL_PX, PAD, origin)
    mx, my = kmr.project_face([mid], view, S, CELL_PX, PAD, origin)[0]

    found = any(
        painted.getpixel((int(round(mx)) + dx, int(round(my)) + dy))[:3] == fe.INK[:3]
        for dx in range(-2, 3) for dy in range(-2, 3)
    )
    assert found, (mx, my)
