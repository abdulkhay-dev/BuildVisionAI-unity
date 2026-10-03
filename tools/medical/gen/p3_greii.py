"""XY-K-GR-EII portable interferential unit: blue bumper shell, white front frame with the black face, rotary knob in the
white chin, standing tilted back ~20° on a white plastic kickstand."""
from p3lib import *

d = D("xy-k-gr-eii", [125, 175, 205], {
    "blue": "plastic#2f9bd8", "white": "gloss#f4f5f7", "face": "gloss#141517", "grid": "plastic#3a3e44", "seam": "plastic#1f6fa8", "win": "plastic#2e3238",
    "knob": "metal#e2e4e7", "logo": "gloss#2f7fd0", "go": "gloss#35c46a", "stop": "gloss#ef7a2a", "rocker": "rubber#151617",
    "stand": "plastic#e3e6ea", "foot": "rubber#2a2b2d", "led": "gloss#58c070"})
ZF, ZB, PY = 150, 110, 12                 # front / back of the body (upright), pivot height
R = rot("x", -20, [0, PY, ZF])
def b(id, box, mat, r=None, **kw): return d.box(id, box, mat, r=r, rot=R, **kw)
# body: blue back/side shell, white front frame, black face
b("shell", [0, PY, ZB, 125, PY + 200, ZF - 5], "blue", r=14)
b("frame", [4, PY + 3, ZF - 9, 121, PY + 197, ZF], "white", r=8)
b("seam", [-0.5, PY + 10, ZF - 30, 125.5, PY + 190, ZF - 29], "seam", soft=True)
# the black face runs down to a thin white bottom rim; the white notch with the knob cuts into it from below
import math as _m
arc = [(62.5 + 22 * _m.cos(_m.radians(a)), PY + 26 + 22 * _m.sin(_m.radians(a))) for a in range(180, -1, -20)]
pts = [(9, PY + 9), (40.5, PY + 9), (40.5, PY + 26)] + arc[1:-1] + [(84.5, PY + 26), (84.5, PY + 9), (116, PY + 9), (116, PY + 191), (9, PY + 191)]
rad = [7, 3, 0] + [0] * (len(arc) - 2) + [0, 3, 7, 7, 7]
d.slab("face", "front", rpoly(pts, rad), [ZF - 1, ZF + 1.2], "face", r=0.8, rot=R)
b("keys", [16, PY + 56, ZF + 1, 32, PY + 66, ZF + 1.6], "grid", soft=True, copies=[[38, 6, 0], [76, 0, 0]])
# printed channel grid at the top of the face, segment windows, LED rows
for k in range(8):
    b(f"chan{k}", [18 + 12.5 * k, PY + 130, ZF + 1, 22 + 12.5 * k, PY + 182, ZF + 1.6], "grid", soft=True)
b("chan-line", [14, PY + 126, ZF + 1, 111, PY + 127.5, ZF + 1.6], "grid", soft=True)
for k, (x0, y0, w, h) in enumerate(((40, 100, 22, 18), (66, 100, 22, 18), (90, 100, 14, 18), (22, 74, 26, 20), (54, 74, 26, 20), (86, 74, 24, 20))):
    b(f"win{k}", [x0, PY + y0, ZF + 1, x0 + w, PY + y0 + h, ZF + 1.6], "win", soft=True)
b("leds", [24, PY + 88, ZF + 1, 104, PY + 89.5, ZF + 1.8], "grid", soft=True)
b("btn-key", [18, PY + 102, ZF + 1, 32, PY + 112, ZF + 2], "grid", r=2, soft=True)
# chin: knob in the white notch, green start and orange stop ring buttons
d.add("knob", "lathe", "knob", at=[62.5, PY + 26, ZF], axis="z", profile=[[0, 0], [15, 0], [15, 14], [13.5, 18], [0, 18]], rot=R)
d.add("knob-knurl", "lathe", "grid", at=[62.5, PY + 26, ZF + 2], axis="z", profile=[[15.2, 0], [15.6, 0], [15.6, 8], [15.2, 8]], rot=R, soft=True)
d.add("knob-cap", "lathe", "logo", at=[62.5, PY + 26, ZF + 18], axis="z", profile=[[0, 0], [7, 0], [7, 1.5], [0, 1.5]], rot=R)
d.add("knob-ring", "lathe", "white", at=[62.5, PY + 26, ZF - 1], axis="z", profile=[[0, 0], [21, 0], [21, 3], [0, 3]], rot=R)
# start ▶ (green ring) and stop ■ (orange ring) on the black face at its lower corners, either side of the notch
for nm, x, m in (("go", 25, "go"), ("stop", 100, "stop")):
    d.add(nm, "lathe", m, at=[x, PY + 24, ZF + 1], axis="z", profile=[[8, 0], [10, 0], [10, 1.5], [8, 1.5]], rot=R, soft=True)
    b(nm + "-ico", [x - 2.5, PY + 21.5, ZF + 1, x + 2.5, PY + 26.5, ZF + 2.2], m, soft=True)
# rocker switch on the right side
b("rocker", [124, PY + 120, ZB + 8, 128, PY + 142, ZB + 22], "rocker", r=2)
# kickstand: two flat white legs from the back down to the floor, cross bar and foot
TOP = [0, PY + 150, ZB]                         # local attach point (upright) → world, by hand: tilted 20° back about the pivot
import math
a = math.radians(20)
def w(y, z):
    yr, zr = y - PY, z - ZF
    return PY + yr * math.cos(a) + zr * math.sin(a), ZF - yr * math.sin(a) + zr * math.cos(a)
ty, tz = w(PY + 150, ZB)
for x in (16, 109):
    d.add(f"leg{x}", "bar", "stand", **{"from": [x, ty, tz + 4], "to": [x, 6, 6]}, section=[14, 7], r=2)
d.add("cross", "bar", "stand", **{"from": [10, 6, 10], "to": [115, 6, 10]}, section=[26, 10], r=3)
d.add("hinge", "bar", "stand", **{"from": [10, ty, tz + 3], "to": [115, ty, tz + 3]}, section=[10, 8], r=3)
d.add("brace", "bar", "stand", **{"from": [16, 34, 20], "to": [109, 34, 20]}, section=[6, 6], r=2)
d.save()
