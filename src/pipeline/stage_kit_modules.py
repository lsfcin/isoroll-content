#!/usr/bin/env python3
"""stage_kit_modules.py — compose 3 arm sheets (blank/blank+cyan/real-texture)
and stage them to output/gen-inbox/ (gitignored) for the render->restyle
lane (T5, C4). Panels arrive already rendered at a fixed cell size (see
kit_module_render.render_panel), so grid placement is a straight paste — the
per-panel centring already happened inside render_panel."""

import json
import shutil
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw

import guide_marks
import kit_module_render as kmr
import kit_modules as km
import face_masks as fm

CELL_PX = 64
PAD = 4

MAT_COLORS = {
    "stone": (150, 150, 150),
    "wood": (120, 80, 40),
    "thatch": (200, 180, 90),
    "blank": (170, 170, 170),
}


def _grid_dims(panels):
    cell_w, cell_h = panels[0]["img"].size
    cols = len(kmr.VIEWS)
    rows = ceil((len(panels) + 1) / cols)
    return cols, rows, cell_w, cell_h


def sheet_grid(panels):
    """cols=len(VIEWS), total_cells=len(panels)+1 -> the trailing cell(s),
    including the bottom-right one, stay black (NB watermark slot)."""
    cols, rows, cell_w, cell_h = _grid_dims(panels)
    canvas = Image.new("RGB", (cols * cell_w, rows * cell_h), (0, 0, 0))
    for idx, p in enumerate(panels):
        row, col = divmod(idx, cols)
        img = p["img"]
        mask = img if img.mode == "RGBA" else None
        canvas.paste(img.convert("RGB"), (col * cell_w, row * cell_h), mask)
    return canvas


def arm_b(panels):
    """Blank technical arm: grayscale sheet, no symbols."""
    return sheet_grid(panels).convert("L").convert("RGB")


def arm_bc(panels):
    """arm_b + guide_marks cyan symbols, one region per panel cell."""
    sheet = arm_b(panels)
    cols, _rows, cell_w, cell_h = _grid_dims(panels)
    rects = [(p["view"], (col * cell_w, row * cell_h, cell_w, cell_h))
             for idx, p in enumerate(panels) for row, col in [divmod(idx, cols)]]
    return guide_marks.apply_marks(sheet, rects)


def arm_a(panels, ordered_by_panel):
    """Per-face deterministic procedural fill keyed by face.mat (no repo texture
    assets exist yet); grayscale MAT_COLORS fallback on an unknown mat."""
    cols, rows, cell_w, cell_h = _grid_dims(panels)
    canvas = Image.new("RGB", (cols * cell_w, rows * cell_h), (0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    for idx, p in enumerate(panels):
        row, col = divmod(idx, cols)
        ox, oy = col * cell_w, row * cell_h
        for _face_id, _kind, mat, poly in ordered_by_panel.get((p["module"], p["view"]), []):
            color = MAT_COLORS.get(mat, MAT_COLORS["blank"])
            draw.polygon([(x + ox, y + oy) for x, y in poly], fill=color)
    return canvas


def stage(out="output/gen-inbox", out_masks=None):
    """gen-inbox holds ONLY what Lucas hand-feeds to the NB web app (arm
    sheets + restyle prompts); machine artifacts (face masks/meta, sheet
    manifest) go to `out_masks` (default: sibling `masks/` next to `out`)."""
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    masks_path = Path(out_masks) if out_masks else out_path.parent / "masks"
    masks_path.mkdir(parents=True, exist_ok=True)

    names = list(km.MODULES)
    s = kmr.shared_scale(names, cell_px=CELL_PX, pad=PAD)

    panels, ordered_by_panel = [], {}
    for name in names:
        for view, (img, ordered, origin) in kmr.render_module(name, s, CELL_PX, PAD).items():
            panels.append({"module": name, "view": view, "img": img, "ordered": ordered, "origin": origin})
            ordered_by_panel[(name, view)] = ordered

    arm_b(panels).save(out_path / "arm_b.png")
    arm_bc(panels).save(out_path / "arm_bc.png")
    arm_a(panels, ordered_by_panel).save(out_path / "arm_a.png")

    manifest_panels = []
    for p in panels:
        xs = [x for _fid, _k, _m, poly in p["ordered"] for x, _y in poly]
        ys = [y for _fid, _k, _m, poly in p["ordered"] for _x, y in poly]
        bbox = (min(xs), min(ys), max(xs), max(ys))
        manifest_panels.append({"module": p["module"], "view": p["view"], "bbox": bbox, "origin": p["origin"]})
    manifest = kmr.build_sheet_manifest(manifest_panels, s)
    (masks_path / "sheet_manifest.json").write_text(json.dumps(manifest, indent=2))

    for p in panels:
        idmap, meta = fm.face_mask(p["ordered"], p["img"].size)
        fm.save_mask(idmap, meta, masks_path / f"{p['module']}_{p['view']}")

    prompts_dir = Path(__file__).parent / "prompts"
    for arm in ("a", "b", "bc"):
        shutil.copy(prompts_dir / f"restyle_arm_{arm}.md", out_path / f"restyle_arm_{arm}.md")
