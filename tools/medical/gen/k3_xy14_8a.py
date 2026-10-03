"""XY-14-8A multifunctional trainer (eight-piece, A), kinesio-3. Sides as in the photos (photo 1 is taken from the
front-right): twin pulley weights inside the front face, a gallows with hand rings over the front-left corner,
wall bars along the right face with the forearm box (tray) and the wrist box (wooden bar) outside them and the green
shoulder-lifting peg rack, the 3-spoke shoulder wheel on the left face, the finger ladder on the back-left post (review 2026-10-03)."""
from k3_lib import *

H = 2390
X0, X1, Z0, Z1 = 720, 1880, 300, 1440
HC = 2000
d = D("xy-14-8a", [2350, 1700, H], {"frame": "plastic#eef0f1"})
cage(d, "", X0, X1, Z0, Z1, HC, S=60, rings=[(1050, "fblr"), (1950, "")])
# wall bars along the right face (taller posts), rungs
XW = X1 + 110
gwb = G(d, "wb-", [XW, 0, Z1], "+x")
wall_bars(gwb, 0, Z1 - Z0, 300, 2250, w=0, n=13, post=60, rung=34)
gwb.box("cap0", [-30, 2330, -30, 30, 2334, 30], "plastic#2a2b2d", copies=[g_step(gwb, [Z1 - Z0, 0, 0])])
for k, y in enumerate((1050, 1950)):
    sq(d, f"wb-tie{k}", [X1, y, Z0], [XW, y, Z0], 50, copies=[[0, 0, Z1 - Z0]])
# twin pulley weights inside the front face ((review) photo 1: the hand rings hang at ~1330)
pulley_unit(d, "pu-", [X0 + 40, 0, Z1 - 230], "+z", W=780, Dp=200, H=HC - 40, ring_y=1330, stack_h=180, base_h=150,
            cuffs=True, cuff_y=1000, stack="plastic#2b2e33", ring_mat="plastic#2a2f8f")
# gallows (pulley ring exerciser) over the front-left post
# (review) photo 1: both ropes run over pulleys at the arm's tip, the two rings hang side by side at ~1260
gallows(d, "ga-", X0, Z1, HC, H, 60, ring_y=1260, n=2, ring_mat="plastic#262c7a", gap=95, tip=40)
# outside the wall bars: forearm box with tray (front part) and wrist box with a wooden bar (back part), facing +x
gf = G(d, "fa-", [XW + 60, 0, 0], "+x")
# (review) the tray reaches to the back (photo 1), the wrist box sits at the back end of the wall bars at ~1450
wheel_unit(gf, -(Z1 - 190), 1220, 1950, 950, wheel_d=0, tray="r", rods_w=0, box_w=20)
gk = G(d, "wk-", [XW + 60, 0, 0], "+x")
wrist_unit(gk, -(Z0 + 200), 1450, 1950, 1050, bar=180)
# (review) green shoulder-lifting peg rack hung on the INSIDE of the wall bars (photo 1: its uprights show behind the
# rungs, one by the front post, one by the back post; photo 2 shows it outside — the main photo is followed)
peg_rack(d, "pg-", XW - 35, Z0 + 230, Z1 - 260, 1050, 1900, n=7, side=-1)
# (review) shoulder wheel with three spokes on the LEFT face, facing out (-x): both photos show it on the face next to
# the gallows corner, its ring reaching past the corner post
gs = G(d, "sw-", [X0, 0, 0], "-x")
wheel_unit(gs, Z1 - 420, 1320, HC - 60, 1050, wheel_d=720, spokes=3, rods_w=60, box_w=80)
# (review) finger ladder on the back face by the back-LEFT post (photo 1: its white saw-tooth back shows through the
# cage behind the front-right post), teeth facing out of the back
gl = G(d, "fl-", [0, 0, Z0 - 30], "-z")
finger_ladder(gl, -(X0 + 130), 1050, 1950, w=0)
print(bbox(d))
d.save()
