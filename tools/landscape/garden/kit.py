"""The asset kit: Poly Haven models appended from .cache/polyhaven/blend plus the procedural flora and props.

Every kit group is a collection under KIT (excluded from the view layer) whose objects are the variants,
named `v00_…`, `v01_…` so a Collection Info node picks them by index. The scene instances them; later the
same groups become the app's landscape catalogue.
"""
import os
import re

import bpy

from .util import PH_BLEND, collection, link

# group -> [(Poly Haven asset, LOD collection suffix or None, variant name filter regex or None)]
PH_GROUPS = {
    "rock_boulder": [("namaqualand_boulder_02", "_LOD1", None), ("namaqualand_boulder_03", "_LOD1", None),
                     ("namaqualand_boulder_04", "_LOD1", None), ("namaqualand_boulder_05", "_LOD1", None),
                     ("namaqualand_boulder_06", "_LOD1", None)],
    "rock_moss": [("rock_moss_set_01", None, None), ("rock_moss_set_02", None, None)],
    "rock_small": [("stone_01", "_LOD1", None), ("rock_07", "_LOD1", None), ("rock_09", "_LOD1", None),
                   ("namaqualand_stones_01", "_LOD1", None)],
    "grass_lawn": [("grass_medium_01", "_LOD1", r"(mid|large|tall)")],
    "grass_short": [("grass_bermuda_01", "_static", r"(medium|tall|clump)"), ("grass_medium_01", "_LOD1", r"small")],
    "grass_tuft": [("grass_medium_02", "_static", None)],
    "fern": [("fern_02", None, None)],
    "groundcover": [("shrub_01", "_LOD1", None), ("shrub_04", "_LOD1", None), ("periwinkle_plant", "_LOD1", None),
                    ("celandine_01", "_LOD1", None), ("weed_plant_02", "_LOD1", None), ("nettle_plant", "_LOD1", None)],
    "shrub": [("shrub_02", "_LOD0", None), ("wild_rooibos_bush", "_LOD0", r"_(a|b|c)")],
    "shrub_big": [("searsia_lucida", "_LOD1", r"_(a|b|c|d)_")],
    "flower_yellow": [("flower_ursinia", "_LOD1", r"_(a|b|c)_"), ("dandelion_01", "_LOD1", r"_(a|b)_")],
    "flower_blue": [("flower_heliophila", "_LOD1", None)],
    "flower_orange": [("flower_gazania", "_LOD1", r"_(e|f|g|h)_")],
    "moss": [("moss_01", "_LOD1", None)],
    "tree_oak": [("island_tree_01", "_LOD0", None), ("island_tree_02", "_LOD0", None)],
    "tree_birch": [("island_tree_03", "_LOD1", None)],
    "tree_maple": [("tree_small_02", "_LOD0", None)],
    "tree_fir": [("fir_tree_01", "_LOD1", None)],
    "tree_fir_small": [("fir_sapling_medium", "_LOD1", None)],
    "tree_fir_far": [("fir_tree_01", "_LOD2", None)],
    "tree_oak_far": [("island_tree_01", "_LOD1", None), ("island_tree_02", "_LOD1", None)],
}


class Kit:
    def __init__(self):
        self.root = collection("KIT")
        self.groups = {}

    def group(self, name):
        return self.groups[name]

    def add_group(self, name, objects):
        """Registers procedural variants as a kit group (objects are moved into it and renamed)."""
        col = collection("KIT_" + name, self.root)
        for i, obj in enumerate(objects):
            link(obj, col)
            obj.name = f"v{i:02d}_{name}"
            obj.location = (0, 0, 0)
        self.groups[name] = col
        return col

    def load_ph(self, only=None):
        for name, sources in PH_GROUPS.items():
            if only and name not in only:
                continue
            objs = []
            for asset, lod, pattern in sources:
                objs += self._append(asset, lod, pattern)
            self.add_group(name, objs)
            print(f"kit {name:16} {len(objs)} variants", flush=True)

    def finish(self):
        """Excludes the kit from rendering (it is only instanced)."""
        bpy.context.view_layer.update()
        from .util import exclude
        exclude(self.root)

    @staticmethod
    def _append(asset, lod, pattern):
        path = os.path.join(PH_BLEND, asset, asset + ".blend")
        with bpy.data.libraries.load(path, link=False) as (src, dst):
            wanted = asset + lod if lod else asset
            if wanted not in src.collections:
                raise RuntimeError(f"{asset}: no collection {wanted} in {list(src.collections)}")
            dst.collections = [wanted]
        col = dst.collections[0]
        out = []
        for obj in list(col.all_objects):
            if obj.type != "MESH" or obj.hide_render:
                continue
            if "geometry_nodes" in obj.name or obj.name.endswith("_geo"):
                continue
            if pattern and not re.search(pattern, obj.name):
                continue
            if obj.parent:
                mw = obj.matrix_world.copy()
                obj.parent = None
                obj.matrix_world = mw
            out.append(obj)
        # the appended collection itself is not linked to the scene; drop it
        for obj in list(col.all_objects):
            if obj not in out:
                bpy.data.objects.remove(obj)
        bpy.data.collections.remove(col)
        return out


def recolor_leaves(objs, hue, sat=1.0, val=1.0, suffix="_red", match=("leaf", "leaves", "foliage")):
    """Copies the leaf materials of `objs` and inserts a Hue/Saturation node after the base colour
    (Japanese maple from a green deciduous tree)."""
    done = {}
    for obj in objs:
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None or not any(m in mat.name.lower() for m in match):
                continue
            if mat.name not in done:
                new = mat.copy()
                new.name = mat.name + suffix
                nt = new.node_tree
                # the diffuse texture feeds either a Principled "Base Color" or a Poly Haven group "Diffuse"
                links = [lk for lk in nt.links if lk.from_node.type == "TEX_IMAGE"
                         and lk.to_socket.name in ("Base Color", "Diffuse")]
                for lk in links:
                    src, dst = lk.from_socket, lk.to_socket
                    hs = nt.nodes.new("ShaderNodeHueSaturation")
                    hs.inputs["Hue"].default_value = hue
                    hs.inputs["Saturation"].default_value = sat
                    hs.inputs["Value"].default_value = val
                    nt.links.new(src, hs.inputs["Color"])
                    nt.links.new(hs.outputs["Color"], dst)
                done[mat.name] = new
            slot.link = "OBJECT" if slot.link == "OBJECT" else slot.link
            slot.material = done[mat.name]
