# [OBSOLETE-MESH] blender_render.py — Main per-direction, per-frame render loop for blender_iso_rig.
from pathlib import Path

import bpy

from blender_camera import create_iso_camera, get_or_create_origin_target
from blender_fbx_import import import_fbx
from blender_scene_setup import setup_depth_compositor, setup_render

DIRECTIONS = ["SE", "E", "NE", "N", "NW", "W", "SW", "S"]
AZIMUTHS   = [  0,  45,  90, 135, 180, 225, 270, 315]  # SE = camera faces NW, character faces viewer


def render_all(args):
    scene   = bpy.context.scene
    out_dir = Path(args.output_dir).resolve()

    origin_z = 0.0
    if args.fbx:
        detected_start, detected_end, origin_z = import_fbx(args.fbx, args)
        # Use detected range unless user explicitly passed --start-frame / --end-frame
        if args.start_frame == 1 and args.end_frame == 20:
            args.start_frame = detected_start
            args.end_frame   = detected_end
            print(f"  Using detected frame range: {args.start_frame}–{args.end_frame}")

    # Allow manual override of camera target Z for framing correction
    if args.frame_center_z is not None:
        origin_z = args.frame_center_z
        print(f"  frame-center-z override: {origin_z:.3f}")
    else:
        print(f"  frame-center-z (auto): {origin_z:.3f}")

    setup_render(scene, args)

    depth_node = None
    if not args.no_depth:
        depth_node = setup_depth_compositor(scene)

    origin_obj = get_or_create_origin_target(scene, origin_z)

    # Pre-compute azimuth map
    azim_map = dict(zip(DIRECTIONS, AZIMUTHS))
    if not args.no_top:
        azim_map["TOP"] = 0
    all_dirs = list(azim_map.keys())
    total = len(all_dirs) * (args.end_frame - args.start_frame + 1)
    done  = 0
    cameras = []

    for direction in all_dirs:
        azimuth  = azim_map[direction]
        elev     = 89.9 if direction == "TOP" else args.elevation
        shift    = 0.0  if direction == "TOP" else args.shift_y

        cam_obj = create_iso_camera(scene, f"iso_cam_{direction}", elev, azimuth,
                                     args.ortho_scale, shift, origin_obj)
        cameras.append(cam_obj)
        scene.camera = cam_obj

        for frame in range(args.start_frame, args.end_frame + 1):
            scene.frame_set(frame)

            render_dir = out_dir / "_renders" / args.state
            render_dir.mkdir(parents=True, exist_ok=True)

            main_path = render_dir / f"frame_{frame:04d}_{direction}.png"
            scene.render.filepath = str(main_path)

            if depth_node is not None:
                depth_node.base_path = str(render_dir) + "/"

            bpy.ops.render.render(write_still=True)

            if depth_node is not None:
                src = render_dir / f"depth_{frame:04d}.png"
                dst = render_dir / f"frame_{frame:04d}_depth_{direction}.png"
                if src.exists():
                    src.rename(dst)

            done += 1
            print(f"  [{done}/{total}] {direction} frame {frame:04d} → {main_path.relative_to(out_dir)}")

    # Clean up rig objects so scene stays clean
    for cam_obj in cameras:
        bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.objects.remove(origin_obj, do_unlink=True)

    print(f"\nDone. {done} renders saved to {out_dir}/_renders/{args.state}/")
