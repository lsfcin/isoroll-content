#!/usr/bin/env python3
"""face_edges.py — thin dark ink edge lines along face-polygon boundaries
(R2-2, design/S4-REVIEW-ROUNDS.md ROUND 2): stroked where two faces meet at
different world normals, plus the module silhouette (an edge with no
matching neighbour at all — open covers like roof_cell/stairs, R2-3/R2-4,
aren't closed solids). Edges are derived from `kit_modules.Face.pts` by
matching shared 3D corner-pairs across faces — geometry known by
construction, never pixel/silhouette detection on the rendered image
(iso-visual HARD RULE: geometry verified by code, not eyes).

`stroke_edges` is view-agnostic (same world-space edges feed every one of
the 9 panels, R1); callers project per-view with
`kit_module_render.project_face` and draw in the SAME far->near order the
painter already composites faces in, so a farther face's ink is correctly
overpainted by a nearer face's opaque texture — the same last-write-wins
occlusion `paint_panel`'s texture loop already relies on, not a second,
inconsistent occlusion test.
"""

INK = (58, 58, 58, 255)  # linework.py's INK ("#3a3a3a"), full opacity
REF_CELL_PX = 512
REF_WIDTH = 2
_TOL = 1e-6


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _normal(pts):
    p0, p1, p2 = pts[0], pts[1], pts[2]
    v1 = tuple(y - x for x, y in zip(p0, p1))
    v2 = tuple(y - x for x, y in zip(p0, p2))
    n = _cross(v1, v2)
    mag = sum(c * c for c in n) ** 0.5
    return tuple(c / mag for c in n) if mag > 1e-12 else (0.0, 0.0, 0.0)


def _same_pt(a, b):
    return all(abs(x - y) < _TOL for x, y in zip(a, b))


def _edges(pts):
    n = len(pts)
    return [(pts[i], pts[(i + 1) % n]) for i in range(n)]


def _shared(e1, e2):
    """Two faces walk a shared boundary in OPPOSITE order (both CCW around
    their own interior), so a shared edge is (a,b) on one face and (b,a) on
    the other — never (a,b)/(a,b)."""
    (a0, a1), (b0, b1) = e1, e2
    return _same_pt(a0, b1) and _same_pt(a1, b0)


def stroke_edges(faces):
    """dict[face_index -> [(p0, p1), ...]] world-space edges to stroke for
    that face: silhouette edges (no neighbour anywhere) plus edges shared
    with a different-normal neighbour. Faces with a matching same-normal
    neighbour (e.g. two coplanar quads that happen to share a seam) are
    left unstroked there — no fold line where there's no visible fold."""
    normals = [_normal(f.pts) for f in faces]
    edge_lists = [_edges(f.pts) for f in faces]
    result = {i: [] for i in range(len(faces))}
    for i, edges_i in enumerate(edge_lists):
        for e in edges_i:
            matched = False
            diff_normal = False
            for j, edges_j in enumerate(edge_lists):
                if j == i:
                    continue
                for e2 in edges_j:
                    if _shared(e, e2):
                        matched = True
                        dot = sum(a * b for a, b in zip(normals[i], normals[j]))
                        if dot < 0.999:
                            diff_normal = True
                        break
                if matched:
                    break
            if not matched or diff_normal:
                result[i].append(e)
    return result


def edge_width(cell_px):
    """~REF_WIDTH px at REF_CELL_PX, scaled linearly with cell size."""
    return max(1, round(REF_WIDTH * cell_px / REF_CELL_PX))


def draw_face_edges(draw, edges, view, s, cell_px, pad, origin, project_face):
    """Stroke `edges` (this face's [(p0,p1),...] from `stroke_edges`) onto
    `draw` (an ImageDraw bound to the panel canvas already painted up to and
    including this face) — call right after pasting the face's own texture
    so nearer faces painted later naturally overpaint ink that lands under
    them, matching the existing painter occlusion convention."""
    width = edge_width(cell_px)
    for p0, p1 in edges:
        (x0, y0), (x1, y1) = project_face([p0, p1], view, s, cell_px, pad, origin)
        draw.line([(x0, y0), (x1, y1)], fill=INK, width=width)
