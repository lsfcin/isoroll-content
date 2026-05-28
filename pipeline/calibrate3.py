"""[OBSOLETE-MESH] calibrate3.py — Sweep camera Z translation at fixed scale=0.020, no constraint rotation.

Camera orientation is baked from elevation/azimuth. Camera translated +Z (up) or -Z (down).
"""
import bpy, bmesh, math, sys, argparse
from pathlib import Path

def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--fbx", required=True)
    p.add_argument("--out", required=True)
    return p.parse_args(argv)

SCALE        = 0.020
CAM_Z_OFFSETS = [-0.04, -0.03, -0.02, -0.01, 0.00, +0.01, +0.02, +0.03, +0.04, +0.05]
DIRECTIONS   = {"SE": 0, "N": 135, "W": 225}
ELEVATION    = 26.57
DIST         = 20.0
RX, RY       = 256, 384

class _FBXStub:
    axis_forward = '-Z'; axis_up = 'Y'
    def report(self, *a): pass

def load_fbx(path):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    from io_scene_fbx import import_fbx as _fbx
    _fbx.load(_FBXStub(), bpy.context, filepath=str(Path(path).resolve()),
              use_anim=True, automatic_bone_orientation=False,
              use_image_search=False, axis_forward='-Z', axis_up='Y')
    mesh_objs = [o for o in bpy.data.objects if o.type == "MESH"]
    mat = bpy.data.materials.new("m")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.75, 0.75, 0.75, 1.0)
    for obj in mesh_objs:
        obj.data.materials.clear()
        obj.data.materials.append(mat)

def render_one(scene, scale, cam_z_offset, azim_deg, out_path):
    for obj in list(bpy.data.objects):
        if obj.name.startswith("_c"):
            bpy.data.objects.remove(obj, do_unlink=True)

    elev = math.radians(ELEVATION)
    azim = math.radians(azim_deg)

    # Camera position: standard isometric position + vertical translation
    cx = DIST * math.cos(elev) * math.sin(azim)
    cy = -DIST * math.cos(elev) * math.cos(azim)
    cz = DIST * math.sin(elev) + cam_z_offset   # ← vertical shift here

    cam_data = bpy.data.cameras.new("_ccam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = scale
    cam_obj = bpy.data.objects.new("_ccam", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = (cx, cy, cz)

    # Fixed rotation from elevation/azimuth — NOT Track To, so no angle change
    # Camera looks toward world origin (0,0,0) from (cx,cy,cz).
    # Direction vector: from cam toward origin
    import mathutils
    direction = mathutils.Vector((0, 0, 0)) - mathutils.Vector((cx, cy, cz))
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

    scene.camera = cam_obj
    scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)

def main():
    args = parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    load_fbx(args.fbx)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = RX
    scene.render.resolution_y = RY
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.frame_set(1)

    combos = [(z, d, az) for z in CAM_Z_OFFSETS for d, az in DIRECTIONS.items()]
    for i, (z, d, az) in enumerate(combos, 1):
        sign = "+" if z >= 0 else ""
        fname = f"{d}_z{sign}{z:.2f}.png"
        render_one(scene, SCALE, z, az, out / fname)
        print(f"  [{i}/{len(combos)}] {fname}")

    print(f"Done → {out}")

main()
