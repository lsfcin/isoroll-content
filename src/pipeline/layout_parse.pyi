from _typeshed import Incomplete
from dataclasses import dataclass, field
from layout_groups import ENCLOSE as ENCLOSE, ROOF_FORMS as ROOF_FORMS, STAIR_TYPES as STAIR_TYPES, grp_base_data as grp_base_data, grp_cell_voxels as grp_cell_voxels

WALL: Incomplete
FLOOR: Incomplete
VOID: Incomplete
DOOR: Incomplete
WINDOW: Incomplete
STAIR_N: Incomplete
STAIR_E: Incomplete
STAIR_S: Incomplete
STAIR_W: Incomplete
STAIRS: Incomplete
SOLID: Incomplete
MARKERS: Incomplete
KNOWN: Incomplete
DEFAULT_WALL_H: int

@dataclass
class Level:
    g: list
    side: dict = field(default_factory=dict)
    type: dict = field(default_factory=dict)
    wmat: dict = field(default_factory=dict)
    fh: dict = field(default_factory=dict)

@dataclass
class Group:
    kind: str
    cells: list
    form: int
    dir: str
    incl: float
    z: float
    enclose: int = ...

@dataclass
class Layout:
    name: str
    grid: list
    wall_h: int = ...
    rows: int = ...
    cols: int = ...
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    levels: dict = field(default_factory=dict)
    groups: list = field(default_factory=list)
    def kind(self, u, v): ...

def rotate_cw(layout, turns: int = 1): ...
def rotate_point(u, v, rows, cols, turns: int = 1): ...
def validate(layout): ...
def parse_text(text, name: str = 'layout'): ...
def load(path): ...
