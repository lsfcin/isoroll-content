#!/usr/bin/env python3
"""layout_material.py — which material a cell is made of, per the v2 attr overlays.

Normative source is design/feel-rig/rig.frag L635: a cell's own material index lives in the `type`
overlay (`TYPES[ch][type[key] || 0]`), while `wmat` keeps the material of the WALL a non-wall cell
sits in — so a door or window in a wood wall still reads wood around the opening. Values in the DSL
are digit chars ("0", "1", ...) indexing layout_groups.TYPES for that character.

The material name is what texture_map.face_texture consumes ("stone" | "wood" | ...), so this is the
one hop between authored layout and painted pixels.
"""

from layout_groups import TYPES, WALLISH

DEFAULT = "stone"


def _index(attrs, r, c):
    raw = attrs.get(f"{r},{c}")
    return int(raw) if raw is not None and str(raw).isdigit() else 0


def _lookup(ch, index):
    names = TYPES.get(ch)
    if not names:
        return DEFAULT
    return names[index] if 0 <= index < len(names) else names[0]


def cell_material(level_attrs, r, c, ch):
    """Material name of cell (r,c) holding char `ch`. level_attrs: {"type": {...}, "wmat": {...}}."""
    type_attrs = level_attrs.get("type", {})
    return _lookup(ch, _index(type_attrs, r, c))


def wall_material(level_attrs, r, c, ch):
    """Material of the wall RUN this cell belongs to — walls use `type`, openings carry `wmat`."""
    if ch in WALLISH and ch not in ("D", "W"):
        return cell_material(level_attrs, r, c, ch)
    wmat_attrs = level_attrs.get("wmat", {})
    return _lookup("#", _index(wmat_attrs, r, c))


def level_attrs(level):
    """The two overlays material resolution reads, as a plain dict (Level or None -> defaults)."""
    if level is None:
        return {"type": {}, "wmat": {}}
    return {"type": level.type, "wmat": level.wmat}
