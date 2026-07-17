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


def _fm():
    import face_masks
    return face_masks


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
    # roof_cell (ROUND 3): the 5 faces (2 render slopes + 2 mask-only gable
    # + 1 mask-only bottom) now form a full closed shell again — every edge
    # matches exactly one different-normal neighbour (a real fold; no
    # accidental coplanar seam), so every edge is still stroked, same
    # end-tally as the R2-3 open-mesh version, just for the "closed solid"
    # reason this time instead of "unmatched silhouette". stroke_edges
    # itself doesn't know or care which faces will actually render —
    # paint_panel's ordered-filter (kit_module_render.ordered_faces) is
    # what keeps a stripped face's stroke from ever being drawn.
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


# ---------------------------------------------------------------------- ROUND 3: no dangling stroke
def test_no_edge_stroke_pixel_lies_outside_the_rendered_faces_dilated_by_stroke_width():
    # ROUND 3 fix (S4-REVIEW-ROUNDS.md): edges must stroke only edges of
    # faces actually RENDERED in a panel, never a stripped/mask-only face's
    # (which used to dangle past the render silhouette, e.g. past the roof
    # plane). roof_cell now carries real gable/bottom geometry again
    # (enclosure-tagged) — this pins that paint_panel's ink never leaks past
    # the render-only (slope-only) silhouette even so.
    from PIL import ImageFilter

    fe, kmr, skm, fm = _fe(), _kmr(), _skm(), _fm()
    view = "y45"
    faces = km.MODULES["roof_cell"]()
    _img, ordered, origin = kmr.render_panel(faces, view, S, CELL_PX, PAD)
    idmap, _meta = fm.face_mask(ordered, (CELL_PX, CELL_PX))
    binary = idmap.point(lambda p: 255 if p > 0 else 0)
    width = fe.edge_width(CELL_PX)
    dilated = binary.filter(ImageFilter.MaxFilter(2 * width + 1))

    painted = skm.paint_panel("roof_cell", view, ordered, S, CELL_PX, PAD, origin)
    stray = sum(
        1 for (r, g, b, _a), m in zip(painted.getdata(), dilated.getdata())
        if (r, g, b) == fe.INK[:3] and m == 0
    )
    assert stray == 0, stray
