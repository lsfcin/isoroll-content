# isorolling Setup
> Environment setup for the isorolling content pipeline and future Foundry module.

## 1. Install ComfyUI

Install in the default OS location. `COMFY_DIR` env var decouples the install path from the code — install anywhere, point the var at it.

**Linux:**
```bash
git clone https://github.com/comfyanonymous/ComfyUI ~/ComfyUI
cd ~/ComfyUI
pip install -r requirements.txt
```

**Windows:**
Download the portable package from the [ComfyUI releases page](https://github.com/comfyanonymous/ComfyUI/releases) and extract it.

---

## 2. Set COMFY_DIR

**Linux — add to `~/.bashrc`:**
```bash
echo 'export COMFY_DIR="$HOME/ComfyUI"' >> ~/.bashrc && source ~/.bashrc
```

**Windows (PowerShell — permanent, per user):**
```powershell
setx COMFY_DIR "C:\path\to\ComfyUI_windows_portable\ComfyUI"
```

Restart terminal after `setx`. Verify:
```bash
echo $COMFY_DIR       # Linux
$env:COMFY_DIR        # Windows
```

---

## 3. Required Models

Place in the correct subfolder under `$COMFY_DIR/models/`.

| Model | Destination | Source |
|-------|-------------|--------|
| `dreamshaperPixelart_v10.safetensors` | `models/checkpoints/` | Civitai |
| `4xUltrasharp_4xUltrasharpV10.pt` | `models/upscale_models/` | Civitai / OpenModelDB |
| `yolov8m-seg.pt` | `models/ultralytics/segm/` | Ultralytics / Civitai (needed only for YOLO workflows) |

---

## 4. Required Extensions

Install via ComfyUI Manager, or clone manually into `$COMFY_DIR/custom_nodes/`.

| Extension | Required for |
|-----------|-------------|
| Impact Pack | FaceDetailer and detailer nodes |
| Impact Subpack | `UltralyticsDetectorProvider` — YOLO detection |

**Important:** Impact Pack and Impact Subpack are separate installs. Subpack is required for `character_quality_yolo.json`. Without it, `UltralyticsDetectorProvider` will not appear in ComfyUI.

---

## 5. Python Dependencies

```bash
pip install requests
```

On Windows with ComfyUI's embedded Python, use `python_embeded\python.exe -m pip install requests` from the portable folder.

---

## 6. Verify Setup

```bash
# ComfyUI running
curl http://127.0.0.1:8188/object_info > /dev/null && echo OK

# COMFY_DIR resolves
ls "$COMFY_DIR/models/checkpoints/"

# Test generation (fast profile — ~30 seconds)
cd /path/to/isoroll/content/cli
python iso-cli.py gen-character "test warrior" --profile fast
```

---

## 7. Verify YOLO nodes (before using YOLO workflows)

```bash
curl -s http://127.0.0.1:8188/object_info | python3 -c \
  "import sys, json; d = json.load(sys.stdin); print('UltralyticsDetectorProvider:', 'UltralyticsDetectorProvider' in d)"
# Expected: UltralyticsDetectorProvider: True
```

If `False`: Impact Subpack is missing or ComfyUI needs a restart after install.
