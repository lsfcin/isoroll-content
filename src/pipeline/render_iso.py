"""[OBSOLETE-MESH] render_iso.py — Isometric sprite render (all 8 directions, fixed config)."""
import bpy, math, sys, argparse
from pathlib import Path

from blender_materials import apply_uv_texture, mesh_x_range, mesh_z_range

def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--fbx", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--state", default="idle")
    p.add_argument("--front-image", default=None,
                   help="Front T-pose image to UV-project onto mesh. Replaces gray material.")
    p.add_argument("--back-image", default=None,
                   help="Back T-pose image for UV projection. Defaults to --front-image if omitted.")
    return p.parse_args(argv)

SCALE      = 0.015
SHIFT_Y    = 0.3
DIRECTIONS = {"SE": 0, "E": 45, "NE": 90, "N": 135, "NW": 180, "W": 225, "SW": 270, "S": 315}
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

    if args.front_image:
        mesh_objs = [o for o in bpy.data.objects if o.type == "MESH"]
        back = args.back_image or args.front_image
        x_min, x_max = mesh_x_range(mesh_objs)
        z_min, z_max = mesh_z_range(mesh_objs)
        apply_uv_texture(mesh_objs, args.front_image, back, x_min, x_max, z_min, z_max)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = RX
    scene.render.resolution_y = RY
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "TEXTURE" if args.front_image else "MATERIAL"
    scene.frame_set(1)

    render_dir = out / "_renders" / args.state
    render_dir.mkdir(parents=True, exist_ok=True)
    combos = list(DIRECTIONS.items())
    for i, (d, az) in enumerate(combos, 1):
        out_path = render_dir / f"frame_0001_{d}.png"
        render_one(scene, SCALE, SHIFT_Y, az, out_path)
        print(f"  [{i}/{len(combos)}] {d} → {out_path}")

    print(f"Done → {render_dir}")

main()
