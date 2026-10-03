from k4lib import *
d = K("xy-2a", [620, 1300, 1000], {
    "frame": "metal#c2c5c9", "orange": "gloss#f08a1c", "shell": "plastic#4a4d52", "black": "plastic#1e1f22",
    "seat": "leather#202124", "cap": "rubber#18191b", "grip": "metal#d6d8db", "foam": "rubber#1c1d1f"})
CX = 310
# --- frame: feet with black caps, main beam with bolts
d.cyl("rear-foot", [40, 38, 90], [580, 38, 90], 60, "frame")
d.lathe("rear-cap", [0, 40, 90], [[0, 0], [36, 0], [40, 10], [40, 70], [34, 84], [0, 86]], "cap", axis="x")
d.lathe("rear-cap-r", [620, 40, 90], [[0, 0], [36, 0], [40, 10], [40, 70], [34, 84], [0, 86]], "cap", axis="x",
        rot=rot("y", 180, [620, 40, 90]))
d.box("rear-pad", [10, 0, 50, 90, 8, 150], "cap", r=3, mirror="x")
d.cyl("front-foot", [70, 34, 1235], [550, 34, 1235], 56, "frame")
d.lathe("front-cap", [40, 36, 1235], [[0, 0], [33, 0], [36, 8], [36, 60], [30, 72], [0, 74]], "cap", axis="x")
d.lathe("front-cap-r", [580, 36, 1235], [[0, 0], [33, 0], [36, 8], [36, 60], [30, 72], [0, 74]], "cap", axis="x",
        rot=rot("y", 180, [580, 36, 1235]))
d.bar("beam", [CX, 75, 70], [CX, 100, 900], [80, 56], "frame", r=6)
d.decal("bolt", [CX - 40.5, 92, 420], [9, 9], "left", "chrome", repeat=rep(4, [0, 0, 55]))
d.decal("bolt2", [CX - 40.5, 72, 420], [9, 9], "left", "chrome", repeat=rep(4, [0, 0, 55]))
d.decal("bolt-r", [CX + 40.5, 92, 420], [9, 9], "right", "chrome", repeat=rep(4, [0, 0, 55]))
# --- seat support, seat, backrest and its frame
d.bar("seat-post", [CX, 100, 360], [CX, 430, 320], [70, 50], "frame", r=6)
d.box("seat-carriage", [235, 410, 200, 385, 445, 380], "frame", r=8)
d.box("seat", [130, 440, 180, 490, 505, 480], "seat", r=32, puff=10)
d.box("seat-rim", [138, 432, 190, 482, 446, 470], "black", r=12)
BR = rot("x", -21, [CX, 505, 190])
d.box("back", [135, 505, 115, 485, 935, 190], "seat", r=38, puff=8, rot=BR)
d.box("back-shell", [145, 520, 95, 475, 920, 118], "black", r=20, rot=BR)
for nm, x in (("l", 140), ("r", 480)):
    d.sweep(f"back-frame-{nm}", [[x, 430, 320], [x, 445, 150], rotx([x, 880, 120], -21, [CX, 505, 190])], [32, 26], "frame",
            shape="oval", bend=60)
d.bar("back-cross", [140, 440, 160], [480, 440, 160], [30, 26], "frame", r=5)
# side handles: black bent tubes from under the seat, silver ribbed grips pointing forward
for nm, x in (("l", 92), ("r", 528)):
    xi = 170 if x < CX else 450
    d.tube(f"handle-{nm}", [[xi, 425, 250], [x, 400, 260], [x, 320, 330], [x, 360, 420], [x, 450, 470]], 30, "black", bend=55)
    d.cyl(f"grip-{nm}", [x, 450, 470], [x, 470, 590], 36, "grip")
    d.cyl(f"grip-rib-{nm}", [x, 452.5, 485], [x, 455, 500], 39, "frame", repeat=rep(5, [0, 3.3, 20]))
    d.lathe(f"grip-end-{nm}", [x, 470, 590], [[0, 0], [18, 0], [18, 8], [12, 16], [0, 18]], "black", axis="z",
            rot=rot("x", -9.5, [x, 470, 590]))
# --- shroud: a wedge in side view (photo) - flat bottom on the beam, top rising from a low round rear nose to a
# tall rounded front; grey body, orange hood band along the top that wraps down round the rear nose
EC = CX
#        z     bottom top   width
SH = [(462, 128, 150, 70), (478, 102, 196, 150), (505, 90, 224, 200), (560, 84, 256, 232), (650, 82, 302, 250),
      (750, 82, 357, 258), (850, 82, 410, 262), (950, 82, 458, 262), (1030, 82, 494, 262), (1080, 83, 514, 260),
      (1120, 84, 523, 256), (1150, 86, 518, 250), (1178, 92, 498, 236), (1198, 102, 464, 214), (1211, 120, 420, 188),
      (1219, 158, 352, 150), (1223, 215, 292, 96)]
def shp(z):
    for (z0, b0, t0, w0), (z1, b1, t1, w1) in zip(SH, SH[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return b0 + (b1 - b0) * t, t0 + (t1 - t0) * t, w0 + (w1 - w0) * t
    return SH[-1][1:]
d.loft("shroud-low", [{"at": z, "w": w, "d": t - b, "r": min(80, w / 2 - 1, (t - b) / 2 - 1), "cx": EC, "cz": (t + b) / 2}
                      for z, b, t, w in SH], "shell", axis="z")
BAND = 92                                  # orange band height on the flank (photo)
hood = []
for z, b, t, w in SH[:11]:
    bb = max(b - 2, t - BAND - 40)         # the band's rounded lower edge tucks under the grey flank
    hood.append({"at": z, "w": w + 4, "d": t + 2 - bb, "r": min(80, (w + 4) / 2 - 1, (t + 2 - bb) / 2 - 1), "cx": EC, "cz": (t + 2 + bb) / 2})
z, b, t, w = 1140, *shp(1140)
hood.append({"at": z, "w": w - 14, "d": BAND, "r": 40, "cx": EC, "cz": t - BAND / 2 - 4})   # band ends inside, front top stays grey
d.loft("shroud-top", hood, "orange", axis="z")
# thin orange swoosh from the rear bottom rising to the crank ring
for nm, o in (("l", -1), ("r", 1)):
    d.sweep(f"swoosh-{nm}", [[EC + o * (shp(z)[2] / 2 + 1), y, z] for z, y in ((520, 112), (640, 175), (760, 238), (850, 282))],
            [14, 4], "orange", shape="oval", bend=150, roll=90)
# crank ring on each flank, grey inner disc, chrome boss, crank arm and pedal
KZ, KY = 1010, 285
for nm, x0, x1, o in (("l", EC - 136, EC - 125, -1), ("r", EC + 125, EC + 136, 1)):
    d.slab(f"ring-{nm}", "side", circle(KZ, KY, 168) + " " + circle(KZ, KY, 142), [x0, x1], "orange", r=2)
    d.slab(f"disc-{nm}", "side", circle(KZ, KY, 141), [x0 + (3 if o > 0 else 0), x1 - (0 if o > 0 else 3)], "plastic#5a5d62", r=2)
    xb = EC + o * 140
    d.cyl(f"boss-{nm}", [EC + o * 128, KY, KZ], [xb, KY, KZ], 50, "chrome")
    ang = 60 if o > 0 else 240            # crank angles 180 deg apart (from +z toward -y)
    ez = KZ + 165 * math.cos(math.radians(ang)); ey = KY - 165 * math.sin(math.radians(ang))
    d.bar(f"crank-{nm}", [xb + o * 8, KY, KZ], [xb + o * 8, ey, ez], [36, 16], "chrome", r=6, roll=90)
    xp = xb + o * 16
    d.cyl(f"spindle-{nm}", [xp, ey, ez], [xp + o * 25, ey, ez], 16, "chrome")
    px0, px1 = sorted([xp + o * 25, xp + o * 125])
    d.box(f"pedal-{nm}", [px0, ey - 18, ez - 60, px1, ey + 14, ez + 60], "black", r=8)
    d.strap(f"pedal-strap-{nm}", [[px0 + 5, ey + 14, ez + 30], [(px0 + px1) / 2, ey + 55, ez + 20], [px1 - 5, ey + 14, ez + 30]],
            [26, 3], "black", bend=40)
xh = EC - shp(720)[2] / 2 + 1
d.lathe("rear-hub", [xh, 262, 720], [[0, 0], [20, 0], [18, 6], [0, 9]], "plastic#9a9da2", axis="x",
        rot=rot("y", 180, [xh, 262, 720]), mirror="x")
# --- column, pulse block, knob, console and handlebar
d.cyl("collar", [CX, 470, 975], [CX, 560, 962], 94, "black")
d.cyl("column", [CX, 520, 968], [CX, 840, 905], 60, "frame")
d.box("pulse", [272, 640, 905, 348, 725, 975], "black", r=14, rot=rot("x", -11, [CX, 680, 940]))
d.box("pulse-pad", [262, 655, 918, 358, 710, 962], "plastic#2e3034", r=8, rot=rot("x", -11, [CX, 680, 940]))
d.lathe("knob", [CX, 770, 870], [[0, 0], [10, 0], [10, 20], [26, 26], [26, 40], [0, 44]], "black", axis="z",
        rot=rot("y", 180, [CX, 770, 870]))
CR = rot("x", -12, [CX, 840, 900])
d.box("console", [215, 820, 850, 405, 890, 950], "plastic#c3c6ca", r=16, rot=CR)
d.decal("console-rib", [CX, 840, 950.6], [170, 6], "front", "plastic#8e9196", rot=CR, repeat=rep(5, [0, 10, 0]))
d.decal("console-rib-b", [CX, 840, 849.4], [170, 6], "back", "plastic#8e9196", rot=CR, repeat=rep(5, [0, 10, 0]))
SR = rot("x", 38, [CX, 885, 880])
d.box("lcd-frame", [210, 885, 868, 410, 1000, 892], "metal#d5d8dc", r=8, rot=SR)
d.screen("lcd", [232, 905, 862, 388, 985, 870], "plastic#3a3d42", face="back", bezel=6, rot=SR)
d.decal("lcd-key", [285, 896, 861.4], [18, 8], "back", "gloss#d9302b", rot=SR, soft=True, copies=[[50, 0, 0]])
for nm, x in (("l", 190), ("r", 430)):
    d.tube(f"bar-{nm}", [[CX, 845, 920], [x, 840, 905], [x, 900, 885], [x, 975, 850], [x + (10 if x > CX else -10), 1000, 805]], 34,
           "foam", bend=45)
d.save()
