# [OBSOLETE-MESH] blender_camera.py — Isometric orthographic camera + target-empty creation for blender_iso_rig.
import math

import bpy


def get_or_create_origin_target(scene, z: float = 0.0):
    """Create 'iso_origin' empty at (0, 0, z) — cameras track this point."""
    if "iso_origin" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["iso_origin"], do_unlink=True)
    obj = bpy.data.objects.new("iso_origin", None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.location = (0, 0, z)
    scene.collection.objects.link(obj)
    return obj


def create_iso_camera(scene, name, elevation_deg, azimuth_deg, ortho_scale, shift_y, origin_obj):
    """Orthographic camera at (elevation, azimuth) with fixed rotation and shift_y pan."""
    import mathutils
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    if name in bpy.data.cameras:
        bpy.data.cameras.remove(bpy.data.cameras[name])

    cam_data = bpy.data.cameras.new(name)
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = ortho_scale
    cam_data.shift_y = shift_y   # vertical pan without rotation — calibrated to center character

    cam_obj = bpy.data.objects.new(name, cam_data)
    scene.collection.objects.link(cam_obj)

    dist = 20.0
    elev = math.radians(elevation_deg)
    azim = math.radians(azimuth_deg)
    cx = dist * math.cos(elev) * math.sin(azim)
    cy = -dist * math.cos(elev) * math.cos(azim)
    cz = dist * math.sin(elev)
    cam_obj.location = (cx, cy, cz)

    # Fixed rotation toward world origin — no Track To to avoid headless constraint update bugs
    target = mathutils.Vector((origin_obj.location.x, origin_obj.location.y, origin_obj.location.z))
    direction = target - mathutils.Vector((cx, cy, cz))
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    return cam_obj
