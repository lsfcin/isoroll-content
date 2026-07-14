#!/usr/bin/env python3
"""test_dsl_v2_serialize.py — C2 (round-trip): to_dsl(parse_text(text)) == text, per fixture.

Seam: layout_serialize.to_dsl (T4, NEW module) + layout_parse.parse_text (T2/T3). Comparison is
per-line-rstripped (trailing whitespace insignificant — mirrors rig.frag updateDsl's own
`.replace(/\\s+$/,'')` on every emitted grid row).
"""
from pathlib import Path

import pytest

from layout_parse import parse_text
from layout_serialize import to_dsl

FIXTURES = Path(__file__).parent / "fixtures" / "golden"


@pytest.mark.parametrize("fixture", [
    "dsl_v2_lroom.txt",
    "dsl_v2_multilevel.txt",
    "dsl_v2_groups.txt",
])
def test_round_trip(fixture):
    original = (FIXTURES / fixture).read_text(encoding="utf-8")
    layout = parse_text(original)
    assert layout.errors == [], f"fixture must parse clean before round-trip: {layout.errors}"
    reserialized = to_dsl(layout)
    assert [ln.rstrip() for ln in reserialized.splitlines()] == [ln.rstrip() for ln in original.splitlines()]
