from dataclasses import dataclass, field

STEPS: int
STAIR_RISE: float

@dataclass
class Opening:
    kind: str
    offset: int

@dataclass
class Box:
    u0: float
    v0: float
    l: float
    d: float
    h: float
    kind: str
    openings: list = field(default_factory=list)
    axis: str = ...

def massing(layout, merge: bool = True): ...
