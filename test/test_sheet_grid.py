#!/usr/bin/env python3
"""test_sheet_grid.py — detect_grid + strip_linework on synthetic magenta-grid fixtures (C1)."""

from PIL import Image, ImageDraw

from fixtures import magenta_grid_sheet
from sheet_grid import detect_grid, magenta_mask, strip_linework
from sheet_utils import even_boundaries, split_cells


def test_detect_grid_matches_even_division_no_drift():
    img, true_xs, true_ys = magenta_grid_sheet(2, 3)
    xs, ys = detect_grid(img, 2, 3)

    assert true_xs == even_boundaries(img.width, 3)
    assert true_ys == even_boundaries(img.height, 2)
    for detected, expected in zip(xs, true_xs):
        assert abs(detected - expected) <= 1
    for detected, expected in zip(ys, true_ys):
        assert abs(detected - expected) <= 1


def test_strip_linework_removes_magenta_keeps_blob_body():
    img, true_xs, true_ys = magenta_grid_sheet(2, 3)
    xs, ys = detect_grid(img, 2, 3)
    cells = split_cells(img, xs, ys)

    # cell (r=0, c=1) has one magenta line: its left edge (boundary xs[1]).
    cell = cells[1]
    original_blob_px = cell.getpixel((50, 50))

    out = strip_linework(cell)

    mmask = magenta_mask(out)
    assert sum(1 for p in mmask.getdata() if p) == 0
    assert out.getpixel((50, 50)) == original_blob_px


def test_strip_linework_keeps_interior_near_white_pixel():
    size = 100
    img = Image.new("RGBA", (size, size), (180, 180, 180, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 1, size - 1), fill=(255, 0, 255, 255))  # magenta edge
    draw.rectangle((45, 45, 55, 55), fill=(240, 240, 240, 255))  # interior near-white

    out = strip_linework(img)

    mmask = magenta_mask(out)
    assert sum(1 for p in mmask.getdata() if p) == 0
    assert out.getpixel((50, 50)) == (240, 240, 240, 255)
