from _typeshed import Incomplete

def parse_args(): ...

SCALE: float
CAM_Z_OFFSETS: Incomplete
DIRECTIONS: Incomplete
ELEVATION: float
DIST: float
RX: Incomplete
RY: Incomplete

class _FBXStub:
    axis_forward: str
    axis_up: str
    def report(self, *a) -> None: ...

def load_fbx(path) -> None: ...
def render_one(scene, scale, cam_z_offset, azim_deg, out_path) -> None: ...
def main() -> None: ...
