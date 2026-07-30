#!/usr/bin/env python3
"""test_scale_consistency.py — shared-scale (px-per-voxel) tests for the
scale-consistency loop (C1-C4). Written before T2-T7 land: calls the new
surface (content_extent, panel_fit_scale, draw_*(s=...)->bbox, render_cells
shared_scale=, write_scale_sidecar, generate(shared_scale=), sheet_qc.
cross_view_dims + CLI) that does not exist yet on this branch, so every test
below is expected RED (AttributeError/TypeError = missing behavior, not a
test bug) until Loop 4b implements it.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

import make_tile_guide as mtg
import sheet_qc as qc
import tile_guide_matrix as tgm
import tile_guide_render as tgr

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = Path(__file__).resolve().parent / "fixtures" / "golden"
CELL_PX = 320

# Must match the params used to generate test/fixtures/golden/*.png (T1).
GOLDEN_SPECS = {
    "9panel": (5, 2, 3),
    "6cell": (4, 1, 3),
    "2cell": (6, 2, 2),
    "1cell": (3, 1, 4),
}


# ---------------------------------------------------------------- C1 ---
# content_extent / panel_fit_scale: single source of per-panel voxel-unit
# content dims + autofit scale, reused by both draw and QC sides.

def test_content_extent_oblique_matches_bbox_extent():
    l, d, h = 5, 2, 3
    minx, maxx, miny, maxy = tgr._bbox(l, d, h)
    w_u, h_u = tgr.content_extent("NE", l, d, h)
    assert w_u == pytest.approx(maxx - minx)
    assert h_u == pytest.approx(maxy - miny)


def test_content_extent_top_zero_dim_uses_min_thick():
    w_u, h_u = tgr.content_extent("TOP", 5, 0, 3)
    assert w_u == 5
    assert h_u == pytest.approx(tgr.MIN_THICK)


def test_content_extent_cardinal_ns_folds_top():
    w_u, h_u = tgr.content_extent("N", 4, 2, 3)
    assert w_u == 4
    assert h_u == pytest.approx(3 + 2 * tgr.TOP_FOLD_RATIO)


def test_panel_fit_scale_matches_legacy_fit_scale():
    l, d, h = 5, 2, 3
    pad = 18
    avail = CELL_PX - 2 * pad
    expected = tgr.fit_scale(l, d, h, avail, avail)
    got = tgr.panel_fit_scale("NE", l, d, h, CELL_PX)
    assert got == pytest.approx(expected)


def test_draw_iso_panel_accepts_forced_scale_and_returns_bbox():
    img = Image.new("RGB", (CELL_PX, CELL_PX), (0, 0, 0))
    bbox = tgr.draw_iso_panel(img, 5, 2, 3, "NE", (0, 0, CELL_PX, CELL_PX), s=10.0)
    assert bbox is not None and len(bbox) == 4


def test_render_cells_shared_scale_uniform_px_per_voxel():
    spec = {
        "rows": 1, "cols": 3,
        "cells": [
            {"row": 0, "col": 0, "orientation": "NE", "w": 5, "h": 3, "d": 2},
            {"row": 0, "col": 1, "orientation": "TOP", "w": 5, "h": 0, "d": 2},
            {"row": 0, "col": 2, "orientation": "N", "w": 5, "h": 3, "d": 2},
        ],
    }
    rows, cols, grid = tgm.parse_spec(spec)
    img, scale_info = tgm.render_cells(rows, cols, grid, cell_px=CELL_PX, shared_scale=True)
    assert "px_per_voxel" in scale_info
    s_shared = scale_info["px_per_voxel"]
    for panel in scale_info["panels"]:
        x0, y0, x1, y1 = panel["bbox"]
        w_u, h_u = tgr.content_extent(panel["orientation"], panel["w"], panel["d"], panel["h"])
        implied = (x1 - x0) / w_u
        assert implied == pytest.approx(s_shared, abs=1e-6)


def test_legacy_autofit_flag_reproduces_golden_bytes(tmp_path):
    for layout, (w, d, h) in GOLDEN_SPECS.items():
        out = tmp_path / f"{layout}.png"
        mtg.generate(w, d, h, layout, out, shared_scale=False)
        got = out.read_bytes()
        want = (GOLDEN / f"{layout}.png").read_bytes()
        assert got == want, f"{layout}: --legacy-autofit output diverged from golden"


# ---------------------------------------------------------------- C2 ---
# {stem}.scale.json sidecar: written by both generate() paths, extended
# (not clobbered) if a sidecar already exists at that stem.

def test_write_scale_sidecar_creates_expected_keys(tmp_path):
    out_path = tmp_path / "sheet.png"
    scale_info = {
        "px_per_voxel": 12.5,
        "panels": [{"row": 0, "col": 0, "orientation": "NE", "w": 5, "d": 2, "h": 3,
                     "bbox": [0, 0, 62, 62]}],
    }
    sidecar_path = tgm.write_scale_sidecar(out_path, scale_info)
    assert sidecar_path == out_path.with_suffix(".scale.json")
    data = json.loads(sidecar_path.read_text())
    assert data["px_per_voxel"] == pytest.approx(12.5)
    assert data["panels"][0]["bbox"] == [0, 0, 62, 62]


def test_write_scale_sidecar_extends_existing_file(tmp_path):
    out_path = tmp_path / "sheet.png"
    sidecar_path = out_path.with_suffix(".scale.json")
    sidecar_path.write_text(json.dumps({"other_key": "keep-me", "px_per_voxel": 1.0, "panels": []}))
    scale_info = {"px_per_voxel": 12.5, "panels": [{"row": 0, "col": 0, "orientation": "TOP",
                                                     "w": 5, "d": 2, "h": 0, "bbox": [0, 0, 40, 20]}]}
    tgm.write_scale_sidecar(out_path, scale_info)
    data = json.loads(sidecar_path.read_text())
    assert data["other_key"] == "keep-me"
    assert data["px_per_voxel"] == pytest.approx(12.5)


def test_make_tile_guide_generate_writes_sidecar(tmp_path):
    out = tmp_path / "guide.png"
    mtg.generate(4, 1, 3, "6cell", out, shared_scale=True)
    sidecar = out.with_suffix(".scale.json")
    assert sidecar.exists()
    data = json.loads(sidecar.read_text())
    assert "px_per_voxel" in data and "panels" in data


# ---------------------------------------------------------------- C3 ---
# sheet_qc.cross_view_dims: bidirectional — clean on a shared-scale sheet,
# violations on a legacy (per-cell autofit) sheet whose bboxes imply a
# different px-per-voxel than the recorded (shared) one.

def _panel(orientation, w, d, h, s):
    w_u, h_u = tgr.content_extent(orientation, w, d, h)
    return {"row": 0, "col": 0, "orientation": orientation, "w": w, "d": d, "h": h,
            "bbox": [0, 0, w_u * s, h_u * s]}


def test_cross_view_dims_clean_on_shared_scale():
    s = 20.0
    scale_info = {"px_per_voxel": s, "panels": [
        _panel("NE", 5, 2, 3, s),
        _panel("TOP", 5, 0, 2, s),
    ]}
    assert qc.cross_view_dims(scale_info) == []


def test_cross_view_dims_flags_legacy_mismatch():
    s_shared = 20.0
    s_cell = 15.0  # this panel was drawn at its own per-cell autofit scale
    scale_info = {"px_per_voxel": s_shared, "panels": [_panel("NE", 5, 2, 3, s_cell)]}
    violations = qc.cross_view_dims(scale_info)
    assert len(violations) == 1
    assert violations[0]["orientation"] == "NE"


def test_sheet_qc_cli_exit_codes(tmp_path):
    py = sys.executable
    s = 20.0
    clean = tmp_path / "clean.scale.json"
    clean.write_text(json.dumps({"px_per_voxel": s, "panels": [_panel("NE", 5, 2, 3, s)]}))
    dirty = tmp_path / "dirty.scale.json"
    dirty.write_text(json.dumps({"px_per_voxel": s, "panels": [_panel("NE", 5, 2, 3, 15.0)]}))

    r_clean = subprocess.run([py, "sheet_qc.py", str(clean)], cwd=ROOT / "src" / "cli",
                              capture_output=True, text=True)
    r_dirty = subprocess.run([py, "sheet_qc.py", str(dirty)], cwd=ROOT / "src" / "cli",
                              capture_output=True, text=True)
    assert r_clean.returncode == 0
    assert r_dirty.returncode == 1


# ---------------------------------------------------------------- C4 ---
# SPECS.md corrective-factor appendix (doc-only criterion; grep seam).

def test_specs_md_has_corrective_factor_appendix():
    text = (ROOT / "SPECS.md").read_text()
    assert "Scale corrective factor" in text
    assert "px_per_voxel" in text
