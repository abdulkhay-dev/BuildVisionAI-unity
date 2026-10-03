"""YHZ-II (steel traction table with console) and YHZ-IV (cabinet traction table) — batch table-4.
python3 t4_yhz.py [yhz-ii] [yhz-iv]   writes only these ids."""
import sys, math
from t4lib import *

MATS = {"white": "plastic#f2f3f5", "seam": "plastic#a9adb4", "panel": "gloss#4d8db0", "dark": "plastic#2a2d32",
        "cap": "rubber#1f2124", "chrome": "chrome", "steel": "metal#b9bdc3", "logo": "gloss#2f78c8",
        "knee": "leather#232528", "strap": "fabric#8f8cab", "ctrl": "gloss#2a6fc0", "cable": "black#1c1d20"}


def console(d, x0, x1, z0, z1, H=950, yb=95, yh=610, yf=790, cast=75, front_castors=True):
    """Xiangyu traction console: lower cabinet (logo), wider head box with a vertical front, top sloping up to the back
    with the blue key panel, a dot vent grille at the front right."""
    d.box("con-cab", [x0 + 50, yb, z0 + 40, x1 - 5, yh, z1 - 25], "white", r=6)
    d.decal("con-door", [(x0 + 50 + x1) / 2 + 15, (yb + yh) / 2, z1 - 24.5], [3, yh - yb - 50], "front", "seam", soft=True,
            copies=[[-(x1 - x0) / 2 + 60, 0, 0]])
    d.decal("con-door-b", [(x0 + x1) / 2 + 40, yb + 22, z1 - 24.5], [x1 - x0 - 120, 3], "front", "seam", soft=True)
    brand(d, "con-logo", x0 + 140, 400, z1 - 25, 52)
    if front_castors:
        castor(d, "con-castor", x0 + 110, z0 + 90, cast, corners(x0 + 110, z0 + 90, x1 - 70, z1 - 80))
    else:   # only the back pair (the front of the console hangs on the beam's castor leg)
        castor(d, "con-castor", x0 + 110, z0 + 90, cast, [[x1 - x0 - 180, 0, 0]])
    # head box: profile in z/y (front face up to yf, slope up to the back to H)
    prof = [(z0, yh), (z1, yh), (z1, yf - 12), (z1 - 30, yf + 6), (z0 + 70, H - 8), (z0, H)]
    side_slab(d, "con-head", prof, x0, x1, "white", r=14)
    ang = math.degrees(math.atan2(H - 8 - (yf + 6), (z1 - 30) - (z0 + 70)))
    zc, yc = (z0 + z1) / 2 + 10, None
    t = ((z1 - 30) - zc) / ((z1 - 30) - (z0 + 70))
    yc = yf + 6 + t * (H - 8 - yf - 6)
    r_ = rot("x", ang, [0, yc, zc])
    d.box("con-panel", [x0 + 125, yc - 4, zc - 160, x1 - 50, yc + 3, zc + 140], "panel", r=3, rot=r_)
    d.box("con-sticker", [x0 + 20, yc - 4, zc - 70, x0 + 115, yc + 2, zc + 60], "plastic#dfe3e8", r=2, rot=r_)
    d.box("con-keys", [x0 + 175, yc + 2, zc - 40, x0 + 205, yc + 5, zc - 20], "plastic#e9edf2", r=2, soft=True, rot=r_,
          repeat=rep(6, [42, 0, 0]), copies=[[0, 0, 45], [0, 0, 90]])
    d.box("con-led", [x0 + 180, yc + 2, zc - 140, x0 + 330, yc + 4, zc - 80], "plastic#173a63", r=2, soft=True, rot=r_)
    d.box("con-led-r", [x0 + 345, yc + 2, zc - 140, x1 - 75, yc + 4, zc - 80], "plastic#173a63", r=2, soft=True, rot=r_)
    d.box("con-red", [x1 - 140, yc + 2, zc + 50, x1 - 112, yc + 5, zc + 75], "gloss#e3342f", r=2, soft=True, rot=r_)
    # vent grille: black dot rows at the lower right of the head front
    d.decal("con-vent", [x1 - 165, yh + 35, z1 + 0.6], [6, 6], "front", "dark", soft=True,
            repeat=rep(14, [9, 0, 0]), copies=[[0, 10, 0], [0, 20, 0], [0, 30, 0], [0, 40, 0]])


def bow_knee(d, xk, xe, ytop, zc, yp, half=150):
    """Upright thin black knee board facing -x hanging from the apex of a chrome bow: on each side an inclined tube
    from the end corner (xe) up to the apex and a short strut from the apex down to the tray behind the board (photo)."""
    ax, ay = xk + 95, ytop - 14
    r_ = rot("z", -8, [xk + 30, yp + 10, zc])
    d.box("knee", [xk, yp + 12, zc - 125, xk + 42, ay - 18, zc + 125], "knee", r=14, rot=r_)
    d.box("knee-plate", [xk + 42, yp + 60, zc - 80, xk + 54, ay - 40, zc + 80], "dark", r=4, rot=r_)
    for nm, zz in (("f", zc + half), ("b", zc - half)):
        d.tube(f"bow-{nm}", [[xe - 15, yp - 5, zz], [xe - 30, yp + 25, zz], [ax, ay, zz], [xk + 175, yp + 2, zz]], 26, "chrome", bend=45)
        d.box(f"bow-foot-{nm}", [xe - 38, yp - 12, zz - 20, xe + 2, yp + 12, zz + 20], "dark", r=4)
        d.box(f"bow-foot2-{nm}", [xk + 158, yp - 2, zz - 18, xk + 192, yp + 14, zz + 18], "dark", r=4)
    d.cyl("bow-x", [ax, ay, zc - half], [ax, ay, zc + half], 22, "chrome")


def harness(d, x0, x1, y, z0, z1, flap, web, edge="fabric#5a62a8", ext=150):
    """Traction harness: a thin periwinkle flap across the split, four transverse grey-blue straps (blue edging)
    standing up as loops at the back, two striped belts along the front reaching onto the next tray, chrome buckles."""
    m = (x0 + x1) / 2
    pts = [(x0 + 20, z0 + 15), (m, z0), (x1 - 20, z0 + 15), (x1, (z0 + z1) / 2), (x1 - 20, z1 - 15), (m, z1),
           (x0 + 20, z1 - 15), (x0 - 10, (z0 + z1) / 2)]
    d.add("harn-c", "slab", flap, plane="top", outline=poly_path(round_poly(pts, 40)), w=[y, y + 14], r=5)
    n = 4
    for k in range(n):
        xx = x0 + 50 + k * (x1 - x0 - 100) / (n - 1)
        path = [[xx, y + 16, z1 + 15], [xx, y + 16, z0 + 30], [xx + 6, y + 48, z0 + 5], [xx + 10, y + 64, z0 - 2]]
        d.strap(f"harn-t{k}", path, [46, 3], edge, bend=22, soft=True)
        d.strap(f"harn-t{k}g", [[q[0], q[1] + 1.5, q[2]] for q in path], [38, 3], web, bend=22, soft=True)
        d.box(f"harn-bk{k}", [xx - 20, y + 17, z0 + 70, xx + 20, y + 25, z0 + 100], "chrome", r=3, soft=True)
    for k, zz in enumerate((z1 - 90, z1 - 170)):
        path = [[x0 - 60, y + 16, zz], [x1 + ext, y + 16, zz]]
        d.strap(f"harn-l{k}", path, [56, 3], edge, soft=True)
        d.strap(f"harn-l{k}g", [[q[0], q[1] + 1.5, q[2]] for q in path], [40, 3], flap, soft=True)
        d.decal(f"harn-l{k}s", [x0 + 30, y + 21, zz], [40, 44], "top", web, soft=True, repeat=rep(6, [(x1 + ext - x0 - 30) / 6, 0, 0]))


def ctrl(d, x, y, z, cable_to):
    """Hand controller: white body, blue face with a row of white keys (one orange) and a scalloped top edge."""
    d.box("hand", [x, y, z - 32, x + 140, y + 26, z + 32], "white", r=10)
    d.decal("hand-face", [x + 70, y + 26.6, z], [126, 52], "top", "ctrl", soft=True)
    d.decal("hand-btn", [x + 30, y + 27.2, z - 8], [15, 15], "top", "plastic#f2f4f7", soft=True, repeat=rep(4, [26, 0, 0]))
    d.decal("hand-btn-o", [x + 82, y + 27.6, z - 8], [15, 15], "top", "gloss#e8742c", soft=True)
    d.decal("hand-txt", [x + 70, y + 27.2, z + 14], [100, 4], "top", "plastic#f2f4f7", soft=True)
    d.tube("hand-cable", [[x, y + 12, z]] + cable_to, 7, "cable", bend=60, soft=True)


def yhz_ii():
    d = D("yhz-ii", [2500, 650, 1110], dict(MATS, pad="leather#ddd8ec", harn="fabric#a9b0dc", strap="fabric#868cae"))
    W, DP = 2500, 650
    console(d, 0, 520, 15, 640, yb=115, front_castors=False)
    # long white box beam with slot vents; at the console end it turns down as a flat leg on a castor
    d.box("beam", [520, 470, 30, W, 720, 625], "white", r=6)
    d.box("beam-leg", [520, 120, 555, 605, 470, 625], "white", r=4, copies=[[0, 0, -525]])
    castor(d, "leg-castor", 563, 590, 100, [[0, 0, -525]])
    for k, x in enumerate((960, 1570, 2190)):
        d.decal(f"vent{k}", [x, 610, 625.6], [120, 8], "front", "plastic#5d6168", soft=True, copies=[[0, -24, 0]])
    # foot-end leg frame: 40 square white tubes, stretchers along z, black feet
    # (photo: one end frame — a leg at each end corner, a low stretcher across between them, a middle post from
    #  the stretcher up to the beam)
    d.box("fleg", [2425, 35, 40, 2470, 475, 85], "white", r=3, copies=[[0, 0, 530]])
    d.box("ffoot", [2422, 0, 37, 2473, 42, 88], "cap", r=4, copies=[[0, 0, 530]])
    d.box("fstr", [2425, 215, 85, 2470, 255, 570], "white", r=3)
    d.box("fpost", [2425, 255, 305, 2470, 475, 350], "white", r=3)
    # mechanism gap and two white trays with lilac-white glossy pads
    d.box("mech", [600, 720, 110, 2420, 765, 540], "plastic#6d7178", r=6)
    for nm, x0, x1 in (("a", 560, 1560), ("b", 1590, 2455)):
        top_pad(d, f"tray-{nm}", x0, x1, 12, DP - 12, 760, 805, "white", cr=60, r=18)
        top_pad(d, f"pad-{nm}", x0 + 25, x1 - 25, 37, DP - 37, 800, 815, "pad", cr=45, r=6)
    # grey straps along the head tray, harness across the split
    for k, zz in enumerate((150, 500)):
        d.strap(f"rope{k}", [[600, 816, zz], [1270, 816, zz]], [30, 3], "strap", soft=True)
    harness(d, 1250, 1540, 814, 150, 520, "harn", "strap", ext=150)
    ctrl(d, 1080, 815, 520, [[900, 822, 560], [640, 822, 600], [590, 812, 600]])
    d.coil("con-coil", [530, 860, 330], [585, 812, 590], 30, 7, 14, "cable", soft=True)
    bow_knee(d, 1700, 2440, 1110, 325, 815)
    d.save()


def yhz_iv():
    d = D("yhz-iv", [2600, 700, 1115], dict(MATS, pad="leather#a3a8d6", harn="fabric#a7aee0", strap="fabric#7c82b0", panel="gloss#34506c"))
    W, DP = 2600, 700
    console(d, 0, 540, 30, 670, cast=90, yb=110)
    # white cabinet with two louvred doors on castors
    d.box("cab", [540, 120, 40, 1900, 720, 660], "white", r=6)
    for k, (x0, x1) in enumerate(((560, 1210), (1230, 1880))):
        z = 660.5
        d.decal(f"door{k}-t", [(x0 + x1) / 2, 700, z], [x1 - x0, 3], "front", "seam", soft=True, copies=[[0, -560, 0]])
        d.decal(f"door{k}-s", [x0, 420, z], [3, 560], "front", "seam", soft=True, copies=[[x1 - x0, 0, 0]])
        for c in (0.28, 0.5, 0.72):
            d.decal(f"louv{k}-{int(c*100)}", [x0 + (x1 - x0) * c, 575, z], [75, 9], "front", "plastic#c2c6cc", soft=True,
                    repeat=rep(6, [0, -48, 0]))
        d.decal(f"screw{k}", [x0 + 20, 680, z + 0.2], [8, 8], "front", "plastic#8c9097", soft=True,
                copies=[[x1 - x0 - 40, 0, 0], [0, -520, 0], [x1 - x0 - 40, -520, 0]])
    castor(d, "castor", 610, 100, 100, corners(610, 100, 1830, 600))
    # stainless trays with chamfered corners and lavender pads; end section on a white housing
    cham_pad(d, "tray-a", 545, 1880, 25, DP - 25, 722, 772, "steel", cx=70, cz=70, cr=20, r=10)
    cham_pad(d, "pad-a", 580, 1845, 58, DP - 58, 768, 822, "pad", cx=55, cz=55, cr=18, r=14)
    cham_pad(d, "tray-b", 1905, 2580, 25, DP - 25, 722, 772, "steel", cx=130, cz=110, cr=20, r=10)
    cham_pad(d, "pad-b", 1940, 2545, 58, DP - 58, 768, 822, "pad", cx=110, cz=90, cr=18, r=14)
    # (photo: a shallow white housing under the end tray, near-vertical sides, rounded bottom edge)
    d.loft("end-house", [sec(625, 600, 560, 110, 2232, 350), sec(650, 650, 610, 125, 2237, 350),
                         sec(722, 668, 640, 135, 2240, 350)], "white")
    harness(d, 1470, 1820, 820, 160, 540, "harn", "strap", ext=200)
    ctrl(d, 1250, 822, 420, [[1100, 826, 440], [700, 826, 560], [560, 826, 600]])
    bow_knee(d, 2060, 2560, 1115, 350, 822)
    d.save()


ids = sys.argv[1:] or ["yhz-ii", "yhz-iv"]
if "yhz-ii" in ids: yhz_ii()
if "yhz-iv" in ids: yhz_iv()
