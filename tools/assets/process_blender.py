"""Prepares external assets for Unity. Run with Blender (numpy inside):

    /Applications/Blender.app/Contents/MacOS/Blender -b --python tools/assets/process_blender.py [-- id ...]

Input: tools/assets/catalog.json and the sources in .cache/polyhaven (tools/assets/fetch_polyhaven.py).
Output: Assets/House4696/External/
  Materials/<id>/<id>_albedo.jpg|png, _normal.jpg, _mask.png   (mask: R metallic, G occlusion, A smoothness)
  Models/<id>/<id>.fbx + <id>_<slot>_* textures
  external.json                                                  (what Unity's importer reads)
Models are normalised: metres, one mesh, pivot at the floor centre (hanging fittings: at the ceiling point),
front facing Blender -Y, material slots named by role ("upholstery", "legs", …).
"""
import json
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(ROOT, ".cache", "polyhaven")
OUT = os.path.join(ROOT, "Assets", "House4696", "External")


# ----------------------------------------------------------------------------------------- images
def load_pixels(path):
    img = bpy.data.images.load(path, check_existing=False)
    img.colorspace_settings.name = "Non-Color"   # raw file values, no colour management
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return px


def save_pixels(px, path, fmt):
    h, w = px.shape[:2]
    img = bpy.data.images.new("out", w, h, alpha=True)
    img.colorspace_settings.name = "Non-Color"
    img.pixels.foreach_set(np.clip(px, 0, 1).astype(np.float32).ravel())
    img.filepath_raw = path
    img.file_format = fmt
    if fmt == "JPEG":
        img.save(filepath=path, quality=92)
    else:
        img.save(filepath=path)
    bpy.data.images.remove(img)


def neutralise(px, target=0.78, contrast=1.0):
    """Grey albedo with the same pattern and a light mean, so a tint (#rrggbb) sets the colour.
    contrast < 1 flattens the pattern (smooth painted walls should not show the scan's cracks and stains)."""
    lum = px[..., 0] * 0.2126 + px[..., 1] * 0.7152 + px[..., 2] * 0.0722
    mean = max(float(lum.mean()), 1e-3)
    lum = (mean + (lum - mean) * contrast) * (target / mean)
    out = px.copy()
    out[..., 0] = out[..., 1] = out[..., 2] = lum
    return out


def write_texture_set(maps, out_dir, prefix, neutral=False, contrast=1.0):
    """maps: dict with diff / nor_gl / arm (/ alpha) file paths. Returns the written file names."""
    os.makedirs(out_dir, exist_ok=True)
    result = {}
    if "diff" in maps:
        px = load_pixels(maps["diff"])
        if neutral:
            px = neutralise(px, contrast=contrast)
        if "alpha" in maps:
            a = load_pixels(maps["alpha"])
            px[..., 3] = a[..., 0]
            name = prefix + "_albedo.png"
            save_pixels(px, os.path.join(out_dir, name), "PNG")
        else:
            px[..., 3] = 1.0
            name = prefix + "_albedo.jpg"
            save_pixels(px, os.path.join(out_dir, name), "JPEG")
        result["albedo"] = name
    if "nor_gl" in maps:
        px = load_pixels(maps["nor_gl"])
        px[..., 3] = 1.0
        name = prefix + "_normal.jpg"
        save_pixels(px, os.path.join(out_dir, name), "JPEG")
        result["normal"] = name
    if "arm" not in maps and "rough" in maps:
        # roughness only: occlusion 1, not metallic
        r = load_pixels(maps["rough"])
        arm = np.ones_like(r)
        arm[..., 1] = r[..., 0]
        arm[..., 2] = 0.0
        maps = dict(maps, arm=None)
    else:
        arm = load_pixels(maps["arm"]) if "arm" in maps else None
    if arm is not None:
        # roughness/AO/metal carry little fine detail: half resolution (box filter) is enough
        if arm.shape[0] >= 1024:
            h, w = arm.shape[0] // 2 * 2, arm.shape[1] // 2 * 2
            arm = arm[:h, :w].reshape(h // 2, 2, w // 2, 2, 4).mean(axis=(1, 3))
        mask = np.zeros_like(arm)
        mask[..., 0] = arm[..., 2]          # metallic
        mask[..., 1] = arm[..., 0]          # occlusion
        mask[..., 3] = 1.0 - arm[..., 1]    # smoothness
        name = prefix + "_mask.png"
        save_pixels(mask, os.path.join(out_dir, name), "PNG")
        result["mask"] = name
    return result


# ----------------------------------------------------------------------------------------- materials
def process_material(entry):
    src = os.path.join(CACHE, entry["source"])
    res = entry.get("res", "1k")
    info = json.load(open(os.path.join(src, "info.json")))
    maps = {k: os.path.join(src, f"{k}_{res}.jpg") for k in ("diff", "nor_gl", "arm", "rough")}
    maps = {k: v for k, v in maps.items() if os.path.exists(v)}
    out_dir = os.path.join(OUT, "Materials", entry["id"])
    files = write_texture_set(maps, out_dir, entry["id"], entry.get("neutral", False), entry.get("contrast", 1.0))
    dims = info.get("dimensions_mm") or [2000, 2000]
    return {
        "id": entry["id"], "name": entry["name"], "category": entry["category"], "source": "polyhaven:" + entry["source"],
        "neutral": entry.get("neutral", False), "metersPerTile": [dims[0] / 1000.0, dims[1] / 1000.0],
        "folder": f"Materials/{entry['id']}", "textures": files,
    }


# ----------------------------------------------------------------------------------------- scene helpers
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mesh_objects():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def join_all(name):
    objs = mesh_objects()
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = name
    obj.data.name = name
    # bake parent transforms into the mesh
    obj.parent = None
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return obj


def bounds(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def set_pivot(obj, hanging=False, back=False, wall=False):
    """Floor centre; hanging fittings: ceiling point; back=True: centre of the back edge (beds stand against a wall);
    wall=True: centre of the back face (frames, sconces: the point on the wall, y = mounting height)."""
    lo, hi = bounds(obj)
    z = hi.z if hanging else (lo.z + hi.z) / 2 if wall else lo.z
    pivot = Vector(((lo.x + hi.x) / 2, hi.y if (back or wall) else (lo.y + hi.y) / 2, z))
    obj.data.transform(Matrix.Translation(-pivot))
    obj.location = (0, 0, 0)
    lo, hi = bounds(obj)
    return [round(hi.x - lo.x, 3), round(hi.y - lo.y, 3), round(hi.z - lo.z, 3)]


DEFAULT_MAX_TRIS = 40000


def decimate(obj, max_tris):
    """Collapse-decimate models over the triangle budget (0 = keep as is): books, chess sets, rocks."""
    tris = triangles(obj)
    if not max_tris or tris <= max_tris:
        return
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("decimate", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = max_tris / tris
    mod.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    print(f"  decimated {obj.name}: {tris} → {triangles(obj)} triangles")


def export_fbx(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"}, apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_UNITS", bake_space_transform=True, axis_forward="-Z", axis_up="Y",
                             mesh_smooth_type="FACE", use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False,
                             path_mode="STRIP", embed_textures=False)


def triangles(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


# ----------------------------------------------------------------------------------------- Poly Haven models
def gltf_materials(path):
    """Material factors from the glTF (for slots without texture maps: glass, emissive globes)."""
    g = json.load(open(path))
    out = {}
    for m in g.get("materials", []):
        pbr = m.get("pbrMetallicRoughness", {})
        out[m.get("name", "")] = {
            "baseColor": pbr.get("baseColorFactor", [1, 1, 1, 1]),
            "metallic": pbr.get("metallicFactor", 1.0),
            "roughness": pbr.get("roughnessFactor", 1.0),
            "emissive": m.get("emissiveFactor", [0, 0, 0]),
            "transparent": m.get("alphaMode") == "BLEND" or "KHR_materials_transmission" in m.get("extensions", {}),
            "cutout": m.get("alphaMode") == "MASK",
        }
    return out


def match_maps(all_maps, key):
    """Texture maps of a material: exact name, a map set whose name ends with / contains it, any case; a single shared
    set ("main") serves every material of the model."""
    if key in all_maps:
        return all_maps[key]
    low = key.lower()
    for k, v in all_maps.items():
        if k.lower() == low or k.lower().endswith("_" + low) or low.endswith("_" + k.lower()):
            return v
    if len(all_maps) == 1:
        return next(iter(all_maps.values()))
    return {}


def process_polyhaven_model(entry):
    src = os.path.join(CACHE, entry["source"])
    info = json.load(open(os.path.join(src, "info.json")))
    factors = gltf_materials(os.path.join(src, "model.gltf"))
    reset()
    bpy.ops.import_scene.gltf(filepath=os.path.join(src, "model.gltf"))
    obj = join_all(entry["id"])
    if entry.get("scale"):
        obj.data.transform(Matrix.Scale(entry["scale"], 4))
    if entry.get("yaw"):
        obj.data.transform(Matrix.Rotation(math.radians(entry["yaw"]), 4, "Z"))   # models whose front is not -Y
    decimate(obj, entry.get("maxTris", DEFAULT_MAX_TRIS))
    size = set_pivot(obj, entry.get("hanging", False), wall=entry.get("pivot") == "wall")

    prefix = entry["source"] + "_"
    rename = entry.get("slots", {})
    slots = []
    out_dir = os.path.join(OUT, "Models", entry["id"])
    for i, s in enumerate(obj.material_slots):
        orig = s.material.name if s.material else f"slot{i}"
        key = orig[len(prefix):] if orig.startswith(prefix) else ("main" if orig == entry["source"] else orig)
        slot = rename.get(key, key)
        s.material.name = slot
        maps = {k: os.path.join(src, v) for k, v in match_maps(info["maps"], key).items()}
        f = factors.get(orig, {})
        slots.append({
            "slot": slot, "textures": write_texture_set(maps, out_dir, f"{entry['id']}_{slot}") if maps else {},
            "baseColor": f.get("baseColor"), "metallic": f.get("metallic"), "roughness": f.get("roughness"),
            "emissive": f.get("emissive"), "transparent": f.get("transparent", False),
            "cutout": f.get("cutout", False) or "alpha" in maps,
        })
    export_fbx(obj, os.path.join(out_dir, entry["id"] + ".fbx"))
    return {
        "id": entry["id"], "name": entry["name"], "category": entry["category"], "source": "polyhaven:" + entry["source"],
        "folder": f"Models/{entry['id']}", "fbx": entry["id"] + ".fbx", "size": size, "triangles": triangles(obj),
        "hanging": entry.get("hanging", False), "slots": slots,
    }


# ----------------------------------------------------------------------------------------- own models (Blender)
class Builder:
    """Soft furniture from bevelled boxes: every part is a box with rounded edges, UVs in metres (cube projection),
    so the library's tiling fabrics keep their real scale. Front faces -Y, floor at z = 0."""

    def __init__(self, name):
        reset()
        self.name = name
        self.slots = []

    def slot(self, name):
        if name not in self.slots:
            self.slots.append(name)
            bpy.data.materials.new(name)
        return name

    def box(self, slot, center, size, radius=0.0, segments=4, rot=(0, 0, 0), bulge=0.0):
        """Box with bevelled (rounded) edges; bulge puffs the top face up like a filled cushion."""
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
        if bulge > 0:
            # subdivide so the top can dome
            bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=6, use_grid_fill=True)
            hz = size[2] / 2
            for v in bm.verts:
                if v.co.z > hz - 1e-4:
                    u = 1 - min(1, abs(v.co.x) / (size[0] / 2)) ** 2
                    w = 1 - min(1, abs(v.co.y) / (size[1] / 2)) ** 2
                    v.co.z += bulge * u * w
        me = bpy.data.meshes.new("part")
        bm.to_mesh(me)
        bm.free()
        obj = bpy.data.objects.new("part", me)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = center
        obj.rotation_euler = [math.radians(a) for a in rot]
        obj.data.materials.append(bpy.data.materials[self.slot(slot)])
        if radius > 0:
            mod = obj.modifiers.new("bevel", "BEVEL")
            mod.width = radius
            mod.segments = segments
            mod.limit_method = "ANGLE"
            mod.angle_limit = math.radians(40)
            mod.harden_normals = False
        for p in obj.data.polygons:
            p.use_smooth = True
        return obj

    def pillow(self, slot, center, size, rot=(0, 0, 0)):
        """Plump pillow: a subdivided box squashed towards its edges."""
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=8, use_grid_fill=True)
        sx, sy, sz = size
        for v in bm.verts:
            x, y, z = v.co.x * 2, v.co.y * 2, v.co.z * 2     # -1..1
            edge = max(abs(x), abs(z))
            thick = (1 - edge ** 4) * 0.9 + 0.1
            v.co = Vector((x * sx / 2, y * sy / 2 * thick, z * sz / 2))
        me = bpy.data.meshes.new("pillow")
        bm.to_mesh(me)
        bm.free()
        obj = bpy.data.objects.new("pillow", me)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = center
        obj.rotation_euler = [math.radians(a) for a in rot]
        obj.data.materials.append(bpy.data.materials[self.slot(slot)])
        mod = obj.modifiers.new("smooth", "SUBSURF")
        mod.levels = 1
        for p in obj.data.polygons:
            p.use_smooth = True
        return obj

    def finish(self, entry, defaults):
        # apply modifiers, merge, metre UVs
        for o in mesh_objects():
            bpy.context.view_layer.objects.active = o
            for m in list(o.modifiers):
                bpy.ops.object.modifier_apply(modifier=m.name)
        obj = join_all(self.name)
        # make the joined object's slot order match self.slots
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.cube_project(cube_size=1.0, correct_aspect=False, clip_to_bounds=False, scale_to_bounds=False)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        size = set_pivot(obj, back=entry.get("pivot") == "back")
        out_dir = os.path.join(OUT, "Models", entry["id"])
        export_fbx(obj, os.path.join(out_dir, entry["id"] + ".fbx"))
        slots = [{"slot": s.material.name, "default": defaults.get(s.material.name), "uvMeters": True} for s in obj.material_slots]
        return {
            "id": entry["id"], "name": entry["name"], "category": entry["category"], "source": "blender:" + entry["blender"],
            "folder": f"Models/{entry['id']}", "fbx": entry["id"] + ".fbx", "size": size, "triangles": triangles(obj),
            "hanging": False, "slots": slots,
        }


def build_sofa_modern(entry):
    """Low three-seat sofa, 2.3 × 0.96 m: upholstered plinth, three seat and back cushions, slim arms, metal legs."""
    b = Builder(entry["id"])
    W, D = 2.30, 0.96
    arm = 0.16
    b.box("upholstery", (0, 0, 0.23), (W, D, 0.22), radius=0.03)                             # plinth
    for sx in (-1, 1):                                                                        # arms
        b.box("upholstery", (sx * (W / 2 - arm / 2), 0.0, 0.40), (arm, D, 0.56), radius=0.06, segments=6)
    b.box("upholstery", (0, D / 2 - 0.09, 0.52), (W - 2 * arm + 0.02, 0.18, 0.62), radius=0.05)   # back frame
    inner = W - 2 * arm
    cw = inner / 3
    for i in range(3):                                                                        # seat cushions
        x = -inner / 2 + cw * (i + 0.5)
        b.box("upholstery", (x, -0.07, 0.405), (cw - 0.012, D - 0.26, 0.14), radius=0.045, segments=6, bulge=0.018)
    for i in range(3):                                                                        # back cushions
        x = -inner / 2 + cw * (i + 0.5)
        b.box("upholstery", (x, D / 2 - 0.25, 0.66), (cw - 0.012, 0.17, 0.42), radius=0.06, segments=6, rot=(-9, 0, 0), bulge=0.02)
    b.pillow("cushion", (-inner / 2 + 0.34, D / 2 - 0.40, 0.66), (0.46, 0.15, 0.44), rot=(-12, 0, 12))
    b.pillow("cushion", (inner / 2 - 0.34, D / 2 - 0.40, 0.66), (0.46, 0.15, 0.44), rot=(-12, 0, -12))
    for sx in (-1, 1):                                                                        # legs
        for sy in (-1, 1):
            b.box("legs", (sx * (W / 2 - 0.10), sy * (D / 2 - 0.10), 0.06), (0.04, 0.04, 0.12), radius=0.004, segments=2)
    return b.finish(entry, {"upholstery": "linen_rough#c8c0b3", "cushion": "velvet#8b5e45", "legs": "black_metal"})


def build_bed_modern(entry):
    """Double bed 1.8 × 2.0 m mattress: channel-tufted headboard, upholstered base, bedding, pillows and a throw."""
    b = Builder(entry["id"])
    W, L = 1.96, 2.14                          # outer size of the base
    head_y = L / 2                             # headboard at +Y (back), foot towards -Y (front)
    b.box("frame", (0, 0, 0.21), (W, L, 0.26), radius=0.03)                                   # upholstered base
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.box("legs", (sx * (W / 2 - 0.08), sy * (L / 2 - 0.08), 0.04), (0.05, 0.05, 0.08), radius=0.005, segments=2)
    channels = 7                                                                              # channel-tufted headboard
    cw = (W + 0.04) / channels
    for i in range(channels):
        x = -(W + 0.04) / 2 + cw * (i + 0.5)
        b.box("headboard", (x, head_y + 0.02, 0.72), (cw - 0.006, 0.11, 1.12), radius=0.045, segments=6, bulge=0.0)
    b.box("frame", (0, head_y + 0.075, 0.70), (W + 0.06, 0.03, 1.16), radius=0.01, segments=2)  # back panel
    b.box("bedding", (0, -0.02, 0.45), (1.80, 2.0, 0.22), radius=0.05, segments=6)             # mattress
    # duvet over the lower three quarters, hanging over the sides, folded back at the top
    b.box("bedding", (0, -0.24, 0.575), (1.90, 1.58, 0.07), radius=0.03, segments=4, bulge=0.025)
    for sx in (-1, 1):
        b.box("bedding", (sx * 0.935, -0.24, 0.44), (0.05, 1.58, 0.26), radius=0.02, segments=3)
    b.box("bedding", (0, -1.01, 0.44), (1.90, 0.05, 0.26), radius=0.02, segments=3)
    b.box("bedding", (0, 0.52, 0.605), (1.90, 0.12, 0.06), radius=0.03, segments=4)            # fold
    b.box("throw", (0, -0.72, 0.625), (1.96, 0.46, 0.035), radius=0.012, segments=3)           # throw across the foot
    for sx in (-1, 1):
        b.box("throw", (sx * 0.975, -0.72, 0.50), (0.035, 0.46, 0.26), radius=0.012, segments=3)
    for sx in (-1, 1):                                                                         # sleeping pillows
        b.pillow("pillow", (sx * 0.43, head_y - 0.24, 0.66), (0.72, 0.16, 0.46), rot=(-70, 0, 0))
    for sx in (-1, 1):                                                                         # decorative pillows
        b.pillow("cushion", (sx * 0.30, head_y - 0.40, 0.68), (0.46, 0.14, 0.44), rot=(-60, 0, sx * 6))
    return b.finish(entry, {"headboard": "wool_herringbone#b4aca0", "frame": "wool_herringbone#b4aca0", "legs": "black_metal",
                            "bedding": "linen_rough#eeeae3", "pillow": "linen_rough#e7e2d9", "cushion": "velvet#6f7a66",
                            "throw": "wool_herringbone#6b6259"})


BUILDERS = {"sofa_modern": build_sofa_modern, "bed_modern": build_bed_modern}


# ----------------------------------------------------------------------------------------- main
def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    only = set(argv)
    catalog = json.load(open(os.path.join(ROOT, "tools", "assets", "catalog.json")))
    manifest_path = os.path.join(OUT, "external.json")
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {"materials": [], "models": []}
    by_id = {e["id"]: e for e in manifest["materials"]}
    for entry in catalog["materials"]:
        if not only or entry["id"] in only:
            by_id[entry["id"]] = process_material(entry)
            print("material", entry["id"])
    manifest["materials"] = [by_id[e["id"]] for e in catalog["materials"] if e["id"] in by_id]
    models = {e["id"]: e for e in manifest["models"]}
    for entry in catalog["models"]:
        if only and entry["id"] not in only:
            continue
        if "source" in entry:
            models[entry["id"]] = process_polyhaven_model(entry)
        else:
            models[entry["id"]] = BUILDERS[entry["blender"]](entry)
        m = models[entry["id"]]
        print("model", m["id"], "size", m["size"], "tris", m["triangles"], "slots", [s["slot"] for s in m["slots"]])
    manifest["models"] = [models[e["id"]] for e in catalog["models"] if e["id"] in models]
    os.makedirs(OUT, exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("manifest", manifest_path)


if __name__ == "__main__":
    main()
