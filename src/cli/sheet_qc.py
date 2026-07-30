#!/usr/bin/env python3
"""sheet_qc.py — silhouette-vs-guide-box IoU QC for NB tile-sheet output cells,
plus cross-view dimension consistency QC for shared-scale tile guide sheets."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))

from PIL import Image, ImageChops

from panel_geometry import content_extent  # noqa: E402

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


# Tolerance for cross-view dimension consistency (implied vs. recorded px_per_voxel).
DIM_TOLERANCE = 0.02


def cross_view_dims(scale_info: dict, tol: float = DIM_TOLERANCE) -> list:
    """Cross-view dimension check: for each recorded panel, the px-per-voxel
    implied by its content bbox (via content_extent, the same projection math
    used to draw it) must match the sheet's recorded px_per_voxel within `tol`
    relative error. A shared-scale sheet is clean by construction; a legacy
    (per-cell autofit) sheet's non-limiting panels were drawn at their own
    scale, so this flags them — that is the intended, not a bug."""
    px_per_voxel = scale_info["px_per_voxel"]
    violations = []
    for panel in scale_info["panels"]:
        w_u, h_u = content_extent(panel["orientation"], panel["w"], panel["d"], panel["h"])
        x0, y0, x1, y1 = panel["bbox"]
        implied = (x1 - x0) / w_u
        rel = abs(implied - px_per_voxel) / px_per_voxel
        if rel > tol:
            violations.append({"row": panel["row"], "col": panel["col"], "orientation": panel["orientation"],
                                "implied": implied, "expected": px_per_voxel, "rel": rel})
    return violations


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Cross-view dimension QC for a *.scale.json sidecar.")
    parser.add_argument("sidecar", type=Path, help="path to a {stem}.scale.json sidecar")
    parser.add_argument("--tolerance", type=float, default=DIM_TOLERANCE)
    args = parser.parse_args()

    scale_info = json.loads(args.sidecar.read_text())
    violations = cross_view_dims(scale_info, args.tolerance)
    for v in violations:
        print(f"VIOLATION row={v['row']} col={v['col']} orientation={v['orientation']} "
              f"implied={v['implied']:.4f} expected={v['expected']:.4f} rel={v['rel']:.4f}")
    sys.exit(1 if violations else 0)
