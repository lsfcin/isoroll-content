#!/usr/bin/env python3
"""paint_faces.py — arm A's painter: warp real textures onto one panel's ordered face quads.

Moved out of stage_kit_modules.py (which was at the size cap) when the camera family became a
parameter; stage_kit_modules re-exports `paint_panel`, so `skm.paint_panel` still resolves for its
sheet composer and for the frozen tests. Behaviour is unchanged at the default dimetric family.
"""

from functools import partial

from PIL import Image, ImageDraw, ImageOps

import face_edges
import kit_module_render as kmr
import kit_modules as km
import texture_map
import texture_warp
from face_project import DIMETRIC

_PNG_CACHE = {}


def texture_png(texture_id):
    """RGBA source PNG for a texture id, cached for the process lifetime."""
    if texture_id not in _PNG_CACHE:
        _PNG_CACHE[texture_id] = Image.open(texture_map.texture_png_path(texture_id)).convert("RGBA")
    return _PNG_CACHE[texture_id]


def paint_panel(module, view, ordered, s, cell_px, pad, origin, family=DIMETRIC):
    """RGBA cell: warp a texture onto every ordered face quad (T4, C1) — tiling via warp_tiling,
    decal (R2-5 slab front/back, flip_h mirrored first) via warp_decal — then stroke that face's
    edge-ink (R2-2, face_edges.py) right after its own paste, so a nearer face pasted later
    overpaints ink under it. Zero MAT_COLORS fills remain.

    `family` must be the camera the `ordered` polys were projected with, or the edge ink lands in a
    different screen frame than the faces it outlines. `ordered`'s own mat column wins over the
    module's Face.mat, which is how a kit builds per-material variants of one module.
    """
    faces = km.MODULES[module]()
    edges = face_edges.stroke_edges(faces)
    project = partial(kmr.project_face, family=family)
    cell = Image.new("RGBA", (cell_px, cell_px), (0, 0, 0, 0))
    draw = ImageDraw.Draw(cell)
    for face_id, kind, mat, poly in ordered:
        i = int(face_id.split(":")[0])
        world_pts = faces[i].pts
        spec = texture_map.face_texture(module, kind, world_pts, mat)
        tex_img = texture_png(spec["id"])
        if spec["type"] == "decal":
            if spec["flip_h"]:
                tex_img = ImageOps.mirror(tex_img)
            warped = texture_warp.warp_decal(tex_img, world_pts, poly)
        else:
            warped = texture_warp.warp_tiling(tex_img, world_pts, poly, spec["dims_voxels"])
        cell.paste(warped, (0, 0), warped)
        face_edges.draw_face_edges(draw, edges.get(i, []), view, s, cell_px, pad, origin, project)
    return cell
