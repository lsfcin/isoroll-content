import subprocess
from _typeshed import Incomplete
from pathlib import Path

ROOT: Incomplete
PIPELINE_DIR: Incomplete
CLI_DIR: Incomplete
GOLDEN: Incomplete
PY: Incomplete
W: Incomplete
D: Incomplete
H: Incomplete

def run_cli(script: str, args: list[str], cwd: Path) -> subprocess.CompletedProcess: ...
def main() -> int: ...
