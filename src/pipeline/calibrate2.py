"""[OBSOLETE-MESH] calibrate2.py — Focused sweep: scale 0.02-0.06, z -0.10 to +0.05, all 4 cardinal views."""
import bpy, math, sys, argparse
from pathlib import Path

def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--fbx", required=True)
    p.add_argument("--out", required=True)
    return p.parse_args(argv)

ORTHO_SCALES  = [0.020, 0.025, 0.030, 0.035, 0.040, 0.050, 0.060, 0.070]
CENTER_Z_VALS = [-0.05, -0.02, 0.00, 0.02, 0.05, 0.08, 0.10]
DIRECTIONS    = {"SE": 0, "N": 135, "W": 225}   # 3 views
ELEVATION = 26.57
RX, RY = 256, 384

class _FBXStub:
    axis_forward = '-Z'; axis_up = 'Y'
    def report(self, *a): pass

def setup():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    from io_scene_fbx import import_fbx as _fbx
    _fbx.load(_FBXStub(), bpy.context,
              filepath=str(Path(bpy.data.filepath).parent if bpy.data.filepath else Path(".")),
              use_anim=True, automatic_bone_orientation=False,
              use_image_search=False, axis_forward='-Z', axis_up='Y')

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

def render_one(scene, fbx_path, s, z, azim, out_path):
    # Remove old camera/origin
    for obj in list(bpy.data.objects):
        if obj.name.startswith("_c"):
            bpy.data.objects.remove(obj, do_unlink=True)

    origin = bpy.data.objects.new("_corigin", None)
    origin.location = (0, 0, z)
    scene.collection.objects.link(origin)

    cam_data = bpy.data.cameras.new("_ccam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = s
    cam_obj = bpy.data.objects.new("_ccam", cam_data)
    scene.collection.objects.link(cam_obj)

    dist = 20.0
    elev = math.radians(ELEVATION)
    azr  = math.radians(azim)
    cam_obj.location = (dist*math.cos(elev)*math.sin(azr),
                        -dist*math.cos(elev)*math.cos(azr),
                        dist*math.sin(elev))
    c = cam_obj.constraints.new("TRACK_TO")
    c.target = origin; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
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

    combos = [(s, z, d, az) for s in ORTHO_SCALES for z in CENTER_Z_VALS for d, az in DIRECTIONS.items()]
    total = len(combos)
    for i, (s, z, d, az) in enumerate(combos, 1):
        fname = f"{d}_scale_{s:.3f}_z_{z:+.3f}.png"
        render_one(scene, args.fbx, s, z, az, out / fname)
        print(f"  [{i}/{total}] {fname}")

    print(f"Done → {out}")

main()
