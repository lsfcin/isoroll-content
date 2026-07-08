#!/usr/bin/env python3
"""test_sheet_qc.py — silhouette_iou unit tests (C3)."""

from fixtures import alpha_blob, filled_mask
from sheet_qc import silhouette_iou


def test_silhouette_iou_identical_masks_near_one():
    box = (10, 10, 50, 50)
    cell = alpha_blob((64, 64), box)
    box_mask = filled_mask((64, 64), box)
    assert silhouette_iou(cell, box_mask) > 0.99


def test_silhouette_iou_disjoint_masks_low():
    cell = alpha_blob((64, 64), (0, 0, 20, 20))
    box_mask = filled_mask((64, 64), (40, 40, 60, 60))
    assert silhouette_iou(cell, box_mask) < 0.5
