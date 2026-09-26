"""Plant and rock placement. Planting follows real garden practice: drifts (Voronoi cells) of one species,
species chosen by zone (stream bank, sunny bed, lawn edge, under trees), spacing per species. Each species
becomes a point cloud instanced by Geometry Nodes from its kit group."""
import math
import random

import bpy
from mathutils import Vector

from . import layout as L
from .util import ValueNoise, point_cloud, smoothstep


def instancer_tree(kit_col):
    """GN group: instance the children of `kit_col` on points by `idx`, rotation `rot` (euler), scale `scl`."""
    name = "GN_Instance_" + kit_col.name
    ng = bpy.data.node_groups.get(name)
    if ng:
        return ng
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    n = ng.nodes
    gi, go = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
    ci = n.new("GeometryNodeCollectionInfo")
    ci.transform_space = "ORIGINAL"
    ci.inputs["Separate Children"].default_value = True
    ci.inputs["Reset Children"].default_value = True
    iop = n.new("GeometryNodeInstanceOnPoints")
    iop.inputs["Pick Instance"].default_value = True

    def named(name, kind):
        a = n.new("GeometryNodeInputNamedAttribute")
        a.data_type = kind
        a.inputs["Name"].default_value = name
        return a.outputs["Attribute"]

    e2r = n.new("FunctionNodeEulerToRotation")
    ng.links.new(named("rot", "FLOAT_VECTOR"), e2r.inputs["Euler"])
    ng.links.new(gi.outputs[0], iop.inputs["Points"])
    ci.inputs["Collection"].default_value = kit_col
    ng.links.new(ci.outputs["Instances"], iop.inputs["Instance"])
    ng.links.new(named("idx", "INT"), iop.inputs["Instance Index"])
    ng.links.new(e2r.outputs["Rotation"], iop.inputs["Rotation"])
    ng.links.new(named("scl", "FLOAT_VECTOR"), iop.inputs["Scale"])
    ng.links.new(iop.outputs["Instances"], go.inputs[0])
    return ng


class Layer:
    """Collects instances of one kit group."""

    def __init__(self, group):
        self.group = group
        self.pos, self.rot, self.scl, self.idx = [], [], [], []

    def add(self, x, y, z, yaw, scale, variant, tilt=(0.0, 0.0), squash=1.0):
        self.pos.append((x, y, z))
        self.rot.append((tilt[0], tilt[1], yaw))
        self.scl.append((scale, scale, scale * squash))
        self.idx.append(variant)

    def build(self, kit, col, name):
        if not self.pos:
            return None
        obj = point_cloud(name, self.pos, col, {"rot": ("FLOAT_VECTOR", self.rot), "scl": ("FLOAT_VECTOR", self.scl),
                                                "idx": ("INT", self.idx)})
        mod = obj.modifiers.new("Instances", "NODES")
        mod.node_group = instancer_tree(kit.group(self.group))
        return obj


# species: kit group, spacing (m), scale range, variant count taken from the kit, sink (m)
SPECIES = {
    "salvia": ("flower_salvia", 0.42, (0.9, 1.25), 0.0),
    "lavender": ("flower_lavender", 0.5, (1.0, 1.35), 0.0),
    "lupin": ("flower_lupin", 0.55, (0.9, 1.2), 0.0),
    "daisy": ("flower_daisy", 0.38, (0.9, 1.3), 0.0),
    "phlox": ("flower_pink", 0.45, (0.9, 1.3), 0.0),
    "heliophila": ("flower_blue", 0.9, (0.6, 0.9), 0.0),
    "yellow": ("flower_yellow", 0.35, (1.2, 1.7), 0.0),
    "gazania": ("flower_orange", 1.2, (0.45, 0.6), 0.0),
    "hosta": ("hosta", 0.55, (1.0, 1.5), 0.0),
    "fern": ("fern", 0.75, (0.9, 1.4), 0.0),
    "tuft": ("grass_tuft", 0.5, (1.8, 2.8), 0.02),
    "shrub": ("shrub", 0.8, (0.55, 1.0), 0.05),
    "shrub_big": ("shrub_big", 1.8, (0.6, 0.9), 0.05),
    "groundcover": ("groundcover", 0.3, (1.3, 2.2), 0.0),
}

# Planting per zone in two layers, as garden designers do: a green structure (shrubs, grasses, ferns) that
# covers the ground, and flower drifts interplanted as accents. zone -> (structure, accents, accent share)
ZONES = {
    "rim": ([("groundcover", 3), ("fern", 1), ("tuft", 1.2)], [], 0.0),
    "bank": ([("fern", 3), ("hosta", 2.5), ("tuft", 3), ("groundcover", 2), ("shrub", 1.2)],
             [("salvia", 1), ("heliophila", 1), ("daisy", 0.8), ("lupin", 0.5)], 0.4),
    "bed": ([("shrub", 3), ("tuft", 2.5), ("groundcover", 2), ("fern", 1), ("hosta", 1), ("shrub_big", 0.6)],
            [("salvia", 3), ("daisy", 2.5), ("phlox", 2.5), ("lavender", 2), ("lupin", 1.2), ("yellow", 0.6),
             ("heliophila", 0.8), ("gazania", 0.3)], 0.72),
    "back": ([("shrub_big", 3), ("shrub", 3), ("fern", 1.5), ("tuft", 1.5)], [("lupin", 1), ("salvia", 1)], 0.3),
}


class Planter:
    def __init__(self, site, kit):
        self.site = site
        self.kit = kit
        self.rnd = random.Random(L.SEED + 31)
        self.noise = ValueNoise(L.SEED + 32)
        self.layers = {}
        self.cells = {}

    def layer(self, group):
        if group not in self.layers:
            self.layers[group] = Layer(group)
        return self.layers[group]

    def variants(self, group):
        return len(self.kit.group(group).objects)

    # ------------------------------------------------------------ drifts

    def _cell_species(self, key_zone, cx, cy):
        """Species of one drift cell; `key_zone` = (zone, layer) with layer 0 = structure, 1 = accents
        (None when the cell carries no accent)."""
        key = (key_zone, cx, cy)
        if key not in self.cells:
            r = random.Random(hash(key) ^ L.SEED)
            zone, layer = key_zone
            items = ZONES[zone][layer]
            if layer == 1 and r.random() > ZONES[zone][2]:
                self.cells[key] = (None, cx + r.random(), cy + r.random())
                return self.cells[key]
            total = sum(w for _, w in items)
            pick = r.uniform(0, total)
            for sp, w in items:
                pick -= w
                if pick <= 0:
                    break
            self.cells[key] = (sp, cx + r.random(), cy + r.random())
        return self.cells[key]

    def species_at(self, zone, x, y, size=1.9, layer=0):
        gx, gy = x / size, y / size
        ix, iy = math.floor(gx), math.floor(gy)
        best, sp_best = 1e9, None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                sp, px, py = self._cell_species((zone, layer), ix + dx, iy + dy)
                d = (px - gx) ** 2 + (py - gy) ** 2
                if d < best:
                    best, sp_best = d, sp
        return sp_best

    # ------------------------------------------------------------ zones

    def zone(self, x, y):
        s = self.site
        if not s.in_plot(x, y, 0.3) or s.in_house(x, y, 1.2):
            return None
        d, _, hw, _ = s.stream_at(x, y)
        if d < hw + 0.15:
            return None
        pd = s.path_distance(x, y)
        lawn_w = 1.0 + 0.8 * (0.5 + 0.5 * self.noise.noise(x * 0.35, y * 0.35))
        if pd < lawn_w:
            return "lawn"
        # bridge landing and deck front stay open
        bx, by = L.BRIDGE["a"]
        if math.hypot(x - bx, y - by) < 1.6:
            return "lawn"
        fx, fy = L.FEATURE_BED["center"]
        if math.hypot(x - fx, y - fy) < L.FEATURE_BED["radius"]:
            return "feature"
        if d < hw + 0.75:
            return "rim"
        if d < hw + 2.4:
            return "bank"
        x0, y0, x1, y1 = L.PLOT
        if min(x1 - x, y1 - y, x - x0) < 3.0:
            return "back"
        return "bed"

    # ------------------------------------------------------------ passes

    def _place(self, sp, x, y, scale=None):
        group, spacing, (s0, s1), sink = SPECIES[sp]
        h = self.site.height(x, y)
        tilt = (self.rnd.uniform(-0.08, 0.08), self.rnd.uniform(-0.08, 0.08))
        self.layer(group).add(x, y, h - sink, self.rnd.uniform(0, 2 * math.pi),
                              scale if scale is not None else self.rnd.uniform(s0, s1),
                              self.rnd.randrange(self.variants(group)), tilt)

    def plant_beds(self, step=0.24):
        x0, y0, x1, y1 = L.PLOT
        s = self.site
        count = 0
        y = y0
        while y < y1:
            x = x0
            while x < x1:
                px, py = x + self.rnd.uniform(0, step), y + self.rnd.uniform(0, step)
                z = self.zone(px, py)
                if z in ("rim", "bank", "bed", "back", "feature"):
                    if z != "feature":
                        sp = self.species_at(z, px, py)
                        if self.rnd.random() < 1.35 * (step / SPECIES[sp][1]) ** 2:
                            self._place(sp, px, py)
                            count += 1
                        accent = self.species_at(z, px, py, size=1.4, layer=1) if ZONES[z][1] else None
                        if accent and self.rnd.random() < 1.1 * (step / SPECIES[accent][1]) ** 2:
                            self._place(accent, px, py)
                            count += 1
                    # low filler between the clumps so no bare soil shows
                    if self.rnd.random() < 0.8:
                        h = s.height(px, py)
                        g = "grass_short" if self.rnd.random() < 0.6 else "moss"
                        self.layer(g).add(px, py, h - 0.01, self.rnd.uniform(0, 6.28),
                                          self.rnd.uniform(2.0, 3.2) if g == "grass_short" else self.rnd.uniform(3, 6),
                                          self.rnd.randrange(self.variants(g)))
                x += step
            y += step
        for sp, x, y, scale in L.FEATURE_BED["plants"]:
            self._place(sp, x, y, scale)
            count += 1
        return count

    def plant_lawn(self, step=0.14):
        """Dense clumps of lawn grass along the paths and around the house."""
        x0, y0, x1, y1 = L.TERRAIN
        s = self.site
        n = 0
        y = y0
        while y < y1:
            x = x0
            while x < x1:
                px, py = x + self.rnd.uniform(0, step), y + self.rnd.uniform(0, step)
                if s.in_plot(px, py, -6) and self.zone(px, py) == "lawn" or \
                        (not s.in_plot(px, py) and s.in_plot(px, py, -6)):
                    if s.path_distance(px, py) > 0.05 and not s.in_house(px, py, 0.1):
                        d, _, hw, _ = s.stream_at(px, py)
                        if d > hw + 0.1:
                            g = "grass_lawn" if self.rnd.random() < 0.75 else "grass_short"
                            self.layer(g).add(px, py, s.height(px, py) - 0.01, self.rnd.uniform(0, 6.28),
                                              self.rnd.uniform(1.1, 1.6) if g == "grass_lawn" else
                                              self.rnd.uniform(1.6, 2.4),
                                              self.rnd.randrange(self.variants(g)))
                            n += 1
                x += step
            y += step
        return n

    def rocks(self):
        """Boulders lining the banks, bigger ones at the cascade lips, stones in the bed."""
        s = self.site
        st = s.stream
        rnd = self.rnd
        boulders = self.layer("rock_moss")
        big = self.layer("rock_boulder")
        small = self.layer("rock_small")
        pos = 0.0
        while pos < st.length:
            p, t = st.at(pos)
            n = Vector((-t.y, t.x, 0))
            hw = s.half_width(pos)
            pool = s.pool_at(pos)
            for side, row in ((-1, 0), (1, 0), (-1, 1), (1, 1)):
                if rnd.random() < (0.9 if row == 0 else 0.35):
                    off = hw + rnd.uniform(-0.3, 0.3) + row * rnd.uniform(0.5, 0.9)
                    q = p + n * side * off
                    if not s.in_plot(q.x, q.y, -10):
                        continue
                    size = rnd.uniform(0.25, 0.6) if row == 0 else rnd.uniform(0.2, 0.45)
                    layer = boulders if rnd.random() < 0.6 else big
                    base = 2.8 if layer is boulders else 2.2    # kit rocks are ~2–3 m
                    z = max(s.height(q.x, q.y), pool.level - 0.1)
                    layer.add(q.x, q.y, z - size * 0.35, rnd.uniform(0, 6.28), size * 2 / base,
                              rnd.randrange(self.variants(layer.group)),
                              (rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3)), squash=rnd.uniform(0.6, 1.0))
            # stones on the bed
            for _ in range(3):
                q = p + n * rnd.uniform(-hw, hw) * 0.9
                z = s.height(q.x, q.y)
                small.add(q.x, q.y, z - 0.01, rnd.uniform(0, 6.28), rnd.uniform(1.5, 4.0),
                          rnd.randrange(self.variants("rock_small")))
            pos += rnd.uniform(0.45, 0.8)
        # cascade lips: a weir of stones across the stream with the tongues pouring between them,
        # big rocks framing the fall and a couple in the plunge pool
        for c in s.cascades:
            p, t = st.at(c["s"])
            n = Vector((-t.y, t.x, 0))
            hw = s.half_width(c["s"])
            u = -1.15
            while u < 1.15:
                gap = next((tg for tg in c["tongues"] if abs(u - tg[0]) < tg[1] + 0.07), None)
                if gap:
                    u = gap[0] + gap[1] + 0.08
                    continue
                size = rnd.uniform(0.22, 0.38)
                q = p + n * hw * u + t * rnd.uniform(-0.05, 0.1)
                big.add(q.x, q.y, c["top"] - size * 0.55, rnd.uniform(0, 6.28), size * 2 / 2.2,
                        rnd.randrange(self.variants("rock_boulder")),
                        (rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2)), squash=rnd.uniform(0.7, 1.0))
                u += size * 1.3 / hw
            # a jumble at the foot of the step hides the cut face; smaller stones under the tongues
            u = -1.0
            while u < 1.0:
                under = any(abs(u - tg[0]) < tg[1] for tg in c["tongues"])
                size = rnd.uniform(0.1, 0.18) if under else rnd.uniform(0.2, 0.34)
                q = p + n * hw * u + t * rnd.uniform(0.12, 0.3)
                big.add(q.x, q.y, c["bottom"] - size * (0.6 if under else 0.35), rnd.uniform(0, 6.28), size * 2 / 2.2,
                        rnd.randrange(self.variants("rock_boulder")),
                        (rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3)), squash=rnd.uniform(0.6, 0.9))
                u += size * 1.1 / hw
            for side in (-1, 1):
                q = p + n * side * (hw + 0.25)
                size = rnd.uniform(0.55, 0.85)
                boulders.add(q.x, q.y, c["bottom"] - 0.1, rnd.uniform(0, 6.28), size * 2 / 2.8,
                             rnd.randrange(self.variants("rock_moss")), (0.0, 0.0), squash=rnd.uniform(0.8, 1.0))
            for _ in range(2):
                q = p + t * rnd.uniform(0.9, 1.8) + n * hw * rnd.uniform(-0.7, 0.7)
                big.add(q.x, q.y, c["bottom"] - 0.18, rnd.uniform(0, 6.28), rnd.uniform(0.12, 0.2),
                        rnd.randrange(self.variants("rock_boulder")), (0, 0), squash=0.7)
        # hero boulders from the layout
        names = {"boulder_a": 1, "boulder_b": 3, "boulder_c": 2, "boulder_d": 0}
        for key, x, y, yaw, scale, sink in L.BOULDERS:
            big.add(x, y, s.height(x, y) - sink, math.radians(yaw), scale, names[key] % self.variants("rock_boulder"))
        # scattered stones in the beds
        for _ in range(260):
            x = rnd.uniform(L.PLOT[0], L.PLOT[2])
            y = rnd.uniform(L.PLOT[1], L.PLOT[3])
            if self.zone(x, y) not in ("bed", "bank"):
                continue
            if rnd.random() < 0.75:
                small.add(x, y, s.height(x, y) - 0.02, rnd.uniform(0, 6.28), rnd.uniform(3, 7),
                          rnd.randrange(self.variants("rock_small")))
            else:
                boulders.add(x, y, s.height(x, y) - 0.1, rnd.uniform(0, 6.28), rnd.uniform(0.1, 0.2),
                             rnd.randrange(self.variants("rock_moss")))

    def trees(self):
        s = self.site
        kinds = {"oak": ("tree_oak", 2.0), "maple_red": ("tree_maple", 1.3), "fir": ("tree_fir", 1.0),
                 "fir_small": ("tree_fir_small", 1.0), "birch": ("tree_birch", 2.6)}
        for kind, x, y, yaw, scale in L.TREES:
            group, base = kinds[kind]
            self.layer(group).add(x, y, s.height(x, y) - 0.05, math.radians(yaw), base * scale,
                                  self.rnd.randrange(self.variants(group)))

    def forest(self, far_height):
        """Trees behind the fence and on the hills around (cheap LODs)."""
        rnd = random.Random(L.SEED + 41)
        s = self.site
        placed = 0
        for _ in range(9000):
            r = 26 + (rnd.random() ** 1.6) * 520
            a = rnd.uniform(-math.pi, math.pi)
            x, y = r * math.sin(a), 10 + r * math.cos(a)
            if s.in_plot(x, y, -2.5):
                continue
            # keep a clearing south of the plot open towards the front camera
            if y < -26 and abs(x) < 60:
                continue
            fir = rnd.random() < (0.35 if r < 120 else 0.6)
            group = "tree_fir_far" if fir else "tree_oak_far"
            sc = rnd.uniform(0.6, 1.1) if fir else rnd.uniform(1.6, 2.6)
            # towards the low sun only trees too short to shade the garden (shadow = height / tan(elevation))
            da = math.atan2(math.sin(a - math.radians(L.SUN["azimuth"])), math.cos(a - math.radians(L.SUN["azimuth"])))
            if abs(da) < math.radians(28):
                x0, y0, x1, y1 = L.PLOT
                edge = math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1))
                height = (17.0 if fir else 5.0) * sc
                if height > 0.8 * edge * math.tan(math.radians(L.SUN["elevation"])):
                    continue
            self.layer(group).add(x, y, far_height(x, y) - 0.2, rnd.uniform(0, 6.28), sc,
                                  rnd.randrange(self.variants(group)))
            placed += 1
        return placed

    def build(self, col):
        objs = []
        for group, layer in sorted(self.layers.items()):
            obj = layer.build(self.kit, col, "Scatter_" + group)
            if obj:
                objs.append(obj)
                print(f"scatter {group:16} {len(layer.pos):6d}", flush=True)
        return objs
