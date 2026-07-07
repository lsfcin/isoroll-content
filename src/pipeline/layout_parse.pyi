from _typeshed import Incomplete
from dataclasses import dataclass, field

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
KNOWN: Incomplete
DEFAULT_WALL_H: int

@dataclass
class Layout:
    name: str
    grid: list
    wall_h: int = ...
    rows: int = ...
    cols: int = ...
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    def kind(self, u, v): ...

def rotate_cw(layout, turns: int = 1): ...
def validate(layout): ...
def parse_text(text, name: str = 'layout'): ...
def load(path): ...
