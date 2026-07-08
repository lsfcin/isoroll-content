#!/usr/bin/env python3
"""test_guide_marks.py — residue_count on synthetic cyan-mark fixtures (C2)."""

from fixtures import clean_image, cyan_squares
from guide_marks import residue_count


def test_residue_count_in_expected_band_for_k_squares():
    k, side = 3, 10
    img = cyan_squares(k, side=side)
    n = residue_count(img)
    exact = k * side * side
    assert 0.95 * exact <= n <= exact


def test_residue_count_zero_on_clean_image():
    img = clean_image()
    assert residue_count(img) == 0
