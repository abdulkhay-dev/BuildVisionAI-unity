"""Pneumatic compression XY-K-WIC-2 (LED panel in a half-dome). Writes only xy-k-wic-2.json.
Review 2026-10-02: the D panel measured on the photo is a half-ellipse ~340 wide x ~160 along its slope (not a flat
half-stadium 322 x 96), so the hump rises ~100 mm above the shell; hump = horizontal loft sections of that ellipse;
shell corners flare to the lip (crease facets); 5 blue oval keys + red one; light-blue knob; leg graphic."""
from p5lib import *
import math

W, DP = 420, 350
CX, CZ = W / 2, DP / 2
# D panel: half-ellipse A x S in its own plane, tilted back ALPHA from vertical; base at (Y0, ZF)
A, S, ALPHA = 170, 160, 50
Y0, ZF = 174, 300
ca, sa = math.cos(math.radians(ALPHA)), math.sin(math.radians(ALPHA))
RISE = S * ca
H = round(Y0 + RISE + 4)
d = D("xy-k-wic-2", [W, DP, H], {"blue": "plastic#a3bfe8", "shell": "gloss#f3f4f5", "frame": "plastic#9dbbee",
                                 "face": "plastic#b9bdd6", "black": "gloss#1c1d22", "red": "gloss#ff2a1f",
                                 "key": "gloss#2f62c8", "dark": "plastic#26282c", "knob": "plastic#8fb1ea"})
# light-blue tub; four corner feet following the rounded footprint (notches between them)
d.loft("tub", [sec(14, 404, 334, 40, CX, CZ), sec(55, 408, 338, 42, CX, CZ), sec(88, 410, 340, 42, CX, CZ)], "blue")
for i, (fx, fz) in enumerate(((8, 8), (W - 8 - 78, 8), (8, DP - 8 - 66), (W - 8 - 78, DP - 8 - 66))):
    rr = [6, 6, 6, 6]
    # corner order of rrect_pts: (x1,y0) (x1,y1) (x0,y1) (x0,y0) -> the outer corner gets the tub radius
    outer = {0: 3, 1: 0, 2: 2, 3: 1}[i]
    rr[outer] = 38
    d.slab(f"foot{i}", "top", rrect(fx, fz, fx + 78, fz + 66, rr), [0, 16], "blue", r=3)
# white shell: lip over the tub, corners flaring from a big top radius to a tighter skirt (crease facets)
d.loft("shell", [sec(84, 414, 344, 34, CX, CZ), sec(90, 420, 350, 36, CX, CZ), sec(118, 420, 350, 38, CX, CZ),
                 sec(160, 417, 347, 74, CX, CZ), sec(171, 410, 340, 70, CX, CZ), sec(177, 400, 330, 64, CX, CZ),
                 sec(180, 388, 318, 58, CX, CZ)], "shell")

def P(u, v, dz=0.0):                 # exact: local (x, y=Y0+v, z=ZF+dz) turned about x by -ALPHA
    return [CX + u, Y0 + v * ca + dz * sa, ZF + dz * ca - v * sa]

tilt = rot("x", -ALPHA, [CX, Y0, ZF])
# hump: horizontal sections of the tilted half-ellipse, front on the panel plane, rounded back
ZB, RB = 22, 90
secs = []
for k in range(13):
    t = RISE * (1 - (1 - k / 12) ** 1.6) if k < 12 else RISE - 1
    q = min(t / RISE, 0.985)
    w = 2 * (A - 3) * math.sqrt(1 - q * q)
    zf = ZF - 3 - t / ca * sa
    zb = ZB + RB * (1 - math.sqrt(1 - q * q))
    secs.append({"at": Y0 - 6 + t, "w": max(w, 30), "d": zf - zb, "r": min(28, w / 2 - 1, (zf - zb) / 2 - 1),
                 "cx": CX, "cz": (zf + zb) / 2})
secs[0]["at"] = Y0 - 6
d.loft("hump", secs, "shell")

def dpath(a, s, n=28):
    return poly([(CX + a * math.cos(math.pi * k / n), Y0 + s * math.sin(math.pi * k / n)) for k in range(n + 1)])

def dpts(a, s, y0, n=28):
    return [(CX + a * math.cos(math.pi * k / n), y0 + s * math.sin(math.pi * k / n)) for k in range(n + 1)]
# blue rim (raised ring) and the recessed lavender face
d.slab("rim", "front", poly(dpts(A, S, Y0)), [ZF - 4, ZF + 2], "frame", r=2, rot=tilt)
d.slab("face", "front", poly(dpts(A - 16, S - 19, Y0 + 9)), [ZF - 4, ZF + 3], "face", r=0.8, rot=tilt)
bead = [P((A - 6) * math.cos(math.pi * k / 24), 6 + (S - 12) * math.sin(math.pi * k / 24), 5) for k in range(25)]
d.tube("bead", bead + [P(-(A - 6), 5, 5), P(A - 6, 5, 5), bead[0]], 11, "frame", bend=8)
zf = ZF + 3
# logo + title, the LED windows 888 / 888 / 8 with red digits, text lines
d.decal("logo", [CX + 14, Y0 + 107, zf + 0.2], [10, 9], "front", "key", soft=True, rot=tilt)
d.decal("title", [CX + 38, Y0 + 107, zf + 0.2], [34, 6], "front", "plastic#4f6fb8", soft=True, rot=tilt)
for x0, x1, n in ((-46, 8, 3), (12, 60, 3), (65, 86, 1)):
    d.box(f"win{x0}", [CX + x0, Y0 + 71, zf - 1, CX + x1, Y0 + 92, zf + 1.2], "black", r=2, rot=tilt)
    step = (x1 - x0 - 6) / n
    for k in range(n):
        d.box(f"dig{x0}-{k}", [CX + x0 + 4 + step * k, Y0 + 75, zf + 1.1, CX + x0 + step * (k + 1), Y0 + 88, zf + 1.6],
              "red", soft=True, rot=tilt)
d.decal("txt1", [CX - 92, Y0 + 58, zf + 0.2], [52, 4], "front", "plastic#6d7690", soft=True, rot=tilt)
d.decal("txt2", [CX - 112, Y0 + 30, zf + 0.2], [40, 3], "front", "plastic#6d7690", soft=True, rot=tilt)
d.decal("txt3", [CX - 108, Y0 + 22, zf + 0.2], [58, 2.5], "front", "plastic#7d86a0", soft=True, rot=tilt)
for k in range(4):
    d.cyl(f"led{k}", P(-43 + 25 * k, 55, 1), P(-43 + 25 * k, 55, 2.6), 6.5, "dark")
# white leg graphic: foot (toe up) at the left, thigh at the right, segment lines
leg = poly([(CX + u, Y0 + v) for u, v in ((-72, 34), (-62, 25), (-40, 27), (-8, 25), (33, 25), (33, 46), (-8, 41),
                                           (-44, 37), (-57, 39), (-59, 52), (-67, 51))])
d.slab("leg", "front", leg, [zf, zf + 0.8], "plastic#ffffff", r=0.3, rot=tilt, soft=True)
for k, u in enumerate((-40, -14, 10)):
    d.decal(f"legline{k}", [CX + u, Y0 + 34, zf + 0.9], [1.2, 14], "front", "plastic#55607a", soft=True, rot=tilt)
# light-blue knob with a dark scale arc, blue oval keys (2 columns: 3 + 2) and the red oval key bottom right
d.cyl("knob-arc", P(54, 37, 1), P(54, 37, 1.4), 47, "dark", soft=True)
d.cyl("knob-arc-in", P(54, 37, 1.4), P(54, 37, 1.8), 44, "face", soft=True)
d.cyl("knob", P(54, 37, 1.8), P(54, 37, 19), 32, "knob")
d.cyl("knob-top", P(54, 37, 19), P(54, 37, 20.5), 28, "gloss#a6c2f0")
for i, (ku, kv) in enumerate(((102, 69), (127, 68), (103, 49), (129, 50), (101, 30))):
    d.slab(f"key{i}", "front", rrect(CX + ku - 11, Y0 + kv - 7.5, CX + ku + 11, Y0 + kv + 7.5, 7.4), [zf, zf + 3.5],
           "key", r=1.2, rot=tilt)
d.slab("key-red", "front", rrect(CX + 117, Y0 + 24, CX + 141, Y0 + 38, 6.9), [zf, zf + 3.5], "red", r=1.2, rot=tilt)
# right side: socket block across the seam, dark-blue recess with two sockets; power socket behind it at the lip
d.box("sock-block", [412, 44, 222, 436, 124, 318], "shell", r=6)
d.box("sock-recess", [434, 56, 234, 437.5, 112, 306], "plastic#2b4f88", r=3)
d.box("sock", [436, 70, 248, 439.5, 98, 264], "dark", r=2, copies=[[0, 0, 30]])
d.box("power", [410, 66, 186, 418, 88, 206], "dark", r=2)
d.save()
