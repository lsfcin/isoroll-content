from _typeshed import Incomplete

def parse_args(): ...

SCALE: float
SHIFT_Y: float
DIRECTIONS: Incomplete
ELEVATION: float
DIST: float
RX: Incomplete
RY: Incomplete

def apply_uv_texture(mesh_objs, front_path, back_path): ...

class _FBXStub:
    axis_forward: str
    axis_up: str
    def report(self, *a) -> None: ...

def load_fbx(path) -> None: ...
def render_one(scene, scale, shift_y, azim_deg, out_path) -> None: ...
def main() -> None: ...
