"""xyrt-43 — sliding board: soft stair block (2 steps + platform) and a long slope, light-blue tops, white sides
with animal decals, light-wood rails, a scooter board on the platform."""
from pd3_lib import *

W, Dp, H = 3350, 910, 550
d = D("xyrt-43", [W, Dp, H], {"blue": "leather#bad2ea", "side": "leather#f1f3f5", "wood": "wood#e8d3a2",
                              "grey": "leather#8e959c"})
s1, s2, xp, xs = 310, 610, 1240, 1240     # step ends, platform end = slope start
h1, h2 = 183, 367
# stair block (blue body) + white side panels
stair = f"M 0 0 L {xp} 0 L {xp} {H} L {s2} {H} L {s2} {h2} L {s1} {h2} L {s1} {h1} L 0 {h1} Z"
d.slab("stair", "front", stair, [6, Dp - 6], "blue", r=14)
for nm, w in (("f", [Dp - 8, Dp]), ("b", [0, 8])):
    d.slab(f"stair-side-{nm}", "front", f"M 8 4 L {xp - 8} 4 L {xp - 8} {H - 22} L {s2 + 8} {H - 22} L {s2 + 8} {h2 - 22} "
           f"L {s1 + 8} {h2 - 22} L {s1 + 8} {h1 - 22} L 8 {h1 - 22} Z", w, "side", r=3)
# slope block
yE = 40
slope = f"M {xs + 6} 0 L {W} 0 L {W} {yE} L {xs + 6} {H} Z"
d.slab("slope", "front", slope, [6, Dp - 6], "blue", r=14)
for nm, w in (("f", [Dp - 8, Dp]), ("b", [0, 8])):
    d.slab(f"slope-side-{nm}", "front", f"M {xs + 14} 4 L {W - 10} 4 L {W - 10} {yE - 14} L {xs + 14} {H - 22} Z", w, "side", r=3)
# wooden rails: platform edges then down the slope edges
rw, rh = 60, 62
for nm, z0 in (("f", Dp - rw - 2), ("b", 2)):
    d.box(f"rail-p-{nm}", [s2 + 2, H - 4, z0, xs, H + rh - 4, z0 + rw], "wood", r=8)
    d.slab(f"rail-s-{nm}", "front", f"M {xs} {H - 4} L {W - 15} {yE - 4} L {W - 15} {yE + rh - 4} L {xs} {H + rh - 4} Z",
           [z0, z0 + rw], "wood", r=8)
# scooter board on the platform
bx0, bx1, bz0, bz1 = 760, 1150, 280, 620
for k, (x, z) in enumerate([(bx0 + 50, bz0 + 50), (bx1 - 50, bz0 + 50), (bx0 + 50, bz1 - 50), (bx1 - 50, bz1 - 50)]):
    d.add(f"sc-w{k}", "wheel", "rubber#1d1e20", at=[x, H + 22, z], d=44, d2=22, axis="x")
d.box("scooter", [bx0, H + 40, bz0, bx1, H + 82, bz1], "grey", r=16, puff=4)
d.box("scooter-base", [bx0 + 15, H + 34, bz0 + 15, bx1 - 15, H + 44, bz1 - 15], "plastic#3a3e44", r=4)
# label + logo at the top of the stair block's front side
d.box("label", [930, 470, Dp, 1200, 500, Dp + 1.5], "plastic#cfe4f6", r=2, soft=True)
d.box("label-txt", [945, 481, Dp + 1, 1185, 489, Dp + 2], "plastic#3d76b8", r=1, soft=True)
d.box("logo", [640, 478, Dp, 700, 496, Dp + 1.5], "plastic#3d76b8", r=2, soft=True)
# animal silhouettes (1 mm slabs on the front side)
def animal(id, path, col, ox, oy, sc):
    import re
    nums = re.split(r"([MLQCZ])", path)
    out = []
    for t in nums:
        t = t.strip()
        if not t: continue
        if t in "MLQCZ": out.append(t); continue
        v = [float(a) for a in t.replace(",", " ").split()]
        out.append(" ".join(f"{ox + v[i] * sc:.1f} {oy - v[i + 1] * sc:.1f}" for i in range(0, len(v), 2)))
    d.slab(id, "front", " ".join(out), [Dp, Dp + 1.2], col, soft=True)
# grasshopper (unit drawing, y down, head left)
GH = ("M 0 40 Q 5 25 25 25 L 60 22 Q 120 18 170 28 Q 185 35 170 44 Q 120 52 60 50 L 25 52 Q 5 52 0 40 Z")
HL = ("M 88 32 Q 108 -4 138 -22 Q 152 -28 156 -12 L 192 58 L 182 62 L 148 2 Q 132 22 124 38 Z")  # thick femur
for nm, pth in (("hopper-body", GH), ("hopper-hind", HL)):
    animal(nm, pth, "plastic#2f8a3a", 760, 330, 1.75)
def stroke(id, a, b, wd=7):
    import math
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    L = math.hypot(b[0] - a[0], b[1] - a[1]); ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    d.box(id, [cx - L / 2, cy - wd / 2, Dp, cx + L / 2, cy + wd / 2, Dp + 1.2], "plastic#2f8a3a", soft=True,
          rot=rot("z", ang, [cx, cy, Dp]))
# legs and antennae in design mm (x right, y up): body underside at y ~ 240
stroke("hopper-l1", [810, 245], [790, 205]); stroke("hopper-l1b", [790, 205], [775, 200])
stroke("hopper-l2", [860, 243], [850, 200]); stroke("hopper-l2b", [850, 200], [835, 196])
stroke("hopper-ant", [770, 270], [700, 300], 5); stroke("hopper-ant2", [775, 275], [715, 320], 5)
# rooster
# rooster facing left (photo): comb, beak, wattle, full breast, four sickle tail feathers sweeping up and back,
# a leg with a foot
RO = ("M 22 38 L 36 30 Q 34 20 40 16 Q 42 6 50 12 Q 54 2 62 10 Q 68 4 70 16 Q 74 20 68 26 Q 74 34 72 46 "
      "Q 76 66 92 76 Q 104 70 112 60 Q 118 20 150 8 Q 176 2 190 22 Q 170 14 150 24 Q 182 18 196 46 Q 176 36 156 44 "
      "Q 190 46 198 78 Q 178 62 160 66 Q 188 82 186 112 Q 170 92 156 92 Q 150 118 128 132 Q 118 140 110 142 "
      "L 112 170 L 124 180 L 100 180 L 104 172 L 100 144 Q 80 140 66 120 Q 54 100 56 78 Q 54 62 48 52 "
      "Q 44 62 40 64 Q 36 56 40 50 L 36 44 Z")
animal("rooster", RO, "plastic#d42a24", 1450, 400, 1.45)
# kangaroo
KA = ("M 0 40 Q 10 20 25 22 L 35 8 L 40 24 Q 60 30 70 50 Q 100 50 120 70 Q 150 90 190 92 Q 150 100 120 92 "
      "L 110 110 L 70 112 L 80 100 Q 55 90 50 60 Q 30 52 0 40 Z")
animal("kangaroo", KA, "plastic#2a44b0", 2280, 230, 1.0)
d.save()
