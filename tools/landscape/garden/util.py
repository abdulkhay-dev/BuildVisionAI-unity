"""Shared helpers: collections, mesh creation, materials, value noise, polylines."""
import math
import os
import random

import bpy
import bmesh
from mathutils import Vector, kdtree

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PH_BLEND = os.path.join(ROOT, ".cache", "polyhaven", "blend")
PH_TEX = os.path.join(ROOT, ".cache", "polyhaven")


# ---------------------------------------------------------------- collections

def collection(name, parent=None, hidden=False):
    """Returns the collection `name`, created under `parent` (scene root by default)."""
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    if hidden:
        exclude(col)
    return col


def exclude(col):
    """Excludes `col` from the view layer (kit masters: instanced, never rendered directly)."""
    def walk(lc):
        if lc.collection == col:
            lc.exclude = True
            return True
        return any(walk(c) for c in lc.children)
    walk(bpy.context.view_layer.layer_collection)


def link(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


# ---------------------------------------------------------------- meshes

def mesh_object(name, verts, faces, col, uvs=None, smooth=True, mats=None, mat_index=None):
    """Creates a mesh object from vertex/face lists; `uvs` is one (u, v) per face corner in face order."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    if uvs is not None:
        layer = me.uv_layers.new(name="UVMap")
        for i, uv in enumerate(uvs):
            layer.data[i].uv = uv
    for m in mats or []:
        me.materials.append(m)
    if mat_index is not None:
        me.polygons.foreach_set("material_index", mat_index)
    me.polygons.foreach_set("use_smooth", [smooth] * len(me.polygons))
    me.validate()
    obj = bpy.data.objects.new(name, me)
    col.objects.link(obj)
    return obj


def join_bmesh(bm, other_mesh, matrix, mat_offset=0):
    """Appends `other_mesh` transformed by `matrix` into `bm`."""
    tmp = bmesh.new()
    tmp.from_mesh(other_mesh)
    bmesh.ops.transform(tmp, matrix=matrix, verts=tmp.verts)
    for f in tmp.faces:
        f.material_index += mat_offset
    me = bpy.data.meshes.new("_tmp")
    tmp.to_mesh(me)
    tmp.free()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)


def point_cloud(name, points, col, attrs):
    """Vertex-only mesh used as instancing points; `attrs` = {name: (type, values)} per vertex."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(p) for p in points], [], [])
    for key, (kind, values) in attrs.items():
        a = me.attributes.new(key, kind, "POINT")
        field = "vector" if kind == "FLOAT_VECTOR" else "value"
        flat = [c for v in values for c in v] if kind == "FLOAT_VECTOR" else list(values)
        a.data.foreach_set(field, flat)
    obj = bpy.data.objects.new(name, me)
    col.objects.link(obj)
    return obj


# ---------------------------------------------------------------- materials

def image(path, non_color=False):
    img = bpy.data.images.load(path, check_existing=True)
    if non_color:
        img.colorspace_settings.name = "Non-Color"
    return img


def ph_maps(source, res="1k"):
    """Diffuse/normal/ARM paths of a cached Poly Haven material (tools/assets pipeline)."""
    base = os.path.join(PH_TEX, source)
    maps = {k: os.path.join(base, f"{k}_{res}.jpg") for k in ("diff", "nor_gl", "arm", "rough")}
    return {k: v for k, v in maps.items() if os.path.exists(v)}


def pbr_material(name, source, scale=1.0, tint=None, bump=1.0, rough_mul=1.0, world_uv=False):
    """Principled material from a cached Poly Haven texture set. `scale` = texture repeats per metre when
    `world_uv` (object-space projection from above), otherwise a UV multiplier."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    maps = ph_maps(source)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    if world_uv:
        coord = nt.nodes.new("ShaderNodeTexCoord")
        src = coord.outputs["Object"]
    else:
        coord = nt.nodes.new("ShaderNodeTexCoord")
        src = coord.outputs["UV"]
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (scale, scale, scale)
    nt.links.new(src, mapping.inputs["Vector"])
    vec = mapping.outputs["Vector"]

    def tex(path, non_color):
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = image(path, non_color)
        nt.links.new(vec, t.inputs["Vector"])
        return t

    if "diff" in maps:
        col = tex(maps["diff"], False).outputs["Color"]
        if tint is not None:
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.blend_type = "MULTIPLY"
            mix.inputs["Factor"].default_value = 1.0
            nt.links.new(col, mix.inputs["A"])
            mix.inputs["B"].default_value = (*tint, 1.0)
            col = mix.outputs["Result"]
        nt.links.new(col, bsdf.inputs["Base Color"])
    if "arm" in maps:
        sep = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(tex(maps["arm"], True).outputs["Color"], sep.inputs["Color"])
        rough = sep.outputs["Green"]
        if rough_mul != 1.0:
            m = nt.nodes.new("ShaderNodeMath")
            m.operation = "MULTIPLY"
            m.inputs[1].default_value = rough_mul
            nt.links.new(rough, m.inputs[0])
            rough = m.outputs[0]
        nt.links.new(rough, bsdf.inputs["Roughness"])
        nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])
    elif "rough" in maps:
        nt.links.new(tex(maps["rough"], True).outputs["Color"], bsdf.inputs["Roughness"])
    if "nor_gl" in maps:
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = bump
        nt.links.new(tex(maps["nor_gl"], True).outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def flat_material(name, color, rough=0.6, metal=0.0, emission=None, strength=0.0, sss=0.0, alpha=1.0,
                  transmission=0.0):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Alpha"].default_value = alpha
    b.inputs["Transmission Weight"].default_value = transmission
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (0.3, 0.6, 0.2)
        b.inputs["Subsurface Scale"].default_value = 0.02
    if emission is not None:
        b.inputs["Emission Color"].default_value = (*emission, 1.0)
        b.inputs["Emission Strength"].default_value = strength
    mat.diffuse_color = (*color, 1.0)
    return mat


# ---------------------------------------------------------------- noise

class ValueNoise:
    """Deterministic smooth 2D value noise (fbm), independent of Blender's noise module."""

    def __init__(self, seed):
        rnd = random.Random(seed)
        self.perm = list(range(256))
        rnd.shuffle(self.perm)
        self.perm += self.perm
        self.vals = [rnd.random() * 2 - 1 for _ in range(256)]

    def _lattice(self, ix, iy):
        return self.vals[self.perm[(self.perm[ix & 255] + iy) & 255]]

    def noise(self, x, y):
        ix, iy = math.floor(x), math.floor(y)
        fx, fy = x - ix, y - iy
        u, v = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        a, b = self._lattice(ix, iy), self._lattice(ix + 1, iy)
        c, d = self._lattice(ix, iy + 1), self._lattice(ix + 1, iy + 1)
        return (a + (b - a) * u) + ((c + (d - c) * u) - (a + (b - a) * u)) * v

    def fbm(self, x, y, octaves=4, lac=2.0, gain=0.5):
        amp, freq, total, norm = 1.0, 1.0, 0.0, 0.0
        for _ in range(octaves):
            total += amp * self.noise(x * freq, y * freq)
            norm += amp
            amp *= gain
            freq *= lac
        return total / norm


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


# ---------------------------------------------------------------- polylines

class Polyline:
    """Densely resampled 2D polyline (Catmull-Rom through the control points) with a KD-tree for
    nearest-point queries: returns (distance, arclength, point, tangent)."""

    def __init__(self, ctrl, step=0.1):
        pts = [Vector((p[0], p[1], 0.0)) for p in ctrl]
        dense = []
        for i in range(len(pts) - 1):
            p0 = pts[max(i - 1, 0)]
            p1, p2 = pts[i], pts[i + 1]
            p3 = pts[min(i + 2, len(pts) - 1)]
            n = max(2, int((p2 - p1).length / step))
            for k in range(n):
                t = k / n
                t2, t3 = t * t, t * t * t
                dense.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                                    + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
        dense.append(pts[-1])
        self.pts = dense
        self.s = [0.0]
        for i in range(1, len(dense)):
            self.s.append(self.s[-1] + (dense[i] - dense[i - 1]).length)
        self.length = self.s[-1]
        self.kd = kdtree.KDTree(len(dense))
        for i, p in enumerate(dense):
            self.kd.insert(p, i)
        self.kd.balance()

    def tangent(self, i):
        a = self.pts[max(i - 1, 0)]
        b = self.pts[min(i + 1, len(self.pts) - 1)]
        return (b - a).normalized()

    def nearest(self, x, y):
        _, i, d = self.kd.find((x, y, 0.0))
        return d, self.s[i], self.pts[i], self.tangent(i)

    def at(self, s):
        """Point and tangent at arclength `s`."""
        s = min(max(s, 0.0), self.length)
        lo, hi = 0, len(self.s) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.s[mid] <= s:
                lo = mid
            else:
                hi = mid
        seg = self.s[hi] - self.s[lo]
        t = 0.0 if seg == 0 else (s - self.s[lo]) / seg
        return self.pts[lo].lerp(self.pts[hi], t), self.tangent(lo)
