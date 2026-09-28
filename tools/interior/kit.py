"""Modelling kit for the interior furniture library (Blender, run through tools/assets/process_blender.py).

Every model is built from simple parts (bevelled boxes, cylinders, lathes, tubes, flat panels) in metres, front towards
Blender -Y, floor at z = 0. Each part belongs to a material slot named by its role ("upholstery", "legs", "top"); a slot
either takes a library / built-in material by default ("velvet#b9ab98", "black_metal", "led") that the house document can
override per item, or carries its own texture made here (paintings, rugs, screen images) with 0..1 UVs.

    k = Kit("sofa_corner")
    k.box("upholstery", (0, 0, 0.2), (2, 1, 0.4), r=0.03)
    return k.finish(entry, {"upholstery": "velvet#b9ab98"}, own={"art": {"albedo": image_array}})
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "Assets", "House4696", "External")


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def _link(bm, name):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _rot(rot):
    return Matrix.Rotation(math.radians(rot[2]), 4, "Z") @ Matrix.Rotation(math.radians(rot[1]), 4, "Y") @ \
        Matrix.Rotation(math.radians(rot[0]), 4, "X")


class Kit:
    """Collects parts, then joins them into one mesh with one material per slot and exports it for Unity."""

    def __init__(self, name):
        reset()
        self.name = name
        self.slots = []
        self.parts = []           # (obj, uv mode: "m" metres | "unit" keep 0..1 | "fit" fit the part's front face)

    # ------------------------------------------------------------------ slots
    def slot(self, name):
        if name not in self.slots:
            self.slots.append(name)
            bpy.data.materials.new(name)
        return bpy.data.materials[name]

    def _add(self, obj, slot, loc, rot, uv="m", smooth="hard"):
        obj.location = loc
        obj.rotation_euler = [math.radians(a) for a in rot]
        obj.data.materials.append(self.slot(slot))
        obj["uv"] = uv
        obj["smooth"] = smooth
        self.parts.append(obj)
        return obj

    # ------------------------------------------------------------------ primitives
    def box(self, slot, c, s, r=0.0, seg=3, rot=(0, 0, 0), bulge=0.0, taper=None, uv="m", soft=False):
        """Box of size s centred at c. r rounds the edges; bulge domes the top (cushions); taper=(sx, sy) scales the
        top face (tapered legs, trapezoid arms)."""
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        if bulge > 0:
            bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=4, use_grid_fill=True)
        for v in bm.verts:
            if taper and v.co.z > 0:
                v.co.x *= taper[0]
                v.co.y *= taper[1]
            v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2]))
            if bulge > 0 and v.co.z > s[2] / 2 - 1e-4:
                u = 1 - min(1, abs(v.co.x) / (s[0] / 2)) ** 2
                w = 1 - min(1, abs(v.co.y) / (s[1] / 2)) ** 2
                v.co.z += bulge * u * w
        obj = _link(bm, "box")
        if r > 0:
            m = obj.modifiers.new("bevel", "BEVEL")
            m.width = min(r, min(s) / 2 - 1e-4)
            m.segments = seg
            m.limit_method = "ANGLE"
            m.angle_limit = math.radians(30)
            m.harden_normals = not (soft or bulge > 0)
        return self._add(obj, slot, c, rot, uv, "soft" if (soft or bulge > 0) else "hard")

    def cyl(self, slot, c, rad, h, seg=32, r=0.0, rot=(0, 0, 0), rad2=None, caps=True, uv="m"):
        """Cylinder (or cone/frustum with rad2) standing on its axis, centre c."""
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=seg, radius1=rad,
                              radius2=rad if rad2 is None else rad2, depth=h)
        obj = _link(bm, "cyl")
        if r > 0:
            m = obj.modifiers.new("bevel", "BEVEL")
            m.width = min(r, h / 2 - 1e-4, rad - 1e-4)
            m.segments = 3
            m.limit_method = "ANGLE"
            m.angle_limit = math.radians(50)
            m.harden_normals = True
        return self._add(obj, slot, c, rot, uv, "cyl")

    def torus(self, slot, c, R, r, seg=64, rseg=12, rot=(0, 0, 0)):
        bm = bmesh.new()
        for i in range(seg):
            a = 2 * math.pi * i / seg
            for j in range(rseg):
                b = 2 * math.pi * j / rseg
                bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
        bm.verts.ensure_lookup_table()
        for i in range(seg):
            for j in range(rseg):
                a, b = i * rseg + j, i * rseg + (j + 1) % rseg
                c2, d = ((i + 1) % seg) * rseg + (j + 1) % rseg, ((i + 1) % seg) * rseg + j
                bm.faces.new((bm.verts[a], bm.verts[d], bm.verts[c2], bm.verts[b]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        return self._add(_link(bm, "torus"), slot, c, rot, "m", "soft")

    def lathe(self, slot, c, profile, seg=40, rot=(0, 0, 0)):
        """Surface of revolution about Z from a profile [(radius, z), …] bottom to top (vases, lamp bases, basins)."""
        bm = bmesh.new()
        rings = []
        for (pr, pz) in profile:
            ring = []
            for i in range(seg):
                a = 2 * math.pi * i / seg
                ring.append(bm.verts.new((pr * math.cos(a), pr * math.sin(a), pz)))
            rings.append(ring)
        for k in range(len(rings) - 1):
            for i in range(seg):
                j = (i + 1) % seg
                bm.faces.new((rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]))
        if profile[0][0] > 1e-4:
            bm.faces.new(list(reversed(rings[0])))
        if profile[-1][0] > 1e-4:
            bm.faces.new(rings[-1])
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        return self._add(_link(bm, "lathe"), slot, c, rot, "m", "soft")

    def tube(self, slot, pts, rad, seg=12, closed=False, res=12):
        """Round tube along a polyline/smooth path of points (lamp arcs, chair frames, faucets, hanger rails)."""
        cu = bpy.data.curves.new("tube", "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = rad
        cu.bevel_resolution = max(1, seg // 4 - 1)
        cu.use_fill_caps = True
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for i, p in enumerate(pts):
            sp.points[i].co = (p[0], p[1], p[2], 1)
        sp.use_cyclic_u = closed
        tmp = bpy.data.objects.new("tube", cu)
        bpy.context.scene.collection.objects.link(tmp)
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
        bpy.data.objects.remove(tmp)
        obj = bpy.data.objects.new("tube", me)
        bpy.context.scene.collection.objects.link(obj)
        return self._add(obj, slot, (0, 0, 0), (0, 0, 0), "m", "soft")

    def panel(self, slot, c, w, h, rot=(0, 0, 0), uv="unit"):
        """Flat rectangle w × h facing -Y (pictures, screens); UVs 0..1 across it."""
        bm = bmesh.new()
        uvl = bm.loops.layers.uv.new()
        vs = [bm.verts.new((x * w / 2, 0, z * h / 2)) for x, z in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        f = bm.faces.new(vs)
        for l, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
            l[uvl].uv = (u, v)
        return self._add(_link(bm, "panel"), slot, c, rot, uv, "hard")

    def disc(self, slot, c, rad, seg=64, rot=(0, 0, 0), uv="unit", thick=0.0):
        """Flat disc facing +Z (round rugs, mirrors facing -Y with rot=(90,0,0)); UVs 0..1 over the bounding square."""
        bm = bmesh.new()
        uvl = bm.loops.layers.uv.new()
        vs = [bm.verts.new((rad * math.cos(2 * math.pi * i / seg), rad * math.sin(2 * math.pi * i / seg), thick / 2))
              for i in range(seg)]
        f = bm.faces.new(vs)
        for l in f.loops:
            l[uvl].uv = (l.vert.co.x / (2 * rad) + 0.5, l.vert.co.y / (2 * rad) + 0.5)
        if thick > 0:
            ret = bmesh.ops.extrude_face_region(bm, geom=[f])
            for v in [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]:
                v.co.z -= thick
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        return self._add(_link(bm, "disc"), slot, c, rot, uv, "hard")

    def slab(self, slot, c, s, rot=(0, 0, 0), r=0.0):
        """Thin box whose TOP face gets 0..1 UVs (rugs, rectangular art on its face after rot)."""
        obj = self.box(slot, c, s, r=r, seg=2, rot=rot, uv="top")
        return obj

    def pillow(self, slot, c, s, rot=(0, 0, 0)):
        """Plump cushion: subdivided box squashed towards its rim, s = (width, thickness, height)."""
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=5, use_grid_fill=True)
        sx, sy, sz = s
        for v in bm.verts:
            x, y, z = v.co.x * 2, v.co.y * 2, v.co.z * 2
            edge = max(abs(x), abs(z))
            thick = (1 - edge ** 4) * 0.88 + 0.12
            v.co = Vector((x * sx / 2, y * sy / 2 * thick, z * sz / 2))
        obj = _link(bm, "pillow")
        obj.modifiers.new("smooth", "SUBSURF").levels = 1
        return self._add(obj, slot, c, rot, "m", "soft")

    def mesh(self, slot, verts, faces, c=(0, 0, 0), rot=(0, 0, 0), smooth="hard", uv="m"):
        bm = bmesh.new()
        vs = [bm.verts.new(v) for v in verts]
        for f in faces:
            bm.faces.new([vs[i] for i in f])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        return self._add(_link(bm, "mesh"), slot, c, rot, uv, smooth)

    # ------------------------------------------------------------------ finishing
    def _bake(self, obj):
        bpy.context.view_layer.objects.active = obj
        for o in bpy.context.selected_objects:
            o.select_set(False)
        obj.select_set(True)
        for m in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        me = obj.data
        mode, smooth = obj["uv"], obj["smooth"]
        bm = bmesh.new()
        bm.from_mesh(me)
        uvl = bm.loops.layers.uv.verify()
        if mode == "m":
            for f in bm.faces:
                n = f.normal
                ax = max(range(3), key=lambda i: abs(n[i]))
                for l in f.loops:
                    co = l.vert.co
                    if ax == 0:
                        l[uvl].uv = (co.y if n.x > 0 else -co.y, co.z)
                    elif ax == 1:
                        l[uvl].uv = (-co.x if n.y > 0 else co.x, co.z)
                    else:
                        l[uvl].uv = (co.x, co.y if n.z > 0 else -co.y)
        elif mode == "top":
            lo = Vector([min(v.co[i] for v in bm.verts) for i in range(3)])
            hi = Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
            for f in bm.faces:
                for l in f.loops:
                    co = l.vert.co
                    l[uvl].uv = ((co.x - lo.x) / max(1e-6, hi.x - lo.x), (co.y - lo.y) / max(1e-6, hi.y - lo.y))
        elif mode == "front":
            lo = Vector([min(v.co[i] for v in bm.verts) for i in range(3)])
            hi = Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
            for f in bm.faces:
                for l in f.loops:
                    co = l.vert.co
                    l[uvl].uv = ((co.x - lo.x) / max(1e-6, hi.x - lo.x), (co.z - lo.z) / max(1e-6, hi.z - lo.z))
        for f in bm.faces:
            f.smooth = smooth != "flat"
        if smooth == "cyl":        # smooth sides, flat caps
            for e in bm.edges:
                if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(40):
                    e.smooth = False
        elif smooth == "hard" and not me.has_custom_normals:
            for e in bm.edges:
                if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(40):
                    e.smooth = False
        bm.to_mesh(me)
        bm.free()

    def finish(self, entry, defaults, own=None, pivot=None, hanging=False):
        """Bake every part, join, set the pivot and export Models/<id>/<id>.fbx (+ own textures). Returns the manifest
        entry process_blender.py writes to external.json.

        defaults: slot → library/built-in material spec. own: slot → {"albedo": HxWx3 float array 0..1 or None,
        "color": (r, g, b) linear, "rough": 0..1, "metal": 0..1, "emit": (r, g, b)}.
        pivot: None (floor centre) | "back" (floor, centre of the back edge) | "wall" (centre of the back face)."""
        own = own or {}
        pivot = pivot or entry.get("pivot")
        hanging = hanging or entry.get("hanging", False)
        for o in list(self.parts):
            self._bake(o)
        bpy.ops.object.select_all(action="DESELECT")
        for o in self.parts:
            o.select_set(True)
        bpy.context.view_layer.objects.active = self.parts[0]
        if len(self.parts) > 1:
            bpy.ops.object.join()
        obj = bpy.context.view_layer.objects.active
        obj.name = obj.data.name = entry["id"]
        # slot order = first use; drop unused material slots
        size = self._pivot(obj, pivot, hanging)
        out_dir = os.path.join(OUT, "Models", entry["id"])
        os.makedirs(out_dir, exist_ok=True)
        for f in os.listdir(out_dir):
            if f.startswith(entry["id"] + "_") and not f.endswith(".meta"):
                os.remove(os.path.join(out_dir, f))
        _export_fbx(obj, os.path.join(out_dir, entry["id"] + ".fbx"))
        slots = []
        for s in obj.material_slots:
            name = s.material.name
            if name in own:
                spec = own[name]
                d = {"slot": name, "textures": {}, "uvMeters": False,
                     "baseColor": list(spec.get("color", (1, 1, 1))) + [1],
                     "roughness": spec.get("rough", 0.6), "metallic": spec.get("metal", 0.0),
                     "emissive": list(spec.get("emit", (0, 0, 0)))}
                if spec.get("albedo") is not None:
                    fn = f"{entry['id']}_{name}_albedo.jpg"
                    save_image(spec["albedo"], os.path.join(out_dir, fn))
                    d["textures"]["albedo"] = fn
                slots.append(d)
            else:
                slots.append({"slot": name, "default": defaults.get(name), "uvMeters": True})
        tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
        return {
            "id": entry["id"], "name": entry["name"], "category": entry["category"], "source": "blender:" + entry["blender"],
            "folder": f"Models/{entry['id']}", "fbx": entry["id"] + ".fbx", "size": size, "triangles": tris,
            "hanging": hanging, "slots": slots,
        }

    @staticmethod
    def _pivot(obj, pivot, hanging):
        pts = [v.co for v in obj.data.vertices]
        lo = Vector([min(p[i] for p in pts) for i in range(3)])
        hi = Vector([max(p[i] for p in pts) for i in range(3)])
        z = hi.z if hanging else (lo.z + hi.z) / 2 if pivot == "wall" else lo.z
        y = hi.y if pivot in ("back", "wall") else (lo.y + hi.y) / 2
        obj.data.transform(Matrix.Translation(-Vector(((lo.x + hi.x) / 2, y, z))))
        obj.location = (0, 0, 0)
        return [round(hi.x - lo.x, 3), round(hi.y - lo.y, 3), round(hi.z - lo.z, 3)]


def _export_fbx(obj, path):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"}, apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_UNITS", bake_space_transform=True, axis_forward="-Z", axis_up="Y",
                             mesh_smooth_type="OFF", use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False,
                             path_mode="STRIP", embed_textures=False)


# ---------------------------------------------------------------------- images
def save_image(px, path, quality=90):
    """px: H×W×3 (or ×4) float array 0..1, row 0 = top."""
    h, w = px.shape[:2]
    rgba = np.ones((h, w, 4), np.float32)
    rgba[..., :px.shape[2]] = np.clip(px, 0, 1)
    img = bpy.data.images.new("tmp", w, h, alpha=False)
    img.pixels.foreach_set(rgba[::-1].ravel())
    img.filepath_raw = path
    img.file_format = "JPEG"
    bpy.context.scene.render.image_settings.quality = quality
    img.save()
    bpy.data.images.remove(img)
