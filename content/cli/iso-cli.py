"""iso-cli — isoroll content pipeline CLI. Run with -h for usage."""

import os
import random
import sys

from comfy_client import (
    copy_to_dir, load_workflow, send_prompt,
    snapshot_pngs, upload_image, wait_for_new_png,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.dirname(BASE_DIR)
PROFILE_DIR = os.path.join(CONTENT_DIR, "profiles")
WORKFLOW_DIR = os.path.join(BASE_DIR, "workflows")

HELP = """
iso-cli — isoroll content pipeline

Commands:
  gen-character <prompt>      txt2img character generation
    --profile  fast|balanced|quality  (default: balanced)
    --out      <dir>                  copy result here

  style-concept <image_path>  img2img style pass on concept art
    --prompt   <text>                 style description (required)
    --denoise  <0.0-1.0>             style strength    (default: 0.55)
    --out      <dir>                  copy result here

Examples:
  python iso-cli.py gen-character "dark fantasy rogue" --profile quality
  python iso-cli.py style-concept ../outputs/tiles/dungeon/concept/dungeon_concept_clean.png \\
      --prompt "isometric dungeon floor tile, dark stone, dark fantasy" --denoise 0.50 \\
      --out ../outputs/tiles/dungeon/styled
"""


# ── Workflow mutations ─────────────────────────────────────────────────────────

def apply_random_seeds(workflow: dict) -> None:
    seed = random.randint(0, 2**32 - 1)
    for node in workflow.values():
        if node.get("class_type") == "KSampler":
            node["inputs"]["seed"] = seed


def inject_prompt(workflow: dict, prompt_text: str) -> None:
    for node in workflow.values():
        if node.get("class_type") == "CLIPTextEncode":
            text = node["inputs"].get("text", "")
            if "REPLACE_PROMPT" in text:
                node["inputs"]["text"] = text.replace("REPLACE_PROMPT", prompt_text)


def inject_input_image(workflow: dict, comfy_filename: str) -> None:
    for node in workflow.values():
        if node.get("class_type") == "LoadImage":
            if node["inputs"].get("image") == "REPLACE_INPUT_IMAGE":
                node["inputs"]["image"] = comfy_filename


def set_base_denoise(workflow: dict, denoise: float) -> None:
    for node in workflow.values():
        if node.get("class_type") == "KSampler":
            node["inputs"]["denoise"] = denoise
            return  # first sampler only; refine pass keeps its own value


# ── Commands ───────────────────────────────────────────────────────────────────

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


# ── Entry point ────────────────────────────────────────────────────────────────

def get_arg(args: list[str], flag: str, default: str | None = None) -> str | None:
    if flag in args:
        idx = args.index(flag)
        if idx + 1 < len(args):
            return args[idx + 1]
    return default


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(HELP)
        return

    command = args[0]

    if command == "gen-character":
        if len(args) < 2:
            print("[FAIL] gen-character requires a prompt.")
            sys.exit(1)
        gen_character(
            prompt=args[1],
            profile_name=get_arg(args, "--profile", "balanced"),
            output_path=get_arg(args, "--out"),
        )

    elif command == "style-concept":
        if len(args) < 2:
            print("[FAIL] style-concept requires an image path.")
            sys.exit(1)
        prompt = get_arg(args, "--prompt")
        if not prompt:
            print("[FAIL] style-concept requires --prompt.")
            sys.exit(1)
        style_concept(
            input_image=args[1],
            prompt=prompt,
            denoise=float(get_arg(args, "--denoise", "0.55")),
            output_path=get_arg(args, "--out"),
        )

    else:
        print(f"[FAIL] Unknown command: {command}")
        print(HELP)
        sys.exit(1)


if __name__ == "__main__":
    main()
