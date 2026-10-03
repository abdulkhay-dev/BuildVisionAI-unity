"""XY-1 upright magnetic bike. Front (+z) = the handlebar end the rider faces. Light-grey tube frame, front and
(curved) rear stabilisers with big black caps, dark-grey glossy flywheel shroud with silver ribbed side panels and a
light-blue spoked crank cap, black saddle, black curved handlebar, small light-blue console, black tension knob."""
import math
from k9lib import *
d = K("xy-1", [520, 880, 1250], {
    "tube": "metal#c4c7cb", "shroud": "gloss#5e6166", "silver": "metal#d3d5d8", "cap": "rubber#18191b",
    "black": "plastic#1c1d20", "seat": "leather#1d1e21", "blue": "gloss#5cb9e8", "chrome": "chrome", "foam": "rubber#1e1f22"})
CX = 260
# --- stabilisers
d.cyl("foot-f", [70, 35, 800], [450, 35, 800], 50, "tube")
endcap(d, "foot-f-c0", [70, 35, 800], "x", dia=70, ln=62, flip=True)
endcap(d, "foot-f-c1", [450, 35, 800], "x", dia=70, ln=62)
# rear stabiliser (photo): a shallow U in plan, its ends bending back to the black caps
d.tube("foot-r", [[60, 35, 72], [60, 35, 110], [140, 35, 175], [380, 35, 175], [460, 35, 110], [460, 35, 72]], 50, "tube", bend=60)
endcap(d, "foot-r-c0", [60, 35, 72], "z", dia=70, ln=62, flip=True)
endcap(d, "foot-r-c1", [460, 35, 72], "z", dia=70, ln=62, flip=True)
d.tube("beam-f", [[CX, 40, 800], [CX, 95, 700], [CX, 120, 640]], 52, "tube", bend=80)
d.tube("beam-r", [[CX, 40, 175], [CX, 95, 250], [CX, 130, 300]], 52, "tube", bend=60)
# --- flywheel shroud (photo): a D-shaped side profile (a low rounded nose at the front, a domed top, a full rounded
# rear), dark-grey gloss; silver ribbed covers wrap the front-lower nose and the rear-upper corner; a dark round dish
# around the crank carries the light-blue spoked cap
HZ, HY = 480, 285                                   # crank hub
KEY = [(z, y + 30) for z, y in [(745, 262), (722, 325), (668, 368), (590, 395), (480, 408), (380, 405), (318, 382), (290, 330),
       (286, 250), (300, 165), (345, 112), (450, 95), (590, 100), (690, 125), (735, 175)]]
def smooth(pts, n=5):
    out = []
    for i in range(len(pts)):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % len(pts)], pts[(i + 2) % len(pts)]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    return out
BODY = smooth(KEY)
def clip(poly, a, b):
    """Keep the part of poly left of the directed line a->b (Sutherland-Hodgman)."""
    side = lambda p: (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    out = []
    for i in range(len(poly)):
        p, q = poly[i - 1], poly[i]
        sp, sq = side(p), side(q)
        if sq >= 0:
            if sp < 0: out.append(lerp(p, q, sp / (sp - sq)))
            out.append(q)
        elif sp >= 0:
            out.append(lerp(p, q, sp / (sp - sq)))
    return out
def grow(poly, e):
    cz, cy = sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)
    return [(p[0] + (p[0] - cz) * e, p[1] + (p[1] - cy) * e) for p in poly]
def chord(poly, y):
    zs = []
    for i in range(len(poly)):
        p, q = poly[i - 1], poly[i]
        if (p[1] - y) * (q[1] - y) < 0:
            zs.append(p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1]))
    return (min(zs), max(zs)) if len(zs) >= 2 else None
SW = 120                                            # half width of the shroud
d.slab("shroud", "side", poly(BODY), [CX - SW, CX + SW], "shroud", r=48)
FRONT = clip(grow(BODY, 0.012), (745, 275), (605, 365))     # below the dark top strip ...
FRONT = clip(FRONT, (590, 420), (575, 60))                   # ... and in front of z ~ 585
REAR = clip(grow(BODY, 0.012), (300, 235), (440, 460))       # behind/above a line from the rear-lower to the top
d.slab("cover-f", "side", poly(FRONT), [CX - SW - 1.5, CX + SW + 1.5], "silver", r=47)
d.slab("cover-r", "side", poly(REAR), [CX - SW - 1.5, CX + SW + 1.5], "silver", r=47)
for nm, s in (("l", -1), ("r", 1)):
    x = CX + s * (SW + 1.5)
    face = "right" if s > 0 else "left"
    for pn, P, y0, y1, st in (("f", FRONT, 158, 330, 14), ("r", REAR, 285, 422, 14)):
        y = y0
        k = 0
        while y <= y1:
            c = chord(P, y)
            if c and c[1] - c[0] > 30:
                d.decal(f"rib-{pn}{nm}{k}", [x + s * 0.6, y, (c[0] + c[1]) / 2], [c[1] - c[0] - 36, 3], face, "plastic#9a9ea3")
            y += st; k += 1
    hx = CX + s * (SW + 1)
    d.cyl(f"dish-{nm}", [hx, HY, HZ], [hx + s * 7, HY, HZ], 290, "gloss#4b4e53")
    # crank cap: dark ring, light-blue disc, 5 dark spokes, dark hub
    hx = CX + s * 127
    d.cyl(f"cap-ring-{nm}", [hx, HY, 480], [hx + s * 8, HY, 480], 175, "plastic#45484d")
    d.cyl(f"cap-blue-{nm}", [hx + s * 8, HY, 480], [hx + s * 11, HY, 480], 140, "blue")
    for k in range(5):
        a = 90 + k * 72
        cz, cy = 480 + 45 * math.cos(math.radians(a)), HY + 45 * math.sin(math.radians(a))
        d.decal(f"spoke-{nm}{k}", [hx + s * 11.6, cy, cz], [90, 8], face, "plastic#45484d",
                rot=rot("x", -a if s > 0 else -a, [hx + s * 11.6, cy, cz]))
    d.cyl(f"hub-{nm}", [hx + s * 11, HY, 480], [hx + s * 25, HY, 480], 55, "black")
    # crank arm + pedal with strap
    ang = 281 if s > 0 else 101
    pz, py = 480 + 165 * math.cos(math.radians(ang)), HY + 165 * math.sin(math.radians(ang))
    d.bar(f"crank-{nm}", [hx + s * 30, HY, 480], [hx + s * 30, py, pz], [22, 14], "chrome", r=5)
    px0 = hx + s * 40
    a_, b_ = sorted([px0, px0 + s * 110])
    d.box(f"pedal-{nm}", [a_, py - 15, pz - 45, b_, py + 15, pz + 45], "black", r=6)
    d.strap(f"pedal-strap-{nm}", [[a_ + 10, py + 12, pz - 30], [(a_ + b_) / 2, py + 38, pz - 15], [b_ - 10, py + 12, pz - 30]],
            [30, 5], "black", bend=40)
# --- seat post (leans back), knob, black saddle
d.cyl("seat-sleeve", [CX, 400, 340], [CX, 540, 310], 58, "tube")
d.cyl("seat-post", [CX, 500, 314], [CX, 880, 230], 46, "tube")
d.cyl("seat-knob-stem", [CX, 470, 320], [CX, 470, 260], 14, "chrome")
d.sphere("seat-knob", [CX, 470, 255], 40, "black")
d.box("seat-clamp", [CX - 30, 870, 200, CX + 30, 900, 270], "black", r=6)
saddle = rpoly([(CX - 130, 90), (CX + 130, 90), (CX + 120, 210), (CX + 60, 320), (CX - 60, 320), (CX - 120, 210)], 45)
d.slab("saddle", "top", saddle, [895, 955], "seat", r=22)
# --- front column, tension knob, console, handlebar
d.cyl("column", [CX, 400, 650], [CX, 1060, 745], 52, "tube")
d.box("knob-block", [CX - 40, 760, 655, CX + 40, 840, 700], "black", r=8)
d.cyl("knob", [CX, 800, 660], [CX, 800, 615], 80, "black")
d.decal("knob-dial", [CX, 800, 614.4], [50, 50], "back", "plastic#3a3c40")
d.box("bar-clamp", [CX - 35, 980, 705, CX + 35, 1030, 760], "tube", r=8)
# handlebar: black foam, across behind the column, both ends sweeping back towards the rider then up and forward
for nm, s in (("l", -1), ("r", 1)):
    d.tube(f"bar-{nm}", [[CX, 1005, 735], [CX + s * 150, 1005, 680], [CX + s * 215, 1020, 600], [CX + s * 225, 1100, 640],
                         [CX + s * 215, 1235, 745]], 36, "foam", bend=70)
d.box("console", [CX - 80, 1060, 700, CX + 80, 1100, 830], "silver", r=12, rot=rot("x", 25, [CX, 1060, 760]))
d.box("console-face", [CX - 70, 1098, 710, CX + 70, 1104, 820], "blue", r=8, rot=rot("x", 25, [CX, 1060, 760]))
d.box("console-lcd", [CX - 40, 1103, 740, CX + 40, 1106, 795], "screen", r=3, rot=rot("x", 25, [CX, 1060, 760]))
d.save()
