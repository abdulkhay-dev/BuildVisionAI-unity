"""Fumigation units HYZ-IB (two perforated heads), HYZ-IC (single funnel head), HYZ-IID (3 places), HYZ-IIE (2 places)."""
import sys
from h3lib import *
Design = D

MATS = {"shell": "gloss#f6f7f8", "grey": "plastic#eef0f3", "blue": "gloss#3a6fe0", "dark": "plastic#2e3238",
        "steel": "metal#c9ccd0", "green": "gloss#2fb24a", "curtain": "plastic#7468f0", "lilac": "gloss#8a8fe0"}


# ------------------------------------------------------------------ HYZ-IB
def perf_head(d, id, rear, yaw):
    """Half-open perforated tube head: axis along +z from the rear end `rear`, turned by yaw (deg about y)."""
    x, y, z = rear
    R, L = 86, 340
    rr_ = rot("y", yaw, [x, y, z])
    sz = lambda at, rad: {"at": at, "w": 2 * rad, "d": 2 * rad, "r": rad, "cx": x, "cz": y}
    # review: an open tube (wall 6 mm, rounded closed rear), so the hollow shows at the front as in the photo
    d.lathe(id, [x, y, z], [[0, 0], [R - 24, 0], [R - 6, 6], [R, 22], [R, L], [R - 6, L], [R - 6, 20], [R - 26, 10], [0, 10]],
            "shell", axis="z", rot=rr_)
    d.lathe(id + "-in", [x, y, z + 11], [[0, 0], [R - 8, 0], [R - 8, 1], [0, 1]], "plastic#c9d0d8", axis="z", rot=rr_, soft=True)
    th = math.radians(yaw)
    n = 0
    for a in (0, 38, -38, 72, -72):
        for t in range(6):
            dx, dy, dz = (R - 2) * math.sin(math.radians(a)), (R - 2) * math.cos(math.radians(a)), 50 + 46 * t
            px, pz = x + dx * math.cos(th) + dz * math.sin(th), z - dx * math.sin(th) + dz * math.cos(th)
            c = [px, y + dy, pz]
            d.box(f"{id}-slot{n}", [c[0] - 4, c[1] - 3, c[2] - 11, c[0] + 4, c[1] + 3, c[2] + 11], "plastic#5f656d",
                  r=2, soft=True, rot=rot("y", yaw, c), rots=[rot("z", -a, c)] if False else None)
            n += 1


def hyz_ib():
    W, Dp, H = 600, 550, 1600
    d = Design("hyz-ib", [W, Dp, H], dict(MATS))
    # base plate on castors
    # review: the photo's base is a U — two front legs with the castors, the front edge between them set back
    d.slab("base", "top", rp([(20, 0), (580, 0), (580, 550), (455, 550), (440, 498), (160, 498), (145, 550), (20, 550)],
                             [40, 40, 50, 16, 30, 30, 16, 50]), [100, 160], "shell", r=16)
    casters(d, "castor", [(70, 60), (530, 60), (70, 490), (530, 490)], 75)
    # cabinet: lower body, upper handle section, console; blue bands
    x0, x1, z0, z1 = 75, 525, 100, 500
    d.box("body", [x0, 160, z0, x1, 640, z1], "grey", r=10)
    d.box("upper", [x0, 655, z0, x1, 828, z1], "grey", r=8)
    d.box("band-b", [x0 - 2, 160, z1 - 4, x1 + 2, 186, z1 + 2], "blue", r=3)
    d.box("band-m", [x0 - 3, 638, z0 - 3, x1 + 3, 657, z1 + 3], "blue", r=4)
    d.box("band-t", [x0 - 3, 826, z0 - 3, x1 + 3, 844, z1 + 3], "blue", r=4)
    d.slab("band-d", "side", P([(z1, 165), (z1, 205), (z0 + 60, 640), (z0 + 22, 640)]), [x1, x1 + 2], "blue", soft=True)
    d.slab("band-dl", "side", P([(z1, 165), (z1, 205), (z0 + 60, 640), (z0 + 22, 640)]), [x0 - 2, x0], "blue", soft=True)
    d.slab("console", "side", rp([(z0, 842), (z1 + 6, 842), (z1 + 6, 880), (z0, 930)], [0, 0, 10, 10]), [x0, x1], "grey", r=8)
    ang = math.degrees(math.atan2(50, z1 + 6 - z0))
    tr = rot("x", ang, [0, 930, z0])
    d.box("con-panel", [x0 + 18, 928, z0 + 20, x1 - 18, 931, z1 - 14], "gloss#f2f5f9", r=6, rot=tr)
    d.box("con-screen", [x0 + 140, 930, z0 + 110, x1 - 140, 932, z1 - 70], "gloss#9fd0f0", r=4, rot=tr)
    d.box("con-lines", [x0 + 40, 930.5, z0 + 120, x0 + 120, 932, z0 + 126], "plastic#9aa6b4", soft=True, rot=tr,
          copies=[[0, 0, 60], [260, 0, 0], [260, 0, 60]])
    # printed LEFT / RIGHT on the sloping panel (drawn flat, then tilted with it)
    turned(d, lambda: (text3(d, "con-l", "LEFT", [x0 + 40, 932, z0 + 210], 20, "plastic#7d8a99", u=(1, 0, 0), v=(0, 0, -1), face="top"),
                       text3(d, "con-r", "RIGHT", [x1 - 125, 932, z0 + 210], 20, "plastic#7d8a99", u=(1, 0, 0), v=(0, 0, -1), face="top")), tr)
    d.box("con-slot", [x0 + 175, 852, z1 + 4, x1 - 175, 866, z1 + 9], "dark", r=3)
    # chrome grab bar
    d.tube("bar", [[x0 + 40, 740, z1], [x0 + 40, 740, z1 + 48], [x1 - 40, 740, z1 + 48], [x1 - 40, 740, z1]], 30,
           "metal#b9bdc3", bend=26)
    d.lathe("bar-mount", [x0 + 40, 740, z1], [[0, 0], [32, 0], [32, 8], [24, 14], [0, 14]], "grey", axis="z",
            copies=[[x1 - x0 - 80, 0, 0]])
    logo(d, "logo", [x0 + 105, 420, z1], 88, "front", blue="gloss#1f3f96")   # the photo's logo is dark navy
    # vent dots on the right side
    d.box("vent", [x1, 340, z1 - 110, x1 + 1.5, 344, z1 - 106], "plastic#9aa1aa", soft=True,
          repeat=rep(10, [0, 14, 0]), copies=[[0, 40, 14 * k] for k in range(1, 5)] + [[0, -110, -230 + 14 * k] for k in range(0, 5)])
    # arms
    # review: both heads point straight forward (their open ends at the front), the right arm column stands at the back
    # third of the right side, the left arm rises from behind the console near the left edge
    xr, zr = x1 + 27, 180
    d.cyl("arm-r", [xr, 280, zr], [xr, 900, zr], 44, "shell")
    d.box("joint-r1", [xr - 26, 300, zr - 32, xr + 26, 370, zr + 32], "shell", r=20)
    d.lathe("joint-r2", [xr - 32, 905, zr], [[0, 0], [50, 0], [50, 64], [0, 64]], "shell", axis="x")
    disc(d, "joint-r2c", [xr + 32, 905, zr], 14, "right", "plastic#9aa1aa")
    d.cyl("arm-r2", [xr, 905, zr], [xr - 10, 1440, zr], 42, "shell")
    perf_head(d, "head-r", [xr - 5, 1490, zr - 70], 0)
    d.cyl("arm-l", [140, 880, z0 + 50], [95, 1400, z0 + 60], 42, "shell")
    d.sphere("arm-l-j", [95, 1405, z0 + 60], 52, "shell")
    perf_head(d, "head-l", [95, 1480, z0 + 10], 0)
    return d


# ------------------------------------------------------------------ HYZ-IC
def hyz_ic():
    W, Dp, H = 550, 450, 1250
    d = Design("hyz-ic", [W, Dp, H], dict(MATS))
    casters(d, "castor", [(70, 70), (480, 70), (70, 380), (480, 380)], 60, "rubber#8c9196")
    cx, cz = 275, 225
    d.loft("base", [sec(84, 540, 440, 130, cx, cz), sec(150, 530, 430, 125, cx, cz), sec(196, 440, 350, 110, cx, cz - 10)],
           "shell", dome="end", domeH=18)
    # review: the photo's column is waisted with a concave front and flares forward/outward into the tray; a low round
    # platform rings its foot on the base
    d.lathe("plinth", [cx, 196, 200], [[0, 0], [205, 0], [205, 10], [190, 18], [0, 18]], "shell")
    d.loft("column", [sec(205, 205, 170, 70, cx, 178), sec(330, 190, 160, 66, cx, 180), sec(430, 192, 165, 66, cx, 186),
                      sec(540, 220, 195, 76, cx, 200), sec(610, 270, 245, 90, cx, 214), sec(650, 320, 290, 100, cx, 222)],
           "shell")
    # small diamond logo label on the column front
    d.decal("col-logo", [cx, 430, 274], [52, 52], "front", "gloss#bcd8f0", rot=rot("z", 45, [cx, 430, 274]),
            rots=[rot("x", 15, [cx, 430, 268.5])])
    d.decal("col-logo-in", [cx, 432, 275], [22, 22], "front", "gloss#3a7fd0", rot=rot("z", 45, [cx, 432, 275]),
            rots=[rot("x", 15, [cx, 430, 268.5])])
    # wavy tray with a dark band under its edge
    tray = (f"M 25 25 L 525 25 Q 548 25 548 50 L 548 395 Q 548 432 515 432 Q 420 400 {cx} 402 Q 130 400 35 432 "
            f"Q 2 432 2 395 L 2 50 Q 2 25 25 25 Z")
    d.slab("tray-band", "top", tray, [640, 668], "plastic#3c4049", r=6)
    d.slab("tray", "top", tray, [664, 690], "shell", r=8)
    # box unit with a chamfered front top carrying the control panel
    bx0, bx1, bz0, bz1, by0, by1 = 60, 490, 60, 400, 690, 850
    d.slab("unit", "side", rp([(bz0, by0), (bz1, by0), (bz1, by1 - 45), (bz1 - 45, by1), (bz0, by1)], [4, 6, 10, 10, 10]),
           [bx0, bx1], "shell", r=10)
    ang = math.degrees(math.atan2(45, 45))
    tr = rot("x", ang, [0, by1, bz1 - 45])
    L = 45 * math.sqrt(2)
    d.box("panel", [230, by1 - 1, bz1 - 45 + 3, 465, by1 + 1.5, bz1 - 45 + L - 3], "plastic#dfe2e6", r=4, rot=tr)
    d.box("lcd", [260, by1 + 1, bz1 - 45 + 8, 340, by1 + 2.5, bz1 - 45 + 28], "plastic#3b4048", r=2, rot=tr)
    d.box("keys", [260, by1 + 1, bz1 - 45 + 38, 274, by1 + 3, bz1 - 45 + 50], "plastic#4b5058", r=2, rot=tr,
          repeat={"n": 5, "step": [20, 0, 0]})
    d.lathe("gbtn-ring", [430, by1 + 1, bz1 - 22], [[0, 0], [30, 0], [30, 8], [0, 8]], "gloss#fbfbfb", rot=tr)
    d.lathe("gbtn", [430, by1 + 8, bz1 - 22], [[0, 0], [22, 0], [22, 5], [14, 9], [0, 9]], "gloss#3cc35a", rot=tr)
    d.box("label", [95, 770, bz1, 175, 795, bz1 + 2], "gloss#2a5fb8", r=2)
    text3(d, "label-t", "XYVL", [104, 776, bz1 + 2.5], 13, "gloss#ffffff", gap=0.3)
    d.box("label2", [95, 742, bz1, 215, 748, bz1 + 1.5], "plastic#9aa6b4", soft=True)
    # fan grille + vents on the left side
    d.box("fan", [bx0 - 3, 720, 230, bx0 + 1, 800, 310], "plastic#c9cdd2", r=6)
    disc(d, "fan-g", [bx0 - 3, 760, 270], 34, "left", "plastic#7a8088")
    d.box("vent", [bx0 - 1.5, 790, 120, bx0, 795, 190], "plastic#9aa1aa", soft=True, repeat=rep(5, [0, -14, 0]))
    # pole, knob, knuckle joint, short arm, funnel head pointing down-left
    px, pz = 180, 120
    d.cyl("pole", [px, by1, pz], [px, 1100, pz], 38, "shell")
    d.cyl("knob", [px, 1000, pz], [px - 45, 1000, pz], 14, "shell")
    d.sphere("knob-b", [px - 48, 1000, pz], 24, "shell")
    jy = 1110
    d.lathe("joint", [px, jy, pz - 30], [[0, 0], [34, 0], [34, 60], [0, 60]], "shell", axis="z")
    disc(d, "joint-c", [px, jy, pz + 30], 15, "front", "plastic#9aa1aa")
    mx, my = 58, 1113                                  # mouth centre; the head's axis points up-right at 50 deg
    hr = rot("z", -50, [mx, my, pz])
    tx, ty = mx + 125 * math.sin(math.radians(50)), my + 125 * math.cos(math.radians(50))
    d.cyl("arm", [px, jy, pz], [tx + 5, ty + 3, pz], 32, "shell")
    d.loft("head", [sec(my, 165, 140, 48, mx, pz), sec(my + 95, 125, 110, 42, mx, pz), sec(my + 125, 80, 76, 32, mx, pz)],
           "shell", dome="end", domeH=18, rot=hr)
    d.box("head-mouth", [mx - 76, my - 1.5, pz - 64, mx + 76, my + 0.5, pz + 64], "plastic#b8bec6", r=40, rot=hr)
    return d


# ------------------------------------------------------------------ HYZ-IID
def rtri(C, Ri, rcs, n=32):
    """Rounded triangle (x, z) points: vertex directions 0/120/240 deg from +z towards +x; rcs = radius per vertex."""
    pts = []
    for i, a in enumerate((0, 120, 240)):
        rc = rcs[i]
        vx = C[0] + (Ri - 0) * math.sin(math.radians(a)); vz = C[1] + Ri * math.cos(math.radians(a))
        # pull the arc centre in so that the arc is tangent to the edges of the triangle of circumradius Ri + 2rc*...
        for k in range(n + 1):
            ph = math.radians(a - 60 + 120 * k / n)
            pts.append((vx + rc * math.sin(ph), vz + rc * math.cos(ph)))
    return pts


def hyz_iid():
    # review (2026-10-03): the photo's front lobe is a wide round bulge (chord ~1.5x a place's face), the places are
    # recessed bays with the curtain tucked behind the lobe edges, and the top ring is nearly round. Plan rebuilt:
    # body lobes r 446 about vertices at 294, places recessed 70; ring a rounded triangle with short flats (r 545 / 200).
    Rb, rcb = 294, 446                           # body: vertex distance, lobe radius
    Rr, rcr = 200, 545                           # ring
    apo = Rr / 2 + rcr                           # centre to the ring's flats (back face at z = 0)
    apo_b = Rb / 2 + rcb                         # centre to the body's place faces (before the recess)
    rec = 70
    W = round(2 * (Rr * math.sin(math.radians(120)) + rcr)) + 4
    C = (W / 2, apo)
    Dp, H = round(apo + Rr + rcr) + 4, 1200
    d = Design("hyz-iid", [W, Dp, H], dict(MATS, curtain="gloss#6457e6"))
    yt0, yt1 = 960, 1110
    top = rtri(C, Rr, [rcr] * 3)
    d.slab("ring", "top", P(top), [yt0, yt1], "shell", r=45)
    # body outline: the three lobe arcs, a recessed bay between each two
    arcs = []
    for a in (0, 120, 240):
        vx, vz = C[0] + Rb * math.sin(math.radians(a)), C[1] + Rb * math.cos(math.radians(a))
        arcs.append([(vx + rcb * math.sin(math.radians(a - 60 + 120 * k / 32)), vz + rcb * math.cos(math.radians(a - 60 + 120 * k / 32)))
                     for k in range(33)])
    arcs = [ar[1:-1] for ar in arcs]                  # one segment in from the tangent points: a small lip
    body = []
    for i, a in enumerate((0, 120, 240)):
        body += arcs[i]
        E, S = arcs[i][-1], arcs[(i + 1) % 3][0]
        nx, nz = math.sin(math.radians(a + 60)), math.cos(math.radians(a + 60))
        body += [(E[0] - rec * nx, E[1] - rec * nz), (S[0] - rec * nx, S[1] - rec * nz)]
    d.slab("body", "top", P(body), [95, yt0 + 2], "shell", r=20)
    # stations at the places (normal angles 60 / 180 / 300)
    hw = Rb * math.sqrt(3) / 2 - 12                  # half width of a bay
    for k, phi in enumerate((60, 180, 300)):
        R_ = rot("y", phi, [C[0], 0, C[1]])
        zf = C[1] + apo_b - rec                      # bay back face
        d.box(f"bay{k}", [C[0] - hw, 95, zf - 30, C[0] + hw, yt0, zf - 12], "plastic#2c2766", r=4, rot=R_)
        folds = []
        for i in range(41):
            t = i / 40
            folds.append((C[0] - hw + 2 * hw * t, zf + 14 + 8 * math.sin(t * math.pi * 9)))
        back = [(x, z - 10) for x, z in reversed(folds)]
        d.slab(f"curtain{k}", "top", P(folds + back), [100, yt0 - 4], "curtain", r=3, rot=R_)
        for j, xz in enumerate((C[0] - hw + 4, C[0] + hw - 4)):
            d.box(f"zip{k}{j}", [xz - 3, 110, zf + 4, xz + 3, yt0 - 10, zf + 24], "plastic#26215e", soft=True, rot=R_)
        # two arm holes on the ring's outer face
        zr = C[1] + apo
        for j, dx in enumerate((-150, 150)):
            d.lathe(f"hole{k}{j}", [C[0] + dx, 1035, zr - 2], [[0, 0], [70, 0], [70, 7], [0, 7]], "fabric#4a3fc4",
                    axis="z", rot=R_, soft=True)
            d.lathe(f"hole{k}{j}i", [C[0] + dx, 1035, zr + 4], [[0, 0], [50, 0], [50, 2], [0, 2]], "fabric#2a2378",
                    axis="z", rot=R_, soft=True)
    # pod with a sloped LCD panel facing outwards
        pz0, pz1 = C[1] + apo - 330, C[1] + apo - 70
        # review: in the photo the pods are joined to the central hub by raised ridges (a three-armed top)
        d.box(f"ridge{k}", [C[0] - 120, yt1 - 5, C[1] + 120, C[0] + 120, yt1 + 95, pz0 + 40], "shell", r=45, rot=R_)
        d.slab(f"pod{k}", "side", rp([(pz0, yt1 - 5), (pz1, yt1 - 5), (pz1 - 60, yt1 + 140), (pz0, yt1 + 140)], [0, 0, 30, 30]),
               [C[0] - 190, C[0] + 190], "shell", r=30, rot=R_)
        ang = math.degrees(math.atan2(145, 60))
        tp = rot("x", -(90 - ang), [0, yt1 - 5, pz1])
        d.box(f"lcd{k}", [C[0] - 120, yt1 + 5, pz1 - 4, C[0] + 120, yt1 + 125, pz1 + 2], "plastic#d7dce4", r=6,
              rot=tp, rots=[R_])
        d.box(f"lcd{k}s", [C[0] - 85, yt1 + 55, pz1 + 1, C[0] + 85, yt1 + 115, pz1 + 3.5], "plastic#aab4c4", r=3,
              rot=tp, rots=[R_])
        d.box(f"lcd{k}k", [C[0] - 85, yt1 + 22, pz1 + 1, C[0] - 67, yt1 + 38, pz1 + 4], "plastic#4b5468", r=2,
              rot=tp, rots=[R_], repeat={"n": 6, "step": [34, 0, 0]})
    # centre hub with a top disc; the well with the chrome lid at its front
    d.lathe("hub", [C[0], yt1 - 5, C[1]], [[0, 0], [330, 0], [320, 50], [250, 100], [160, 125], [0, 125]], "shell")
    d.lathe("hub-top", [C[0], yt1 + 118, C[1]], [[0, 0], [150, 0], [150, 8], [0, 8]], "gloss#e9edf2")
    d.box("hub-panel", [C[0] - 60, yt1 + 125, C[1] - 40, C[0] + 60, yt1 + 128, C[1] + 40], "plastic#c7ced8", r=6)
    btn(d, "hub-btn", [C[0] - 90, yt1 + 126, C[1] + 20], 16, "top", "green", h=5)
    wz = C[1] + 330
    d.lathe("well-rim", [C[0], yt1 - 4, wz], [[150, 0], [205, 0], [200, 30], [175, 36], [150, 20]], "shell")
    d.lathe("well", [C[0], yt1 - 2, wz], [[0, 0], [155, 0], [155, 3], [0, 3]], "plastic#c3c8ce")
    d.lathe("lid", [C[0], yt1 + 1, wz], [[0, 0], [120, 0], [120, 14], [95, 22], [0, 24]], "chrome")
    d.cyl("knob-s", [C[0], yt1 + 24, wz], [C[0], yt1 + 70, wz], 16, "chrome")
    d.box("knob", [C[0] - 50, yt1 + 66, wz - 10, C[0] + 50, yt1 + 82, wz + 10], "black", r=6)
    d.box("knob2", [C[0] - 10, yt1 + 66, wz - 50, C[0] + 10, yt1 + 82, wz + 50], "black", r=6)
    # front lobe: logo projected on the curved surface, drain valve, feet
    zc = C[1] + Rb                                  # front arc centre z
    rlob = rcb
    def surf(p):
        dx = p[0] - C[0]
        return [p[0], p[1], zc + math.sqrt(max(rlob * rlob - dx * dx, 0)) + 4.5]
    zfront = zc + rlob
    # review: the photo's logo is big (badge ~150) and centred on the lobe
    disc(d, "logo-badge", [C[0] - 200, 610, zfront - 30], 72, "front", BLUE, t=32)
    d.decal("logo-v", [C[0] - 195, 602, zfront + 3], [22, 88], "front", "gloss#ffffff", soft=True)
    d.decal("logo-h", [C[0] - 203, 632, zfront + 3], [100, 20], "front", "gloss#ffffff", soft=True)
    text3(d, "logo-cn", "翔宇医疗", [C[0] - 110, 598, 0], 74, BLUE, gap=0.2, surf=surf)
    text3(d, "logo-en", "XIANGYU MEDICAL", [C[0] - 110, 552, 0], 22, BLUE, gap=0.3, surf=surf)
    d.cyl("drain", [C[0], 230, zfront - 10], [C[0], 230, zfront + 40], 30, "metal#c9a456")
    d.cyl("drain-h", [C[0] - 22, 230, zfront + 28], [C[0] + 22, 230, zfront + 28], 18, "metal#c9a456")
    for i, a in enumerate((0, 120, 240)):
        for s_ in (-28, 28):
            ph = math.radians(a + s_)
            r_ = Rb + rcb - 170
            d.cyl(f"foot{i}{s_ > 0}", [C[0] + r_ * math.sin(ph), 0, C[1] + r_ * math.cos(ph)],
                  [C[0] + r_ * math.sin(ph), 96, C[1] + r_ * math.cos(ph)], 60, "black")
    return d


# ------------------------------------------------------------------ HYZ-IIE
def hyz_iie():
    W, Dp, H = 1300, 1000, 1300
    d = Design("hyz-iie", [W, Dp, H], dict(MATS))
    sx0, sx1 = 470, 830
    # lilac spine with a well cut in its top front, two cheeks round the well
    d.slab("spine", "side", rp([(0, 40), (Dp, 40), (Dp, 1040), (760, 1040), (760, 1300), (0, 1300)], [0, 0, 6, 6, 60, 120]),
           [sx0, sx1], "lilac", r=18)
    d.slab("cheek", "side", rp([(700, 1040), (Dp, 1040), (Dp, 1200), (880, 1300), (700, 1300)], [0, 0, 60, 60, 0]),
           [sx0, sx0 + 42], "lilac", r=14, copies=[[sx1 - sx0 - 42, 0, 0]])
    d.box("well-back", [sx0 + 30, 1040, 740, sx1 - 30, 1290, 770], "shell", r=8)
    d.box("well-floor", [sx0 + 30, 1036, 760, sx1 - 30, 1044, Dp - 4], "shell", r=4)
    d.lathe("lid", [650, 1044, 880], [[0, 0], [100, 0], [100, 14], [80, 22], [0, 24]], "chrome")
    d.cyl("knob-s", [650, 1066, 880], [650, 1110, 880], 16, "chrome")
    d.box("knob", [600, 1104, 870, 700, 1120, 890], "black", r=6)
    # front of the spine: logo badge, vertical lettering, door, screws
    zf = Dp
    disc(d, "badge", [650, 880, zf], 62, "front", "gloss#ffffff")
    d.decal("badge-v", [655, 872, zf + 2.2], [18, 74], "front", "lilac", soft=True)
    d.decal("badge-h", [645, 900, zf + 2.2], [84, 16], "front", "lilac", soft=True)
    for i, ch in enumerate("翔宇医疗"):
        text3(d, f"vt{i}", ch, [604, 690 - i * 120, zf + 1.5], 95, "gloss#ffffff", gap=0.2)
    d.box("door", [560, 110, zf - 4, 740, 330, zf + 6], "gloss#9196e6", r=6)
    d.slab("door-line", "front", rrp(560, 110, 740, 330, 6) + " " + rrp(563, 113, 737, 327, 5), [zf + 6, zf + 7.5],
           "plastic#5d62b0", soft=True)
    d.tube("door-h", [[590, 185, zf + 6], [586, 220, zf + 22], [586, 260, zf + 22], [590, 295, zf + 6]], 10, "chrome", bend=10)
    disc(d, "screw", [500, 1000, zf], 6, "front", "plastic#555a66", copies=[[300, 0, 0], [0, -460, 0], [300, -460, 0],
                                                                           [0, -880, 0], [300, -880, 0]])
    # left lobe — review: the photo's left arm holes are foreshortened ellipses and the curtain sits on the lobe's LEFT
    # side face; the lobe's front is plain white. So the left place faces left (mirror of the right lobe)
    xa, xb = 0, sx0 + 20
    d.slab("l-low", "top", rrp(xa + 150, 0, xb, Dp, 140), [40, 1000], "shell", r=30)
    d.slab("l-wall", "top", rrp(xa, Dp - 170, xb - 100, Dp, 60), [40, 1000], "shell", r=30)
    d.slab("l-wall2", "top", rrp(xa, 0, xb - 100, 170, 60), [40, 1000], "shell", r=30)
    d.slab("l-up", "top", rrp(xa, 0, xb, Dp, 140), [810, 1000], "shell", r=40)
    d.slab("l-top", "top", rrp(xa + 40, 60, xb - 30, 640, 110), [990, 1150], "shell", r=45)
    for j, z in enumerate((380, 620)):
        d.lathe(f"lhole{j}", [-2, 905, z], [[0, 0], [70, 0], [70, 6], [0, 6]], "fabric#4a3fc4", axis="x", soft=True)
        d.lathe(f"lhole{j}i", [-3.5, 905, z], [[0, 0], [48, 0], [48, 2], [0, 2]], "fabric#2a2378", axis="x", soft=True)
    folds = [(170 + 660 * i / 50, 30 - 8 * math.sin(i / 50 * math.pi * 9)) for i in range(51)]
    d.slab("l-curtain", "top", P([(x, z) for z, x in folds] + [(x + 12, z) for z, x in reversed(folds)]), [60, 812],
           "curtain", r=3)
    d.box("l-zip", [16, 70, 166, 30, 805, 174], "plastic#26215e", soft=True, copies=[[0, 0, 660]])
    tl = rot("x", -12, [0, 1040, 646])
    d.box("l-lcd", [150, 1040, 634, 340, 1130, 646], "plastic#d7dce4", r=6, rot=tl)
    d.box("l-lcd-s", [175, 1075, 645, 315, 1122, 648], "plastic#aab4c4", r=3, rot=tl)
    d.box("l-lcd-k", [175, 1050, 645, 187, 1062, 649], "plastic#4b5468", r=2, rot=tl, repeat={"n": 6, "step": [24, 0, 0]})
    # right lobe (place facing the right side): plain white front, curtain + holes on the right face
    xa, xb = sx1 - 20, W
    d.slab("r-low", "top", rrp(xa, 0, xb - 150, Dp, 140), [40, 1000], "shell", r=30)
    d.slab("r-wall", "top", rrp(xa + 100, Dp - 170, xb, Dp, 60), [40, 1000], "shell", r=30)
    d.slab("r-wall2", "top", rrp(xa + 100, 0, xb, 170, 60), [40, 1000], "shell", r=30)
    d.slab("r-up", "top", rrp(xa, 0, xb, Dp, 140), [810, 1000], "shell", r=40)
    d.slab("r-top", "top", rrp(W - 330, 200, W - 40, 800, 110), [990, 1150], "shell", r=45)
    tr_ = rot("z", -12, [W - 46, 1040, 0])
    d.box("r-lcd", [W - 46, 1040, 405, W - 34, 1130, 595], "plastic#d7dce4", r=6, rot=tr_)
    for j, z in enumerate((380, 620)):
        d.lathe(f"rhole{j}", [W - 4, 905, z], [[0, 0], [70, 0], [70, 6], [0, 6]], "fabric#4a3fc4", axis="x", soft=True)
        d.lathe(f"rhole{j}i", [W + 1, 905, z], [[0, 0], [48, 0], [48, 2], [0, 2]], "fabric#2a2378", axis="x", soft=True)
    folds = [(170 + 660 * i / 50, W - 30 + 8 * math.sin(i / 50 * math.pi * 9)) for i in range(51)]
    d.slab("r-curtain", "top", P([(x, z) for z, x in folds] + [(x - 12, z) for z, x in reversed(folds)]), [60, 812],
           "curtain", r=3)
    d.cyl("foot", [60, 0, 60], [60, 40, 60], 40, "chrome", copies=[[0, 0, 860], [1180, 0, 0], [1180, 0, 860], [590, 0, 880]])
    return d


if __name__ == "__main__":
    fns = {"hyz-ib": hyz_ib, "hyz-ic": hyz_ic, "hyz-iid": hyz_iid, "hyz-iie": hyz_iie}
    for i in (sys.argv[1:] or list(fns)):
        go(fns[i]())
