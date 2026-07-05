from _typeshed import Incomplete

TOP_RED: Incomplete
BACK_GRAY: Incomplete
FRONT_GREEN: Incomplete
WEST_BLUE: Incomplete
EAST_PURPLE: Incomplete
SILHOUETTE: Incomplete
GRID_LINE: Incomplete
SIL_WIDTH: int
GRID_WIDTH: int
TOP_FOLD_RATIO: Incomplete

def fit_scale(l, d, h, avail_w, avail_h): ...
def draw_iso_panel(img, l, d, h, view, cell_box, pad: int = 18): ...
def draw_square_grid(draw, cols, rows, color, cell_box, pad: int = 18) -> None: ...
def draw_flat_grid(draw, cols, rows, body_color, top_rows, cell_box, pad: int = 18): ...
