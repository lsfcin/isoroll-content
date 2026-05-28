"""[OBSOLETE-MESH] calibrate_camera.py — Batch render to find correct ortho_scale + frame_center_z.

Run from repo root:
    blender --background --python content/pipeline/calibrate_camera.py -- \
        --fbx content/chars/rogue/rig/rogue_idle.fbx \
        --out content/chars/rogue/_calibration

Output: calibrate/scale_{s}_z_{z}.png  (SE view, frame 1)
"""
import bpy, bmesh, math, sys, argparse
from pathlib import Path

def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--fbx", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--direction", default="SE", help="Camera direction to render (default: SE)")
    return p.parse_args(argv)

AZIMUTHS = {"SE":0,"E":45,"NE":90,"N":135,"NW":180,"W":225,"SW":270,"S":315}

# ── Sweep ranges ──────────────────────────────────────────────────────────────
ORTHO_SCALES   = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.7, 1.0]
CENTER_Z_VALS  = [-0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15, 0.20]

ELEVATION = 26.57
RESOLUTION_X, RESOLUTION_Y = 256, 384


class _FBXStub:
    axis_forward = '-Z'; axis_up = 'Y'
    def report(self, level, msg): pass


def import_fbx(fbx_path):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    from io_scene_fbx import import_fbx as _fbx
    _fbx.load(_FBXStub(), bpy.context, filepath=str(Path(fbx_path).resolve()),
              use_anim=True, automatic_bone_orientation=False,
              use_image_search=False, axis_forward='-Z', axis_up='Y')
    mesh_objs = [o for o in bpy.data.objects if o.type == "MESH"]
    print(f"  FBX loaded: {len(mesh_objs)} mesh objects")
    for obj in mesh_objs:
        print(f"    {obj.name}  scale={tuple(obj.scale)}")
        import mathutils
        z_all = [(obj.matrix_world @ mathutils.Vector(c)).z for c in obj.bound_box]
        x_all = [(obj.matrix_world @ mathutils.Vector(c)).x for c in obj.bound_box]
        y_all = [(obj.matrix_world @ mathutils.Vector(c)).y for c in obj.bound_box]
        print(f"      x=[{min(x_all):.4f},{max(x_all):.4f}]  "
              f"y=[{min(y_all):.4f},{max(y_all):.4f}]  "
              f"z=[{min(z_all):.4f},{max(z_all):.4f}]")
    return mesh_objs


def apply_solid_material(mesh_objs):
    mat = bpy.data.materials.new("cal_solid")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.7, 0.7, 0.7, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.8
    for obj in mesh_objs:
        obj.data.materials.clear()
        obj.data.materials.append(mat)


def setup_scene():
    scene = bpy.context.scene
    r = scene.render
    r.engine = "BLENDER_WORKBENCH"
    r.resolution_x = RESOLUTION_X
    r.resolution_y = RESOLUTION_Y
    r.resolution_percentage = 100
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGB"
    r.film_transparent = False
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    return scene


def make_camera(scene, ortho_scale, center_z, azimuth_deg, elevation_deg):
    name = "cal_cam"
    for obj in list(bpy.data.objects):
        if obj.name.startswith("cal_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Origin empty
    origin = bpy.data.objects.new("cal_origin", None)
    origin.location = (0, 0, center_z)
    scene.collection.objects.link(origin)

    cam_data = bpy.data.cameras.new(name)
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = ortho_scale
    cam_obj = bpy.data.objects.new(name, cam_data)
    scene.collection.objects.link(cam_obj)

    dist = 20.0
    elev = math.radians(elevation_deg)
    azim = math.radians(azimuth_deg)
    cam_obj.location = (
        dist * math.cos(elev) * math.sin(azim),
        -dist * math.cos(elev) * math.cos(azim),
        dist * math.sin(elev),
    )
    c = cam_obj.constraints.new("TRACK_TO")
    c.target = origin
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"

    scene.camera = cam_obj
    return cam_obj, origin


def main():
    args = parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    mesh_objs = import_fbx(args.fbx)
    apply_solid_material(mesh_objs)
    scene = setup_scene()
    scene.frame_set(1)

    azimuth = AZIMUTHS.get(args.direction, 0)
    total = len(ORTHO_SCALES) * len(CENTER_Z_VALS)
    done = 0

    for s in ORTHO_SCALES:
        for z in CENTER_Z_VALS:
            cam, origin = make_camera(scene, s, z, azimuth, ELEVATION)
            fname = f"scale_{s:.3f}_z_{z:+.3f}.png"
            scene.render.filepath = str(out_dir / fname)
            bpy.ops.render.render(write_still=True)
            done += 1
            print(f"  [{done}/{total}] {fname}")

    print(f"\nDone. {done} images → {out_dir}")


main()
