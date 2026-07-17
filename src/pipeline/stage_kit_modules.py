#!/usr/bin/env python3
"""stage_kit_modules.py — compose one 5x2 sheet PER MODULE per arm
(blank/blank+cyan/real-texture) and stage them to output/gen-inbox/
(gitignored) for the render->restyle lane (T4/T4b, C4/C5). Panels arrive
already rendered at a fixed cell size (see kit_module_render.render_panel),
so grid placement is a straight paste. Sheet-per-module contract (R2/R3):
`panels` for sheet_grid/arm_b/arm_bc/arm_a is ONE module's 9 view-panels
(VIEWS order). Grid fixed 5 cols x 2 rows, gutter + magenta separators —
one shared `s` across every module/view (C4). P1: `stage()` writes arm_a
only. CELL_PX 512 (R2-1) via the supersample path in texture_warp.py.
ROUND 3 (S4-REVIEW-ROUNDS.md): `stage()` also emits per-view enclosure-mask
PNGs (enclosure_masks.py) for the stripped stair/roof faces — never painted
here, staged alongside the render-visible masks."""

import json
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

import guide_marks
import face_edges
import kit_module_render as kmr
import kit_modules as km
import face_masks as fm
import enclosure_masks
import texture_map
import texture_warp

CELL_PX = 512  # R2-1: 2x the prior 256px cell (S4-REVIEW-ROUNDS.md ROUND 2)
PAD = 4

GRID_COLS, GRID_ROWS = 5, 2  # 10 cells for VIEWS' 9 entries + 1 blank
GUTTER = 8
MAGENTA = (255, 0, 255)

MAT_COLORS = {
    "stone": (150, 150, 150),
    "wood": (120, 80, 40),
    "thatch": (200, 180, 90),
    "blank": (170, 170, 170),
}

_PNG_CACHE = {}


def _texture_png(texture_id):
    if texture_id not in _PNG_CACHE:
        _PNG_CACHE[texture_id] = Image.open(texture_map.texture_png_path(texture_id)).convert("RGBA")
    return _PNG_CACHE[texture_id]


def _cell_origin(idx, cell_px):
    row, col = divmod(idx, GRID_COLS)
    return col * (cell_px + GUTTER), row * (cell_px + GUTTER)


def _sheet_size(cell_px):
    w = GRID_COLS * cell_px + (GRID_COLS - 1) * GUTTER
    h = GRID_ROWS * cell_px + (GRID_ROWS - 1) * GUTTER
    return w, h


def _draw_gutter_lines(canvas, cell_px):
    draw = ImageDraw.Draw(canvas)
    w, h = canvas.size
    for col in range(1, GRID_COLS):
        x = col * cell_px + (col - 1) * GUTTER + GUTTER // 2
        draw.line([(x, 0), (x, h)], fill=MAGENTA, width=3)
    for row in range(1, GRID_ROWS):
        y = row * cell_px + (row - 1) * GUTTER + GUTTER // 2
        draw.line([(0, y), (w, y)], fill=MAGENTA, width=3)


def _shared_s(panels):
    """Recover the module-shared px-per-voxel `s` used to render `panels`,
    from the cell size baked into panels[0]['img'] (C4: one s per sheet,
    never re-measured from pixels — a re-derivation, not a fresh measure)."""
    cell_px = panels[0]["img"].size[0]
    return kmr.shared_scale(list(km.MODULES), cell_px=cell_px, pad=PAD), cell_px


def sheet_grid(panels):
    """5x2 grid (9 views + 1 blank bottom-right watermark cell), gutter +
    magenta separators (R3)."""
    cell_px = panels[0]["img"].size[0]
    w, h = _sheet_size(cell_px)
    canvas = Image.new("RGB", (w, h), (0, 0, 0))
    for idx, p in enumerate(panels):
        ox, oy = _cell_origin(idx, cell_px)
        img = p["img"]
        mask = img if img.mode == "RGBA" else None
        canvas.paste(img.convert("RGB"), (ox, oy), mask)
    _draw_gutter_lines(canvas, cell_px)
    return canvas


def arm_b(panels):
    """Blank technical arm: grayscale sheet, no symbols."""
    return sheet_grid(panels).convert("L").convert("RGB")


def arm_bc(panels):
    """arm_b + guide_marks cyan symbols, one region per panel cell."""
    sheet = arm_b(panels)
    cell_px = panels[0]["img"].size[0]
    rects = [(p["view"], (*_cell_origin(idx, cell_px), cell_px, cell_px))
             for idx, p in enumerate(panels)]
    return guide_marks.apply_marks(sheet, rects)


def paint_panel(module, view, ordered, s, cell_px, pad, origin):
    """RGBA cell: warp a texture onto every ordered face quad (T4, C1) —
    tiling via warp_tiling, decal (R2-5 slab front/back, flip_h mirrored
    first) via warp_decal — then stroke that face's edge-ink (R2-2,
    face_edges.py) right after its own paste, so a nearer face pasted later
    overpaints ink under it. Zero MAT_COLORS fills remain."""
    faces = km.MODULES[module]()
    edges = face_edges.stroke_edges(faces)
    cell = Image.new("RGBA", (cell_px, cell_px), (0, 0, 0, 0))
    draw = ImageDraw.Draw(cell)
    for face_id, kind, mat, poly in ordered:
        i = int(face_id.split(":")[0])
        world_pts = faces[i].pts
        spec = texture_map.face_texture(module, kind, world_pts, mat)
        tex_img = _texture_png(spec["id"])
        if spec["type"] == "decal":
            if spec["flip_h"]:
                tex_img = ImageOps.mirror(tex_img)
            warped = texture_warp.warp_decal(tex_img, world_pts, poly)
        else:
            warped = texture_warp.warp_tiling(tex_img, world_pts, poly, spec["dims_voxels"])
        cell.paste(warped, (0, 0), warped)
        face_edges.draw_face_edges(draw, edges.get(i, []), view, s, cell_px, pad, origin, kmr.project_face)
    return cell


def arm_a(panels, ordered_by_panel):
    """Real-texture arm: paint_panel per view, composed on the same 5x2
    grid+gutter+magenta layout as sheet_grid (T4)."""
    s, cell_px = _shared_s(panels)
    w, h = _sheet_size(cell_px)
    canvas = Image.new("RGB", (w, h), (0, 0, 0))
    for idx, p in enumerate(panels):
        ox, oy = _cell_origin(idx, cell_px)
        ordered = ordered_by_panel.get((p["module"], p["view"]), p["ordered"])
        painted = paint_panel(p["module"], p["view"], ordered, s, cell_px, PAD, p["origin"])
        canvas.paste(painted, (ox, oy), painted)
    _draw_gutter_lines(canvas, cell_px)
    return canvas


def stage(out="output/gen-inbox", out_masks=None):
    """gen-inbox holds ONLY what Lucas hand-feeds to the NB web app (P1:
    arm a only — `{module}__a.png` / `{module}__a_prompt.txt` stem pairs);
    machine artifacts (face masks/meta, sheet manifest) go to `out_masks`
    (default: sibling `masks/` next to `out`)."""
    out_path = Path(out)
    out_path.mkdir(parents=True, exist_ok=True)
    masks_path = Path(out_masks) if out_masks else out_path.parent / "masks"
    masks_path.mkdir(parents=True, exist_ok=True)

    names = list(km.MODULES)
    s = kmr.shared_scale(names, cell_px=CELL_PX, pad=PAD)  # ONE global s (C4)

    prompts_dir = Path(__file__).parent / "prompts"
    prompt_body_a = (prompts_dir / "restyle_arm_a.md").read_text()

    all_panels = []
    for name in names:
        module_panels = []
        ordered_by_panel = {}
        for view, (img, ordered, origin) in kmr.render_module(name, s, CELL_PX, PAD).items():
            p = {"module": name, "view": view, "img": img, "ordered": ordered, "origin": origin}
            module_panels.append(p)
            all_panels.append(p)
            ordered_by_panel[(name, view)] = ordered

        arm_a(module_panels, ordered_by_panel).save(out_path / f"{name}__a.png")
        (out_path / f"{name}__a_prompt.txt").write_text(f"# {name}\n\n{prompt_body_a}")

        # R3: mask-only enclosure faces (never painted above) get tagged masks.
        origins = {p["view"]: p["origin"] for p in module_panels}
        for view, enc in kmr.enclosure_faces(name, s, CELL_PX, PAD, origins).items():
            enclosure_masks.save_enclosure_masks(name, view, enc, CELL_PX, masks_path)

    manifest_panels = []
    for p in all_panels:
        xs = [x for _fid, _k, _m, poly in p["ordered"] for x, _y in poly]
        ys = [y for _fid, _k, _m, poly in p["ordered"] for _x, y in poly]
        bbox = (min(xs), min(ys), max(xs), max(ys))
        manifest_panels.append({"module": p["module"], "view": p["view"], "bbox": bbox, "origin": p["origin"]})
    manifest = kmr.build_sheet_manifest(manifest_panels, s)
    (masks_path / "sheet_manifest.json").write_text(json.dumps(manifest, indent=2))

    for p in all_panels:
        idmap, meta = fm.face_mask(p["ordered"], p["img"].size)
        fm.save_mask(idmap, meta, masks_path / f"{p['module']}_{p['view']}")
