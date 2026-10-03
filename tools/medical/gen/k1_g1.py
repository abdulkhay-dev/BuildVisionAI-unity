"""xy-k-g1: manual BWS gait frame (printed 120 x 109 x 180 cm). Column at the back centre, legs run forward,
top arm bends forward to the black foam top bar that hangs the harness; patient stands in the front half."""
from k1lib import *

d = D("xy-k-g1", [1090, 1200, 1800], {
    "cream": "plastic#efe9d6", "chrome": "chrome", "foam": "rubber#1e1f21", "black": "plastic#1b1c1e",
    "web": "fabric#1c1d20", "mesh": "fabric#6e625a", "blue": "gloss#2347c8", "grey": "rubber#6f7378"})
CX, CZ = 545, 200
# --- floor legs along z with braked grey castors at both ends
for x in (60, 1030):
    d.cyl(f"leg-{x}", [x, 105, 40], [x, 105, 1160], 40, "cream")
    d.sphere(f"leg-end-{x}", [x, 105, 40], 40, "cream", copies=[[0, 0, 1120]])
    d.add(f"castor-{x}", "caster", "grey", at=[x, 0, 70], d=75, copies=[[0, 0, 1060]])
# --- raised hub at the back centre; double curved tubes sweeping down to each leg
d.box("hub", [CX - 70, 495, CZ - 70, CX + 70, 525, CZ + 70], "cream", r=8)
for s in (-1, 1):
    for dz in (-32, 32):
        z = CZ + dz
        x0, x1 = CX + s * 40, (60 if s < 0 else 1030)
        d.tube(f"sweep-{'l' if s < 0 else 'r'}{dz}", [[x0, 510, z], [CX + s * 260, 470, z + 20], [x1 - s * 50, 260, z + 70],
                                                      [x1, 108, z + 140]], 34, "cream", bend=160)
# --- column: outer tube, inner telescopic tube, black clamp pin, top bending forward into the bar arm
d.box("column", [CX - 40, 520, CZ - 40, CX + 40, 1260, CZ + 40], "cream", r=6)
d.box("column-collar", [CX - 46, 1240, CZ - 46, CX + 46, 1275, CZ + 46], "cream", r=6)
d.box("column-inner", [CX - 31, 1260, CZ - 31, CX + 31, 1640, CZ + 31], "cream", r=5)
d.box("clamp", [CX + 40, 1150, CZ - 18, CX + 70, 1240, CZ + 18], "black", r=5)
d.cyl("clamp-pin", [CX + 70, 1200, CZ], [CX + 110, 1200, CZ], 16, "black")
d.box("rack", [CX - 12, 1270, CZ - 46, CX + 12, 1460, CZ - 31], "black", r=3)
d.sweep("top-arm", [[CX, 1620, CZ], [CX, 1760, CZ], [CX, 1760, 440]], [62, 62], "cream", bend=120, r=6)
# --- black foam top bar with chrome caps and a blue label, hooks hanging the harness
TZ, TY = 445, 1760
# the photo shows the arm clamping the bar ~70 % along it (toward +x): the bar and the harness hanging from it
# sit ~115 mm to -x of the column
BX = CX - 115
d.box("bar-clamp", [CX - 45, TY - 40, TZ - 40, CX + 45, TY + 40, TZ + 40], "cream", r=10)
d.cyl("top-bar", [BX - 265, TY, TZ], [BX + 265, TY, TZ], 52, "foam")
d.cyl("top-cap", [BX - 283, TY, TZ], [BX - 263, TY, TZ], 46, "chrome", copies=[[546, 0, 0]])
d.cyl("top-label", [BX + 55, TY, TZ], [BX + 175, TY, TZ], 55, "blue")
for x in (BX - 195, BX + 195):
    d.cyl(f"hook-stem-{x}", [x, TY - 26, TZ], [x, TY - 60, TZ], 12, "chrome")
    d.tube(f"hook-ring-{x}", [[x, TY - 60, TZ], [x - 18, TY - 80, TZ], [x, TY - 100, TZ], [x + 18, TY - 80, TZ],
                              [x, TY - 60, TZ]], 8, "chrome", bend=12)
# --- handrails: crossbar through the column at ~850, black foam handles pointing forward
HY = 850
d.cyl("rail-cross", [300, HY, CZ], [790, HY, CZ], 34, "cream")
d.box("rail-joint", [CX - 50, HY - 30, CZ - 50, CX + 50, HY + 30, CZ + 50], "cream", r=6)
for x in (300, 790):
    d.box(f"rail-elbow-{x}", [x - 24, HY - 24, CZ - 24, x + 24, HY + 24, CZ + 24], "chrome", r=8)
    d.cyl(f"handle-{x}", [x, HY, CZ + 20], [x, HY, CZ + 340], 42, "foam")
    d.sphere(f"handle-end-{x}", [x, HY, CZ + 340], 42, "foam")
# --- black harness: shoulder straps from the hooks, crossed strap, blue tabs, vest with mesh sides, leg loops
HZ = 440
for s, x in ((-1, BX - 195), (1, BX + 195)):
    xv = BX + s * 150
    d.strap(f"shoulder-{x}", [[x, TY - 100, TZ], [x, 1500, HZ], [xv, 1300, HZ + 10]], [45, 4], "web", bend=80, soft=True)
    d.box(f"tab-{x}", [x + s * 2 - 22, 1380, HZ - 6, x + s * 2 + 22, 1460, HZ + 8], "blue", r=4, soft=True)
    d.box(f"buckle-{x}", [x - 18, 1560, HZ - 4, x + 18, 1572, HZ + 6], "chrome", r=2, soft=True)
d.strap("cross-strap", [[BX - 193, 1650, TZ], [BX, 1450, HZ + 4], [BX + 155, 1280, HZ + 10]], [50, 4], "web", bend=80, soft=True, roll=90)
# brown mesh triangles on the vest's upper front, narrowing up to the shoulder straps (photo)
for s_ in (-1, 1):
    xa, xb, xt = BX + s_ * 205, BX + s_ * 75, BX + s_ * 155
    tri = f"M {min(xa, xb)} 1200 L {max(xa, xb)} 1200 L {xt + 12} 1330 L {xt - 12} 1330 Z"
    d.slab(f"vest-mesh-{s_}", "front", tri, [540, 556], "mesh", r=3, soft=True)
d.box("vest", [BX - 210, 1010, 330, BX + 210, 1215, 550], "web", r=35, puff=6, soft=True)
d.box("vest-buckle", [BX - 25, 1080, 557, BX + 25, 1110, 566], "chrome", r=3, soft=True)
for s in (-1, 1):
    xc = BX + s * 85
    d.box(f"leg-buckle-{s}", [xc - 12, 950, 520, xc + 12, 990, 530], "chrome", r=3, soft=True)
    d.strap(f"leg-loop-{s}", [[xc - 50, 1015, 500], [xc - 70, 820, 490], [xc, 700, 470], [xc + 70, 820, 490],
                              [xc + 50, 1015, 500]], [40, 4], "web", bend=70, soft=True)
    d.box(f"leg-pad-{s}", [xc - 65, 700, 420, xc + 65, 770, 510], "web", r=20, puff=5, soft=True)
d.save()
