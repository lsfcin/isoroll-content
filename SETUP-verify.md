# Verification
> Probes that say whether the install works, node by node.
> feature: install probes

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
