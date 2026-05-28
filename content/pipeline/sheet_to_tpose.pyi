from _typeshed import Incomplete
from pathlib import Path

OUTER_MARGIN: int
CELL_W: int
CELL_H: int
BORDER: int
COLS: int
ROWS: int
PANEL_NAMES: Incomplete
TPOSE_COL: Incomplete
TPOSE_ROW: Incomplete

def cell_box(col, row): ...
def extract(sheet_path: Path, char: str, out_dir: Path, offset_x: int, offset_y: int, debug: bool): ...
