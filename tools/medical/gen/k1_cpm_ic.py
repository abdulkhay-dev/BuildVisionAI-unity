"""xy-cpm-ic: elbow CPM desk unit. Front = the membrane panel face. Hinge axis along z on the box top near -x;
forearm cradle over the box toward +x, upper-arm frame rising toward -x at 45 deg (as in the photo)."""
import math
from k1lib import *

d = D("xy-cpm-ic", [660, 380, 620], {
    "white": "gloss#f4f5f6", "panel": "plastic#c6cad0", "lcd": "gloss#a9bd8a", "key": "gloss#1f3f8f",
    "chrome": "chrome", "black": "plastic#18191b", "sling": "fabric#1c1d20", "blue": "gloss#2a7fd0"})
X0, Z0, Z1 = 290, 20, 260
# --- white box, grey front panel (LCD, 6 keys, green rocker), inlet + blue label + DB9 on the +x side
BW = 300   # the box is ~1.4x wider than tall (both photos); the panel covers only its right ~57 %
d.box("box", [X0, 0, Z0, X0 + BW, 210, Z1], "white", r=24)
PX = X0 + 118
d.box("panel", [PX, 22, Z1 - 1, PX + 170, 196, Z1 + 2.5], "panel", r=5)
d.box("lcd", [PX + 12, 126, Z1 + 2, PX + 112, 170, Z1 + 3.5], "lcd", r=3, soft=True)
d.box("key", [PX + 12, 92, Z1 + 2, PX + 30, 106, Z1 + 5], "key", r=3, soft=True, repeat=rep(4, [26, 0, 0]))
d.box("key-r", [PX + 140, 150, Z1 + 2, PX + 158, 166, Z1 + 5], "key", r=3, soft=True, copies=[[0, -26, 0]])
d.box("key-z", [PX + 134, 58, Z1 + 2, PX + 162, 96, Z1 + 5], "key", r=3, soft=True)
d.box("rocker-frame", [PX + 8, 34, Z1 + 2, PX + 46, 72, Z1 + 5], "black", r=3)
d.box("rocker", [PX + 14, 40, Z1 + 4, PX + 40, 66, Z1 + 10], "gloss#1f9a4a", r=3)
d.decal("panel-text", [PX + 88, 70, Z1 + 2.8], [70, 8], "front", "plastic#7d828a", soft=True, copies=[[0, -16, 0], [0, -28, 0]])
d.decal("panel-logo", [PX + 20, 186, Z1 + 2.8], [14, 10], "front", "blue", soft=True)
d.box("inlet", [X0 + BW - 2, 70, 150, X0 + BW + 4, 112, 196], "black", r=4)
d.decal("label", [X0 + BW + 0.6, 120, 80], [50, 100], "right", "blue", soft=True)
d.box("db9", [X0 + BW - 2, 160, 40, X0 + BW + 24, 196, 92], "plastic#9a9da2", r=5)
d.cyl("screw", [X0 + 70, 14, Z1], [X0 + 70, 14, Z1 + 3], 8, "chrome", soft=True, copies=[[200, 0, 0]])
# --- hinge: chrome fins on the box top, hubs (axis z) with blue logo, axle
HX, HY = X0 + 60, 268
for nm, z in (("b", 62), ("f", 218)):
    d.box(f"fin-{nm}", [HX - 40, 205, z - 3, HX + 70, 250, z + 3], "chrome", r=2, rot=rot("z", 18, [HX + 15, 228, z]))
d.box("hinge-base", [HX - 30, 206, 50, HX + 130, 214, 230], "chrome", r=3)
d.cyl("hub-b", [HX, HY, 30], [HX, HY, 68], 56, "chrome")
d.cyl("hub-f", [HX, HY, 212], [HX, HY, 250], 56, "chrome")
d.lathe("hub-logo-f", [HX, HY, 250], [[0, 0], [8, 0], [8, 1], [0, 1]], "blue", axis="z")
d.lathe("hub-logo-b", [HX, HY, 29], [[0, 0], [8, 0], [8, 1], [0, 1]], "blue", axis="z")
# --- forearm cradle: two chrome rods along +x over the box, black end caps, black sling with straps
for nm, z in (("b", 72), ("f", 208)):
    d.cyl(f"fore-rod-{nm}", [HX, HY, z], [628, HY, z], 16, "chrome")
    d.cyl(f"fore-cap-{nm}", [626, HY, z], [648, HY, z], 20, "black")
d.box("fore-sling", [HX + 50, 236, 66, HX + 330, 266, 214], "sling", r=12, puff=5)
d.strap("fore-strap", [[HX + 150, 272, 60], [HX + 150, 286, 140], [HX + 150, 272, 220]], [45, 3], "sling", bend=50,
        soft=True, copies=[[130, 0, 0]])
# --- upper-arm frame: U of chrome rods rising toward -x at 45 deg, black sling, clamp plate and knobs
L = 470
c, s = math.cos(math.radians(45)), math.sin(math.radians(45))
TX, TY = HX - L * c, HY + L * s
d.tube("upper-frame", [[HX, HY, 72], [TX, TY, 72], [TX, TY, 208], [HX, HY, 208]], 14, "chrome", bend=30)
mx, my = HX - 0.55 * L * c, HY + 0.55 * L * s
d.box("upper-sling", [mx - 125, my - 16, 66, mx + 125, my + 12, 214], "sling", r=12, puff=4,
      rot=rot("z", -45, [mx, my, 140]))
d.strap("upper-strap", [[mx, my, 60], [mx - 14, my + 14, 140], [mx, my, 220]], [45, 3], "sling", bend=50, soft=True)
d.box("end-plate", [TX + 10, TY - 60, 80, TX + 20, TY + 10, 200], "chrome", r=3, rot=rot("z", -45, [TX, TY, 140]))
d.box("end-clamp", [TX - 6, TY - 12, 64, TX + 30, TY + 12, 216], "chrome", r=4, rot=rot("z", -45, [TX, TY, 140]))
kx, ky = HX - 0.3 * L * c, HY + 0.3 * L * s
d.box("slide-clamp", [kx - 18, ky - 14, 206, kx + 18, ky + 14, 226], "chrome", r=4, rot=rot("z", -45, [kx, ky, 216]))
d.lathe("star-knob", [kx, ky, 226], [[0, 0], [8, 0], [8, 10], [22, 12], [22, 30], [0, 32]], "black", axis="z", sides=8)
d.lathe("tip-knob", [TX + 30, TY - 40, 216], [[0, 0], [6, 0], [6, 8], [16, 10], [16, 24], [0, 26]], "black", axis="z",
        sides=8)
# --- hand controller in front right, coiled cable to the DB9
controller(d, "controller", 480, 292, [X0 + BW + 24, 178, 66])
d.save()
