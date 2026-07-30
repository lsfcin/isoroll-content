#!/usr/bin/env python3
"""test_cabin_golden.py — the PLAYABLE fixture, end to end through the seam, for all 9 views.

The cabin replaces the bare l-room as the fixture that can actually exercise the pipeline: two
rooms, an interior and an exterior door, a window, a stair up to a platform, a roof section, and two
wall materials. It is what a style verdict will eventually be passed on, and what the module loads.

What is goldened: the MANIFEST (exact JSON) for one view per projection family — that is the
contract the module consumes. The assembled PNG is checked by invariants and determinism rather
than pixel-for-pixel at full size: it is a QC preview, not a shipped asset, and a multi-megabyte
pixel golden would break on any Pillow rounding change without telling us anything the invariants
do not. Regenerate goldens with:  python3 test/test_cabin_golden.py --regenerate
"""

import json
from pathlib import Path

import pytest

import kit_arm_a
import render_scene
import view_table as vt
from layout_massing import massing
from layout_parse import load, rotate_cw

CABIN = "src/pipeline/layouts/cabin.txt"
GOLDEN = Path("test/fixtures/golden")
GOLDEN_VIEWS = ("SW", "S", "TOP")  # one per projection family


@pytest.fixture(scope="module")
def cabin():
    layout = load(CABIN)
    assert layout.errors == [], layout.errors
    return layout


@pytest.fixture(scope="module")
def kit_root(tmp_path_factory):
    root = tmp_path_factory.mktemp("kit")
    kit_arm_a.build_all(root)
    return root


def test_the_cabin_fixture_carries_everything_a_style_verdict_needs(cabin):
    """Two rooms, both openings, a stair, a roof and two materials — the l-room had none of this."""
    boxes = massing(cabin, merge=False)
    mats = {box.mat for box in boxes if box.kind in ("wall", "floor")}
    groups = {box.grp.split(":")[0] for box in boxes if box.kind == "GRP"}
    assert len(mats) >= 2, mats
    assert groups == {"roof", "stair"}, groups
    openings = [op.kind for box in boxes for op in box.openings]
    assert openings.count("door") >= 2 and openings.count("window") >= 1, openings


def test_every_view_renders_sprites_and_a_manifest_through_the_seam(cabin, kit_root):
    for view in vt.VIEWS:
        result = render_scene.render_scene(cabin, view, kit_root)
        assert result["view"] == view and result["arm"] == "a"
        assert result["sprites"], view
        manifest = result["manifest"]
        assert manifest["tiles"], view
        assert manifest["walls"], view
        assert manifest["pxPerVoxel"] > 0
        assert manifest["chunk"]["index"] == [0, 0]


def test_every_manifest_tile_resolves_to_a_sprite_this_kit_carries(cabin, kit_root):
    """A tile whose asset does not exist is a silently missing cell — the loose end this catches."""
    for view in vt.VIEWS:
        result = render_scene.render_scene(cabin, view, kit_root)
        for tile in result["manifest"]["tiles"]:
            path = Path(result["kit_dir"]) / tile["asset"]
            assert path.exists(), (view, tile["piece"], tile["mat"], tile["dir"], tile["asset"])


def test_geometry_round_trips_through_all_nine_views(cabin):
    """Walls, group cells and floor area are properties of the scene, not of the view."""
    seen = set()
    for view in vt.VIEWS:
        turned = rotate_cw(cabin, vt.turns(view))
        boxes = massing(turned, merge=False)
        merged = massing(turned, merge=True)
        wall_voxels = sum(box.l * box.d for box in merged if box.kind == "wall")
        groups = sum(1 for box in boxes if box.kind == "GRP")
        floor_area = sum(box.l * box.d for box in boxes if box.kind == "floor")
        seen.add((wall_voxels, groups, floor_area))
    assert len(seen) == 1, seen


def test_both_wall_materials_survive_every_rotation(cabin):
    """The wmat/type overlay is rotated with its cells, so the material mix cannot drift by view."""
    counts = set()
    for view in vt.VIEWS:
        turned = rotate_cw(cabin, vt.turns(view))
        boxes = massing(turned, merge=False)
        stone = sum(1 for box in boxes if box.kind == "wall" and box.mat == "stone")
        wood = sum(1 for box in boxes if box.kind == "wall" and box.mat == "wood")
        counts.add((stone, wood))
    assert len(counts) == 1, counts
    (stone, wood), = counts
    assert stone > 0 and wood > 0


def test_assembled_view_is_deterministic_and_not_blank(cabin, kit_root):
    for view in GOLDEN_VIEWS:
        first = render_scene.render_image(cabin, view, kit_root)
        second = render_scene.render_image(cabin, view, kit_root)
        assert first.tobytes() == second.tobytes(), f"{view} assembly is not deterministic"
        low, high = first.convert("L").getextrema()
        assert high > low, f"{view} assembled to a flat image"


@pytest.mark.parametrize("view", GOLDEN_VIEWS)
def test_manifest_matches_golden(cabin, kit_root, view):
    golden = GOLDEN / f"cabin_{view.lower()}_manifest.json"
    actual = render_scene.render_scene(cabin, view, kit_root)["manifest"]
    expected = json.loads(golden.read_text())
    assert actual == expected


def _regenerate():
    layout = load(CABIN)
    root = Path("/tmp/cabin-kit")
    kit_arm_a.build_all(root)
    for view in GOLDEN_VIEWS:
        manifest = render_scene.render_scene(layout, view, root)["manifest"]
        payload = json.dumps(manifest, indent=2)
        (GOLDEN / f"cabin_{view.lower()}_manifest.json").write_text(payload)
        print(f"wrote cabin_{view.lower()}_manifest.json")


if __name__ == "__main__":
    _regenerate()
