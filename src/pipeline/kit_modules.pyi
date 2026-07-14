from _typeshed import Incomplete
from dataclasses import dataclass

UNIT_SQUARE: Incomplete
WALL_H: float
THIN: float
ROOF_H: float
ROOF_RIDGE_V: float
ROOF_EAVE: float
OPENING_MARGIN: float

@dataclass
class Face:
    pts: list
    kind: str
    mat: str = ...

def extrude(footprint, z0, h, mat: str = 'blank'): ...
def from_boxes(boxes, mat: str = 'blank'): ...

MODULES: Incomplete
