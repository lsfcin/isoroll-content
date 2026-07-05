# workflow_ops.py — Workflow mutation helpers for the isoroll ComfyUI pipeline.
import random


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


def inject_concept_image(workflow: dict, comfy_filename: str) -> None:
    for node in workflow.values():
        if node.get("class_type") == "LoadImage":
            if node["inputs"].get("image") == "REPLACE_CONCEPT_IMAGE":
                node["inputs"]["image"] = comfy_filename


def set_base_denoise(workflow: dict, denoise: float) -> None:
    for node in workflow.values():
        if node.get("class_type") == "KSampler":
            node["inputs"]["denoise"] = denoise
            return  # first sampler only; refine pass keeps its own value


def set_ipadapter_weight(workflow: dict, weight: float) -> None:
    for node in workflow.values():
        if node.get("class_type") == "IPAdapterAdvanced":
            node["inputs"]["weight"] = weight
            return


def inject_output_size(workflow: dict, width: int, height: int) -> None:
    for node in workflow.values():
        if node.get("class_type") == "ImageScale":
            if node["inputs"].get("width") == "REPLACE_WIDTH":
                node["inputs"]["width"] = width
                node["inputs"]["height"] = height
                return
