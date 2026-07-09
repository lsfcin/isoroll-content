#!/usr/bin/env python3
"""test_scene_manifest_kit_meta.py — Loop 4a (re-run) tests for the metadata-only kit seam.

Closes the integration gap raised in .loop/export-manifest/5-user.md
(FLAG: RETURN loop=3 reason=integration-gap): build_manifest must not require
kit piece PNGs on disk, only kit.json metadata — otherwise a missing-asset kit
crashes on an eager PIL Image.open() before wall_schema.validate_manifest's
graceful [FAIL] path ever runs. See .loop/export-manifest/3-arch.md
"Architecture (re-run after RETURN loop=3 reason=integration-gap)" for the
design: new `scene_assemble.load_kit_meta(kit_dir)` (kit.json only, no PIL),
`build_manifest` switched from `load_kit` to `load_kit_meta`.

The CLI-level graceful-fail path (nonzero exit, no traceback, real subprocess)
is already covered by test/e2e_export_manifest.py step 6 — not duplicated
here. This file covers only the unit-level seam named in the architecture:
build_manifest succeeding against a kit dir containing ONLY kit.json.

Does not touch test/test_export_manifest.py (existing Loop 4a tests untouched
per the re-run instructions).
"""

import json
import shutil
from pathlib import Path

import pytest

from layout_parse import load
from scene_manifest import build_manifest

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = ROOT / "src" / "pipeline" / "layouts" / "l-room.txt"
KIT_DIR = ROOT / "output" / "kit-guide"


@pytest.fixture(scope="module")
def layout():
    return load(LAYOUT)


@pytest.fixture
def metadata_only_kit_dir(tmp_path):
    """A kit dir with kit.json but none of the piece PNGs — the state a
    hand-painted kit is routinely in mid-development (5-user.md's scenario)."""
    dest = tmp_path / "kit-meta-only"
    dest.mkdir()
    shutil.copy(KIT_DIR / "kit.json", dest / "kit.json")
    return dest


# --- new seam: metadata-only kit dir (no PNGs) ---

def test_load_kit_meta_reads_json_without_pngs(metadata_only_kit_dir):
    from scene_assemble import load_kit_meta

    meta = load_kit_meta(str(metadata_only_kit_dir))
    expected = json.loads((KIT_DIR / "kit.json").read_text())
    assert meta == expected
    assert "pieces" in meta and "px_per_unit" in meta


def test_build_manifest_succeeds_against_metadata_only_kit(layout, metadata_only_kit_dir):
    manifest = build_manifest(layout, str(metadata_only_kit_dir), view="NW")
    assert manifest["tiles"]
    assert manifest["walls"]
    expected_px_per_unit = json.loads((KIT_DIR / "kit.json").read_text())["px_per_unit"]
    assert manifest["pxPerVoxel"] == expected_px_per_unit
