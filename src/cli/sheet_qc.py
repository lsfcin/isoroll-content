#!/usr/bin/env python3
"""sheet_qc.py — silhouette-vs-guide-box IoU QC for NB tile-sheet output cells."""

from __future__ import annotations

from PIL import Image, ImageChops

# Alpha value at/above which a pixel counts as foreground, for cells that
# carry an alpha channel.
ALPHA_MIN = 8
# Luminance value at/above which a pixel counts as foreground, for cells
# with no alpha channel (silhouette falls back to "not near-black bg").
LUMA_MIN = 16


def _has_alpha(img: Image.Image) -> bool:
    """True when `img` carries usable transparency."""
    return img.mode in ("RGBA", "LA", "PA") or "transparency" in img.info


def silhouette_mask(img: Image.Image, alpha_min: int = ALPHA_MIN) -> Image.Image:
    """Binary L mask (255 = foreground) from alpha, or luminance if opaque."""
    if _has_alpha(img):
        channel = img.convert("RGBA").getchannel("A")
        threshold = alpha_min
    else:
        channel = img.convert("L")
        threshold = LUMA_MIN
    return channel.point(lambda v: 255 if v >= threshold else 0)


def _count(mask: Image.Image) -> int:
    """Count of set (nonzero) pixels in a binary L mask."""
    return sum(1 for p in mask.getdata() if p)


def mask_iou(a: Image.Image, b: Image.Image) -> float:
    """Intersection-over-union of two binary L masks. Empty union -> 1.0."""
    inter = _count(ImageChops.multiply(a, b))
    union = _count(ImageChops.lighter(a, b))
    return 1.0 if union == 0 else inter / union


def silhouette_iou(cell: Image.Image, box_mask: Image.Image, alpha_min: int = ALPHA_MIN) -> float:
    """IoU between an NB output cell's silhouette and the guide box mask."""
    return mask_iou(silhouette_mask(cell, alpha_min), box_mask)
