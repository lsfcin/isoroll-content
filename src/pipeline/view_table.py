#!/usr/bin/env python3
"""view_table.py — the 8+1 view table: one entry per view (projection matrix + backface-cull axis).

A view is a FAMILY (how the camera projects the ground plane) plus TURNS (how many clockwise grid
rotations put that camera behind the named compass corner). Both dimetric and cardinal views are
therefore ONE table entry each (SCENE-CREATION.md § 8+1 views, ROADMAP D2) — cardinal is not a new
art regime under a deterministic renderer, just a different projection matrix + cull axis.

Family derivation (pinned by test/test_view_table.py, never re-derived by hand):
    x = k * (R . (u,v)),   y = k * r * (D . (u,v)) - z
with R the ground direction that maps to screen-right, D the one that maps to screen-down (= the
direction the camera sits along, so bigger D-component means nearer the viewer), k = sqrt(2) and
r = 0.5 the 2:1 dimetric constants already baked into scene_guide_render.

    dimetric  R=(1,-1)/sqrt2  D=(1,1)/sqrt2  -> x = u-v,          y = 0.5(u+v) - z   [pre-existing]
    cardinal  R=(0,-1)        D=(1,0)        -> x = -sqrt2 * v,    y = (sqrt2/2)u - z
    top       plan view, no z term                                y = v

Rotating D from (1,1)/sqrt2 to (1,0) is a -45 deg turn; R gets the same turn, which is what fixes
cardinal's signs (and hence which compass name each turn count carries). Consequence worth stating
because it is the invariant test: every family projects a unit ground cell to the SAME screen area
(dimetric rhombus 2x1 /2 = 1; cardinal rect sqrt2 x sqrt2/2 = 1; top square 1x1 = 1), so a piece
does not change apparent size when the view switches.
"""

_SQRT2 = 2 ** 0.5

# (u -> (x,y), v -> (x,y), z -> (x,y)) — see the derivation in the module docstring.
_DIMETRIC = ((1.0, 0.5), (-1.0, 0.5), (0.0, -1.0))
_CARDINAL = ((0.0, _SQRT2 / 2), (-_SQRT2, 0.0), (0.0, -1.0))
_TOP = ((1.0, 0.0), (0.0, 1.0), (0.0, 0.0))

# cull axis = (D_u, D_v, 1): the camera's look-toward-viewer direction, dotted with a face normal
# in kit_module_render._front_facing. Dimetric's (1,1,1) is the pre-existing value.
FAMILIES = {
    "dimetric": {"matrix": _DIMETRIC, "cull": (1.0, 1.0, 1.0)},
    "cardinal": {"matrix": _CARDINAL, "cull": (1.0, 0.0, 1.0)},
    "top": {"matrix": _TOP, "cull": (0.0, 0.0, 1.0)},
}

# view -> (family, clockwise grid turns). Dimetric names/turns are the frozen pre-existing table;
# cardinal ones follow from it: the cardinal camera at +u sits between the SW (+u+v) and SE (+u-v)
# dimetric cameras, so it carries the compass name between SW and SE, i.e. S — and the turn order
# then advances the same way the dimetric one does.
VIEW_TABLE = {
    "SW": ("dimetric", 0), "SE": ("dimetric", 1), "NE": ("dimetric", 2), "NW": ("dimetric", 3),
    "S": ("cardinal", 0), "E": ("cardinal", 1), "N": ("cardinal", 2), "W": ("cardinal", 3),
    "TOP": ("top", 0),
}

# Facing vocabulary order (core/skills/iso-visual.md, module `Facing` type).
VIEWS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW", "TOP")

# Back-compatible alias: callers that only need the grid rotation (scene_assemble, scene_manifest,
# scene_anchors, scene_guide_render) keep indexing this by view name, now for all 9 views.
VIEW_TURNS = {view: turns for view, (_family, turns) in VIEW_TABLE.items()}


DIMETRIC = "dimetric"  # the pre-existing default family — what every legacy caller renders under


def family(view):
    """Projection family of a view — "dimetric" | "cardinal" | "top"."""
    return VIEW_TABLE[view][0]


def turns(view):
    """Clockwise grid rotations that put the camera behind this view's compass corner."""
    return VIEW_TABLE[view][1]


def matrix(family_name):
    """The family's 3x2 projection matrix ((ux,uy),(vx,vy),(zx,zy))."""
    return FAMILIES[family_name]["matrix"]


def cull_axis(family_name):
    """The family's backface-cull axis (camera look-toward-viewer direction, ground part + up)."""
    return FAMILIES[family_name]["cull"]


def project(family_name, u, v, z):
    """Unit-scale screen (x, y) of a world point in this family (no scale, no origin applied)."""
    (ux, uy), (vx, vy), (zx, zy) = matrix(family_name)
    x = u * ux + v * vx + z * zx
    y = u * uy + v * vy + z * zy
    return x, y


def depth_key(family_name, u, v, z):
    """Painter-order key (far -> near, ascending): ground depth along the camera axis, then height.

    One expression for all three families because the ground part IS the cull axis: dimetric gives
    the pre-existing (u+v, z), cardinal gives (u, z), top gives (0, z) — a plan view stacks purely
    by height, which is what kit_module_render's old TOP branch did by hand.
    """
    axis = cull_axis(family_name)
    return (u * axis[0] + v * axis[1], z)
