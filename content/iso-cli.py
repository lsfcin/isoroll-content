import sys
import json
import requests
import uuid
import glob
import os
import shutil

COMFY_URL = "http://127.0.0.1:8188/prompt"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def get_comfy_dir():
    comfy_dir = os.environ.get("COMFY_DIR")

    if not comfy_dir:
        raise RuntimeError(
            "COMFY_DIR não está definido. "
            "Use: setx COMFY_DIR \"C:\\...\\ComfyUI\""
        )

    return comfy_dir

def get_output_dir():
    return os.path.join(get_comfy_dir(), "output")

def copy_to_destination(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(src, dst)

def get_latest_image(output_dir=None):
    output_dir = output_dir or get_output_dir()

    files = glob.glob(os.path.join(output_dir, "**/*.png"), recursive=True)
    if not files:
        return None

    return max(files, key=os.path.getctime)

def apply_output_path(workflow, output_path):
    for node in workflow.values():
        if node.get("class_type") == "SaveImage":
            node["inputs"]["filename_prefix"] = output_path.replace("\\", "/")

def load_profile(profile_name):
    path = os.path.join(BASE_DIR, "render_profiles", f"{profile_name}.json")

    with open(path, "r") as f:
        return json.load(f)

def load_workflow(prompt_text, profile_name):
    workflow_path = os.path.join(BASE_DIR, "workflows", f"character_{profile_name}.json")

    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    import random
    seed = random.randint(0, 2**32 - 1)

    for node in workflow.values():
        if node.get("class_type") == "KSampler":
            node["inputs"]["seed"] = seed

    # injeta prompt positivo
    for node in workflow.values():
        if node.get("class_type") == "CLIPTextEncode":
            text = node["inputs"].get("text", "")
            if "low quality" not in text.lower():
                node["inputs"]["text"] = prompt_text

    return workflow


def send_prompt(workflow):
    payload = {
        "prompt": workflow,
        "client_id": str(uuid.uuid4())
    }

    try:
        res = requests.post(COMFY_URL, json=payload)

        print(f"[DEBUG] Status code: {res.status_code}")
        print(f"[DEBUG] Response text: {res.text}")

        res.raise_for_status()

        return res.json()

    except Exception as e:
        print("[ERRO] Falha ao enviar para ComfyUI")
        print(e)
        return None


def gen_character(prompt, profile_name, output_path):
    profile = load_profile(profile_name)

    print(f"[INFO] Profile: {profile_name}")
    print(f"[INFO] Prompt: {prompt}")
    print(f"[INFO] Output: {output_path}")

    workflow = load_workflow(prompt, profile_name)

    output_dir = get_output_dir()

    # snapshot antes
    before = set(glob.glob(os.path.join(output_dir, "**/*.png"), recursive=True))

    import random

    for node in workflow.values():
        if node.get("class_type") == "KSampler":
            node["inputs"]["seed"] = random.randint(0, 999999999)
            
    result = send_prompt(workflow)

    if not result:
        print("[FAIL] geração falhou")
        return

    print("[INFO] aguardando geração...")

    import time

    latest = None

    timeout_seconds = 600  # 10 minutos
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:

        after = set(glob.glob(os.path.join(output_dir, "**/*.png"), recursive=True))
        new_files = after - before

        if new_files:
            latest = max(new_files, key=os.path.getctime)
            break

        time.sleep(1)

    if not latest:
        print("[FAIL] timeout aguardando imagem")
        return

    print(f"[INFO] imagem gerada: {latest}")

    if output_path:
        filename = os.path.basename(latest)
        dest = os.path.abspath(os.path.join(output_path, filename))

        copy_to_destination(latest, dest)

        print(f"[OK] copiado para: {dest}")

def main():
    if len(sys.argv) < 3:
        print("Uso: iso-cli gen-character 'prompt' --out path")
        return

    command = sys.argv[1]
    prompt = sys.argv[2]

    profile_name = "balanced"

    if "--profile" in sys.argv:
        idx = sys.argv.index("--profile")
        profile_name = sys.argv[idx + 1]

    output_path = None

    if "--out" in sys.argv:
        idx = sys.argv.index("--out")
        output_path = sys.argv[idx + 1]

    if command == "gen-character":
        gen_character(prompt, profile_name=profile_name, output_path=output_path)


if __name__ == "__main__":
    main()
