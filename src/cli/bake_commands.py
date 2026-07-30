#!/usr/bin/env python3
"""bake_commands.py — bake-scene verb: layout -> arm-A cell sprites + one manifest per view.

This is the command form of the frozen seam (pipeline/render_scene.py). It produces everything
Foundry needs for a scene: a sprite set per projection family under <out>/kit/, and a manifest per
view under <out>/manifests/. Sprite sets are shared across the views of a family by design — the 4
dimetric views are cell remaps of the same art, and so are the 4 cardinal ones.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))

import render_scene  # noqa: E402
import view_table  # noqa: E402
from layout_parse import load  # noqa: E402
from wall_schema import validate_manifest  # noqa: E402


def _parse(argv):
    parser = argparse.ArgumentParser(prog="iso-cli.py bake-scene")
    parser.add_argument("--layout", required=True, help="layout DSL file")
    parser.add_argument("--out", default="output/scenes", help="output root (default: output/scenes)")
    parser.add_argument("--views", default="", help="comma-separated subset (default: all 8+1)")
    parser.add_argument("--arm", default="a", help="content arm behind the seam (default: a)")
    parser.add_argument("--skip-kit", action="store_true", help="reuse the sprite sets already in <out>/kit")
    parser.add_argument("--preview", action="store_true", help="also write an assembled QC PNG per view")
    return parser.parse_args(argv)


def _views_from(raw):
    if not raw:
        return list(view_table.VIEWS)
    return [name.strip() for name in raw.split(",") if name.strip()]


def run_bake(argv):
    args = _parse(argv)
    layout = load(args.layout)
    if layout.errors:
        print("[FAIL] layout errors:")
        for err in layout.errors:
            print(f"  {err}")
        sys.exit(1)

    out = Path(args.out)
    kit_root = out / "kit"
    if not args.skip_kit:
        kits = render_scene.build_kits(kit_root)
        for family, manifest in kits.items():
            print(f"kit[{family}]: {len(manifest['pieces'])} pieces @ {manifest['px_per_unit']:.1f} px/voxel")

    views = _views_from(args.views)
    manifests = render_scene.bake(layout, kit_root, out / "manifests", views, args.arm)

    failed = 0
    for view, manifest in manifests.items():
        kit_dir = render_scene.kit_dir_for(kit_root, view)
        errors = validate_manifest(manifest, str(kit_dir))
        if errors:
            failed += 1
            print(f"[FAIL] {view}: {len(errors)} manifest errors")
            for err in errors[:5]:
                print(f"  {err}")
        else:
            print(f"{view:4} {len(manifest['tiles']):3} tiles  {len(manifest['walls']):3} walls")

    if args.preview:
        previews = out / "preview"
        previews.mkdir(parents=True, exist_ok=True)
        for view in views:
            image = render_scene.render_image(layout, view, kit_root)
            image.save(previews / f"{layout.name}_{view}.png")
        print(f"previews: {previews}")

    if failed:
        sys.exit(1)
    print(f"Saved: {out}/manifests ({len(manifests)} views)")
