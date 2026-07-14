#!/usr/bin/env python3
"""layout_serialize.py — Layout -> canonical DSL v2 text, ported from rig.frag updateDsl (L1088-1119).

T4 (.loop/dsl-v2-python/3-arch.md). Round-trip contract (C2): to_dsl(parse_text(text)) == text,
compared per-line-rstripped. Unlike rig.frag's live editor (whose in-memory grid never stores R/S —
they're a computed overlay recomputed at render time), our parser keeps R/S markers verbatim in
Level.g when it reads them (see layout_dsl_v2.py), so emission here is a straight, lossless replay
of the parsed model — no gvox recompute needed.
"""

from layout_groups import ENCLOSE, ROOF_FORMS, SIDE_NAME, STAIR_TYPES


def _group_line(group):
    kind_word = "stair" if group.kind == "stair" else "roof"
    rs = [cell[0] for cell in group.cells]
    cs = [cell[1] for cell in group.cells]
    form_name = STAIR_TYPES[group.form] if group.kind == "stair" else ROOF_FORMS[group.form]
    line = (f"{kind_word}: {min(rs)},{min(cs)} {max(rs)},{max(cs)} form={form_name} "
            f"dir={SIDE_NAME[group.dir]} incl={group.incl}ft z={group.z}")
    if group.kind == "roof":
        line += f" enclose={ENCLOSE[group.enclose or 0]}"
    return line


def _attr_rows(level, attr_name):
    attr = getattr(level, attr_name)
    if not attr:
        return None
    cols = len(level.g[0]) if level.g else 0
    rows = []
    for r in range(len(level.g)):
        rows.append("".join(str(attr.get(f"{r},{c}", ".")) for c in range(cols)))
    return rows


def _level_lines(lvl, level):
    lines = [f"level {lvl}:", *level.g]
    for attr_name in ("side", "type", "wmat", "fh"):
        rows = _attr_rows(level, attr_name)
        if rows is not None:
            lines.append(f"layer {attr_name}:")
            lines.extend(rows)
    return lines


def to_dsl(layout):
    """`layout` (parsed Layout, v2 shape) -> canonical DSL text — see module docstring."""
    lines = [f"name: {layout.name}"]
    if layout.levels:
        for lvl in sorted(layout.levels):
            lines.append("")
            lines.extend(_level_lines(lvl, layout.levels[lvl]))
        for group in layout.groups:
            lines.append(_group_line(group))
    else:
        lines.extend(layout.grid)
    return "\n".join(lines)
