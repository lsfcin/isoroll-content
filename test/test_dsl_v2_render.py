#!/usr/bin/env python3
"""test_dsl_v2_render.py — C5 (guide render): scene_guide_render consumes massing v2 (multi-level).

Seam: scene_guide_render.render_scene_panel(...).getextrema() — non-uniform channel (not all-black)
on the multilevel fixture. This is the top of the dependency chain in 3-arch.md's seams list: it
needs T2/T3 (parse), T5 (massing v2, Box.z0), and T7 (render threads z0 through _faces/_fit/_quad
and the painter sort key) all landing together, so expect it to be the last v2 test to go green.
"""
from pathlib import Path

from layout_parse import parse_text
from scene_guide_render import render_scene_panel

FIXTURES = Path(__file__).parent / "fixtures" / "golden"


def test_multilevel_render_is_non_blank():
    layout = parse_text((FIXTURES / "dsl_v2_multilevel.txt").read_text(encoding="utf-8"))
    assert layout.errors == []
    img = render_scene_panel(layout, "NW", 256)
    extrema = img.getextrema()  # ((minR,maxR),(minG,maxG),(minB,maxB))
    assert any(lo != hi for lo, hi in extrema), "expected a non-blank (not all-black) panel"


# ---- C5-seam+ (3-arch.md Amendment, RETURN loop=3 reason=integration-gap) ----
# Loop 5 evidence: scene_guide_render crashes with "min() empty" on the groups fixture --
# massing() currently emits zero boxes for a groups-only scene (no wall/floor/stair cells; R/S
# are markers, not SOLID/STAIRS), so Cam._fit's min(xs)/max(xs) over an empty list raises
# ValueError. Fixing this needs BOTH the empty-massing guard AND the GRP boxes from C3-seam+
# (once GRP boxes exist the list isn't empty; the guard is defense for any future all-void scene).

def test_groups_only_scene_renders_without_crashing():
    """C5-seam+: a group-only scene (1 roof + 1 stair, no walls/floors/plain stairs) must render
    without raising, and produce a non-blank panel (the GRP roof/stair boxes drawn as plain
    z0..z0+h boxes per the Amendment). view="SW" (identity rotation) sidesteps the documented
    rotate_cw group-reorientation limitation, same choice as the C4-seam+ manifest test."""
    layout = parse_text((FIXTURES / "dsl_v2_groups.txt").read_text(encoding="utf-8"))
    assert layout.errors == []
    img = render_scene_panel(layout, "SW", 256)
    extrema = img.getextrema()
    assert any(lo != hi for lo, hi in extrema), "expected a non-blank (not all-black) panel"
