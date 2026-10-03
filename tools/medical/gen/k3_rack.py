"""XY-15 sandbag rack and XY-16 sandbag (binding) rack, kinesio-3. Writes xy-15.json and xy-16.json."""
from k3_lib import *

W, Dd, H = 650, 400, 670
TD = 25            # frame tube
XL, XR = 22, W - 22
YL = 285           # lower shelf
ZF, ZB = 368, 28   # front leg, rear leg
TOPF, TOPB = 572, 615   # top shelf height at its front / back (tilted to the front)


def frame(d):
    for nm, x in (("l", XL), ("r", XR)):
        # S side tube: front leg up to the lower shelf, diagonal up and back, hairpin bend into the top shelf rail
        d.tube(f"side-{nm}", [[x, 105, ZF], [x, YL, ZF], [x, 470, 210], [x, TOPB + 38, 18], [x, TOPB + 10, 5],
                               [x, TOPB, 40], [x, TOPF, Dd - 12]], TD, "frame", bend=60)
        d.cyl(f"cap-{nm}", [x, TOPF - 1.5, Dd - 14], [x, TOPF - 4, Dd + 2], TD + 3, "plastic#1d1e20")
        # rear U leg from the lower shelf side rail down to the rear castor
        d.tube(f"rear-{nm}", [[x, YL, 120], [x, YL + 15, 18], [x, 105, ZB]], TD, "frame", bend=40)
        d.caster(f"cas-{nm}", [x, 0, ZF + 12], 64, "rubber#1d1e20", copies=[[0, 0, ZB - ZF - 4]])
        d.cyl(f"stem-{nm}", [x, 80, ZF], [x, 110, ZF], 22, "frame", copies=[[0, 0, ZB - ZF]])
    # rear low cross tube between the rear legs
    d.cyl("rear-x", [XL, 200, ZB + 4], [XR, 200, ZB + 4], 20, "frame")
    # lower shelf: perimeter tube and white slats
    for nm, y0, y1 in (("lo", YL, YL), ("hi", TOPF, TOPB)):
        z0, z1 = 40, Dd - 25
        def yz(z): return y0 + (y1 - y0) * (z1 - z) / (z1 - z0)
        d.cyl(f"{nm}-f", [XL, yz(z1), z1], [XR, yz(z1), z1], 20, "frame")
        d.cyl(f"{nm}-b", [XL, yz(z0), z0], [XR, yz(z0), z0], 20, "frame")
        if nm == "lo":
            d.cyl(f"{nm}-sl", [XL, y0, z0], [XL, y0, z1], 18, "frame", copies=[[XR - XL, 0, 0]])
        n = 6
        for k in range(n):
            z = z0 + 25 + (z1 - z0 - 50) * k / (n - 1)
            d.box(f"{nm}-slat{k}", [XL + 10, yz(z) - 9, z - 14, XR - 10, yz(z) - 2, z + 14], "frame", r=2)
    # small blue label on the top front rail
    d.decal("label", [W - 120, TOPF, Dd - 25 + 10.5], [70, 14], "gloss#2f62c4", face="front", soft=True)


def shelf_tilt(y_front, y_back, z):
    z0, z1 = 40, Dd - 25
    return y_front + (y_back - y_front) * (z1 - z) / (z1 - z0)


def xy15():
    # (review) the sacks were smooth boxes that read as jerrycans: now soft pear-shaped lofts in satin PU, the belly
    # low at the front, narrowing to a gathered drawstring neck with a chrome ring at the back top; the lower tier is
    # lower and longer to the front (lying more on its side), the upper taller (photo)
    d = D("xy-15", [W, Dd, H], {"frame": "plastic#f0f1f2", "bag": "leather#92c843", "bagd": "leather#6aa52a"})
    frame(d)
    for tier, yb, tilt, hh0, zf in (("lo", YL - 2, 0, 128, Dd - 10), ("hi", (TOPF + TOPB) / 2 - 5, 7.4, 150, Dd - 30)):
        n = 9
        bw = (XR - XL - 30) / n
        for k in range(n):
            x0 = XL + 15 + k * bw
            hh = hh0 + (k * 37 % 3) * 14
            lean = (-9 if k % 2 else 8) + (k % 3) * 3
            ab = [x0 + bw / 2, yb, Dd / 2]
            tr = dict(rot={"axis": "z", "deg": lean, "about": ab}, rots=[{"axis": "y", "deg": (k * 53 % 17) - 8, "about": ab},
                                                                   {"axis": "x", "deg": tilt, "about": ab}])
            # soft pear-shaped sack (loft): full round belly low at the front, narrowing to the neck at the back top
            cx = x0 + bw / 2
            zc = (50 + zf) / 2
            dd = zf - 50
            bl = 1.0 + 0.12 * ((k * 7) % 3)
            d.loft(f"{tier}-bag{k}", [sec(yb, bw * 0.95, dd * 0.92, bw * 0.4, cx, zc + 6),
                                      sec(yb + hh * 0.3, bw * 1.12 * bl, dd, bw * 0.5, cx, zc + 12),
                                      sec(yb + hh * 0.62, bw * 1.0, dd * 0.86, bw * 0.45, cx + (lean * 0.6), zc - 2),
                                      sec(yb + hh * 0.84, bw * 0.88, dd * 0.62, bw * 0.4, cx, 140),
                                      sec(yb + hh * 0.97, 62, 58, 28, cx, 100)], "bag", **tr)
            # gathered neck at the back top: a short cone of puckered cloth and the chrome ring round it
            d.add(f"{tier}-neck{k}", "lathe", "bag", at=[x0 + bw / 2, yb + hh - 10, 95],
                  profile=[[30, 0], [20, 18], [14, 34], [22, 46], [0, 50]], **tr)
            d.tube(f"{tier}-ring{k}", ring(x0 + bw / 2, yb + hh + 26, 95, 20, 14, "xz", 12), 5, "chrome", soft=True, **tr)
    d.save()


def xy16():
    # (review) photo: flat cuffs (~32 thick) in a dark camo — black dominant with teal and grey-white patches — and thin
    # black straps lying back over the rear ends, not upright loops
    d = D("xy-16", [W, Dd, H], {"frame": "plastic#f0f1f2", "teal": "fabric#2aa3c4", "dark": "fabric#1b1d20",
                                 "grey": "fabric#9aa3a8", "light": "fabric#d9e2e6"})
    frame(d)
    for tier, yb, tilt in (("lo", YL + 2, 0), ("hi", (TOPF + TOPB) / 2 - 2, 7.4)):
        n = 7
        cw = (XR - XL - 24) / n
        ab = [W / 2, yb, Dd / 2]
        tr = {"rot": {"axis": "x", "deg": tilt, "about": ab}} if tilt else {}
        for k in range(n):
            x0 = XL + 12 + k * cw
            npk = 5
            pl = (Dd - 80) / npk
            for j in range(npk):
                m = ["dark", "teal", "dark", "grey", "teal", "dark"][(j + 2 * k) % 6]
                z0, z1 = 50 + j * pl + 2, 50 + (j + 1) * pl - 2
                d.box(f"{tier}-p{k}-{j}", [x0 + 3, yb, z0, x0 + cw - 3, yb + 32, z1], m, r=12, puff=6, **tr)
                # camo patch on each pocket
                pm = {"dark": "teal", "teal": "dark", "grey": "light"}[m]
                d.add(f"{tier}-blot{k}-{j}", "decal", pm, at=[x0 + cw * (0.35 + 0.3 * ((j + k) % 2)), yb + 38, (z0 + z1) / 2 + 4],
                      size=[cw * 0.42, pl * 0.45], face="top", soft=True, **tr)
            # thin black Velcro strap out of the back end, lying back and curling up a little
            sx = x0 + cw / 2
            d.strap(f"{tier}-strap{k}", [[sx, yb + 20, 54], [sx, yb + 34 + (k % 2) * 10, 30], [sx, yb + 50 + (k % 2) * 12, 12]],
                    [32, 3], "dark", bend=20, soft=True, **tr)
    d.save()

xy15()
xy16()
