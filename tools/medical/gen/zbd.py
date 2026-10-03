from pfx_lib import *
import math
# bedside unit: base and column at the back, boom reaching forward (+z) over the bed, motor drum with leg cradles at the front
d = D("xy-zbd-ic", [650, 1350, 1500], {
  "blue": "gloss#2f6fbf", "white": "plastic#eef0f2", "steel": "metal#c8ccd2", "black": "plastic#1d1f22",
  "pad": "leather#1f2023", "strap": "fabric#1a1b1d"})
CX = 325
# --- base: white housing with a rear chamfer, flat blue legs forward, castors front and rear
d.slab("housing", "side", "M 0 60 L 400 60 L 400 230 L 110 230 L 0 160 Z", [40, 610], "white", r=20)
d.box("leg", [50, 30, 0, 110, 62, 820], "blue", r=6, mirror="x")
d.add("castor", "caster", at=[80, 0, 790], d=60, mirror="x", copies=[[0, 0, -760]])
# --- column: blue lower, brushed silver telescopic upper
d.box("column", [CX - 50, 225, 130, CX + 50, 650, 230], "blue", r=8)
d.box("column-in", [CX - 42, 640, 138, CX + 42, 1125, 222], "steel", r=6)
d.box("column-collar", [CX - 54, 630, 126, CX + 54, 660, 234], "blue", r=8)
# --- bed-docking clamp: blue bar forward with knobs, black saddle under it, black U handle behind the column
d.box("clamp-sleeve", [CX - 55, 840, 122, CX + 55, 905, 238], "blue", r=10)
d.box("clamp-bar", [CX - 45, 860, 238, CX + 45, 900, 560], "blue", r=8)
d.slab("saddle", "side", "M 280 860 L 560 860 Q 560 740 420 735 Q 280 740 280 860 Z", [CX - 80, CX + 80], "pad", r=25)
d.lathe("clamp-knob", [CX, 900, 290], [[0, 0], [8, 0], [8, 16], [24, 20], [24, 38], [0, 40]], "black",
        copies=[[0, 0, 210]])
d.sweep("clamp-handle", [[CX - 70, 880, 122], [CX - 80, 880, 20], [CX + 80, 880, 20], [CX + 70, 880, 122]],
        [26, 26], "black", shape="round", bend=55)
# --- boom: blue block over the column, silver section with the logo plate, blue sleeve, joint block
d.box("boom-block", [CX - 55, 1120, 120, CX + 55, 1235, 240], "blue", r=10)
d.box("boom-silver", [CX - 42, 1130, 240, CX + 42, 1225, 470], "steel", r=6)
d.decal("boom-logo", [CX + 42.6, 1178, 355], [140, 50], "right", "plastic#dfe6f0", soft=True)
d.decal("boom-logo-mark", [CX + 43.2, 1178, 310], [28, 28], "right", "gloss#2f6fbf", soft=True)
d.decal("boom-logo-mark-l", [CX - 43.2, 1178, 310], [28, 28], "left", "gloss#2f6fbf", soft=True)
d.box("boom-sleeve", [CX - 50, 1122, 460, CX + 50, 1233, 560], "blue", r=8)
d.box("joint", [CX - 55, 1040, 560, CX + 55, 1235, 690], "blue", r=12)
d.decal("joint-panel", [CX + 55.6, 1140, 625], [110, 170], "right", "white", soft=True)
d.decal("joint-panel-l", [CX - 55.6, 1140, 625], [110, 170], "left", "white", soft=True)
d.lathe("joint-knob", [CX + 55, 1080, 625], [[0, 0], [10, 0], [10, 18], [30, 22], [30, 44], [0, 46]], "black", axis="x")
# --- arm from the joint block forward and slightly down to the drum
DZ, DY = 1000, 900
d.bar("arm", [CX, 1070, 650], [CX, DY + 90, DZ - 40], [90, 90], "blue", r=8)
d.box("arm-cap", [CX - 50, 1030, 660, CX + 50, 1120, 700], "white", r=10, rot=rot("x", 14, [CX, 1075, 680]))
# motor drum, axis across x, domed white faces
d.lathe("drum", [CX - 80, DY, DZ], [[0, 0], [120, 0], [150, 18], [160, 40], [160, 120], [150, 142], [120, 160], [0, 160]],
        "white", axis="x")
d.decal("drum-logo", [CX + 80.6, DY + 20, DZ], [70, 30], "right", "plastic#3a5f9f", soft=True)
# cranks at 180 deg, calf cradles (black pad in a white U shell), foot plate, straps
def cradle(nm, x, y, z0, z1):
    def U(r, t, yc):
        return (f"M {x - r} {yc + 45} L {x - r} {yc} Q {x - r} {yc - r} {x} {yc - r} Q {x + r} {yc - r} {x + r} {yc} "
                f"L {x + r} {yc + 45} L {x + r - t} {yc + 45} L {x + r - t} {yc} Q {x + r - t} {yc - r + t} {x} {yc - r + t} "
                f"Q {x - r + t} {yc - r + t} {x - r + t} {yc} L {x - r + t} {yc + 45} Z")
    d.slab(f"cradle-{nm}", "front", U(78, 12, y), [z0, z1], "black", r=5)
    d.slab(f"cradle-pad-{nm}", "front", U(66, 14, y), [z0 + 6, z1 - 6], "plastic#dcdfe2", r=6)
    d.strap(f"cradle-strap-{nm}", [[x - 78, y + 40, (z0 + z1) / 2], [x, y + 72, (z0 + z1) / 2], [x + 78, y + 40, (z0 + z1) / 2]],
            [45, 4], "strap", bend=50, soft=True)
    xk = x + 78 if x > CX else x - 78
    d.lathe(f"cradle-knob-{nm}", [xk, y - 20, (z0 + z1) / 2], [[0, 0], [8, 0], [8, 14], [20, 16], [20, 32], [0, 34]],
            "black", axis="x", rot=rot("y", 0 if x > CX else 180, [xk, y - 20, (z0 + z1) / 2]))
for nm, side, a in (("l", -1, 120), ("r", 1, 300)):
    ang = math.radians(a)
    py, pz = DY + 130 * math.sin(ang), DZ + 130 * math.cos(ang)
    xh = CX + side * 82           # drum face
    xp = CX + side * 175          # pedal / cradle centre
    d.cyl(f"crank-hub-{nm}", [xh, DY, DZ], [xh + side * 22, DY, DZ], 70, "steel")
    d.bar(f"crank-{nm}", [xh + side * 30, DY, DZ], [xh + side * 30, py, pz], [50, 22], "white", r=8)
    d.cyl(f"pedal-axle-{nm}", [xh + side * 20, py, pz], [xp, py, pz], 26, "steel")
    d.bar(f"strut-{nm}", [xp, py - 10, pz - 40], [xp, py - 10, pz + 270], [40, 20], "black", r=6)
    cradle(nm, xp, py + 50, pz - 30, pz + 170)
    # white foot plate at the front end with a black strap
    d.box(f"foot-plate-{nm}", [xp - 70, py - 40, pz + 180, xp + 70, py - 15, pz + 330], "white", r=10)
    d.strap(f"foot-strap-{nm}", [[xp - 70, py - 15, pz + 260], [xp, py + 30, pz + 262], [xp + 70, py - 15, pz + 260]],
            [40, 4], "strap", bend=30, soft=True)
# --- swivel touch screen on top of the column block
d.cyl("swivel", [CX, 1235, 180], [CX, 1275, 180], 60, "steel")
d.add("screen", "screen", "white", box=[195, 1275, 150, 455, 1495, 210], r=16, face="front", bezel=28)
# the photo's display is light (switched on, pale grey-blue with a lighter swirl), not black: decals over the glass
d.decal("screen-lit", [325, 1385, 210.8], [202, 162], "front", "gloss#aab8c6", soft=True)
d.decal("screen-lit2", [325, 1350, 211.2], [190, 40], "front", "gloss#c9d4de", soft=True)
d.save()
