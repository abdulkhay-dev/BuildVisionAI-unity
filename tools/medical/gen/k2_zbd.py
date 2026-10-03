"""xy-zbd-id (arms) / xy-zbd-iid (legs) / xy-zbd-iiid (arms + legs) — passive/active exercisers (kinesio-2).
Frame: the patient sits at the front (z = depth): the wheel tube is at the front, the white cowl foot at the back,
the column leans/rises towards the patient, crank heads face him."""
import math
from k2lib import *

MATS = {"blue": "gloss#2b5ea8", "white": "gloss#eef0f2", "grey": "plastic#9aa0a8", "steel": "metal#c8ccd2",
        "black": "plastic#1d1f22", "foam": "rubber#1b1c1e", "strap": "fabric#1a1b1d", "tyre": "rubber#8d9096",
        "screen-lit": "gloss#aab8c6"}


def cowl(d, x0, x1, z0, z1, h):
    """White loaf-shaped rear foot lying along z (rounded top, flat rear face), navy plate under it."""
    rr = (x1 - x0) / 2 - 5
    o = f"M {x0} 0 L {x1} 0 L {x1} {h - rr} Q {x1} {h} {x1 - rr} {h} L {x0 + rr} {h} Q {x0} {h} {x0} {h - rr} Z"
    d.slab("cowl", "front", o, [z0, z1], "white", r=30)
    d.box("cowl-plate", [x0 - 10, 0, z0 + 10, x1 + 10, 16, z1 + 20], "blue", r=4)
    d.decal("cowl-screw", [x1 + 0.6, 45, z0 + 60], [10, 10], "right", "grey", soft=True, copies=[[0, 0, z1 - z0 - 120]])


def cowl_x(d, x0, x1, z0, z1, h, rr=90):
    """White loaf foot lying ACROSS the width (x) under the column foot: flat front/back faces with a rounded top,
    rounded ends, straight on the floor (the navy beam rides over it to the column)."""
    o = f"M {z0} 0 L {z1} 0 L {z1} {h - rr} Q {z1} {h} {z1 - rr} {h} L {z0 + rr} {h} Q {z0} {h} {z0} {h - rr} Z"
    d.slab("cowl", "side", o, [x0, x1], "white", r=45)
    for x in (x0 + 70, x1 - 70):
        d.decal(f"cowl-screw{x}", [x, 50, z1 + 0.6], [10, 10], "front", "grey", soft=True)


def front_tube(d, z, x0, x1, roller=False):
    d.cyl("front-tube", [x0 + 20, 34, z], [x1 - 20, 34, z], 40, "blue")
    if roller:
        for nm, x in (("l", x0 + 20), ("r", x1 - 20)):
            d.cyl(f"roller-{nm}", [x - 22, 34, z], [x + 22, 34, z], 66, "plastic#e7e1cc")
    else:
        for nm, x in (("l", x0 + 22), ("r", x1 - 22)):
            wheel = d.add(f"wheel-{nm}", "wheel", "tyre", at=[x, 33, z], d=66, d2=26, axis="x")
            d.cyl(f"hub-{nm}", [x - 15, 33, z], [x + 15, 33, z], 30, "plastic#f4f4f4")


def screen_box(d, cx, y0, z, w, h, neck=40, label=False, turn=0, label_dx=0):
    """White square touch-screen box on a short neck; `turn` swivels it about the neck (deg, towards +x)."""
    d.cyl("neck", [cx, y0 - neck, z - 30], [cx, y0 + 5, z - 30], 44, "white")
    R = rot("y", turn, [cx, y0, z - 30])
    scr(d, "screen", [cx - w / 2, y0, z - 60, cx + w / 2, y0 + h, z], "white", r=18, face="front", bezel=28, rot=R)
    d.decal("screen-lit", [cx, y0 + h / 2, z + 0.8], [w - 60, h - 60], "front", "screen-lit", soft=True, rot=R)
    if label:
        d.decal("screen-label", [cx + label_dx, y0 + h - 14, z + 0.8], [w * 0.4, 14], "front", "gloss#f2c400", soft=True, rot=R)


def crank_head(d, nm, cx, cy, cz, dia, thick, arm=100, up_left=True, disc="silver"):
    """Round white crank drum (axis x) with blue rings, crank arms 180 deg apart and black foam handles outward."""
    x0, x1 = cx - thick / 2, cx + thick / 2
    rr = dia / 2
    d.lathe(f"{nm}-drum", [x0, cy, cz], [[0, 0], [rr - 18, 0], [rr, 16], [rr, thick - 16], [rr - 18, thick], [0, thick]], "white", axis="x")
    for s, xf in ((-1, x0), (1, x1)):
        xo = xf + s * 2
        prof = [[0, 0], [rr * 0.78, 0], [rr * 0.78, 3], [0, 3]]
        d.lathe(f"{nm}-ring{s}", [xo, cy, cz], prof, "blue", axis="x", rot=rot("y", 180, [xo, cy, cz]) if s < 0 else None)
        xo2 = xf + s * 3.5
        d.lathe(f"{nm}-face{s}", [xo2, cy, cz], [[0, 0], [rr * 0.55, 0], [rr * 0.55, 3], [0, 3]], "white", axis="x",
                rot=rot("y", 180, [xo2, cy, cz]) if s < 0 else None)
    d.cyl(f"{nm}-axle", [x0 - 30, cy, cz], [x1 + 30, cy, cz], 30, "steel")
    for s, xf in ((-1, x0), (1, x1)):
        up = (s < 0) == up_left
        ey = cy + (arm if up else -arm)
        xa = xf + s * 30
        if disc == "silver":
            d.cyl(f"{nm}-disc{s}", [xa - 8, cy, cz], [xa + 8, cy, cz], 95, "steel")
        d.bar(f"{nm}-arm{s}", [xa + s * 6, cy, cz], [xa + s * 6, ey, cz], [16, 46], "steel", r=6)
        d.cyl(f"{nm}-grip{s}", [xa + s * 14, ey, cz], [xa + s * 130, ey, cz], 42, "foam")
        d.cyl(f"{nm}-grip-end{s}", [xa + s * 130, ey, cz], [xa + s * 136, ey, cz], 34, "black")


def leg_pedals(d, cx, cy, cz, half, crank=125, ang_r=-60):
    """Leg crank: blue crank arms 180 deg apart, white calf shells (open to the back) with black straps, black foot cups."""
    for s, a in ((1, ang_r), (-1, ang_r + 180)):
        ra = math.radians(a)
        py, pz = cy + crank * math.sin(ra), cz + crank * math.cos(ra)
        xh = cx + s * half
        xp = cx + s * (half + 95)
        nm = "r" if s > 0 else "l"
        d.bar(f"crank-{nm}", [xh + s * 14, cy, cz], [xh + s * 14, py, pz], [26, 52], "blue", r=8)
        d.cyl(f"pedal-axle-{nm}", [xh, py, pz], [xp, py, pz], 26, "steel")
        # calf shell: U in plan (x/z), open to -z, from the foot cup up
        r0, t = 72, 9
        o = (f"M {xp - r0} {pz} L {xp - r0} {pz + 20} Q {xp - r0} {pz + r0 + 20} {xp} {pz + r0 + 20} Q {xp + r0} {pz + r0 + 20} {xp + r0} {pz + 20} "
             f"L {xp + r0} {pz} L {xp + r0 - t} {pz} L {xp + r0 - t} {pz + 20} Q {xp + r0 - t} {pz + r0 + 20 - t} {xp} {pz + r0 + 20 - t} "
             f"Q {xp - r0 + t} {pz + r0 + 20 - t} {xp - r0 + t} {pz + 20} L {xp - r0 + t} {pz} Z")
        d.slab(f"shell-{nm}", "top", o, [py - 20, py + 190], "white", r=4)
        d.box(f"foot-cup-{nm}", [xp - 62, py - 45, pz - 110, xp + 62, py - 20, pz + 85], "black", r=10)
        d.box(f"foot-heel-{nm}", [xp - 62, py - 20, pz + 40, xp + 62, py + 30, pz + 85], "black", r=10)
        for k, yy in enumerate((py + 40, py + 140)):
            d.strap(f"strap-{nm}{k}", [[xp - r0, yy, pz + 5], [xp, yy, pz - 40], [xp + r0, yy, pz + 5]], [40, 4], "strap", bend=40, soft=True)
        d.strap(f"strap-foot-{nm}", [[xp - 62, py - 20, pz - 60], [xp, py + 25, pz - 62], [xp + 62, py - 20, pz - 60]], [40, 4], "strap",
                bend=30, soft=True)


# =============== XY-ZBD-ID: arm ergometer, column leaning ~16 deg forward
# layout measured on the photo with the crank disc (230) as scale: transverse loaf foot under the column foot, the
# head a long white body from the column top forward to the disc, the U handle further back
d = D("xy-zbd-id", [650, 900, 1400], MATS)
CX = 325
cowl_x(d, 45, 605, 95, 335, 215)
front_tube(d, 650, 40, 610)
d.bar("beam", [CX, 34, 640], [CX, 196, 260], [130, 50], "blue", r=8)
d.box("saddle", [CX - 65, 196, 150, CX + 65, 222, 300], "blue", r=8)
d.bar("column", [CX, 200, 215], [CX, 900, 430], [90, 62], "blue", r=8)
d.decal("column-screw", [CX + 45.6, 300, 255], [8, 8], "right", "grey", soft=True, copies=[[0, 30, 0], [0, 0, 20], [0, 30, 20]])
d.bar("telescope", [CX, 880, 425], [CX, 975, 452], [78, 52], "white", r=8)
star_knob(d, "clamp-knob", [CX, 910, 415], "z", -1, dd=40)
d.box("joint", [CX - 50, 950, 405, CX + 50, 990, 500], "steel", r=6)
star_knob(d, "joint-knob", [CX + 50, 970, 455], "x", 1, dd=52, l=40)
# head: a long white body from behind the column top forward to the crank drum, navy side panels with the white name
d.box("head", [CX - 70, 985, 370, CX + 70, 1110, 770], "white", r=55)
for s in (-1, 1):
    xb = CX + s * 70
    d.box(f"head-panel{s}", [min(xb, xb + s * 4), 1003, 420, max(xb, xb + s * 4), 1092, 690], "blue", r=36)
text_side(d, "head-text", "XIANGYU MEDICAL", [CX + 74.6, 1038, 672], 17, "plastic#ffffff", face="right")
text_side(d, "head-text-l", "XIANGYU MEDICAL", [CX - 74.6, 1038, 438], 17, "plastic#ffffff", face="left")
crank_head(d, "crank", CX, 1045, 760, 230, 150, arm=100, up_left=True)
# black U handle behind the head (round tube, rising a little to the back)
d.tube("u-handle", [[CX - 62, 1055, 390], [CX - 175, 1065, 345], [CX - 185, 1090, 215], [CX + 185, 1090, 215],
                    [CX + 175, 1065, 345], [CX + 62, 1055, 390]], 32, "foam", bend=75)
# screen over the column top, swivelled to face the right-front (the photo's camera)
screen_box(d, CX, 1140, 600, 270, 250, neck=55, turn=68)
d.save()

# =============== XY-ZBD-IID: leg cycle, curved blue column behind the big drum, handle head with horn bars
d = D("xy-zbd-iid", [560, 750, 1150], MATS)
CX = 280
cowl_x(d, 30, 530, 20, 310, 210)
front_tube(d, 615, 20, 540)
d.bar("beam", [CX, 34, 600], [CX, 200, 250], [120, 50], "blue", r=8)
DY, DZ = 375, 470
# the column comes down to the top-back of the drum; from there a curved navy plate on each drum face runs round the
# hub (a ring with the white hub face) and on down to the base beam (photo) - no column behind the drum
d.sweep("column", [[CX, 545, 392], [CX, 640, 362], [CX, 780, 345]], [90, 62], "blue", r=8, bend=110)
d.lathe("drum", [CX - 62, DY, DZ], [[0, 0], [160, 0], [180, 18], [180, 106], [160, 124], [0, 124]], "white", axis="x")
def arc_pt(a, r): return (DZ + r * math.cos(math.radians(a)), DY + r * math.sin(math.radians(a)))
def band(a0, a1, r0, r1, end0, end1):
    """outline: from the ring's arc (angles a0..a1, radius r1) out to the straight end end0-end1 (z, y)."""
    p0, p1 = arc_pt(a0, r1), arc_pt(a1, r1)
    return (f"M {p0[0]:.1f} {p0[1]:.1f} A {r1} {r1} 0 0 1 {p1[0]:.1f} {p1[1]:.1f} "
            f"L {end1[0]} {end1[1]} L {end0[0]} {end0[1]} Z")
for s in (-1, 1):
    xo = CX + s * 62
    w = [min(xo, xo + s * 8), max(xo, xo + s * 8)]
    ring = (f"M {DZ - 100} {DY} A 100 100 0 1 0 {DZ + 100} {DY} A 100 100 0 1 0 {DZ - 100} {DY} Z "
            f"M {DZ - 44} {DY} A 44 44 0 1 1 {DZ + 44} {DY} A 44 44 0 1 1 {DZ - 44} {DY} Z")
    d.slab(f"hub-ring{s}", "side", ring, w, "blue", r=3)
    # upper band: from the ring's top-back up to the column foot (curving)
    d.slab(f"plate-up{s}", "side", band(150, 95, 0, 98, (340, 560), (420, 575)), w, "blue", r=3)
    # lower band: from the ring's bottom down-back to the beam
    d.slab(f"plate-dn{s}", "side", band(-75, -140, 0, 98, (430, 105), (350, 120)), w, "blue", r=3)
    xw = CX + s * 70.5
    d.lathe(f"hub-face{s}", [xw, DY, DZ], [[0, 0], [44, 0], [44, 3], [0, 3]], "white", axis="x",
            rot=rot("y", 180, [xw, DY, DZ]) if s < 0 else None)
    d.decal(f"drum-dots{s}", [CX + s * 62.4, DY + 140, DZ + 40], [10, 10], "right" if s > 0 else "left", "grey", soft=True,
            copies=[[0, -40, 90], [0, -150, 120], [0, -230, 50], [0, 30, -100]])
d.box("plate-screws", [CX - 75, 600, 365, CX + 75, 612, 400], "steel", r=4)
d.cyl("hub", [CX - 80, DY, DZ], [CX + 80, DY, DZ], 50, "steel")
leg_pedals(d, CX, DY, DZ, 80, crank=130, ang_r=-55)
d.bar("telescope", [CX, 760, 345], [CX, 890, 350], [78, 52], "white", r=8)
star_knob(d, "clamp-knob", [CX, 820, 316], "z", -1, dd=40)
star_knob(d, "head-knob", [CX + 40, 880, 330], "x", 1, dd=52, l=40)
# handle head + horn bars reaching forward to the patient
d.box("handle-head", [CX - 150, 885, 340, CX + 150, 960, 455], "white", r=30)
d.box("handle-inset", [CX - 90, 900, 454, CX + 90, 945, 458], "blue", r=10)
for s in (-1, 1):
    d.tube(f"horn{s}", [[CX + s * 140, 925, 420], [CX + s * 200, 925, 470], [CX + s * 215, 935, 600], [CX + s * 170, 945, 690]],
           34, "foam", bend=80)
screen_box(d, CX, 985, 410, 230, 190, neck=25, turn=68)
d.save()

# =============== XY-ZBD-IIID: legs drum low, arm crank housing on top sloping to the patient
d = D("xy-zbd-iiid", [650, 650, 1300], {**MATS, "blue": "gloss#2b4e86"})
CX = 325
front_tube(d, 610, 30, 620, roller=True)
d.bar("beam", [CX, 40, 600], [CX, 40, 110], [90, 60], "blue", r=8)
d.cyl("rear-foot", [130, 40, 120], [520, 40, 120], 44, "blue")
d.cyl("rear-pad", [140, 0, 120], [140, 18, 120], 40, "black", copies=[[370, 0, 0]])
d.sweep("column", [[CX, 60, 170], [CX, 330, 175], [CX, 640, 215], [CX, 860, 240]], [90, 62], "blue", r=8, bend=120)
d.box("joint", [CX - 55, 840, 195, CX + 55, 905, 290], "black", r=10)
star_knob(d, "joint-knob", [CX - 55, 875, 245], "x", -1, dd=60, l=44)
star_knob(d, "col-knob", [CX + 45, 760, 225], "x", 1, dd=40)
DY, DZ = 420, 380
d.lathe("leg-drum", [CX - 65, DY, DZ], [[0, 0], [148, 0], [165, 16], [165, 114], [148, 130], [0, 130]], "white", axis="x")
for s in (-1, 1):
    xo = CX + s * 67
    d.lathe(f"leg-ring{s}", [xo, DY, DZ], [[0, 0], [120, 0], [120, 3], [0, 3]], "blue", axis="x",
            rot=rot("y", 180, [xo, DY, DZ]) if s < 0 else None)
    d.lathe(f"leg-face{s}", [xo + s * 1.5, DY, DZ], [[0, 0], [95, 0], [95, 3], [0, 3]], "white", axis="x",
            rot=rot("y", 180, [xo + s * 1.5, DY, DZ]) if s < 0 else None)
d.decal("leg-label", [CX + 70, DY + 40, DZ + 80], [20, 90], "right", "gloss#f2c400", soft=True)
d.decal("leg-label-l", [CX - 70, DY + 40, DZ - 80], [20, 90], "left", "gloss#f2c400", soft=True)
d.cyl("leg-hub", [CX - 80, DY, DZ], [CX + 80, DY, DZ], 50, "steel")
leg_pedals(d, CX, DY, DZ, 80, crank=120, ang_r=-50)
# upper arm housing sloping down to the arm drum, blue band on its sides
d.bar("arm-housing", [CX, 965, 225], [CX, 880, 470], [130, 120], "white", r=40)
d.bar("arm-band", [CX, 958, 245], [CX, 885, 455], [136, 40], "blue", r=10)
crank_head(d, "arm", CX, 870, 485, 220, 170, arm=95, up_left=True)
d.tube("u-handle", [[CX - 62, 975, 300], [CX - 225, 985, 260], [CX - 235, 995, 90], [CX + 235, 995, 90],
                    [CX + 225, 985, 260], [CX + 62, 975, 300]], 34, "foam", bend=80)
screen_box(d, CX, 1060, 300, 280, 230, neck=60, label=True, turn=-40, label_dx=-60)
# the name along the navy band on both sides of the arm housing (sloping ~19 deg down to the patient)
text_side(d, "band-text-l", "XIANGYU MEDICAL", [CX - 68.6, 950, 250], 11, "plastic#ffffff", face="left", ang=-19)
text_side(d, "band-text-r", "XIANGYU MEDICAL", [CX + 68.6, 908, 370], 11, "plastic#ffffff", face="right", ang=19)
d.save()
