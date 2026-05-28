# image_commands.py — Image processing commands: upscale, rembg, face restore.
import os
import sys
from pathlib import Path

from comfy_client import (
    copy_to_dir, load_workflow, send_prompt,
    snapshot_pngs, upload_image, wait_for_new_png,
)
from workflow_ops import inject_input_image, inject_output_size, inject_prompt

_HERE = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_DIR = os.path.join(_HERE, "workflows")

SIZE_PRESETS = {
    "character": (1024, 1536),
    "tile":      (1024, 1024),
}


def _run_rembg(image_path: str) -> str:
    from rembg import remove
    print("[INFO] Running rembg background removal ...")
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    result = remove(img_bytes)
    out_path = Path(image_path).with_suffix(".rembg.png")
    with open(out_path, "wb") as f:
        f.write(result)
    print(f"[OK]   BG removed: {out_path}")
    return str(out_path)


def detail_image(
    input_image: str, size: str, run_rembg: bool, output_path: str | None
) -> None:
    """Pure upscale — 4xUltrasharp → target size. No SD, no pose drift."""
    if not os.path.exists(input_image):
        print(f"[FAIL] Image not found: {input_image}")
        sys.exit(1)

    workflow_path = os.path.join(WORKFLOW_DIR, "upscale_pass.json")
    if not os.path.exists(workflow_path):
        print(f"[FAIL] Workflow not found: {workflow_path}")
        sys.exit(1)

    print(f"[INFO] input:    {input_image}")
    print(f"[INFO] rembg:    {'on' if run_rembg else 'off'}")

    print("[INFO] Uploading to ComfyUI ...")
    comfy_filename = upload_image(input_image)
    print(f"[INFO] Stored as: {comfy_filename}")

    w, h = SIZE_PRESETS.get(size, SIZE_PRESETS["character"])
    print(f"[INFO] size:     {w}x{h} ({size})")

    workflow = load_workflow(workflow_path)
    inject_input_image(workflow, comfy_filename)
    inject_output_size(workflow, w, h)

    before = snapshot_pngs()
    if not send_prompt(workflow):
        sys.exit(1)

    print("[INFO] Upscaling ...")
    latest = wait_for_new_png(before)
    if not latest:
        print("[FAIL] Timeout.")
        sys.exit(1)

    print(f"[OK]   Upscaled:  {latest}")

    if run_rembg:
        latest = _run_rembg(latest)

    if output_path:
        dest = copy_to_dir(latest, output_path)
        print(f"[OK]   Saved to:  {dest}")


def face_restore(
    input_image: str, prompt: str, run_rembg: bool, output_path: str | None
) -> None:
    """Visible-face characters only: UltimateSDUpscale (denoise 0.06) + CodeFormer."""
    if not os.path.exists(input_image):
        print(f"[FAIL] Image not found: {input_image}")
        sys.exit(1)

    workflow_path = os.path.join(WORKFLOW_DIR, "face_restore_pass.json")
    if not os.path.exists(workflow_path):
        print(f"[FAIL] Workflow not found: {workflow_path}")
        sys.exit(1)

    print(f"[INFO] input:    {input_image}")
    print(f"[INFO] prompt:   {prompt}")
    print(f"[INFO] rembg:    {'on' if run_rembg else 'off'}")

    print("[INFO] Uploading to ComfyUI ...")
    comfy_filename = upload_image(input_image)
    print(f"[INFO] Stored as: {comfy_filename}")

    workflow = load_workflow(workflow_path)
    inject_input_image(workflow, comfy_filename)
    inject_prompt(workflow, prompt)

    before = snapshot_pngs()
    if not send_prompt(workflow):
        sys.exit(1)

    print("[INFO] Waiting for face restore ...")
    latest = wait_for_new_png(before)
    if not latest:
        print("[FAIL] Timeout.")
        sys.exit(1)

    print(f"[OK]   Restored:  {latest}")

    if run_rembg:
        latest = _run_rembg(latest)

    if output_path:
        dest = copy_to_dir(latest, output_path)
        print(f"[OK]   Saved to:  {dest}")
