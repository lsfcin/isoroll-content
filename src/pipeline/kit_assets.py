#!/usr/bin/env python3
"""kit_assets.py — resolve a tile's sprite name against whatever kit is in play.

A tile says WHAT it is (piece: wall / floor / door_u / roof / stair), what it is made of (mat), and
which way it points (direction, for oriented group pieces). A kit says which of those distinctions
it actually carries: the flat guide kit (kit_render.py) has one "wall"; the arm-A kit (kit_arm_a.py)
has "wall__stone" and "wall__wood" plus "roof_N".."roof_W". Keeping the tile's vocabulary semantic
and resolving to a file name HERE is what lets both kits back the same manifest — and what keeps a
piece name meaning the same thing in every kit instead of one kit's naming leaking into the layout.

Most specific wins: direction, then material, then the bare piece.
"""


def candidates(piece, mat="", direction=""):
    """Sprite names for a tile, most specific first."""
    names = []
    if direction:
        names.append(f"{piece}_{direction}")
    if mat:
        names.append(f"{piece}__{mat}")
    names.append(piece)
    return names


def resolve(kit_pieces, piece, mat="", direction=""):
    """The name this kit actually carries, or None when it carries no variant of this piece."""
    for name in candidates(piece, mat, direction):
        if name in kit_pieces:
            return name
    return None


def asset_name(kit_pieces, piece, mat="", direction=""):
    """Sprite file name for a tile. Falls back to the bare piece so a manifest is never assetless —
    validation (wall_schema) is what reports a piece the kit cannot serve."""
    resolved = resolve(kit_pieces, piece, mat, direction)
    name = resolved if resolved else piece
    return f"{name}.png"
