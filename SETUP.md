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

> **Troubleshooting:** if `$COMFY_DIR/models/{checkpoints,embeddings,loras,upscale_models}` are symlinks that don't resolve, the link target — `/mnt/workspace/models/diffusion/` (lowercase `models`, canonical — never recreate a capital-`Models/`) — is missing; `mkdir -p` the four subdirs there. The "Source" column above often names a provider without a literal URL; resolve the actual download link via web search when needed.

### Checkpoints

| Model | Destination | Source | Priority |
|-------|-------------|--------|----------|
| `lyriel_v16.safetensors` | `models/checkpoints/` | Civitai | **Primary** — dark fantasy illustrated style |
| `toonyou_beta6.safetensors` | `models/checkpoints/` | Civitai | Secondary — cartoon/illustrated, cleaner sprites |
| `cetusMix_Whalefall2.safetensors` | `models/checkpoints/` | Civitai | Secondary — anime/semi-realistic |
| `dreamshaperPixelart_v10.safetensors` | `models/checkpoints/` | Civitai | Legacy — kept in workflows but not downloaded |
| `4xUltrasharp_4xUltrasharpV10.pt` | `models/upscale_models/` | Civitai / OpenModelDB | Upscale (optional) |

### ControlNet Models (SD1.5)

All go in `models/controlnet/` (lowercase). Download from HuggingFace `lllyasviel/ControlNet-v1-1`.

| Model | Use |
|-------|-----|
| `control_v11p_sd15_openpose.pth` | Pose skeleton control (Path B) |
| `control_v11f1e_sd15_tile.pth` | Structure-preserving style pass (Path A) |
| `control_v11p_sd15_depth.pth` | Depth map control (Path A, Blender depth pass) |
| `control_v11p_sd15_lineart.pth` | Lineart control (Path A, Blender Freestyle output) |

### IP-Adapter Models

Go in `models/ipadapter/`. Download from HuggingFace `h94/IP-Adapter`.

| Model | Use |
|-------|-----|
| `ip-adapter-plus_sd15.bin` | **Primary** — stronger identity lock than base |
| `ip-adapter_sd15.bin` | Fallback — lighter, faster |
| `ip-adapter-plus_sdxl_vit-h.bin` | SDXL variant (if SDXL tests pass) |

### CLIP Vision Models (required by IP-Adapter)

Go in `models/clip_vision/`. IP-Adapter does NOT bundle the image encoder — must download separately.

| File | Source | Use |
|------|--------|-----|
| `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` | [h94/IP-Adapter image_encoder](https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors) — **rename after download** | SD1.5 ip-adapter-plus (~2GB) |
| `CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors` | [h94/IP-Adapter sdxl image_encoder](https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/image_encoder/model.safetensors) — **rename after download** | SDXL ip-adapter variants |

```bash
# SD1.5 CLIP Vision (for ip-adapter-plus_sd15):
wget "https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors" \
     -O "$COMFY_DIR/models/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"
```

### YOLO / Detailer Models (needed only for M3)

| Model | Destination |
|-------|-------------|
| `yolov8m-seg.pt` | `models/ultralytics/segm/` |
| `face_yolov8m.pt` | `models/ultralytics/bbox/` |
| `hand_yolov8s.pt` | `models/ultralytics/bbox/` |

### Face Restore Models (visible-face characters only)

Go in `models/facerestore_models/`. Used by `face-restore` CLI command (CodeFormer). **Do not use on masked/hooded characters** — CodeFormer expects human face anatomy.

| Model | Source |
|-------|--------|
| `codeformer.pth` | [sczhou/CodeFormer releases](https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth) |
| `GFPGANv1.4.pth` | [TencentARC/GFPGAN releases](https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth) (optional) |

Face detection models (`models/facedetection/`) download automatically on first `face-restore` run.

---

## 4. Required Extensions

Install via ComfyUI Manager (`Install Custom Nodes`), or clone into `$COMFY_DIR/custom_nodes/`.

| Extension | Manager search name | Required for |
|-----------|--------------------|-|
| Impact Pack | `ComfyUI Impact Pack` | FaceDetailer, detailer nodes |
| Impact Subpack | `ComfyUI Impact Subpack` | `UltralyticsDetectorProvider` (YOLO) |
| IPAdapter Plus | `ComfyUI_IPAdapter_plus` | IP-Adapter character identity |
| ControlNet Aux | `comfyui-controlnet-aux` | DWPose detector, depth/lineart preprocessors |
| AnimateDiff Evolved | `ComfyUI-AnimateDiff-Evolved` | Effects animation (L4) |
| rembg node | `comfyui-rembg` | Background removal in-workflow |
| RIFE VFI | `ComfyUI_RIFE_VFI` | Frame interpolation (Path B temporal consistency) |
| Video Helper Suite | `ComfyUI-Video-Helper-Suite` | Video frame loading/saving |
| UltimateSDUpscale | clone `https://github.com/ssitu/ComfyUI_UltimateSDUpscale --recursive` | Tile-based upscale without pose drift (`face-restore` command) |
| facerestore_cf | clone `https://github.com/mav-rik/facerestore_cf` | CodeFormer face restoration (`face-restore` command) |

**Important:** Impact Pack and Impact Subpack are separate installs. Subpack is required for `character_quality_yolo.json`. Without it, `UltralyticsDetectorProvider` will not appear in ComfyUI.

---

## 5. Python Dependencies

```bash
# ComfyUI CLI and pipeline tools
pip install requests

# Standalone background removal (GPU-accelerated)
pip install "rembg[gpu]"

# Spritesheet packing
pip install Pillow

# For Blender batch script (if running outside Blender's embedded Python)
# Blender uses its own Python — see §8 for Blender setup
```

On Windows with ComfyUI's embedded Python:
```powershell
python_embeded\python.exe -m pip install requests "rembg[gpu]" Pillow
```

---

## 6. SDXL Low-VRAM Setup (RTX 3050 6GB)

Add these flags to ComfyUI launch command when running SDXL models:

```bash
python main.py --lowvram --bf16-unet
```

Or on Windows portable:
```powershell
.\run_nvidia_gpu.bat --lowvram --bf16-unet
```

`--lowvram`: offloads model parts to CPU RAM, reduces peak VRAM at cost of speed.
`--bf16-unet`: uses bfloat16 instead of float32 for UNet, cuts VRAM ~30%.

For SD1.5 workloads, these flags are optional but can help when running IP-Adapter + 2× ControlNet simultaneously.

---

## 7. Blender Setup

Install Blender (free): https://www.blender.org/download/

```bash
blender --version   # verify available from command line
```

Blender batch rendering (headless):
```bash
blender --background scene.blend --python src/pipeline/blender_iso_rig.py
```

No additional pip installs needed inside Blender — the rig script uses only Blender's built-in Python API (`bpy`).

---

## 8. Verify Setup

```bash
# ComfyUI running
curl http://127.0.0.1:8188/object_info > /dev/null && echo OK

# COMFY_DIR resolves
ls "$COMFY_DIR/models/checkpoints/"

# Verify lyriel_v16 present
ls "$COMFY_DIR/models/checkpoints/lyriel_v16.safetensors"

# Verify ControlNet models
ls "$COMFY_DIR/models/ControlNet/"

# Verify IP-Adapter
ls "$COMFY_DIR/models/ipadapter/"

# Test generation (fast profile — ~30 seconds)
cd /path/to/isoroll-content/src/cli
python iso-cli.py gen-character "test warrior" --profile fast

# Verify rembg
python -c "import rembg; print('rembg OK')"

# Verify Blender
blender --version
```

---

## 9. Verify YOLO nodes (before using YOLO workflows)

```bash
curl -s http://127.0.0.1:8188/object_info | python3 -c \
  "import sys, json; d = json.load(sys.stdin); print('UltralyticsDetectorProvider:', 'UltralyticsDetectorProvider' in d)"
# Expected: UltralyticsDetectorProvider: True
```

If `False`: Impact Subpack is missing or ComfyUI needs a restart after install.

---

## 10. Verify IP-Adapter and ControlNet nodes

```bash
curl -s http://127.0.0.1:8188/object_info | python3 -c \
  "import sys, json
d = json.load(sys.stdin)
for node in ['IPAdapterPlus', 'ControlNetLoader', 'DWPreprocessor', 'OpenposePreprocessor', 'RIFEInterpolation']:
    print(f'{node}: {node in d}')
"
```

All should print `True` after installing the required custom nodes.
