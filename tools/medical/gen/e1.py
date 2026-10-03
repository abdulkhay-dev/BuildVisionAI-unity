from pfx_lib import *
# mobile manual body-weight-support frame: open base (two legs), column at the rear centre, overhead arm forward
d = D("xy-k-e1", [900, 1100, 1900], {
  "white": "plastic#f2f2f2", "chrome": "chrome", "steel": "metal#d2d5d9", "black": "rubber#1c1d1f",
  "harness": "fabric#1e2022", "blue": "fabric#2b6fd0", "grey": "plastic#9aa0a8", "green": "fabric#5e8f3a",
  "pad": "fabric#26282b"})
XL, CX, CZ = 70, 450, 150
# --- base legs with telescopic joint brackets, castors, curved struts arching to the column foot
d.bar("leg", [XL, 125, 50], [XL, 125, 1070], [40, 32], "white", r=6, mirror="x")
d.box("leg-joint", [XL - 26, 105, 470, XL + 26, 145, 560], "white", r=6, mirror="x")
d.decal("leg-screw", [XL - 26.5, 125, 490], [8, 8], "left", "grey", soft=True, mirror="x", copies=[[0, 0, 50]])
d.box("leg-cap", [XL - 22, 108, 1062, XL + 22, 142, 1076], "grey", r=6, mirror="x", copies=[[0, 0, -1022]])
d.add("castor", "caster", "rubber#cfd2d6", at=[XL, 0, 80], d=100, mirror="x", copies=[[0, 0, 960]])
# the column foot sits high (~470) on the photo: the struts rise from the legs' rear parts and arch over to it
d.tube("strut", [[XL, 140, 200], [XL + 10, 330, 190], [XL + 120, 450, 170], [CX - 40, 468, CZ]], 36, "white",
       bend=160, mirror="x")
# --- column: chrome square in two sections with flanges, white tube and overhead arm, push handle, hooks
d.box("col-foot", [CX - 75, 455, CZ - 75, CX + 75, 475, CZ + 75], "steel", r=4)
d.box("column", [CX - 30, 475, CZ - 30, CX + 30, 1090, CZ + 30], "chrome", r=4)
d.box("column-up", [CX - 34, 1120, CZ - 34, CX + 34, 1480, CZ + 34], "chrome", r=4)
d.box("col-flange", [CX - 60, 1475, CZ - 60, CX + 60, 1490, CZ + 60], "steel", r=3)
d.sweep("overhead", [[CX, 1485, CZ], [CX, 1870, CZ], [CX, 1880, 360], [CX, 1860, 560], [CX, 1875, 770]],
        [40, 40], "white", shape="round", bend=110)
d.lathe("overhead-cap", [CX, 1875, 770], [[0, 0], [22, 0], [22, 14], [0, 16]], "grey", axis="z")
d.bar("handle-post", [CX, 1880, 200], [CX + 60, 1890, 200], [24, 24], "white", r=10)
d.cyl("push-handle", [CX + 60, 1890, 170], [CX + 60, 1890, 330], 34, "white")
d.lathe("push-handle-cap", [CX + 60, 1890, 330], [[0, 0], [19, 0], [19, 12], [0, 14]], "grey", axis="z")
HM, HF = 470, 720            # hooks: mid, front
for nm, z in (("m", HM), ("f", HF)):
    d.coil(f"hook-{nm}", [CX, 1855, z], [CX, 1790, z], 26, 6, 2, "steel")
    d.tube(f"hook-clip-{nm}", [[CX, 1790, z], [CX, 1760, z - 12], [CX, 1735, z], [CX, 1760, z + 12], [CX, 1790, z]],
           7, "steel", bend=10)
# --- handrails: T clamp on the column with a knob, two black foam bars forward
d.box("rail-clamp", [CX - 200, 1090, CZ - 30, CX + 200, 1122, CZ + 30], "steel", r=8)
d.lathe("rail-knob", [CX + 30, 1106, CZ + 30], [[0, 0], [8, 0], [8, 18], [22, 22], [22, 40], [0, 42]], "black", axis="z")
d.cyl("handrail", [CX - 175, 1135, 70], [CX - 175, 1135, 710], 42, "black", mirror="x")
d.cyl("handrail-mount", [CX - 175, 1122, CZ], [CX - 175, 1135, CZ], 50, "steel", mirror="x")
# --- harness: flat straps, blue pads, padded vest with green lining, thigh cuffs
VZ = 600
S = [44, 3]
d.strap("strap-l", [[CX, 1735, HF], [CX - 60, 1550, HF - 40], [CX - 150, 1080, VZ + 40]], S, "harness", bend=60, soft=True)
d.strap("strap-x", [[CX, 1735, HF], [CX + 40, 1500, HF - 50], [CX + 130, 1080, VZ + 60]], S, "harness", bend=60, soft=True)
d.strap("strap-r", [[CX, 1735, HM], [CX + 60, 1550, HM + 60], [CX + 150, 1080, VZ - 30]], S, "harness", bend=60, soft=True)
d.bar("pad-roll-r", [CX + 12, 1715, HM + 10], [CX + 30, 1630, HM + 30], [60, 40], "pad", r=18, soft=True)
d.bar("blue-pad-l", [CX - 96, 1420, VZ + 75], [CX - 126, 1300, VZ + 57], [62, 22], "blue", r=10, soft=True)
d.bar("blue-pad-r", [CX + 98, 1430, VZ + 2], [CX + 122, 1320, VZ - 14], [50, 18], "blue", r=8, soft=True)
d.loft("vest", [sec(860, 340, 250, 110, CX, VZ), sec(960, 370, 270, 120, CX, VZ), sec(1080, 350, 260, 115, CX, VZ)],
       "harness", caps=False, soft=True)
d.loft("vest-lining", [sec(1050, 330, 238, 105, CX, VZ), sec(1082, 338, 244, 108, CX, VZ)], "green", caps=False, soft=True)
d.strap("vest-belt", [[CX - 185, 900, VZ], [CX, 895, VZ + 140], [CX + 185, 900, VZ]], [40, 4], "harness", bend=120, soft=True)
d.box("vest-buckle", [CX - 24, 880, VZ + 135, CX + 24, 920, VZ + 146], "grey", r=4, soft=True)
d.strap("loose-strap", [[CX - 175, 900, VZ + 40], [CX - 210, 720, VZ + 50], [CX - 220, 540, VZ + 40]], [40, 3], "harness",
        bend=60, soft=True)
for nm, s in (("l", -1), ("r", 1)):
    x = CX + s * 90
    d.coil(f"clip-{nm}", [x, 855, VZ + 60], [x, 800, VZ + 60], 20, 5, 2, "steel", soft=True)
    d.strap(f"thigh-strap-{nm}", [[x, 800, VZ + 60], [x + s * 10, 730, VZ + 70], [x + s * 15, 660, VZ + 75]], [36, 3],
            "harness", bend=40, soft=True)
    d.loft(f"thigh-cuff-{nm}", [sec(530, 170, 170, 85, x + s * 15, VZ), sec(600, 180, 180, 90, x + s * 15, VZ),
                                sec(670, 170, 170, 85, x + s * 15, VZ)], "pad", caps=False, soft=True)
d.save()
