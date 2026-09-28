"""Kitchen (reference tile «Кухня»): a modular run the app assembles from pieces — black French-door fridge, oven column,
walnut pantry column, handleless dark-grey base units (drawers, sink, induction hob) under a warm stone worktop, walnut
wall cabinets with LED strips, the grey upper row near the ceiling — plus the waterfall marble island, upholstered bar
stools and slim black cylinder pendants.

Run conventions: back of every unit at +Y (pivot "back" / "wall"), base units 0.9 high (0.1 toe-kick with an LED strip
under the carcass, 0.76 carcass, 0.04 worktop), 0.62 deep over the worktop; tall units 2.4 high, 0.6 deep."""
import math

import bmesh
import numpy as np

from kit import Kit, _link

# ---------------------------------------------------------------------- shared dimensions and materials
TOE, TOP_T = 0.10, 0.04          # toe-kick height, worktop thickness
CARC_D, FRONT_T = 0.56, 0.02     # carcass depth (from the wall), front thickness
GAP = 0.005                      # shadow gap between fronts
MAT = {
    "fronts": "furniture_dark#3b3a39",       # handleless dark-grey matt lacquer
    "carcass": "furniture_dark",
    "plinth": "furniture_dark#1c1b1a",
    "handle": "furniture_dark#232221",      # recessed grip-channel profile
    "led": "led",
    "walnut": "walnut_veneer",
    "sink": "granite_dark",
    "faucet": "black_metal",
}


# ---------------------------------------------------------------------- local helpers
def _noise(n, cells, seed):
    """Tileable value noise n×n (the lattice wraps, so the image repeats seamlessly)."""
    r = np.random.default_rng(seed)
    g = r.random((cells, cells))
    t = np.arange(n) * cells / n
    i0 = t.astype(int)
    f = t - i0
    f = f * f * (3 - 2 * f)
    i1 = (i0 + 1) % cells
    a, b = g[i0][:, i0], g[i0][:, i1]
    c, d = g[i1][:, i0], g[i1][:, i1]
    top = a + (b - a) * f[None, :]
    bot = c + (d - c) * f[None, :]
    return top + (bot - top) * f[:, None]


def _fbm(n, cells, octaves, seed, gain=0.5):
    out, amp, tot = np.zeros((n, n)), 1.0, 0.0
    for o in range(octaves):
        out += amp * _noise(n, cells * 2 ** o, seed + 13 * o)
        tot += amp
        amp *= gain
    return out / tot


def _hex(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def marble(n=1024, seed=5, base="#7b6655", cloud="#4a3b30", vein="#d8c9b4", vein2="#a8927c", strength=1.0):
    """Tileable slab marble (1 m repeat with metre UVs): clouded ground, long diagonal veins warped by turbulence, finer
    secondary veins. Colours in sRGB hex."""
    y, x = np.mgrid[0:n, 0:n] / n
    warp = _fbm(n, 3, 5, seed) * 2 - 1
    warp2 = _fbm(n, 5, 4, seed + 7) * 2 - 1
    cl = _fbm(n, 2, 5, seed + 3)
    img = _hex(base)[None, None, :] + (_hex(cloud) - _hex(base))[None, None, :] * np.clip((cl - 0.35) * 2.2, 0, 1)[..., None]
    # main veins: sin of an integer-frequency diagonal field keeps the tile seamless
    p = 2 * np.pi * (1 * x + 2 * y) + 5.5 * warp
    v = np.abs(np.sin(p))
    main = np.clip(1 - v / 0.06, 0, 1) ** 1.5 * np.clip(_fbm(n, 4, 3, seed + 11) * 1.8 - 0.35, 0, 1)
    p2 = 2 * np.pi * (3 * x - 2 * y) + 7.0 * warp2
    fine = np.clip(1 - np.abs(np.sin(p2)) / 0.025, 0, 1) * np.clip(_fbm(n, 6, 3, seed + 21) * 2 - 0.8, 0, 1)
    halo = np.clip(1 - v / 0.25, 0, 1) ** 2 * 0.35
    img = img + (_hex(vein2) - img) * (halo * strength)[..., None]
    img = img + (_hex(vein2) - img) * (fine * 0.8 * strength)[..., None]
    img = img + (_hex(vein) - img) * (main * strength)[..., None]
    grain = _fbm(n, 64, 2, seed + 31) - 0.5
    return np.clip(img + grain[..., None] * 0.05, 0, 1)


def hob_image(n=512):
    """Black glass induction top seen from above (u = width, v = depth): four faint zone rings and a touch strip."""
    y, x = np.mgrid[0:n, 0:n] / n
    img = np.full((n, n, 3), 0.028)
    for cx, cy, r in ((0.28, 0.66, 0.17), (0.72, 0.66, 0.13), (0.28, 0.27, 0.13), (0.72, 0.27, 0.17)):
        d = np.hypot(x - cx, y - cy)
        ring = np.clip(1 - np.abs(d - r) / 0.004, 0, 1) + 0.6 * np.clip(1 - np.abs(d - r * 0.35) / 0.003, 0, 1)
        img += ring[..., None] * 0.16
    strip = (np.abs(y - 0.07) < 0.03) & (np.abs(x - 0.5) < 0.3)
    img[strip] += 0.05
    for i in range(7):
        dot = np.hypot(x - (0.26 + i * 0.08), y - 0.07) < 0.008
        img[dot] = 0.55
    return np.clip(img, 0, 1)


_MARBLE = {}


def _worktop_tex():
    if "w" not in _MARBLE:
        _MARBLE["w"] = marble(1024, seed=9, base="#b9ab98", cloud="#9a8a76", vein="#f3ece2", vein2="#7a6958", strength=1.0)
    return _MARBLE["w"]


def _island_tex():
    if "i" not in _MARBLE:
        _MARBLE["i"] = marble(1024, seed=5, base="#8e7865", cloud="#5c4a3b", vein="#e6d8c4", vein2="#b09a84")
    return _MARBLE["i"]


def _stone(tex):
    return {"albedo": tex, "rough": 0.35}


def _fronts_column(k, x0, x1, z0, z1, ys, heights, slot="fronts", grip=0.0):
    """Stack of fronts between z0..z1 on the face plane ys (front face at ys - FRONT_T); heights are weights. grip leaves
    a recessed channel of that height above every front (handleless J-profile) filled with a dark 'handle' profile."""
    tot = sum(heights)
    avail = z1 - z0
    z = z0
    for h in heights:
        hh = avail * h / tot
        top = z + hh - (grip if grip else GAP)
        k.box(slot, ((x0 + x1) / 2, ys - FRONT_T / 2, (z + top) / 2), (x1 - x0 - 2 * GAP, FRONT_T, top - z), r=0.002, seg=1)
        if grip:
            k.box("handle", ((x0 + x1) / 2, ys - 0.004, top + grip / 2), (x1 - x0, 0.008, grip), r=0.0, seg=1)
        z += hh


def _base_shell(k, W, D=CARC_D, led=True):
    """Toe-kick, carcass and the LED strip under the carcass front edge (base units; back face at y = 0)."""
    k.box("plinth", (0, -(D - 0.06) / 2, TOE / 2), (W, D - 0.06, TOE))
    k.box("carcass", (0, -D / 2, (TOE + 0.9 - TOP_T) / 2), (W - 0.002, D, 0.9 - TOP_T - TOE))
    if led:
        k.box("led", (0, -D + 0.035, TOE - 0.003), (W - 0.04, 0.012, 0.006))


def _worktop(k, W, hole=None, depth=0.62):
    """Stone worktop over a base unit; hole=(cx, cy, w, d) leaves a cut-out (built from four strips)."""
    z = 0.9 - TOP_T / 2
    if not hole:
        k.box("top", (0, -depth / 2, z), (W, depth, TOP_T))
        return
    cx, cy, w, d = hole
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2
    k.box("top", ((-W / 2 + x0) / 2, -depth / 2, z), (x0 + W / 2, depth, TOP_T))
    k.box("top", ((W / 2 + x1) / 2, -depth / 2, z), (W / 2 - x1, depth, TOP_T))
    k.box("top", (cx, (y1 + 0) / 2, z), (w, -y1, TOP_T))
    k.box("top", (cx, (-depth + y0) / 2, z), (w, y0 + depth, TOP_T))


def _sink(k, cx, cy, w, d, depth=0.2, ztop=0.9 - TOP_T):
    """Undermount basin (open box) under a worktop cut-out."""
    t = 0.012
    zb = ztop - depth
    k.box("sink", (cx, cy, zb + t / 2), (w + 2 * t, d + 2 * t, t))
    k.box("sink", (cx - w / 2 - t / 2, cy, zb + depth / 2), (t, d + 2 * t, depth))
    k.box("sink", (cx + w / 2 + t / 2, cy, zb + depth / 2), (t, d + 2 * t, depth))
    k.box("sink", (cx, cy - d / 2 - t / 2, zb + depth / 2), (w, t, depth))
    k.box("sink", (cx, cy + d / 2 + t / 2, zb + depth / 2), (w, t, depth))
    k.cyl("faucet", (cx, cy, zb + t + 0.002), 0.035, 0.004, seg=20)          # drain


def _faucet(k, x, y, z, reach=0.22, h=0.36, face=-1):
    """Black gooseneck faucet on the worktop at (x, y, z); the spout reaches `reach` towards face*Y."""
    k.cyl("faucet", (x, y, z + 0.008), 0.028, 0.016, seg=24, r=0.004)
    k.cyl("faucet", (x, y, z + 0.09), 0.018, 0.16, seg=20)
    pts = [(x, y, z + 0.16)]
    for i in range(1, 17):
        a = math.pi * i / 16
        pts.append((x, y + face * reach / 2 * (1 - math.cos(a)), z + 0.16 + (h - 0.16) * math.sin(a) ** 0.8 +
                    (0.0 if i < 16 else 0)))
    tip = pts[-1]
    pts.append((x, tip[1], tip[2] - 0.05))
    k.tube("faucet", pts, 0.012, seg=12)
    k.cyl("faucet", (x, tip[1], tip[2] - 0.06), 0.016, 0.03, seg=16)
    # side lever
    k.box("faucet", (x + 0.03, y, z + 0.14), (0.05, 0.012, 0.012), r=0.004, seg=2, rot=(0, -15, 0))


# ---------------------------------------------------------------------- tall units
def kitchen_fridge_black(e):
    """Black French-door fridge 0.9 × 0.7 × 2.0: two doors over a freezer drawer, long vertical bar handles, water
    dispenser panel on the left door, dark grille at the floor."""
    k = Kit(e["id"])
    W, D, H = 0.9, 0.7, 2.0
    body_d = D - 0.06
    k.box("body", (0, -body_d / 2, H / 2), (W, body_d, H), r=0.006, seg=2)
    k.box("plinth", (0, -body_d - 0.02, 0.04), (W - 0.02, 0.04, 0.07))
    yf = -body_d - 0.025
    zd = 0.78
    dw = (W - 0.006) / 2
    for s in (-1, 1):
        k.box("fronts", (s * (dw + 0.006) / 2, yf, (zd + H - 0.005) / 2), (dw, 0.05, H - 0.005 - zd), r=0.008, seg=2)
    k.box("fronts", (0, yf, (0.085 + zd - 0.006) / 2), (W, 0.05, zd - 0.006 - 0.085), r=0.008, seg=2)
    # handles: vertical bars at the inner edges, a horizontal bar on the drawer
    hy = yf - 0.025 - 0.035
    for s in (-1, 1):
        hx = s * 0.045
        k.cyl("handle", (hx, hy, zd + 0.62), 0.011, 0.72, seg=12)
        for zz in (zd + 0.3, zd + 0.94):
            k.cyl("handle", (hx, hy + 0.018, zz), 0.008, 0.036, seg=10, rot=(90, 0, 0))
    k.cyl("handle", (0, hy, zd - 0.09), 0.011, 0.6, seg=12, rot=(0, 90, 0))
    for xx in (-0.27, 0.27):
        k.cyl("handle", (xx, hy + 0.018, zd - 0.09), 0.008, 0.036, seg=10, rot=(90, 0, 0))
    # dispenser recess + display
    k.box("glass", (-0.2, yf - 0.026, 1.28), (0.2, 0.004, 0.32), r=0.01, seg=2)
    k.box("display", (-0.2, yf - 0.029, 1.4), (0.08, 0.002, 0.018))
    return k.finish(e, {"body": "furniture_dark", "plinth": "charcoal", "fronts": "black_metal#141414",
                        "handle": "steel#2c2c2c", "glass": "black_glass", "display": "led"}, pivot="back")


def _tall_shell(k, W=0.6, D=CARC_D, H=2.4):
    k.box("plinth", (0, -(D - 0.06) / 2, TOE / 2), (W, D - 0.06, TOE))
    k.box("carcass", (0, -D / 2, (TOE + H) / 2), (W - 0.002, D, H - TOE))


def kitchen_tall_cabinet(e):
    """Walnut-veneer pantry column 0.6 × 0.6 × 2.4: two doors (lower tall, upper short) with a vertical grip channel on
    the left side, recessed toe-kick."""
    k = Kit(e["id"])
    W, H = 0.6, 2.4
    _tall_shell(k, W)
    ys = -CARC_D
    ch = 0.028
    x0, x1 = -W / 2 + ch, W / 2
    split = 1.72
    k.box("fronts", ((x0 + x1) / 2, ys - FRONT_T / 2, (TOE + split - GAP) / 2), (x1 - x0 - GAP, FRONT_T, split - GAP - TOE),
          r=0.002, seg=1)
    k.box("fronts", ((x0 + x1) / 2, ys - FRONT_T / 2, (split + H - GAP) / 2), (x1 - x0 - GAP, FRONT_T, H - GAP - split),
          r=0.002, seg=1)
    k.box("handle", (-W / 2 + ch / 2, ys - 0.004, (TOE + H) / 2), (ch, 0.008, H - TOE - GAP))
    return k.finish(e, {"fronts": MAT["walnut"], "carcass": MAT["carcass"], "plinth": MAT["plinth"],
                        "handle": MAT["handle"]}, pivot="back")


def _oven(k, cz, h, W=0.6, ys=-CARC_D, compact=False):
    """Built-in black-glass oven (or compact combi/microwave) centred at height cz, flush with the fronts."""
    w = W - 0.012
    y = ys - FRONT_T / 2
    k.box("appliance", (0, y, cz), (w, FRONT_T + 0.004, h - 0.008), r=0.004, seg=2)
    strip = 0.09 if not compact else 0.075
    top = cz + (h - 0.008) / 2
    k.box("trim", (0, y - 0.003, top - strip / 2), (w - 0.02, 0.002, strip - 0.02))
    k.box("display", (0, y - 0.0045, top - strip / 2), (0.1, 0.002, 0.022))
    for s in (-1, 1):                                               # control knobs
        k.cyl("handle", (s * 0.2, y - 0.014, top - strip / 2), 0.018, 0.02, seg=16, rot=(90, 0, 0), r=0.004)
    wh = h - strip - 0.12
    k.box("glass", (0, y - 0.0028, top - strip - 0.035 - wh / 2), (w - 0.14, 0.002, wh))
    # handle bar across the door
    hz = top - strip - 0.03
    k.cyl("handle", (0, y - 0.045, hz), 0.01, w - 0.1, seg=12, rot=(0, 90, 0))
    for s in (-1, 1):
        k.cyl("handle", (s * (w / 2 - 0.08), y - 0.028, hz), 0.007, 0.036, seg=10, rot=(90, 0, 0))


def kitchen_oven_column(e):
    """Tall column 0.6 × 0.6 × 2.4 with a built-in black oven and a compact combi/microwave stacked at eye level,
    walnut drawers below and a walnut door above."""
    k = Kit(e["id"])
    W, H = 0.6, 2.4
    _tall_shell(k, W)
    ys = -CARC_D
    _fronts_column(k, -W / 2, W / 2, TOE, 0.8, ys, [1, 1], slot="fronts")
    _oven(k, 0.8 + 0.3, 0.6, W, ys)
    _oven(k, 1.4 + 0.225, 0.45, W, ys, compact=True)
    k.box("fronts", (0, ys - FRONT_T / 2, (1.85 + GAP + H - GAP) / 2), (W - 2 * GAP, FRONT_T, H - 1.85 - 2 * GAP),
          r=0.002, seg=1)
    return k.finish(e, {"fronts": MAT["walnut"], "carcass": MAT["carcass"], "plinth": MAT["plinth"],
                        "appliance": "black_glass", "trim": "black_metal#2a2a2a", "display": "led", "handle": "steel#3a3a3a",
                        "glass": "furniture_dark#0c0b0b"}, pivot="back")


# ---------------------------------------------------------------------- base units
def _base(e, W, heights):
    k = Kit(e["id"])
    _base_shell(k, W)
    _fronts_column(k, -W / 2, W / 2, TOE, 0.9 - TOP_T, -CARC_D, heights, grip=0.022)
    _worktop(k, W)
    return k.finish(e, {"fronts": MAT["fronts"], "carcass": MAT["carcass"], "plinth": MAT["plinth"],
                        "handle": MAT["handle"], "led": MAT["led"]}, own={"top": _stone(_worktop_tex())}, pivot="back")


def kitchen_base_600(e):
    """Handleless dark-grey base unit 0.6 wide: three drawers with grip channels, stone worktop, LED toe-kick."""
    return _base(e, 0.6, [0.9, 1.1, 1.3])


def kitchen_base_900(e):
    """Handleless dark-grey base unit 0.9 wide: three wide drawers, stone worktop, LED toe-kick."""
    return _base(e, 0.9, [0.9, 1.1, 1.3])


def kitchen_sink_base(e):
    """Sink base 0.8 wide: undermount dark basin cut into the stone worktop, black gooseneck faucet, false drawer front
    over a door."""
    k = Kit(e["id"])
    W = 0.8
    _base_shell(k, W)
    _fronts_column(k, -W / 2, W / 2, TOE, 0.9 - TOP_T, -CARC_D, [2.8, 1.0], grip=0.022)
    hole = (0, -0.31, 0.6, 0.42)
    _worktop(k, W, hole)
    _sink(k, *hole)
    _faucet(k, 0, -0.06, 0.9, reach=0.2, h=0.38, face=-1)
    return k.finish(e, {"fronts": MAT["fronts"], "carcass": MAT["carcass"], "plinth": MAT["plinth"],
                        "handle": MAT["handle"], "led": MAT["led"], "sink": MAT["sink"], "faucet": MAT["faucet"]},
                    own={"top": _stone(_worktop_tex()), }, pivot="back")


def kitchen_cooktop_base(e):
    """Hob base 0.8 wide: black-glass induction hob (four zones, touch strip) set into the worktop over two deep pan
    drawers."""
    k = Kit(e["id"])
    W = 0.8
    _base_shell(k, W)
    _fronts_column(k, -W / 2, W / 2, TOE, 0.9 - TOP_T, -CARC_D, [1.2, 1.0], grip=0.022)
    _worktop(k, W)
    k.slab("hob", (0, -0.32, 0.9 + 0.003), (0.6, 0.52, 0.006), r=0.002)
    return k.finish(e, {"fronts": MAT["fronts"], "carcass": MAT["carcass"], "plinth": MAT["plinth"],
                        "handle": MAT["handle"], "led": MAT["led"]},
                    own={"top": _stone(_worktop_tex()), "hob": {"albedo": hob_image(), "rough": 0.08}}, pivot="back")


# ---------------------------------------------------------------------- wall units
def _wall_unit(e, W, doors, H, D, led):
    k = Kit(e["id"])
    k.box("carcass", (0, -D / 2 + FRONT_T / 2, H / 2), (W, D - FRONT_T, H))
    drop = 0.02 if led else 0.0                  # fronts run past the carcass bottom = finger pull
    dw = W / doors
    for i in range(doors):
        x = -W / 2 + dw * (i + 0.5)
        k.box("fronts", (x, -D + FRONT_T / 2, (H - drop) / 2), (dw - 2 * GAP, FRONT_T, H + drop - GAP), r=0.002, seg=1)
    if led:
        k.box("led", (0, -D + 0.06, -0.003), (W - 0.04, 0.012, 0.006))
    return k


def kitchen_wall_cabinet(e):
    """Walnut-veneer wall cabinet 0.9 × 0.35 × 0.75, two handleless doors (fronts drop 2 cm as a finger pull), LED
    strip underneath."""
    k = _wall_unit(e, 0.9, 2, 0.75, 0.35, True)
    return k.finish(e, {"carcass": MAT["carcass"], "fronts": MAT["walnut"], "led": MAT["led"]}, pivot="wall")


def kitchen_wall_cabinet_600(e):
    """Walnut-veneer wall cabinet 0.6 × 0.35 × 0.75, one door, LED strip underneath."""
    k = _wall_unit(e, 0.6, 1, 0.75, 0.35, True)
    return k.finish(e, {"carcass": MAT["carcass"], "fronts": MAT["walnut"], "led": MAT["led"]}, pivot="wall")


def kitchen_upper_grey(e):
    """Top row module under the ceiling: dark-grey handleless cabinet 0.9 × 0.35 × 0.5 with two doors."""
    k = _wall_unit(e, 0.9, 2, 0.5, 0.35, False)
    return k.finish(e, {"carcass": MAT["carcass"], "fronts": MAT["fronts"]}, pivot="wall")


# ---------------------------------------------------------------------- island
def kitchen_island_waterfall(e):
    """Island 2.8 × 1.1 × 0.92: brown-veined marble top and waterfall ends, dark-grey cabinet body on the working side
    (+Y: drawers, sink module), panelled back on the stool side (-Y) under a 0.3 m overhang, integrated sink with a black
    faucet, LED toe-kick on both sides. Pivot floor centre."""
    k = Kit(e["id"])
    L, D, H, T = 2.8, 1.1, 0.92, 0.05
    y0, y1 = -D / 2, D / 2
    # sink cut-out in the top (towards the working side)
    sx, sy, sw, sd = 0.0, 0.2, 0.72, 0.42
    zt = H - T / 2
    xa, xb, ya, yb = sx - sw / 2, sx + sw / 2, sy - sd / 2, sy + sd / 2
    k.box("marble", ((-L / 2 + xa) / 2, 0, zt), (xa + L / 2, D, T), r=0.004, seg=2)
    k.box("marble", ((L / 2 + xb) / 2, 0, zt), (L / 2 - xb, D, T), r=0.004, seg=2)
    k.box("marble", (sx, (yb + y1) / 2, zt), (sw, y1 - yb, T), r=0.004, seg=2)
    k.box("marble", (sx, (y0 + ya) / 2, zt), (sw, ya - y0, T), r=0.004, seg=2)
    for s in (-1, 1):                                               # waterfall ends
        k.box("marble", (s * (L / 2 - T / 2), 0, (H - T) / 2), (T, D, H - T + 0.002), r=0.004, seg=2)
    _sink(k, sx, sy, sw, sd, depth=0.21, ztop=H - T)
    _faucet(k, sx, sy - sd / 2 - 0.06, H, reach=0.22, h=0.4, face=1)
    # body: working side fronts at +Y, stool side panelled back recessed 0.3 under the top
    bx = L - 2 * T - 0.004
    by0, by1 = y0 + 0.30, y1 - 0.02 - FRONT_T
    zc0, zc1 = TOE, H - T
    k.box("carcass", (0, (by0 + by1) / 2, (zc0 + zc1) / 2), (bx, by1 - by0, zc1 - zc0))
    k.box("plinth", (0, (by0 + by1) / 2, TOE / 2), (bx, by1 - by0 - 0.12, TOE))
    for yy in (by1 - 0.035, by0 + 0.035):
        k.box("led", (0, yy, TOE - 0.003), (bx - 0.04, 0.012, 0.006))
    # working-side fronts: drawers | sink doors | drawers, facing +Y
    mw = bx / 3
    for i, hs in enumerate(([0.9, 1.1, 1.3], [2.8, 1.0], [0.9, 1.1, 1.3])):
        xa0 = -bx / 2 + mw * i
        _fronts_back(k, xa0, xa0 + mw, zc0, zc1, by1, hs)
    # stool side: flat panels with shadow gaps
    for i in range(4):
        pw = bx / 4
        x = -bx / 2 + pw * (i + 0.5)
        k.box("fronts", (x, by0 - FRONT_T / 2, (zc0 + zc1 - GAP) / 2), (pw - 2 * GAP, FRONT_T, zc1 - zc0 - GAP), r=0.002, seg=1)
    return k.finish(e, {"carcass": MAT["carcass"], "plinth": MAT["plinth"], "led": MAT["led"], "sink": MAT["sink"],
                        "faucet": MAT["faucet"], "fronts": MAT["fronts"], "handle": MAT["handle"]},
                    own={"marble": _stone(_island_tex())})


def _fronts_back(k, x0, x1, z0, z1, yb, heights, grip=0.022):
    """Like _fronts_column but the fronts face +Y (island working side), back face of the fronts at yb."""
    tot = sum(heights)
    z = z0
    for h in heights:
        hh = (z1 - z0) * h / tot
        top = z + hh - grip
        k.box("fronts", ((x0 + x1) / 2, yb + FRONT_T / 2, (z + top) / 2), (x1 - x0 - 2 * GAP, FRONT_T, top - z), r=0.002, seg=1)
        k.box("handle", ((x0 + x1) / 2, yb + 0.004, top + grip / 2), (x1 - x0, 0.008, grip))
        z += hh


# ---------------------------------------------------------------------- seating and lighting
def _shell_band(k, slot, cy, z0, R, t, arc, h_mid, h_side, n=24):
    """Curved upholstered back: a thick band on a circle of radius R around (0, cy) spanning `arc` degrees centred on
    +Y, its height falling from h_mid at the back to h_side at the tips; subdivided once for soft edges."""
    bm = bmesh.new()
    rings = []
    for i in range(n + 1):
        a = math.radians(-arc / 2 + arc * i / n)
        f = math.cos(a / math.radians(arc / 2) * math.pi / 2)
        h = h_side + (h_mid - h_side) * f
        dx, dy = math.sin(a), math.cos(a)
        ri, ro = R - t / 2, R + t / 2
        rings.append([bm.verts.new((dx * ri, cy + dy * ri, z0)), bm.verts.new((dx * ri, cy + dy * ri, z0 + h)),
                      bm.verts.new((dx * ro, cy + dy * ro, z0 + h)), bm.verts.new((dx * ro, cy + dy * ro, z0))])
    for i in range(n):
        a, b = rings[i], rings[i + 1]
        for j in range(4):
            bm.faces.new((a[j], a[(j + 1) % 4], b[(j + 1) % 4], b[j]))
    bm.faces.new(rings[0])
    bm.faces.new(list(reversed(rings[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = _link(bm, "band")
    obj.modifiers.new("smooth", "SUBSURF").levels = 1
    return k._add(obj, slot, (0, 0, 0), (0, 0, 0), "m", "soft")


def bar_stool_upholstered(e):
    """Counter stool, seat 0.75: taupe upholstered seat with a low wrap-around back, four thin splayed black legs and a
    round footrest ring."""
    k = Kit(e["id"])
    zs = 0.7
    k.lathe("upholstery", (0, -0.01, zs - 0.005), [(0.0, 0.0), (0.17, 0.0), (0.205, 0.012), (0.222, 0.04), (0.218, 0.066),
                                                  (0.2, 0.08), (0.12, 0.086), (0.0, 0.088)], seg=40)
    _shell_band(k, "upholstery", -0.01, zs + 0.02, 0.2, 0.05, 200, 0.26, 0.07, n=28)
    k.cyl("legs", (0, -0.01, zs - 0.012), 0.165, 0.016, seg=32, r=0.004)
    feet = []
    for i in range(4):
        a = math.radians(45 + 90 * i)
        top = (0.15 * math.cos(a), -0.01 + 0.14 * math.sin(a), zs - 0.02)
        bot = (0.24 * math.cos(a), -0.01 + 0.23 * math.sin(a), 0.006)
        k.tube("legs", [top, bot], 0.0095, seg=10)
        k.cyl("legs", (bot[0], bot[1], 0.005), 0.012, 0.01, seg=12)
        feet.append((top, bot))
    zr = 0.26
    t = (zs - 0.02 - zr) / (zs - 0.026)
    rr = math.hypot(feet[0][0][0] + (feet[0][1][0] - feet[0][0][0]) * t, feet[0][0][1] + 0.01 + (feet[0][1][1] - feet[0][0][1]) * t)
    k.torus("legs", (0, -0.01, zr), rr, 0.009, seg=48, rseg=8)
    return k.finish(e, {"upholstery": "velvet#958a7f", "legs": "black_metal"})


def pendant_cylinder_black(e):
    """Slim black cylinder pendant Ø0.1 × 0.35 on a cable, 0.9 m from the ceiling to the glowing underside."""
    k = Kit(e["id"])
    drop = 0.9
    k.cyl("body", (0, 0, -0.012), 0.05, 0.024, seg=32, r=0.004)                  # ceiling canopy
    k.cyl("cable", (0, 0, -(drop - 0.35) / 2), 0.0025, drop - 0.35 - 0.02, seg=8)
    k.cyl("body", (0, 0, -drop + 0.35 / 2), 0.05, 0.35, seg=40, r=0.003)
    k.cyl("glow", (0, 0, -drop - 0.001), 0.042, 0.004, seg=32)
    return k.finish(e, {"body": "black_metal", "cable": "black_metal", "glow": "downlight"}, hanging=True)


ENTRIES = [
    ("kitchen_fridge_black", "Холодильник чёрный French Door 0,9 м", "kitchen", kitchen_fridge_black, {"pivot": "back"}),
    ("kitchen_oven_column", "Пенал с духовкой и микроволновкой, орех", "kitchen", kitchen_oven_column, {"pivot": "back"}),
    ("kitchen_tall_cabinet", "Пенал высокий 0,6 м, орех", "kitchen", kitchen_tall_cabinet, {"pivot": "back"}),
    ("kitchen_base_600", "Нижний модуль 0,6 м с ящиками, графит", "kitchen", kitchen_base_600, {"pivot": "back"}),
    ("kitchen_base_900", "Нижний модуль 0,9 м с ящиками, графит", "kitchen", kitchen_base_900, {"pivot": "back"}),
    ("kitchen_sink_base", "Модуль под мойку 0,8 м со смесителем", "kitchen", kitchen_sink_base, {"pivot": "back"}),
    ("kitchen_cooktop_base", "Модуль с индукционной варочной панелью 0,8 м", "kitchen", kitchen_cooktop_base, {"pivot": "back"}),
    ("kitchen_wall_cabinet", "Навесной шкаф 0,9 м, орех, с подсветкой", "kitchen", kitchen_wall_cabinet, {"pivot": "wall"}),
    ("kitchen_wall_cabinet_600", "Навесной шкаф 0,6 м, орех, с подсветкой", "kitchen", kitchen_wall_cabinet_600, {"pivot": "wall"}),
    ("kitchen_upper_grey", "Верхний ряд шкафов 0,9 м, графит", "kitchen", kitchen_upper_grey, {"pivot": "wall"}),
    ("kitchen_island_waterfall", "Кухонный остров с водопадной столешницей 2,8 м", "kitchen", kitchen_island_waterfall, {}),
    ("bar_stool_upholstered", "Барный стул мягкий с низкой спинкой", "seating", bar_stool_upholstered, {}),
    ("pendant_cylinder_black", "Подвес-цилиндр чёрный", "lighting", pendant_cylinder_black, {"hanging": True}),
]
