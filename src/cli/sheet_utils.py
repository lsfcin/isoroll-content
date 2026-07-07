#!/usr/bin/env python3
"""sheet_utils.py — Shared utilities for sprite/pipeline sheet processing.

Shared home for grid splitting, rembg-based background removal, watermark
masking, and NB tile-sheet layout definitions. sprite_splitter.py and
preprocess.py still carry their own copies of split/rembg logic — migrating
them here is pending (see ROADMAP S0-E6).
"""

from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path
from typing import ClassVar

from PIL import Image, ImageChops, ImageDraw

# ---------------------------------------------------------------------------
# Layout definitions
# ---------------------------------------------------------------------------

DEFAULT_LAYOUTS: dict[str, list[list[str]]] = {
    "6cell": [["NW", "NE", "TOP"], ["SW", "SE", "CAPTION"]],
    "2cell": [["SW", "NE", "TOP", "CAPTION"]],
    "1cell": [["SW", "TOP", "CAPTION"]],
}


class SheetLayout:
    """Encapsulates a named NB tile-sheet layout: label grid + dimensions."""

    _cache: ClassVar[dict[str, "SheetLayout"]] = {}

    def __init__(self, name: str, grid: list[list[str]]) -> None:
        self.name = name
        self.grid = grid

    @classmethod
    def get(cls, name: str) -> "SheetLayout":
        if name not in cls._cache:
            if name not in DEFAULT_LAYOUTS:
                known = ", ".join(DEFAULT_LAYOUTS)
                raise ValueError(f"Unknown layout: {name}. Known: {known}")
            cls._cache[name] = cls(name, DEFAULT_LAYOUTS[name])
        return cls._cache[name]

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0]) if self.grid else 0

    def labels(self) -> list[str]:
        """Flat list of labels in reading order, top-left → bottom-right."""
        return [cell for row in self.grid for cell in row]

    def non_caption_labels(self) -> list[str]:
        return [label for label in self.labels() if label != "CAPTION"]

    def expected_cells(self) -> int:
        return self.rows * self.cols


# ---------------------------------------------------------------------------
# Image I/O
# ---------------------------------------------------------------------------


def load_image(path: Path) -> Image.Image:
    """Load an image and ensure it is RGBA."""
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    return Image.open(path).convert("RGBA")


# ---------------------------------------------------------------------------
# Grid split
# ---------------------------------------------------------------------------


def split_grid(img: Image.Image, rows: int, cols: int, *, padding: int = 0) -> list[Image.Image]:
    """Split image into rows × cols cells and return in reading order.

    Parameters:
        img: source image
        rows: number of grid rows
        cols: number of grid columns
        padding: pixels to trim from each cell edge

    Returns:
        List of PIL Images (one per cell)
    """
    w, h = img.size
    cell_w = w // cols
    cell_h = h // rows
    cells = []
    for row in range(rows):
        for col in range(cols):
            x1 = col * cell_w + padding
            y1 = row * cell_h + padding
            x2 = (col + 1) * cell_w - padding
            y2 = (row + 1) * cell_h - padding
            cells.append(img.crop((x1, y1, x2, y2)))
    return cells


# ---------------------------------------------------------------------------
# Background removal (rembg only)
# ---------------------------------------------------------------------------


def remove_background(img: Image.Image) -> Image.Image:
    """Remove background using rembg.remove().

    Raises:
        SystemExit if rembg is not installed.
    """
    try:
        from rembg import remove
    except ImportError:
        print("ERROR: rembg not installed.")
        print("  pip install \"rembg[gpu]\" Pillow")
        sys.exit(1)

    if isinstance(img, bytes):
        result_bytes = remove(img)
    else:
        buf = BytesIO()
        img.save(buf, format="PNG")
        result_bytes = remove(buf.getvalue())

    result_buf = BytesIO(result_bytes)
    return Image.open(result_buf).convert("RGBA")


# ---------------------------------------------------------------------------
# Watermark removal
# ---------------------------------------------------------------------------


def remove_watermark(
    img: Image.Image,
    *,
    region: tuple[int, int, int, int] | None = None,
) -> Image.Image:
    """Erase a region by making it completely transparent.

    Parameters:
        img: input image
        region: (x1, y1, x2, y2) in absolute pixels, or None for a
                default bottom-right ~ caption cell area.
    """
    w, h = img.size
    if region is None:
        x1, y1, x2, y2 = int(w * 0.65), int(h * 0.65), w, h
    else:
        x1, y1, x2, y2 = region

    mask = Image.new("L", (w, h), 255)
    draw = ImageDraw.Draw(mask)
    draw.rectangle((x1, y1, x2, y2), fill=0)
    r, g, b, a = img.split()
    alpha = ImageChops.multiply(a, mask)
    return Image.merge("RGBA", (r, g, b, alpha))
