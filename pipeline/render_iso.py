"""[OBSOLETE-MESH] render_iso.py — Isometric sprite render (all 8 directions, fixed config)."""
import bpy, bmesh, math, sys, argparse
from pathlib import Path

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

def _mesh_bounds(mesh_objs):
    """Return (x_min, x_max, z_min, z_max) in world space across all mesh objects."""
    import mathutils
    xs, zs = [], []
    for obj in mesh_objs:
        for corner in obj.bound_box:
            w = obj.matrix_world @ mathutils.Vector(corner)
            xs.append(w.x)
            zs.append(w.z)
    if not xs:
        return -1.0, 1.0, 0.0, 2.0
    return min(xs), max(xs), min(zs), max(zs)


def apply_uv_texture(mesh_objs, front_path, back_path):
    """Project front/back T-pose images onto mesh via orthographic XZ UV mapping.
    Front-facing faces (world Y-normal < 0) → front image.
    Back-facing faces → back image with mirrored U.
    """
    import mathutils

    x_min, x_max, z_min, z_max = _mesh_bounds(mesh_objs)
    x_span = (x_max - x_min) or 1e-6
    z_span = (z_max - z_min) or 1e-6

    def _load_img(path, name):
        if name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[name])
        return bpy.data.images.load(str(Path(path).resolve()))

    front_img = _load_img(front_path, "iso_tex_front")
    back_img  = _load_img(back_path, "iso_tex_back") if back_path != front_path else front_img

    def _make_mat(name, img):
        if name in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials[name])
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        uv   = nodes.new("ShaderNodeUVMap");    uv.uv_map = "iso_uv"; uv.location = (-500, 0)
        tex  = nodes.new("ShaderNodeTexImage"); tex.image = img;       tex.location = (-280, 0)
        bsdf = nodes.new("ShaderNodeBsdfPrincipled");                  bsdf.location = (20, 0)
        out  = nodes.new("ShaderNodeOutputMaterial");                  out.location  = (320, 0)
        bsdf.inputs["Roughness"].default_value = 1.0
        bsdf.inputs["Metallic"].default_value  = 0.0
        for spec in ("Specular", "Specular IOR Level"):
            if spec in bsdf.inputs:
                bsdf.inputs[spec].default_value = 0.0
                break
        links.new(uv.outputs["UV"],     tex.inputs["Vector"])
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        nodes.active = tex  # Workbench TEXTURE mode reads the active image texture node
        return mat

    mat_front = _make_mat("iso_mat_front", front_img)
    mat_back  = _make_mat("iso_mat_back",  back_img)

    for obj in mesh_objs:
        obj.data.materials.clear()
        obj.data.materials.append(mat_front)  # index 0
        obj.data.materials.append(mat_back)   # index 1

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        nor_mat  = obj.matrix_world.to_3x3().inverted().transposed()
        uv_layer = bm.loops.layers.uv.new("iso_uv")

        for face in bm.faces:
            w_normal = (nor_mat @ face.normal).normalized()
            is_front = w_normal.y < 0
            face.material_index = 0 if is_front else 1
            for loop in face.loops:
                v_world = obj.matrix_world @ loop.vert.co
                u = (v_world.x - x_min) / x_span
                v = (v_world.z - z_min) / z_span
                if not is_front:
                    u = 1.0 - u
                loop[uv_layer].uv = (max(0.0, min(1.0, u)), max(0.0, min(1.0, v)))

        bm.to_mesh(obj.data)
        bm.free()
        uv_l = obj.data.uv_layers.get("iso_uv")
        if uv_l:
            uv_l.active_render = True
        obj.data.update()

    print(f"  UV texture: front='{Path(front_path).name}'  back='{Path(back_path).name}'")


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
        apply_uv_texture(mesh_objs, args.front_image, back)

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
