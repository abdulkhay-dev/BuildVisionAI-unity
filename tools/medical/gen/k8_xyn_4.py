"""XYN-4 wall pulley exerciser: a chrome wall rail, a white square post sliding in it (sleeve with black knobs), a
white arm out from the wall with a brace, a grey roller with two pulley blocks, black ropes, two blue hand rings.
Wall at z = 0; the arm runs out along z."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

W, DP, H = 350, 410, 1620   # printed 430: the drawn parts span 350 across x (see review)
d = D("xyn-4", [W, DP, H], {"frame": "plastic#f1f1ee", "chrome": "chrome", "grey": "metal#9a9ea3", "black": "plastic#1b1c1e",
                            "rope": "fabric#1a1b1d", "ring": "gloss#1f3fae", "cream": "plastic#ece6cf"})
CX = W / 2
# wall rail with a dark slot, white wall brackets at its ends
d.box("rail", [CX - 22, 15, 4, CX + 22, 1110, 34], "chrome", r=3)
d.decal("rail-slot", [CX, 420, 34.6], [12, 700], "front", "plastic#1f3a3a")
for k, (y0, y1) in (("t", (1030, 1100)), ("b", (25, 90))):
    d.box(f"wb-{k}", [CX - 55, y0, 0, CX + 55, y1, 6], "frame", r=3)
    d.box(f"wbs-{k}", [CX - 30, y0 + 5, 4, CX + 30, y1 - 5, 36], "frame", r=3)
    d.cyl(f"wbh-{k}", [CX - 40, (y0 + y1) / 2, 6], [CX - 40, (y0 + y1) / 2, 7.5], 12, "grey", copies=[[80, 0, 0]])
# post in front of the rail, sleeve clamping both
d.box("post", [CX - 20, 430, 38, CX + 20, H, 78], "frame", r=3)
d.box("sleeve", [CX - 30, 520, 2, CX + 30, 780, 86], "frame", r=5)
d.decal("sleeve-slot", [CX, 650, 86.6], [10, 160], "front", "plastic#c9ccd0")
for y in (560, 750):
    star_knob(d, f"sknob{y}", [CX - 30, y, 45], "x", -1, "black", dd=30, l=26)
d.box("post-cap", [CX - 20, 428, 38, CX + 20, 436, 78], "black", r=2)
# arm out from the wall, brace, bolts, end cap
AY0, AY1 = H - 42, H - 2
d.box("arm", [CX - 20, AY0, 38, CX + 20, AY1, DP - 12], "frame", r=3)
d.box("arm-cap", [CX - 20, AY0, DP - 14, CX + 20, AY1, DP - 4], "black", r=3)
d.bar("brace", [CX, 1250, 60], [CX, AY0 + 6, 255], [36, 24], "frame", r=3)
for z in (58, 160, 300):
    d.cyl(f"bolt{z}", [CX - 21, AY0 + 20, z], [CX - 24, AY0 + 20, z], 12, "grey", copies=[[48, 0, 0]])
d.cyl("bolt-b", [CX - 21, 1265, 58], [CX - 24, 1265, 58], 12, "grey", copies=[[48, 0, 0]])
# roller across x under the arm end, two pulley blocks on swivel hooks, rope between them
RZ = DP - 40
d.box("yoke", [CX - 12, AY0 - 40, RZ - 14, CX + 12, AY0, RZ + 14], "frame", r=3)
d.cyl("roller", [CX - 125, AY0 - 45, RZ], [CX + 125, AY0 - 45, RZ], 40, "grey")
d.cyl("pin", [CX, AY1, RZ], [CX, AY1 + 14, RZ], 14, "grey")
d.cyl("roller-cap", [CX - 137, AY0 - 45, RZ], [CX - 123, AY0 - 45, RZ], 44, "black", copies=[[260, 0, 0]])
for k, x in (("l", CX - 105), ("r", CX + 105)):
    d.cyl(f"hook-{k}", [x, AY0 - 65, RZ], [x, AY0 - 110, RZ], 8, "chrome")
    d.lathe(f"swivel-{k}", [x, AY0 - 130, RZ], [[0, 0], [9, 0], [11, 10], [6, 22], [0, 24]], "chrome")
    d.box(f"block-{k}", [x - 22, AY0 - 210, RZ - 14, x + 22, AY0 - 128, RZ + 14], "cream", r=9)
    d.cyl(f"sheave-{k}", [x, AY0 - 175, RZ - 15], [x, AY0 - 175, RZ + 15], 34, "plastic#4a4d52")
d.decal("block-num", [CX - 105, AY0 - 150, RZ + 14.6], [10, 14], "front", "plastic#2a2c2f")
d.cyl("rope-x", [CX - 105, AY0 - 190, RZ], [CX + 105, AY0 - 190, RZ], 5, "rope", soft=True)


def hand_ring(k, x, yc, z, tilt):
    """blue rubber hand ring Ø150 as a band (two tubes), tilted `tilt` deg back from vertical; returns the top point"""
    t = math.radians(tilt)
    nrm = [0, math.sin(t), -math.cos(t)]        # band width direction (ring axis)
    pts = []
    for i in range(25):
        a = 2 * math.pi * i / 24
        u, v = 70 * math.cos(a), 70 * math.sin(a)
        pts.append([x + u, yc + v * math.cos(t), z + v * math.sin(t)])
    for j, s in enumerate((-7, 7)):
        d.tube(f"ring-{k}{j}", [[p[0] + nrm[0] * s, p[1] + nrm[1] * s, p[2] + nrm[2] * s] for p in pts], 13, "ring", soft=True)
    return [x, yc + 70 * math.cos(t), z + 70 * math.sin(t)]


top_l = hand_ring("l", CX - 105, 190, 150, 35)
top_r = hand_ring("r", CX + 105, 380, 185, 30)
d.cyl("rope-l", [CX - 105, AY0 - 210, RZ], top_l, 5, "rope", soft=True)
d.cyl("rope-r", [CX + 105, AY0 - 210, RZ], top_r, 5, "rope", soft=True)
d.save()
