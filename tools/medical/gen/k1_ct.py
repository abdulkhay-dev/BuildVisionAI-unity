"""xy-ct-iv / xy-ct-iii: round ADL training table on a telescopic column and a 3-arm star base.
Domed white shell with 3 arched openings (front, +-120 deg) between the base arms; iv has the screen tower."""
import math, sys
from k1lib import *

C = 575
R, RI = 520, 494          # shell outer / inner radius at the top of the wall (under the lid)
RB = 552                  # outer radius at the foot: the wall flares outward ~7 deg (photo)
FLARE = math.degrees(math.atan((RB - R) / 245.0))
Y0, YO, YL = 470, 710, 840  # skirt top, opening top, lid top
HALF = math.degrees(math.asin(250 / R))
MATS = {"white": "gloss#f3f4f5", "skirt": "plastic#bfc3c8", "column": "plastic#c8ccd2", "base": "plastic#5a5f66",
        "inner": "plastic#4a4f57", "mod": "plastic#c9ccd1", "face": "plastic#3a3f46", "chrome": "chrome",
        "black": "plastic#1d1e20", "ring": "plastic#b9bdc2", "wing": "plastic#8a8d93", "red": "gloss#d32a22",
        "yellow": "plastic#f2c230"}


def P(r, deg):
    a = math.radians(deg)
    return C + r * math.sin(a), C + r * math.cos(a)


def sector(a0, a1, ro, ri, n=14):
    pts = [P(ro, a0 + (a1 - a0) * i / n) for i in range(n + 1)] + [P(ri, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
    return "M " + " L ".join(f"{x:.1f} {z:.1f}" for x, z in pts) + " Z"


def flared(az):
    """Turns of a wall piece drawn facing +z at the top radius: tilt the foot outward, then turn to azimuth az."""
    az = (az + 180.0) % 360.0 - 180.0   # keep the turn in (-180, 180]
    return rot("x", -FLARE, [C, YO + 5, C + R]), [rot("y", round(az, 2), [C, 0, C])]


def wall(d, tag, a0, a1, n, widen0=0.0, widen1=0.0):
    """A flared wall sector a0..a1 (deg) of n flat tilted facets; the end facets narrow toward the foot by widen*
    (mm), so the openings get wider at the bottom as in the photo."""
    dl = (a1 - a0) / n
    L = 245.0 / math.cos(math.radians(FLARE))
    yt, yb = YO + 5, YO + 5 - L
    # the end facets are two steps wide, so their foot can narrow by widen* without crossing over
    segs = [(a0, a0 + 2 * dl)] + [(a0 + (2 + k) * dl, a0 + (3 + k) * dl) for k in range(n - 4)] + [(a1 - 2 * dl, a1)]
    for k, (s0, s1) in enumerate(segs):
        a, h = (s0 + s1) / 2, (s1 - s0) / 2
        ht = R * math.tan(math.radians(h)) + 1.5
        hb = RB * math.tan(math.radians(h)) + 1.5
        bl = -hb + (widen0 if k == 0 else 0)
        br = hb - (widen1 if k == len(segs) - 1 else 0)
        out = f"M {C - ht:.1f} {yt:.1f} L {C + ht:.1f} {yt:.1f} L {C + br:.1f} {yb:.1f} L {C + bl:.1f} {yb:.1f} Z"
        r0, rr = flared(a)
        d.slab(f"wall-{tag}-{k}", "front", out, [C + R - 26, C + R], "white", r=1, rot=r0, rots=rr)


def opening_parts(d, th, tag, modules):
    """Fillets of the arch corners and the modules seen through the opening at azimuth th (0 = front)."""
    T = rot("y", th, [C, 0, C]) if th else None
    for s in (-1, 1):
        # corner fillet drawn in the plane of the wall's end facet (opening edge at azimuth th + s*HALF)
        x = C
        out = f"M {x} {YO - 95} L {x} {YO + 5} L {x - s * 95} {YO + 5} Q {x} {YO + 5} {x} {YO - 95} Z"
        r0, rr = flared(th + s * HALF)
        d.slab(f"fillet-{tag}-{'l' if s < 0 else 'r'}", "front", out, [C + R - 26, C + R - 0.5], "white", r=2,
               rot=r0, rots=rr)
    for i, m in enumerate(modules):
        m(d, f"{tag}-{i}", T)


# --- modules (drawn for the front opening, turned for the others)
def wheel_module(d, t, T):
    d.box(f"m-wheel-box-{t}", [C - 235, Y0 + 10, C + 320, C - 110, Y0 + 190, C + 420], "mod", r=10, rot=T)
    d.tube(f"m-wheel-{t}", [[C - 172 + 88 * math.cos(math.radians(a)), Y0 + 120 + 88 * math.sin(math.radians(a)), C + 452]
                            for a in range(0, 361, 30)], 20, "white", bend=30, rot=T)
    d.cyl(f"m-wheel-spoke-{t}", [C - 255, Y0 + 120, C + 452], [C - 89, Y0 + 120, C + 452], 16, "white", rot=T)
    d.cyl(f"m-wheel-hub-{t}", [C - 172, Y0 + 120, C + 420], [C - 172, Y0 + 120, C + 462], 34, "chrome", rot=T)


def lever_module(d, t, T):
    d.box(f"m-lever-box-{t}", [C - 70, Y0 + 10, C + 300, C + 95, Y0 + 225, C + 440], "mod", r=10, rot=T)
    d.box(f"m-lever-face-{t}", [C - 50, Y0 + 30, C + 438, C + 75, Y0 + 205, C + 444], "face", r=6, rot=T)
    d.cyl(f"m-lever-rose-{t}", [C - 10, Y0 + 125, C + 444], [C - 10, Y0 + 125, C + 470], 36, "chrome", rot=T)
    d.bar(f"m-lever-{t}", [C - 10, Y0 + 125, C + 466], [C + 140, Y0 + 125, C + 466], [22, 22], "chrome", r=10, rot=T)


def clamp_module(d, t, T):
    d.box(f"m-clamp-base-{t}", [C + 120, Y0 + 10, C + 330, C + 240, Y0 + 70, C + 460], "white", r=10, rot=T)
    d.box(f"m-clamp-slot-{t}", [C + 140, Y0 + 30, C + 459, C + 222, Y0 + 44, C + 462], "face", r=4, rot=T)
    d.cyl(f"m-clamp-screw-{t}", [C + 180, Y0 + 70, C + 380], [C + 180, Y0 + 175, C + 380], 26, "chrome", rot=T)
    d.box(f"m-clamp-bar-{t}", [C + 120, Y0 + 82, C + 365, C + 240, Y0 + 100, C + 395], "face", r=5, rot=T)


def arrow_module(d, t, T):
    d.box(f"m-arrow-box-{t}", [C - 80, Y0 + 10, C + 320, C + 90, Y0 + 220, C + 440], "mod", r=10, rot=T)
    # light face with a 4-colour arrow pad: triangles pointing out (blue up, green right, red down, yellow left)
    d.box(f"m-arrow-face-{t}", [C - 60, Y0 + 30, C + 438, C + 70, Y0 + 200, C + 444], "plastic#e4e6e9", r=6, rot=T)
    cx, cy = C + 5, Y0 + 115
    for nm, ux, uy, col in (("u", 0, 1, "gloss#2f7fd0"), ("r", 1, 0, "gloss#3aa84a"), ("d", 0, -1, "gloss#d3262a"),
                            ("l", -1, 0, "gloss#f0c419")):
        vx, vy = -uy, ux
        p0 = (cx + ux * 24 + vx * 24, cy + uy * 24 + vy * 24)
        p1 = (cx + ux * 24 - vx * 24, cy + uy * 24 - vy * 24)
        p2 = (cx + ux * 58, cy + uy * 58)
        tri = f"M {p0[0]:.1f} {p0[1]:.1f} L {p1[0]:.1f} {p1[1]:.1f} L {p2[0]:.1f} {p2[1]:.1f} Z"
        d.slab(f"m-arrow-{nm}-{t}", "front", tri, [C + 443, C + 448], col, r=1, rot=T)
    d.cyl(f"m-arrow-c-{t}", [cx, cy, C + 443], [cx, cy, C + 452], 34, "white", rot=T)
    d.box(f"m-arrow-white-{t}", [C - 230, Y0 + 10, C + 340, C - 110, Y0 + 100, C + 460], "white", r=10, rot=T)


def knob_module(d, t, T):
    d.box(f"m-knob-box-{t}", [C - 150, Y0 + 10, C + 310, C - 10, Y0 + 200, C + 430], "mod", r=10, rot=T)
    d.box(f"m-knob-face-{t}", [C - 132, Y0 + 28, C + 428, C - 28, Y0 + 182, C + 434], "face", r=6, rot=T)
    d.sphere(f"m-knob-{t}", [C - 80, Y0 + 105, C + 450], 46, "chrome", rot=T)
    d.box(f"m-keypad-box-{t}", [C + 30, Y0 + 10, C + 320, C + 160, Y0 + 190, C + 430], "white", r=10, rot=T)
    d.box(f"m-keypad-face-{t}", [C + 48, Y0 + 28, C + 428, C + 142, Y0 + 172, C + 434], "face", r=6, rot=T)
    d.box(f"m-keypad-key-{t}", [C + 60, Y0 + 140, C + 433, C + 80, Y0 + 158, C + 437], "white", r=3, rot=T,
          repeat={"n": 3, "step": [28, 0, 0]}, copies=[[0, -36, 0], [0, -72, 0]])


def build(id, screen):
    H = 1215 if screen else 845
    d = D(id, [1150, 1150, H], MATS)
    # --- graphite 3-arm star base with castors (arms at +-60 and 180 deg, between the openings)
    for i, th in enumerate((60, -60, 180)):
        d.slab(f"base-arm-{i}", "top", None, None, "base", r=22, box=[C - 75, 80, C, C + 75, 172, C + 440],
               radii=[60], rot=rot("y", th, [C, 0, C]))
        x, z = P(395, th)
        d.add(f"castor-{i}", "caster", "rubber#d4d6d8", at=[x, 0, z], d=70)
    d.lathe("base-hub", [C, 80, C], [[0, 0], [150, 0], [150, 92], [0, 92]], "base")
    # --- light-grey column with groove lines, black motor box under the table
    d.box("column", [C - 92, 170, C - 80, C + 92, Y0 - 25, C + 80], "column", r=10)
    d.box("column-groove", [C - 40, 190, C + 79, C - 36, Y0 - 40, C + 82], "ring", soft=True, copies=[[76, 0, 0]])
    d.box("motor-box", [C + 85, Y0 - 140, C - 40, C + 175, Y0 - 30, C + 60], "black", r=8)
    d.box("table-frame", [C - 200, Y0 - 40, C - 200, C + 200, Y0 - 30, C + 200], "base", r=6)
    # --- skirt plate, inner dark drum + turntable, shell walls between the openings, domed lid
    d.lathe("skirt", [C, Y0 - 30, C], [[0, 0], [575, 0], [575, 30], [0, 30]], "skirt", sides=64)
    d.lathe("inner", [C, Y0, C], [[0, 0], [300, 0], [300, YO - Y0 + 5], [0, YO - Y0 + 5]], "inner", sides=48)
    for i, th in enumerate((0, 120, 240)):
        d.slab(f"cavity-{i}", "top", sector(th - HALF - 4, th + HALF + 4, 300, 280), [Y0, YO], "inner", r=2)
        d.slab(f"cavity-side-{i}", "top", sector(th - HALF - 1, th - HALF + 1, RI, 300, n=2), [Y0, YO], "inner", r=2)
        d.slab(f"cavity-side2-{i}", "top", sector(th + HALF - 1, th + HALF + 1, RI, 300, n=2), [Y0, YO], "inner", r=2)
    d.lathe("turntable", [C, Y0, C], [[0, 0], [505, 0], [505, 8], [0, 8]], "mod", sides=48)
    for i, th in enumerate((0, 120, 240)):
        wall(d, str(i), th + HALF, th + 120 - HALF, 22, widen0=34, widen1=34)
    # domed lid: flat top to r ~400, a broad rounded shoulder down to the wall
    d.lathe("lid", [C, YO, C], [[0, 0], [R, 0], [R, 15], [R - 8, 45], [R - 25, 80], [R - 55, 108], [R - 90, 124],
                                [R - 120, 130], [0, 130]], "white", sides=96)
    # top: grey ring (and the logo on iii)
    d.lathe("top-ring", [C, YL, C], [[340, 0], [365, 0], [365, 1.5], [340, 1.5], [340, 0]], "ring", sides=64, caps=False)
    # --- openings: arch fillets + modules
    if screen:
        front = [wheel_module, lever_module, clamp_module]
    else:
        front = [arrow_module, clamp_module]
    opening_parts(d, 0, "f", front)
    opening_parts(d, 120, "r", [knob_module])
    opening_parts(d, 240, "l", [knob_module])
    # yellow labels on the skirt by the openings, e-stop boxes under the skirt edge left and right
    for th in (-32, 32, 88, 152, 208, 272):
        x, z = P(564, th)
        d.box(f"label-{th}", [x - 8, Y0, z - 14, x + 8, Y0 + 1.5, z + 14], "yellow", soft=True,
              rot=rot("y", th, [x, 0, z]))
    for nm, th in (("l", -95), ("r", 95)):
        x, z = P(545, th)
        T = rot("y", th, [x, 0, z])
        d.box(f"estop-box-{nm}", [x - 50, Y0 - 75, z - 30, x + 50, Y0 - 30, z + 30], "base", r=6, rot=T)
        d.cyl(f"estop-{nm}", [x, Y0 - 52, z + 30], [x, Y0 - 52, z + 44], 24, "red", rot=T)
    if screen:
        # --- screen tower: white post, white head with the screen, grey side wings angled back
        d.box("post", [C - 120, YL - 10, C - 80, C + 120, 985, C + 80], "white", r=22)
        d.box("head", [C - 160, 975, C - 30, C + 160, 1215, C + 40], "white", r=18)
        d.add("screen", "screen", "black", box=[C - 140, 995, C + 34, C + 140, 1195, C + 42], r=6, face="front", bezel=6)
        d.box("wing-l", [C - 212, 982, C - 40, C - 160, 1208, C + 18], "wing", r=12, rot=rot("y", -28, [C - 160, 0, C]))
        d.box("wing-r", [C + 160, 982, C - 40, C + 212, 1208, C + 18], "wing", r=12, rot=rot("y", 28, [C + 160, 0, C]))
    else:
        d.lathe("logo-ring", [C, YL, C], [[230, 0], [244, 0], [244, 1.5], [230, 1.5], [230, 0]], "ring", sides=48, caps=False)
        d.box("logo-h", [C - 170, YL, C - 40, C + 170, YL + 2, C + 40], "ring", r=20, soft=True)
        d.box("logo-v", [C - 42, YL, C - 150, C + 42, YL + 2, C + 150], "ring", r=20, soft=True)
    return d


if __name__ == "__main__":
    for id in sys.argv[1:] or ["xy-ct-iv", "xy-ct-iii"]:
        build(id, id == "xy-ct-iv").save()
