"""Exports the landscape kit for the House app (Unity):

    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P tools/landscape/export_kit.py [-- id ...]

Input: Poly Haven .blend models and ground textures in .cache/polyhaven (tools/landscape/fetch_garden.py) and
the procedural perennials of tools/landscape/garden/flora.py.
Output: Assets/House4696/External/Landscape/
  Models/<variant>.fbx          one FBX per variant, objects <variant>_LOD0 / _LOD1 (/ _LOD2 impostor cards of plants)
  Textures/impostors/…          the impostor atlas: front and side view of every plant, unlit colour + alpha
  Textures/<material>/…         albedo (png with alpha for cutout foliage), normal, mask (R metal, G AO, A smooth)
  Terrain/<layer>/…             ground layers for the terrain
  landscape.json                manifest read by Unity's LandscapeKitImporter
Budgets are realtime ones (MacBook Air, dense gardens): LOD0 targets below, LOD1 from Poly Haven's own lower LOD
or a collapse decimation. Pivots: ground centre, metres, Blender Z up (FBX exported Y up, -Z forward).
"""
import json
import math
import os
import re
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "assets"))

import process_blender as pb  # noqa: E402  (texture packing shared with the furniture library)
from garden import flora  # noqa: E402
from garden.util import PH_BLEND, PH_TEX, ROOT  # noqa: E402

OUT = os.path.join(ROOT, "Assets", "House4696", "External", "Landscape")

BOULDERS = ["namaqualand_boulder_02", "namaqualand_boulder_03", "namaqualand_boulder_04", "namaqualand_boulder_05",
            "namaqualand_boulder_06"]

# kind: rock (collider, shadows), stone (small, no collider), plant (mesh instances, LODs), detail (terrain detail
# mesh: grass and ground cover drawn instanced by the terrain, single LOD).
# src: (asset, LOD0 collection suffix, LOD1 suffix or decimation ratio or None, variant filter)
KIT = [
    {"id": "rock_boulder", "kind": "rock", "grey": 0.25,
     "src": [(a, "_LOD3", None, None) for a in BOULDERS], "lod0": 2500, "lod1": 0.3},
    {"id": "rock_moss", "kind": "rock",
     "src": [("rock_moss_set_01", "", None, None), ("rock_moss_set_02", "", None, None)], "lod0": 2000, "lod1": 0.3},
    {"id": "rock_small", "kind": "stone",
     "src": [("stone_01", "_LOD3", None, None), ("rock_07", "_LOD3", None, None), ("rock_09", "_LOD3", None, None),
             ("namaqualand_stones_01", "_LOD3", None, None)], "lod0": 400},
    {"id": "grass_lawn", "kind": "detail", "src": [("grass_medium_01", "_LOD2", None, r"(mid|large|tall)")]},
    {"id": "grass_short", "kind": "detail", "src": [("grass_bermuda_01", "_static", None, r"(medium|tall|clump)")]},
    {"id": "moss", "kind": "detail", "src": [("moss_01", "_LOD0", None, None)]},
    {"id": "groundcover", "kind": "detail",
     "src": [("shrub_04", "_LOD2", None, None), ("periwinkle_plant", "_LOD4", None, None),
             ("celandine_01", "_LOD1", None, None), ("weed_plant_02", "_LOD2", None, None),
             ("nettle_plant", "_LOD3", None, None)]},
    # the same low plants as instanced plants in the beds (with LODs and impostor cards)
    {"id": "groundcover_plant", "kind": "plant",
     "src": [("periwinkle_plant", "_LOD3", "_LOD5", None), ("celandine_01", "_LOD0", "_LOD2", None),
             ("weed_plant_02", "_LOD1", "_LOD3", None), ("nettle_plant", "_LOD2", "_LOD3", None)]},
    {"id": "grass_tuft", "kind": "plant", "src": [("grass_medium_02", "_static", 0.4, None)]},
    {"id": "fern", "kind": "plant", "src": [("fern_02", "", 0.4, None)]},
    {"id": "shrub", "kind": "plant",
     "src": [("shrub_02", "_LOD1", "_LOD2", None), ("wild_rooibos_bush", "_LOD2", "_LOD3", r"_(a|b|c)")]},
    {"id": "flower_yellow", "kind": "plant",
     "src": [("flower_ursinia", "_LOD2", 0.4, r"_(a|b|c)_"), ("dandelion_01", "_LOD2", "_LOD3", r"_(a|b)_")]},
    {"id": "flower_orange", "kind": "plant", "src": [("flower_gazania", "_LOD1", "_LOD3", r"_(e|f|g|h)_")]},
    # procedural perennials (flora.py): builder, count, kwargs
    {"id": "flower_salvia", "kind": "plant", "flora": ("spike_plant", 4, 100, {"flower": (0.26, 0.12, 0.62)})},
    {"id": "flower_lavender", "kind": "plant",
     "flora": ("spike_plant", 3, 200, {"flower": (0.42, 0.33, 0.78), "height": (0.3, 0.45), "spike": 0.3,
                                       "floret": 0.014, "stems": (30, 44), "leaf_color": (0.2, 0.26, 0.17),
                                       "spread": 0.2})},
    {"id": "flower_lupin", "kind": "plant",
     "flora": ("spike_plant", 3, 300, {"stems": (5, 8), "height": (0.7, 1.0), "spike": 0.42, "floret": 0.028,
                                       "leaves": 16, "leaf_len": 0.2, "spread": 0.12,
                                       "flower": [(0.32, 0.22, 0.75), (0.75, 0.3, 0.6), (0.5, 0.25, 0.8)]})},
    {"id": "flower_daisy", "kind": "plant", "flora": ("daisy", 4, 400, {})},
    {"id": "flower_pink", "kind": "plant",
     "flora": ("phlox", 3, 500, {"flower": [(0.9, 0.3, 0.6), (0.95, 0.5, 0.72), (0.75, 0.2, 0.55)]})},
    {"id": "hosta", "kind": "plant", "flora": ("hosta", 3, 600, {})},
]

TERRAIN_LAYERS = [("soil", "forest_ground_04", "2k"), ("grass", "sparse_grass", "2k"),
                  ("pebbles", "river_small_rocks", "2k"), ("mud", "brown_mud_leaves_01", "2k")]

FLORA_DETAIL_LOD1 = 0.55     # LOD1 of the perennials: from ~9 m, dense enough that the switch does not show
PALETTE = 64          # flora palette texture size (4096 colours, 4 bits per channel)


# ----------------------------------------------------------------------------------------- scene
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def tris(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def append_variants(asset, suffix, pattern):
    """Mesh objects of the asset's LOD collection keyed by variant (name without _LODn)."""
    path = os.path.join(PH_BLEND, asset, asset + ".blend")
    wanted = asset + suffix
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        if wanted not in src.collections:
            # fewer LODs than asked: take the coarsest one that exists
            m = re.fullmatch(r"_LOD(\d+)", suffix)
            lower = [asset + f"_LOD{k}" for k in range(int(m.group(1)) - 1, -1, -1)] if m else []
            wanted = next((c for c in lower if c in src.collections), None)
            if wanted is None:
                raise RuntimeError(f"{asset}: no collection {asset + suffix}")
        dst.collections = [wanted]
    col = dst.collections[0]
    out = {}
    for obj in col.all_objects:
        if obj.type != "MESH" or obj.hide_render or "geometry_nodes" in obj.name or obj.name.endswith("_geo"):
            continue
        if any(m and m.name.endswith("_sphere") for m in obj.data.materials):
            continue
        if pattern and not re.search(pattern, obj.name):
            continue
        key = re.sub(r"(\.\d+)?$", "", re.sub(r"_LOD\d+(\.\d+)?$", "", obj.name))
        out[key] = obj
    for obj in list(col.all_objects):
        if obj not in out.values():
            bpy.data.objects.remove(obj)
    bpy.data.collections.remove(col)
    for obj in out.values():
        bpy.context.scene.collection.objects.link(obj)
    return out


def localise(obj, name):
    """Own mesh copy in object space with rotation/scale applied and the location dropped (pivot = PH origin)."""
    me = obj.data.copy()
    loc, rot, scl = obj.matrix_world.decompose()
    from mathutils import Matrix
    me.transform(Matrix.LocRotScale(None, rot, scl))
    new = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(new)
    return new


def decimate(obj, target):
    t = tris(obj)
    if t <= target:
        return
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = target / t
    mod.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=mod.name)


def ground_pivot(objs):
    """Moves the meshes so the lowest point of LOD0 sits at z = 0 (x/y stay on the Poly Haven origin)."""
    zmin = min(v.co.z for v in objs[0].data.vertices)
    for o in objs:
        for v in o.data.vertices:
            v.co.z -= zmin


def size_of(obj):
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    return [round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3), round(max(zs) - min(zs), 3)]


def export(objs, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"}, apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_UNITS", bake_space_transform=True, axis_forward="-Z",
                             axis_up="Y", mesh_smooth_type="FACE", use_mesh_modifiers=True, add_leaf_bones=False,
                             bake_anim=False, path_mode="STRIP", embed_textures=False)


# ----------------------------------------------------------------------------------------- textures
KINDS = [("_diff_", "diff"), ("_alpha_", "alpha"), ("_opacity_", "alpha"), ("_nor_gl_", "nor_gl"), ("_arm_", "arm"), ("_rough_", "rough")]


def material_maps(mat, asset):
    maps = {}
    if not mat.use_nodes:
        return maps
    for node in mat.node_tree.nodes:
        stack = [node] if node.type != "GROUP" else list(node.node_tree.nodes)
        for n in stack:
            if n.type != "TEX_IMAGE" or n.image is None:
                continue
            base = os.path.basename(n.image.filepath or n.image.name)
            for token, kind in KINDS:
                if token in base and kind not in maps:
                    path = bpy.path.abspath(n.image.filepath)
                    if not os.path.exists(path):
                        path = os.path.join(PH_BLEND, asset, "textures", base)
                    if os.path.exists(path):
                        maps[kind] = path
    return maps


def desaturate(path, amount):
    px = pb.load_pixels(path)
    lum = px[..., 0] * 0.2126 + px[..., 1] * 0.7152 + px[..., 2] * 0.0722
    for c in range(3):
        px[..., c] = lum + (px[..., c] - lum) * amount
    pb.save_pixels(px, path, "PNG" if path.endswith(".png") else "JPEG")


class Materials:
    def __init__(self):
        self.done = {}

    def export(self, mat, asset, grey=None):
        """Writes the texture set of a Poly Haven material once; returns the Unity slot name."""
        # appending a second LOD collection brings a copy of the material (".001"): same texture set
        name = re.sub(r"\.\d+$", "", mat.name) + ("_grey" if grey is not None else "")
        if name in self.done:
            return name
        maps = material_maps(mat, asset)
        files = pb.write_texture_set(maps, os.path.join(OUT, "Textures", name), name) if maps else {}
        if grey is not None and "albedo" in files:
            desaturate(os.path.join(OUT, "Textures", name, files["albedo"]), grey)
        self.done[name] = {"name": name, "folder": f"Textures/{name}", "textures": files,
                           "cutout": "alpha" in maps, "twoSided": "alpha" in maps}
        print(f"  material {name}: {sorted(maps)}", flush=True)
        return name


# ----------------------------------------------------------------------------------------- flora palette
class Palette:
    """All procedural perennials share one opaque material whose albedo is a colour palette: every face's
    UVs point at the texel of its (quantised) colour."""

    def __init__(self):
        self.index = {}

    def texel(self, rgb):
        key = tuple(min(15, int(c * 15 + 0.5)) for c in rgb)
        if key not in self.index:
            self.index[key] = len(self.index)
        i = self.index[key]
        if i >= PALETTE * PALETTE:
            raise RuntimeError("palette full")
        return ((i % PALETTE) + 0.5) / PALETTE, ((i // PALETTE) + 0.5) / PALETTE

    def apply(self, obj):
        me = obj.data
        col = me.attributes["col"]
        uv = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            c = [0.0, 0.0, 0.0]
            for vi in poly.vertices:
                v = col.data[vi].color
                c = [c[k] + v[k] / len(poly.vertices) for k in range(3)]
            # linear → sRGB for the albedo texture
            srgb = [min(1.0, max(0.0, x)) ** (1 / 2.2) for x in c]
            u, v = self.texel(srgb)
            for li in poly.loop_indices:
                uv.data[li].uv = (u, v)
        me.materials.clear()
        mat = bpy.data.materials.get("flora") or bpy.data.materials.new("flora")
        me.materials.append(mat)
        for poly in me.polygons:
            poly.material_index = 0
        me.attributes.remove(me.attributes["col"])

    def write(self):
        px = np.zeros((PALETTE, PALETTE, 4), dtype=np.float32)
        px[..., 3] = 1.0
        for key, i in self.index.items():
            px[i // PALETTE, i % PALETTE, :3] = [k / 15 for k in key]
        folder = os.path.join(OUT, "Textures", "flora")
        os.makedirs(folder, exist_ok=True)
        pb.save_pixels(px, os.path.join(folder, "flora_albedo.png"), "PNG")
        mask = np.zeros((4, 4, 4), dtype=np.float32)
        mask[..., 1] = 1.0            # occlusion
        mask[..., 3] = 0.3            # smoothness
        pb.save_pixels(mask, os.path.join(folder, "flora_mask.png"), "PNG")
        print(f"  palette: {len(self.index)} colours", flush=True)
        return {"name": "flora", "folder": "Textures/flora",
                "textures": {"albedo": "flora_albedo.png", "mask": "flora_mask.png"},
                "cutout": False, "twoSided": True, "point": True}


# ----------------------------------------------------------------------------------------- impostors
IMPOSTOR_CELL = 128
IMPOSTOR_GRID = (16, 16)      # columns × rows of cells: a 2048 × 2048 atlas, 256 views (three per plant)


def _unlit_copy(mat):
    """A copy of `mat` that emits its base colour and keeps its cut-out alpha (for capturing albedo views)."""
    m = mat.copy()
    nt = m.node_tree
    if nt is None:
        return m

    def source(node, name):
        if node is None or name not in node.inputs:
            return None
        inp = node.inputs[name]
        return inp.links[0].from_socket if inp.links else inp.default_value

    principled = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    group = next((n for n in nt.nodes if n.type == "GROUP" and "Diffuse" in n.inputs), None)
    color = source(group, "Diffuse") if group else None
    alpha = source(group, "Alpha") if group else None
    invert = False
    if color is None:
        color = source(principled, "Base Color")
    if alpha is None and principled is not None and principled.inputs["Alpha"].links:
        alpha = source(principled, "Alpha")
    if alpha is None:
        # cut-out through a Mix Shader with a Transparent BSDF on one side (flower_gazania)
        for n in nt.nodes:
            if n.type == "MIX_SHADER" and n.inputs[0].links:
                a, b = n.inputs[1], n.inputs[2]
                if a.links and a.links[0].from_node.type == "BSDF_TRANSPARENT":
                    alpha = n.inputs[0].links[0].from_socket
                elif b.links and b.links[0].from_node.type == "BSDF_TRANSPARENT":
                    alpha, invert = n.inputs[0].links[0].from_socket, True
    emit = nt.nodes.new("ShaderNodeEmission")
    if isinstance(color, bpy.types.NodeSocket):
        nt.links.new(color, emit.inputs["Color"])
    elif color is not None:
        emit.inputs["Color"].default_value = tuple(color)[:4] if len(tuple(color)) >= 4 else (*color, 1.0)
    transp = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    if isinstance(alpha, bpy.types.NodeSocket):
        if invert:
            inv = nt.nodes.new("ShaderNodeMath")
            inv.operation = "SUBTRACT"
            inv.inputs[0].default_value = 1.0
            nt.links.new(alpha, inv.inputs[1])
            alpha = inv.outputs[0]
        nt.links.new(alpha, mix.inputs[0])
    else:
        mix.inputs[0].default_value = float(alpha) if alpha is not None else 1.0
    nt.links.new(transp.outputs[0], mix.inputs[1])
    nt.links.new(emit.outputs[0], mix.inputs[2])
    out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output), None) or \
        next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if out is None:
        out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def _dilate(px, passes=10):
    """Bleeds the colour of opaque texels into the transparent ones so mipmaps have no dark fringes."""
    rgb = px[..., :3].copy()
    filled = px[..., 3] > 0.3
    for _ in range(passes):
        acc = np.zeros_like(rgb)
        cnt = np.zeros(filled.shape, dtype=np.float32)
        for shift in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            sf = np.roll(filled, shift, axis=(0, 1))
            sr = np.roll(rgb, shift, axis=(0, 1))
            m = sf & ~filled
            acc[m] += sr[m]
            cnt[m] += 1
        new = cnt > 0
        rgb[new] = acc[new] / cnt[new][:, None]
        filled |= new
    out = px.copy()
    out[..., :3] = rgb
    return out


class Impostors:
    """Front and side views of every plant in one atlas, and the two crossed cards (LOD2) that show them.
    Cells are kept per variant in the manifest, so re-exporting one group rewrites only its cells."""

    def __init__(self, manifest):
        info = manifest.get("impostors") or {}
        cols, rows = IMPOSTOR_GRID
        same = info.get("grid") == [cols, rows] and info.get("cell") == IMPOSTOR_CELL
        self.cells = {k: list(v) for k, v in info.get("cells", {}).items()} if same else {}
        self.next = info.get("next", 0) if same else 0
        self.path = os.path.join(OUT, "Textures", "impostors", "impostors_albedo.png")
        self.atlas = pb.load_pixels(self.path) if same and os.path.exists(self.path) else \
            np.zeros((rows * IMPOSTOR_CELL, cols * IMPOSTOR_CELL, 4), dtype=np.float32)
        self.used = False

    def _cell_rect(self, i):
        cols, rows = IMPOSTOR_GRID
        c, r = i % cols, i // cols
        inset = 0.5 / IMPOSTOR_CELL
        return ((c + inset) / cols, (r + inset) / rows, (c + 1 - inset) / cols, (r + 1 - inset) / rows)

    def _put(self, i, px):
        cols, _ = IMPOSTOR_GRID
        c, r = i % cols, i // cols
        n = IMPOSTOR_CELL
        self.atlas[r * n:(r + 1) * n, c * n:(c + 1) * n] = px

    def _render(self, obj, view, box):
        """view: "front" (looks along +Y), "side" (along -X) or "top" (down -Z)."""
        sc = bpy.context.scene
        (xmin, xmax, ymin, ymax, zmax) = box
        cx, cy, zc = (xmin + xmax) / 2, (ymin + ymax) / 2, zmax / 2
        front = view == "front"
        if view == "top":
            size = max(xmax - xmin, ymax - ymin) * 1.06
        else:
            size = max(xmax - xmin if front else ymax - ymin, zmax) * 1.06
        cam_data = bpy.data.cameras.new("impostor_cam")
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = size
        cam_data.clip_start, cam_data.clip_end = 0.01, 100.0
        cam = bpy.data.objects.new("impostor_cam", cam_data)
        sc.collection.objects.link(cam)
        if view == "front":                        # looks along +Y: image right = +X, up = +Z
            cam.location = (cx, ymin - 5.0, zc)
            cam.rotation_euler = (math.pi / 2, 0.0, 0.0)
        elif view == "side":                       # looks along -X: image right = +Y, up = +Z
            cam.location = (xmax + 5.0, cy, zc)
            cam.rotation_euler = (math.pi / 2, 0.0, math.pi / 2)
        else:                                      # looks down: image right = +X, up = +Y
            cam.location = (cx, cy, zmax + 5.0)
            cam.rotation_euler = (0.0, 0.0, 0.0)
        sc.camera = cam
        path = os.path.join(bpy.app.tempdir or "/tmp", f"impostor_{obj.name}_{view}.png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        px = pb.load_pixels(path)
        os.remove(path)
        bpy.data.objects.remove(cam)
        bpy.data.cameras.remove(cam_data)
        return px, size, (cx, cy, zc)

    def build(self, vid, obj):
        """Captures `obj` (LOD0, pivot on the ground) and returns the LOD2 object `<vid>_LOD2`."""
        sc = bpy.context.scene
        sc.render.engine = "CYCLES"
        sc.cycles.device = "CPU"
        sc.cycles.samples = 16
        sc.cycles.use_denoising = False
        sc.cycles.filter_width = 1.0
        sc.render.resolution_x = sc.render.resolution_y = IMPOSTOR_CELL
        sc.render.resolution_percentage = 100
        sc.render.film_transparent = True
        sc.render.image_settings.file_format = "PNG"
        sc.render.image_settings.color_mode = "RGBA"
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
        sc.view_settings.exposure = 0.0
        sc.view_settings.gamma = 1.0
        hidden = [o for o in sc.objects if o is not obj and not o.hide_render]
        for o in hidden:
            o.hide_render = True
        originals = [s.material for s in obj.material_slots]
        for s in obj.material_slots:
            if s.material:
                s.material = _unlit_copy(s.material)
        xs = [v.co.x for v in obj.data.vertices]
        ys = [v.co.y for v in obj.data.vertices]
        zs = [v.co.z for v in obj.data.vertices]
        box = (min(xs), max(xs), min(ys), max(ys), max(zs))
        views = [self._render(obj, v, box) for v in ("front", "side", "top")]
        for s, m in zip(obj.material_slots, originals):
            copy = s.material
            s.material = m
            if copy is not None and copy is not m:
                bpy.data.materials.remove(copy)
        for o in hidden:
            o.hide_render = False

        cells = self.cells.get(vid)
        if cells is None or len(cells) != len(views):
            if self.next + len(views) > IMPOSTOR_GRID[0] * IMPOSTOR_GRID[1]:
                raise RuntimeError("impostor atlas full: enlarge IMPOSTOR_GRID")
            cells = list(range(self.next, self.next + len(views)))
            self.next += len(views)
            self.cells[vid] = cells
        verts, faces, uvs = [], [], []
        n = IMPOSTOR_CELL
        zmax = box[4]
        for (px, size, (cx, cy, zc)), cell, view in zip(views, cells, ("front", "side", "top")):
            self._put(cell, px)
            u0, v0, u1, v1 = self._cell_rect(cell)
            # crop the card to the silhouette (+1 texel): the empty part of the square cell would still be shaded
            # and alpha-tested for every pixel it covers
            cols = np.where((px[..., 3] > 0.02).any(axis=0))[0]
            rows = np.where((px[..., 3] > 0.02).any(axis=1))[0]
            if len(cols) == 0:
                continue
            c0, c1 = max(0, cols[0] - 1), min(n, cols[-1] + 2)
            r0, r1 = max(0, rows[0] - 1), min(n, rows[-1] + 2)
            a0, a1 = -size / 2 + size * c0 / n, -size / 2 + size * c1 / n        # image right, from the centre
            b0, b1 = -size / 2 + size * r0 / n, -size / 2 + size * r1 / n        # image up, from the centre
            U0, U1 = u0 + (u1 - u0) * c0 / n, u0 + (u1 - u0) * c1 / n
            V0, V1 = v0 + (v1 - v0) * r0 / n, v0 + (v1 - v0) * r1 / n
            if view == "front":
                quad = [(cx + a0, cy, zc + b0), (cx + a1, cy, zc + b0), (cx + a1, cy, zc + b1), (cx + a0, cy, zc + b1)]
            elif view == "side":
                quad = [(cx, cy + a0, zc + b0), (cx, cy + a1, zc + b0), (cx, cy + a1, zc + b1), (cx, cy + a0, zc + b1)]
            else:
                # the crown seen from above, a horizontal card a little above half height: what orbit and top
                # views see of a bed (the vertical cards are edge-on from there)
                z = zmax * 0.6
                quad = [(cx + a0, cy + b0, z), (cx + a1, cy + b0, z), (cx + a1, cy + b1, z), (cx + a0, cy + b1, z)]
            base = len(verts)
            verts += quad
            faces.append((base, base + 1, base + 2, base + 3))
            uvs += [(U0, V0), (U1, V0), (U1, V1), (U0, V1)]
        me = bpy.data.meshes.new(vid + "_LOD2")
        me.from_pydata(verts, [], faces)
        layer = me.uv_layers.new(name="UVMap")
        for i, uv in enumerate(uvs):
            layer.data[i].uv = uv
        # foliage lighting: the cards take the light like the top of a crown, not like two flat walls
        me.normals_split_custom_set([(0.0, 0.0, 1.0)] * len(me.loops))
        mat = bpy.data.materials.get("impostor") or bpy.data.materials.new("impostor")
        me.materials.append(mat)
        card = bpy.data.objects.new(vid + "_LOD2", me)
        sc.collection.objects.link(card)
        self.used = True
        return card

    def write(self):
        folder = os.path.dirname(self.path)
        os.makedirs(folder, exist_ok=True)
        pb.save_pixels(_dilate(self.atlas), self.path, "PNG")
        print(f"  impostor atlas: {self.next} views", flush=True)
        return {"name": "impostor", "folder": "Textures/impostors", "textures": {"albedo": "impostors_albedo.png"},
                "cutout": True, "twoSided": True, "impostor": True, "smoothness": 0.08}

    def info(self):
        return {"cells": self.cells, "next": self.next, "grid": list(IMPOSTOR_GRID), "cell": IMPOSTOR_CELL}


# ----------------------------------------------------------------------------------------- groups
def fix_images(asset):
    """Appended images keep paths relative to their .blend: point them at the asset's texture folder (for Cycles)."""
    for img in bpy.data.images:
        if img.source != "FILE" or os.path.exists(bpy.path.abspath(img.filepath)):
            continue
        path = os.path.join(PH_BLEND, asset, "textures", os.path.basename(img.filepath))
        if os.path.exists(path):
            img.filepath = path
            img.reload()


def export_ph_group(entry, mats, impostors):
    variants = []
    for asset, lod0, lod1, pattern in entry["src"]:
        reset()
        v0 = append_variants(asset, lod0, pattern)
        v1 = append_variants(asset, lod1, pattern) if isinstance(lod1, str) else {}
        for key in sorted(v0):
            vid = f"{entry['id']}_{len(variants):02d}"
            a = localise(v0[key], vid + "_LOD0")
            if "lod0" in entry:
                decimate(a, entry["lod0"])
            objs = [a]
            if isinstance(lod1, str) and key in v1:
                objs.append(localise(v1[key], vid + "_LOD1"))
            elif isinstance(lod1, float):
                b = localise(a, vid + "_LOD1")
                b.data = a.data.copy()
                decimate(b, max(60, int(tris(a) * lod1)))
                objs.append(b)
            elif "lod1" in entry and isinstance(entry["lod1"], float):
                b = localise(a, vid + "_LOD1")
                b.data = a.data.copy()
                decimate(b, max(60, int(tris(a) * entry["lod1"])))
                objs.append(b)
            ground_pivot(objs)
            if entry["kind"] == "plant":
                fix_images(asset)
                objs.append(impostors.build(vid, a))
            # material slots → exported texture sets (renamed so the FBX slot = the Unity material)
            for o in objs:
                for slot in o.material_slots:
                    if slot.material and slot.material.name != "impostor":
                        name = mats.export(slot.material, asset, entry.get("grey"))
                        if slot.material.name != name:
                            m = bpy.data.materials.get(name) or slot.material.copy()
                            m.name = name
                            slot.material = m
            export(objs, os.path.join(OUT, "Models", vid + ".fbx"))
            variants.append({"id": vid, "fbx": f"Models/{vid}.fbx", "source": f"polyhaven:{asset}",
                             "size": size_of(objs[0]), "tris": [tris(o) for o in objs],
                             "materials": sorted({s.material.name for s in objs[0].material_slots if s.material})})
            print(f"  {vid:18} {asset:24} tris {variants[-1]['tris']}", flush=True)
    return variants


def export_flora_group(entry, palette, impostors):
    builder, count, seed0, kwargs = entry["flora"]
    fn = getattr(flora, builder)
    variants = []
    for i in range(count):
        reset()
        col = bpy.context.scene.collection
        kw = {k: (v[i % len(v)] if isinstance(v, list) else v) for k, v in kwargs.items()}
        vid = f"{entry['id']}_{i:02d}"
        objs = []
        card = None
        for lod, detail in ((0, 1.0), (1, FLORA_DETAIL_LOD1)):
            flora.DETAIL = detail
            obj = fn(f"{vid}_LOD{lod}", seed0 + i, col, **kw)
            if lod == 0:
                card = impostors.build(vid, obj)       # with the colour-attribute materials, before the palette
            palette.apply(obj)
            objs.append(obj)
        flora.DETAIL = 1.0
        objs.append(card)
        export(objs, os.path.join(OUT, "Models", vid + ".fbx"))
        variants.append({"id": vid, "fbx": f"Models/{vid}.fbx", "source": f"procedural:{builder}",
                         "size": size_of(objs[0]), "tris": [tris(o) for o in objs], "materials": ["flora"]})
        print(f"  {vid:18} {builder:24} tris {variants[-1]['tris']}", flush=True)
    return variants


def export_terrain_layers():
    layers = []
    for lid, source, res in TERRAIN_LAYERS:
        base = os.path.join(PH_TEX, source)
        maps = {k: os.path.join(base, f"{k}_{res}.jpg") for k in ("diff", "nor_gl", "arm")}
        maps = {k: v for k, v in maps.items() if os.path.exists(v)}
        files = pb.write_texture_set(maps, os.path.join(OUT, "Terrain", lid), lid)
        info = json.load(open(os.path.join(base, "info.json")))
        dims = info.get("dimensions_mm") or [2000, 2000]
        layers.append({"id": lid, "source": "polyhaven:" + source, "folder": f"Terrain/{lid}", "textures": files,
                       "metersPerTile": [dims[0] / 1000.0, dims[1] / 1000.0]})
        print(f"  terrain layer {lid} ← {source}", flush=True)
    return layers


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    only = set(argv)
    manifest_path = os.path.join(OUT, "landscape.json")
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
    groups = {g["id"]: g for g in manifest.get("groups", [])}
    materials = {m["name"]: m for m in manifest.get("materials", [])}
    mats, palette, impostors = Materials(), Palette(), Impostors(manifest)
    flora_ran = False
    for entry in KIT:
        if only and entry["id"] not in only and not (entry.get("flora") and "flora" in only):
            continue
        print(f"group {entry['id']}", flush=True)
        if "flora" in entry:
            variants = export_flora_group(entry, palette, impostors)
            flora_ran = True
        else:
            variants = export_ph_group(entry, mats, impostors)
        groups[entry["id"]] = {"id": entry["id"], "kind": entry["kind"], "variants": variants}
    materials.update(mats.done)
    if flora_ran:
        if only and not all(e["id"] in only or "flora" in only for e in KIT if "flora" in e):
            raise SystemExit("flora groups share one palette: export them together (argument 'flora')")
        materials["flora"] = palette.write()
    if impostors.used:
        materials["impostor"] = impostors.write()
        manifest["impostors"] = impostors.info()
    if not only or "terrain" in only:
        manifest["terrainLayers"] = export_terrain_layers()
    manifest["groups"] = [groups[e["id"]] for e in KIT if e["id"] in groups]
    manifest["materials"] = sorted(materials.values(), key=lambda m: m["name"])
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    total = sum(len(g["variants"]) for g in manifest["groups"])
    print(f"manifest {manifest_path}: {len(manifest['groups'])} groups, {total} variants, "
          f"{len(manifest['materials'])} materials", flush=True)


if __name__ == "__main__":
    main()
