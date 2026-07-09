#!/usr/bin/env python3
"""wall_schema.py — validate_manifest: structural check mirroring wall-types.d.ts WallDef.

Pure stdlib. Structural-only when called with a single argument (used by tests
and by any caller that only cares about shape); pass kit_dir to also validate
that tile assets resolve on disk.
"""

import json
from pathlib import Path

_COORD_FIELDS = ("ax", "ay", "bx", "by")
_CONFIG_KEYS = {"move", "sense", "sound", "light", "door", "dir"}


def _validate_walls(walls):
    errors = []
    for i, wall in enumerate(walls):
        for field in _COORD_FIELDS:
            value = wall.get(field)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"walls[{i}].{field} not numeric: {value!r}")
            elif not (0 <= value <= 1):
                errors.append(f"walls[{i}].{field} out of range [0,1]: {value!r}")
        for field in ("topOffset", "bottomOffset"):
            value = wall.get(field)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"walls[{i}].{field} not numeric: {value!r}")
        config = wall.get("config", {})
        extra_keys = set(config.keys()) - _CONFIG_KEYS
        if extra_keys:
            errors.append(f"walls[{i}].config has unknown keys: {sorted(extra_keys)}")
        for key, value in config.items():
            if not isinstance(value, int) or isinstance(value, bool) or not (0 <= value <= 2):
                errors.append(f"walls[{i}].config[{key!r}] not int in [0,2]: {value!r}")
    return errors


def _validate_tile_assets(tiles, kit_dir):
    kit_pieces = json.loads((Path(kit_dir) / "kit.json").read_text())["pieces"]
    errors = []
    for i, tile in enumerate(tiles):
        if tile.get("piece") not in kit_pieces:
            continue
        if not (Path(kit_dir) / tile["asset"]).exists():
            errors.append(f"tiles[{i}].asset does not resolve in kit_dir: {tile['asset']!r}")
    return errors


def validate_manifest(m, kit_dir=None):
    """Return a list of error strings; empty list means the manifest is structurally clean."""
    errors = _validate_walls(m.get("walls", []))
    if kit_dir is not None:
        errors += _validate_tile_assets(m.get("tiles", []), kit_dir)
    return errors
