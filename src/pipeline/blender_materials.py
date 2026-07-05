# [OBSOLETE-MESH] blender_materials.py — Zone-color and UV-texture materials for blender_iso_rig.
from pathlib import Path

import bmesh
import bpy


def mesh_z_range(mesh_objs) -> tuple[float, float]:
    """Return (z_min, z_max) across all mesh object bounding boxes in world space."""
    import mathutils
    z_all = []
    for obj in mesh_objs:
        for corner in obj.bound_box:
            z_all.append((obj.matrix_world @ mathutils.Vector(corner)).z)
    if not z_all:
        return 0.0, 0.0
    return min(z_all), max(z_all)


def mesh_x_range(mesh_objs) -> tuple[float, float]:
    """Return (x_min, x_max) across all mesh objects in world space."""
    import mathutils
    x_all = []
    for obj in mesh_objs:
        for corner in obj.bound_box:
            x_all.append((obj.matrix_world @ mathutils.Vector(corner)).x)
    if not x_all:
        return -1.0, 1.0
    return min(x_all), max(x_all)


def apply_character_materials(mesh_objs, z_min: float, z_max: float) -> None:
    """Assign 3-zone Principled BSDF materials by face Z height:
      top 20%  → hood/head (dark teal)
      mid 60%  → body/armor (near-black)
      bot 20%  → legs/boots (dark brown)
    This gives ControlNet enough color contrast to infer front vs back orientation."""
    z_range = z_max - z_min
    if z_range < 1e-6:
        return

    zone_defs = [
        ("iso_mat_hood", (0.02, 0.18, 0.22)),  # dark teal   — head/hood
        ("iso_mat_body", (0.03, 0.03, 0.05)),  # near-black  — armor/torso
        ("iso_mat_legs", (0.08, 0.05, 0.02)),  # dark brown  — boots/legs
    ]
    mats = []
    for name, rgb in zone_defs:
        if name in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials[name])
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
            bsdf.inputs["Roughness"].default_value  = 1.0
            bsdf.inputs["Metallic"].default_value   = 0.0
            for spec_name in ("Specular", "Specular IOR Level"):
                if spec_name in bsdf.inputs:
                    bsdf.inputs[spec_name].default_value = 0.0
                    break
        mats.append(mat)

    for obj in mesh_objs:
        obj.data.materials.clear()
        for mat in mats:
            obj.data.materials.append(mat)

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        for face in bm.faces:
            centroid_world = obj.matrix_world @ face.calc_center_median()
            z_norm = (centroid_world.z - z_min) / z_range
            if z_norm >= 0.80:
                face.material_index = 0   # hood/head
            elif z_norm >= 0.20:
                face.material_index = 1   # body/armor
            else:
                face.material_index = 2   # legs/boots
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()

    print(f"  Zone materials applied to {len(mesh_objs)} mesh object(s)  "
          f"(z_min={z_min:.3f}  z_max={z_max:.3f})")


def apply_uv_texture(mesh_objs, front_path: str, back_path: str,
                     x_min: float, x_max: float, z_min: float, z_max: float) -> None:
    """Project front/back T-pose images onto mesh using face-normal-based UV mapping.

    Faces whose world-space Y-normal < 0 (front-facing in Blender default orientation)
    get the front image. Back-facing faces get the back image with horizontally mirrored UV.
    This gives geometrically correct texturing for all 8 isometric render angles.
    """
    import mathutils

    def _load_img(path, name):
        if name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[name])
        return bpy.data.images.load(str(Path(path).resolve()))

    front_img = _load_img(front_path, "iso_tex_front_img")
    back_img  = _load_img(back_path,  "iso_tex_back_img") if back_path != front_path else front_img

    def _make_img_mat(name: str, img) -> "bpy.types.Material":
        if name in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials[name])
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        uv   = nodes.new("ShaderNodeUVMap");     uv.uv_map = "iso_uv"; uv.location = (-500, 0)
        tex  = nodes.new("ShaderNodeTexImage");  tex.image = img;       tex.location = (-280, 0)
        bsdf = nodes.new("ShaderNodeBsdfPrincipled");                   bsdf.location = (20, 0)
        out  = nodes.new("ShaderNodeOutputMaterial");                   out.location  = (320, 0)
        bsdf.inputs["Roughness"].default_value = 1.0
        bsdf.inputs["Metallic"].default_value  = 0.0
        for spec in ("Specular", "Specular IOR Level"):
            if spec in bsdf.inputs:
                bsdf.inputs[spec].default_value = 0.0
                break
        links.new(uv.outputs["UV"],          tex.inputs["Vector"])
        links.new(tex.outputs["Color"],      bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"],      out.inputs["Surface"])
        nodes.active = tex  # Workbench TEXTURE shading mode reads the active image texture node
        return mat

    mat_front = _make_img_mat("iso_tex_front", front_img)
    mat_back  = _make_img_mat("iso_tex_back",  back_img)

    x_span = (x_max - x_min) or 1e-6
    z_span = (z_max - z_min) or 1e-6

    for obj in mesh_objs:
        obj.data.materials.clear()
        obj.data.materials.append(mat_front)   # index 0 — front
        obj.data.materials.append(mat_back)    # index 1 — back

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        world_mat = obj.matrix_world
        # Normals need inverse-transpose of the 3×3 rotation+scale portion
        nor_mat = world_mat.to_3x3().inverted().transposed()

        uv_layer = bm.loops.layers.uv.new("iso_uv")

        for face in bm.faces:
            w_normal = nor_mat @ face.normal
            w_normal.normalize()
            # In Blender Z-up / Y-forward: character faces -Y; front face normals point -Y.
            is_front = w_normal.y < 0
            face.material_index = 0 if is_front else 1

            for loop in face.loops:
                v_world = world_mat @ loop.vert.co
                u = (v_world.x - x_min) / x_span
                v = (v_world.z - z_min) / z_span
                if not is_front:
                    u = 1.0 - u  # mirror back view horizontally
                loop[uv_layer].uv = (max(0.0, min(1.0, u)), max(0.0, min(1.0, v)))

        bm.to_mesh(obj.data)
        bm.free()
        # Make iso_uv the active render UV so EEVEE samples it (not the original FBX UV)
        iso_uv_layer = obj.data.uv_layers.get("iso_uv")
        if iso_uv_layer:
            iso_uv_layer.active_render = True
        obj.data.update()

    print(f"  UV texture applied to {len(mesh_objs)} object(s)  "
          f"front='{Path(front_path).name}'  back='{Path(back_path).name}'")


def apply_solid_material(mesh_objs) -> None:
    """Replace all materials with a solid opaque gray Principled BSDF."""
    name = "iso_solid"
    if name in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[name])
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = "OPAQUE"
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.6, 0.6, 0.6, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.8
    for obj in mesh_objs:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    print(f"  Solid gray material applied to {len(mesh_objs)} object(s)")
