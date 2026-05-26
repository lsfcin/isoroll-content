# Hades-style model comparison: all 5 checkpoints through detailer pipeline
import json, requests, uuid, time, glob, os, shutil

COMFY_URL = "http://127.0.0.1:8188"
COMFY_DIR = os.environ.get("COMFY_DIR", os.path.expanduser("~/ComfyUI"))
OUTPUT_DIR = os.path.join(COMFY_DIR, "output")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_PATH = os.path.join(BASE_DIR, "../cli/workflows/character_quality_detailer.json")
RESULTS_DIR = os.path.join(BASE_DIR, "hades-comparison")

PROMPT = (
    "trickster demigod, full body, slim agile build, dark leather armor, "
    "twin daggers sheathed at hips, confident stance, dark underworld caverns, "
    "teal and gold accents, dramatic rim lighting, painterly dark fantasy concept art, "
    "bold outlines, vibrant colors, highly detailed face and hands"
)
SEED = 77

CHECKPOINTS = [
    "dreamshaper_8.safetensors",
    "ghostmix_v20Bakedvae.safetensors",
    "cetusMix_Whalefall2.safetensors",
    "toonyou_beta6.safetensors",
    "lyriel_v16.safetensors",
    "revAnimated_v2Rebirth.safetensors",
]


def load_workflow(ckpt):
    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        w = json.load(f)
    for node in w.values():
        ct = node.get("class_type")
        if ct == "CheckpointLoaderSimple":
            node["inputs"]["ckpt_name"] = ckpt
        elif ct in ("KSampler", "FaceDetailer"):
            node["inputs"]["seed"] = SEED
        elif ct == "CLIPTextEncode":
            text = node["inputs"].get("text", "")
            if "REPLACE_PROMPT" in text:
                node["inputs"]["text"] = text.replace("REPLACE_PROMPT", PROMPT)
    return w


def submit(workflow):
    payload = {"prompt": workflow, "client_id": str(uuid.uuid4())}
    r = requests.post(f"{COMFY_URL}/prompt", json=payload)
    r.raise_for_status()
    return r.json()["prompt_id"]


def wait_for_output(prompt_id, before_set, timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        after = set(glob.glob(os.path.join(OUTPUT_DIR, "**/*.png"), recursive=True))
        new = after - before_set
        if new:
            return max(new, key=os.path.getctime)
        r = requests.get(f"{COMFY_URL}/history/{prompt_id}")
        if r.ok:
            hist = r.json()
            if prompt_id in hist:
                status = hist[prompt_id].get("status", {})
                if status.get("completed"):
                    after = set(glob.glob(os.path.join(OUTPUT_DIR, "**/*.png"), recursive=True))
                    new = after - before_set
                    if new:
                        return max(new, key=os.path.getctime)
                if status.get("status_str") == "error":
                    print(f"  [ERROR] {hist[prompt_id].get('outputs')}")
                    return None
        time.sleep(3)
    return None


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    manifest = []

    for ckpt in CHECKPOINTS:
        name = ckpt.replace(".safetensors", "").replace(".pt", "")
        print(f"\n[TEST] {name}")
        workflow = load_workflow(ckpt)
        before = set(glob.glob(os.path.join(OUTPUT_DIR, "**/*.png"), recursive=True))
        t0 = time.time()
        try:
            pid = submit(workflow)
        except Exception as e:
            print(f"  [FAIL] submit: {e}")
            continue
        print(f"  prompt_id={pid}")
        result = wait_for_output(pid, before)
        elapsed = round(time.time() - t0, 1)
        if result:
            dest = os.path.join(RESULTS_DIR, f"{name}.png")
            shutil.copy(result, dest)
            print(f"  [OK] {elapsed}s → {dest}")
            manifest.append({"model": ckpt, "seed": SEED, "time_s": elapsed, "file": dest})
        else:
            print(f"  [FAIL] timeout {elapsed}s")
            manifest.append({"model": ckpt, "seed": SEED, "time_s": elapsed, "file": None, "error": "timeout"})

    with open(os.path.join(RESULTS_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nDone. Results in {RESULTS_DIR}")


if __name__ == "__main__":
    main()
