# [OBSOLETE-MESH] calibrate4.py — Sweep camera shift_y (vertical pan) and ortho_scale (size).
"""[OBSOLETE-MESH] calibrate4.py — Sweep camera shift_y (vertical pan) and ortho_scale (size).
camera.shift_y > 0 → view shifts up → character moves DOWN in frame.
"""
import bpy, math, sys, argparse
from pathlib import Path

def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--fbx", required=True)
    p.add_argument("--out", required=True)
    return p.parse_args(argv)

SCALES     = [0.015, 0.018, 0.020, 0.022, 0.025]
SHIFT_Y    = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
DIRECTIONS = {"SE": 0, "N": 135, "W": 225}
ELEVATION  = 26.57
DIST       = 20.0
RX, RY     = 256, 384

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

def render_one(scene, scale, shift_y, azim_deg, out_path):
    import mathutils
    for obj in list(bpy.data.objects):
        if obj.name.startswith("_c"):
            bpy.data.objects.remove(obj, do_unlink=True)

    elev = math.radians(ELEVATION)
    azim = math.radians(azim_deg)
    cx = DIST * math.cos(elev) * math.sin(azim)
    cy = -DIST * math.cos(elev) * math.cos(azim)
    cz = DIST * math.sin(elev)

    cam_data = bpy.data.cameras.new("_ccam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = scale
    cam_data.shift_y = shift_y        # ← vertical pan, no rotation
    cam_obj = bpy.data.objects.new("_ccam", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = (cx, cy, cz)
    direction = mathutils.Vector((0, 0, 0)) - mathutils.Vector((cx, cy, cz))
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

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

    combos = [(s, sy, d, az) for s in SCALES for sy in SHIFT_Y for d, az in DIRECTIONS.items()]
    for i, (s, sy, d, az) in enumerate(combos, 1):
        fname = f"{d}_scale{s:.3f}_shift{sy:.1f}.png"
        render_one(scene, s, sy, az, out / fname)
        print(f"  [{i}/{len(combos)}] {fname}")

    print(f"Done → {out}")

main()
