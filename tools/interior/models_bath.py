"""Bathroom (reference tile «Ванная комната»): floating double walnut vanity, backlit mirror, walk-in shower with a black
frame, wall-hung toilet with flush plate, black towel ladder, bath mat."""
import math

from kit import Kit


def drape(k, slot, x0, x1, z0, z1, y, amp=0.006, waves=3.0, thick=0.008, flare=0.0, nx=24, nz=7):
    """Hanging cloth sheet from z1 (top) down to z0 in the plane y: soft vertical folds whose depth grows towards the
    hem (towels, tea towels). flare pushes the hem away from the plane (+ = towards -Y)."""
    verts, faces = [], []
    for side in (0, 1):
        for j in range(nz):
            t = j / (nz - 1)                 # 0 top … 1 hem
            z = z1 + (z0 - z1) * t
            for i in range(nx):
                u = i / (nx - 1)
                x = x0 + (x1 - x0) * u
                w = amp * (0.35 + 0.65 * t) * math.sin(2 * math.pi * waves * u + 0.7)
                yy = y + w - flare * t * t + (thick / 2 if side else -thick / 2)
                verts.append((x, yy, z))
    n = nx * nz
    for j in range(nz - 1):
        for i in range(nx - 1):
            a = j * nx + i
            faces.append((a, a + 1, a + nx + 1, a + nx))
            faces.append((n + a, n + a + nx, n + a + nx + 1, n + a + 1))
    for i in range(nx - 1):                  # top and hem edges
        for j in (0, nz - 1):
            a = j * nx + i
            faces.append((a, n + a, n + a + 1, a + 1))
    for j in range(nz - 1):                  # side edges
        for i in (0, nx - 1):
            a = j * nx + i
            faces.append((a, a + nx, n + a + nx, n + a))
    return k.mesh(slot, verts, faces, smooth="soft")


def _faucet_deck(k, slot, x, y, z, reach=0.14, h=0.24):
    """Tall single-lever deck faucet (for vessel basins): round foot, stem, spout bending forward (-Y), side lever."""
    k.cyl(slot, (x, y, z + 0.006), 0.026, 0.012, seg=24, r=0.003)
    pts =[(x, y, z + 0.01), (x, y, z + h - 0.05)]
    R = 0.05
    for i in range(1, 7):
        a = i / 6 * math.pi / 2
        pts.append((x, y - R * (1 - math.cos(a)), z + h - 0.05 + R * math.sin(a)))
    pts.append((x, y - R - (reach - R), z + h))
    k.tube(slot, pts, 0.012, seg=12)
    k.cyl(slot, (x, y - reach + 0.006, z + h - 0.012), 0.012, 0.02, seg=16)          # aerator tip
    k.box(slot, (x + 0.03, y + 0.004, z + h - 0.075), (0.05, 0.012, 0.012), r=0.004, seg=2, rot=(0, -12, 0))


def vanity_float_double(e):
    """Floating double vanity 1.6 × 0.5 × 0.5: walnut carcass, 2 + 2 drawers with shadow gaps and grip channels, white
    quartz top with two oval vessel basins, tall black faucets, LED strip under it. Pivot on the wall at its centre."""
    k = Kit(e["id"])
    W, D, H = 1.6, 0.5, 0.47          # carcass; top 30 mm on it → 0.5
    back = D / 2
    y0 = back - D / 2                 # carcass centre y
    k.box("carcass", (0, y0 + 0.01, H / 2), (W, D - 0.02, H), r=0.003, seg=2)
    # drawers: two columns each side of the centre divider, two rows (shadow gap 6 mm)
    g = 0.006
    fy = back - D + 0.002             # face of the drawer fronts (18 mm on the carcass)
    hw = W / 2
    rows = [(0.0, H * 0.46), (H * 0.46, H)]
    for side in (-1, 1):
        cx = side * hw / 2
        for (z0, z1) in rows:
            k.box("fronts", (cx, fy + 0.009, (z0 + z1) / 2), (hw - g, 0.018, z1 - z0 - g), r=0.002, seg=1)
            # grip channel along the top edge of each drawer
            k.box("grip", (cx, fy - 0.0005, z1 - g / 2 - 0.014), (hw - 0.06, 0.002, 0.018))
    # quartz top, 10 mm overhang at the front
    tz = H + 0.015
    k.box("top", (0, back - (D + 0.01) / 2, tz), (W + 0.01, D + 0.01, 0.03), r=0.003, seg=2)
    # two oval vessel basins and faucets behind them
    for side in (-1, 1):
        bx, by = side * 0.4, back - 0.28
        prof = [(0.0, 0.0), (0.12, 0.0), (0.175, 0.02), (0.2, 0.06), (0.205, 0.12), (0.196, 0.125), (0.188, 0.07),
                (0.165, 0.03), (0.11, 0.018), (0.0, 0.016)]
        b = k.lathe("basin", (bx, by, H + 0.03), prof, seg=48)
        b.scale = (1.0, 0.8, 1.0)
        k.cyl("basin", (bx, by, H + 0.03 + 0.019), 0.03, 0.004, seg=20)      # drain cap (same ceramic)
        _faucet_deck(k, "faucet", bx, back - 0.06, H + 0.03, reach=0.16, h=0.3)
    k.box("led", (0, back - D / 2, 0.003), (W - 0.12, 0.02, 0.006))
    return k.finish(e, {"carcass": "walnut_veneer", "fronts": "walnut_veneer", "grip": "furniture_dark",
                        "top": "soft_white", "basin": "ceramic", "faucet": "black_metal", "led": "led"}, pivot="wall")


def mirror_led_rect(e):
    """Rectangular backlit mirror 1.4 × 0.8 on a 30 mm back box; frosted glowing band round the edge and an LED halo
    behind. Pivot on the wall at its centre."""
    k = Kit(e["id"])
    W, H = 1.4, 0.8
    k.box("back", (0, 0.015, 0), (W - 0.1, 0.03, H - 0.1), r=0.004, seg=1)
    k.box("mirror", (0, -0.003, 0), (W, 0.006, H), r=0.0015, seg=1)
    b = 0.022                           # frosted band, 30 mm in from the edge
    ins = 0.035
    fy = -0.0062
    k.box("led", (0, fy, H / 2 - ins), (W - 2 * ins + b, 0.0006, b))
    k.box("led", (0, fy, -H / 2 + ins), (W - 2 * ins + b, 0.0006, b))
    k.box("led", (W / 2 - ins, fy, 0), (b, 0.0006, H - 2 * ins - b))
    k.box("led", (-W / 2 + ins, fy, 0), (b, 0.0006, H - 2 * ins - b))
    # halo strip on the back box rim (glows on the wall)
    for (c, s) in (((0, 0.02, (H - 0.1) / 2), (W - 0.1, 0.012, 0.004)), ((0, 0.02, -(H - 0.1) / 2), (W - 0.1, 0.012, 0.004)),
                   (((W - 0.1) / 2, 0.02, 0), (0.004, 0.012, H - 0.1)), ((-(W - 0.1) / 2, 0.02, 0), (0.004, 0.012, H - 0.1))):
        k.box("led", c, s)
    return k.finish(e, {"back": "furniture_dark", "mirror": "mirror", "led": "led"}, pivot="wall")


def shower_glass_black(e):
    """Walk-in shower 1.2 × 0.9 × 2.1 against a wall: fixed front glass 0.75 wide (walk-in gap on the right) and a side
    glass on the left, thin black profiles, stabiliser bar; black rain head on a wall arm, wall mixer and hand shower
    on a slide rail, linear floor drain. Pivot on the floor at the wall."""
    k = Kit(e["id"])
    W, D, H = 1.2, 0.9, 2.1
    back, front = 0.0, -D
    xl = -W / 2
    fw = 0.75
    t, p = 0.008, 0.022                 # glass thickness, profile size
    m = "frame"
    # side glass (x = xl) from the wall to the front, front glass from the corner to the right
    k.box("glass", (xl, (front + back) / 2, H / 2), (t, D - p, H - 2 * p))
    k.box("glass", (xl + fw / 2, front, H / 2), (fw - p, t, H - 2 * p))
    # profiles: wall channel, corner post, free edge, top and bottom rails
    k.box(m, (xl, back - 0.01, H / 2), (p, 0.02, H), r=0.002, seg=1)
    k.box(m, (xl, front, H / 2), (p, p, H), r=0.002, seg=1)
    k.box(m, (xl + fw, front, H / 2), (0.014, p, H), r=0.002, seg=1)
    k.box(m, (xl, (front + back) / 2, H - p / 2), (p, D, p), r=0.002, seg=1)
    k.box(m, (xl + fw / 2, front, H - p / 2), (fw, p, p), r=0.002, seg=1)
    k.box(m, (xl, (front + back) / 2, p / 4), (p, D, p / 2), r=0.002, seg=1)
    k.box(m, (xl + fw / 2, front, p / 4), (fw, p, p / 2), r=0.002, seg=1)
    # stabiliser bar from the free edge back to the wall
    k.tube(m, [(xl + fw, front + 0.01, H - 0.06), (xl + fw, back - 0.02, H - 0.06)], 0.009, seg=8)
    k.cyl(m, (xl + fw, back - 0.008, H - 0.06), 0.02, 0.016, seg=16, rot=(90, 0, 0))
    # rain shower: wall flange, arm, square head
    cx = 0.1
    k.cyl(m, (cx, back - 0.008, 2.08), 0.028, 0.016, seg=20, rot=(90, 0, 0))
    k.tube(m, [(cx, back - 0.01, 2.08), (cx, back - 0.36, 2.08), (cx, back - 0.4, 2.06)], 0.011, seg=10)
    k.box(m, (cx, back - 0.44, 2.04), (0.3, 0.3, 0.012), r=0.004, seg=2)
    k.box("nozzles", (cx, back - 0.44, 2.0335), (0.26, 0.26, 0.001))
    # wall mixer: round plate, body, lever; hand shower on a slide rail with hose
    mz = 1.05
    k.cyl(m, (cx, back - 0.004, mz), 0.075, 0.008, seg=32, r=0.002, rot=(90, 0, 0))
    k.cyl(m, (cx, back - 0.03, mz), 0.03, 0.05, seg=20, r=0.004, rot=(90, 0, 0))
    k.box(m, (cx + 0.04, back - 0.05, mz + 0.01), (0.09, 0.014, 0.012), r=0.004, seg=2, rot=(0, -15, 0))
    rx = cx + 0.3
    k.tube(m, [(rx, back - 0.012, 1.0), (rx, back - 0.012, 1.8)], 0.0085, seg=8)
    for z in (1.0, 1.8):
        k.box(m, (rx, back - 0.007, z), (0.03, 0.014, 0.03), r=0.004, seg=2)
    k.box(m, (rx, back - 0.03, 1.55), (0.035, 0.03, 0.04), r=0.004, seg=2)
    k.tube(m, [(rx, back - 0.05, 1.53), (rx, back - 0.07, 1.62), (rx, back - 0.09, 1.72)], 0.013, seg=10)
    k.cyl(m, (rx, back - 0.1, 1.74), 0.038, 0.02, seg=24, r=0.004, rot=(-60, 0, 0))
    hose = []                                         # hose sagging from the hand shower to the mixer outlet
    ax, az, bx2, bz2 = rx, 1.5, cx + 0.02, mz - 0.045
    for i in range(13):
        t = i / 12
        hose.append((ax + (bx2 - ax) * t, back - 0.05, az + (bz2 - az) * t - 0.32 * math.sin(math.pi * t)))
    k.tube(m, hose, 0.007, seg=8)
    # linear drain along the wall
    k.box(m, (0.0, back - 0.08, 0.001), (1.1, 0.06, 0.002))
    k.box("nozzles", (0.0, back - 0.08, 0.0025), (1.06, 0.03, 0.001))
    return k.finish(e, {"glass": "glass", m: "black_metal", "nozzles": "charcoal"}, pivot="back")


def toilet_wall_hung(e):
    """Wall-hung toilet: rounded white bowl 0.36 × 0.53, seat at 0.4, slim closed lid; black flush plate with two
    brushed buttons on the wall above it. Pivot on the floor at the wall."""
    k = Kit(e["id"])
    back = 0.0
    L = 0.53
    k.box("ceramic", (0, back - L / 2, 0.315), (0.3, L - 0.05, 0.13), r=0.1, seg=5, taper=(1.2, 1.1), soft=True)
    k.box("ceramic", (0, back - 0.06, 0.3), (0.32, 0.12, 0.16), r=0.03, seg=3)            # wall flange
    k.box("seat", (0, back - L / 2 - 0.005, 0.388), (0.355, L - 0.04, 0.026), r=0.012, seg=3, taper=(0.98, 0.98))
    k.box("seat", (0, back - L / 2 + 0.005, 0.405), (0.345, L - 0.07, 0.012), r=0.005, seg=2)
    k.box("hinge", (0, back - 0.07, 0.402), (0.2, 0.03, 0.03), r=0.012, seg=3)
    # flush plate
    k.box("plate", (0, back - 0.005, 1.0), (0.25, 0.01, 0.165), r=0.003, seg=1)
    k.box("button", (-0.055, back - 0.011, 1.0), (0.09, 0.004, 0.11), r=0.003, seg=1)
    k.box("button", (0.055, back - 0.011, 1.0), (0.09, 0.004, 0.11), r=0.003, seg=1)
    # floor anchor: a 3 mm sliver flat on the wall plane at floor level (hidden by the wall) so that the bounds reach
    # the floor and the app places the bowl at its real height with the floor/back pivot
    k.mesh("plate", [(-0.0015, back, 0.0), (0.0015, back, 0.0), (0.0, back, 0.003)], [(0, 1, 2)])
    return k.finish(e, {"ceramic": "ceramic", "seat": "gloss_white", "hinge": "chrome", "plate": "black_metal",
                        "button": "steel"}, pivot="back")


def towel_ladder_black(e):
    """Black towel ladder radiator 0.5 × 1.2, 0.11 off the wall, with a grey towel folded over a bar; bottom 0.15 above
    the floor when hung at its centre 0.75. Pivot on the wall at its centre."""
    k = Kit(e["id"])
    W, H = 0.5, 1.2
    fy = -0.09
    m = "metal"
    for sx in (-1, 1):
        k.box(m, (sx * (W / 2 - 0.0125), fy, 0), (0.025, 0.025, H), r=0.004, seg=2)
        for z in (-H / 2 + 0.1, H / 2 - 0.1):
            k.cyl(m, (sx * (W / 2 - 0.0125), fy / 2 + 0.002, z), 0.009, -fy - 0.012, seg=12, rot=(90, 0, 0))
            k.cyl(m, (sx * (W / 2 - 0.0125), -0.003, z), 0.022, 0.006, seg=16, rot=(90, 0, 0))
    bars = [-0.54, -0.44, -0.34, -0.2, -0.1, 0.0, 0.14, 0.24, 0.34, 0.48, 0.57]
    for z in bars:
        k.tube(m, [(-W / 2 + 0.02, fy, z), (W / 2 - 0.02, fy, z)], 0.0095, seg=8)
    # towel folded over the 0.24 bar: front drop, back drop, rounded fold
    zb, tw = 0.24, 0.42
    k.cyl("towel", (0.0, fy, zb + 0.002), 0.02, tw, seg=16, rot=(0, 90, 0))
    drape(k, "towel", -tw / 2, tw / 2, zb - 0.58, zb + 0.002, fy - 0.016, amp=0.008, waves=2.5, thick=0.009, flare=0.012)
    drape(k, "towel", -tw / 2 + 0.01, tw / 2 - 0.01, zb - 0.4, zb + 0.002, fy + 0.016, amp=0.006, waves=2.0, thick=0.009,
          flare=-0.008)
    return k.finish(e, {m: "black_metal", "towel": "terry#8e8a85"}, pivot="wall")


def bath_mat(e):
    """Light bath mat 0.8 × 0.5, 15 mm pile with soft edges."""
    k = Kit(e["id"])
    k.box("mat", (0, 0, 0.0075), (0.8, 0.5, 0.015), r=0.007, seg=3, soft=True)
    return k.finish(e, {"mat": "terry#fff9ef"})


ENTRIES = [
    ("vanity_float_double", "Тумба подвесная двойная, орех, с накладными раковинами 1,6 м", "bath", vanity_float_double,
     {"pivot": "wall"}),
    ("mirror_led_rect", "Зеркало с LED-подсветкой 1,4 × 0,8", "bath", mirror_led_rect, {"pivot": "wall"}),
    ("shower_glass_black", "Душевая walk-in, стекло в чёрной раме 1,2 × 0,9", "bath", shower_glass_black, {"pivot": "back"}),
    ("toilet_wall_hung", "Унитаз подвесной с кнопкой смыва", "bath", toilet_wall_hung, {"pivot": "back"}),
    ("towel_ladder_black", "Полотенцесушитель-лесенка чёрный с полотенцем", "bath", towel_ladder_black, {"pivot": "wall"}),
    ("bath_mat", "Коврик для ванной 0,8 × 0,5, светлый", "textiles", bath_mat, {}),
]
