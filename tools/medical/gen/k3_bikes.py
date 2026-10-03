"""XY-2 upright bike and XY-1A upright bike (commercial), kinesio-3. Front (z = depth) = the end the rider faces
(console, handlebars), the seat at the back — as the other bikes of the catalogue (kinesio-4)."""
from k3_lib import *


def path_svg(pts):
    return "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in pts) + " Z"


def smooth(pts, n=6):
    """closed Chaikin-smoothed polygon"""
    for _ in range(n // 2):
        out = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            out.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            out.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        pts = out
    return pts


def shrink(pts, k):
    cz = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    return [(cz + (p[0] - cz) * k, cy + (p[1] - cy) * k) for p in pts]


def pedals(d, hub, xl, xr, crank=170, ang=35, mat_c="metal#c3c6ca"):
    """cranks at `ang` deg from the vertical (left one forward-down), black pedals with straps"""
    a = math.radians(ang)
    for k, (x, sgn, xo) in enumerate(((xl, 1, -1), (xr, -1, 1))):
        pz = hub[2] + sgn * crank * math.sin(a); py = hub[1] - sgn * crank * math.cos(a)
        d.bar(f"crank{k}", [x, hub[1], hub[2]], [x, py, pz], [26, 14], mat_c, r=5)
        px = x + xo * 60
        d.cyl(f"spindle{k}", [x, py, pz], [px, py, pz], 14, "chrome")
        d.box(f"pedal{k}", [px - 50 if xo > 0 else px - 50, py - 14, pz - 55, px + 50, py + 14, pz + 55], "plastic#202224", r=6)
        d.strap(f"pstrap{k}", [[px - 48, py + 12, pz + 25], [px - 40, py + 45, pz + 10], [px + 40, py + 45, pz + 10],
                               [px + 48, py + 12, pz + 25]], [36, 3], "plastic#2a2c2f", bend=15, soft=True)


def xy2():
    W, Dd, H = 450, 1160, 1230
    d = D("xy-2", [W, Dd, H], {"frame": "metal#a9acb0", "shell": "metal#b7babd", "panel": "metal#9a9ea2",
                                "black": "plastic#1f2022", "cyan": "gloss#3cc6e0"})
    XC = W / 2
    hub = [XC, 300, 735]
    # floor stabilisers with black end caps (front ones are transport wheels)
    d.cyl("stab-r", [40, 34, 85], [W - 40, 34, 85], 58, "frame")
    d.cyl("cap-r", [0, 34, 85], [44, 34, 85], 66, "black", copies=[[W - 44, 0, 0]])
    d.cyl("stab-f", [45, 34, Dd - 80], [W - 45, 34, Dd - 80], 58, "frame")
    d.add("wheel-f", "wheel", "black", at=[22, 36, Dd - 80], d=72, d2=44, axis="x", copies=[[W - 44, 0, 0]])
    # legs from the housing to the stabilisers
    d.sweep("leg-r", [[XC, 170, 300], [XC, 110, 190], [XC, 50, 110]], [70, 45], "frame", shape="oval", bend=60)
    d.sweep("leg-f", [[XC, 160, 860], [XC, 90, 980], [XC, 50, Dd - 95]], [70, 45], "frame", shape="oval", bend=80)
    # housing ((review) photo: an egg whose narrow top meets the seat post and whose belly reaches far back over the
    # rear foot, the rear edge sweeping down from the seat post; the first draft stopped at the seat post)
    out = smooth([(910, 440), (935, 320), (905, 185), (820, 115), (650, 95), (450, 100), (280, 120), (190, 170),
                  (175, 280), (230, 420), (330, 540), (420, 600), (520, 590), (660, 530), (800, 470)], 6)
    d.slab("housing", "side", path_svg(out), [XC - 95, XC + 95], "shell", r=40)
    inner = shrink(out, 0.8)
    d.slab("panel", "side", path_svg(inner), [XC - 98, XC + 98], "panel", r=10)
    # cyan ring round the crank hub on both sides, dark hub disc, three cyan stripes at the top front
    for sgn, x in ((-1, XC - 100), (1, XC + 100)):
        n = "l" if sgn < 0 else "r"
        d.tube(f"ring-{n}", ring(x, hub[1], hub[2], 118, 118, "zy", 28), 16, "cyan")
        d.cyl(f"rdisc-{n}", [x - sgn * 4, hub[1], hub[2]], [x + sgn * 2, hub[1], hub[2]], 222, "shell")
        d.cyl(f"hubc-{n}", [x, hub[1], hub[2]], [x + sgn * 12, hub[1], hub[2]], 60, "black")
        for k in range(3):
            d.add(f"stripe-{n}{k}", "decal", "cyan", at=[x + sgn * 0.5 - sgn * 2, 500 - k * 22, 600 - k * 6], size=[150, 8],
                  face="left" if sgn < 0 else "right", soft=True,
                  rot={"axis": "x", "deg": 12 if sgn < 0 else 12, "about": [x, 500 - k * 22, 600 - k * 6]})
    pedals(d, hub, XC - 112, XC + 112)
    # curved handlebar column (oval), tension knob, console, black handlebar
    d.sweep("column", [[XC, 430, 850], [XC, 640, 905], [XC, 900, 950], [XC, 1085, 965]], [72, 46], "frame",
            shape="oval", bend=260)
    d.cyl("knob", [XC, 880, 925], [XC, 880, 880], 62, "black")
    d.cyl("knob-c", [XC, 880, 880], [XC, 880, 872], 40, "plastic#3a3c40")
    cons = [XC - 95, 1060, 930, XC + 95, 1180, 1010]
    ab = [XC, 1080, 970]
    d.box("console", cons, "shell", r=18, rot={"axis": "x", "deg": 28, "about": ab})
    d.add("lcd", "screen", "plastic#5c6066", box=[XC - 60, 1095, 925, XC + 60, 1150, 935], face="back", bezel=6,
          rot={"axis": "x", "deg": 28, "about": ab})
    d.add("lcd-blue", "decal", "gloss#41b6e6", at=[XC + 35, 1110, 924], size=[30, 18], face="back", soft=True,
          rot={"axis": "x", "deg": 28, "about": ab})
    for sgn in (-1, 1):
        n = "l" if sgn < 0 else "r"
        x0 = XC + sgn * 30
        x1 = XC + sgn * 170
        d.tube(f"bar-{n}", [[x0, 1030, 975], [x1, 1030, 975], [x1 + sgn * 10, 1140, 985], [x1 + sgn * 18, 1215, 1030]], 32,
               "black", bend=60)
        d.cyl(f"barcap-{n}", [x1 + sgn * 18, 1215, 1030], [x1 + sgn * 19, 1222, 1036], 30, "plastic#3a3c40")
    # seat: black bellows post, silver slider with knob, black saddle
    d.add("seatpost", "tube", "black", path=[[XC, 590, 420], [XC, 820, 360]], d=50, rib=4, pitch=14)
    d.cyl("collar", [XC, 580, 425], [XC, 640, 410], 64, "frame")
    d.cyl("knob-s", [XC + 30, 620, 440], [XC + 55, 620, 470], 34, "black")
    d.bar("slider", [XC, 835, 470], [XC, 835, 250], [44, 30], "frame", r=5)
    d.cyl("knob-sl", [XC, 812, 250], [XC, 790, 250], 36, "black")
    d.loft("saddle", [sec(850, 150, 290, 60, XC, 360), sec(890, 230, 280, 80, XC, 380), sec(915, 220, 270, 80, XC, 380)],
           "black", dome="end", domeH=10)
    d.box("nose", [XC - 50, 880, 470, XC + 50, 915, 560], "black", r=20)
    # black carry strap at the housing top in front of the seat post
    d.strap("handle", [[XC, 600, 520], [XC, 650, 500], [XC, 655, 450], [XC, 610, 430]], [30, 6], "black", bend=20)
    d.save()


def xy1a():
    W, Dd, H = 650, 1040, 1380
    d = D("xy-1a", [W, Dd, H], {"shell": "metal#b9bcc0", "post": "metal#c9ccd0", "black": "plastic#1d1e20",
                                 "rubber": "rubber#202124", "red": "gloss#c8302a", "dark": "plastic#4a4e54"})
    XC = W / 2
    hub = [XC, 330, 640]
    # rear rubber stabiliser bar, small front foot with transport wheels
    d.box("stab-r", [25, 0, 45, W - 25, 72, 145], "rubber", r=30)
    d.box("stab-f", [XC - 170, 0, 900, XC + 170, 55, 990], "rubber", r=22)
    d.add("wheel-f", "wheel", "rubber", at=[XC - 175, 32, 960], d=60, d2=30, axis="x", copies=[[350, 0, 0]])
    # long curved housing: front tower under the console post, low middle, the seat tower and a tail sweeping down
    # to the rear foot
    out = smooth([(975, 70), (995, 320), (965, 560), (890, 625), (760, 625), (600, 625), (470, 640),
                  (380, 600), (335, 470), (270, 300), (190, 140), (150, 70), (260, 75), (420, 150), (600, 165),
                  (800, 120), (900, 60)], 6)
    d.slab("housing", "side", path_svg(out), [XC - 130, XC + 130], "shell", r=55)
    # dark recess behind the cranks on both sides
    rec = smooth([(680, 150), (685, 540), (600, 540), (595, 150)], 4)
    d.slab("recess", "side", path_svg(rec), [XC - 133, XC + 133], "dark", r=8)
    d.cyl("hubc", [XC - 140, hub[1], hub[2]], [XC + 140, hub[1], hub[2]], 70, "post")
    pedals(d, hub, XC - 145, XC + 145, crank=170, ang=40)
    # black collars, console post (silver), cup holder
    d.loft("collar-f", [sec(560, 180, 200, 60, XC, 880), sec(640, 140, 140, 60, XC, 890), sec(720, 100, 100, 48, XC, 895)],
           "black")
    d.cyl("post", [XC, 700, 895], [XC, 1180, 860], 82, "post")
    d.lathe("cup", [XC, 820, 795], [[0, 0], [42, 0], [48, 110], [44, 112], [0, 8]], "black")
    d.box("cup-arm", [XC - 15, 860, 800, XC + 15, 900, 860], "black", r=6)
    # console: silver bezel, dark face with an LCD and a key field, tilted to the rider
    ab = [XC, 1240, 860]
    tilt = -40
    d.box("console", [XC - 180, 1195, 760, XC + 180, 1265, 980], "post", r=30, rot={"axis": "x", "deg": tilt, "about": ab})
    d.add("face", "screen", "dark", box=[XC - 160, 1262, 775, XC + 160, 1270, 965], face="top", bezel=4,
          rot={"axis": "x", "deg": tilt, "about": ab})
    d.add("lcd", "decal", "plastic#2b3036", at=[XC - 20, 1271, 905], size=[200, 70], face="top", soft=True,
          rot={"axis": "x", "deg": tilt, "about": ab})
    d.add("keys", "decal", "plastic#7d838a", at=[XC, 1271, 830], size=[30, 12], face="top", soft=True,
          rot={"axis": "x", "deg": tilt, "about": ab}, repeat={"n": 6, "step": [45, 0, 0], "local": True})
    d.add("keys-w", "decal", "plastic#e4e6e8", at=[XC - 112, 1271, 800], size=[24, 9], face="top", soft=True,
          rot={"axis": "x", "deg": tilt, "about": ab}, repeat={"n": 6, "step": [45, 0, 0], "local": True})
    d.add("bezel-lip", "box", "plastic#d7d9dc", box=[XC - 175, 1200, 755, XC + 175, 1240, 790], r=14,
          rot={"axis": "x", "deg": tilt, "about": ab})
    # black ergonomic handlebars round the console, silver pulse grips, horns rising at the outer ends
    for sgn in (-1, 1):
        n = "l" if sgn < 0 else "r"
        d.tube(f"bar-{n}", [[XC + sgn * 35, 1130, 850], [XC + sgn * 200, 1140, 830], [XC + sgn * 270, 1150, 740],
                            [XC + sgn * 280, 1190, 680], [XC + sgn * 285, 1330, 690]], 34, "black", bend=60)
        d.cyl(f"pulse-{n}", [XC + sgn * 120, 1134, 842], [XC + sgn * 205, 1140, 826], 40, "post")
        d.cyl(f"barcap-{n}", [XC + sgn * 285, 1330, 690], [XC + sgn * 285, 1340, 690], 32, "plastic#3a3c40")
    # seat: black collar, red-anodised post with a silver top, black contoured saddle, orange knob
    d.loft("collar-s", [sec(580, 190, 240, 70, XC, 450), sec(660, 140, 150, 60, XC, 440), sec(720, 90, 90, 40, XC, 430)],
           "black")
    d.cyl("seatpost", [XC, 700, 432], [XC, 830, 405], 48, "red")
    d.cyl("seatpost-t", [XC, 830, 405], [XC, 860, 400], 44, "post")
    d.sphere("knob", [XC + 70, 650, 520], 34, "gloss#f08a24")
    d.loft("saddle", [sec(860, 160, 300, 60, XC, 400), sec(905, 250, 290, 90, XC, 410), sec(935, 240, 270, 90, XC, 405)],
           "black", dome="end", domeH=12)
    d.box("nose", [XC - 55, 900, 500, XC + 55, 932, 575], "black", r=22)
    d.save()


xy2()
xy1a()
