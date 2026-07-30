from _typeshed import Incomplete
from panel_geometry import content_extent as content_extent, panel_fit_scale as panel_fit_scale

FACE_TOP: Incomplete
FACE_LONG: Incomplete
FACE_CAP: Incomplete
MAGENTA: Incomplete
SILHOUETTE = MAGENTA
GRID_LINE = MAGENTA
SIL_WIDTH: int
GRID_WIDTH: int
HINGE_BAND_FRAC: float

def draw_iso_panel(img, l, d, h, view, cell_box, pad=..., mark_edge: bool = False, s=None): ...
def draw_square_grid(draw, cols, rows, color, cell_box, pad=..., s=None): ...
def draw_flat_grid(draw, cols, rows, body_color, top_rows, cell_box, pad=..., s=None): ...
