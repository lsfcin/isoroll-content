"""ComfyUI API client helpers for the isoroll pipeline."""

import glob
import json
import os
import shutil
import time
import uuid

import requests

COMFY_BASE_URL = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")
PROMPT_URL = f"{COMFY_BASE_URL}/prompt"
UPLOAD_URL = f"{COMFY_BASE_URL}/upload/image"
TIMEOUT_SECONDS = 600


def get_comfy_dir() -> str:
    comfy_dir = os.environ.get("COMFY_DIR")
    if not comfy_dir:
        raise RuntimeError(
            "COMFY_DIR is not set.\n"
            "  Linux:   export COMFY_DIR=$HOME/ComfyUI\n"
            "  Windows: setx COMFY_DIR C:\\path\\to\\ComfyUI"
        )
    return comfy_dir


def get_output_dir() -> str:
    return os.path.join(get_comfy_dir(), "output")


def upload_image(image_path: str) -> str:
    """Upload image to ComfyUI input folder. Returns filename ComfyUI assigned."""
    with open(image_path, "rb") as f:
        res = requests.post(
            UPLOAD_URL,
            files={"image": (os.path.basename(image_path), f, "image/png")},
        )
        res.raise_for_status()
        return res.json()["name"]


def send_prompt(workflow: dict) -> dict | None:
    payload = {"prompt": workflow, "client_id": str(uuid.uuid4())}
    try:
        res = requests.post(PROMPT_URL, json=payload)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"[FAIL] ComfyUI request failed: {e}")
        return None


def snapshot_pngs() -> set[str]:
    output_dir = get_output_dir()
    return set(glob.glob(os.path.join(output_dir, "**/*.png"), recursive=True))


def wait_for_new_png(before: set[str]) -> str | None:
    start = time.time()
    while time.time() - start < TIMEOUT_SECONDS:
        after = snapshot_pngs()
        new = after - before
        if new:
            return max(new, key=os.path.getctime)
        time.sleep(1)
    return None


def load_workflow(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.pop("PIPELINE_NOTE", None)
    return data


def copy_to_dir(src: str, dst_dir: str) -> str:
    os.makedirs(dst_dir, exist_ok=True)
    dest = os.path.join(dst_dir, os.path.basename(src))
    shutil.copy2(src, dest)
    return dest
