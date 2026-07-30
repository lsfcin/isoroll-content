#!/usr/bin/env python3
"""render_scene.py — THE SEAM. `render_scene(layout, view) -> {cell sprites, manifest}`.

Frozen 2026-07-29 (SCENE-CREATION.md § The seam): every content arm implements this one entry, and
choosing an arm is an A/B behind it, never an architecture change. The contract is the structure —
cell sprites plus a manifest carrying WallDefs, boundHeight, imageOffset, pxPerVoxel and the D7
chunk guard; the pixels are swappable.

Arm A (today's kit assembly) is implementation A: a reusable sprite per piece, pasted per cell. Its
code is untouched behind here — this module only names the seam and routes to it, so a later arm B
(cells rendered at their real world position) or A' (Wang/corner-matched variant sets) plugs in by
adding an entry to ARMS, not by changing any caller.

The view is one of the 8+1 (view_table.VIEWS). A sprite SET is per projection family, not per view:
the four dimetric views are cell remaps of the same art and so are the four cardinal ones, so
`kit_dir_for` points a view at its family's kit.
"""

import json
from pathlib import Path

import kit_arm_a
import scene_assemble
import scene_manifest
import view_table


def kit_dir_for(kit_root, view):
    """Where this view's sprite set lives: one directory per projection family."""
    family = view_table.family(view)
    return Path(kit_root) / family


def _arm_a(layout, view, kit_root):
    """Implementation A — load the family's pre-baked kit; sprites are reused across cells."""
    kit_dir = kit_dir_for(kit_root, view)
    manifest, sprites = scene_assemble.load_kit(kit_dir)
    scene = scene_manifest.build_manifest(layout, kit_dir, view)
    return {"sprites": sprites, "kit": manifest, "manifest": scene, "kit_dir": kit_dir}


ARMS = {"a": _arm_a}


def render_scene(layout, view, kit_root, arm="a"):
    """{view, arm, sprites, manifest, kit, kit_dir} — the cell sprites and manifest for one view.

    `sprites` is keyed by kit piece name; every manifest tile's `asset` names one of them (or a
    piece this kit does not carry, which validation reports and assembly skips).
    """
    if view not in view_table.VIEW_TABLE:
        raise KeyError(f"unknown view {view!r} — expected one of {sorted(view_table.VIEW_TABLE)}")
    build = ARMS[arm]
    result = build(layout, view, kit_root)
    result["view"] = view
    result["arm"] = arm
    return result


def render_image(layout, view, kit_root):
    """The assembled preview PNG for one view — a content-side QC artifact, not a shipped asset.

    Foundry composes the scene itself from `sprites` + `manifest`; this is what a golden test and a
    board diff look at.
    """
    kit_dir = kit_dir_for(kit_root, view)
    return scene_assemble.assemble(layout, view, kit_dir)


def bake(layout, kit_root, out_dir, views=None, arm="a"):
    """Write one manifest per view into `out_dir`. Sprite sets are shared, so they are NOT copied
    per view — the manifest's assets resolve against `kit_root/<family>/`. Returns {view: manifest}.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = {}
    for view in (views if views is not None else view_table.VIEWS):
        result = render_scene(layout, view, kit_root, arm)
        manifest = result["manifest"]
        manifest["kit"] = str(kit_dir_for(kit_root, view))
        # lowercase, single-extension: the workspace naming gate rejects both `SW` and the
        # `<slug>.TYPE.json` double-extension shape (core/SCHEMA.md).
        path = out / f"{layout.name}_{view.lower()}_manifest.json"
        payload = json.dumps(manifest, indent=2)
        path.write_text(payload)
        written[view] = manifest
    return written


def build_kits(kit_root):
    """Bake arm A's sprite sets (one per family) — the pixels every view above resolves against."""
    return kit_arm_a.build_all(kit_root)
