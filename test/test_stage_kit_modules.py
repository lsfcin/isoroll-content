#!/usr/bin/env python3
"""test_stage_kit_modules.py — per-module arm sheets staged to
output/gen-inbox (C4, C5). AMENDED 2026-07-16 (Loop 4a, arm-a-homography,
ruling R2/R3 — see .loop/arm-a-homography/1-plan.md): the mega-sheet
contract ("exactly 3 arm sheets") is a SANCTIONED, user-authorized contract
change to sheet-per-object (`{module}__{arm}.png` stem pairs), not a fudge.
Assertions below are amended in place per R2's own instruction ("AMENDED,
not fudged"); nothing is deleted, the file's coverage (grid blank corner,
zero/nonzero cyan residue, size agreement, file-count contract) is preserved
under the new shape.

Seam: stage_kit_modules.py — arm_b/arm_bc/sheet_grid/arm_a keep their
existing `(panels)` / `(panels, ordered_by_panel)` call shape (only `arm_a`'s
signature is explicitly "KEPT" by 3-arch.md T4, but no line proposes changing
the sibling arm_b/arm_bc/sheet_grid signatures either — they're documented
as reusing the new `module_sheet` composer internally). What changes is the
CALLER: `panels` is now expected to be ONE module's 9 view-panels (not every
module's panels pooled together), producing a 5-col x 2-row grid (10 cells,
9 used, bottom-right blank) instead of the old 9-col grid. If Loop 4b's
actual per-arm call shape differs, raise `RETURN loop=4a reason=test-wrong`,
don't hand-edit these tests.

Grid-cell sampling below deliberately avoids hardcoding gutter/pad pixel
math (unspecified numerically by 3-arch.md — "uniform pad gutter" has no
pinned width): it samples the CENTER of the bottom-right grid cell
(w//5, h//2 pitch), a point guaranteed to fall inside that cell's interior
regardless of the exact gutter width chosen by Loop 4b.
"""

from PIL import Image

import guide_marks

CELL_PX = 96
PAD = 4
GRID_COLS, GRID_ROWS = 5, 2


def _kmr():
    import kit_module_render
    return kit_module_render


def _km():
    import kit_modules
    return kit_modules


def _skm():
    import stage_kit_modules
    return stage_kit_modules


def _panels_for(module):
    """One module's 9 view-panels, scaled with the SAME global shared_scale
    used across every module (C4 — one s per sheet, never re-measured)."""
    kmr, km = _kmr(), _km()
    names = list(km.MODULES)
    s = kmr.shared_scale(names, cell_px=CELL_PX, pad=PAD)
    rendered = kmr.render_module(module, s, CELL_PX, PAD)
    return [{"module": module, "view": view, "img": img, "ordered": ordered, "origin": origin}
            for view, (img, ordered, origin) in rendered.items()]


def _bottom_right_cell_center(sheet):
    w, h = sheet.size
    cell_w, cell_h = w // GRID_COLS, h // GRID_ROWS
    return w - cell_w // 2, h - cell_h // 2


def test_per_module_sheet_grid_is_five_by_two_with_a_blank_bottom_right_cell():
    panels = _panels_for("wall_band")
    sheet = _skm().sheet_grid(panels).convert("RGB")
    w, h = sheet.size
    # C5/R3: 5 cols x 2 rows (10 cells, 9 views + 1 blank) — NOT the old
    # 9-col mega-sheet grid. Bounds are generous (any reasonable gutter
    # width survives) but discriminate 5 cols worth of width from 9.
    assert 4 * CELL_PX < w <= 5 * CELL_PX + 4 * (CELL_PX // 2), w
    assert CELL_PX < h <= 2 * CELL_PX + (CELL_PX // 2), h

    cx, cy = _bottom_right_cell_center(sheet)
    r = min(sheet.size) // (GRID_COLS * 4)
    region = sheet.crop((cx - r, cy - r, cx + r, cy + r))
    assert all(px == (0, 0, 0) for px in region.getdata())


def test_arm_b_is_blank_technical_with_zero_cyan_residue():
    sheet = _skm().arm_b(_panels_for("roof_cell"))
    assert guide_marks.residue_count(sheet) == 0


def test_arm_bc_adds_cyan_symbols_over_arm_b():
    sheet_bc = _skm().arm_bc(_panels_for("roof_cell"))
    assert guide_marks.residue_count(sheet_bc) > 0


def test_arm_a_matches_the_sheet_grid_size():
    skm = _skm()
    panels = _panels_for("stair_45")
    ordered_by_panel = {(p["module"], p["view"]): p["ordered"] for p in panels}
    sheet_a = skm.arm_a(panels, ordered_by_panel)
    assert sheet_a.size == skm.sheet_grid(panels).size


def test_per_module_sheet_has_magenta_gutter_separators():
    skm = _skm()
    panels = _panels_for("wall_band")
    ordered_by_panel = {(p["module"], p["view"]): p["ordered"] for p in panels}
    sheet = skm.arm_a(panels, ordered_by_panel).convert("RGB")
    assert any(px == (255, 0, 255) for px in sheet.getdata()), (
        "R3: magenta panel separators must survive on the composed sheet")


def test_stage_writes_one_stem_pair_per_module_arm_a_only(tmp_path):
    # Contract (AMENDED 2026-07-16, P1 S4-REVIEW-ROUNDS.md — arm a only):
    # was "one stem pair per module PER ARM" (27 = 9 modules x 3 arms);
    # arm_b/arm_bc stay in code (parked, unit-tested above) but no longer
    # get staged, so gen-inbox now holds 9 stem pairs, not 27.
    km = _km()
    names = sorted(km.MODULES)
    out = tmp_path / "gen-inbox"
    _skm().stage(out=str(out))

    pngs = sorted(out.glob("*.png"))
    expected_png_stems = {f"{name}__a" for name in names}
    assert {p.stem for p in pngs} == expected_png_stems, sorted(p.name for p in pngs)
    assert len(pngs) == len(names)

    prompts = sorted(out.glob("*_prompt.txt"))
    expected_prompt_stems = {f"{name}__a_prompt" for name in names}
    assert {p.stem for p in prompts} == expected_prompt_stems
    assert len(prompts) == len(names)

    for p in prompts:
        module, arm = p.name.removesuffix("_prompt.txt").rsplit("__", 1)
        assert module in names and arm == "a", p.name

    assert not list(out.glob("*.json")), "machine artifacts must not pollute gen-inbox"
    assert len(pngs) + len(prompts) == len(list(out.iterdir())), (
        "gen-inbox must hold nothing but per-module stem pairs")


def test_stage_sheet_dims_are_eight_x_the_original_64px_cell(tmp_path):
    # P2 (S4-REVIEW-ROUNDS.md): CELL_PX 64 -> 256 (4x linear). R2-1 (ROUND 2,
    # AMENDED 2026-07-16): 256 -> 512 (8x linear from the original 64px
    # cell) — the P2 resolution bump alone still left visible aliasing, so
    # this round both doubles the cell again AND enables the 2x
    # supersample->LANCZOS path in texture_warp.py (the actual fix; the
    # resolution bump is on top of that). GUTTER is unchanged, so overall
    # sheet dims are ~8x, not exactly 8x — assert the cell size itself (the
    # thing that actually changed) plus a generous bound on the sheet,
    # rather than a brittle exact-pixel equality.
    skm = _skm()
    assert skm.CELL_PX == 512
    out = tmp_path / "gen-inbox"
    skm.stage(out=str(out))
    from PIL import Image
    sheet = Image.open(out / f"{sorted(_km().MODULES)[0]}__a.png")
    w, h = skm._sheet_size(skm.CELL_PX)
    assert sheet.size == (w, h)
    assert w > 8 * (5 * 64 + 4 * 8) * 0.9, "sheet width should be ~8x the original 64px-cell sheet"


def test_stage_still_writes_per_module_view_masks_and_one_manifest(tmp_path):
    out = tmp_path / "gen-inbox"
    masks = tmp_path / "masks"
    _skm().stage(out=str(out), out_masks=str(masks))

    assert (masks / "sheet_manifest.json").exists()
    facemasks = list(masks.glob("*_facemask.png"))
    assert facemasks, "per-face masks must land in masks/"
    assert len(facemasks) == len(list(masks.glob("*_faces.json")))
