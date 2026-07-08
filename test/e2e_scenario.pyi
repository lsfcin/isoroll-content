from PIL import Image
from _typeshed import Incomplete
from pathlib import Path

ROOT: Incomplete
PIPELINE_DIR: Incomplete
CLI_DIR: Incomplete
PY: Incomplete
CYAN_TOL: int
NW_IOU_MIN: float
OTHER_IOU_MIN: float
LABELS: Incomplete

def run_cli(script: str, args: list[str], cwd: Path) -> str: ...
def recolor_preserve_silhouette(img: Image.Image) -> Image.Image: ...
def inject_residue(dirty: Image.Image, marked: Image.Image, region_box: tuple[int, int, int, int]) -> Image.Image: ...
def main() -> int: ...
