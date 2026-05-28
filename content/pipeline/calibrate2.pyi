from _typeshed import Incomplete

def parse_args(): ...

ORTHO_SCALES: Incomplete
CENTER_Z_VALS: Incomplete
DIRECTIONS: Incomplete
ELEVATION: float
RX: Incomplete
RY: Incomplete

class _FBXStub:
    axis_forward: str
    axis_up: str
    def report(self, *a) -> None: ...

def setup() -> None: ...
def load_fbx(path) -> None: ...
def render_one(scene, fbx_path, s, z, azim, out_path) -> None: ...
def main() -> None: ...
