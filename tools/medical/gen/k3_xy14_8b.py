"""XY-14-8B multifunctional trainer (eight-piece, with training table), kinesio-3. Cube frame on castors with a wire
mesh roof and a wire grid on the back face; twin pulley weights on the left face, a wrist box on the left face front,
forearm box with tray and a crank wrist box on the back grid, finger ladder, ropes with rings, traction slings,
low 3-section training table inside."""
from k3_lib import *

W, Dd, H = 2480, 2480, 2200
d = D("xy-14-8b", [W, Dd, H], {"frame": "plastic#eef0f1", "pad": "leather#8e9399", "grid": "metal#dcdfe2"})
# (review) the cage stops 250 short of the front: the gallows arm and the floor outrigger stand out in front of it
# (photo 1), so the printed 2480 depth includes them
X0, X1, Z0, Z1 = 30, W - 30, 30, Dd - 250
B = 105
cage(d, "", X0, X1, Z0, Z1, H, S=55, rings=[(1080, "fblr"), (1720, "bl"), (B + 420, "l")], feet=False, base=B)
d.caster("cas", [X0, 0, Z0 + 20], 75, copies=[[X1 - X0, 0, 0], [0, 0, Z1 - Z0], [X1 - X0, 0, Z1 - Z0]])
# wire mesh roof ((review) as fine as the back grid, ~110 cells)
d.cyl("roof-x", [X0, H - 12, Z0 + 110], [X1, H - 12, Z0 + 110], 5, "grid", repeat=rep(19, [0, 0, 110]))
d.cyl("roof-z", [X0 + 110, H - 12, Z0], [X0 + 110, H - 12, Z1], 5, "grid", repeat=rep(21, [110, 0, 0]))
# (review) floor outrigger in front: from the front castors it angles out ~200 and runs along the front (photo 1)
d.tube("outrig", [[X0 + 20, 28, Z1 - 10], [X0 + 200, 28, Z1 + 200], [X1 - 420, 28, Z1 + 200], [X1 - 230, 28, Z1 - 10]],
       45, "frame", bend=20)
# (review) small gallows arm out of the front-left corner top: arm forward with a brace along the left face, a pulley
# at its tip, the rope down to a blue ring outside the cage at ~1000
sq(d, "gal-arm", [X0, H - 40, Z1 - 350], [X0, H - 40, Z1 + 225], 45)
sq(d, "gal-brace", [X0, H - 40, Z1 - 300], [X0, H - 330, Z1 - 30], 40)
d.add("gal-pul", "wheel", "plastic#3a3d42", at=[X0, H - 95, Z1 + 200], d=70, d2=22, axis="x")
d.cyl("gal-rope", [X0, H - 130, Z1 + 225], [X0, 1060, Z1 + 225], 6, "plastic#f2f2ee", soft=True)
d.tube("gal-ring", ring(X0, 1010, Z1 + 225, 40, 50, "zy", 16), 16, "plastic#2350c0", soft=True)
# wire grid on the back face from the mid ring to the top
d.cyl("grid-v", [X0 + 110, 1080, Z0 + 10], [X0 + 110, H - 30, Z0 + 10], 6, "grid", repeat=rep(21, [110, 0, 0]))
d.cyl("grid-h", [X0, 1080 + 110, Z0 + 10], [X1, 1080 + 110, Z0 + 10], 6, "grid", repeat=rep(9, [0, 110, 0]))
d.decal("lbl", [X1 + 28, 1500, Z1 - 200], [14, 300], "gloss#2f62c4", face="right", soft=True)
# twin pulley weights inside the left face, facing +x
# (review) photo 1: the columns stand in the back half of the left face, grey cuff blocks at the mid ring, clear
# water-bottle weights
pulley_unit(d, "pu-", [X0 + 40, B, 1150], "+x", W=760, Dp=200, H=H - B - 40, ring_y=1350, stack_h=180, base_h=130,
            top_label=True, ring_mat="plastic#2350c0", cuffs=True, cuff_y=1000, stack="acrylic#9fd8dccc")
for p_ in d.d["parts"]:
    if p_["id"].startswith("pu-cuff") and not p_["id"].startswith("pu-cuffb"): p_["mat"] = "plastic#8a93a2"
# wrist / forearm carriage on the left face near the front, facing +x
gw = G(d, "wr-", [X0 + 30, 0, Z1 - 230], "+x")
wrist_unit(gw, 0, 1300, 1720, 1080, knob="l")
# back grid: forearm box with tray and a crank wrist box, facing +z
gf = G(d, "fa-", [0, 0, Z0 + 40], "+z")
wheel_unit(gf, 1250, 1380, 1720, 1080, wheel_d=0, tray="r", rods_w=0, box_w=10)
gk = G(d, "wk-", [0, 0, Z0 + 40], "+z")
wrist_unit(gk, 2150, 1550, 1720, 1080, knob="r")
gk.cyl("crank", [2250, 1550, 140], [2330, 1550, 140], 30, "chrome")
gk.cyl("crank-g", [2330, 1550, 140], [2330, 1450, 140], 28, "plastic#1d1e20")
# finger ladder on the back face at the right
gl = G(d, "fl-", [0, 0, Z0 + 30], "+z")
finger_ladder(gl, 2350, 1100, 2050, w=0)
# (review) two pulleys under the roof near the back-left corner, ropes down to blue D rings just above the mid ring
for k, z in enumerate((330, 110)):
    x = X0 + 200 + 120 * k
    d.add(f"pul{k}", "wheel", "plastic#3a3d42", at=[x, H - 75, z], d=70, d2=22, axis="x")
    d.cyl(f"rope{k}", [x, H - 110, z], [x, 1250, z], 6, "plastic#f2f2ee", soft=True)
    d.tube(f"ring{k}", ring(x, 1205, z, 55, 40, "zy", 16), 14, "plastic#2350c0", soft=True)
# black traction slings hanging from the roof in front of the grid
for k, x in enumerate((1550, 1800)):
    d.cyl(f"sling-r{k}", [x, H - 20, 300], [x, 1350, 300], 6, "plastic#2a2c30", soft=True)
    d.strap(f"sling{k}", [[x - 70, 1350, 300], [x - 80, 1000, 320], [x, 930, 340], [x + 80, 1000, 320], [x + 70, 1350, 300]],
            [120, 5], "fabric#1e2128", bend=80, soft=True)
# training table: 3 grey padded sections on a white frame with trestle legs, two grey straps
TX0, TX1, TZ0, TZ1, TY = 290, 2190, 930, 1580, 450
d.box("t-frame", [TX0 + 20, TY - 110, TZ0 + 20, TX1 - 20, TY - 70, TZ1 - 20], "frame", r=4)
d.decal("t-lbl", [TX0 + 300, TY - 90, TZ1 - 19.4], [220, 16], "gloss#2f62c4", face="front", soft=True)
segs = [(TX0, TX0 + 620), (TX0 + 630, TX0 + 1260), (TX0 + 1270, TX1)]
for k, (a, b) in enumerate(segs):
    d.box(f"t-pad{k}", [a, TY - 70, TZ0, b, TY, TZ1], "pad", r=18, puff=6)
for k, x in enumerate((TX0 + 950, TX0 + 1150)):
    d.strap(f"t-belt{k}", [[x, TY - 60, TZ0 - 5], [x, TY + 8, TZ0 + 40], [x, TY + 8, TZ1 - 40], [x, TY - 60, TZ1 + 5]],
            [110, 5], "fabric#8a8f95", bend=20, soft=True)
for k, x in enumerate((TX0 + 220, TX1 - 220)):
    for z in (TZ0 + 60, TZ1 - 60):
        sq(d, f"t-leg{k}{z}", [x - 60, 0, z], [x + 60, TY - 110, z], 40)
    sq(d, f"t-legx{k}", [x - 50, 150, TZ0 + 60], [x - 50, 150, TZ1 - 60], 35)
    d.box(f"t-foot{k}", [x - 90, 0, TZ0 + 35, x - 30, 20, TZ0 + 85], "plastic#2a2b2d", copies=[[0, 0, TZ1 - TZ0 - 120]])
print(bbox(d))
d.save()
