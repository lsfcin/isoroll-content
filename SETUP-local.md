# Local environment
> Python deps, the low-VRAM SDXL settings for a 3050, and the Blender lane.
> feature: python deps, blender fallback

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
