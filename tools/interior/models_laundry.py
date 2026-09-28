"""Laundry (reference tile «Прачечная»): white front-loading washer and matching dryer, counter run with a sink and an
open bay for the two machines, wood wall cabinets with an open shelf and LED, lidded laundry basket."""
import math

from kit import Kit


def _front_loader(k, dryer):
    """White front loader 0.6 × 0.6 × 0.85 (back at y = 0): body, control panel with a drawer, display and a chrome
    knob, round door (brushed ring, chrome lip, dark glass), service hatch and plinth. The dryer swaps the panel layout
    (water-tank drawer, knob left of a wide display) and has a flat door glass."""
    W, D, H = 0.6, 0.58, 0.85
    fy = -D                                    # front face
    k.box("body", (0, -D / 2, 0.015 + (H - 0.015) / 2), (W - 0.004, D - 0.01, H - 0.015), r=0.014, seg=3)
    for sx in (-1, 1):
        for sy in (-0.05, -D + 0.05):
            k.cyl("trim", (sx * (W / 2 - 0.05), sy, 0.01), 0.018, 0.02, seg=12)
    # control panel: its own face split off by a dark line
    pz0, pz1 = 0.715, H - 0.012
    k.box("panel", (0, fy + 0.002, (pz0 + pz1) / 2), (W - 0.03, 0.006, pz1 - pz0), r=0.004, seg=2)
    k.box("trim", (0, fy + 0.004, pz0 - 0.003), (W - 0.03, 0.006, 0.004))
    pc = (pz0 + pz1) / 2
    if not dryer:
        # detergent drawer on the left with a finger pull, display centre-right, knob right
        k.box("panel", (-0.18, fy - 0.003, pc), (0.2, 0.012, 0.1), r=0.005, seg=2)
        k.box("trim", (-0.18, fy - 0.0095, pc - 0.034), (0.1, 0.002, 0.012), r=0.001, seg=1)
        k.box("display", (0.04, fy - 0.001, pc + 0.005), (0.13, 0.004, 0.05), r=0.004, seg=2)
        for i in range(4):
            k.cyl("knob", (-0.005 + i * 0.03, fy - 0.002, pc - 0.04), 0.006, 0.006, seg=10, rot=(90, 0, 0))
        kx = 0.205
    else:
        # water-tank drawer on the left, knob left of centre, wide display on the right
        k.box("panel", (-0.2, fy - 0.003, pc), (0.16, 0.012, 0.1), r=0.005, seg=2)
        k.box("trim", (-0.14, fy - 0.0095, pc), (0.012, 0.002, 0.06), r=0.001, seg=1)
        k.box("display", (0.15, fy - 0.001, pc + 0.002), (0.2, 0.004, 0.062), r=0.004, seg=2)
        for i in range(3):
            k.cyl("knob", (0.1 + i * 0.05, fy - 0.002, pc - 0.043), 0.006, 0.006, seg=10, rot=(90, 0, 0))
        kx = -0.03
    k.cyl("trim", (kx, fy - 0.001, pc), 0.04, 0.004, seg=32, rot=(90, 0, 0))
    k.cyl("knob", (kx, fy - 0.014, pc), 0.031, 0.026, seg=32, r=0.004, rot=(90, 0, 0))
    k.box("trim", (kx, fy - 0.0275, pc + 0.018), (0.004, 0.002, 0.016))      # pointer mark
    # door
    dz = 0.40
    k.cyl("ring", (0, fy - 0.017, dz), 0.232, 0.034, seg=64, r=0.012, rot=(90, 0, 0))
    k.torus("knob", (0, fy - 0.036, dz), 0.178, 0.011, seg=64, rseg=10, rot=(90, 0, 0))
    if dryer:
        k.cyl("door_glass", (0, fy - 0.036, dz), 0.17, 0.006, seg=48, rot=(90, 0, 0))
    else:
        k.lathe("door_glass", (0, fy - 0.03, dz), [(0.172, 0.0), (0.16, 0.014), (0.12, 0.03), (0.06, 0.038), (0.0, 0.04)],
                seg=48, rot=(90, 0, 0))
    k.box("trim", (0.2, fy - 0.03, dz), (0.03, 0.02, 0.07), r=0.008, seg=2)      # door grip
    # service hatch and plinth line
    k.box("panel", (-0.22, fy - 0.001, 0.085), (0.1, 0.004, 0.08), r=0.003, seg=1)
    k.box("trim", (0, fy + 0.004, 0.035), (W - 0.03, 0.006, 0.004))


def washer_front_white(e):
    """White front-loading washer 0.6 × 0.6 × 0.85: detergent drawer, display and chrome programme knob, round door with
    a domed dark glass. Pivot on the floor at the wall."""
    k = Kit(e["id"])
    _front_loader(k, dryer=False)
    return k.finish(e, {"body": "gloss_white", "trim": "charcoal", "panel": "soft_white", "display": "screen",
                        "knob": "chrome", "ring": "white_metal", "door_glass": "black_glass"}, pivot="back")


def dryer_front_white(e):
    """Matching white tumble dryer 0.6 × 0.6 × 0.85: water-tank drawer, knob left of a wide display, flat dark door
    glass. Pivot on the floor at the wall."""
    k = Kit(e["id"])
    _front_loader(k, dryer=True)
    return k.finish(e, {"body": "gloss_white", "trim": "charcoal", "panel": "soft_white", "display": "screen",
                        "knob": "chrome", "ring": "white_metal", "door_glass": "black_glass"}, pivot="back")


def laundry_counter_run(e):
    """Laundry counter run 1.8 × 0.62, h 0.9: stone worktop over an open bay 1.2 wide for a washer and a dryer
    side by side, a 0.58 two-door sink base on the right with an undermount steel sink and a black gooseneck faucet.
    Pivot on the floor at the wall."""
    k = Kit(e["id"])
    W, D, H, T = 1.8, 0.62, 0.9, 0.03
    x0, x1 = -W / 2, W / 2
    xs = x1 - 0.58                              # sink base from xs to x1; bay from x0 + gable to xs
    cd = 0.58                                   # carcass depth
    # end gable of the bay (carries the worktop), carcass of the sink base with a recessed plinth
    k.box("carcass", (x0 + 0.01, -cd / 2, (H - T) / 2), (0.02, cd, H - T), r=0.002, seg=1)
    k.box("carcass", ((xs + x1) / 2, -cd / 2 + 0.01, (H - T + 0.1) / 2), (x1 - xs, cd - 0.02, H - T - 0.1), r=0.002, seg=1)
    k.box("plinth", ((xs + x1) / 2, -cd / 2 + 0.03, 0.05), (x1 - xs - 0.02, cd - 0.06, 0.1))
    # two doors with shadow gaps, grip channel under the worktop
    g = 0.005
    dw = (x1 - xs) / 2
    fz0, fz1 = 0.1 + g, H - T - 0.035
    for i in range(2):
        cx = xs + dw * (i + 0.5)
        k.box("fronts", (cx, -cd - 0.009, (fz0 + fz1) / 2), (dw - g, 0.018, fz1 - fz0), r=0.002, seg=1)
    k.box("plinth", ((xs + x1) / 2, -cd + 0.005, H - T - 0.018), (x1 - xs - 0.004, 0.02, 0.032))
    # worktop round an undermount sink opening
    sx, sw, sd = (xs + x1) / 2, 0.42, 0.36
    sy = -D / 2 - 0.02
    ox0, ox1, oy0, oy1 = sx - sw / 2, sx + sw / 2, sy - sd / 2, sy + sd / 2
    tz = H - T / 2
    k.box("top", ((x0 + ox0) / 2, -D / 2, tz), (ox0 - x0, D, T), r=0.003, seg=2)
    k.box("top", ((ox1 + x1) / 2, -D / 2, tz), (x1 - ox1, D, T), r=0.003, seg=2)
    k.box("top", (sx, (-D + oy0) / 2, tz), (sw + 0.002, oy0 + D, T), r=0.003, seg=2)
    k.box("top", (sx, oy1 / 2, tz), (sw + 0.002, -oy1, T), r=0.003, seg=2)
    # sink bowl: walls, bottom, drain
    bd, st = 0.19, 0.008
    bz = H - T - bd / 2
    k.box("sink", (sx, sy, H - T - bd), (sw, sd, st), r=0.003, seg=1)
    k.box("sink", (ox0 + st / 2, sy, bz), (st, sd, bd), r=0.002, seg=1)
    k.box("sink", (ox1 - st / 2, sy, bz), (st, sd, bd), r=0.002, seg=1)
    k.box("sink", (sx, oy0 + st / 2, bz), (sw, st, bd), r=0.002, seg=1)
    k.box("sink", (sx, oy1 - st / 2, bz), (sw, st, bd), r=0.002, seg=1)
    k.cyl("faucet", (sx, sy, H - T - bd + st / 2 + 0.001), 0.035, 0.003, seg=24)
    # gooseneck faucet behind the sink
    fx, fy, fz = sx, oy1 + 0.05, H
    k.cyl("faucet", (fx, fy, fz + 0.008), 0.028, 0.016, seg=24, r=0.003)
    pts = [(fx, fy, fz + 0.01), (fx, fy, fz + 0.3)]
    R = 0.1
    for i in range(1, 13):
        a = i / 12 * math.pi
        pts.append((fx, fy - R + R * math.cos(a), fz + 0.3 + R * math.sin(a)))
    pts.append((fx, fy - 2 * R, fz + 0.26))
    k.tube("faucet", pts, 0.012, seg=12)
    k.box("faucet", (fx + 0.035, fy, fz + 0.1), (0.05, 0.012, 0.012), r=0.004, seg=2, rot=(0, -15, 0))
    return k.finish(e, {"carcass": "grey_oak_veneer", "fronts": "grey_oak_veneer", "plinth": "charcoal",
                        "top": "microcement#e6ddd0", "sink": "steel", "faucet": "black_metal"}, pivot="back")


def laundry_wall_units(e):
    """Wall units 1.8 × 0.35 × 0.7: three handle-less wood cabinets (1.2) and an open shelving box (0.6) with a middle
    shelf, white storage boxes and jars; LED strip under the whole run. Pivot on the wall at its centre."""
    k = Kit(e["id"])
    W, D, H = 1.8, 0.35, 0.7
    xo = -W / 2 + 0.6                           # open box from -W/2 to xo, cabinets from xo to W/2
    t = 0.022
    # open box: frame, back, middle shelf
    ox = (-W / 2 + xo) / 2
    k.box("frame", (-W / 2 + t / 2, -D / 2, 0), (t, D, H), r=0.002, seg=1)
    k.box("frame", (xo - t / 2, -D / 2, 0), (t, D, H), r=0.002, seg=1)
    k.box("frame", (ox, -D / 2, H / 2 - t / 2), (0.6, D, t), r=0.002, seg=1)
    k.box("frame", (ox, -D / 2, -H / 2 + t / 2), (0.6, D, t), r=0.002, seg=1)
    k.box("frame", (ox, -D / 2, 0), (0.6 - 2 * t, D - 0.01, t), r=0.002, seg=1)
    k.box("frame", (ox, -0.006, 0), (0.6 - 2 * t, 0.012, H - 2 * t))
    # cabinets: carcass + three doors with shadow gaps
    cw = W / 2 - xo
    k.box("carcass", ((xo + W / 2) / 2, -D / 2 + 0.01, 0), (cw, D - 0.02, H), r=0.002, seg=1)
    g = 0.005
    dw = cw / 3
    for i in range(3):
        k.box("fronts", (xo + dw * (i + 0.5), -D + 0.009, 0), (dw - g, 0.018, H - g), r=0.002, seg=1)
    # contents of the open box: lower shelf two lidded boxes, upper shelf jars and folded towels
    sb = -H / 2 + t
    for i, bx in enumerate((ox - 0.13, ox + 0.13)):
        k.box("boxes", (bx, -D / 2 - 0.01, sb + 0.1), (0.22, 0.26, 0.2), r=0.01, seg=2)
        k.box("boxes", (bx, -D / 2 - 0.01, sb + 0.2), (0.225, 0.265, 0.02), r=0.006, seg=2)
        k.box("trim", (bx, -D / 2 - 0.142, sb + 0.13), (0.08, 0.002, 0.025), r=0.001, seg=1)
    su = t / 2
    for j, (jx, jh) in enumerate(((ox - 0.19, 0.2), (ox - 0.08, 0.16))):
        k.lathe("jars", (jx, -D / 2, su), [(0.0, 0.0), (0.05, 0.0), (0.052, 0.01), (0.052, jh - 0.03), (0.045, jh - 0.02),
                                           (0.045, jh - 0.02), (0.0, jh - 0.02)], seg=24)
        k.cyl("lids", (jx, -D / 2, su + jh - 0.01), 0.048, 0.02, seg=24, r=0.004)
    for i in range(3):
        k.box("towels", (ox + 0.14, -D / 2 - 0.02, su + 0.028 + i * 0.052), (0.24, 0.22 - 0.01 * i, 0.05), r=0.02, seg=3,
              rot=(0, 0, 2 - 3 * i), soft=True)
    # LED strip under everything
    k.box("led", (0, -D + 0.05, -H / 2 - 0.002), (W - 0.06, 0.018, 0.004))
    return k.finish(e, {"frame": "black_oak_veneer", "carcass": "grey_oak_veneer#9c8f82", "fronts": "grey_oak_veneer#9c8f82",
                        "boxes": "soft_white", "trim": "charcoal", "jars": "glass", "lids": "oak_veneer",
                        "towels": "terry#e9e3da", "led": "led"}, pivot="wall")


def laundry_basket_white(e):
    """White lidded laundry hamper Ø0.44, h 0.6, slightly tapered with woven ribs, lid with a knob."""
    k = Kit(e["id"])
    prof = [(0.0, 0.0), (0.18, 0.0), (0.19, 0.012)]
    n = 14
    for i in range(n + 1):                     # ribs: small bulges every rib
        z = 0.02 + i * (0.53 / n)
        r = 0.19 + 0.03 * (z / 0.55)
        prof.append((r, z))
        if i < n:
            prof.append((r + 0.004, z + 0.53 / n / 2))
    prof += [(0.224, 0.56), (0.21, 0.56), (0.21, 0.4)]
    k.lathe("body", (0, 0, 0), prof, seg=48)
    k.lathe("lid", (0, 0, 0.555), [(0.0, 0.035), (0.08, 0.034), (0.18, 0.026), (0.228, 0.014), (0.232, 0.0), (0.21, 0.0),
                                   (0.0, 0.0)], seg=48)
    k.lathe("lid", (0, 0, 0.588), [(0.0, 0.0), (0.03, 0.0), (0.022, 0.012), (0.03, 0.028), (0.0, 0.03)], seg=24)
    return k.finish(e, {"body": "cotton_waffle#f4f1ec", "lid": "soft_white"})


ENTRIES = [
    ("washer_front_white", "Стиральная машина фронтальная белая", "utility", washer_front_white, {"pivot": "back"}),
    ("dryer_front_white", "Сушильная машина фронтальная белая", "utility", dryer_front_white, {"pivot": "back"}),
    ("laundry_counter_run", "Столешница для прачечной 1,8 м с мойкой и нишей под две машины", "kitchen",
     laundry_counter_run, {"pivot": "back"}),
    ("laundry_wall_units", "Навесные шкафы 1,8 м с открытой полкой и подсветкой", "storage", laundry_wall_units,
     {"pivot": "wall"}),
    ("laundry_basket_white", "Корзина для белья белая с крышкой", "utility", laundry_basket_white, {}),
]
