"""Studio previews of library models → one contact sheet (for review against the reference).

    Blender -b --python tools/interior/preview.py -- <out.png> <id|room> ...
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import materials  # noqa: E402
import models  # noqa: E402
from kit import ROOT  # noqa: E402

HDRI = os.path.join(ROOT, ".cache", "polyhaven", "blend", "hdri", "kloppenheim_06_puresky_4k.hdr")
CELL = 420


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "GPU"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = CELL
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    env = w.node_tree.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(HDRI)
    w.node_tree.links.new(env.outputs["Color"], w.node_tree.nodes["Background"].inputs["Color"])
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    bpy.ops.mesh.primitive_plane_add(size=40)
    fl = bpy.context.object
    fl.data.materials.append(materials.builtin("soft_white#d9d6d0"))
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 2.5
    sun.data.angle = math.radians(8)
    sun.rotation_euler = (math.radians(50), 0, math.radians(35))
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.lens = 50
    sc.collection.objects.link(cam)
    sc.camera = cam
    return fl, cam


def frame(cam, root, hanging, wall):
    pts = [o.matrix_world @ Vector(c) for o in root.children_recursive if o.type == "MESH" for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    c = (lo + hi) / 2
    r = (hi - lo).length / 2
    d = Vector((0.5, -1.0, 0.45 if not wall else 0.2)).normalized()
    dist = r / math.sin(math.radians(18)) * 0.82
    cam.location = c + d * dist
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    return lo


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    out, want = argv[0], set(argv[1:])
    ids = [e for e, _ in models.entries() if not want or e["id"] in want or e["room"] in want]
    have = {m["id"] for m in materials.manifest()["models"]}
    ids = [e for e in ids if e["id"] in have]
    tiles = []
    tmp = out + ".tile.png"
    for e in ids:
        floor, cam = setup()
        materials._cache.clear()
        wall = e.get("pivot") == "wall"
        hanging = e.get("hanging", False)
        z = 1.2 if wall else 2.2 if hanging else 0.0
        root = materials.import_model(e["id"], (0, 0, z))
        bpy.context.view_layer.update()
        lo = frame(cam, root, hanging, wall)
        if wall:                                   # a wall behind wall pieces
            bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0.002 + max(0, 0), 5), rotation=(math.radians(90), 0, 0))
            bpy.context.object.data.materials.append(materials.builtin("soft_white#e3e0da"))
        bpy.context.scene.render.filepath = tmp
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(tmp)
        a = np.array(img.pixels[:], np.float32).reshape(CELL, CELL, 4)
        tiles.append(a)
        bpy.data.images.remove(img)
        print("rendered", e["id"], flush=True)
    cols = min(5, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = np.ones((rows * CELL, cols * CELL, 4), np.float32)
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        sheet[(rows - 1 - r) * CELL:(rows - r) * CELL, c * CELL:(c + 1) * CELL] = t
    img = bpy.data.images.new("sheet", cols * CELL, rows * CELL)
    img.pixels.foreach_set(sheet.ravel())
    img.filepath_raw = out
    img.file_format = "PNG"
    img.save()
    os.remove(tmp)
    print("sheet", out, [e["id"] for e in ids])


main()
