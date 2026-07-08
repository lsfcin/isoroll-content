#!/usr/bin/env python3
"""test_grid_drift.py — detect_grid tolerates +-2px grid-line drift (C4)."""

from fixtures import magenta_grid_sheet
from sheet_grid import detect_grid
from sheet_utils import split_cells


def test_detect_grid_snaps_to_drifted_interior_lines():
    drift = {("x", 0): 2, ("x", 1): -2, ("y", 0): 2}
    img, true_xs, true_ys = magenta_grid_sheet(2, 3, drift=drift)

    xs, ys = detect_grid(img, 2, 3)

    for i in (1, 2):  # interior x boundaries
        assert abs(xs[i] - true_xs[i]) <= 1
    assert abs(ys[1] - true_ys[1]) <= 1  # interior y boundary

    cells = split_cells(img, xs, ys)
    assert len(cells) == 6
