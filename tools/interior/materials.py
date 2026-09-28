"""Blender approximations of the app's materials, for look-dev renders of library models.

Library ids ("velvet#b9ab98", "oak_veneer") load the processed textures from Assets/House4696/External/Materials (albedo ×
tint like URP's _BaseColor, normal, mask R metal / G AO / A smoothness) with UVs in metres / metersPerTile. Built-in
palette names ("black_metal", "led", "glass") are plain Principled settings close to Runtime/Catalog/InteriorMaterials."""
import os

import bpy

from kit import OUT

_manifest = None


def manifest():
    global _manifest
    if _manifest is None:
        import json
        _manifest = json.load(open(os.path.join(OUT, "external.json")))
    return _manifest


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


# name: (base colour linear, roughness, metallic, extra)
BUILTIN = {
    "black_metal": ((0.02, 0.02, 0.02), 0.45, 0.8, {}),
    "blackmetal": ((0.02, 0.02, 0.02), 0.45, 0.8, {}),
    "brass": ((0.72, 0.5, 0.25), 0.28, 1.0, {}),
    "chrome": ((0.8, 0.8, 0.8), 0.08, 1.0, {}),
    "white_metal": ((0.8, 0.8, 0.78), 0.35, 0.6, {}),
    "steel": ((0.6, 0.6, 0.6), 0.3, 1.0, {}),
    "mirror": ((0.92, 0.92, 0.92), 0.01, 1.0, {}),
    "glass": ((0.95, 0.97, 0.97), 0.02, 0.0, {"transmission": 1.0}),
    "black_glass": ((0.01, 0.01, 0.012), 0.05, 0.0, {}),
    "screen": ((0.006, 0.006, 0.007), 0.06, 0.0, {}),
    "led": ((1.0, 0.9, 0.75), 0.5, 0.0, {"emit": (1.0, 0.72, 0.42), "strength": 12.0}),
    "globe": ((0.95, 0.93, 0.9), 0.4, 0.0, {"emit": (1.0, 0.8, 0.55), "strength": 4.0}),
    "lamp_shade": ((0.95, 0.91, 0.84), 0.8, 0.0, {"emit": (1.0, 0.75, 0.48), "strength": 2.0}),
    "downlight": ((1, 1, 1), 0.5, 0.0, {"emit": (1.0, 0.85, 0.65), "strength": 20.0}),
    "ceramic": ((0.88, 0.88, 0.86), 0.12, 0.0, {}),
    "gloss_white": ((0.86, 0.855, 0.84), 0.1, 0.0, {}),
    "soft_white": ((0.85, 0.84, 0.82), 0.5, 0.0, {}),
    "stoneware": ((0.55, 0.5, 0.45), 0.7, 0.0, {}),
    "furniture_dark": ((0.035, 0.032, 0.03), 0.55, 0.0, {}),
    "bedding": ((0.9, 0.88, 0.85), 0.9, 0.0, {}),
    "towel": ((0.78, 0.75, 0.7), 0.95, 0.0, {}),
    "rug": ((0.65, 0.6, 0.52), 0.95, 0.0, {}),
    "rattan": ((0.45, 0.3, 0.16), 0.7, 0.0, {}),
    "leather": ((0.25, 0.13, 0.07), 0.45, 0.0, {}),
    "charcoal": ((0.05, 0.05, 0.048), 0.9, 0.0, {}),
    "linen": ((0.6, 0.53, 0.42), 0.9, 0.0, {}),
    "walnut": ((0.2, 0.1, 0.05), 0.5, 0.0, {}),
    "oak_light": ((0.7, 0.45, 0.25), 0.5, 0.0, {}),
    "plaster": ((0.8, 0.78, 0.74), 0.9, 0.0, {}),
    "render": ((0.78, 0.75, 0.7), 0.9, 0.0, {}),
    "stucco": ((0.08, 0.08, 0.08), 0.9, 0.0, {}),
    "soffit": ((0.5, 0.45, 0.38), 0.7, 0.0, {}),
    "coping": ((0.1, 0.1, 0.1), 0.5, 0.6, {}),
}


def _node_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes["Principled BSDF"]


def _img(path, non_color=False):
    img = bpy.data.images.load(path, check_existing=True)
    if non_color:
        img.colorspace_settings.name = "Non-Color"
    return img


def library(spec):
    """Material for a library id with an optional #tint; None if unknown."""
    base, _, tint = spec.partition("#")
    entry = next((m for m in manifest()["materials"] if m["id"] == base), None)
    if entry is None:
        return None
    m, n, l, p = _node_mat(spec)
    folder = os.path.join(OUT, entry["folder"])
    tx = entry["textures"]
    uv = n.new("ShaderNodeUVMap")
    mp = n.new("ShaderNodeMapping")
    s = entry.get("metersPerTile", [1, 1])
    mp.inputs["Scale"].default_value = (1 / s[0], 1 / s[1], 1)
    l.new(uv.outputs["UV"], mp.inputs["Vector"])
    alb = n.new("ShaderNodeTexImage")
    alb.image = _img(os.path.join(folder, tx["albedo"]))
    l.new(mp.outputs["Vector"], alb.inputs["Vector"])
    col = alb.outputs["Color"]
    if tint:
        mul = n.new("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs["Factor"].default_value = 1.0
        l.new(col, mul.inputs[6])
        mul.inputs[7].default_value = (*srgb(tint), 1)
        col = mul.outputs[2]
    l.new(col, p.inputs["Base Color"])
    if tx.get("normal"):
        nt = n.new("ShaderNodeTexImage")
        nt.image = _img(os.path.join(folder, tx["normal"]), True)
        l.new(mp.outputs["Vector"], nt.inputs["Vector"])
        nm = n.new("ShaderNodeNormalMap")
        l.new(nt.outputs["Color"], nm.inputs["Color"])
        l.new(nm.outputs["Normal"], p.inputs["Normal"])
    if tx.get("mask"):
        mk = n.new("ShaderNodeTexImage")
        mk.image = _img(os.path.join(folder, tx["mask"]), True)
        l.new(mp.outputs["Vector"], mk.inputs["Vector"])
        sep = n.new("ShaderNodeSeparateColor")
        l.new(mk.outputs["Color"], sep.inputs["Color"])
        l.new(sep.outputs["Red"], p.inputs["Metallic"])
        inv = n.new("ShaderNodeMath")
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1.0
        l.new(mk.outputs["Alpha"], inv.inputs[1])
        l.new(inv.outputs[0], p.inputs["Roughness"])
    return m


def builtin(spec):
    base, _, tint = spec.partition("#")
    key = base.lower()
    if key not in BUILTIN:
        return None
    col, rough, metal, extra = BUILTIN[key]
    if tint:
        col = srgb(tint)
    m, n, l, p = _node_mat(spec)
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if "transmission" in extra:
        p.inputs["Transmission Weight"].default_value = extra["transmission"]
        p.inputs["IOR"].default_value = 1.45
    if "emit" in extra:
        p.inputs["Emission Color"].default_value = (*extra["emit"], 1)
        p.inputs["Emission Strength"].default_value = extra["strength"]
    return m


def own(model_id, slot):
    """A model's own material (textures written by the kit, factors from the manifest)."""
    entry = next(m for m in manifest()["models"] if m["id"] == model_id)
    s = next(x for x in entry["slots"] if x["slot"] == slot)
    m, n, l, p = _node_mat(f"{model_id}_{slot}")
    tx = s.get("textures", {})
    t = None
    if tx.get("albedo"):
        t = n.new("ShaderNodeTexImage")
        t.image = _img(os.path.join(OUT, entry["folder"], tx["albedo"]))
        l.new(t.outputs["Color"], p.inputs["Base Color"])
    elif s.get("baseColor"):
        p.inputs["Base Color"].default_value = s["baseColor"]
    p.inputs["Roughness"].default_value = s.get("roughness", 0.6)
    p.inputs["Metallic"].default_value = s.get("metallic", 0.0)
    em = s.get("emissive", [0, 0, 0])
    if any(em):
        p.inputs["Emission Color"].default_value = (*em, 1)
        p.inputs["Emission Strength"].default_value = 1.5
        if t is not None:                   # textured glow: the picture itself (screens), like the Unity importer
            mul = n.new("ShaderNodeMix")
            mul.data_type = "RGBA"
            mul.blend_type = "MULTIPLY"
            mul.inputs["Factor"].default_value = 1.0
            l.new(t.outputs["Color"], mul.inputs[6])
            mul.inputs[7].default_value = (*em, 1)
            l.new(mul.outputs[2], p.inputs["Emission Color"])
    return m


_cache = {}


def resolve(spec, model_id=None, slot=None):
    key = (spec, model_id, slot)
    if key in _cache:
        return _cache[key]
    m = None
    if spec is None and model_id:
        m = own(model_id, slot)
    else:
        m = builtin(spec) or library(spec)
        if m is None:
            print("unknown material", spec)
            m = builtin("plaster")
    _cache[key] = m
    return m


def import_model(model_id, loc=(0, 0, 0), yaw=0.0, params=None, name=None):
    """Imports Models/<id>/<id>.fbx and dresses it like the app does (item params override slot defaults)."""
    import math
    entry = next(m for m in manifest()["models"] if m["id"] == model_id)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(OUT, entry["folder"], entry["fbx"]))
    new = [o for o in bpy.data.objects if o not in before]
    params = params or {}
    for o in new:
        if o.type != "MESH":
            continue
        for i, ms in enumerate(o.material_slots):
            sname = ms.material.name.split(".")[0] if ms.material else f"slot{i}"
            s = next((x for x in entry["slots"] if x["slot"] == sname), None)
            if s is None:
                continue
            want = params.get(sname, s.get("default"))
            has_own = bool(s.get("textures")) or "baseColor" in s
            if want and want != "original":
                ms.material = resolve(want)
            elif has_own:
                ms.material = resolve(None, model_id, sname)
    root = bpy.data.objects.new(name or model_id, None)
    bpy.context.scene.collection.objects.link(root)
    for o in new:
        if o.parent is None:
            o.parent = root
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(yaw))
    return root
