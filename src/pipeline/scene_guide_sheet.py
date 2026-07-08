#!/usr/bin/env python3
"""scene_guide_sheet.py — compose the 6-cell NB scene-guide sheet (views + plan + caption + marks) and CLI."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import guide_marks
import layout_parse
import scene_anchors
from scene_guide_render import VIEW_TURNS, render_plan_panel, render_scene_panel
from tile_guide_render import MAGENTA

SHEET_ROWS = [["NW", "NE", "TOP"], ["SW", "SE", "CAPTION"]]  # same 6-cell contract as make_tile_guide


def _font(px):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", px)
    except OSError:
        return ImageFont.load_default()


def _label(row, col, kind):
    index = row * len(SHEET_ROWS[0]) + col + 1
    return f"{index} {kind}" + (" ▼" if kind == "TOP" else "")


def compose_sheet(layout, cell_px=640, marks_mode=None, params=None):
    """Full sheet image + the (view, box) panel list used for marks/postproc.

    marks_mode: None | "anchored" (symbols attached to geometry) | "columns" | "varied"."""
    rows, cols = len(SHEET_ROWS), len(SHEET_ROWS[0])
    sheet = Image.new("RGB", (cols * cell_px, rows * cell_px), (0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    font = _font(max(14, cell_px // 18))
    panels = []
    for r, row_kinds in enumerate(SHEET_ROWS):
        for c, kind in enumerate(row_kinds):
            box = (c * cell_px, r * cell_px, cell_px, cell_px)
            panels.append((kind, box))
            if kind == "TOP":
                sheet.paste(render_plan_panel(layout, cell_px), box[:2])
            elif kind == "CAPTION":
                text = (f"{layout.name}\n{layout.cols}x{layout.rows} cells\n"
                        f"wall_h {layout.wall_h}\nscene guide v2")
                draw.multiline_text((box[0] + cell_px * 0.1, box[1] + cell_px * 0.3),
                                    text, fill=MAGENTA, font=font, spacing=8)
            else:
                sheet.paste(render_scene_panel(layout, kind, cell_px), box[:2])
    if marks_mode == "anchored":
        specs = []
        for kind, box in panels:
            if kind in VIEW_TURNS:
                specs.append((kind, box, scene_anchors.project(layout, kind, cell_px)))
        sheet = scene_anchors.apply_anchored(sheet, specs, params)
        draw = ImageDraw.Draw(sheet)
    elif marks_mode in ("columns", "varied"):
        params = params or guide_marks.MarkParams()
        params.scheme = marks_mode
        sheet = guide_marks.apply_marks(sheet, panels, params)
        draw = ImageDraw.Draw(sheet)
    for r, row_kinds in enumerate(SHEET_ROWS):  # labels and separators over everything
        for c, kind in enumerate(row_kinds):
            if kind != "CAPTION":
                draw.text((c * cell_px + 10, r * cell_px + 6), _label(r, c, kind), fill=MAGENTA, font=font)
    for c in range(1, cols):
        draw.line([(c * cell_px, 0), (c * cell_px, sheet.height)], fill=MAGENTA, width=3)
    for r in range(1, rows):
        draw.line([(0, r * cell_px), (sheet.width, r * cell_px)], fill=MAGENTA, width=3)
    return sheet, panels


def main():
    parser = argparse.ArgumentParser(description="Render the NB scene-guide sheet for a layout file.")
    parser.add_argument("--layout", required=True, type=Path, help="layout DSL file")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cell-px", type=int, default=640)
    parser.add_argument("--marks", action="store_true", help="apply registration marks")
    parser.add_argument("--marks-mode", choices=["anchored", "columns", "varied"], default="anchored")
    parser.add_argument("--back-mode", choices=["occluded", "faded"], default="occluded")
    parser.add_argument("--opacity", type=float, default=0.85)
    args = parser.parse_args()

    layout = layout_parse.load(args.layout)
    if layout.errors:
        raise SystemExit("layout errors:\n" + "\n".join(layout.errors))
    for warning in layout.warnings:
        print("warn:", warning)
    mode = args.marks_mode if args.marks else None
    params = guide_marks.MarkParams(back_mode=args.back_mode, opacity=args.opacity)
    sheet, _panels = compose_sheet(layout, args.cell_px, mode, params)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)
    print(f"Saved: {args.output}  ({sheet.width}x{sheet.height} px)")


if __name__ == "__main__":
    main()
