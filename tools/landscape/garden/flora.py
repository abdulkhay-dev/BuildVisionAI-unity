"""Procedural perennials missing from Poly Haven: salvia/lavender spikes, lupins, shasta daisies, phlox and
hostas. Each builder returns one clump mesh object (origin at the ground centre); colours vary per floret
through the `col` point attribute read by the materials."""
import math
import random

import bpy
import bmesh
from mathutils import Matrix, Vector

from .util import collection

# 1.0 = full clump (renders, LOD0 in the app); lower values thin stems/florets/leaves out for distant LODs
DETAIL = 1.0


def _n(k):
    return max(1, int(round(k * DETAIL)))


# ---------------------------------------------------------------- materials

def _attr_material(name, rough=0.55, sss=0.25, translucent=0.25):
    """Principled + translucency, base colour from the `col` attribute."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    out = nt.nodes["Material Output"]
    bsdf = nt.nodes["Principled BSDF"]
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "col"
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Specular IOR Level"].default_value = 0.25
    bsdf.inputs["Subsurface Weight"].default_value = sss
    bsdf.inputs["Subsurface Radius"].default_value = (0.4, 0.4, 0.2)
    bsdf.inputs["Subsurface Scale"].default_value = 0.005
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Subsurface Color"] if "Subsurface Color" in bsdf.inputs
                 else bsdf.inputs["Base Color"])
    trans = nt.nodes.new("ShaderNodeBsdfTranslucent")
    nt.links.new(attr.outputs["Color"], trans.inputs["Color"])
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = translucent
    nt.links.new(bsdf.outputs["BSDF"], mix.inputs[1])
    nt.links.new(trans.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return mat


def materials():
    return {"leaf": _attr_material("M_FloraLeaf", rough=0.5, translucent=0.3),
            "petal": _attr_material("M_FloraPetal", rough=0.45, translucent=0.35),
            "stem": _attr_material("M_FloraStem", rough=0.6, translucent=0.15)}


# ---------------------------------------------------------------- mesh builder

class Clump:
    def __init__(self, name, seed):
        self.name = name
        self.rnd = random.Random(seed)
        self.bm = bmesh.new()
        self.col = self.bm.verts.layers.float_color.new("col")
        self.mats = materials()
        self.order = ["leaf", "petal", "stem"]

    def _face(self, verts, color, mat):
        vs = [self.bm.verts.new(v) for v in verts]
        for v in vs:
            v[self.col] = (*color, 1.0)
        f = self.bm.faces.new(vs)
        f.material_index = self.order.index(mat)
        f.smooth = True
        return vs

    def strip(self, pts, widths, normal_side, color, mat, color_tip=None):
        """Ribbon along `pts` (list of Vector); width per point; `normal_side` = the ribbon's side axis."""
        rows = []
        for i, (p, w) in enumerate(zip(pts, widths)):
            side = normal_side[i] if isinstance(normal_side, list) else normal_side
            rows.append((p - side * w / 2, p + side * w / 2))
        n = len(rows)
        for i in range(n - 1):
            t = i / max(1, n - 2)
            c = color if color_tip is None else tuple(a + (b - a) * t for a, b in zip(color, color_tip))
            (a0, a1), (b0, b1) = rows[i], rows[i + 1]
            if (b1 - b0).length < 1e-5:
                self._face([a0, a1, b0], c, mat)
            else:
                self._face([a0, a1, b1, b0], c, mat)

    def tube(self, pts, radius, color, mat, sides=4):
        rings = []
        for i, p in enumerate(pts):
            d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            q = d.to_track_quat("Z", "Y")
            r = radius * (1.0 - 0.6 * i / max(1, len(pts) - 1))
            rings.append([p + q @ Vector((math.cos(a) * r, math.sin(a) * r, 0))
                          for a in [k * 2 * math.pi / sides for k in range(sides)]])
        for i in range(len(rings) - 1):
            for k in range(sides):
                self._face([rings[i][k], rings[i][(k + 1) % sides], rings[i + 1][(k + 1) % sides],
                            rings[i + 1][k]], color, mat)

    def leaf(self, base, direction, length, width, droop, color, segs=5, color_tip=None):
        """A lanceolate leaf from `base` along `direction` (horizontal-ish), bending down by `droop`."""
        d = direction.normalized()
        side = d.cross(Vector((0, 0, 1)))
        if side.length < 1e-4:
            side = Vector((1, 0, 0))
        side.normalize()
        pts, ws = [], []
        for i in range(segs + 1):
            t = i / segs
            pts.append(base + d * length * t + Vector((0, 0, -droop * t * t)))
            ws.append(width * math.sin(math.pi * min(0.98, t * 0.9 + 0.05)) * (1.0 if t < 1 else 0.0))
        # keep a small crease: tilt the side slightly upwards
        self.strip(pts, ws, side, color, mat="leaf", color_tip=color_tip)

    def stem(self, base, height, lean, bend=0.15, segs=6):
        """Returns the points of a gently curved stem."""
        az = self.rnd.uniform(0, 2 * math.pi)
        dx, dy = math.cos(az), math.sin(az)
        pts = []
        for i in range(segs + 1):
            t = i / segs
            off = lean * t + bend * t * t
            pts.append(base + Vector((dx * off, dy * off, height * t)))
        return pts

    def build(self, col):
        me = bpy.data.meshes.new(self.name)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        for key in self.order:
            me.materials.append(self.mats[key])
        obj = bpy.data.objects.new(self.name, me)
        col.objects.link(obj)
        return obj


def _jitter(rnd, color, amount=0.08):
    return tuple(max(0.0, min(1.0, c * (1.0 + rnd.uniform(-amount, amount)))) for c in color)


GREEN = (0.10, 0.22, 0.05)
GREEN_DARK = (0.05, 0.13, 0.03)
GREEN_GREY = (0.16, 0.22, 0.12)


def _basal_leaves(c, count, length, width, color, radius=0.06, up=0.25):
    for _ in range(count):
        az = c.rnd.uniform(0, 2 * math.pi)
        d = Vector((math.cos(az), math.sin(az), c.rnd.uniform(up * 0.5, up)))
        base = Vector((math.cos(az) * radius * c.rnd.random(), math.sin(az) * radius * c.rnd.random(), 0.01))
        c.leaf(base, d, length * c.rnd.uniform(0.7, 1.1), width * c.rnd.uniform(0.8, 1.2),
               droop=length * c.rnd.uniform(0.2, 0.45), color=_jitter(c.rnd, color),
               color_tip=_jitter(c.rnd, tuple(x * 1.25 for x in color)))


# ---------------------------------------------------------------- species

def spike_plant(name, seed, col, stems=(18, 28), height=(0.38, 0.6), flower=(0.30, 0.18, 0.62), spike=0.45,
                floret=0.018, leaves=24, leaf_len=0.16, leaf_color=GREEN_GREY, spread=0.14):
    """Salvia / lavender / lupin style: many stems whose upper part carries florets."""
    c = Clump(name, seed)
    _basal_leaves(c, _n(leaves), leaf_len, leaf_len * 0.28 / DETAIL ** 0.5, leaf_color, radius=spread * 0.6)
    for _ in range(_n(c.rnd.randint(*stems))):
        base = Vector((c.rnd.gauss(0, spread * 0.5), c.rnd.gauss(0, spread * 0.5), 0.0))
        h = c.rnd.uniform(*height)
        pts = c.stem(base, h, lean=c.rnd.uniform(0.02, spread), bend=c.rnd.uniform(0.0, 0.05))
        c.tube(pts, 0.004, _jitter(c.rnd, GREEN), "stem", sides=3)
        # florets on the upper part of the stem, whorls getting smaller towards the tip
        tint = _jitter(c.rnd, flower, 0.18)
        floret_d = floret / DETAIL ** 0.5
        n = max(2, int(h * spike / (floret_d * 0.9)))
        top = pts[-1]
        for k in range(n):
            t = k / max(1, n - 1)
            p = pts[0].lerp(top, 1.0 - spike + spike * t)
            size = floret_d * (1.1 - 0.6 * t)
            for w in range(3 if DETAIL >= 0.75 else 2):
                az = c.rnd.uniform(0, 2 * math.pi)
                o = Vector((math.cos(az), math.sin(az), 0.3)) * size
                ctr = p + o
                shade = tuple(x * c.rnd.uniform(0.75, 1.2) for x in tint)
                # a small bent diamond facing outwards
                side = Vector((-math.sin(az), math.cos(az), 0)) * size * 0.55
                up = Vector((0, 0, size * 0.9))
                c._face([ctr - up * 0.3, ctr + side, ctr + up + o * 0.4, ctr - side], shade, "petal")
    return c.build(col)


def daisy(name, seed, col, flowers=(10, 16), height=(0.35, 0.58), petal=0.035, petals=18,
          petal_color=(0.9, 0.9, 0.86), centre=(0.75, 0.5, 0.04), leaves=30, spread=0.13):
    """Shasta daisy / leucanthemum clump."""
    c = Clump(name, seed)
    _basal_leaves(c, _n(leaves), 0.15, 0.035 / DETAIL ** 0.5, GREEN_DARK, radius=spread * 0.6, up=0.45)
    petals = petals if DETAIL >= 0.75 else 9
    for _ in range(_n(c.rnd.randint(*flowers))):
        base = Vector((c.rnd.gauss(0, spread * 0.4), c.rnd.gauss(0, spread * 0.4), 0.0))
        h = c.rnd.uniform(*height)
        pts = c.stem(base, h, lean=c.rnd.uniform(0.03, spread * 1.2), bend=c.rnd.uniform(0.0, 0.05))
        c.tube(pts, 0.0035, _jitter(c.rnd, GREEN), "stem", sides=3)
        top = pts[-1]
        facing = (pts[-1] - pts[-2]).normalized().lerp(Vector((0, 0, 1)), 0.5).normalized()
        q = facing.to_track_quat("Z", "Y")
        r = petal * c.rnd.uniform(0.85, 1.15)
        for k in range(petals):
            a = (k + c.rnd.uniform(-0.2, 0.2)) * 2 * math.pi / petals
            d = Vector((math.cos(a), math.sin(a), 0))
            s = Vector((-math.sin(a), math.cos(a), 0))
            cup = Vector((0, 0, 0.12))
            wide = 18.0 / petals
            p0 = d * r * 0.18
            p1 = d * r * 0.6 + s * r * 0.11 * wide + cup * r
            p2 = d * r * 1.0 + cup * r * 0.3 - Vector((0, 0, r * 0.15))
            p3 = d * r * 0.6 - s * r * 0.11 * wide + cup * r
            c._face([top + q @ p0, top + q @ p1, top + q @ p2, top + q @ p3],
                    _jitter(c.rnd, petal_color, 0.04), "petal")
        # domed centre
        ring = [top + q @ Vector((math.cos(a) * r * 0.22, math.sin(a) * r * 0.22, r * 0.06))
                for a in [k * 2 * math.pi / 8 for k in range(8)]]
        apex = top + q @ Vector((0, 0, r * 0.2))
        for k in range(8):
            c._face([ring[k], ring[(k + 1) % 8], apex], _jitter(c.rnd, centre, 0.1), "petal")
    return c.build(col)


def phlox(name, seed, col, heads=(7, 11), height=(0.3, 0.5), flower=(0.85, 0.25, 0.55), leaves=40, spread=0.18):
    """Garden phlox: stems ending in domed clusters of five-petalled flowers."""
    c = Clump(name, seed)
    tint = _jitter(c.rnd, flower, 0.15)
    for _ in range(_n(c.rnd.randint(*heads))):
        base = Vector((c.rnd.gauss(0, spread * 0.4), c.rnd.gauss(0, spread * 0.4), 0.0))
        h = c.rnd.uniform(*height)
        pts = c.stem(base, h, lean=c.rnd.uniform(0.02, spread), bend=0.02)
        c.tube(pts, 0.004, _jitter(c.rnd, GREEN), "stem", sides=3)
        # leaves in pairs along the stem
        for k in range(1, 1 + _n(4)):
            p = pts[0].lerp(pts[-1], k / 5.5)
            az = c.rnd.uniform(0, 2 * math.pi)
            for sgn in (1, -1):
                d = Vector((math.cos(az) * sgn, math.sin(az) * sgn, 0.25))
                c.leaf(p, d, 0.07, 0.022, 0.02, _jitter(c.rnd, GREEN))
        top = pts[-1]
        for _k in range(_n(c.rnd.randint(16, 26))):
            # points on a flattened dome
            u, v = c.rnd.uniform(0, 2 * math.pi), c.rnd.uniform(0, 0.9)
            rr = 0.06 * math.sqrt(v)
            p = top + Vector((math.cos(u) * rr, math.sin(u) * rr, 0.035 * (1 - v)))
            n = (p - (top - Vector((0, 0, 0.05)))).normalized()
            q = n.to_track_quat("Z", "Y")
            fr = 0.011 * c.rnd.uniform(0.85, 1.15) / DETAIL ** 0.5
            shade = tuple(x * c.rnd.uniform(0.85, 1.12) for x in tint)
            ctr = p
            rim = [p + q @ Vector((math.cos(a) * fr, math.sin(a) * fr, 0)) for a in
                   [k * 2 * math.pi / 5 + c.rnd.uniform(0, 1) for k in range(5)]]
            for k in range(5):
                c._face([ctr, rim[k], rim[(k + 1) % 5]], shade, "petal")
    return c.build(col)


def hosta(name, seed, col, leaves=(14, 22), size=0.26, color=(0.12, 0.25, 0.08)):
    """Broad-leaved rosette (hosta / bergenia) for the shady stream banks."""
    c = Clump(name, seed)
    for _ in range(_n(c.rnd.randint(*leaves))):
        az = c.rnd.uniform(0, 2 * math.pi)
        up = c.rnd.uniform(0.5, 1.0)
        d = Vector((math.cos(az), math.sin(az), up))
        L = size * c.rnd.uniform(0.75, 1.1)
        # petiole then a wide blade
        base = Vector((0, 0, 0.0))
        c.leaf(base + d.normalized() * L * 0.35, Vector((d.x, d.y, up * 0.4)), L, L * 0.55, droop=L * 0.35,
               color=_jitter(c.rnd, color, 0.12), segs=6 if DETAIL >= 0.75 else 3,
               color_tip=_jitter(c.rnd, tuple(x * 1.2 for x in color), 0.1))
        c.tube([base, base + d.normalized() * L * 0.36], 0.004, _jitter(c.rnd, GREEN), "stem", sides=3)
    return c.build(col)


def build_all(kit):
    """Adds the procedural flora groups to the kit."""
    tmp = collection("_flora_tmp")
    groups = {
        "flower_salvia": [spike_plant(f"salvia_{i}", 100 + i, tmp, flower=(0.26, 0.12, 0.62)) for i in range(4)],
        "flower_lavender": [spike_plant(f"lavender_{i}", 200 + i, tmp, flower=(0.42, 0.33, 0.78), height=(0.3, 0.45),
                                        spike=0.3, floret=0.014, stems=(30, 44), leaf_color=(0.2, 0.26, 0.17),
                                        spread=0.2) for i in range(3)],
        "flower_lupin": [spike_plant(f"lupin_{i}", 300 + i, tmp, stems=(5, 8), height=(0.7, 1.0), spike=0.42,
                                     floret=0.028, leaves=16, leaf_len=0.2, spread=0.12,
                                     flower=[(0.32, 0.22, 0.75), (0.75, 0.3, 0.6), (0.5, 0.25, 0.8)][i % 3])
                         for i in range(3)],
        "flower_daisy": [daisy(f"daisy_{i}", 400 + i, tmp) for i in range(4)],
        "flower_pink": [phlox(f"phlox_{i}", 500 + i, tmp, flower=[(0.9, 0.3, 0.6), (0.95, 0.5, 0.72),
                                                                  (0.75, 0.2, 0.55)][i % 3]) for i in range(3)],
        "hosta": [hosta(f"hosta_{i}", 600 + i, tmp) for i in range(3)],
    }
    for name, objs in groups.items():
        kit.add_group(name, objs)
    bpy.data.collections.remove(tmp)
