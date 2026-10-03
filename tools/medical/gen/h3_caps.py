"""Steam capsules HYZ-IIID (horizontal), HYZ-IIIE (swing cabin + LCD trolley), HYZ-IIIB (swing capsule + console).
Head end at the left as in the photos; consoles/trolleys stand at the left."""
import sys
from h3lib import *
Design = D

MATS = {"shell": "gloss#f7f8f9", "dark": "plastic#2e3238", "grey": "plastic#8d97aa", "blue": "gloss#2f62d8",
        "green": "gloss#2fb24a", "steel": "metal#c9ccd0", "inner": "gloss#eef1f4"}


def rbox(d, id, b, rplan, redge, mat, **kw):
    x0, y0, z0, x1, y1, z1 = b
    return d.slab(id, "top", rrp(x0, z0, x1, z1, rplan), [y0, y1], mat, r=redge, **kw)


def z_surf(w, dd, r, cy, cz, y):
    hw, hd = w / 2, dd / 2
    dy = abs(y - cy)
    if dy <= hd - r: return cz + hw
    t = min(dy - (hd - r), r)
    return cz + hw - r + math.sqrt(max(r * r - t * t, 0))


def turn(p, piv, deg):
    """Point p (x, y) turned about piv by deg (engine sense about z: +deg turns x towards y)."""
    a = math.radians(deg)
    dx, dy = p[0] - piv[0], p[1] - piv[1]
    return (piv[0] + dx * math.cos(a) - dy * math.sin(a), piv[1] + dx * math.sin(a) + dy * math.cos(a))


# ------------------------------------------------------------------ HYZ-IIID
def interp(S, x):
    for a, b in zip(S, S[1:]):
        if a[0] <= x <= b[0]:
            t = (x - a[0]) / (b[0] - a[0])
            return [a[k] + (b[k] - a[k]) * t for k in range(len(a))]
    return list(S[0] if x < S[0][0] else S[-1])


def hyz_iiid():
    W, Dp, H = 1900, 900, 1300
    d = Design("hyz-iiid", [W, Dp, H], dict(MATS))
    cz = Dp / 2
    # (x, w across z, d across y, r, cy)
    # (x, w across z, d across y, r, cy): tall head back at the left, the lid sloping to a blunt foot end
    S = [(130, 820, 1000, 380, 790), (250, 870, 1020, 400, 780), (380, 880, 1000, 400, 770), (500, 880, 900, 400, 720),
         (800, 880, 860, 400, 690), (1150, 880, 790, 370, 630), (1500, 870, 720, 330, 545), (1800, 840, 620, 280, 490)]
    d.loft("shell", [{"at": x, "w": w, "d": dd, "r": r, "cx": cy, "cz": cz} for x, w, dd, r, cy in S], "shell", axis="x",
           dome="end", domeH=90)
    # grey rear of the head shell
    d.loft("head-back", [{"at": 20, "w": 700, "d": 860, "r": 330, "cx": 760, "cz": cz},
                         {"at": 150, "w": 800, "d": 980, "r": 380, "cx": 785, "cz": cz}], "grey", axis="x", dome="start",
           domeH=50)
    # scooped head rest between the head back and the lid (light inner)
    d.sphere("head-well", [380, 1262, cz], None, "gloss#e3e7ec", radii=[130, 32, 300])
    def zs(x, y):
        _, w, dd, r, cy = interp(S, x)
        return z_surf(w, dd, r, cy, cz, y)
    def top(x):
        _, w, dd, r, cy = interp(S, x)
        return cy + dd / 2
    # grey skirt along the bottom, castors
    d.loft("skirt", [{"at": 120, "w": 640, "d": 300, "r": 120, "cx": 245, "cz": cz},
                     {"at": 1780, "w": 640, "d": 300, "r": 120, "cx": 245, "cz": cz}], "grey", axis="x", dome="both", domeH=60)
    casters(d, "castor", [(220, 150), (220, Dp - 150), (1680, 150), (1680, Dp - 150)], 75)
    # white lower head block with the big round side panel (flat front)
    # review: the lower head block follows the round side panel (the photo's shell edge rises from the circle)
    k_ = 0.5523 * 292
    d.slab("headblock", "front", f"M 60 95 L 340 88 C {340 + k_} 88 632 {380 - k_} 632 380 L 632 560 L 60 560 Z",
           [40, Dp - 24], "shell", r=60)
    zf = Dp - 20             # review: panel brought forward so the shell's bulge no longer cuts its top
    d.lathe("panel", [340, 380, zf - 6], [[0, 0], [262, 0], [262, 14], [250, 24], [0, 24]], "gloss#f3f4f6", axis="z")
    d.decal("panel-emb-v", [345, 470, zf + 19], [26, 120], "front", "plastic#dfe3e8", soft=True)
    d.decal("panel-emb-h", [330, 520, zf + 19], [120, 22], "front", "plastic#dfe3e8", soft=True)
    text3(d, "panel-cn", "翔宇医疗", [205, 395, zf + 19], 52, "plastic#d9dde3", gap=0.2, stroke=9)
    green_btns = [(250, 300), (330, 300), (270, 255), (350, 255), (290, 210), (370, 210)]
    for i, (x, y) in enumerate(green_btns):
        btn(d, f"gb{i}", [x, y, zf + 18], 20, "front", "green", h=6, ring_mat="plastic#e0e3e7")
    d.box("lcd", [310, 165, zf + 17, 345, 195, zf + 20], "dark", r=2)
    d.decal("plate", [118, 380, zf + 19], [60, 150], "front", "plastic#c9cdd3", soft=True)
    # blue + grey double edge line: across the top behind the head, down the sides, along to the foot end
    def side_path(dy, back=False):
        pts = []
        for x, y in [(450, None), (500, 1120), (620, 960), (800, 800), (1000, 720), (1250, 690), (1500, 680), (1760, 680)]:
            yy = (top(x) - 30 if y is None else y) + dy
            z = zs(x, yy) + 3
            pts.append([x, yy, (Dp - z) if back else z])
        return pts
    for k, (dy, m) in enumerate(((0, "blue"), (-22, "plastic#c3c9d2"))):
        d.tube(f"seam{k}", side_path(dy), 13, m, bend=140, soft=True)
        d.tube(f"seam{k}b", side_path(dy, True), 13, m, bend=140, soft=True)
    d.tube("seam-top", [[450, top(450) - 30, zs(450, top(450) - 30) + 3], [450, top(450) + 3, cz],
                        [450, top(450) - 30, Dp - zs(450, top(450) - 30) - 3]], 13, "blue", bend=300, soft=True)
    # speaker disc on the head front, top cover disc, window patch, handle pocket
    ys = 1130
    d.lathe("speaker", [220, ys, zs(220, ys) - 8], [[0, 0], [62, 0], [62, 12], [0, 12]], "gloss#f0f2f4", axis="z")
    d.box("speaker-dots", [208, ys - 8, zs(220, ys) + 3, 212, ys - 4, zs(220, ys) + 5], "plastic#9aa1aa", soft=True,
          repeat=rep(4, [8, 0, 0]), copies=[[0, 8, 0], [0, 16, 0]])
    d.lathe("cover", [640, top(640) - 6, cz], [[0, 0], [130, 0], [130, 9], [110, 13], [0, 13]], "gloss#f1f3f5")
    d.sphere("window", [1020, top(1020) - 8, cz], None, "acrylic#6f95e6d0", radii=[190, 16, 160])
    yh = 960
    zp = zs(780, yh)
    d.box("pocket", [640, yh - 70, zp - 40, 920, yh + 70, zp + 6], "shell", r=30)
    d.box("pocket-in", [660, yh - 52, zp - 30, 900, yh + 52, zp + 8], "gloss#e6e9ec", r=22)
    d.cyl("pocket-bar", [675, yh - 5, zp + 4], [885, yh - 5, zp + 4], 24, "chrome")
    # flat hinge plate at the foot end
    d.box("hinge-plate", [1700, 650, 110, 1900, 712, Dp - 110], "shell", r=12)
    d.box("hinge", [1745, 712, 160, 1800, 722, 260], "chrome", r=3, copies=[[0, 0, 380]])
    d.box("hinge-pin", [1795, 690, 140, 1815, 735, 280], "chrome", r=6, copies=[[0, 0, 380]])
    return d


# ------------------------------------------------------------------ HYZ-IIIB
def console_iiib(d, cxm, czm):
    # X base on castors
    for k, a in enumerate((45, -45)):
        d.bar(f"cb-arm{k}", [cxm - 270 * math.cos(math.radians(a)), 95, czm - 270 * math.sin(math.radians(a))],
              [cxm + 270 * math.cos(math.radians(a)), 95, czm + 270 * math.sin(math.radians(a))], [80, 46], "shell", r=18)
    pts = [(cxm + 245 * math.cos(math.radians(a)), czm + 245 * math.sin(math.radians(a))) for a in (45, 135, 225, 315)]
    casters(d, "cb-castor", pts, 55, "rubber#1d1d1d")
    d.loft("cb-col", [sec(118, 250, 230, 95, cxm, czm), sec(500, 300, 260, 110, cxm, czm),
                      sec(780, 360, 300, 125, cxm, czm)], "shell")
    # head: sloped top with a grey LCD
    z0, z1 = czm - 150, czm + 150
    d.slab("cb-head", "side", rp([(z0, 780), (z1, 780), (z1, 820), (z0, 880)], [0, 0, 20, 30]),
           [cxm - 180, cxm + 180], "shell", r=30)
    ang = math.degrees(math.atan2(60, z1 - z0))
    tr = rot("x", ang, [0, 880, z0])
    d.box("cb-frame", [cxm - 150, 877, z0 + 30, cxm + 150, 881, z1 - 20], "plastic#b9bec4", r=24, rot=tr)
    d.box("cb-lcd", [cxm - 105, 880, z0 + 55, cxm + 105, 883, z1 - 70], "plastic#6d737a", r=4, rot=tr)
    # blue curve line round the upper part and down the right side
    yb = 650
    d.tube("cb-line", [[cxm - 172, yb + 30, czm - 40], [cxm - 120, yb, czm + 150], [cxm, yb - 30, czm + 156],
                       [cxm + 120, yb, czm + 150], [cxm + 172, yb + 30, czm - 40]], 6, "blue", bend=120, soft=True)
    d.tube("cb-line2", [[cxm + 172, yb + 10, czm + 60], [cxm + 158, 400, czm + 40], [cxm + 140, 160, czm - 30]], 6, "blue",
           bend=200, soft=True)
    logo(d, "cb-logo", [cxm - 70, 440, czm + 138], 36, "front")


def hyz_iiib():
    Dp, H = 840, 1900
    X0 = 720                     # left of the capsule assembly
    L, t, th = 1450, 640, -40          # review: the photos show ~38-40 deg
    d = Design("hyz-iiib", [2200, Dp, H], dict(MATS))
    console_iiib(d, 300, 420)
    # capsule in its horizontal pose: x in [Xc - L/2, Xc + L/2], y in [Yc, Yc + t]; turned about the pivot (Xc, Yc)
    Xc, Yc = 1233, 773
    piv = [Xc, Yc, 0]
    R_ = rot("z", th, piv)
    xa, xb = Xc - L / 2, Xc + L / 2
    zf, zb = Dp - 10, 10
    plan = rrp(xa, zb, xb, zf, 230)
    d.slab("cap", "top", plan, [Yc, Yc + t], "shell", r=150, rot=R_)
    # blue edge line round the lid split
    ring_pts = [[x, Yc + 333, z] for x, z in offset(rr(xa, zb, xb, zf, 230, n=10), 4)]
    d.tube("cap-seam", ring_pts + [ring_pts[0]], 16, "blue", bend=20, rot=R_, soft=True)
    # head well at the top end, long chrome handle on the lid front, stickers + logo label on the lid top
    d.sphere("head-well", [xa + 150, Yc + t - 10, Dp / 2], None, "gloss#e9edf1", radii=[120, 22, 230], rot=R_)
    d.tube("handle", [[xa + 330, Yc + 470, zf - 40], [xa + 340, Yc + 470, zf + 30], [xa + 760, Yc + 470, zf + 30],
                      [xa + 770, Yc + 470, zf - 40]], 26, "chrome", bend=30, rot=R_)
    yt = Yc + t + 0.5
    d.box("sticker1", [xa + 520, yt - 2, 200, xa + 700, yt + 1.5, 420], "gloss#5f9a52", r=10, rot=R_, soft=True)
    d.box("sticker2", [xa + 950, yt - 2, 180, xa + 1260, yt + 1.5, 380], "gloss#6aa35c", r=10, rot=R_, soft=True)
    d.lathe("label", [xa + 820, yt - 2, 300], [[0, 0], [95, 0], [95, 4], [0, 4]], "gloss#d9e7f6", rot=R_, soft=True)
    d.lathe("label-b", [xa + 820, yt + 1, 300], [[0, 0], [30, 0], [30, 2], [0, 2]], BLUE, rot=R_, soft=True)
    # pedestal: trapezoid box with a small control panel, gas struts to the capsule
    pz0, pz1 = 200, 660
    d.slab("ped", "front", rp([(Xc - 480, 60), (Xc + 30, 60), (Xc + 30, 690), (Xc - 210, 690)], [10, 10, 20, 30]),
           [pz0, pz1], "shell", r=25)
    px0 = Xc - 230
    d.box("ped-panel", [px0, 230, pz1 - 2, px0 + 140, 500, pz1 + 4], "gloss#f2f4f6", r=8)
    d.box("ped-spk", [px0 + 20, 440, pz1 + 3, px0 + 50, 470, pz1 + 5], "plastic#c3c8ce", r=4, copies=[[70, 0, 0]])
    btn(d, "ped-g", [px0 + 40, 380, pz1 + 4], 22, "front", "green", h=6)
    btn(d, "ped-y", [px0 + 100, 380, pz1 + 4], 22, "front", "gloss#e2b330", h=6)
    d.box("ped-sw", [px0 + 55, 280, pz1 + 3, px0 + 85, 330, pz1 + 12], "dark", r=3)
    for k, z in enumerate((330, 530)):
        d.bar(f"strut{k}", [Xc - 150, 680, z], [Xc - 130, Yc + 140, z], [60, 30], "shell", r=8)
        d.cyl(f"strut-rod{k}", [Xc - 40, 680, z], [Xc - 30, Yc + 40, z], 22, "chrome")
    # base plate with the raised oval foot tray at the right
    d.slab("plate", "top", rp([(X0 - 20, 140), (X0 + 1080, 140), (X0 + 1400, 420), (X0 + 1080, 700), (X0 - 20, 700)],
                               [30, 260, 260, 260, 30]), [0, 60], "shell", r=20)
    tray = ell(X0 + 1160, 420, 230, 260, n=48)
    d.slab("tray-rim", "top", ring(tray, offset(tray, -45)), [55, 130], "shell", r=18)
    d.slab("tray-in", "top", P(offset(tray, -40)), [55, 70], "gloss#f2ebe9")
    return d


# ------------------------------------------------------------------ HYZ-IIIE
def trolley_iiie(d, x0, z0):
    x1, z1 = x0 + 450, z0 + 450
    rbox(d, "tr-base", [x0, 80, z0, x1, 380, z1], 30, 18, "plastic#3d4146")
    rbox(d, "tr-dark", [x1 - 130, 370, z0, x1, 650, z0 + 260], 30, 18, "plastic#3d4146")
    rbox(d, "tr-mid", [x0, 376, z0 + 10, x1 - 125, 770, z1], 24, 14, "shell")
    rbox(d, "tr-mid2", [x1 - 140, 640, z0 + 10, x1, 770, z1], 24, 14, "shell")
    # bottle window with a clear bottle and a flowmeter
    d.box("tr-win", [x0 + 70, 470, z1 - 6, x0 + 210, 700, z1 + 1], "plastic#dfe3e8", r=8)
    d.cyl("tr-bottle", [x0 + 140, 490, z1 - 50], [x0 + 140, 640, z1 - 50], 90, "acrylic#e8f0f4c0")
    d.cyl("tr-cap", [x0 + 140, 640, z1 - 50], [x0 + 140, 670, z1 - 50], 50, "dark")
    d.box("tr-flow", [x0 + 238, 520, z1 - 4, x0 + 262, 680, z1 + 6], "acrylic#bfe3f6d0", r=5)
    logo(d, "tr-logo", [x0 + 80, 420, z1 + 1], 50, "front")
    # top box overhanging at the front with the sloped LCD
    d.slab("tr-top", "side", rp([(z0, 770), (z1 + 40, 770), (z1 + 40, 900), (z0, 1000)], [0, 6, 14, 14]),
           [x0 - 10, x1 + 10], "shell", r=16)
    ang = math.degrees(math.atan2(100, z1 + 40 - z0))
    tr = rot("x", ang, [0, 1000, z0])
    d.box("tr-frame", [x0 + 40, 998, z0 + 50, x1 - 40, 1002, z1 + 10], "gloss#3d72d8", r=6, rot=tr)
    d.box("tr-lcd", [x0 + 52, 1001, z0 + 62, x1 - 52, 1004, z1 - 2], "gloss#c9dcef", r=4, rot=tr)
    casters(d, "tr-castor", [(x0 + 55, z0 + 55), (x1 - 55, z0 + 55), (x0 + 55, z1 - 55), (x1 - 55, z1 - 55)], 60)


def hyz_iiie():
    Dp = 850
    X0 = 560
    d = Design("hyz-iiie", [2100, Dp, 1800], dict(MATS))
    trolley_iiie(d, 0, 200)
    # review (2026-10-03): the photos show the cabin's head end as a near-vertical rounded back rising into a hood, the
    # lid's top sloping ~33 deg down to a round foot end, the underside rising from the foot to the pedestal neck —
    # drawn as one side-profile slab (measured on the photo, 1.76 mm/px) instead of a tilted box
    zf, zb = Dp - 25, 25
    prof = ("M 560 760 L 560 1600 Q 560 1798 760 1798 L 1010 1790 Q 1075 1770 1110 1690 L 1722 1285 L 1960 960 "
            "Q 2075 800 2050 660 Q 2020 520 1862 440 L 1493 360 Q 1250 420 1040 640 Q 820 760 560 760 Z")
    d.slab("cap", "front", prof, [zb, zf], "shell", r=160)
    # lid outline: blue line with a stainless strip, from over the top behind the hood down the side, then to the foot
    def lid_line(z, dz):
        return [[880, 1795, z - dz * 200], [870, 1720, z], [830, 1560, z], [1600, 560, z], [1800, 600, z], [1965, 650, z]]
    for k, (zz, dz) in enumerate(((zf + 3, 1), (zb - 3, -1))):
        d.tube(f"lid-line{k}", lid_line(zz, dz), 16, "blue", bend=110, soft=True)
        d.tube(f"lid-strip{k}", [[p[0] + 14, p[1] - 12, p[2]] for p in lid_line(zz, dz)][1:], 8, "steel", bend=110, soft=True)
    d.tube("lid-line-top", [[880, 1795, zf - 200], [880, 1801, Dp / 2], [880, 1795, zb + 200]], 16, "blue", bend=300, soft=True)
    # blue window on the sloping top near the head; handle pocket with a stainless bar along the slope
    wx = 1290; wy = 1690 - (wx - 1110) * 0.657
    d.box("window", [wx - 170, wy - 10, 220, wx + 170, wy + 8, 630], "acrylic#5a86e0c8", r=60, rot=rot("z", -33, [wx, wy, 0]))
    hx, hy = 1265, 1110
    hr = rot("z", -55, [hx, hy, 0])
    d.box("pocket", [hx - 170, hy - 55, zf - 40, hx + 170, hy + 55, zf + 8], "shell", r=28, rot=hr)
    d.box("pocket-in", [hx - 150, hy - 40, zf - 30, hx + 150, hy + 40, zf + 10], "gloss#e6e9ec", r=20, rot=hr)
    d.cyl("pocket-bar", [hx - 135, hy, zf + 6], [hx + 135, hy, zf + 6], 20, "chrome", rot=hr)
    px, py = 1000, 700                         # pivot (grey stub under the cabin's underside)
    # pedestal: big round housing at the pivot, grey stub, grey step at the left, low foot platform to the right
    rr_ = 270
    dcx, dcy = 990, 380                        # round housing centre as on the photo
    d.loft("disc", [{"at": 120, "w": 2 * rr_ - 40, "d": 2 * rr_ - 40, "r": rr_ - 20, "cx": dcx, "cz": dcy},
                    {"at": 150, "w": 2 * rr_, "d": 2 * rr_, "r": rr_, "cx": dcx, "cz": dcy},
                    {"at": 700, "w": 2 * rr_, "d": 2 * rr_, "r": rr_, "cx": dcx, "cz": dcy},
                    {"at": 730, "w": 2 * rr_ - 40, "d": 2 * rr_ - 40, "r": rr_ - 20, "cx": dcx, "cz": dcy}], "shell", axis="z")
    d.lathe("disc-cover", [dcx, dcy, 728], [[0, 0], [rr_ - 45, 0], [rr_ - 45, 4], [0, 4]], "gloss#f2f4f6", axis="z")
    d.decal("disc-emb-v", [dcx + 5, dcy + 60, 733], [24, 100], "front", "plastic#dde1e6", soft=True)
    d.decal("disc-emb-h", [dcx - 10, dcy + 105, 733], [100, 20], "front", "plastic#dde1e6", soft=True)
    text3(d, "disc-cn", "翔宇医疗", [dcx - 130, dcy - 60, 733], 60, "plastic#d5d9df", gap=0.2, stroke=9)
    for k, a in enumerate((45, 135, 225, 315)):
        disc(d, f"screw{k}", [dcx + (rr_ - 70) * math.cos(math.radians(a)), dcy + (rr_ - 70) * math.sin(math.radians(a)), 733],
             5, "front", "plastic#555a62")
    d.box("stub", [px - 40, dcy + rr_ - 30, 340, px + 40, py + 20, 510], "plastic#b9bec5", r=10)
    disc(d, "stub-bolt", [px, py - 40, 510], 16, "front", "plastic#555a62", t=6)
    d.box("stub2", [px + 220, dcy + 120, 340, px + 280, py - 120, 510], "plastic#b9bec5", r=10)
    # C body: from the housing down to the long platform
    xe = X0 + 1520
    d.slab("ramp", "front", f"M {dcx} 60 L {xe} 60 L {xe} 180 L {dcx + 520} 180 Q {dcx + 330} 190 {dcx + 230} {dcy} Z",
           [130, 720], "shell", r=30)
    d.slab("platform", "top", rp([(dcx - 200, 120), (xe, 120), (xe, 730), (dcx - 200, 730)], [20, 120, 120, 20]),
           [0, 180], "shell", r=30)
    d.slab("tray", "top", rrp(xe - 400, 210, xe - 40, 640, 80), [176, 184], "gloss#f3e1dc")
    d.slab("tray-rim", "top", rrp(xe - 420, 190, xe - 20, 660, 90) + " " + rrp(xe - 400, 210, xe - 40, 640, 80),
           [176, 196], "shell", r=6)
    rbox(d, "step", [dcx - 430, 0, 150, dcx - 230, 140, 700], 40, 20, "plastic#9097a0")
    return d


if __name__ == "__main__":
    fns = {"hyz-iiid": hyz_iiid, "hyz-iiib": hyz_iiib, "hyz-iiie": hyz_iiie}
    for i in (sys.argv[1:] or list(fns)):
        go(fns[i]())
