from _typeshed import Incomplete

FACE_TOP: Incomplete
FACE_LONG: Incomplete
FACE_CAP: Incomplete
MAGENTA: Incomplete
SILHOUETTE = MAGENTA
GRID_LINE = MAGENTA
SIL_WIDTH: int
GRID_WIDTH: int
MIN_THICK: float
HINGE_BAND_FRAC: float
TOP_FOLD_RATIO: Incomplete

def fit_scale(l, d, h, avail_w, avail_h): ...
def draw_iso_panel(img, l, d, h, view, cell_box, pad: int = 18, mark_edge: bool = False): ...
def draw_square_grid(draw, cols, rows, color, cell_box, pad: int = 18) -> None: ...
def draw_flat_grid(draw, cols, rows, body_color, top_rows, cell_box, pad: int = 18): ...
