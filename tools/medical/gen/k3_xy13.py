"""XY-13 multifunctional trainer (four-piece: shoulder wheel, forearm rotation, wrist ext/flex, pulley weights),
kinesio-3. Cage of white square tubes; the twin pulley unit stands along the outside of the left face, the wrist box
on the left face near the front, the shoulder wheel with the forearm tray on the front face at the right."""
from k3_lib import *

W, Dd, H = 1400, 1280, 1800   # photo proportions (printed 1810 x 1470 does not match the photo, see notes)
d = D("xy-13", [W, Dd, H], {"frame": "plastic#eef0f1"})
S = 60
X0, X1 = 280, W - 30        # cage posts (centres)
Z0, Z1 = 30, 980
# corner posts, top ring, bottom ring
for k, (x, z) in enumerate(((X0, Z0), (X1, Z0), (X0, Z1), (X1, Z1))):
    sq(d, f"post{k}", [x, 0, z], [x, H - S / 2, z], S)
for nm, y in (("top", H - S / 2), ("bot", S / 2)):
    sq(d, f"{nm}-f", [X0, y, Z1], [X1, y, Z1], S)
    sq(d, f"{nm}-b", [X0, y, Z0], [X1, y, Z0], S)
    sq(d, f"{nm}-l", [X0, y, Z0], [X0, y, Z1], S)
    sq(d, f"{nm}-r", [X1, y, Z0], [X1, y, Z1], S)
d.box("feet", [X0 - 32, 0, Z0 - 32, X0 + 32, 6, Z0 + 32], "rubber", copies=[[X1 - X0, 0, 0], [0, 0, Z1 - Z0], [X1 - X0, 0, Z1 - Z0]])
# (review) the photo shows no inner frame: one mid ring at ~790 on all four faces (the front one carries the wheel's
# lower bracket, the left one the wrist rods)
YM = 790
for nm, a, b_ in (("mid-f", [X0, YM, Z1], [X1, YM, Z1]), ("mid-b", [X0, YM, Z0], [X1, YM, Z0]),
                  ("mid-l", [X0, YM, Z0], [X0, YM, Z1]), ("mid-r", [X1, YM, Z0], [X1, YM, Z1])):
    sq(d, nm, a, b_, 50)
d.decal("logo", [X1 - 160, H - 30, Z1 + 30.6], [60, 16], "gloss#2a62c8", face="front", soft=True)
# twin pulley weight unit along the outside of the left face, facing -x
pulley_unit(d, "pu-", [X0 - 35, 0, 120], "-x", W=760, Dp=220, H=H, ring_y=1250, stack_h=190, base_h=170,
            cuffs=True, cuff_y=930, ring_mat="plastic#1f4fc4", stack="acrylic#7cc9cfd0")
# (review) the white square post between the two columns, floor to cap
sq(d, "pu-cpost", [X0 - 145, 0, 120 + 380], [X0 - 145, H - 45, 120 + 380], 45)
# red straps round the weight stacks (sandbag harness)
for k, z in enumerate((120 + 190, 120 + 570)):
    d.strap(f"rstrap{k}", [[X0 - 255, 160, z - 60], [X0 - 262, 330, z - 40], [X0 - 262, 330, z + 40], [X0 - 255, 160, z + 60]],
            [14, 3], "fabric#d8344a", bend=30, soft=True)
    d.strap(f"rstrap2{k}", [[X0 - 255, 120, z - 30], [X0 - 266, 380, z], [X0 - 255, 120, z + 30]], [12, 3], "fabric#c42a40",
            bend=40, soft=True)
# wrist box on the left face near the front, facing -x
# (review) the box faces into the cage (the user stands inside); from outside the photo shows its plain back with a
# dark slot, its rods run from the mid ring to the top ring
gw = G(d, "wr-", [X0 - 20, 0, 860], "+x")
wrist_unit(gw, 0, 1350, H - 60, YM, knob="l")
d.decal("wr-slot", [X0 - 30.8, 1350, 860], [22, 70], "plastic#2a2c2f", face="left", soft=True)
# shoulder wheel + forearm tray on the front face, right part, standing proud of the face
gs = G(d, "sw-", [0, 0, Z1], "+z")
wheel_unit(gs, 960, 1250, H - 60, YM + 25, wheel_d=700, spokes=0, tray="r", rods_w=100, box_w=80)
d.box("sw-brk", [960 - 110, H - 60, Z1 + 20, 960 + 110, H - 20, Z1 + 110], "frame", r=4)
d.box("sw-brk2", [960 - 110, YM - 30, Z1 + 20, 960 + 110, YM + 25, Z1 + 110], "frame", r=4)
d.save()
