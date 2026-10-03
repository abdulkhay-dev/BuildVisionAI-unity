"""Portal BWS frames of batch robot-1: xy-k-m1 (two stations, cantilever), xy-k-m2 (= M1 + treadmill + bike),
xy-k-m3 (single arch, castors, handrails), xy-k-m4 (pneumatic single arch).
Posts: white upper, dark lower part with a slanted split (higher on the inner side), on A-shaped dark feet; white
top beam with chamfered bolted corner plates; hoist cable, cream ball, chrome spreader bar, black harness.
usage: python3 r_portal.py [id ...]"""
import sys
from r_lib import *

PW, PD = 120, 100          # post section (x, z)
BH = 120                   # beam height


def post(d, n, x0, zc, H, split=(820, 990), inner=+1):
    """Post x0..x0+PW: dark lower part with a slanted top, white upper part up to the beam."""
    x1 = x0 + PW
    ylo, yhi = split
    yl, yr = (ylo, yhi) if inner > 0 else (yhi, ylo)        # the split is higher on the inner side
    z0, z1 = zc - PD / 2, zc + PD / 2
    d.slab(f"post-low-{n}", "front", f"M {x0} 380 L {x1} 380 L {x1} {yr} L {x0} {yl} Z", [z0, z1], "dark", r=4)
    d.slab(f"post-up-{n}", "front", f"M {x0} {yl} L {x1} {yr} L {x1} {H - BH} L {x0} {H - BH} Z", [z0, z1], "white", r=4)


def foot(d, n, x0, zc, depth=800, castors=False):
    """A-shaped dark foot along z under the post: a low bar on the floor rising in concave flanks to the post."""
    x1 = x0 + PW
    h0 = 95 if castors else 45
    hz = depth / 2
    o = (f"M {zc - hz} {h0} L {zc + hz} {h0} L {zc + hz} {h0 + 90} Q {zc + hz - 20} {h0 + 110} {zc + hz - 80} {h0 + 115} "
         f"Q {zc + 120} {h0 + 150} {zc + 60} {420} L {zc - 60} 420 Q {zc - 120} {h0 + 150} {zc - hz + 80} {h0 + 115} "
         f"Q {zc - hz + 20} {h0 + 110} {zc - hz} {h0 + 90} Z")
    d.slab(f"foot-{n}", "side", o, [x0 - 5, x1 + 5], "dark", r=6)
    if castors:
        d.caster(f"castor-{n}", [x0 + PW / 2, 0, zc - hz + 70], 75, "rubber#cfd2d6", copies=[[0, 0, depth - 140]])
    else:
        d.cyl(f"lev-{n}", [x0 + PW / 2, 0, zc - hz + 60], [x0 + PW / 2, h0, zc - hz + 60], 50, "black",
              copies=[[0, 0, depth - 120]])


def corner(d, n, x0, zc, H, left=False, right=False, g=150):
    """Front corner plate over a post top: gussets to the sides in `left`/`right` (inner sides of the beam),
    an outer side without a beam gets a 45-degree chamfer; bolt heads on the front."""
    x1 = x0 + PW
    yb = H - BH
    pts = []
    if left:
        pts += [(x0 - g, yb), (x0 - g, H)]
    else:
        pts += [(x0, yb - 160), (x0, H - 70), (x0 + 70, H)]
    if right:
        pts += [(x1 + g, H), (x1 + g, yb), (x1, yb - g)]
    else:
        pts += [(x1 - 70, H), (x1, H - 70), (x1, yb - 160)]
    if left:
        pts += [(x0, yb - g)]
    o = "M " + " L ".join(f"{a:.0f} {b:.0f}" for a, b in pts) + " Z"
    d.slab(f"corner-{n}", "front", o, [zc - PD / 2 - 3, zc + PD / 2 + 3], "white", r=4)
    bolts = [(x0 + 30, H - 45), (x1 - 30, H - 45), (x0 + 30, H - 110), (x1 - 30, H - 110), (x0 + 60, yb - 60)]
    if left:
        bolts += [(x0 - 90, H - 45), (x0 - 90, H - 95)]
    if right:
        bolts += [(x1 + 90, H - 45), (x1 + 90, H - 95)]
    for k, (bx, by) in enumerate(bolts):
        d.decal(f"bolt-{n}-{k}", [bx, by, zc + PD / 2 + 3.5], [11, 11], "bolt", face="front", soft=True)


def hoist(d, n, x, zc, H, ball_y, spread=440, tilt=0):
    """Hoist cable from the beam, a cream ball and a chrome spreader bar with two hooks; returns the hook points."""
    d.cyl(f"cable-{n}", [x, H - BH, zc], [x, ball_y + 20, zc], 6, "rope", soft=True)
    d.box(f"cable-exit-{n}", [x - 25, H - BH - 8, zc - 25, x + 25, H - BH, zc + 25], "black", r=3)
    d.sphere(f"ball-{n}", [x, ball_y, zc], 44, "cream")
    sy = ball_y - 50
    d.cyl(f"spreader-{n}", [x - spread / 2, sy + tilt, zc], [x + spread / 2, sy - tilt, zc], 26, "chrome")
    d.tube(f"spreader-link-{n}", [[x, ball_y - 20, zc], [x - 12, sy, zc], [x + 12, sy, zc], [x, ball_y - 20, zc]], 8, "chrome",
           bend=6)
    return [hook(d, f"hook-{n}-{i}", [x + s * (spread / 2 - 20), sy + (-s) * tilt, zc], "chrome", 90)
            for i, s in enumerate((-1, 1))]


def panel(d, n, x, y, zc, mat="blue", floor_box=None):
    """Small control panel on a post front, its cable running down to the floor box."""
    zf = zc + PD / 2
    d.box(f"panel-{n}", [x - 38, y, zf, x + 38, y + 120, zf + 34], mat, r=8)
    d.box(f"panel-face-{n}", [x - 28, y + 55, zf + 34, x + 28, y + 100, zf + 35], "lcd", r=2, soft=True)
    if floor_box:
        bx, bz = floor_box
        d.tube(f"panel-cable-{n}", [[x + 30, y, zf + 20], [x + 45, y - 300, zf + 30], [x + 50, 300, zf + 40],
                                    [bx, 120, bz]], 8, "black", bend=120, soft=True)


def ctrl_box(d, n, x0, z0, w=300, dd=200):
    d.box(f"ctrl-{n}", [x0, 0, z0, x0 + w, 160, z0 + dd], "white", r=12)
    d.lathe(f"ctrl-knob-{n}", [x0 + 60, 160, z0 + 60], [[0, 0], [12, 0], [12, 14], [0, 16]], "black",
            repeat=rep(4, [45, 0, 0]))


MATS = {"white": "plastic#f2f3f4", "dark": "plastic#2a3546", "black": "plastic#1b1d20", "chrome": "chrome",
        "cream": "plastic#efe6c8", "rope": "metal#dcdcdc", "bolt": "plastic#8d939a", "blue": "gloss#2f86d0",
        "lcd": "plastic#d9eef5", "web": "fabric#17191c", "vpad": "fabric#1f2226", "red": "gloss#d42a26",
        "steel": "metal#cfd3d8"}


def two_station(id_, Dp, zc):
    # review 2026-10-03: the M1/M2 photos show the left post's floor box OUTSIDE the left post (-x) and the right
    # post's box on its +x side; the frame is shifted by OX to make room (W 2000 -> 2320, closer to the 2400 leaflet)
    OX = 320
    W, H = 2000 + OX, 2400
    d = D(id_, [W, Dp, H], dict(MATS))
    xl, xr = OX, 1260 + OX               # posts
    for n, x0, inner in (("l", xl, 1), ("r", xr, -1)):
        post(d, n, x0, zc, H, inner=inner)
        foot(d, n, x0, zc)
    d.box("beam", [xl + 60, H - BH, zc - PD / 2, W - 2, H, zc + PD / 2], "white", r=4)
    d.box("beam-end", [W - 70, H - BH, zc - PD / 2, W, H, zc + PD / 2], "white", r=14)
    corner(d, "l", xl, zc, H, right=True)
    corner(d, "r", xr, zc, H, left=True, right=True)
    d.decal("beam-bolt", [(xl + xr + PW) / 2, H - 60, zc + PD / 2 + 0.5], [11, 11], "bolt", face="front", soft=True)
    d.box("scale", [xr + 30, 1550, zc + PD / 2, xr + 50, 1950, zc + PD / 2 + 1.5], "blue", r=1, soft=True)
    ctrl_box(d, "l", xl - 310, zc - 330)
    ctrl_box(d, "r", xr + PW + 10, zc - 330)
    panel(d, "l", xl + 60, 1300, zc, floor_box=(xl - 160, zc - 230))
    panel(d, "r", xr + 60, 1300, zc, floor_box=(xr + 260, zc - 230))
    d.tube("ctrl-cord-l", [[xl - 310, 40, zc - 230], [xl - 320, 4, zc - 120], [xl - 220, 4, zc + 40], [xl - 300, 4, zc + 200]],
           7, "black", bend=60, soft=True)
    s1 = (xl + xr + PW) / 2
    s2 = 1730 + OX
    for n, x, tilt in (("1", s1, 18), ("2", s2, 12)):
        hk = hoist(d, n, x, zc, H, 2060, tilt=tilt)
        harness(d, x, zc + 30, 1950, hk, vest_y=1420, mat="web", pad="vpad", accent="red", buckle="black", pre=f"h{n}",
                vest_w=380, vest_d=260)
    return d, s1, s2


def gen_m1():
    d, _, _ = two_station("xy-k-m1", 900, 450)
    d.save()


def treadmill(d, x0, z0, L=2000, Wd=820):
    """Dark-bronze rehab treadmill with parallel handrails, console at the front (z0 + L)."""
    x1 = x0 + Wd
    z1 = z0 + L
    d.box("tm-deck", [x0, 40, z0, x1, 200, z1 - 300], "black", r=20)
    d.box("tm-belt", [x0 + 110, 200, z0 + 20, x1 - 110, 212, z1 - 320], "belt", r=10)
    d.box("tm-side", [x0 + 10, 200, z0 + 10, x0 + 105, 215, z1 - 310], "black", r=6, copies=[[Wd - 115, 0, 0]])
    d.loft("tm-hood", [sec(40, Wd - 20, 300, 60, (x0 + x1) / 2, z1 - 150), sec(260, Wd - 60, 260, 70, (x0 + x1) / 2, z1 - 160),
                       sec(300, Wd - 120, 200, 60, (x0 + x1) / 2, z1 - 170)], "black")
    d.cyl("tm-foot", [x0 + 40, 0, z0 + 60], [x0 + 40, 40, z0 + 60], 40, "black", copies=[[Wd - 80, 0, 0]])
    for i, x in enumerate((x0 + 40, x1 - 40)):
        d.sweep(f"tm-upright-{i}", [[x, 200, z1 - 230], [x, 700, z1 - 130], [x, 1180, z1 - 220]], [70, 45], "bronze",
                bend=500, r=10)
        so = -1 if i == 0 else 1            # outward: the black ear handles hang outside the uprights (photo)
        d.tube(f"tm-loop-{i}", [[x - so * 20, 1170, z1 - 180], [x + so * 120, 1110, z1 - 280],
                                 [x + so * 120, 940, z1 - 420], [x + so * 10, 870, z1 - 470]], 42, "black", bend=90)
    d.bar("tm-cross", [x0 + 40, 900, z1 - 170], [x1 - 40, 900, z1 - 170], [60, 70], "bronze", r=8)
    # console (review 2026-10-03): a wide black visor arched in plan, wider than the uprights, tilted towards the
    # walker, with a dark display window, two speaker slots and the blue logo; red switch on the motor hood
    xm = (x0 + x1) / 2
    vis = []
    for u in (-1, -0.7, -0.35, 0, 0.35, 0.7, 1):
        vis.append({"at": xm + u * (Wd / 2 + 70), "w": 300 - 60 * abs(u), "d": 130 - 30 * abs(u), "r": 50,
                    "cx": 1230 - 40 * u * u, "cz": z1 - 210 + 70 * (1 - u * u)})
    d.loft("tm-console", vis, "black", axis="x", rot=rot("x", -18, [xm, 1230, z1 - 150]))
    d.box("tm-display", [xm - 120, 1290, z1 - 250, xm + 120, 1302, z1 - 170], "leds", r=6,
          rot=rot("x", -18, [xm, 1230, z1 - 150]))
    d.box("tm-slot", [xm - 70, 1180, z1 - 72, xm - 50, 1230, z1 - 66], "belt", r=4, copies=[[100, 0, 0]],
          rot=rot("x", -18, [xm, 1230, z1 - 150]))
    d.cyl("tm-logo", [xm, 1300, z1 - 120], [xm, 1303, z1 - 120], 30, "blue", soft=True)
    d.box("tm-switch", [xm - 30, 160, z1 - 1, xm + 30, 200, z1 + 4], "red", r=6)
    d.cyl("tm-hood-logo", [xm, 300, z1 - 200], [xm, 303, z1 - 200], 30, "blue", soft=True)
    # parallel handrails: 3 bronze posts each side, chrome top rails, height knobs
    for i, x in enumerate((x0 + 30, x1 - 30)):
        for k, z in enumerate((z0 + 80, z0 + 700, z0 + 1300)):
            d.bar(f"tm-post-{i}-{k}", [x, 200, z], [x, 960, z], [50, 50], "bronze", r=4)
            d.lathe(f"tm-knob-{i}-{k}", [x, 760, z + 25], [[0, 0], [10, 0], [10, 12], [24, 16], [24, 32], [0, 34]], "black",
                    axis="z")
        d.cyl(f"tm-rail-{i}", [x, 975, z0 + 40], [x, 975, z0 + 1340], 38, "chrome")
        d.sphere(f"tm-rail-end-{i}", [x, 975, z0 + 40], 38, "chrome", copies=[[0, 0, 1300]])


def bike(d, x0, zc):
    """Upright exercise bike lying along x (handlebar at +x): silver flywheel housing, black frame, saddle, feet."""
    d.cyl("bk-foot-rear", [x0, 30, zc - 260], [x0, 30, zc + 260], 50, "black")
    d.cyl("bk-foot-front", [x0 + 700, 30, zc - 260], [x0 + 700, 30, zc + 260], 50, "black")
    d.bar("bk-beam", [x0, 40, zc], [x0 + 700, 40, zc], [60, 40], "black", r=6)
    d.loft("bk-housing", [sec(40, 380, 140, 60, x0 + 470, zc), sec(300, 400, 150, 70, x0 + 480, zc),
                          sec(470, 260, 120, 60, x0 + 470, zc)], "silver", dome="end", domeH=60)
    d.bar("bk-seatpost", [x0 + 300, 60, zc], [x0 + 230, 900, zc], [55, 45], "black", r=10)
    d.box("bk-saddle", [x0 + 130, 900, zc - 90, x0 + 330, 960, zc + 90], "black", r=28)
    # review 2026-10-03: the photo's handlebar is lower (~1030) - a U bar with upturned grips, the console on the stem
    d.bar("bk-stem", [x0 + 560, 400, zc], [x0 + 690, 1000, zc], [55, 45], "black", r=10)
    d.tube("bk-bars", [[x0 + 860, 1150, zc - 200], [x0 + 860, 1040, zc - 200], [x0 + 700, 1020, zc - 200], [x0 + 700, 1020, zc + 200],
                       [x0 + 860, 1040, zc + 200], [x0 + 860, 1150, zc + 200]], 32, "black", bend=60)
    d.box("bk-console", [x0 + 640, 1000, zc - 70, x0 + 720, 1080, zc + 70], "black", r=12)
    d.cyl("bk-crank", [x0 + 470, 300, zc - 160], [x0 + 470, 300, zc + 160], 30, "black")
    d.box("bk-pedal", [x0 + 420, 280, zc - 200, x0 + 520, 310, zc - 150], "black", r=6, copies=[[0, 0, 350]])


def gen_m2():
    d, s1, s2 = two_station("xy-k-m2", 2100, 1300)
    d.d["mats"].update({"bronze": "metal#4c443d", "belt": "rubber#1e1f21", "leds": "gloss#3a1a1a", "silver": "metal#b8bcc2"})
    treadmill(d, s1 - 410, 80)
    bike(d, s2 - 330, 1300)
    d.save()


def single(id_, W, Dp, H, castors, dark, rails, panel_y, ball_y, vest_y, extra=None, split=(880, 1040), scales=True,
           OX=0, scale_y=(1500, 1820), scale_w=40):
    """OX (review 2026-10-03): room on the left for the floor box standing OUTSIDE the left post (M3 photo)."""
    d = D(id_, [W + OX, Dp, H], dict(MATS, dark=dark))
    zc = Dp / 2
    xl, xr = OX, OX + W - PW
    for n, x0, inner in (("l", xl, 1), ("r", xr, -1)):
        post(d, n, x0, zc, H, inner=inner, split=split)
        foot(d, n, x0, zc, castors=castors)
        if scales:
            xm = x0 + PW / 2
            d.box(f"scale-{n}", [xm - scale_w / 2, scale_y[0], zc + PD / 2, xm + scale_w / 2, scale_y[1], zc + PD / 2 + 1.5], "blue",
                  r=1, soft=True)
    d.box("beam", [xl + 60, H - BH, zc - PD / 2, xr + 60, H, zc + PD / 2], "white", r=4)
    corner(d, "l", xl, zc, H, right=True)
    corner(d, "r", xr, zc, H, left=True)
    d.decal("beam-bolt", [OX + W / 2, H - 60, zc + PD / 2 + 0.5], [11, 11], "bolt", face="front", soft=True)
    if rails:
        # black handrails on clamps, pointing inward from each post, knob lock
        for n, x0, s in (("l", xl, 1), ("r", xr, -1)):
            xi = x0 + (PW if s > 0 else 0)
            d.box(f"rail-clamp-{n}", [x0 - 6, 960, zc - PD / 2 - 6, x0 + PW + 6, 1060, zc + PD / 2 + 6], "dark", r=6)
            d.cyl(f"rail-{n}", [xi, 1030, zc + 20], [xi + s * 250, 1030, zc + 20], 40, "foam")
            d.sphere(f"rail-end-{n}", [xi + s * 250, 1030, zc + 20], 40, "foam")
            d.lathe(f"rail-knob-{n}", [x0 + PW / 2, 1010, zc + PD / 2 + 6], [[0, 0], [9, 0], [9, 14], [22, 18], [22, 36], [0, 38]],
                    "black", axis="z")
    d.d["mats"]["foam"] = "rubber#1d1f22"
    if panel_y:
        if OX:
            panel(d, "l", xl + 60, panel_y, zc, floor_box=(xl - 140, zc - 60))
            ctrl_box(d, "l", xl - 260, zc - 150, w=240, dd=180)
        else:
            panel(d, "l", xl + 60, panel_y, zc, floor_box=(xl + 150, zc - 300))
            ctrl_box(d, "l", xl + PW + 10, zc - 380, w=240, dd=180)
    hk = hoist(d, "1", OX + W / 2, zc, H, ball_y, spread=460, tilt=0)
    harness(d, OX + W / 2, zc + 30, ball_y, hk, vest_y=vest_y, mat="web", pad="vpad", accent="red", buckle="black",
            vest_w=360, vest_d=250)
    if extra:
        extra(d, zc)
    d.save()


def m4_extra(d, zc):
    # pneumatic: grey control unit with a gauge window and a knob on the right post; air hose to the beam
    x = 1400 - PW / 2
    d.box("air-unit", [x - 55, 1620, zc + 50, x + 55, 1850, zc + 95], "grey", r=8)
    d.box("air-window", [x - 35, 1760, zc + 95, x + 35, 1820, zc + 96.5], "lcd", r=3, soft=True)
    d.lathe("air-knob", [x, 1680, zc + 95], [[0, 0], [20, 0], [20, 18], [0, 22]], "black", axis="z")
    d.cyl("air-cyl", [700, 2280, zc], [700, 2230, zc], 60, "grey")    # small fitting at the cable exit (photo)


GEN = {
    "xy-k-m1": gen_m1,
    "xy-k-m2": gen_m2,
    "xy-k-m3": lambda: single("xy-k-m3", 1200, 900, 2300, True, "plastic#2a3546", True, 1150, 1880, 1250, OX=270,
                              scale_y=(1300, 1530), scale_w=34),
    "xy-k-m4": lambda: (MATS.update(grey="plastic#a7acb3") or
                        single("xy-k-m4", 1400, 900, 2400, False, "plastic#1f4744", False, None, 1750, 1250, m4_extra,
                               split=(760, 860), scales=False)),
}

if __name__ == "__main__":
    for i in (sys.argv[1:] or list(GEN)):
        GEN[i]()
