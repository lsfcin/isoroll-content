#!/usr/bin/env python3
"""test_stage_kit_modules.py — 3 arm sheets staged to output/gen-inbox (C4).

Seam: stage_kit_modules.py (T5) — does NOT exist yet on this branch, along
with kit_module_render.py/kit_modules.py it depends on. `_skm()`/`_kmr()`/
`_km()` import them lazily inside each test's call phase (not at module top
level) so a missing module reports one clean FAILED per test instead of
aborting collection for the whole session (see test_kit_modules.py's header
for the verified reason). guide_marks already exists, so it's imported
normally at the top.

Added beyond the Carry `tasks:` T7 file list (which only names
test_kit_modules.py/test_kit_module_render.py) because 3-arch.md's own
Evaluation > seams section requires a C4 assertion ("3 sheet files exist,
bottom-right cell all-black, residue(arm_bc)>0 & residue(arm_b)==0") that has
no home in the other two files — this file is that home.

NOTE for Loop 4b (documented seam decision, not pinned by 3-arch.md): the
`panels` argument shared by sheet_grid/arm_b/arm_bc/arm_a is a list of dicts
{module, view, img, ordered, origin} — one entry per rendered panel. The
architecture names these functions and their intent but not their exact
calling convention; if Loop 4b's natural shape differs, raise
`RETURN loop=4a reason=test-wrong`, don't hand-edit this test.
"""

from PIL import Image

import guide_marks

CELL_PX = 96
PAD = 4


def _kmr():
    import kit_module_render
    return kit_module_render


def _km():
    import kit_modules
    return kit_modules


def _skm():
    import stage_kit_modules
    return stage_kit_modules


def _panels():
    kmr, km = _kmr(), _km()
    names = list(km.MODULES)
    s = kmr.shared_scale(names, cell_px=CELL_PX, pad=PAD)
    panels = []
    for name in names:
        rendered = kmr.render_module(name, s, CELL_PX, PAD)
        for view, (img, ordered, origin) in rendered.items():
            panels.append({"module": name, "view": view, "img": img, "ordered": ordered, "origin": origin})
    return panels


def test_sheet_grid_leaves_the_bottom_right_cell_blank():
    panels = _panels()
    sheet = _skm().sheet_grid(panels).convert("RGB")
    w, h = sheet.size
    cell = sheet.crop((w - CELL_PX, h - CELL_PX, w, h))
    assert all(px == (0, 0, 0) for px in cell.getdata())


def test_arm_b_is_blank_technical_with_zero_cyan_residue():
    sheet = _skm().arm_b(_panels())
    assert guide_marks.residue_count(sheet) == 0


def test_arm_bc_adds_cyan_symbols_over_arm_b():
    sheet_bc = _skm().arm_bc(_panels())
    assert guide_marks.residue_count(sheet_bc) > 0


def test_arm_a_matches_the_sheet_grid_size():
    skm = _skm()
    panels = _panels()
    ordered_by_panel = {(p["module"], p["view"]): p["ordered"] for p in panels}
    sheet_a = skm.arm_a(panels, ordered_by_panel)
    assert sheet_a.size == skm.sheet_grid(panels).size


def test_stage_writes_three_arm_sheets_a_manifest_and_the_three_restyle_prompts(tmp_path):
    out = tmp_path / "gen-inbox"
    _skm().stage(out=str(out))

    pngs = sorted(out.glob("*.png"))
    sheets = [p for p in pngs if Image.open(p).width > CELL_PX]
    assert len(sheets) == 3, [p.name for p in pngs]

    assert list(out.glob("*.json")), "expected a sheet manifest json"

    prompts = sorted(p.name for p in out.glob("restyle_arm_*.md"))
    assert prompts == ["restyle_arm_a.md", "restyle_arm_b.md", "restyle_arm_bc.md"]
