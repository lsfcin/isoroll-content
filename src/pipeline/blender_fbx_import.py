# [OBSOLETE-MESH] blender_fbx_import.py — Mixamo FBX import, normalization, and lighting for blender_iso_rig.
from pathlib import Path

import bpy

from blender_materials import (
    apply_character_materials,
    apply_solid_material,
    apply_uv_texture,
    mesh_x_range,
    mesh_z_range,
)


class _FBXOperatorStub:
    """Minimal stub so import_fbx.load() can call self.report() without crashing."""
    axis_forward = '-Z'
    axis_up      = 'Y'
    def report(self, level, msg):
        print(f"  [FBX] {msg}")


def import_fbx(fbx_path: str, args) -> tuple[int, int, float]:
    """Import Mixamo FBX, normalize scale to ~2m, return detected (start, end) frame range + center_z."""
    abs_path = str(Path(fbx_path).resolve())
    print(f"  Importing FBX: {abs_path}")

    # Clear default cube/light/camera added by Blender's empty startup
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    # Blender 5: bpy.ops.import_scene.fbx() is broken in headless mode (CollectionProperty
    # 'files' inaccessible without UI context). Call the underlying loader directly.
    from io_scene_fbx import import_fbx as _fbx_loader
    _fbx_loader.load(
        _FBXOperatorStub(),
        bpy.context,
        filepath=abs_path,
        use_anim=True,
        automatic_bone_orientation=False,
        use_image_search=False,
        axis_forward='-Z',
        axis_up='Y',
    )

    # Detect armature and action frame range
    arm_obj = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
    frame_start, frame_end = args.start_frame, args.end_frame
    if arm_obj and arm_obj.animation_data and arm_obj.animation_data.action:
        action = arm_obj.animation_data.action
        frame_start = int(action.frame_range[0])
        frame_end   = int(action.frame_range[1])
        print(f"  Action: '{action.name}'  frames {frame_start}–{frame_end}")

    # Normalize scale: Mixamo often exports at cm (1 unit = 1 cm → character ~180 units tall).
    mesh_objs = [o for o in bpy.data.objects if o.type == "MESH"]
    center_z  = 0.0
    if mesh_objs:
        z_min, z_max = mesh_z_range(mesh_objs)
        height = z_max - z_min
        print(f"  Character height: {height:.2f} units  z=[{z_min:.2f}, {z_max:.2f}]")

        if height > 10:
            # Apply scale and recompute z range in scaled world space
            for obj in bpy.data.objects:
                if obj.parent is None:
                    obj.scale = (0.01, 0.01, 0.01)
            bpy.context.view_layer.update()
            z_min, z_max = mesh_z_range(mesh_objs)
            height = z_max - z_min
            print(f"  Scale 0.01 applied  height={height:.3f}  z=[{z_min:.3f}, {z_max:.3f}]")

        # Center character at z=0: offset root objects so bounding box center lands on origin.
        # This lets us always use frame_center_z=0, avoiding Blender headless Track To update bugs.
        z_geo_center = (z_min + z_max) / 2.0
        for obj in bpy.data.objects:
            if obj.parent is None:
                obj.location.z -= z_geo_center
        bpy.context.view_layer.update()
        z_min -= z_geo_center
        z_max -= z_geo_center
        print(f"  Z-centered (offset {-z_geo_center:+.4f})  z=[{z_min:.4f}, {z_max:.4f}]")

        # Camera target: always world origin after centering.
        center_z = 0.0

        print(f"  ortho_scale={args.ortho_scale:.4f}  shift_y={args.shift_y:.2f}")

        if not args.no_materials:
            if getattr(args, "front_image", None):
                x_min_m, x_max_m = mesh_x_range(mesh_objs)
                back = args.back_image or args.front_image
                apply_uv_texture(mesh_objs, args.front_image, back,
                                 x_min_m, x_max_m, z_min, z_max)
            else:
                apply_character_materials(mesh_objs, z_min, z_max)
        else:
            # Mixamo FBX materials use BLEND alpha mode → near-transparent renders.
            # Replace with a solid gray material so the mesh silhouette is visible.
            apply_solid_material(mesh_objs)

    # Add isometric 3-point light rig (deleted with default scene objects above)
    _add_lights(bpy.context.scene)

    return frame_start, frame_end, center_z


def _add_lights(scene):
    """3-point light rig: key (sun from high-left), fill (softer from right), rim (back-right).
    SUN direction is derived from location → origin so lights actually illuminate the character."""
    import mathutils
    lights = [
        ("iso_key",  "SUN",   (-3,  4, 6), (0.9, 0.85, 0.8), 3.0),
        ("iso_fill", "SUN",   ( 4, -2, 4), (0.6, 0.65, 0.8), 1.5),
        ("iso_rim",  "SUN",   ( 1, -4, 3), (0.8, 0.7,  0.9), 1.0),
    ]
    for name, kind, loc, color, strength in lights:
        if name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
        light_data = bpy.data.lights.new(name, kind)
        light_data.energy = strength
        light_data.color  = color
        light_obj = bpy.data.objects.new(name, light_data)
        light_obj.location = loc
        # SUN emits along its local -Z; rotate so -Z points from loc toward origin
        rot = mathutils.Vector(loc).normalized()
        light_obj.rotation_euler = (-mathutils.Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        scene.collection.objects.link(light_obj)

    # Slight ambient so shadow sides aren't pure black
    if scene.world and scene.world.node_tree:
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.08, 0.08, 0.10, 1.0)
            bg.inputs["Strength"].default_value = 0.5
