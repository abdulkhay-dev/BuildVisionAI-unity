"""Terrain meshes: the detailed plot (0.25 m grid, stream carved in) and the far land with hills and
mountains out to the horizon. Masks for the materials are stored as point attributes."""
import math

import bpy

from . import layout as L
from .util import ValueNoise, collection, image, mesh_object, ph_maps, smoothstep


# ---------------------------------------------------------------- material

def _tex_set(nt, vec, source, tint=(1, 1, 1)):
    """Nodes for one Poly Haven texture set; returns (color, roughness, normal colour) sockets."""
    maps = ph_maps(source, "2k") or ph_maps(source)

    def tex(path, non_color):
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = image(path, non_color)
        nt.links.new(vec, t.inputs["Vector"])
        return t.outputs["Color"]

    col = tex(maps["diff"], False)
    if tint != (1, 1, 1):
        m = nt.nodes.new("ShaderNodeMix")
        m.data_type, m.blend_type = "RGBA", "MULTIPLY"
        m.inputs["Factor"].default_value = 1.0
        nt.links.new(col, m.inputs["A"])
        m.inputs["B"].default_value = (*tint, 1)
        col = m.outputs["Result"]
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(tex(maps["arm"], True), sep.inputs["Color"])
    return col, sep.outputs["Green"], tex(maps["nor_gl"], True)


def _mix(nt, kind, fac, a, b):
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = kind
    if kind == "RGBA":
        m.blend_type = "MIX"
    nt.links.new(fac, m.inputs["Factor"])
    nt.links.new(a, m.inputs["A"])
    nt.links.new(b, m.inputs["B"])
    return m.outputs["Result"]


def terrain_material():
    """Soil/mulch under the beds, grass on the lawns, pebbles in the stream bed, darker when wet."""
    mat = bpy.data.materials.new("M_Terrain")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (0.5, 0.5, 0.5)
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    vec = mapping.outputs["Vector"]
    small = nt.nodes.new("ShaderNodeMapping")
    small.inputs["Scale"].default_value = (0.9, 0.9, 0.9)
    nt.links.new(coord.outputs["Object"], small.inputs["Vector"])

    soil = _tex_set(nt, vec, "forest_ground_04", (0.75, 0.8, 0.6))
    grass = _tex_set(nt, vec, "sparse_grass", (0.8, 1.0, 0.65))
    bed = _tex_set(nt, small.outputs["Vector"], "river_small_rocks", (0.95, 0.95, 0.9))

    def attr(name):
        a = nt.nodes.new("ShaderNodeAttribute")
        a.attribute_type = "GEOMETRY"
        a.attribute_name = name
        return a.outputs["Fac"]

    lawn, wet, pebble = attr("lawn"), attr("wet"), attr("pebble")
    col = _mix(nt, "RGBA", lawn, soil[0], grass[0])
    col = _mix(nt, "RGBA", pebble, col, bed[0])
    rough = _mix(nt, "FLOAT", lawn, soil[1], grass[1])
    rough = _mix(nt, "FLOAT", pebble, rough, bed[1])
    nor = _mix(nt, "RGBA", lawn, soil[2], grass[2])
    nor = _mix(nt, "RGBA", pebble, nor, bed[2])
    # wet: darker and glossier
    dark = nt.nodes.new("ShaderNodeMix")
    dark.data_type, dark.blend_type = "RGBA", "MULTIPLY"
    nt.links.new(wet, dark.inputs["Factor"])
    nt.links.new(col, dark.inputs["A"])
    dark.inputs["B"].default_value = (0.45, 0.45, 0.42, 1)
    wr = nt.nodes.new("ShaderNodeMath")
    wr.operation = "MULTIPLY_ADD"
    nt.links.new(wet, wr.inputs[0])
    wr.inputs[1].default_value = -0.6
    nt.links.new(rough, wr.inputs[2])
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = 1.0
    nt.links.new(nor, nm.inputs["Color"])
    nt.links.new(dark.outputs["Result"], bsdf.inputs["Base Color"])
    nt.links.new(wr.outputs["Value"], bsdf.inputs["Roughness"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def far_material():
    """Far land: meadow/forest green low down, rock higher up, fading into the sky with distance."""
    mat = bpy.data.materials.new("M_FarLand")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.9
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs["Vector"])
    # height and slope → rock
    hmap = nt.nodes.new("ShaderNodeMapRange")
    hmap.inputs["From Min"].default_value = 120
    hmap.inputs["From Max"].default_value = 700
    nt.links.new(sep.outputs["Z"], hmap.inputs["Value"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.004
    noise.inputs["Detail"].default_value = 8
    nt.links.new(geo.outputs["Position"], noise.inputs["Vector"])
    forest = nt.nodes.new("ShaderNodeValToRGB")
    forest.color_ramp.elements[0].color = (0.018, 0.035, 0.012, 1)
    forest.color_ramp.elements[1].color = (0.06, 0.08, 0.03, 1)
    nt.links.new(noise.outputs["Fac"], forest.inputs["Fac"])
    rock = nt.nodes.new("ShaderNodeValToRGB")
    rock.color_ramp.elements[0].color = (0.10, 0.09, 0.08, 1)
    rock.color_ramp.elements[1].color = (0.22, 0.2, 0.18, 1)
    nt.links.new(noise.outputs["Fac"], rock.inputs["Fac"])
    col = _mix(nt, "RGBA", hmap.outputs["Result"], forest.outputs["Color"], rock.outputs["Color"])
    # aerial perspective
    cam = nt.nodes.new("ShaderNodeCameraData")
    haze = nt.nodes.new("ShaderNodeMapRange")
    haze.inputs["From Min"].default_value = 150
    haze.inputs["From Max"].default_value = 9000
    haze.interpolation_type = "SMOOTHSTEP"
    nt.links.new(cam.outputs["View Distance"], haze.inputs["Value"])
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 0.6
    nt.links.new(haze.outputs["Result"], pw.inputs[0])
    hc = nt.nodes.new("ShaderNodeRGB")
    hc.outputs[0].default_value = (0.42, 0.48, 0.62, 1)
    final = _mix(nt, "RGBA", pw.outputs["Value"], col, hc.outputs[0])
    nt.links.new(final, bsdf.inputs["Base Color"])
    # distant land also glows a little with the scattered sky light
    emit = nt.nodes.new("ShaderNodeMath")
    emit.operation = "MULTIPLY"
    emit.inputs[1].default_value = 0.9
    nt.links.new(pw.outputs["Value"], emit.inputs[0])
    nt.links.new(final, bsdf.inputs["Emission Color"])
    nt.links.new(emit.outputs["Value"], bsdf.inputs["Emission Strength"])
    return mat


# ---------------------------------------------------------------- meshes

def build_plot(site, col, step=0.25):
    x0, y0, x1, y1 = L.TERRAIN
    nx, ny = int((x1 - x0) / step) + 1, int((y1 - y0) / step) + 1
    verts, lawn, wet, pebble = [], [], [], []
    rnd = ValueNoise(L.SEED + 7)
    for j in range(ny):
        y = y0 + j * step
        for i in range(nx):
            x = x0 + i * step
            z = site.height(x, y)
            d, s, hw, w = site.stream_at(x, y)
            verts.append((x, y, z))
            pd = site.path_distance(x, y)
            lawn_mask = 1.0 - smoothstep(1.2, 2.4, pd + 0.4 * rnd.noise(x * 0.8, y * 0.8))
            if site.in_house(x, y, 3.0):
                lawn_mask = 1.0
            if not site.in_plot(x, y):
                lawn_mask = 0.6 + 0.4 * rnd.noise(x * 0.3, y * 0.3)
            lawn.append(lawn_mask * (1.0 - smoothstep(0.0, -0.3, -(d - hw - 0.8))))
            pebble.append(1.0 - smoothstep(hw - 0.2, hw + 0.5, d))
            wet.append(1.0 - smoothstep(0.0, 0.12, z - w - 0.04))
    faces = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            faces.append((a, a + 1, a + nx + 1, a + nx))
    obj = mesh_object("Terrain", verts, faces, col, mats=[terrain_material()])
    me = obj.data
    for name, vals in (("lawn", lawn), ("wet", wet), ("pebble", pebble)):
        a = me.attributes.new(name, "FLOAT", "POINT")
        a.data.foreach_set("value", vals)
    return obj


def far_height(site, noise, x, y):
    """Plot ground near the centre, rolling forested hills further out, a mountain range to the north."""
    h = site.natural(x, y)
    r = math.hypot(x, y - 10)
    hills = 26.0 * smoothstep(120, 900, r) * (0.55 + 0.45 * noise.fbm(x / 420, y / 420, 4))
    # ridged mountains, highest roughly north
    ang = math.atan2(x, y)            # 0 = north
    ridge = 0.0
    if r > 1400:
        n = 1.0 - abs(noise.fbm(x / 1600 + 11, y / 1600 - 7, 5))
        n = n * n
        bias = 0.45 + 0.55 * math.cos(ang) ** 2 if abs(ang) < 2.2 else 0.25
        # a saddle where the sun sets so it can still light the garden
        sun = math.radians(L.SUN["azimuth"])
        da = math.atan2(math.sin(ang - sun), math.cos(ang - sun))
        bias *= 1.0 - 0.55 * math.exp(-(da / 0.25) ** 2)
        ridge = 850.0 * smoothstep(1400, 5200, r) * n * bias
        ridge += 90 * noise.fbm(x / 300, y / 300, 4) * smoothstep(1400, 3000, r)
    return h + hills + ridge


def build_far(site, col, n=260, extent=11000.0):
    noise = ValueNoise(L.SEED + 3)
    x0, y0, x1, y1 = L.TERRAIN

    def axis(k):
        u = k / (n - 1) * 2 - 1
        return math.copysign(extent * (math.expm1(4.2 * abs(u)) / math.expm1(4.2)), u)

    coords = [axis(k) for k in range(n)]
    verts = []
    for y in coords:
        for x in coords:
            yy = y + 10.0
            z = far_height(site, noise, x, yy)
            inside = x0 + 1 < x < x1 - 1 and y0 + 1 < yy < y1 - 1
            verts.append((x, yy, z - (4.0 if inside else 0.0)))   # under the plot mesh and its stream bed
    faces = []
    for j in range(n - 1):
        for i in range(n - 1):
            a = j * n + i
            faces.append((a, a + 1, a + n + 1, a + n))
    return mesh_object("FarLand", verts, faces, col, mats=[far_material()])
