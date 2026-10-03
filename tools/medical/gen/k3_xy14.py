"""XY-14 multifunctional trainer (seven-piece), kinesio-3.

Review 2026-10-03 (layout re-read from both photos: photo 2 is from the front-left, photo 1 from the back-right):
- the wall bars are the RIGHT face (+x), the chest-and-back straightener stands outside the LEFT face facing out
  (-x, its black back to the cage), the twin pulley weights fill the front face's LEFT half, the finger ladder is on
  the back-left post (photo 1) — the first draft had all of this mirrored;
- the anklebone tilt board faces the front in the right part of the cage, leaning back onto a top cross beam, its
  grey foot cradle with castors and the yellow-gripped handles standing at the front face;
- the thing above the top is the gallows (post from the front mid beam to 2390, arm to +x with a gusset, two pulleys,
  a white D ring and a blue ring), not a tall backboard: the hoop hangs from a small white board under the back top;
- the cage is 1880 high (photo 2: the gallows rises a third above it), the wall-bar posts 2060."""
from k3_lib import *

H, HC, HWB = 2390, 1880, 2060
X0, X1, Z0, Z1 = 1410, 2810, 30, 1330
d = D("xy-14", [2840, 1360, H], {"frame": "plastic#eef0f1", "grey": "leather#9aa0a6"})
cage(d, "", X0, X1, Z0, Z1, HC, S=60, rings=[(1000, "fbl")], posts_h={1: HWB, 3: HWB})
sq(d, "front-up", [X0, 1340, Z1], [X1, 1340, Z1], 50)
sq(d, "top-x", [X0, HC - 30, 600], [X1, HC - 30, 600], 50)
# wall bars = the right face
gwb = G(d, "wb-", [X1, 0, Z1], "+x")
gwb.cyl("rung", [30, 220, 0], [Z1 - Z0 - 30, 220, 0], 34, "frame", repeat={"n": 11, "step": [0, 175, 0]})
# anklebone tilt board in the right part, facing the front, leaning back onto the top cross beam
XC = X1 - 400
Bz, By, Tz, Ty = 1150, 170, 650, 1860
L = math.hypot(Bz - Tz, Ty - By)
ang = -math.degrees(math.atan2(Bz - Tz, Ty - By))
rb = {"axis": "x", "deg": ang, "about": [XC, By, Bz]}
d.box("ab-board", [XC - 300, By, Bz - 35, XC + 300, By + L, Bz + 35], "grey", r=22, puff=4, rot=rb)
d.box("ab-back", [XC - 285, By + 40, Bz - 45, XC + 285, By + L - 40, Bz - 33], "plastic#d6d9dc", rot=rb)
for k, dx in enumerate((-120, 120)):   # two light foot slots in the lower board
    d.box(f"ab-slot{k}", [XC + dx - 45, By + 120, Bz + 35, XC + dx + 45, By + 520, Bz + 38], "plastic#e9ebed", r=40, rot=rb)
# foot cradle: a grey wedge at the front with two tilted foot plates and heel stops
d.slab("ab-base", "side", f"M {Bz - 160} 0 L 1355 0 L 1355 70 L {Bz + 40} 300 L {Bz - 160} 160 Z", [XC - 330, XC + 330],
       "plastic#a7adb3", r=10)
for k, dx in enumerate((-120, 120)):
    d.box(f"ab-foot{k}", [XC + dx - 75, 150, Bz + 40, XC + dx + 75, 172, Bz + 200], "plastic#8f959b", r=8,
          rot={"axis": "x", "deg": -18, "about": [XC, 160, Bz + 40]})
d.caster("ab-cas", [XC - 290, 0, 1300], 60, copies=[[580, 0, 0]])
# handles rising at the cradle's sides, yellow grips pointing forward
for k, s in enumerate((-1, 1)):
    x = XC + s * 380
    d.tube(f"ab-h{k}", [[XC + s * 320, 40, 1250], [x, 40, 1250], [x, 840, 1150], [x, 860, 1000]], 28, "frame", bend=60)
    d.cyl(f"ab-hg{k}", [x, 862, 1010], [x + s * 10, 870, 1230], 40, "gloss#e7b23a")
# basketball hoop under the back top: small white board, ring into the cage, red/white net
XH = X0 + 620
HY = 1640
d.box("bb-board", [XH - 220, HY, Z0 + 30, XH + 220, HC - 60, Z0 + 55], "frame", r=8)
d.box("bb-sq", [XH - 100, HY + 30, Z0 + 55, XH + 100, HY + 140, Z0 + 58], "plastic#c9ced3")
R = 200
HCz = Z0 + 75 + R
d.tube("bb-hoop", ring(XH, HY, HCz, R, R, "xz", 32), 16, "frame")
d.box("bb-brk", [XH - 50, HY - 70, Z0 + 55, XH + 50, HY + 8, Z0 + 80], "frame", r=4)
net(d, "bb-net", [XH, HY - 10, HCz], R - 8, 100, 380, n=14, rows=6, white=0.4, d_=7)
# finger ladder on the back-left post, teeth facing out of the back
gl = G(d, "fl-", [0, 0, Z0 - 30], "-z")
finger_ladder(gl, -(X0 + 130), 1050, HC - 60, w=0)
# twin pulley weights in the front face's left half
pulley_unit(d, "pu-", [X0 + 50, 0, Z1 - 260], "+z", W=560, Dp=200, H=HC - 60, ring_y=1250, stack_h=170, base_h=150,
            top_label=False, ring_mat="plastic#2350c0", stack="acrylic#8fd3d6c8")
# gallows on the front face: post from the mid beam, arm to +x with a gusset, two pulleys, a white D ring and a blue ring
XG = X0 + 640
gallows(d, "ga-", XG, Z1, 1000, H, XG + 520, ring_y=1360, n=2, ring_mat="plastic#2350c0")
d.slab("ga-gus", "front", f"M {XG + 25} {H - 50} L {XG + 230} {H - 50} L {XG + 25} {H - 260} Z", [Z1 - 6, Z1 + 6], "frame", r=3)
for p in d.d["parts"]:
    if p["id"] == "ga-ring1": p["mat"] = "plastic#f4f4f0"     # the near-post rope ends in a white D ring
# two triangular slings hanging from the top cross beam
for k, x in enumerate((X0 + 380, X0 + 560)):
    d.cyl(f"sl-rope{k}", [x, HC - 55, 600], [x, 1620, 600], 6, "plastic#f2f2ee", soft=True)
    d.tube(f"sl-tri{k}", [[x, 1620, 600], [x - 70, 1460, 600], [x + 70, 1460, 600], [x, 1620, 600]], 10, "plastic#cfd3d6", soft=True)
    d.cyl(f"sl-grip{k}", [x - 60, 1455, 600], [x + 60, 1455, 600], 30, "gloss#c8333a")
# chest-and-back straightener outside the left face, facing out (-x), its black back to the cage
s0 = len(d.d["parts"])
straightener(d, "st-", 1810, 0, top=1880, bottom_y=620, board_z=(690, 250), loop=True, back="plastic#2a2d31")
turn_y(d, s0, -90, [1280, 0, 0])
d.save()
