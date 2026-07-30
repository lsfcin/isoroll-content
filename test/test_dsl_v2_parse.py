#!/usr/bin/env python3
"""test_dsl_v2_parse.py — C1 (parse): v2 fixtures parse clean; invalid fixtures raise errors.

Seam: layout_parse.parse_text(text).errors — see .loop/dsl-v2-python/3-arch.md DECISION D3, T2/T3.
Expected RED until T2/T3 land: parse_text still reads v1 grammar, so `level N:` lines get
swallowed into the grid itself (as bogus rows, producing unknown-cell errors) instead of being
recognized as level-block headers. This is the root-cause red for every other v2 test file too.
"""
from pathlib import Path

import pytest

from layout_parse import parse_text

FIXTURES = Path(__file__).parent / "fixtures" / "golden"


def _load(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


@pytest.mark.parametrize("fixture", [
    "dsl_v2_lroom.txt",
    "dsl_v2_multilevel.txt",
    "dsl_v2_groups.txt",
])
def test_valid_v2_fixture_parses_clean(fixture):
    layout = parse_text(_load(fixture))
    assert layout.errors == [], f"{fixture}: {layout.errors}"


def test_misplaced_marker_is_an_error():
    """R with no matching roof/stair group line: an authored marker not covered by any
    group's computed voxel span fails the D3 union check."""
    layout = parse_text(_load("dsl_v2_invalid_misplaced_r.txt"))
    assert layout.errors != []


def test_bad_stair_incl_is_an_error():
    """incl must be 2.5 or 5 (ft/cell) — 45deg=5ft or half=2.5ft only (rig.frag stair rule)."""
    layout = parse_text(_load("dsl_v2_invalid_badincl.txt"))
    assert layout.errors != []
    assert any("incl" in e for e in layout.errors)


def test_double_booked_voxel_is_an_error():
    """Two roof groups both claiming cell (0,0) at level 1 (both flat, z=1, so both compute
    voxel span [1,2) for that cell) — the same voxel can't belong to two group surfaces."""
    text = (
        "name: dsl-v2-double-book\n"
        "\n"
        "level 1:\n"
        "R\n"
        "roof: 0,0 0,0 form=flat dir=N incl=5ft z=1 enclose=none\n"
        "roof: 0,0 0,0 form=flat dir=E incl=5ft z=1 enclose=none\n"
    )
    layout = parse_text(text)
    assert layout.errors != []
