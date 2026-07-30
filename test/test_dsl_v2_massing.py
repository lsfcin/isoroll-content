#!/usr/bin/env python3
"""test_dsl_v2_massing.py — C3 (massing): per-cell Z-run boxes match rig semantics.

Seam: layout_massing.massing() Box list (T5) + layout_groups pure geometry (T1). Two layers of
test: (a) isolated geometry unit tests for grp_base_data/grp_cell_voxels, hand-derived from
rig.frag L423-443 for a flat roof and a shed1 stair (derivation recorded in
.loop/dsl-v2-python/4a-tests.md and mirrored by the dsl_v2_groups.txt fixture); (b) Box.z0
(DECISION D1) on the simplest possible v2 fixture — a lone wall voxel, no groups, no Z-merge
branching — so the new field is exercised without needing the full group pipeline.
"""
from pathlib import Path

from layout_groups import grp_base_data, grp_cell_voxels
from layout_massing import massing
from layout_parse import Group, parse_text

FIXTURES = Path(__file__).parent / "fixtures" / "golden"


# ---- C3a: pure group geometry (hand-derived, rig.frag L423-443) ----

def test_flat_roof_spans_one_level():
    """Flat form: hAt is constant == z everywhere, so the surface always spans exactly
    [floor(z), floor(z)+1) — one level, regardless of cell position within the bbox."""
    roof = Group(kind="roof", cells=[(0, 0), (0, 1), (0, 2), (0, 3)], form=0, dir="^", incl=5, z=1, enclose=0)
    base = grp_base_data(roof)
    for (r, c) in roof.cells:
        assert grp_cell_voxels(base, roof, r, c) == (1, 2)


def test_shed1_stair_spans_rise_with_position():
    """dir=E (">"), incl=5 -> rise=incl/5=1 voxel/cell. z=0. 2-cell bbox (1,0)-(1,1): cell
    (1,0) sits low (span [0,1)); cell (1,1) is one rise higher (span [1,2)) — this is the
    exact derivation frozen into the dsl_v2_groups.txt fixture's stair line."""
    stair = Group(kind="stair", cells=[(1, 0), (1, 1)], form=0, dir=">", incl=5, z=0)
    base = grp_base_data(stair)
    assert grp_cell_voxels(base, stair, 1, 0) == (0, 1)
    assert grp_cell_voxels(base, stair, 1, 1) == (1, 2)


# ---- C3b: Box.z0 on the simplest fixture (no groups, no merge ambiguity) ----

def test_box_has_z0_single_level_wall():
    """A lone wall cell at level 0 should still produce a Box with z0 == 0.0 (DECISION D1:
    default keeps single-level back-compat)."""
    layout = parse_text("name: single-wall\n\nlevel 0:\n#\n")
    assert layout.errors == []
    boxes = massing(layout)
    wall_boxes = [b for b in boxes if b.kind == "wall"]
    assert len(wall_boxes) == 1
    assert wall_boxes[0].z0 == 0.0


# ---- C3-seam+ (3-arch.md Amendment, RETURN loop=3 reason=integration-gap) ----
# Loop 5 evidence: massing() never calls grp_base_data/grp_cell_voxels, so the groups fixture
# produced zero boxes (no wall/floor/stair cells either — R/S are markers, not SOLID/STAIRS).
# This is the escape the Amendment sharpened: massing() must emit one GRP box per group cell,
# z0/h == that cell's grp_cell_voxels span — the exact spans frozen above by
# test_flat_roof_spans_one_level / test_shed1_stair_spans_rise_with_position.

def test_groups_fixture_emits_one_grp_box_per_group_cell_matching_voxel_span():
    """C3-seam+: massing() on the dsl_v2_groups.txt fixture (1 flat roof, 4 cells + 1 shed1
    stair, 2 cells) must emit a "GRP" box per group cell whose (z0, z0+h) equals that cell's
    grp_cell_voxels span (D0: per-cell Z-run, not a merged run — groups have no run-merge
    concept). Box position: v0==r, u0==c (layout.kind(u,v) convention: grid[v][u])."""
    layout = parse_text((FIXTURES / "dsl_v2_groups.txt").read_text(encoding="utf-8"))
    assert layout.errors == []
    assert layout.groups, "fixture must parse 2 groups (1 roof, 1 stair)"

    expected = {}
    for group in layout.groups:
        base = grp_base_data(group)
        for (r, c) in group.cells:
            expected[(r, c)] = grp_cell_voxels(base, group, r, c)

    boxes = massing(layout)
    grp_boxes = [b for b in boxes if b.kind == "GRP"]
    assert len(grp_boxes) == len(expected), (
        f"expected {len(expected)} GRP boxes (one per group cell), got {len(grp_boxes)}"
    )

    found = {(b.v0, b.u0): (b.z0, b.z0 + b.h) for b in grp_boxes}
    for (r, c), (vox_lo, vox_hi) in expected.items():
        assert (r, c) in found, f"no GRP box at cell (r={r}, c={c})"
        assert found[(r, c)] == (vox_lo, vox_hi), (
            f"cell (r={r},c={c}) span {found[(r, c)]} != expected {(vox_lo, vox_hi)}"
        )
