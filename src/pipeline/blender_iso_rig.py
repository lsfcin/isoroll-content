# [OBSOLETE-MESH] blender_iso_rig.py — Isometric camera rig for isoroll asset rendering.
"""[OBSOLETE-MESH] blender_iso_rig.py — Isometric camera rig for isoroll asset rendering.
Entry point only — see blender_scene_setup.py, blender_materials.py, blender_fbx_import.py,
blender_camera.py, blender_render.py for the implementation this dispatches to.

Run headless from the isoroll-content repo root:
    blender --background --python src/pipeline/blender_iso_rig.py -- \
        --fbx assets/chars/rogue/rig/standing_idle.fbx \
        --state neutral-idle \
        --output-dir assets/chars/rogue

All paths are relative to CWD at launch time (the repo root).

Output per frame per direction (flat, direction as filename suffix):
    {output_dir}/_renders/{state}/frame_{n:04d}_{direction}.png        RGBA
    {output_dir}/_renders/{state}/frame_{n:04d}_depth_{direction}.png  depth (grayscale)

Elevation presets (pass --elevation):
    26.57   2:1 dimetric — Hades / Diablo standard (default)
    35.264  true isometric — tile edges at 30° screen-space angle

Framing:  --frame-center-z overrides the auto-computed camera target Z.
          If character appears in upper portion of frame, increase this value.
          If in lower portion, decrease it.
"""

import argparse
import sys

from blender_render import render_all


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser(description="Render isometric asset views from Blender scene.")
    p.add_argument("--state",        default="idle",  help="Animation state label (e.g. idle, walk)")
    p.add_argument("--start-frame",  type=int, default=1)
    p.add_argument("--end-frame",    type=int, default=20)
    p.add_argument("--output-dir",   required=True,   help="Asset output root (e.g. assets/chars/rogue)")
    p.add_argument("--elevation",    type=float, default=26.57, help="Camera elevation in degrees")
    p.add_argument("--ortho-scale",  type=float, default=0.015,
                   help="Orthographic scale. Default 0.015 (calibrated for TripoSR→Mixamo FBX).")
    p.add_argument("--shift-y",      type=float, default=0.3,
                   help="Camera vertical pan (shift_y). Default 0.3 (centers character in frame).")
    p.add_argument("--no-depth",       action="store_true", help="Skip depth pass (faster)")
    p.add_argument("--no-top",         action="store_true", help="Skip overhead TOP view")
    p.add_argument("--no-materials",   action="store_true", help="Skip auto material assignment (keep original FBX materials)")
    p.add_argument("--resolution-x",   type=int, default=256)
    p.add_argument("--resolution-y",   type=int, default=384, help="Use 256 for tiles, 384 for characters")
    p.add_argument("--fbx",            default=None, help="Import this FBX before rendering (Mixamo workflow — no .blend needed)")
    p.add_argument("--frame-center-z", type=float, default=None,
                   help="Override camera target Z (Blender units). Auto-computed if omitted. "
                        "Tune if character appears off-center vertically.")
    p.add_argument("--front-image", default=None,
                   help="Front-facing T-pose image to project as UV texture (Strategy S3). "
                        "Replaces zone-color materials with real image texture.")
    p.add_argument("--back-image",  default=None,
                   help="Back-facing T-pose image for UV projection. Defaults to --front-image if omitted.")
    return p.parse_args(argv)


def main():
    args = parse_args()
    print(f"isoroll blender rig")
    print(f"  state={args.state}  frames={args.start_frame}–{args.end_frame}")
    print(f"  elevation={args.elevation}°  ortho_scale={args.ortho_scale}")
    print(f"  output={args.output_dir}")
    print(f"  depth={'off' if args.no_depth else 'on'}  top={'off' if args.no_top else 'on'}  "
          f"materials={'off' if args.no_materials else 'on'}")
    if args.frame_center_z is not None:
        print(f"  frame-center-z (override)={args.frame_center_z}")
    render_all(args)


main()
