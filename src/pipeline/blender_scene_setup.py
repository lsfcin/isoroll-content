# [OBSOLETE-MESH] blender_scene_setup.py — Render engine and depth-compositor setup for blender_iso_rig.

def setup_render(scene, args):
    r = scene.render
    # Workbench renders solid geometry without lighting complexity — works headlessly.
    r.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    r.resolution_x = args.resolution_x
    r.resolution_y = args.resolution_y
    r.resolution_percentage = 100
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGB"
    r.image_settings.color_depth = "8"
    r.film_transparent = False
    # World background initialized to dark — _add_lights sets final values with ambient fill


def setup_depth_compositor(scene):
    """Add compositor nodes to export normalized depth pass alongside main render."""
    scene.view_layers[0].use_pass_z = True
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()

    rl       = tree.nodes.new("CompositorNodeRLayers");  rl.location = (0, 0)
    comp     = tree.nodes.new("CompositorNodeComposite"); comp.location = (800, 100)
    norm     = tree.nodes.new("CompositorNodeNormalize"); norm.location = (250, -150)
    invert   = tree.nodes.new("CompositorNodeInvert");    invert.location = (450, -150)  # closer = brighter
    file_out = tree.nodes.new("CompositorNodeOutputFile"); file_out.location = (650, -150)

    file_out.format.file_format = "PNG"
    file_out.format.color_mode  = "BW"
    file_out.format.color_depth = "8"
    # base_path and slot path set per-render in the loop
    file_out.file_slots[0].path = "depth_"

    tree.links.new(rl.outputs["Image"], comp.inputs["Image"])
    tree.links.new(rl.outputs["Depth"], norm.inputs["Value"])
    tree.links.new(norm.outputs["Value"], invert.inputs["Color"])
    tree.links.new(invert.outputs["Color"], file_out.inputs[0])

    return file_out  # caller updates base_path per render
