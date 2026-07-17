from _typeshed import Incomplete
from dataclasses import dataclass

UNIT_SQUARE: Incomplete
WALL_H: float
THIN: float
ROOF_H: float
STAIR_ENCLOSURE: Incomplete
STAIR_LATERAL: Incomplete
ROOF_RIDGE_V: float
SLAB_THICK: float

@dataclass
class Face:
    pts: list
    kind: str
    mat: str = ...
    enclosure: str = ...

def extrude(footprint, z0, h, mat: str = 'blank'): ...
def from_boxes(boxes, mat: str = 'blank'): ...

MODULES: Incomplete
