#!/usr/bin/env python3
"""e2e_scale_consistency.py — Loop 5 user scenario: an artist regenerates a
real 9panel guide sheet, trusts the shared-scale sidecar, and QC catches it
if a legacy per-cell render sneaks back in.

Not a pytest file (no `test_` prefix — never auto-collected by
`verify-fast`/`verify-full`). Chains real entrypoints end-to-end, the way an
artist's render batch would exercise them:

  1. make_tile_guide.py generates a real 9panel guide (subprocess, cwd=src/pipeline,
     default shared-scale mode — no --legacy-autofit).
  2. The {stem}.scale.json sidecar is loaded and checked: exactly one
     px_per_voxel value covers all 9 panels (single source of truth, no
     downstream re-measuring pixels — C2).
  3. sheet_qc.py CLI runs cross_view_dims against that sidecar (subprocess,
     cwd=src/cli) — must exit 0, clean (C3, shared-scale side).
  4. The same wall is regenerated with --legacy-autofit (per-cell autofit,
     the pre-change behavior).
  5. sheet_qc.py CLI runs again against the legacy sidecar — must exit
     nonzero with >=1 violation (C3, bidirectional: QC catches a stale/
     legacy sheet whose per-panel bboxes no longer agree with one shared
     scale).
  6. The legacy PNG bytes are compared against the pre-change golden fixture
     (test/fixtures/golden/9panel.png, captured in Loop 4a/T1) — must be
     byte-identical, proving --legacy-autofit is a true behavior-preserving
     escape hatch (C1).

Usage: python3 test/e2e_scale_consistency.py
Exit 0 + "PASS" line on success, exit 1 on any verdict mismatch.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_DIR = ROOT / "src" / "pipeline"
CLI_DIR = ROOT / "src" / "cli"
GOLDEN = ROOT / "test" / "fixtures" / "golden" / "9panel.png"
PY = sys.executable

# Must match test/test_scale_consistency.py GOLDEN_SPECS["9panel"] (the params
# test/fixtures/golden/9panel.png was captured with in Loop 4a/T1).
W, D, H = 5, 2, 3


def run_cli(script: str, args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PY, script, *args], cwd=cwd, capture_output=True, text=True
    )


def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="e2e-scale-consistency-"))
    shared_out = workdir / "9panel_shared.png"
    legacy_out = workdir / "9panel_legacy.png"
    shared_sidecar = shared_out.with_suffix(".scale.json")
    legacy_sidecar = legacy_out.with_suffix(".scale.json")

    print(f"[1/6] make_tile_guide.py (default shared-scale) -> {shared_out}")
    r1 = run_cli(
        "make_tile_guide.py",
        ["--width", str(W), "--depth", str(D), "--height", str(H),
         "--layout", "9panel", "--output", str(shared_out)],
        cwd=PIPELINE_DIR,
    )
    print(r1.stdout.strip())
    if r1.returncode != 0:
        print("FAIL: make_tile_guide.py (shared-scale) errored:\n" + r1.stderr)
        return 1

    print(f"[2/6] verify sidecar: one shared px_per_voxel -> {shared_sidecar}")
    if not shared_sidecar.exists():
        print(f"FAIL: sidecar not written: {shared_sidecar}")
        return 1
    data = json.loads(shared_sidecar.read_text())
    s_shared = data.get("px_per_voxel")
    panels = data.get("panels", [])
    print(f"  px_per_voxel = {s_shared}  panels = {len(panels)}")
    sidecar_ok = isinstance(s_shared, (int, float)) and len(panels) == 9
    if not sidecar_ok:
        print("FAIL: sidecar missing single px_per_voxel or wrong panel count")
        return 1

    print("[3/6] sheet_qc.py on shared-scale sheet (expect clean, exit 0)")
    r2 = run_cli("sheet_qc.py", [str(shared_sidecar)], cwd=CLI_DIR)
    print(r2.stdout.strip() or "(no violations printed)")
    qc_shared_clean = r2.returncode == 0
    print(f"  exit={r2.returncode} clean={qc_shared_clean}")

    print(f"[4/6] make_tile_guide.py --legacy-autofit -> {legacy_out}")
    r3 = run_cli(
        "make_tile_guide.py",
        ["--width", str(W), "--depth", str(D), "--height", str(H),
         "--layout", "9panel", "--output", str(legacy_out), "--legacy-autofit"],
        cwd=PIPELINE_DIR,
    )
    print(r3.stdout.strip())
    if r3.returncode != 0:
        print("FAIL: make_tile_guide.py (legacy) errored:\n" + r3.stderr)
        return 1

    print("[5/6] sheet_qc.py on legacy sheet (expect violations, nonzero exit)")
    r4 = run_cli("sheet_qc.py", [str(legacy_sidecar)], cwd=CLI_DIR)
    print(r4.stdout.strip())
    qc_legacy_flagged = r4.returncode != 0 and "VIOLATION" in r4.stdout
    print(f"  exit={r4.returncode} flagged={qc_legacy_flagged}")

    print(f"[6/6] byte-compare legacy output vs golden -> {GOLDEN}")
    got = legacy_out.read_bytes()
    want = GOLDEN.read_bytes()
    legacy_matches_golden = got == want
    print(f"  legacy bytes == golden bytes: {legacy_matches_golden}")

    print(
        f"RESULT sidecar_ok={sidecar_ok} qc_shared_clean={qc_shared_clean} "
        f"qc_legacy_flagged={qc_legacy_flagged} legacy_matches_golden={legacy_matches_golden}"
    )

    if not (sidecar_ok and qc_shared_clean and qc_legacy_flagged and legacy_matches_golden):
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
