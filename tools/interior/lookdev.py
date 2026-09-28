"""Look-dev of the reference house in Blender: builds a simplified shell (walls with openings, floors, ceilings, glazing,
balcony) from tools/interior/modern12.house.json, places the library models exactly like the app does, lights it and
renders the house's walk views (Cycles) → Renders/interior/<view>.png + sheet.png. Also saves Renders/interior/house.blend.

    Blender -b --python tools/interior/lookdev.py -- [--samples 96] [--size 1200x800] [view name …]

App → Blender: [x, y, z] → (x, z, y); item rotation r (0 = north, 90 = east) → yaw 180 − r (models face −Y)."""
import json
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import materials  # noqa: E402
from kit import ROOT  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "Renders", "interior")
HDRI = os.path.join(ROOT, ".cache", "polyhaven", "blend", "hdri", "qwantani_sunset_puresky_4k.hdr")


def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    opt = {"samples": 96, "size": (1200, 800), "views": [], "doc": os.path.join(HERE, "modern12.house.json"), "save": True}
    i = 0
    while i < len(a):
        if a[i] == "--samples":
            opt["samples"] = int(a[i + 1]); i += 2
        elif a[i] == "--size":
            w, h = a[i + 1].split("x"); opt["size"] = (int(w), int(h)); i += 2
        elif a[i] == "--doc":
            opt["doc"] = a[i + 1]; i += 2
        elif a[i] == "--nosave":
            opt["save"] = False; i += 1
        else:
            opt["views"].append(a[i]); i += 1
    return opt


# ---------------------------------------------------------------------------------------------------- geometry helpers
def mat(spec):
    return materials.resolve(spec)


def obj_from_bm(bm, name, coll):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    return o


def metre_uv(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            c = o.matrix_world @ l.vert.co
            l[uv].uv = (c.y, c.z) if ax == 0 else (c.x, c.z) if ax == 1 else (c.x, c.y)
    bm.to_mesh(o.data)
    bm.free()


def box(name, lo, hi, material, coll):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector([lo[i] + (v.co[i] + 0.5) * (hi[i] - lo[i]) for i in range(3)])
    o = obj_from_bm(bm, name, coll)
    o.data.materials.append(material)
    metre_uv(o)
    return o


def prism(name, outline, z0, z1, material, coll):
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z0)) for x, y in outline]
    f = bm.faces.new(vs)
    bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in bm.verts:
        if v not in vs:
            v.co.z = z1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = obj_from_bm(bm, name, coll)
    o.data.materials.append(material)
    metre_uv(o)
    return o


# ---------------------------------------------------------------------------------------------------- the house
class House:
    def __init__(self, doc):
        self.doc = doc
        self.levels = {l["id"]: l for l in doc["levels"]}
        order = sorted(doc["levels"], key=lambda l: l["elevation"])
        self.next = {order[i]["id"]: order[i + 1] for i in range(len(order) - 1)}
        self.coll = bpy.data.collections.new("shell")
        bpy.context.scene.collection.children.link(self.coll)
        self.furn = bpy.data.collections.new("furniture")
        bpy.context.scene.collection.children.link(self.furn)

    def wall_extent(self, w):
        L = self.levels[w["level"]]
        if w.get("kind") == "interior":
            return L["elevation"], L["elevation"] + L["height"]
        bottom = 0.0 if L["elevation"] == min(l["elevation"] for l in self.levels.values()) else L["elevation"] - L["slab"]
        nxt = self.next.get(w["level"])
        top = (nxt["elevation"] - nxt["slab"]) if nxt else L["elevation"] + L["height"] + 0.3
        return w.get("bottom", bottom), w.get("top", top)

    def walls(self):
        for w in self.doc["walls"]:
            a, b = Vector((*w["a"], 0)), Vector((*w["b"], 0))
            d = (b - a).normalized()
            left = Vector((-d.y, d.x, 0))
            interior = w.get("kind") == "interior"
            t = w.get("thickness", 0.12 if interior else 0.4)
            o0, o1 = (-t / 2, t / 2) if interior else (0.0, t)
            z0, z1 = self.wall_extent(w)
            bm = bmesh.new()
            pts = [a + left * o0, b + left * o0, b + left * o1, a + left * o1]
            vs = [bm.verts.new((p.x, p.y, z0)) for p in pts]
            f = bm.faces.new(vs)
            bmesh.ops.extrude_face_region(bm, geom=[f])
            for v in bm.verts:
                if v not in vs:
                    v.co.z = z1
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
            o = obj_from_bm(bm, "wall_" + w["id"], self.coll)
            inside = mat(w.get("inside", "plaster"))
            outside = mat(w.get("outside", "plaster" if interior else "stucco"))
            o.data.materials.append(inside)
            o.data.materials.append(outside)
            # openings: boolean cutters
            L = self.levels[w["level"]]
            cutters = []
            for op in self.doc["openings"]:
                if op["wall"] != w["id"]:
                    continue
                typ = op.get("type", "window")
                sill = op.get("sill", 0.9 if typ == "window" else 0.0)
                y0 = L["elevation"] + sill
                y1 = y0 + op["height"]
                p0 = a + d * op["at"]
                p1 = p0 + d * op["width"]
                c = box("cut", (0, 0, 0), (1, 1, 1), inside, self.coll)
                bmc = bmesh.new()
                corners = [p0 + left * (o0 - 0.3), p1 + left * (o0 - 0.3), p1 + left * (o1 + 0.3), p0 + left * (o1 + 0.3)]
                vs = [bmc.verts.new((p.x, p.y, y0)) for p in corners]
                fc = bmc.faces.new(vs)
                bmesh.ops.extrude_face_region(bmc, geom=[fc])
                for v in bmc.verts:
                    if v not in vs:
                        v.co.z = y1
                bmesh.ops.recalc_face_normals(bmc, faces=bmc.faces[:])
                bmc.to_mesh(c.data)
                bmc.free()
                cutters.append(c)
                self.fill_opening(op, typ, p0, p1, d, left, o0, o1, y0, y1)
            for c in cutters:
                m = o.modifiers.new("cut", "BOOLEAN")
                m.operation = "DIFFERENCE"
                m.solver = "EXACT"
                m.object = c
            bpy.context.view_layer.objects.active = o
            for m in list(o.modifiers):
                bpy.ops.object.modifier_apply(modifier=m.name)
            for c in cutters:
                bpy.data.objects.remove(c)
            # faces towards the left side = inside finish, right = outside; reveals (along d) inside too
            for p in o.data.polygons:
                p.material_index = 1 if p.normal.dot(left) < -0.5 else 0
            metre_uv(o)

    def fill_opening(self, op, typ, p0, p1, d, left, o0, o1, y0, y1):
        mid = (o0 + o1) / 2
        frame = mat("black_metal")
        if typ in ("window", "glazing", "entryDoor"):
            cols = op.get("columns", 1)
            fw = 0.05
            for i in range(cols + 1):                      # mullions
                q = p0 + (p1 - p0) * (i / cols)
                lo = q + left * (mid - 0.04) - d * fw / 2
                hi = q + left * (mid + 0.04) + d * fw / 2
                box("mullion", (min(lo.x, hi.x), min(lo.y, hi.y), y0), (max(lo.x, hi.x), max(lo.y, hi.y), y1), frame, self.coll)
            for z in (y0, y1 - fw):
                lo, hi = p0 + left * (mid - 0.04), p1 + left * (mid + 0.04)
                box("rail", (min(lo.x, hi.x), min(lo.y, hi.y), z), (max(lo.x, hi.x), max(lo.y, hi.y), z + fw), frame, self.coll)
            lo, hi = p0 + left * (mid - 0.006), p1 + left * (mid + 0.006)
            g = box("glass", (min(lo.x, hi.x), min(lo.y, hi.y), y0), (max(lo.x, hi.x), max(lo.y, hi.y), y1), mat("glass"), self.coll)
            g.visible_shadow = False
        elif typ in ("solidDoor",):
            lo, hi = p0 + left * (mid - 0.03), p1 + left * (mid + 0.03)
            box("door", (min(lo.x, hi.x), min(lo.y, hi.y), y0), (max(lo.x, hi.x), max(lo.y, hi.y), y1), mat("furniture_dark"), self.coll)
        elif typ == "door":
            # interior doors shown open against the wall: just a frame
            pass

    def rooms(self):
        for r in self.doc["rooms"]:
            L = self.levels[r["level"]]
            e, h = L["elevation"], r.get("height", L["height"])
            prism("floor_" + r["id"], r["outline"], e - L["slab"], e, mat(r.get("floor", "oak_planks")), self.coll)
            # a few mm below the slab above: coplanar faces would shadow each other (black ceilings in Cycles)
            prism("ceil_" + r["id"], r["outline"], e + h - 0.03, e + h - 0.01, mat(r.get("ceiling", "plaster#f2efe9")), self.coll)

    def elements(self):
        for el in self.doc.get("elements", []):
            if el["type"] in ("platform", "box", "beam", "column"):
                lo, hi = el["min"], el["max"]
                box(el["id"], (lo[0], lo[2], lo[1]), (hi[0], hi[2], hi[1]), mat(el.get("top", el.get("material", "plaster"))), self.coll)
            elif el["type"] == "railing":
                path = el["path"]
                for i in range(len(path) - 1):
                    a, b = path[i], path[i + 1]
                    lo = (min(a[0], b[0]) - 0.01, min(a[1], b[1]) - 0.01, el["y"])
                    hi = (max(a[0], b[0]) + 0.01, max(a[1], b[1]) + 0.01, el["y"] + el.get("height", 1.0))
                    g = box("rail_glass", lo, hi, mat("glass"), self.coll)
                    g.visible_shadow = False
                    box("rail_top", (lo[0], lo[1], hi[2] - 0.03), (hi[0], hi[1], hi[2]), mat("black_metal"), self.coll)
        for r in self.doc.get("roofs", []):
            top = max(self.wall_extent(w)[1] for w in self.doc["walls"] if w.get("kind") != "interior")
            xs = [p[0] for p in r["outline"]]
            ys = [p[1] for p in r["outline"]]
            box("roof", (min(xs) - 0.4, min(ys) - 0.4, top - 0.3), (max(xs) + 0.4, max(ys) + 0.4, top), mat("stucco#3a3a3a"), self.coll)

    def items(self):
        missing = []
        have = {m["id"] for m in materials.manifest()["models"]}
        for it in self.doc["items"]:
            if it["model"] not in have:
                missing.append(it["model"])
                continue
            L = self.levels[it["level"]]
            x, y, z = it["position"]
            root = materials.import_model(it["model"], (x, z, L["elevation"] + y), 180 - it.get("rotation", 0),
                                          it.get("params"), name="item_" + it["id"])
            for o in root.children_recursive:
                for c in o.users_collection:
                    c.objects.unlink(o)
                self.furn.objects.link(o)
            for c in root.users_collection:
                c.objects.unlink(root)
            self.furn.objects.link(root)
        if missing:
            print("MISSING MODELS (procedural or not built yet):", sorted(set(missing)))

    def lights(self):
        for l in self.doc.get("lights", []):
            L = self.levels.get(l.get("level"), {"elevation": 0})
            x, y, z = l["position"]
            ld = bpy.data.lights.new(l["id"], "POINT")
            ld.energy = 70 * l.get("intensity", 1)
            ld.shadow_soft_size = 0.15
            ld.color = (1.0, 0.82, 0.62) if l.get("color", "warm") == "warm" else (0.9, 0.95, 1.0)
            o = bpy.data.objects.new(l["id"], ld)
            o.location = (x, z, L["elevation"] + y)
            bpy.context.scene.collection.objects.link(o)
        # soft fill in every room without an explicit light (the app does the same)
        for r in self.doc["rooms"]:
            L = self.levels[r["level"]]
            xs = [p[0] for p in r["outline"]]
            ys = [p[1] for p in r["outline"]]
            area = (max(xs) - min(xs)) * (max(ys) - min(ys))
            ld = bpy.data.lights.new("fill_" + r["id"], "AREA")
            ld.shape = "RECTANGLE"
            ld.size, ld.size_y = (max(xs) - min(xs)) * 0.7, (max(ys) - min(ys)) * 0.7
            ld.energy = 8 * area
            ld.color = (1.0, 0.86, 0.7)
            o = bpy.data.objects.new("fill_" + r["id"], ld)
            o.location = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, L["elevation"] + r.get("height", L["height"]) - 0.06)   # under the ceiling panel
            o.visible_camera = False
            o.visible_glossy = False
            bpy.context.scene.collection.objects.link(o)


def ground_and_world():
    sc = bpy.context.scene
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    env = w.node_tree.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(HDRI)
    mp = w.node_tree.nodes.new("ShaderNodeMapping")
    tc = w.node_tree.nodes.new("ShaderNodeTexCoord")
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(160))
    w.node_tree.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    w.node_tree.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    w.node_tree.links.new(env.outputs["Color"], w.node_tree.nodes["Background"].inputs["Color"])
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    coll = bpy.data.collections.new("site")
    sc.collection.children.link(coll)
    box("ground", (-60, -60, -0.2), (80, 80, 0.0), mat("lawn_texture"), coll)
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.5
    sun.data.angle = math.radians(1.5)
    sun.data.color = (1.0, 0.85, 0.68)
    az = math.radians(215)
    sun.rotation_euler = (math.radians(90 - 32), 0, -az + math.pi)
    sc.collection.objects.link(sun)
    # a ring of distant trees so windows show a landscape (landscape kit if present)
    trees(coll)


def trees(coll):
    """Fir and broadleaf trees from the Poly Haven cache, scattered 12–50 m around the house (the view from the windows)."""
    src = os.path.join(ROOT, ".cache", "polyhaven", "blend")
    protos = []
    for name in ("fir_tree_01", "fir_tree_01", "fir_sapling_medium", "island_tree_01"):
        path = os.path.join(src, name, name + ".blend")
        if not os.path.exists(path) or any(p.name.startswith(name) for p in protos):
            continue
        with bpy.data.libraries.load(path, link=False) as (src_data, dst):
            dst.objects = [n for n in src_data.objects]
        meshes = [o for o in dst.objects if o is not None and o.type == "MESH"]
        if not meshes:
            continue
        # one proto per file: the biggest mesh (LOD0)
        best = max(meshes, key=lambda o: len(o.data.polygons))
        best.name = name
        best.parent = None
        protos.append(best)
    if not protos:
        print("no trees")
        return
    rng = np.random.default_rng(3)
    n = 0
    for _ in range(220):
        a = rng.random() * 2 * math.pi
        r = 13 + rng.random() ** 0.7 * 45
        x, y = 8.5 + math.cos(a) * r, 6 + math.sin(a) * r
        if -3 < y < 18 and -4 < x < 22:
            continue
        p = protos[rng.integers(len(protos))]
        o = bpy.data.objects.new("tree", p.data)
        o.location = (x, y, 0)
        s = 0.9 + rng.random() * 0.7
        o.scale = (s, s, s)
        o.rotation_euler[2] = rng.random() * 6.28
        coll.objects.link(o)
        n += 1
    print("trees", n, [p.name for p in protos])


def render_views(doc, opt):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "GPU"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for dv in prefs.devices:
        dv.use = True
    sc.cycles.samples = opt["samples"]
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.render.resolution_x, sc.render.resolution_y = opt["size"]
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = 0.3
    levels = {l["id"]: l for l in doc["levels"]}
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.lens = 18
    cam.data.sensor_width = 36
    sc.collection.objects.link(cam)
    sc.camera = cam
    os.makedirs(OUT_DIR, exist_ok=True)
    done = []
    for v in doc["views"]:
        if v.get("type") != "walk" or (opt["views"] and v["name"] not in opt["views"]):
            continue
        x, y, z = v["position"]
        cam.location = (x, z, y + 1.45)
        cam.rotation_euler = (math.radians(90 + v.get("pitch", 0)), 0, -math.radians(v.get("yaw", 0)))
        path = os.path.join(OUT_DIR, v["name"] + ".png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        done.append(path)
        print("rendered", v["name"], flush=True)
    return done


def main():
    opt = args()
    doc = json.load(open(opt["doc"]))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    h = House(doc)
    h.walls()
    h.rooms()
    h.elements()
    h.items()
    h.lights()
    ground_and_world()
    if opt["save"]:
        os.makedirs(OUT_DIR, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "house.blend"))
    render_views(doc, opt)


main()
