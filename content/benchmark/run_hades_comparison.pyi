from _typeshed import Incomplete

COMFY_URL: str
COMFY_DIR: Incomplete
OUTPUT_DIR: Incomplete
BASE_DIR: Incomplete
WORKFLOW_PATH: Incomplete
RESULTS_DIR: Incomplete
PROMPT: str
SEED: int
CHECKPOINTS: Incomplete

def load_workflow(ckpt): ...
def submit(workflow): ...
def wait_for_output(prompt_id, before_set, timeout: int = 600): ...
def main() -> None: ...
