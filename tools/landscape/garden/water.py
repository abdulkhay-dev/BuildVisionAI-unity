"""The stream: level pools, cascade sheets between them and foam where the water lands."""
import math

import bpy
from mathutils import Vector

from .util import mesh_object


def water_material():
    mat = bpy.data.materials.new("M_Water")
    mat.use_nodes = True
    nt = mat.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1)
    b.inputs["Roughness"].default_value = 0.025
    b.inputs["IOR"].default_value = 1.333
    b.inputs["Transmission Weight"].default_value = 1.0
    # ripples: two noise layers stretched along the flow (UV u = along the stream)
    uv = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.9, 2.2, 1.0)
    nt.links.new(uv.outputs["Object"], mp.inputs["Vector"])
    n1 = nt.nodes.new("ShaderNodeTexNoise")
    n1.inputs["Scale"].default_value = 3.0
    n1.inputs["Detail"].default_value = 6.0
    n1.inputs["Roughness"].default_value = 0.55
    nt.links.new(mp.outputs["Vector"], n1.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.1
    bump.inputs["Distance"].default_value = 0.02
    nt.links.new(n1.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return mat


def _no_shadow(obj):
    """Water must not shadow its own bed (without caustics a refractive surface blocks the sun)."""
    obj.visible_shadow = False
    return obj


def foam_material():
    """White water: noise streaks along the flow (UV v), mostly opaque at the top of the fall."""
    mat = bpy.data.materials.new("M_Foam")
    mat.use_nodes = True
    nt = mat.node_tree
    out = nt.nodes["Material Output"]
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.92, 0.95, 0.95, 1)
    b.inputs["Roughness"].default_value = 0.35
    b.inputs["Subsurface Weight"].default_value = 0.4
    b.inputs["Subsurface Radius"].default_value = (0.5, 0.6, 0.7)
    b.inputs["Subsurface Scale"].default_value = 0.02
    uv = nt.nodes.new("ShaderNodeUVMap")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs["Vector"])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    mulx = nt.nodes.new("ShaderNodeMath")
    mulx.operation = "MULTIPLY"
    mulx.inputs[1].default_value = 22.0
    nt.links.new(sep.outputs["X"], mulx.inputs[0])
    muly = nt.nodes.new("ShaderNodeMath")
    muly.operation = "MULTIPLY"
    muly.inputs[1].default_value = 2.5
    nt.links.new(sep.outputs["Y"], muly.inputs[0])
    nt.links.new(mulx.outputs[0], comb.inputs["X"])
    nt.links.new(muly.outputs[0], comb.inputs["Y"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 1.0
    noise.inputs["Detail"].default_value = 8.0
    noise.inputs["Roughness"].default_value = 0.65
    nt.links.new(comb.outputs["Vector"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.38
    ramp.color_ramp.elements[1].position = 0.62
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    # the foam attribute (0..1) fades the white out downstream / at the sheet edges
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_type = "GEOMETRY"
    attr.attribute_name = "foam"
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    nt.links.new(ramp.outputs["Color"], mul.inputs[0])
    nt.links.new(attr.outputs["Fac"], mul.inputs[1])
    water = nt.nodes.new("ShaderNodeBsdfGlass")
    water.inputs["IOR"].default_value = 1.333
    water.inputs["Roughness"].default_value = 0.05
    water.inputs["Color"].default_value = (0.9, 1.0, 0.95, 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mul.outputs[0], mix.inputs["Fac"])
    nt.links.new(water.outputs["BSDF"], mix.inputs[1])
    nt.links.new(b.outputs["BSDF"], mix.inputs[2])
    # the landing foam patch is partly transparent (no glass under it)
    transp = nt.nodes.new("ShaderNodeBsdfTransparent")
    tattr = nt.nodes.new("ShaderNodeAttribute")
    tattr.attribute_type = "GEOMETRY"
    tattr.attribute_name = "patch"
    mix2 = nt.nodes.new("ShaderNodeMixShader")
    # patch: transparent where there is no foam; sheet: glass where there is no foam
    sel = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tattr.outputs["Fac"], sel.inputs["Fac"])
    nt.links.new(mix.outputs["Shader"], sel.inputs[1])
    nt.links.new(mul.outputs[0], mix2.inputs["Fac"])
    nt.links.new(transp.outputs["BSDF"], mix2.inputs[1])
    nt.links.new(b.outputs["BSDF"], mix2.inputs[2])
    nt.links.new(mix2.outputs["Shader"], sel.inputs[2])
    nt.links.new(sel.outputs["Shader"], out.inputs["Surface"])
    return mat


def _normal(t):
    return Vector((-t.y, t.x, 0.0))


def build(site, col):
    wmat, fmat = water_material(), foam_material()
    objs = []
    stream = site.stream
    # pools: level ribbons slightly wider than the channel so they meet the banks
    for k, pool in enumerate(site.pools):
        verts, faces = [], []
        across = 10
        steps = max(2, int((pool.s1 - pool.s0) / 0.2))
        for i in range(steps + 1):
            s = pool.s0 + (pool.s1 - pool.s0) * i / steps
            p, t = stream.at(s)
            n = _normal(t)
            hw = site.half_width(s) + 0.45
            for j in range(across + 1):
                u = -1 + 2 * j / across
                q = p + n * hw * u
                verts.append((q.x, q.y, pool.level))
        for i in range(steps):
            for j in range(across):
                a = i * (across + 1) + j
                faces.append((a, a + across + 1, a + across + 2, a + 1))
        objs.append(_no_shadow(mesh_object(f"Water_Pool_{k:02d}", verts, faces, col, mats=[wmat])))
    # cascades: a curved sheet per tongue over the lip plus a foam patch where each lands
    for k, c in enumerate(site.cascades):
        p0, t = stream.at(c["s"])
        n = _normal(t)
        drop = c["top"] - c["bottom"]
        hw_lip = site.half_width(c["s"])
        run = 0.2 + drop * 0.4
        verts, faces, uvs, foam, patch = [], [], [], [], []
        for ti, (u0, half) in enumerate(c["tongues"]):
            p = p0 + n * hw_lip * u0
            hw = hw_lip * half
            rows, across = 14, 8
            base = len(verts)
            for i in range(rows + 1):
                v = i / rows
                fwd = run * v - 0.1
                z = c["top"] + 0.01 - drop * (v ** 1.7)
                for j in range(across + 1):
                    u = -1 + 2 * j / across
                    wav = 0.03 * math.sin(u * 7.0 + k + ti) * v
                    q = p + t * (fwd + wav) + n * hw * u * (1.0 + 0.5 * v)
                    verts.append((q.x, q.y, z))
                    foam.append(min(1.0, 0.35 + 1.3 * v) * (1.0 - abs(u) ** 4))
                    patch.append(0.0)
            for i in range(rows):
                for j in range(across):
                    a = base + i * (across + 1) + j
                    f = (a, a + 1, a + across + 2, a + across + 1)
                    faces.append(f)
                    for idx in f:
                        ii, jj = divmod(idx - base, across + 1)
                        uvs.append((jj / across + ti * 0.37, ii / rows))
            # landing patch: a disc of foam fading outwards, a hair above the pool below
            base = len(verts)
            ring, seg = 5, 20
            ctr = p + t * (run + 0.15)
            for r_i in range(ring + 1):
                r = (r_i / ring) * (hw * 2.2 + 0.25)
                for s_i in range(seg):
                    a = 2 * math.pi * s_i / seg
                    q = ctr + t * math.cos(a) * r * 1.5 + n * math.sin(a) * r
                    verts.append((q.x, q.y, c["bottom"] + 0.012))
                    foam.append((1.0 - r_i / ring) ** 1.3)
                    patch.append(1.0)
            for r_i in range(ring):
                for s_i in range(seg):
                    a = base + r_i * seg + s_i
                    b = base + r_i * seg + (s_i + 1) % seg
                    f = (a, b, b + seg, a + seg)
                    faces.append(f)
                    for idx in f:
                        rr, ss = divmod(idx - base, seg)
                        uvs.append((ss / seg + ti * 0.29, rr / ring))
        obj = _no_shadow(mesh_object(f"Water_Cascade_{k:02d}", verts, faces, col, uvs=uvs, mats=[fmat]))
        for name, vals in (("foam", foam), ("patch", patch)):
            a = obj.data.attributes.new(name, "FLOAT", "POINT")
            a.data.foreach_set("value", vals)
        objs.append(obj)
    return objs
