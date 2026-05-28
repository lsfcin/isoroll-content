from _typeshed import Incomplete
from pathlib import Path

OUTER_MARGIN: int
CELL_W: int
CELL_H: int
BORDER: int
COLS: int
ROWS: int
BG: Incomplete
CELL_BG: Incomplete
BORDER_COLOR: Incomplete
MARKER_COLOR: Incomplete
LABEL_TITLE: Incomplete
LABEL_TPOSE: Incomplete
LABEL_SUB: Incomplete
SAFE_DIVIDER: Incomplete
LABEL_TOP_PAD: int
SAFE_ZONE_Y: int
PANEL_LABELS: Incomplete
FONT_PATHS: Incomplete

def load_font(size): ...
def total_size(): ...
def cell_origin(col, row): ...
def generate(out_path: Path): ...
