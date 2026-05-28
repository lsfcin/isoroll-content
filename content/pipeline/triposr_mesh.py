"""[OBSOLETE-MESH] triposr_mesh.py — Generate a 3D mesh from a single concept image using TripoSR.

Requires TripoSR cloned to /home/lucas/TripoSR (torchmcubes patched to use scikit-image).
Model (~1.2 GB) downloads from HuggingFace on first run.

Usage:
    python content/pipeline/triposr_mesh.py \\
        --image content/chars/rogue/concept/rogue_concept_clean.png \\
        --character rogue \\
        [--resolution 128] \\
        [--bake-texture] \\
        [--device cuda:0]

Output:
    content/chars/{character}/mesh/mesh.obj
    content/chars/{character}/mesh/texture.png  (if --bake-texture)

Next step (manual — Mixamo):
    1. Go to https://www.mixamo.com
    2. Upload mesh/mesh.obj
    3. Mixamo auto-rigs the humanoid mesh
    4. Download each animation as FBX (With Skin):
         idle, walk, run, attack, hurt, death
    5. Save FBXs to content/chars/{character}/rig/{character}_{state}.fbx
    6. Run s3_batch.sh or blender_iso_rig.py with --fbx and --no-materials
"""

import argparse
import sys
import os
from pathlib import Path

TRIPOSR_DIR = Path("/home/lucas/TripoSR")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--image",       required=True, help="Concept art image path")
    p.add_argument("--character",   required=True, help="Character name (e.g. rogue)")
    p.add_argument("--output-dir",  default=None,  help="Override output dir")
    p.add_argument("--resolution",  type=int, default=128,
                   help="Marching cubes resolution. 128=fast, 256=detailed. Default: 128")
    p.add_argument("--bake-texture", action="store_true",
                   help="Bake UV texture atlas (larger output, better for Blender materials)")
    p.add_argument("--device",      default="cuda:0")
    p.add_argument("--chunk-size",  type=int, default=8192,
                   help="Lower = less VRAM. Default: 8192")
    p.add_argument("--mesh-rotate-x", type=float, default=0.0,
                   help="Pre-rotate mesh around X axis before export (degrees). Default 0.")
    p.add_argument("--mesh-rotate-y", type=float, default=0.0,
                   help="Pre-rotate mesh around Y axis before export (degrees). Default 0.")
    p.add_argument("--mesh-rotate-z", type=float, default=90.0,
                   help="Pre-rotate mesh around Z axis before export (degrees). Default +90 "
                        "(empirically determined: TripoSR raw output → Mixamo correct orientation).")
    return p.parse_args()


def main():
    args = parse_args()

    if not TRIPOSR_DIR.exists():
        print(f"Error: TripoSR not found at {TRIPOSR_DIR}")
        print("  git clone https://github.com/VAST-AI-Research/TripoSR /home/lucas/TripoSR")
        sys.exit(1)

    sys.path.insert(0, str(TRIPOSR_DIR))

    import numpy as np
    import torch
    from PIL import Image
    import rembg

    from tsr.system import TSR
    from tsr.utils import remove_background, resize_foreground

    # bake_texture needs moderngl (requires OpenGL display) — unavailable headless.
    # We skip UV baking; vertex colors are sufficient for mesh geometry.
    # Blender will project T-pose concept art as UV texture instead (--front-image / --back-image).
    if args.bake_texture:
        print("  Warning: --bake-texture requires moderngl (OpenGL display). Ignoring.")
        args.bake_texture = False

    img_path = Path(args.image)
    if not img_path.exists():
        print(f"Error: image not found: {img_path}")
        sys.exit(1)

    out_dir = Path(args.output_dir) if args.output_dir else \
              Path(f"content/chars/{args.character}/mesh")
    out_dir.mkdir(parents=True, exist_ok=True)

    device = args.device
    if not torch.cuda.is_available():
        device = "cpu"
        print("  CUDA not available — using CPU (slow)")

    print(f"triposr_mesh")
    print(f"  image     : {img_path}")
    print(f"  output    : {out_dir}")
    print(f"  resolution: {args.resolution}")
    print(f"  device    : {device}")
    print()

    print("Loading model (downloads ~1.2 GB on first run)...")
    model = TSR.from_pretrained(
        "stabilityai/TripoSR",
        config_name="config.yaml",
        weight_name="model.ckpt",
    )
    model.renderer.set_chunk_size(args.chunk_size)
    model.to(device)
    print("  Model loaded.")

    print("Preprocessing image...")
    rembg_session = rembg.new_session()
    image = remove_background(Image.open(img_path), rembg_session)
    image = resize_foreground(image, 0.85)
    img_arr = np.array(image).astype(np.float32) / 255.0
    # Composite on gray background (TripoSR expects gray, not white)
    img_arr = img_arr[:, :, :3] * img_arr[:, :, 3:4] + (1 - img_arr[:, :, 3:4]) * 0.5
    image = Image.fromarray((img_arr * 255.0).astype(np.uint8))
    preprocessed_path = out_dir / "input_preprocessed.png"
    image.save(preprocessed_path)
    print(f"  Preprocessed → {preprocessed_path}")

    print("Running TripoSR model...")
    with torch.no_grad():
        scene_codes = model([image], device=device)
    print("  Model inference done.")

    print(f"Extracting mesh (resolution={args.resolution})...")
    meshes = model.extract_mesh(
        scene_codes,
        has_vertex_color=not args.bake_texture,
        resolution=args.resolution,
    )
    print("  Mesh extracted.")

    mesh_format = "obj"
    mesh_path = out_dir / f"mesh.{mesh_format}"

    mesh = meshes[0]

    import numpy as np
    import trimesh as _trimesh
    for deg, axis, label in [
        (args.mesh_rotate_x, [1, 0, 0], "X"),
        (args.mesh_rotate_y, [0, 1, 0], "Y"),
        (args.mesh_rotate_z, [0, 0, 1], "Z"),
    ]:
        if deg != 0.0:
            R = _trimesh.transformations.rotation_matrix(np.radians(deg), axis)
            mesh.apply_transform(R)
            print(f"  {label}-rotation {deg:+.0f}° applied")

    mesh.export(str(mesh_path))

    print(f"  Mesh    → {mesh_path}")
    print()
    print("=" * 60)
    print("NEXT STEP — Mixamo auto-rigging (manual, ~2 min):")
    print("=" * 60)
    print(f"  1. Go to https://www.mixamo.com")
    print(f"  2. Click 'Upload Character'")
    print(f"  3. Upload: {mesh_path.resolve()}")
    print(f"  4. Mixamo auto-rigs the humanoid mesh")
    print(f"  5. Download animations as FBX (With Skin):")
    print(f"       - Idle (breathing)")
    print(f"       - Walking")
    print(f"       - Running")
    print(f"       - Attack (sword slash or similar)")
    print(f"       - Hit reaction")
    print(f"       - Death")
    print(f"  6. Save each FBX to:")
    print(f"       content/chars/{args.character}/rig/{args.character}_idle.fbx")
    print(f"       content/chars/{args.character}/rig/{args.character}_walk.fbx")
    print(f"       ... etc")
    print()
    print("  7. Render all directions:")
    print(f"       bash content/pipeline/s3_batch.sh {args.character}")
    print("=" * 60)


if __name__ == "__main__":
    main()
