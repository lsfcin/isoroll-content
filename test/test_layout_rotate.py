#!/usr/bin/env python3
"""test_layout_rotate.py — rotation is a remap of the SAME physical scene, for all 9 views.

The 8+1 view table only works because rotate_cw rotates everything keyed by a cell: the grid, each
level's per-cell overlays (side/type/wmat/fh) and every roof/stair group (cells + ascent arrow).
Before this, groups and overlays were carried over unrotated, so a rotated view showed a stair
pointing the wrong way and materials painted onto other cells. These are the invariants that make
that unshippable.
"""

import layout_rotate as lr
import view_table as vt
from layout_groups import grp_base_data, grp_cell_voxels
from layout_massing import massing
from layout_parse import load, parse_text, rotate_cw

_GROUPS_FIXTURE = "test/fixtures/golden/dsl_v2_groups.txt"
_WMAT_LAYOUT = """name: wmat-probe

level 0:
####
#..#
####
layer wmat:
....
.w..
....
"""


def _group_spans(layout):
    """Per-group multiset of (voxLo, voxHi) over its cells — the group's physical shape."""
    spans = []
    for group in layout.groups:
        base = grp_base_data(group)
        cells = sorted(grp_cell_voxels(base, group, r, c) for (r, c) in group.cells)
        spans.append((group.kind, group.form, group.z, cells))
    return sorted(spans)


def test_four_turns_is_the_identity_on_grid_groups_and_overlays():
    layout = load(_GROUPS_FIXTURE)
    turned = rotate_cw(layout, 4)
    assert [level.g for level in turned.levels.values()] == [level.g for level in layout.levels.values()]
    assert [(g.cells, g.dir) for g in turned.groups] == [(g.cells, g.dir) for g in layout.groups]


def test_group_shape_survives_every_rotation():
    layout = load(_GROUPS_FIXTURE)
    expected = _group_spans(layout)
    for turns in range(4):
        assert _group_spans(rotate_cw(layout, turns)) == expected, f"turns={turns}"


def test_group_ascent_arrow_advances_one_step_clockwise_per_turn():
    layout = load(_GROUPS_FIXTURE)
    stair = [g for g in layout.groups if g.kind == "stair"][0]
    seen = []
    for turns in range(4):
        turned_stair = [g for g in rotate_cw(layout, turns).groups if g.kind == "stair"][0]
        seen.append(turned_stair.dir)
    assert seen == [stair.dir, lr.rotate_arrow(stair.dir), lr.rotate_arrow(stair.dir, 2),
                    lr.rotate_arrow(stair.dir, 3)]
    assert len(set(seen)) == 4, "a stair must point somewhere different in each rotation"


def test_a_material_overlay_travels_with_its_own_cell():
    layout = parse_text(_WMAT_LAYOUT)
    assert layout.errors == []
    assert layout.levels[0].wmat == {"1,1": "w"}
    for turns in range(4):
        turned = rotate_cw(layout, turns)
        assert len(turned.levels[0].wmat) == 1, f"turns={turns} lost the overlay"
        key = next(iter(turned.levels[0].wmat))
        r, c = (int(part) for part in key.split(","))
        assert turned.levels[0].g[r][c] == ".", f"turns={turns} put wmat on {turned.levels[0].g[r][c]!r}"


def test_wall_count_round_trips_through_every_one_of_the_nine_views():
    """The module-side oracle in content form: walls are a property of the scene, not of the view."""
    layout = load("src/pipeline/layouts/l-room.txt")
    counts = {}
    for view in vt.VIEWS:
        turned = rotate_cw(layout, vt.turns(view))
        walls = [box for box in massing(turned, merge=True) if box.kind == "wall"]
        voxels = sum(box.l * box.d for box in walls)
        counts[view] = voxels
    assert len(set(counts.values())) == 1, counts


def test_group_cell_count_round_trips_through_every_one_of_the_nine_views():
    layout = load(_GROUPS_FIXTURE)
    counts = {}
    for view in vt.VIEWS:
        turned = rotate_cw(layout, vt.turns(view))
        counts[view] = len([box for box in massing(turned, merge=False) if box.kind == "GRP"])
    assert len(set(counts.values())) == 1, counts
    assert counts[vt.VIEWS[0]] > 0
