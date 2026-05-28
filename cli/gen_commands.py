# gen_commands.py — Generation commands: txt2img, style-concept, IP-Adapter ref.
import os
import sys

from comfy_client import (
    copy_to_dir, load_workflow, send_prompt,
    snapshot_pngs, upload_image, wait_for_new_png,
)
from workflow_ops import (
    apply_random_seeds, inject_prompt, inject_input_image,
    set_base_denoise, set_ipadapter_weight,
)

_HERE = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_DIR = os.path.join(_HERE, "workflows")


def gen_character(prompt: str, profile_name: str, output_path: str | None) -> None:
    workflow_path = os.path.join(WORKFLOW_DIR, f"character_{profile_name}.json")
    if not os.path.exists(workflow_path):
        print(f"[FAIL] Workflow not found: {workflow_path}")
        sys.exit(1)

    print(f"[INFO] profile:  {profile_name}")
    print(f"[INFO] prompt:   {prompt}")

    workflow = load_workflow(workflow_path)
    inject_prompt(workflow, prompt)
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


def style_concept(
    input_image: str, prompt: str, denoise: float, output_path: str | None
) -> None:
    if not os.path.exists(input_image):
        print(f"[FAIL] Image not found: {input_image}")
        sys.exit(1)

    workflow_path = os.path.join(WORKFLOW_DIR, "concept_img2img.json")
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


def ipadapter_ref(
    input_image: str, prompt: str, weight: float, output_path: str | None
) -> None:
    if not os.path.exists(input_image):
        print(f"[FAIL] Image not found: {input_image}")
        sys.exit(1)

    workflow_path = os.path.join(WORKFLOW_DIR, "ipadapter_txt2img.json")
    if not os.path.exists(workflow_path):
        print(f"[FAIL] Workflow not found: {workflow_path}")
        sys.exit(1)

    print(f"[INFO] input:    {input_image}")
    print(f"[INFO] prompt:   {prompt}")
    print(f"[INFO] weight:   {weight}")

    print("[INFO] Uploading to ComfyUI ...")
    comfy_filename = upload_image(input_image)
    print(f"[INFO] Stored as: {comfy_filename}")

    workflow = load_workflow(workflow_path)
    inject_input_image(workflow, comfy_filename)
    inject_prompt(workflow, prompt)
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
