#!/usr/bin/env python3
"""texture_map.py — face(kind,mat) -> texture FAMILY/variant lookup (T1, C2,
C8). Pure lookup, no PIL geometry (that's texture_warp.py's job). See
3-arch.md Architecture section for the pinned FAMILY table and the
deterministic-variant-from-world-column rule (R1)."""

import hashlib
import json
from pathlib import Path

_TEXTURES_ROOT = Path(__file__).resolve().parents[2] / "assets" / "textures"
_TEXTURES_JSON = _TEXTURES_ROOT / "textures.json"

_STONE_LIKE_MATS = ("blank", "thatch")

_SLAB_DECAL = {"door_1x2": "door_1x2x0", "window_1x1": "window_1x1x0"}  # R2-5

_TEXTURES_CACHE = None


def load_textures():
    """dict[texture_id -> {png, type, dims_voxels, continuity}] parsed from
    assets/textures/textures.json (cached, process-lifetime)."""
    global _TEXTURES_CACHE
    if _TEXTURES_CACHE is None:
        with open(_TEXTURES_JSON) as fh:
            _TEXTURES_CACHE = json.load(fh)
    return _TEXTURES_CACHE


def _face_normal(world_pts):
    p0, p1, p2 = world_pts[0], world_pts[1], world_pts[2]
    v1 = tuple(b - a for a, b in zip(p0, p1))
    v2 = tuple(b - a for a, b in zip(p0, p2))
    n = (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
    )
    mag = sum(c * c for c in n) ** 0.5
    if mag < 1e-12:
        return (0.0, 0.0, 1.0)
    return tuple(c / mag for c in n)


def FAMILY(module, kind, normal, mat):
    """Family-name table (3-arch.md Architecture, texture_map.py). blank/thatch
    mat default to stone. Slab (door/window), stair, and roof/base get
    kind-specific overrides that win over the generic top/side rule."""
    eff_mat = "stone" if mat in _STONE_LIKE_MATS else mat

    if module in _SLAB_DECAL:
        # R2-5: standalone door/window slab. The two LARGE v-normal faces
        # (front/back) get the object's own decal family (single-member
        # family — variant() returns it unconditionally); every other face
        # (the thin u-normal edges + top/bottom caps) is plain wood tone +
        # edge lines (face_edges.py), never the decal.
        if kind == "side" and abs(normal[1]) > 0.9:
            return _SLAB_DECAL[module]
        return "wall_wood_side"

    if module.startswith("stair"):
        if kind == "top":
            return "stair_tread"
        if kind == "bottom":
            return "floor_stone"
        if kind == "side":
            return "stair_riser" if abs(normal[0]) > 0.9 else "wall_stone_side"
        return "wall_stone_side"

    if kind == "bottom":
        return "floor_stone"
    if kind in ("slope", "gable"):
        return "roof_shingle"
    if module == "base" and kind == "top":
        return "floor_stone"
    if kind == "top":
        return f"wall_{eff_mat}_top"
    if kind == "side":
        return f"wall_{eff_mat}_side"
    return "wall_stone_side"


def _family_members(family):
    textures = load_textures()
    if family in textures:
        return [family]
    prefix = f"{family}_v"
    return sorted(k for k in textures if k.startswith(prefix))


def variant(family, world_pts):
    """Deterministic texture_id within `family`, keyed ONLY on the world
    column (u,v) of `world_pts` (R1) — never on z, never on view/yaw, so the
    same spot always shows the same variant across all 9 views (C8)."""
    members = _family_members(family)
    if not members:
        return family
    if len(members) == 1:
        return members[0]
    min_u = min(p[0] for p in world_pts)
    min_v = min(p[1] for p in world_pts)
    col = (round(min_u * 4), round(min_v * 4))
    digest = hashlib.md5(f"{family}|{col}".encode()).hexdigest()
    idx = int(digest, 16) % len(members)
    return members[idx]


def face_texture(module, kind, world_pts, mat):
    """{id, type, dims_voxels, flip_h} for a face — FAMILY -> variant ->
    load_textures lookup. Never raises (blank/unmapped module falls back
    safely). `flip_h` (R2-5) is True only for a slab module's BACK large
    face (normal points +v, the SLAB_THICK side) — texture_warp's caller
    mirrors the source before warping so the door/window's real-world
    hardware (handle/keyhole) sits on the same physical edge seen from
    either side: physically-correct object continuity, not a sprite mirror.
    False for every other face, including a slab's own front face."""
    normal = _face_normal(world_pts)
    family = FAMILY(module, kind, normal, mat)
    textures = load_textures()
    if family not in textures and not _family_members(family):
        family = "wall_stone_side"
    tex_id = variant(family, world_pts)
    spec = textures.get(tex_id)
    if spec is None:
        tex_id = "wall_stone_side_v1"
        spec = textures[tex_id]
    flip_h = module in _SLAB_DECAL and kind == "side" and normal[1] > 0.9
    return {"id": tex_id, "type": spec["type"], "dims_voxels": spec["dims_voxels"], "flip_h": flip_h}


def texture_png_path(texture_id):
    """Absolute path to `texture_id`'s PNG (assets/textures/<png>)."""
    return _TEXTURES_ROOT / load_textures()[texture_id]["png"]
