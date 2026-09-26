"""Hand-made props: arched timber bridge, stone lantern (tōrō), garden post lantern, stepping stones and the
board fence. Each builder makes one object with its origin at the ground centre."""
import math
import random

import bpy
import bmesh
from mathutils import Matrix, Vector

from . import layout as L
from .util import ValueNoise, collection, flat_material, pbr_material


def _box(bm, center, size, rot=None, mat=0):
    m = Matrix.Translation(center)
    if rot is not None:
        m = m @ rot
    m = m @ Matrix.Diagonal((size[0], size[1], size[2], 1.0))
    geom = bmesh.ops.create_cube(bm, size=1.0, matrix=m)
    for f in {f for v in geom["verts"] for f in v.link_faces}:
        f.material_index = mat
    return geom


def _cyl(bm, center, r1, r2, depth, segs=8, mat=0, rot=None):
    m = Matrix.Translation(center)
    if rot is not None:
        m = m @ rot
    geom = bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r1, radius2=r2, depth=depth, matrix=m)
    for f in {f for v in geom["verts"] for f in v.link_faces}:
        f.material_index = mat
    return geom


def _finish(bm, name, col, mats, smooth=False, bevel=None):
    if bevel:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=1, affect="EDGES", clamp_overlap=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("use_smooth", [smooth] * len(me.polygons))
    obj = bpy.data.objects.new(name, me)
    col.objects.link(obj)
    # box-projected UVs so the wood/stone textures are not stretched
    uv = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        n = poly.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (co.y, co.z) if ax == 0 else ((co.x, co.z) if ax == 1 else (co.x, co.y))
    return obj


# ---------------------------------------------------------------- materials

def wood():
    return pbr_material("M_BridgeWood", "brown_planks_05", scale=0.8, tint=(0.75, 0.6, 0.48))


def stone():
    return pbr_material("M_LanternStone", "granite_tile", scale=0.6,
                        tint=(0.72, 0.72, 0.68))


def slab():
    return pbr_material("M_StepStone", "grey_stone_path", scale=0.7, tint=(0.9, 0.88, 0.84))


def metal():
    return flat_material("M_LampMetal", (0.025, 0.025, 0.024), rough=0.45, metal=0.9)


def glow():
    return flat_material("M_LampGlow", (1.0, 0.8, 0.55), rough=0.3, emission=(1.0, 0.62, 0.3), strength=12.0,
                         transmission=0.3)


def fence_wood():
    return pbr_material("M_FenceWood", "brown_planks_05", scale=0.9,
                        tint=(0.55, 0.42, 0.32))


# ---------------------------------------------------------------- bridge

def bridge(col):
    """Arched plank bridge from BRIDGE.a to BRIDGE.b (object local X along the span)."""
    a, b = Vector((*L.BRIDGE["a"], 0)), Vector((*L.BRIDGE["b"], 0))
    span = (b - a).length
    width, rise = L.BRIDGE["width"], L.BRIDGE["rise"]
    bm = bmesh.new()

    def arch(x):   # height of the deck top at x in [-span/2, span/2]
        return rise * (1 - (2 * x / span) ** 2)

    # deck planks across the span
    n = int(span / 0.16)
    for i in range(n):
        x = -span / 2 + (i + 0.5) * span / n
        z = arch(x)
        slope = -8 * rise * x / (span * span)
        rot = Matrix.Rotation(math.atan(slope), 4, "Y")
        _box(bm, Vector((x, 0, z - 0.03)), (span / n * 0.9, width, 0.05), rot)
    # two curved stringers
    for side in (-1, 1):
        for i in range(24):
            x0 = -span / 2 + i * span / 24
            x1 = x0 + span / 24
            xm = (x0 + x1) / 2
            slope = math.atan(-8 * rise * xm / (span * span))
            _box(bm, Vector((xm, side * (width / 2 - 0.08), arch(xm) - 0.14)), (span / 24 * 1.02, 0.1, 0.2),
                 Matrix.Rotation(slope, 4, "Y"))
    # posts and handrails
    posts = 6
    for side in (-1, 1):
        y = side * (width / 2 + 0.02)
        for i in range(posts + 1):
            x = -span / 2 + 0.15 + i * (span - 0.3) / posts
            _box(bm, Vector((x, y, arch(x) + 0.42)), (0.09, 0.09, 0.9))
        for rail_h, th in ((0.86, 0.07), (0.45, 0.045)):
            for i in range(24):
                x0 = -span / 2 + 0.15 + i * (span - 0.3) / 24
                x1 = x0 + (span - 0.3) / 24
                xm = (x0 + x1) / 2
                slope = math.atan(-8 * rise * xm / (span * span))
                _box(bm, Vector((xm, y, arch(xm) + rail_h)), ((x1 - x0) * 1.03, th + 0.02, th),
                     Matrix.Rotation(slope, 4, "Y"))
    obj = _finish(bm, "Bridge", col, [wood()], bevel=0.008)
    mid = (a + b) / 2
    obj.location = mid
    obj.rotation_euler = (0, 0, math.atan2(b.y - a.y, b.x - a.x))
    return obj


# ---------------------------------------------------------------- lanterns

def stone_lantern(col, name="StoneLantern"):
    """Kasuga-style tōrō, ~1.3 m."""
    bm = bmesh.new()
    _cyl(bm, Vector((0, 0, 0.06)), 0.3, 0.26, 0.12, segs=6)                 # base
    _cyl(bm, Vector((0, 0, 0.4)), 0.09, 0.08, 0.56, segs=10)               # pillar
    _cyl(bm, Vector((0, 0, 0.72)), 0.2, 0.24, 0.1, segs=6)                 # platform
    # light box: four posts around a glowing core
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        _box(bm, Vector((math.cos(a) * 0.14, math.sin(a) * 0.14, 0.88)), (0.07, 0.07, 0.22),
             Matrix.Rotation(a, 4, "Z"))
    _box(bm, Vector((0, 0, 0.88)), (0.16, 0.16, 0.2), mat=1)
    _cyl(bm, Vector((0, 0, 1.04)), 0.36, 0.1, 0.16, segs=6)                # roof
    _cyl(bm, Vector((0, 0, 1.0)), 0.36, 0.36, 0.04, segs=6)                # roof rim
    _cyl(bm, Vector((0, 0, 1.17)), 0.05, 0.02, 0.12, segs=8)               # finial
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.045, matrix=Matrix.Translation((0, 0, 1.26)))
    return _finish(bm, name, col, [stone(), glow()], bevel=0.01)


def garden_lamp(col, name="GardenLamp"):
    """Black post lantern with a warm glass box, ~1.1 m."""
    bm = bmesh.new()
    _box(bm, Vector((0, 0, 0.05)), (0.18, 0.18, 0.1))
    _box(bm, Vector((0, 0, 0.5)), (0.07, 0.07, 0.85))
    _box(bm, Vector((0, 0, 0.94)), (0.2, 0.2, 0.03))
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        _box(bm, Vector((math.cos(a) * 0.12, math.sin(a) * 0.12, 1.06)), (0.02, 0.02, 0.22))
    _box(bm, Vector((0, 0, 1.06)), (0.15, 0.15, 0.2), mat=1)
    _cyl(bm, Vector((0, 0, 1.22)), 0.16, 0.03, 0.1, segs=4, rot=Matrix.Rotation(math.pi / 4, 4, "Z"))
    return _finish(bm, name, col, [metal(), glow()], bevel=0.004)


def lamp_light(obj, height, power, radius=0.06, color=(1.0, 0.68, 0.38)):
    light = bpy.data.lights.new(obj.name + "_light", "POINT")
    light.energy = power
    light.color = color
    light.shadow_soft_size = radius
    lo = bpy.data.objects.new(obj.name + "_light", light)
    obj.users_collection[0].objects.link(lo)
    lo.parent = obj
    lo.location = (0, 0, height)
    return lo


# ---------------------------------------------------------------- stepping stones

def stepping_stones(site, col):
    """Irregular flat slabs along every path, set flush with the ground."""
    rnd = random.Random(L.SEED + 11)
    noise = ValueNoise(L.SEED + 12)
    bm = bmesh.new()
    for pid, (poly, width) in site.paths.items():
        s = 0.3
        while s < poly.length - 0.2:
            p, t = poly.at(s)
            n = Vector((-t.y, t.x, 0))
            size = rnd.uniform(0.55, 0.8) * (width / 1.1) ** 0.5
            # two slabs side by side on the wide main path now and then
            offsets = [rnd.uniform(-0.12, 0.12)]
            if width > 1.0 and rnd.random() < 0.35:
                offsets = [-0.28, 0.3]
                size *= 0.72
            for off in offsets:
                c = p + n * off * width
                if not site.in_plot(c.x, c.y, -8):
                    continue
                d, _, hw, _ = site.stream_at(c.x, c.y)
                if d < hw + 0.3:
                    continue
                z = site.height(c.x, c.y)
                seg = 14
                rot = rnd.uniform(0, math.pi)
                sx, sy = size * rnd.uniform(0.85, 1.15), size * rnd.uniform(0.65, 0.9)
                top, bot = [], []
                for k in range(seg):
                    a = 2 * math.pi * k / seg
                    r = 1.0 + 0.16 * noise.noise(math.cos(a) * 2 + s * 3, math.sin(a) * 2 + off * 7)
                    lx, ly = math.cos(a) * sx / 2 * r, math.sin(a) * sy / 2 * r
                    x = c.x + lx * math.cos(rot) - ly * math.sin(rot)
                    y = c.y + lx * math.sin(rot) + ly * math.cos(rot)
                    zz = site.height(x, y)
                    top.append(bm.verts.new((x, y, max(z, zz) + 0.035 + rnd.uniform(-0.006, 0.006))))
                    bot.append(bm.verts.new((x, y, min(z, zz) - 0.08)))
                ctr = bm.verts.new((c.x, c.y, z + 0.04))
                for k in range(seg):
                    bm.faces.new((ctr, top[k], top[(k + 1) % seg]))
                    bm.faces.new((top[k], bot[k], bot[(k + 1) % seg], top[(k + 1) % seg]))
            s += size * rnd.uniform(1.05, 1.25)
    bmesh.ops.bevel(bm, geom=[e for e in bm.edges if len(e.link_faces) == 2 and
                              e.calc_face_angle(0) > 0.6], offset=0.015, segments=2, clamp_overlap=True)
    return _finish(bm, "SteppingStones", col, [slab()], smooth=False)


# ---------------------------------------------------------------- fence

def fence(site, col):
    """Vertical board fence along the east and north plot lines (and the west behind the house)."""
    x0, y0, x1, y1 = L.PLOT
    runs = [((x1, y0 + 4), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, 17.0))]
    bm = bmesh.new()
    rnd = random.Random(L.SEED + 21)
    for (ax, ay), (bx, by) in runs:
        a, b = Vector((ax, ay, 0)), Vector((bx, by, 0))
        length = (b - a).length
        t = (b - a).normalized()
        ang = math.atan2(t.y, t.x)
        rot = Matrix.Rotation(ang, 4, "Z")
        n = int(length / 0.15)
        for i in range(n):
            p = a + t * (i + 0.5) * length / n
            z = site.height(p.x, p.y)
            d, _, hw, w = site.stream_at(p.x, p.y)
            if d < hw + 0.2:
                z = max(z, w + 0.05)
            h = 1.85 + rnd.uniform(-0.01, 0.01)
            _box(bm, Vector((p.x, p.y, z + h / 2 - 0.05)), (length / n * 0.94, 0.025, h), rot)
        # rails and posts on the inner side
        for i in range(int(length / 2.4) + 1):
            p = a + t * min(length, i * 2.4)
            z = site.height(p.x, p.y)
            _box(bm, Vector((p.x, p.y, z + 0.9)) - (Matrix.Rotation(ang, 3, "Z") @ Vector((0, 0.06, 0))) *
                 (1 if (ax, ay) != (x0, y1) else -1), (0.1, 0.1, 1.9), rot)
    return _finish(bm, "Fence", col, [fence_wood()])
