#!/usr/bin/env python3
"""e2e_scenario.py — Loop 5 user scenario: full postproc QC pipeline, one dirty NB output.

Not a pytest file (no `test_` prefix — never auto-collected by `verify-fast`/
`verify-full`). Chains real entrypoints end-to-end, the way an artist's
render batch would exercise them:

  1. make_tile_guide.py generates a real 6cell tile guide (subprocess, cwd=src/pipeline).
  2. guide_marks.py overlays registration marks on it (subprocess CLI, cwd=src/pipeline).
  3. A simulated "NB output" is built in-process: the guide is recolored
     (silhouette-preserving tint — background stays near-black, content
     brightens) to stand in for NB's restyle, then a patch of the real cyan
     marks is pasted back into the NW panel to simulate marks NB failed to
     chroma-key out (residue).
  4. sheet_postproc.py (the real grid-split CLI: detect_grid + split_cells +
     strip_linework, --keep-bg so no rembg/network call — same C5 "no NB/API
     calls" constraint as the unit suite) runs against both the dirty output
     and the clean guide (subprocess, cwd=src/cli).
  5. sheet_qc + guide_marks metrics run against the split cells: residue_count
     must catch the injected residue and stay 0 on the clean guide;
     silhouette_iou (RGB/luminance path, i.e. ignoring the strip_linework
     alpha channel so it measures actual drawn content, not just which
     pixels survived line-stripping) must be high everywhere and visibly
     dip — but stay high — on the residue-contaminated NW panel.

Usage: python3 test/e2e_scenario.py
Exit 0 + "PASS" line on success, exit 1 on any verdict mismatch.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_DIR = ROOT / "src" / "pipeline"
CLI_DIR = ROOT / "src" / "cli"
PY = sys.executable

sys.path.insert(0, str(CLI_DIR))
sys.path.insert(0, str(PIPELINE_DIR))
import sheet_grid  # noqa: E402
import sheet_qc  # noqa: E402
import guide_marks  # noqa: E402

CYAN_TOL = 60
NW_IOU_MIN = 0.90
OTHER_IOU_MIN = 0.95
LABELS = ["NW", "NE", "TOP", "SW", "SE"]  # CAPTION is skipped by sheet_postproc.run()


def run_cli(script: str, args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        [PY, script, *args], cwd=cwd, capture_output=True, text=True, check=True
    )
    return result.stdout


def recolor_preserve_silhouette(img: Image.Image) -> Image.Image:
    """Stand-in for an NB restyle pass: tint every pixel except real magenta
    linework. Background (0,0,0) * tint == (0,0,0), so it stays background
    under sheet_qc's luminance fallback; foreground content brightens/shifts
    hue but stays well above LUMA_MIN — the silhouette is preserved even
    though the artwork looks different."""
    arr = np.array(img.convert("RGB")).astype(np.float64)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    magenta = (r >= sheet_grid.RB_MIN) & (b >= sheet_grid.RB_MIN) & (g <= sheet_grid.G_MAX)
    tint = np.clip(arr * np.array([0.6, 0.9, 1.3]), 0, 255)
    out = np.where(magenta[..., None], arr, tint).astype(np.uint8)
    return Image.fromarray(out, mode="RGB")


def inject_residue(dirty: Image.Image, marked: Image.Image, region_box: tuple[int, int, int, int]) -> Image.Image:
    """Paste the real cyan mark pixels found in `marked` within `region_box`
    onto `dirty`, simulating a few registration marks NB failed to key out."""
    arr_dirty = np.array(dirty.convert("RGB"))
    arr_marked = np.array(marked.convert("RGB"))
    r, g, b = (arr_marked[..., i].astype(int) for i in range(3))
    cyan = (np.abs(r - 0) <= CYAN_TOL) & (np.abs(g - 255) <= CYAN_TOL) & (np.abs(b - 255) <= CYAN_TOL)
    mask = np.zeros_like(cyan)
    x1, y1, x2, y2 = region_box
    mask[y1:y2, x1:x2] = cyan[y1:y2, x1:x2]
    arr_dirty[mask] = arr_marked[mask]
    return Image.fromarray(arr_dirty, mode="RGB")


def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="e2e-postproc-"))
    guide_path = workdir / "guide.png"
    marked_path = workdir / "marked.png"
    dirty_path = workdir / "nb_output_dirty.png"
    clean_split_dir = workdir / "clean_split"
    dirty_split_dir = workdir / "dirty_split"

    print(f"[1/5] make_tile_guide.py -> {guide_path}")
    print(run_cli(
        "make_tile_guide.py",
        ["--width", "3", "--height", "2", "--layout", "6cell", "--output", str(guide_path)],
        cwd=PIPELINE_DIR,
    ).strip())

    print(f"[2/5] guide_marks.py -> {marked_path}")
    print(run_cli(
        "guide_marks.py",
        ["--input", str(guide_path), "--output", str(marked_path),
         "--layout", "6cell", "--scheme", "columns", "--back-mode", "occluded"],
        cwd=PIPELINE_DIR,
    ).strip())

    print("[3/5] simulating NB output: recolor + leave residue in NW panel")
    guide_img = Image.open(guide_path)
    marked_img = Image.open(marked_path)
    dirty = recolor_preserve_silhouette(guide_img)
    w, h = dirty.size
    nw_box = (0, 0, w // 3, h // 2)  # NW panel of the 6cell (2 rows x 3 cols) grid
    dirty = inject_residue(dirty, marked_img, nw_box)
    dirty.save(dirty_path)

    print("[4/5] sheet_postproc.py grid split (--keep-bg: no rembg/network call)")
    run_cli(
        "sheet_postproc.py",
        [str(dirty_path), "--layout", "6cell", "-o", str(dirty_split_dir), "--prefix", "e2e", "--keep-bg"],
        cwd=CLI_DIR,
    )
    run_cli(
        "sheet_postproc.py",
        [str(guide_path), "--layout", "6cell", "-o", str(clean_split_dir), "--prefix", "e2e", "--keep-bg"],
        cwd=CLI_DIR,
    )

    print("[5/5] sheet_qc + guide_marks metrics")
    residue_dirty = guide_marks.residue_count(Image.open(dirty_path))
    residue_clean = guide_marks.residue_count(Image.open(guide_path))
    print(f"  residue_count(dirty nb output) = {residue_dirty}")
    print(f"  residue_count(clean guide)     = {residue_clean}")

    ious: dict[str, float] = {}
    for label in LABELS:
        dirty_cell = Image.open(dirty_split_dir / f"e2e_{label}.png").convert("RGB")
        clean_cell = Image.open(clean_split_dir / f"e2e_{label}.png").convert("RGB")
        box_mask = sheet_qc.silhouette_mask(clean_cell)
        ious[label] = sheet_qc.silhouette_iou(dirty_cell, box_mask)
        print(f"  silhouette_iou[{label}] = {ious[label]:.4f}")

    residue_ok = residue_dirty > 0 and residue_clean == 0
    iou_ok = ious["NW"] >= NW_IOU_MIN and all(ious[l] >= OTHER_IOU_MIN for l in ("NE", "TOP", "SW", "SE"))
    print(f"RESULT residue_detected={residue_ok} iou_high={iou_ok}")

    if not (residue_ok and iou_ok):
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
