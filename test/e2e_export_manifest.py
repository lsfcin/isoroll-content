#!/usr/bin/env python3
"""e2e_export_manifest.py — Loop 5 user scenario: export-manifest CLI verb, full round-trip.

Not a pytest file (`e2e_` prefix, no `test_` — never auto-collected by
`verify-fast`/`verify-full`). Chains the real entrypoints end-to-end, the
way a module importer working the P2 seam would exercise them:

  1. `iso-cli.py export-manifest` (the real dispatch path, subprocess —
     not a direct `run_export()` call) exports the l-room scene for the
     default NW view.
  2. The written manifest is checked for C1 shape (every tile/wall has the
     fields the module's importer needs) and, independently of the CLI's
     own internal gate, re-validated against `wall_schema.validate_manifest`
     (C2) — a clean pass here proves the schema mirror agrees with what the
     exporter actually wrote to disk, not just what it computed in memory.
  3. C3 round-trip: wall / door / window / stair counts are re-derived
     straight from the layout DSL via `layout_parse.load` + `layout_massing`
     — the source of truth the manifest must agree with — independently of
     the manifest-building code path itself.
  4. C4: every tile asset present in kit.json resolves under the real
     `output/kit-guide` on disk (the actual gray kit, not a fixture copy).
  5. A second, different view (SW) is exported through the same real CLI
     call to confirm the verb behaves correctly across the `--view` axis,
     not just the default.
  6. Negative path: the CLI is invoked a third time against a kit dir with
     `wall.png` deleted — the real subprocess must exit nonzero and print
     the missing-asset error, proving the C2 "failure = nonzero exit"
     contract holds through the actual entrypoint, not only through a
     direct `validate_manifest()` call.

Usage: python3 test/e2e_export_manifest.py
Exit 0 + "PASS" line on success, exit 1 on any verdict mismatch.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI_DIR = ROOT / "src" / "cli"
PIPELINE_DIR = ROOT / "src" / "pipeline"
LAYOUT = ROOT / "src" / "pipeline" / "layouts" / "l-room.txt"
KIT_DIR = ROOT / "output" / "kit-guide"
PY = sys.executable

sys.path.insert(0, str(PIPELINE_DIR))
sys.path.insert(0, str(CLI_DIR))
from layout_parse import load  # noqa: E402
from layout_massing import massing  # noqa: E402
from wall_schema import validate_manifest  # noqa: E402


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PY, str(CLI_DIR / "iso-cli.py"), *args],
        cwd=ROOT, capture_output=True, text=True,
    )


def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="e2e-export-manifest-"))
    nw_out = workdir / "l-room-NW.manifest.json"
    sw_out = workdir / "l-room-SW.manifest.json"
    broken_kit = workdir / "kit-guide-broken"

    print(f"[1/6] iso-cli.py export-manifest --view NW -> {nw_out}")
    result = run_cli(["export-manifest", "--layout", str(LAYOUT), "--view", "NW", "--out", str(nw_out)])
    print(result.stdout.strip())
    if result.returncode != 0 or not nw_out.exists():
        print(f"FAIL: NW export did not succeed (exit={result.returncode})\n{result.stderr}")
        return 1
    manifest = json.loads(nw_out.read_text())

    print("[2/6] C1 shape + C2 independent re-validation of the written file")
    tile_fields = {"piece", "asset", "facing", "u", "v", "boundHeight", "imageOffset", "pxPerVoxel"}
    wall_fields = {"ax", "ay", "bx", "by", "topOffset", "bottomOffset", "config"}
    shape_ok = (
        bool(manifest.get("tiles")) and all(tile_fields <= t.keys() for t in manifest["tiles"])
        and bool(manifest.get("walls")) and all(wall_fields <= w.keys() for w in manifest["walls"])
    )
    reval_errors = validate_manifest(manifest, str(KIT_DIR))
    print(f"  shape_ok={shape_ok} reval_errors={reval_errors}")
    if not shape_ok or reval_errors:
        print("FAIL: written manifest fails shape/schema re-check")
        return 1

    print("[3/6] C3 round-trip: counts re-derived from the layout DSL")
    layout = load(LAYOUT)
    expected_walls = len([b for b in massing(layout, merge=True) if b.kind == "wall"])
    doors = sum(1 for t in manifest["tiles"] if t["piece"].startswith("door"))
    windows = sum(1 for t in manifest["tiles"] if t["piece"].startswith("window"))
    stairs = sum(1 for t in manifest["tiles"] if t["piece"] == "stair")
    dsl_doors = sum(row.count("D") for row in Path(LAYOUT).read_text().splitlines())
    dsl_windows = sum(row.count("W") for row in Path(LAYOUT).read_text().splitlines())
    counts_ok = (
        len(manifest["walls"]) == expected_walls
        and doors == dsl_doors and windows == dsl_windows and stairs == 0
    )
    print(f"  walls={len(manifest['walls'])}/{expected_walls} doors={doors}/{dsl_doors} windows={windows}/{dsl_windows} stairs={stairs}")
    if not counts_ok:
        print("FAIL: manifest counts do not round-trip against the layout DSL")
        return 1

    print("[4/6] C4 asset resolution against the real gray kit")
    kit_pieces = json.loads((KIT_DIR / "kit.json").read_text())["pieces"]
    resolved_any = False
    for tile in manifest["tiles"]:
        if tile["piece"] in kit_pieces:
            resolved_any = True
            if not (KIT_DIR / tile["asset"]).exists():
                print(f"FAIL: tile asset does not resolve: {tile['asset']}")
                return 1
    if not resolved_any:
        print("FAIL: no tile in the manifest referenced a real kit piece")
        return 1

    print("[5/6] second real export, different view (SW), same seam")
    result_sw = run_cli(["export-manifest", "--layout", str(LAYOUT), "--view", "SW", "--out", str(sw_out)])
    print(result_sw.stdout.strip())
    sw_ok = result_sw.returncode == 0 and sw_out.exists()
    if sw_ok:
        sw_manifest = json.loads(sw_out.read_text())
        sw_ok = sw_manifest["view"] == "SW" and validate_manifest(sw_manifest, str(KIT_DIR)) == []
    print(f"  sw_ok={sw_ok}")
    if not sw_ok:
        print("FAIL: SW view export did not round-trip cleanly")
        return 1

    print("[6/6] negative path: kit missing an asset -> real CLI must exit nonzero")
    shutil.copytree(KIT_DIR, broken_kit)
    (broken_kit / "wall.png").unlink()
    result_broken = run_cli(["export-manifest", "--layout", str(LAYOUT), "--kit", str(broken_kit),
                              "--view", "NW", "--out", str(workdir / "l-room-broken.manifest.json")])
    print(result_broken.stdout.strip())
    broken_ok = result_broken.returncode != 0 and "wall.png" in result_broken.stdout
    print(f"  broken_ok={broken_ok} exit={result_broken.returncode}")
    if not broken_ok:
        print("FAIL: exporter did not refuse a manifest with a missing asset")
        return 1

    print("RESULT shape_ok=True counts_ok=True c4_ok=True sw_ok=True broken_ok=True")
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
