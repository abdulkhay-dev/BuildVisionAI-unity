"""NMES XY-K-SISS-C and TENS XY-K-SJD-C: one moulded cart, accent colour and socket panel differ.
Writes only xy-k-siss-c.json and xy-k-sjd-c.json."""
from lib import *

def qpts(p0, c, p1, n=12):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]) for t in (k / n for k in range(n + 1))]

def band(pts, half):
    """Closed outline of a band of half-width `half` along a polyline (plane coords)."""
    import math
    L, R = [], []
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, len(pts) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l * half, dx / l * half
        L.append((p[0] + nx, p[1] + ny)); R.append((p[0] - nx, p[1] - ny))
    ring = L + R[::-1]
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in ring) + " Z"

def build(id_, acc, basec, frame, cols, ring_top, letter, tag):
    d = D(id_, [600, 520, 1060], {
        "shell": "gloss#f6f7f9", "door": "gloss#fbfbfc", "acc": acc, "frame": frame, "glass": "gloss#7f858d",
        "grey": "plastic#d3d6da", "dark": "plastic#3b4046", "black": "gloss#141517", "blue": "gloss#2f7fd0"})
    # ---- base: H-plinth with concave edges, castors at its corners
    base = ("M 15 45 Q 15 0 60 0 Q 300 90 540 0 Q 585 0 585 45 Q 500 260 585 475 Q 585 520 540 520 "
            "Q 300 470 60 520 Q 15 520 15 475 Q 100 260 15 45 Z")
    d.slab("base", "top", base, [120, 170], basec, r=14)
    d.add("castor", "caster", "rubber#9aa0a7", at=[60, 0, 60], d=100, copies=[[480, 0, 0], [0, 0, 400], [480, 0, 400]])
    d.cyl("castor-boss", [60, 112, 60], [60, 122, 60], 44, basec, copies=[[480, 0, 0], [0, 0, 400], [480, 0, 400]])
    # ---- body
    d.box("body", [100, 168, 70, 500, 1058, 490], "shell", r=40)
    d.box("top-glass", [122, 1050, 92, 478, 1061, 468], "glass", r=12)
    # swoosh stripe on both sides (side plane: a = z, b = y)
    sw = "M 312 1012 C 314 760 352 450 448 172 L 418 172 C 340 420 300 620 252 800 C 218 920 160 992 92 1012 Z"
    d.slab("swoosh", "side", sw, [96, 101], "acc", r=1.5, mirror="x")
    # seam line: across the front, then curving up each side to the swoosh's top
    d.decal("seam-front", [300, 928, 490], [330, 5], "front", "acc", soft=True)
    d.slab("seam-side", "side", band(qpts((452, 928), (360, 930), (314, 1010)), 2.5), [97, 101], "acc", r=1, mirror="x")
    # ---- socket panel
    # (centred on the front and ~3/4 of its width, as the doors under it)
    d.box("sock-frame", [142, 943, 486, 448, 1030, 495], "frame", r=10)
    d.box("sock-panel", [152, 952, 492, 438, 1021, 496.5], "plastic#d6dade", r=6)
    xs0, xs1 = (208, 392) if cols == 4 else (190, 410)
    step = (xs1 - xs0) / (cols - 1)
    row = [[step * k, 0, 0] for k in range(1, cols)]
    d.cyl("sock-top", [xs0, 1002, 495], [xs0, 1002, 500], 18, ring_top, copies=row)
    d.cyl("sock-bot", [xs0, 971, 495], [xs0, 971, 500], 18, "plastic#a7adb4", copies=row)
    d.cyl("sock-pin", [xs0, 1002, 498], [xs0, 1002, 502], 7, "dark", copies=row + [[step * k, -31, 0] for k in range(cols)])
    d.decal("sock-warn", [162, 961, 496.7], [8, 8], "front", "gloss#f2c21b", soft=True)
    # ---- doors
    d.box("door-gap", [135, 632, 487, 455, 862, 491], "plastic#50565c", r=4)
    d.box("door-up", [138, 793, 487, 452, 859, 494], "door", r=5)
    d.box("door-lo", [138, 635, 487, 452, 790, 494], "door", r=5)
    tab = "M 225 {t} L 365 {t} L 365 {m} Q 360 {b} 345 {b} L 245 {b} Q 230 {b} 225 {m} Z"
    d.slab("handle-up", "front", tab.format(t=857, m=850, b=840), [493, 496], "black", r=1)
    d.slab("handle-lo", "front", tab.format(t=788, m=781, b=771), [493, 496], "black", r=1)
    d.slab("warn", "front", "M 283 812 L 307 812 L 295 833 Z M 287 815 L 303 815 L 295 829 Z", [493, 495], "dark", r=0.5)
    d.decal("door-icon", [295, 748, 494], [40, 9], "front", "plastic#a3a9b0", soft=True)
    # ---- logo and lettering
    d.cyl("logo-mark", [226, 610, 489], [226, 610, 492], 30, "blue", soft=True)
    d.decal("logo-text", [288, 616, 490], [72, 13], "front", "plastic#5b97d9", soft=True)
    d.decal("logo-sub", [292, 599, 490], [76, 5], "front", "plastic#8db0d8", soft=True)
    d.decal("letter-line", [398, 347, 490], [3, 275], "front", letter, soft=True)
    d.decal("letter-kink", [398, 452, 490], [12, 9], "front", letter, soft=True, rot=rot("z", 35, [398, 452, 490]))
    d.decal("letters", [374, 427, 490], [11, 18], "front", letter, soft=True, copies=[[0, -37 * k, 0] for k in range(1, 4)])
    d.decal("tag", [417, 262, 490], [22, 100], "front", tag, soft=True)
    d.decal("tag-text", [417, 300, 490.3], [11, 13], "front", "plastic#eef6f8", soft=True, repeat=rep(4, [0, -24, 0]))
    # ---- cable holder (right side): open tray with a comb, solid pocket at the front end
    d.box("holder-back", [500, 800, 95, 507, 905, 470], "grey", r=2)
    d.box("holder-floor", [500, 800, 95, 590, 808, 470], "grey", r=3)
    out = "M 95 800 L 470 800 L 470 895 L 335 895"
    for z0 in (290, 225, 160):
        out += f" L {z0 + 26} 895 L {z0 + 26} 862 Q {z0 + 26} 848 {z0 + 13} 848 Q {z0} 848 {z0} 862 L {z0} 895"
    out += " L 95 895 Z"
    d.slab("holder-wall", "side", out, [583, 590], "grey", r=2)
    d.box("holder-end", [500, 800, 95, 590, 895, 101], "grey", r=2, copies=[[0, 0, 369], [0, 0, 230]])
    # small hook bracket (left side)
    d.slab("hook-tab", "side", "M 398 800 L 446 800 L 446 850 Q 446 874 422 874 Q 398 874 398 850 Z", [60, 66], "grey", r=2)
    d.box("hook-foot", [60, 796, 398, 100, 804, 446], "grey", r=2)
    d.save()

build("xy-k-siss-c", "plastic#22a3b5", "plastic#22a3b5", "plastic#8fd8e2", 4, "plastic#a7adb4", "plastic#7cc6d2", "plastic#2aa7b8")
build("xy-k-sjd-c", "plastic#868b92", "plastic#a3a8ae", "plastic#c4c8cd", 6, "gloss#2f7fd0", "plastic#8db3dc", "plastic#5d9ad6")
