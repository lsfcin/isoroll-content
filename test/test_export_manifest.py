#!/usr/bin/env python3
"""test_export_manifest.py — Loop 4a tests for the export-manifest CLI verb.

Covers C1 (manifest shape + verb wiring), C2 (wall-schema validation),
C3 (round-trip counts vs the layout DSL), C4 (asset resolution) from
.loop/export-manifest/3-arch.md, against the l-room fixture.
"""

import copy
import json
from pathlib import Path

import pytest

from layout_parse import load
from layout_massing import massing
from scene_manifest import build_manifest
from wall_schema import validate_manifest

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = ROOT / "src" / "pipeline" / "layouts" / "l-room.txt"
KIT_DIR = ROOT / "output" / "kit-guide"


@pytest.fixture(scope="module")
def layout():
    return load(LAYOUT)


@pytest.fixture(scope="module")
def manifest(layout):
    return build_manifest(layout, str(KIT_DIR), view="NW")


# --- C1: manifest shape + verb wiring ---

def test_tiles_have_all_fields(manifest):
    required = {"piece", "asset", "facing", "u", "v", "boundHeight", "imageOffset", "pxPerVoxel"}
    assert manifest["tiles"], "expected at least one tile"
    for tile in manifest["tiles"]:
        assert required <= tile.keys(), tile


def test_walls_are_walldefs(manifest):
    required = {"ax", "ay", "bx", "by", "topOffset", "bottomOffset", "config"}
    assert manifest["walls"], "expected at least one wall"
    for wall in manifest["walls"]:
        assert required <= wall.keys(), wall


def test_run_export_cli_verb(tmp_path):
    from export_commands import run_export

    out = tmp_path / "l-room.manifest.json"
    run_export(["--layout", str(LAYOUT), "--kit", str(KIT_DIR), "--view", "NW", "--out", str(out)])
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["scene"] == "l-room"
    assert data["view"] == "NW"
    assert data["tiles"] and data["walls"]


# --- C2: wall-schema validation mirrors wall-types.d.ts ---

def test_validate_clean_manifest_passes(manifest):
    assert validate_manifest(manifest) == []


def test_validate_catches_out_of_range_ax(manifest):
    low = copy.deepcopy(manifest)
    low["walls"][0]["ax"] = -0.1
    assert len(validate_manifest(low)) >= 1

    high = copy.deepcopy(manifest)
    high["walls"][0]["ax"] = 1.1
    assert len(validate_manifest(high)) >= 1


# --- C3: round-trip counts vs the layout DSL (l-room fixture) ---

def test_wall_count_matches_dsl(manifest, layout):
    expected = len([b for b in massing(layout, merge=True) if b.kind == "wall"])
    assert expected == 6  # pinned: l-room has 6 merged wall runs (verified in arch seam)
    assert len(manifest["walls"]) == expected


def test_door_window_stair_tile_counts(manifest):
    doors = [t for t in manifest["tiles"] if t["piece"].startswith("door")]
    windows = [t for t in manifest["tiles"] if t["piece"].startswith("window")]
    stairs = [t for t in manifest["tiles"] if t["piece"] == "stair"]
    assert len(doors) == 1
    assert len(windows) == 1
    assert len(stairs) == 0


# --- C4: asset references resolve against the gray kit output ---

def test_tile_assets_resolve_in_kit(manifest):
    kit_pieces = json.loads((KIT_DIR / "kit.json").read_text())["pieces"]
    resolved_any = False
    for tile in manifest["tiles"]:
        if tile["piece"] in kit_pieces:
            assert (KIT_DIR / tile["asset"]).exists(), tile["asset"]
            resolved_any = True
    assert resolved_any


def test_validate_manifest_flags_missing_asset(manifest):
    bad = copy.deepcopy(manifest)
    changed = False
    for tile in bad["tiles"]:
        if tile["piece"] == "wall":
            tile["asset"] = "does-not-exist.png"
            changed = True
            break
    assert changed
    errs = validate_manifest(bad, kit_dir=str(KIT_DIR))
    assert len(errs) >= 1
