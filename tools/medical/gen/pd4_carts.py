"""Tube-frame items of batch pediatric-4: XYRT-45 / XYRT-46 sand-bag carts, XYRT-50 creeping frame, XYRT-66 pedal cart.
Front = +z (z = depth), x from the left seen from the front."""
from pd4lib import *

WHITE = "plastic#eeeeec"


def cart(id, kind):
    W, DD, H = 670, 330, 760
    d = D(id, [W, DD, H], {"frame": WHITE, "cap": "rubber#1c1d1f"})
    yl, yt = 330, 615            # lower / top shelf height (tube centre line)
    zf, zb = 300, 32             # front / back legs
    for side, x in (("l", 22), ("r", W - 22)):
        # S frame: front leg up to the lower shelf, diagonal up to the back of the top shelf, then forward along it
        d.tube(f"s-{side}", [[x, 62, zf], [x, yl, zf], [x, yt + 25, zb + 10], [x, yt + 25, DD - 22]], 25, "frame",
               bend=70)
        d.cyl(f"cap-{side}", [x, yt + 25, DD - 24], [x, yt + 25, DD], 30, "cap")
        # rear leg up to the lower shelf, then forward along its end into the front leg
        d.tube(f"u-{side}", [[x, 62, zb], [x, yl, zb], [x, yl, zf - 10]], 25, "frame", bend=45)
        for z in (zf, zb):
            d.cyl(f"stem-{side}{z}", [x, 50, z], [x, 66, z], 22, "frame")
            caster(d, f"castor-{side}{z}", x, z, 60)
    # shelves: white sheet trays with tube rims (XYRT-45) / tube racks (XYRT-46)
    for nm, y, z0, z1 in (("low", yl, zb, zf), ("top", yt, zb + 20, DD - 30)):
        d.cyl(f"{nm}-rim-f", [22, y + 8, z1], [W - 22, y + 8, z1], 22, "frame")
        d.cyl(f"{nm}-rim-b", [22, y + 8, z0], [W - 22, y + 8, z0], 22, "frame")
        if kind == "cuff":
            d.box(f"{nm}-tray", [30, y - 4, z0, W - 30, y + 2, z1], "frame", r=2)
            d.box(f"{nm}-lip", [30, y - 4, z1 - 4, W - 30, y + 30, z1 + 8], "frame", r=3)
        else:
            d.cyl(f"{nm}-wire", [22, y, z0 + 60], [W - 22, y, z0 + 60], 14, "frame",
                  copies=[[0, 0, (z1 - z0 - 120) / 2], [0, 0, z1 - z0 - 120]])
            d.box(f"{nm}-clip", [W / 2 - 15, y - 10, z0, W / 2 + 15, y + 6, z1], "metal#b8bcc2", r=3)
    # small blue maker's label on the right end of the top shelf
    d.box("label", [W - 13, yt + 10, 150, W - 9, yt + 34, 215], "plastic#3a6cc8", r=2, soft=True)
    if kind == "cuff":
        # cuff weights (photo): ~10 per shelf lying front-back, a wide black band with 4 flat crumpled turquoise
        # sand pockets, a lot of black between and round them; laid loosely (shifted, slightly turned, overlapping);
        # long black Velcro ends rising at the back at varied angles
        import random
        rnd = random.Random(45 if id == "xyrt-45" else 46)
        for nm, y, z0, z1 in (("low", yl + 2, zb + 12, zf - 14), ("top", yt + 2, zb + 25, DD - 40)):
            n, pitch, x0 = 10, 59, 64
            L = z1 - z0
            for k in range(n):
                xc = x0 + k * pitch + rnd.uniform(-7, 7)
                dz = rnd.uniform(-8, 8)
                yy = y + (6 if k % 2 else 0)                  # every other cuff lies a little over its neighbours
                r_ = rot("y", rnd.uniform(-9, 9), [xc, yy, (z0 + z1) / 2])
                d.box(f"{nm}-band{k}", [xc - 30, yy, z0 + dz, xc + 30, yy + 14, z1 + dz], "fabric#1d1f23", r=6,
                      puff=2, rot=r_)
                pl = (L - 40) / 4
                d.box(f"{nm}-pk{k}", [xc - 17, yy + 8, z0 + dz + 16, xc + 17, yy + 26, z0 + dz + 16 + pl - 22],
                      "fabric#1f9fb4", r=9, puff=5, rot=r_, copies=[[0, rnd.uniform(-3, 3), j * pl] for j in range(1, 4)])
                # Velcro end: up and back from the back pocket, a random lean
                lean = rnd.uniform(-1, 1)
                h = rnd.uniform(25, 80)
                d.strap(f"{nm}-velcro{k}", [[xc, yy + 10, z0 + dz + 30], [xc, yy + 18, z0 + dz + 2],
                                            [xc + lean * 20, yy + h * 0.6, z0 + dz - 30],
                                            [xc + lean * 40, yy + h, z0 + dz - 60]], [26, 3], "fabric#17181b",
                        bend=20, soft=True)
    else:
        # lime-green drawstring sand bags (photo): soft rounded sacks side by side touching, each a little different,
        # their gathered necks drawn to the back-top, steel rings lying on the top at the back; vertical creases
        import random
        rnd = random.Random(46)
        for nm, y, zc in (("low", yl + 6, (zb + zf) / 2), ("top", yt + 6, (zb + DD - 20) / 2)):
            n, pitch, x0 = 9, 66, 70
            for k in range(n):
                xc = x0 + k * pitch + rnd.uniform(-5, 5)
                w = rnd.uniform(78, 90)
                h = rnd.uniform(135, 160)
                zz = zc + rnd.uniform(-10, 10)
                r_ = rot("z", rnd.uniform(-6, 6), [xc, y, zz])
                d.loft(f"{nm}-bag{k}", [sec(y, w * 0.8, 225, w * 0.38, xc, zz + 12),
                                        sec(y + h * 0.3, w, 262, w * 0.48, xc, zz + 14),
                                        sec(y + h * 0.62, w * 0.95, 232, w * 0.46, xc, zz + 2),
                                        sec(y + h * 0.85, w * 0.85, 190, w * 0.42, xc, zz - 25),
                                        sec(y + h, w * 0.45, 60, w * 0.22, xc, zz - 78)],
                       "fabric#86c43a", dome="end", domeH=10, rot=r_)
                # steel ring through the gathered neck, lying back on the top of the sack
                rc = [xc + rnd.uniform(-6, 6), y + h + 2, zz - 92]
                tilt = rnd.uniform(15, 40)
                ring_pts = [[rc[0] + 38 * math.cos(math.radians(a)), rc[1] + 38 * math.sin(math.radians(a)) * math.sin(math.radians(tilt)),
                             rc[2] + 38 * math.sin(math.radians(a)) * math.cos(math.radians(tilt))] for a in range(0, 361, 30)]
                d.tube(f"{nm}-ring{k}", ring_pts, 5, "chrome", soft=True)
    return d


def xyrt45(): return cart("xyrt-45", "cuff")
def xyrt46(): return cart("xyrt-46", "bag")


def xyrt50():
    W, DD, H = 800, 400, 620
    d = D("xyrt-50", [W, DD, H], {"frame": "metal#c8c2b2", "ball": "rubber#1a1b1d", "sling": "fabric#3a66c4"})
    yt = H - 13
    xa, xb = 25, W - 25
    for nm, z in (("f", DD - 25), ("b", 25)):
        # long rail bending down into the legs at both ends
        d.tube(f"rail-{nm}", [[xa, 120, z], [xa, yt, z], [xb, yt, z], [xb, 120, z]], 25, "frame", bend=70)
        # telescopic lower legs (thinner), black ball castors
        for x in (xa, xb):
            d.cyl(f"leg-{nm}{x}", [x, 30, z], [x, 140, z], 21, "frame")
            d.cyl(f"collar-{nm}{x}", [x, 118, z], [x, 132, z], 29, "frame")
            d.sphere(f"ball-{nm}{x}", [x, 25, z], 50, "ball")
    # end cross rails just inside the bends
    for x in (xa + 55, xb - 55):
        d.cyl(f"cross-{x}", [x, yt - 2, 25], [x, yt - 2, DD - 25], 22, "frame")
    # two blue slings hanging between the long rails like hammocks
    for i, xc in enumerate((235, 545)):
        zf, zb = DD - 25, 25
        path = [[xc, yt + 13, zf - 8], [xc, yt + 6, zf + 13], [xc, yt - 60, zf + 14], [xc, 330, zf - 35],
                [xc, 285, zf - 110], [xc, 285, zb + 110], [xc, 330, zb + 35], [xc, yt - 60, zb - 14], [xc, yt + 6, zb - 13],
                [xc, yt + 13, zb + 8]]
        d.strap(f"sling{i}", path, [165, 4], "sling", bend=60)   # photo: ~0.2 of the rail length each
    return d


def xyrt66():
    W, DD, H = 350, 400, 570
    d = D("xyrt-66", [W, DD, H], {"deck": "plastic#2f9e48", "tube": "plastic#e6e9ec", "grip": "rubber#202124",
                                  "hub": "plastic#2f9e48", "steel": "chrome"})
    wd, ww = 150, 36
    yax = wd / 2
    # 4 wheels: black tyres, green hubs with holes
    for nm, x in (("l", ww / 2), ("r", W - ww / 2)):
        for zn, z in (("b", 85), ("f", DD - 85)):
            d.add(f"tyre-{nm}{zn}", "wheel", "rubber#1d1e20", at=[x, yax, z], d=wd, d2=ww, axis="x")
            d.lathe(f"hub-{nm}{zn}", [x + (ww / 2 + 1 if nm == "r" else -ww / 2 - 1), yax, z],
                    [[0, 0], [52, 0], [52, 4], [20, 7], [0, 7]], "hub", axis="x" if nm == "r" else "x",
                    rot=rot("z", 0 if nm == "r" else 180, [x + (ww / 2 + 1 if nm == "r" else -ww / 2 - 1), yax, z]))
            d.sphere(f"hubh-{nm}{zn}", [x + (ww / 2 + 6 if nm == "r" else -ww / 2 - 6), yax + 30, z], 13, "plastic#1f6e30",
                     soft=True, copies=[[0, -30 + 30 * math.cos(math.radians(a)), 30 * math.sin(math.radians(a))]
                                        for a in (72, 144, 216, 288)])
    # crank axles (chrome) through the wheels
    for z in (85, DD - 85):
        d.tube(f"axle{z}", [[ww, yax, z], [W / 2 - 8, yax, z], [W / 2 - 8, yax + 30, z], [W / 2 + 8, yax + 30, z],
                            [W / 2 + 8, yax, z], [W - ww, yax, z]], 14, "steel", bend=8)
    # the two footboards: left one shifted back (narrow tongue at the back), right one forward (tongue + label at front)
    yb = yax + 28

    def board(id, x0, x1, z0, z1, tongue_back):
        tx0, tx1 = x0 + 15, x0 + 75
        if tongue_back:
            pts = [(x0, z0 + 70), (tx0, z0 + 70), (tx0, z0), (tx1, z0), (tx1, z0 + 70), (x1, z0 + 70), (x1, z1), (x0, z1)]
        else:
            tx0, tx1 = x1 - 75, x1 - 15
            pts = [(x0, z0), (x1, z0), (x1, z1 - 70), (tx1, z1 - 70), (tx1, z1), (tx0, z1), (tx0, z1 - 70), (x0, z1 - 70)]
        from sflib import round_poly
        d.slab(id, "top", P(round_poly(pts, 18)), [yb, yb + 30], "deck", r=8)
    board("board-l", ww + 6, W / 2 - 4, 20, DD - 80, True)
    board("board-r", W / 2 + 4, W - ww - 6, 75, DD - 5, False)
    d.sphere("label", [W - ww - 46, yb + 30, DD - 40], None, "plastic#f2f4f6", radii=[22, 2, 12], soft=True)
    # handrails: an inverted white tube U on each board (legs front/back), black U foam grip over the bend
    for nm, x, z0, z1 in (("l", ww + 22, 95, 230), ("r", W - ww - 22, 165, 300)):
        d.tube(f"rail-{nm}", [[x, yb + 25, z0 + 25], [x, yb + 25, z0], [x, H - 50, z0], [x, H - 50, z1], [x, yb + 25, z1],
                              [x, yb + 25, z1 - 25]], 20, "tube", bend=55)
        d.tube(f"grip-{nm}", [[x, H - 150, z0], [x, H - 32, z0], [x, H - 32, z1], [x, H - 150, z1]], 34, "grip",
               bend=60)
    return d


if __name__ == "__main__":
    main({"xyrt-45": xyrt45, "xyrt-46": xyrt46, "xyrt-50": xyrt50, "xyrt-66": xyrt66})
