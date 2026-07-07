from _typeshed import Incomplete
from dataclasses import dataclass
from pathlib import Path

BG: Incomplete
MAGENTA: Incomplete
ORIENTATIONS: Incomplete
OBLIQUE: Incomplete
REQUIRED_KEYS: Incomplete

@dataclass
class CellSpec:
    row: int
    col: int
    orientation: str
    w: int
    h: int
    d: int
    label: str = ...
    mark: bool = ...

def draw_panel(img, draw, orientation, w, d, h, box, mark: bool = False) -> None: ...
def draw_caption(draw, box, font, label) -> None: ...
def parse_spec(spec): ...
def render_cells(rows, cols, grid, cell_px: int = 320): ...
def generate(spec, out_path: Path, cell_px: int = 320): ...
def resolve_cells_arg(raw: str): ...
