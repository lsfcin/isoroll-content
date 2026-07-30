from _typeshed import Incomplete
from dataclasses import dataclass
from typing import Callable

NLVL: int
WALLISH: Incomplete
DIAG: Incomplete
STAIRS: Incomplete
ARROW_CW: Incomplete
DIAG_CW: Incomplete
ASCENT: Incomplete
SIDE_NAME: Incomplete
ROOF_FORMS: Incomplete
STAIR_TYPES: Incomplete
ENCLOSE: Incomplete
TYPES: Incomplete

def diag_solid(grid, r, c, ch): ...

@dataclass
class _BaseData:
    aOf: Callable[[float, float], float]
    aLow: float
    aHigh: float
    rise: float
    form: str
    hAt: Callable[[float, float], float]

def grp_base_data(group): ...
def grp_cell_voxels(base_data, group, r, c): ...
