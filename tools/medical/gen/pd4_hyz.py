"""Batch pediatric-5: HYZ-IIR paediatric fumigation pod, XYRT-41 paediatric tilt table (drawn tilted as the photo).
Long axis along x, front = +z."""
from pd4lib import *


def sx(at, w, dd, r, cy, cz):
    """loft section for axis x: at = x, w across z, dd across y, centre (y = cy, z = cz)."""
    return {"at": at, "w": w, "d": dd, "r": r, "cx": cy, "cz": cz}


def hyziir():
    W, DD, H = 1500, 750, 950
    d = D("hyz-iir", [W, DD, H], {"lil": "gloss#a9a2e2", "lild": "gloss#8d86c6", "grey": "gloss#dcdde2",
                                  "tray": "gloss#f1f2f5", "win": "gloss#c8d3dd", "green": "gloss#2fb24a"})
    cz = 375
    # light-grey oval base plate, short lilac pedestal flaring into the tub
    plate = rr(200, 120, 1230, 630, 255)
    d.slab("plate", "top", P(plate), [0, 44], "grey", r=18)
    d.loft("pedestal", [sec(40, 640, 330, 165, 680, cz), sec(200, 600, 300, 150, 680, cz),
                        sec(290, 760, 420, 210, 690, cz), sec(330, 1000, 560, 280, 695, cz)], "lil")
    d.cyl("nipple", [985, 90, 470], [1010, 90, 520], 14, "metal#c9ccd0")
    # tub: oval hull, rounded bottom
    d.loft("tub", [sec(300, 1000, 470, 235, 700, cz), sec(380, 1250, 640, 320, 700, cz),
                   sec(480, 1370, 720, 360, 700, cz), sec(590, 1395, 742, 371, 700, cz),
                   sec(615, 1395, 742, 371, 700, cz)], "lil")
    # grey rim band all round, tongue of the control panel at the head end (right)
    rim = rr(-8, cz - 382, 1408, cz + 382, 380)
    d.slab("rim", "top", P(rim), [608, 650], "grey", r=12)
    d.slab("panel", "top", P(rr(1180, 300, 1500, 735, 60)), [600, 652], "grey", r=12)
    d.loft("panel-under", [sec(520, 160, 300, 60, 1330, 560), sec(600, 300, 420, 60, 1350, 520)], "grey")
    d.box("tray", [960, 650, 120, 1330, 655, 630], "tray", r=4)
    d.box("hole", [990, 655, 180, 996, 656, 186], "plastic#9aa0a8", soft=True, repeat=rep(11, [30, 0, 0]),
          copies=[[0, 0, 40 * k] for k in range(1, 8)])
    d.box("display", [1310, 652, 470, 1480, 656, 690], "gloss#59606e", r=6)
    d.box("display-lcd", [1330, 655, 590, 1400, 658, 670], "gloss#2b3f55", r=2)
    d.box("display-led", [1420, 655, 500, 1450, 658, 520], "gloss#d8c24a", r=2, copies=[[0, 0, 40], [0, 0, 80]])
    d.box("display-key", [1340, 655, 500, 1380, 658, 540], "gloss#cfd3da", r=3, copies=[[0, 0, 50]])
    for i, x in enumerate((1395, 1445)):
        d.lathe(f"btn{i}", [x, 625, 735], [[0, 0], [15, 0], [15, 4], [10, 9], [0, 9]], "green", axis="z")
    # lilac hood (photo): one helmet shell along x — highest over the foot end, sloping down continuously and
    # narrowing into the arched head tunnel (no step between dome and tunnel)
    hs = [(10, 380, 70, 640), (60, 600, 190, 690), (160, 734, 345, 772), (700, 734, 345, 772),
          (840, 560, 285, 742), (960, 480, 250, 725), (1062, 465, 240, 720)]
    d.loft("hood", [sx(x, w, dd, min(w, dd) * 0.45, cy, cz) for x, w, dd, cy in hs], "lil", axis="x")
    # head opening: dark arch on the tunnel end
    arch = [(cz - 165, 650), (cz + 165, 650)] + [(cz + 165 * math.cos(math.radians(a)), 670 + 150 * math.sin(math.radians(a)))
                                                 for a in range(0, 181, 10)]
    d.slab("arch", "side", P(arch), [1060, 1066], "plastic#5f5a86", r=2)
    # windows on the upper front slope (photo): a big rounded window over the foot end, a teardrop (round at the
    # left, pointed and lower to the right) beside it, a long strip on the top. Each window is drawn as thin slices
    # across x that follow the hood's cross-section (an arc band on the shell's rounded corner), so it lies on the
    # curved surface instead of a flat plate.
    def hsec(x):
        for (x0, w0, d0, c0), (x1, w1, d1, c1) in zip(hs, hs[1:]):
            if x0 <= x <= x1:
                t = (x - x0) / (x1 - x0)
                return w0 + (w1 - w0) * t, d0 + (d1 - d0) * t, c0 + (c1 - c0) * t
        return hs[-1][1:]

    def window(nm, xa, xb, prof, n=30):
        """Thin slices across x on the shell's rounded corner (constant section there, so they line up);
        prof(u) -> (centre elevation deg, half span deg), u = 0..1 along x; 0 deg = front, 90 = top."""
        step = (xb - xa) / n
        for k in range(n):
            ec, hspan = prof((k + 0.5) / n)
            if hspan <= 0.5: continue
            w, dd, cy = hsec(xa + step * (k + 0.5))
            R = min(w, dd) * 0.45
            zc, yc = cz + w / 2 - R, cy + dd / 2 - R
            e0, e1 = ec - hspan, ec + hspan
            m = 10
            arc_ = [(zc + (R + 3) * math.cos(math.radians(e0 + (e1 - e0) * j / m)),
                     yc + (R + 3) * math.sin(math.radians(e0 + (e1 - e0) * j / m))) for j in range(m + 1)]
            arc_ += [(zc + (R - 4) * math.cos(math.radians(e1 - (e1 - e0) * j / m)),
                      yc + (R - 4) * math.sin(math.radians(e1 - (e1 - e0) * j / m))) for j in range(m + 1)]
            d.slab(f"win-{nm}{k}", "side", P(arc_), [xa + step * k, xa + step * (k + 1)], "win", soft=True)

    def rounded(ec, half, cut=0.25):
        def f(u):
            q = abs(2 * u - 1)
            k = 1.0 if q < 1 - cut else math.sqrt(max(0.0, 1 - ((q - (1 - cut)) / cut) ** 2))
            return ec, half * (0.35 + 0.65 * k)
        return f

    def tear_(u):
        h = 26 * (math.sqrt(max(0.0, 1 - ((0.33 - u) / 0.33) ** 2)) if u < 0.33 else (1 - u) / 0.67)
        return 40 - 16 * u, h
    window("big", 180, 425, rounded(38, 27))
    window("tear", 455, 700, tear_)
    window("top", 230, 480, rounded(86, 9, 0.35), n=16)
    d.sphere("handle-rec", [610, 705, 733], None, "lild", radii=[118, 30, 10], soft=True)
    d.sphere("handle", [610, 705, 738], None, "chrome", radii=[100, 17, 9])
    return d


def xyrt41():
    TILT = 55
    W, DD = 1700, 700
    px, py = 1250, 560                      # pivot (near the foot end)
    c, s = math.cos(math.radians(-TILT)), math.sin(math.radians(-TILT))

    def T(x, y, z):
        """bed-local (flat) point -> world (tilted about the pivot)."""
        return [px + (x - px) * c - (y - py) * s, py + (x - px) * s + (y - py) * c, z]
    br = rot("z", -TILT, [px, py, 0])
    yb = py + 40                            # bed board top (local)
    xh, xf = 1440 - 1600, 1440              # head / foot end (local)
    tray_x = xh + 400
    H = int(max(T(xh, yb + 70, 0)[1], T(tray_x + 20, yb + 540, 0)[1]) + 15)
    d = D("xyrt-41", [W, DD, H], {"frame": "plastic#e3e5e9", "pad": "leather#2f9ad8", "padl": "leather#56b0e2",
                                  "wood": "wood#a56e4e", "steel": "metal#c9ccd0", "blk": "plastic#202124"})
    # white rectangular base frame on 4 corner legs with levelling feet, 4 castors, cross members
    for z0 in (40, DD - 90):
        d.box(f"rail-{z0}", [30, 140, z0, W - 30, 195, z0 + 50], "frame", r=4)
    for x0 in (30, W - 90):
        d.box(f"end-{x0}", [x0, 140, 40, x0 + 60, 195, DD - 40], "frame", r=4)
        d.box(f"leg-{x0}", [x0, 40, 40, x0 + 60, 140, 90], "frame", r=3, copies=[[0, 0, DD - 130]])
        d.cyl(f"foot-{x0}", [x0 + 30, 0, 65], [x0 + 30, 40, 65], 40, "blk", copies=[[0, 0, DD - 130]])
    for x in (620, 1150):
        d.box(f"cross-{x}", [x, 150, 90, x + 50, 190, DD - 90], "frame", r=3)
    for x in (230, 1480):
        d.box(f"cmount-{x}", [x - 30, 100, 60, x + 30, 140, 120], "frame", r=3, copies=[[0, 0, DD - 180]])
        caster(d, f"castor-{x}", x, 90, 75, copies=[[0, 0, DD - 180]])
    # pivot posts near the foot end; small rectangular hand rail frame at the head end
    d.box("post", [px - 30, 195, 60, px + 30, py, 110], "frame", r=3, copies=[[0, 0, DD - 170]])
    d.cyl("pivot", [px, py, 50], [px, py, DD - 50], 40, "steel")
    # photo: the small rail frame at the head end stands ACROSS the base (an inverted U from the front rail to the back)
    d.tube("hand-rail", [[190, 195, 65], [190, 470, 65], [190, 470, DD - 65], [190, 195, DD - 65]], 32, "frame", bend=30)
    # black linear actuator from the cross member up to the bed underside
    a0 = [645, 190, DD / 2]
    a1 = T(760, yb - 70, DD / 2)
    mid = [a0[k] + (a1[k] - a0[k]) * 0.55 for k in range(3)]
    d.cyl("act-body", a0, mid, 70, "blk")
    d.cyl("act-rod", mid, a1, 34, "steel")
    d.box("act-motor", [600, 190, DD / 2 - 110, 720, 290, DD / 2 - 40], "blk", r=20)
    # tilted bed: aluminium side rails, white board, blue PU pad with straps, leg slot, splits
    d.box("bed-rail", [xh + 20, yb - 70, 30, xf, yb, 70], "steel", r=6, rot=br, copies=None)
    d.box("bed-rail2", [xh + 20, yb - 70, DD - 70, xf, yb, DD - 30], "steel", r=6, rot=br)
    # red stripe along the inside of each aluminium side rail (photo)
    d.box("rail-stripe", [xh + 30, yb - 62, 26, xf - 10, yb - 50, 30], "plastic#d23a2a", soft=True, rot=br)
    d.box("rail-stripe2", [xh + 30, yb - 62, DD - 30, xf - 10, yb - 50, DD - 26], "plastic#d23a2a", soft=True, rot=br)
    d.box("bed-board", [xh + 10, yb - 15, 40, xf, yb, DD - 40], "frame", r=4, rot=br)
    d.box("pad-head", [xh, yb, 35, xh + 330, yb + 70, DD - 35], "pad", r=24, puff=4, rot=br)
    d.box("pad-main", [xh + 335, yb, 35, xf, yb + 70, DD - 35], "pad", r=24, puff=4, rot=br)
    d.box("slot", [xh + 950, yb + 66, DD / 2 - 14, xh + 1300, yb + 72, DD / 2 + 14], "padl", r=6, rot=br)
    for i, xs in enumerate((xh + 400, xh + 820, xh + 1170)):
        d.box(f"strap{i}", [xs, yb - 25, 28, xs + 130, yb + 78, DD - 28], "padl", r=10, rot=br)
        d.box(f"buckle{i}", [xs + 40, yb + 20, DD - 30, xs + 90, yb + 60, DD - 22], "blk", r=4, rot=br)
    # chest tray (wood, U cut-out, stainless bow) standing off the bed; foot plate at the foot end
    tray = [(20, yb + 120), (DD - 20, yb + 120), (DD - 20, yb + 520), (20, yb + 520)]
    cut = [(DD / 2 - 160, yb + 110), (DD / 2 + 160, yb + 110), (DD / 2 + 160, yb + 260), (DD / 2 - 160, yb + 260)]
    from sflib import round_poly
    outline = P(round_poly(tray, 40)) + " " + P(round_poly(cut, 60))
    # cut-out is open at the bed side: the bed-side strip of the outline is removed by drawing the tray as a U
    u = [(20, yb + 120), (DD / 2 - 160, yb + 120), (DD / 2 - 160, yb + 270), (DD / 2 + 160, yb + 270),
         (DD / 2 + 160, yb + 120), (DD - 20, yb + 120), (DD - 20, yb + 520), (20, yb + 520)]
    d.slab("tray", "side", P(round_poly(u, 35)), [tray_x, tray_x + 22], "wood", r=5, rot=br)
    d.tube("tray-bow", [[tray_x + 11, yb + 20, 15], [tray_x + 11, yb + 535, 15], [tray_x + 11, yb + 535, DD - 15],
                        [tray_x + 11, yb + 20, DD - 15]], 22, "steel", bend=45, rot=br)
    # foot plate: photo — opened past square to the bed, ~15 deg towards the floor
    fo = {"rot": rot("z", -15, [xf, yb - 20, 0]), "rots": [br]}
    d.box("foot-plate", [xf - 5, yb - 20, 60, xf + 18, yb + 260, DD - 60], "wood", r=6, **fo)
    d.tube("foot-bow", [[xf + 6, yb - 30, 50], [xf + 6, yb + 270, 50], [xf + 6, yb + 270, DD - 50],
                        [xf + 6, yb - 30, DD - 50]], 18, "steel", bend=30, **fo)
    # side lever with black knob on the front side of the bed
    l0 = T(xh + 620, yb - 40, DD - 30)
    d.cyl("lever", l0, [l0[0] - 60, l0[1] - 260, DD + 0], 18, "steel")
    d.sphere("lever-knob", [l0[0] - 10, l0[1] - 40, DD - 15], 40, "blk")
    # hand switch hanging at the head end, its cable down to the base
    h0 = T(xh + 40, yb - 60, 20)
    d.box("switch", [h0[0] - 25, h0[1] - 130, 0, h0[0] + 25, h0[1] - 20, 30], "plastic#3f8fd8", r=8)
    d.tube("cable", [[h0[0], h0[1] - 130, 15], [h0[0] - 20, 900, 15], [h0[0] - 10, 400, 25], [200, 200, 40]], 7, "blk",
           bend=200, soft=True)
    return d


if __name__ == "__main__":
    main({"hyz-iir": hyziir, "xyrt-41": xyrt41})
