"""xy-zbd-iiidl / -iidl / -idl: seatless upper+lower limb cycle trainers (one body, three fittings).
Patient sits at the front (+z, the crossbar end) facing the column; the screen faces the patient."""
import math, sys
from k1lib import *

W, DP, H = 620, 1150, 1550
CX = W / 2
MATS = {"white": "plastic#f2f3f5", "grey": "plastic#9a9ea5", "disc": "plastic#8f949b", "pink": "gloss#e0457b",
        "black": "rubber#1c1d1f", "metal": "metal#c9ccd0", "chrome": "chrome", "dark": "plastic#2a2c30",
        "logo": "plastic#6b7078"}


def build(id, crank, pedals, grip_bar=False, screen_print=None, rear_grips=True):
    d = D(id, [W, DP, H], MATS)
    # --- base: rear box foot with a grey band, front crossbar, low centre rail, levelling pads
    d.box("rear-foot", [205, 22, 20, 415, 172, 400], "white", r=42)
    d.box("rear-foot-band", [201, 48, 16, 419, 128, 404], "grey", r=34)
    d.cyl("pad", [240, 0, 55], [240, 22, 55], 50, "black", copies=[[140, 0, 0], [0, 0, 310], [140, 0, 310]])
    d.box("cross-bar", [20, 22, 1040, 600, 132, 1140], "white", r=52)
    d.cyl("cross-pin", [215, 128, 1090], [215, 156, 1090], 14, "chrome", copies=[[190, 0, 0]])
    d.cyl("cross-pad", [60, 0, 1090], [60, 22, 1090], 50, "black", copies=[[500, 0, 0]])
    d.box("centre-rail", [255, 22, 200, 365, 118, 1060], "white", r=34)
    # --- main column leaning ~28 deg toward the patient, grey collar, short inner tube
    a = [CX, 120, 190]
    u = [0, 0.884, 0.467]
    def P(t): return [CX, a[1] + u[1] * t, a[2] + u[2] * t]
    d.bar("column", a, P(840), [170, 120], "white", r=48)
    d.bar("column-collar", P(830), P(880), [184, 134], "grey", r=52)
    d.bar("column-inner", P(870), P(960), [120, 84], "metal", r=20)
    top = P(960)
    # "Sunnyou 翔宇" reading up the column's -x face (along the column), small grey line under it
    o = P(150)
    text(d, "column-logo", "Sunnyou", [CX - 85.6, o[1] - 10.7, o[2] + 20.3], 46, "logo", along=(u[2], u[1]), face="left")
    o2 = P(150 + text_len("Sunnyou ", 46) + 6)
    text(d, "column-logo-cn", "翔宇", [CX - 85.6, o2[1] - 10.7, o2[2] + 20.3], 46, "logo", along=(u[2], u[1]), face="left")
    o3 = P(150 + 150)
    sub = [CX - 85.6, o3[1] - 18.7, o3[2] + 35.4]
    d.decal("column-logo-sub", sub, [4, 190], "left", "plastic#b4b8be", soft=True, rot=rot("x", 28, sub))
    # --- head bracket under the capsule: clamp block, black ball knob (-x), lever (+x), L clamp at the front
    hy = 1060
    d.box("bracket", [258, top[1] - 10, top[2] - 70, 362, 985, top[2] + 70], "metal", r=10)
    d.cyl("knob-stem", [258, 960, top[2] - 30], [232, 960, top[2] - 30], 16, "metal")
    d.sphere("knob", [222, 960, top[2] - 30], 52, "dark")
    d.box("lever", [362, 948, top[2] + 10, 382, 972, top[2] + 80], "dark", r=8)
    d.box("front-clamp", [296, 952, 745, 326, 985, 800], "dark", r=6)
    # --- head capsule along z, rear end rounded, sphere at the front
    d.loft("capsule", [sec(212, 120, 130, 50, CX, hy - 4), sec(236, 172, 182, 62, CX, hy - 2), sec(290, 186, 198, 62, CX, hy),
                       sec(570, 186, 198, 62, CX, hy), sec(700, 168, 176, 60, CX, hy), sec(800, 150, 152, 60, CX, hy)],
           "white", axis="z")
    d.sphere("sphere", [CX, hy, 900], 262, "white")
    # grey disc with a double pink ring, flush with the sphere
    ring_disc(d, "sphere-disc", [CX + 110, hy, 900], 70, 66, "pink", "disc", mirror="x")
    ring_disc(d, "sphere-disc2", [CX + 111.2, hy, 900], 62, 58, "pink", "disc", mirror="x")
    text(d, "capsule-logo", "Sunnyou", [CX - 93.6, hy - 22, 380], 38, "logo", face="left")
    text_right(d, "capsule-logo-r", "Sunnyou", [CX + 93.6, hy - 22, 380 + text_len("Sunnyou", 38)], 38, "logo")
    # silver oval bosses near the rear end, black grips sideways
    d.sphere("rear-boss-rim", [CX - 88, hy, 300], None, "plastic#7d8288", radii=[12, 56, 70], mirror="x")
    d.sphere("rear-boss", [CX - 91, hy, 300], None, "metal", radii=[13, 51, 65], mirror="x")
    if rear_grips:
        d.cyl("rear-grip", [CX - 98, hy, 300], [CX - 250, hy, 300], 36, "black", mirror="x")
        d.sphere("rear-grip-end", [CX - 250, hy, 300], 36, "black", mirror="x")
    else:
        d.sphere("rear-knob", [CX - 100, hy, 300], None, "white", radii=[16, 28, 28], mirror="x")
    # --- screen on a short stalk, facing the patient, tilted back 10 deg; red e-stop behind-left
    d.cyl("stalk", [CX, 1150, 520], [CX, 1192, 520], 62, "white")
    tilt = rot("x", -10, [CX, 1190, 520])
    d.add("screen", "screen", "dark", box=[10, 1185, 504, 610, 1545, 536], r=14, face="front", bezel=20,
          print=screen_print, rot=tilt)
    d.lathe("estop", [228, 1148, 400], [[0, 0], [13, 0], [13, 12], [17, 14], [17, 24], [0, 26]], "gloss#d82a20")
    # --- upper crank on the sphere (cranks at 180 deg) or a straight grip bar
    if crank:
        for nm, sx, dy, dz in (("l", -1, -165, -40), ("r", 1, 165, 30)):
            xs = CX + sx * 128
            end = [xs + sx * 8, hy + dy, 900 + dz]
            d.bar(f"crank-{nm}", [xs, hy, 900], end, [38, 16], "white", r=7)
            d.cyl(f"crank-hub-{nm}", [xs - sx * 4, hy, 900], [xs + sx * 14, hy, 900], 26, "metal")
            d.cyl(f"crank-boss-{nm}", [end[0] - sx * 6, end[1], end[2]], [end[0] + sx * 18, end[1], end[2]], 58, "white")
            d.cyl(f"crank-grip-{nm}", [end[0] + sx * 18, end[1], end[2]], [end[0] + sx * 140, end[1], end[2]], 36, "black")
            d.sphere(f"crank-grip-end-{nm}", [end[0] + sx * 140, end[1], end[2]], 36, "black")
    if grip_bar:
        d.cyl("grip-bar", [50, hy, 900], [570, hy, 900], 38, "black")
        d.cyl("grip-boss", [CX - 140, hy, 900], [CX - 118, hy, 900], 60, "white", mirror="x")
        d.sphere("grip-bar-end", [50, hy, 900], 38, "black", mirror="x")
    # --- lower drive drum: thick white drum, recessed grey disc with a pink ring on both sides
    DY, DZ = 440, 640
    d.lathe("drum", [CX - 110, DY, DZ], [[0, 14], [142, 14], [152, 4], [176, 0], [200, 8], [212, 36], [212, 184],
                                         [200, 212], [176, 220], [152, 216], [142, 206], [0, 206]], "white", axis="x")
    d.box("drum-web", [208, 100, 500, 412, 330, 760], "white", r=60)
    ring_disc(d, "drum-disc", [CX - 99, DY, DZ], 138, 134, "pink", "disc", out=-1, mirror="x")
    ring_disc(d, "drum-disc2", [CX - 100.2, DY, DZ], 129, 125, "pink", "disc", out=-1, mirror="x")
    if pedals:
        for nm, sx, ang in (("l", -1, 205), ("r", 1, 25)):
            # crank plate from the drum centre to the pedal axle (180 deg apart)
            r = 115
            ay, az = DY + r * math.sin(math.radians(ang)), DZ + r * math.cos(math.radians(ang))
            xp = CX + sx * 118
            d.bar(f"pedal-crank-{nm}", [xp, DY, DZ], [xp, ay, az], [44, 14], "metal", r=6)
            d.cyl(f"pedal-axle-{nm}", [xp, ay, az], [xp + sx * 30, ay, az], 22, "metal")
            d.bar(f"pedal-slot-{nm}", [xp + sx * 7.5, DY + 0.25 * (ay - DY), DZ + 0.25 * (az - DZ)],
                  [xp + sx * 7.5, DY + 0.8 * (ay - DY), DZ + 0.8 * (az - DZ)], [2, 10], "dark", soft=True)
            # foot cradle outside the crank: sole along z (toes to the rear), heel cup at the front
            x0, x1 = (xp + sx * 30, xp + sx * 150)
            lo, hi = min(x0, x1), max(x0, x1)
            sy = ay - 20
            z0, z1 = az - 210, az + 95
            # sole with a slightly raised toe (rear) and a tall rounded heel cup (front)
            sole = (f"M {z0} {sy + 22} Q {z0} {sy} {z0 + 30} {sy} L {z1 - 45} {sy} Q {z1} {sy} {z1} {sy + 45} "
                    f"L {z1} {sy + 120} Q {z1} {sy + 132} {z1 - 12} {sy + 132} Q {z1 - 22} {sy + 132} {z1 - 22} {sy + 120} "
                    f"L {z1 - 22} {sy + 52} Q {z1 - 22} {sy + 20} {z1 - 55} {sy + 20} L {z0 + 30} {sy + 20} "
                    f"Q {z0 + 14} {sy + 20} {z0 + 10} {sy + 30} Z")
            d.slab(f"cradle-{nm}", "side", sole, [lo, hi], "white", r=6)
            # side walls: tall at the heel, low toward the toe
            wall = (f"M {z0 + 25} {sy + 10} L {z1 - 30} {sy + 10} Q {z1 - 8} {sy + 10} {z1 - 8} {sy + 40} "
                    f"L {z1 - 8} {sy + 118} Q {z1 - 30} {sy + 118} {z1 - 60} {sy + 92} L {z0 + 60} {sy + 46} "
                    f"Q {z0 + 30} {sy + 40} {z0 + 25} {sy + 24} Z")
            d.slab(f"cradle-wall-{nm}", "side", wall, [lo, lo + 10], "white", r=4)
            d.slab(f"cradle-wall2-{nm}", "side", wall, [hi - 10, hi], "white", r=4)
            # calf support: bent white stalk from the heel up to a C-shaped shell cupping the calf from the front
            xc = (lo + hi) / 2
            d.sweep(f"calf-stalk-{nm}", [[xc, sy + 80, z1 - 6], [xc, sy + 200, z1 + 10], [xc, sy + 320, z1 - 10]],
                    [40, 12], "white", bend=60, r=4)
            cz = z1 - 10
            d.slab(f"calf-shell-{nm}", "top", ushell(xc, z1 - 60, 70, 10, open_to="-z"), [sy + 300, sy + 440],
                   "white", r=4)
            d.cyl(f"calf-knob-{nm}", [xc, sy + 360, cz + 2], [xc, sy + 360, cz + 22], 30, "metal")
    return d


if __name__ == "__main__":
    which = sys.argv[1:] or ["xy-zbd-iiidl", "xy-zbd-iidl", "xy-zbd-idl"]
    for id in which:
        if id == "xy-zbd-iiidl":
            build(id, crank=True, pedals=True, screen_print="med_xy-zbd-iiidl_screen").save()
        elif id == "xy-zbd-iidl":
            build(id, crank=False, pedals=True, grip_bar=True, rear_grips=False,
                  screen_print="med_xy-zbd-iiidl_screen").save()
        elif id == "xy-zbd-idl":
            build(id, crank=True, pedals=False, screen_print="med_xy-zbd-iiidl_screen").save()
