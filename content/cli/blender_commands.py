# blender_commands.py — Blender render stylization commands: Path A and Path A+B hybrid.
import os
import sys

from comfy_client import (
    copy_to_dir, load_workflow, send_prompt,
    snapshot_pngs, upload_image, wait_for_new_png,
)
from workflow_ops import (
    apply_random_seeds, inject_concept_image, inject_input_image,
    inject_prompt, set_base_denoise, set_ipadapter_weight,
)

_HERE = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_DIR = os.path.join(_HERE, "workflows")


def blender_stylize(
    input_image: str, prompt: str, denoise: float, output_path: str | None
) -> None:
    """Path A — ControlNet Tile stylization of a Blender render."""
    if not os.path.exists(input_image):
        print(f"[FAIL] Image not found: {input_image}")
        sys.exit(1)

    workflow_path = os.path.join(WORKFLOW_DIR, "blender_controlnet_tile.json")
    if not os.path.exists(workflow_path):
        print(f"[FAIL] Workflow not found: {workflow_path}")
        sys.exit(1)

    print(f"[INFO] input:    {input_image}")
    print(f"[INFO] prompt:   {prompt}")
    print(f"[INFO] denoise:  {denoise}")

    print("[INFO] Uploading to ComfyUI ...")
    comfy_filename = upload_image(input_image)
    print(f"[INFO] Stored as: {comfy_filename}")

    workflow = load_workflow(workflow_path)
    inject_input_image(workflow, comfy_filename)
    inject_prompt(workflow, prompt)
    set_base_denoise(workflow, denoise)
    apply_random_seeds(workflow)

    before = snapshot_pngs()
    if not send_prompt(workflow):
        sys.exit(1)

    print("[INFO] Waiting for generation ...")
    latest = wait_for_new_png(before)
    if not latest:
        print("[FAIL] Timeout.")
        sys.exit(1)

    print(f"[OK]   Generated: {latest}")
    if output_path:
        dest = copy_to_dir(latest, output_path)
        print(f"[OK]   Saved to:  {dest}")


def blender_ipadapter(
    input_image: str, concept_image: str, prompt: str,
    denoise: float, weight: float, output_path: str | None
) -> None:
    """Path A+B hybrid — IP-Adapter identity + ControlNet Tile structure from Blender render."""
    for p in (input_image, concept_image):
        if not os.path.exists(p):
            print(f"[FAIL] Image not found: {p}")
            sys.exit(1)

    workflow_path = os.path.join(WORKFLOW_DIR, "blender_ipadapter_tile.json")
    if not os.path.exists(workflow_path):
        print(f"[FAIL] Workflow not found: {workflow_path}")
        sys.exit(1)

    print(f"[INFO] render:   {input_image}")
    print(f"[INFO] concept:  {concept_image}")
    print(f"[INFO] prompt:   {prompt}")
    print(f"[INFO] denoise:  {denoise}  weight: {weight}")

    print("[INFO] Uploading to ComfyUI ...")
    render_fname = upload_image(input_image)
    concept_fname = upload_image(concept_image)
    print(f"[INFO] Render as:  {render_fname}")
    print(f"[INFO] Concept as: {concept_fname}")

    workflow = load_workflow(workflow_path)
    inject_input_image(workflow, render_fname)
    inject_concept_image(workflow, concept_fname)
    inject_prompt(workflow, prompt)
    set_base_denoise(workflow, denoise)
    set_ipadapter_weight(workflow, weight)
    apply_random_seeds(workflow)

    before = snapshot_pngs()
    if not send_prompt(workflow):
        sys.exit(1)

    print("[INFO] Waiting for generation ...")
    latest = wait_for_new_png(before)
    if not latest:
        print("[FAIL] Timeout.")
        sys.exit(1)

    print(f"[OK]   Generated: {latest}")
    if output_path:
        dest = copy_to_dir(latest, output_path)
        print(f"[OK]   Saved to:  {dest}")
