#!/usr/bin/env python3
"""test_dsl_v2_manifest.py — C4 (manifest): tile.z / wall.dir / boundHeight + HUD counts.

Seam: scene_manifest.build_manifest fields (T6) + count_hud() (T6, rig.frag updateHud L1073-1084:
walls/diags count VOXELS, D/W count RUNS, stairs = stair-group count, roofs = groups - stairs).
Reuses the existing gray kit fixture (output/kit-guide), same pattern as test_export_manifest.py.
Counts below are hand-derived per fixture (shown inline) from dsl_v2_multilevel.txt / _groups.txt.
"""
from pathlib import Path

from layout_groups import grp_base_data, grp_cell_voxels
from layout_parse import parse_text
from scene_manifest import build_manifest, count_hud

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "golden"
KIT_DIR = ROOT / "output" / "kit-guide"


def _layout(fixture):
    return parse_text((FIXTURES / fixture).read_text(encoding="utf-8"))


def test_hud_counts_multilevel():
    layout = _layout("dsl_v2_multilevel.txt")
    assert layout.errors == []
    hud = count_hud(layout)
    # 2 levels x 4x4 ring (12 '#' voxels/level = 24 total); level 1 has one 'D' cell whose
    # level-0 same-cell neighbor is '.', so it's a new run (doors=1); floors: 4 (lvl0) + 3 (lvl1,
    # one floor cell replaced by the door) = 7.
    assert hud == {"walls": 24, "doors": 1, "windows": 0, "floors": 7, "stairs": 0, "roofs": 0}


def test_hud_counts_groups():
    layout = _layout("dsl_v2_groups.txt")
    assert layout.errors == []
    hud = count_hud(layout)
    # R/S marker chars count toward neither walls nor floors (rig.frag only counts "#"/diag
    # and "."); stairs/roofs come from the Group list itself: 1 stair group, 1 roof group.
    assert hud == {"walls": 0, "doors": 0, "windows": 0, "floors": 0, "stairs": 1, "roofs": 1}


def test_manifest_tile_z_field_multilevel():
    layout = _layout("dsl_v2_multilevel.txt")
    manifest = build_manifest(layout, str(KIT_DIR), view="NW")
    assert manifest["tiles"], "expected at least one tile"
    for tile in manifest["tiles"]:
        assert "z" in tile, tile


def test_manifest_wall_dir_and_bound_height_multilevel():
    layout = _layout("dsl_v2_multilevel.txt")
    manifest = build_manifest(layout, str(KIT_DIR), view="NW")
    assert manifest["walls"], "expected at least one wall run"
    for wall in manifest["walls"]:
        assert "dir" in wall, wall
        assert wall["boundHeight"] > 0


# ---- C4-seam+ (3-arch.md Amendment, RETURN loop=3 reason=integration-gap) ----
# Loop 5 evidence: groups fixture -> manifest tiles=0. massing() emitting no GRP boxes (C3-seam+)
# cascades here: _piece_for(box) never sees a "GRP" box so build_manifest's tile loop stays
# empty. view="SW" (VIEW_TURNS["SW"]==0, identity rotation) is used deliberately -- rotate_cw
# does NOT re-orient group cells/dir (documented limitation in layout_parse.rotate_cw), so any
# other view would desync tile (u,v) from the group cells' original (c,r); that desync is out of
# scope for this seam.

def test_manifest_group_cell_placements_groups_fixture():
    """C4-seam+: build_manifest on the groups fixture must produce len(tiles)>0, with one tile
    placement per group cell where tile.z == that cell's grp_cell_voxels vox_lo and
    tile.boundHeight == vox_hi - vox_lo (same spans frozen in test_dsl_v2_massing.py's
    test_groups_fixture_emits_one_grp_box_per_group_cell_matching_voxel_span)."""
    layout = _layout("dsl_v2_groups.txt")
    assert layout.errors == []

    expected = {}
    for group in layout.groups:
        base = grp_base_data(group)
        for (r, c) in group.cells:
            expected[(r, c)] = grp_cell_voxels(base, group, r, c)

    manifest = build_manifest(layout, str(KIT_DIR), view="SW")
    assert manifest["tiles"], "expected at least one tile for the groups fixture"

    found = {(t["v"], t["u"]): (t["z"], t["z"] + t["boundHeight"]) for t in manifest["tiles"]}
    for (r, c), (vox_lo, vox_hi) in expected.items():
        assert (r, c) in found, f"no tile placement at cell (r={r}, c={c})"
        assert found[(r, c)] == (vox_lo, vox_hi), (
            f"cell (r={r},c={c}) tile span {found[(r, c)]} != expected {(vox_lo, vox_hi)}"
        )
