#!/usr/bin/env python3
"""export_commands.py — export-manifest verb: layout + kit → scene manifest JSON."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))

from layout_parse import load  # noqa: E402
from scene_manifest import build_manifest  # noqa: E402
from wall_schema import validate_manifest  # noqa: E402


def run_export(argv):
    parser = argparse.ArgumentParser(prog="iso-cli.py export-manifest")
    parser.add_argument("--layout", required=True, help="layout DSL file")
    parser.add_argument("--kit", default="output/kit-guide", help="dir with kit.json (default: output/kit-guide)")
    parser.add_argument("--view", default="NW", choices=["SW", "SE", "NE", "NW"])
    parser.add_argument("--out", default=None, help="output path (default: output/manifests/{layout.name}.manifest.json)")
    args = parser.parse_args(argv)

    layout = load(args.layout)
    if layout.errors:
        print("[FAIL] layout errors:")
        for err in layout.errors:
            print(f"  {err}")
        sys.exit(1)

    manifest = build_manifest(layout, args.kit, args.view)
    errors = validate_manifest(manifest, args.kit)
    if errors:
        print("[FAIL] manifest validation errors:")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)

    out = Path(args.out) if args.out else Path("output/manifests") / f"{layout.name}.manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2))
    print(f"Saved: {out}")
