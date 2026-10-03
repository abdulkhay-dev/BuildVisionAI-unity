"""Rail items of batch pediatric-4: XYRT-6 children's parallel bars with correction plate, XYRT-7 training stairs.
Length along x, front = +z."""
from pd4lib import *

RAIL = "plastic#9fc4ea"
POST = "plastic#eef0f1"


def knob(d, id, at, face_dir, copies=None):
    """Black star knob on a post: stem + knob along z (face_dir +1 front, -1 back) or x (face_dir 'x+', 'x-')."""
    x, y, z = at
    if face_dir in (1, -1):
        d.cyl(id + "-s", [x, y, z], [x, y, z + 32 * face_dir], 10, "plastic#2a2b2d", copies=copies)
        d.cyl(id, [x, y, z + 24 * face_dir], [x, y, z + 44 * face_dir], 34, "plastic#1d1e20", sides=10, copies=copies)
    else:
        s = 1 if face_dir == "x+" else -1
        d.cyl(id + "-s", [x, y, z], [x + 32 * s, y, z], 10, "plastic#2a2b2d", copies=copies)
        d.cyl(id, [x + 24 * s, y, z], [x + 44 * s, y, z], 34, "plastic#1d1e20", sides=10, copies=copies)


def xyrt6():
    L, DD, H = 2900, 610, 900
    d = D("xyrt-6", [L, DD, H], {"rail": RAIL, "post": POST, "edge": "plastic#e3c7b7", "top": "plastic#a8b2c3",
                                 "wood": "wood#e8c690", "inner": "metal#b99c92"})
    # base board: beige laminate edge, ramped (bevelled) ends, blue-grey top
    d.slab("base", "front", P([(0, 0), (L, 0), (L, 8), (L - 120, 36), (120, 36), (0, 8)]), [0, DD], "edge", r=3)
    d.box("base-top", [124, 35, 4, L - 124, 41, DD - 4], "top", r=2)
    d.box("label", [520, 14, DD + 0.5, 640, 26, DD + 1.5], "plastic#3456a8", soft=True)
    # wooden correction plate: wedge 400 wide, high (110) at the front, 15 deg slope to the back
    x0, x1, zb, zf = 500, 2400, 95, 495
    xr = x1 - 160                         # photo: the right end of the plate is a ramp down to the base
    d.slab("plate", "side", P([(zb, 41), (zf, 41), (zf, 82), (zb + 12, 150), (zb, 148)]), [x0, xr + 2], "wood", r=6)
    n = 5
    for k in range(n):                    # the ramp in strips across the plate, each at its own wedge height
        za, zb_ = zb + (zf - zb) * k / n, zb + (zf - zb) * (k + 1) / n
        h = 82 + (150 - 82) * (zf - (za + zb_) / 2) / (zf - zb)
        d.slab(f"ramp{k}", "front", P([(xr, 41), (x1, 41), (x1, 47), (xr, h)]), [za, zb_], "wood", r=3)
    # posts: white outer tube, brownish inner tube, knob, clamp bracket, rails
    zr = (85, DD - 85)
    for xp in (420, L - 420):
        for zi, zp in enumerate(zr):
            front = zi == 1
            nm = f"{xp}-{zi}"
            d.lathe(f"flange-{nm}", [xp, 41, zp], [[0, 0], [38, 0], [38, 6], [28, 14], [0, 14]], "post")
            d.cyl(f"post-{nm}", [xp, 41, zp], [xp, 620, zp], 50, "post")
            d.cyl(f"inner-{nm}", [xp, 610, zp], [xp, H - 50, zp], 36, "inner")
            d.cyl(f"collar-{nm}", [xp, 600, zp], [xp, 628, zp], 56, "post")
            knob(d, f"knob-{nm}", [xp, 560, zp + (25 if front else -25)], 1 if front else -1)
            d.box(f"clamp-{nm}", [xp - 45, H - 62, zp - 22, xp + 45, H - 38, zp + 22], "inner", r=6)
            if front:
                d.cyl(f"lever-{nm}", [xp - 40, H - 50, zp], [xp - 120, H - 52, zp + 20], 14, "plastic#1d1e20")
                d.sphere(f"lever-ball-{nm}", [xp - 122, H - 52, zp + 20], 24, "plastic#1d1e20")
    # light-blue round handrails, ends turned down
    for zi, zp in enumerate(zr):
        d.tube(f"rail{zi}", [[25, H - 85, zp], [25, H - 20, zp], [L - 25, H - 20, zp], [L - 25, H - 85, zp]], 40, "rail",
               bend=40)
    return d


def xyrt7():
    L, DD, H = 3370, 670, 1430
    d = D("xyrt-7", [L, DD, H], {"rail": RAIL, "post": POST, "side": "plastic#dcc6a8", "tread": "plastic#bccde0",
                                 "trim": "metal#c4c8cc"})
    z0, z1 = 40, DD - 40
    xa, xb = 150, L - 150                 # body ends
    lx0, lx1 = 1385, 1985                 # landing
    rise, n = 120, 4
    run = (lx0 - xa) / n                  # ~309
    # landing block
    d.box("landing", [lx0, 0, z0, lx1, 5 * rise, z1], "side", r=3)
    d.box("landing-top", [lx0 + 2, 5 * rise - 2, z0 + 2, lx1 - 2, 5 * rise + 6, z1 - 2], "tread", r=3)
    # the two flights (mirrored): a plinth tread and 4 steps, side faces light wood, treads blue-grey
    for side in ("l", "r"):
        for k in range(n + 1):
            yk = rise * (k + 1) if k < n else None
            if k == n: break
            if side == "l":
                xs, xe = xa + k * run, lx0
            else:
                xs, xe = lx1, xb - k * run
            d.box(f"step-{side}{k}", [xs, rise * k, z0, xe, rise * (k + 1), z1], "side", r=2)
            xr = xs if side == "l" else xe
            d.box(f"riser-{side}{k}", [xr - 2, rise * k + 2, z0 + 2, xr + 2, rise * (k + 1), z1 - 2], "tread", r=1)
            d.box(f"tread-{side}{k}", [xs + 2, rise * (k + 1) - 2, z0 + 2, xe - 2, rise * (k + 1) + 6, z1 - 2], "tread",
                  r=3)
    d.box("riser-land", [lx0 - 2, 4 * rise, z0 + 2, lx0 + 2, 5 * rise, z1 - 2], "tread", r=1, copies=[[lx1 - lx0, 0, 0]])
    # aluminium trims at the module joints
    for x in (lx0, lx1):
        d.box(f"trim{x}", [x - 4, 0, z1 - 2, x + 4, 5 * rise, z1 + 3], "trim", r=1, copies=[[0, 0, -(z1 - z0) - 1]])
    # handrails: a sloped rail per flight and side, a horizontal rail over the landing, white posts with black knobs
    top = H - 20                       # landing rail centre
    for zi, zp in enumerate((z0 + 20, z1 - 20)):
        front = zi == 1
        fd = 1 if front else -1
        d.tube(f"rail-land{zi}", [[lx0 - 60, top, zp], [lx1 + 60, top, zp]], 40, "rail")
        for xp in (lx0 + 40, lx1 - 40):
            d.cyl(f"post-land{zi}-{xp}", [xp, 5 * rise, zp], [xp, top - 18, zp], 32, "post")
            knob(d, f"knob-land{zi}-{xp}", [xp, top - 120, zp + 14 * fd], fd)
        for side in ("l", "r"):
            sgn = 1 if side == "l" else -1
            xe0 = 60 if side == "l" else L - 60          # low end of the rail
            xe1 = lx0 - 90 if side == "l" else lx1 + 90  # high end
            y0, y1 = 900, top - 50
            slope = (y1 - y0) / (xe1 - xe0)
            d.tube(f"rail-{side}{zi}", [[xe0, y0 - 70, zp], [xe0, y0, zp], [xe1, y1, zp]], 40, "rail", bend=40)
            for f in (0.08, 0.55):
                xp = xe0 + (xe1 - xe0) * f + sgn * 40
                yr = y0 + slope * (xp - xe0)
                # tread height under the post
                k = int(((xp - xa) / run) if side == "l" else ((xb - xp) / run))
                yb = rise * (max(0, min(k, n - 1)) + 1)
                d.cyl(f"post-{side}{zi}-{f}", [xp, yb, zp], [xp, yr - 18, zp], 32, "post")
                knob(d, f"knob-{side}{zi}-{f}", [xp, yr - 130, zp + 14 * fd], fd)
    return d


if __name__ == "__main__":
    main({"xyrt-6": xyrt6, "xyrt-7": xyrt7})
