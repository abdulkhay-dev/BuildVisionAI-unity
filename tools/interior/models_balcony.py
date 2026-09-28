"""Balcony (reference tile «Балкон»): woven rattan lounge armchair with cream cushions and a round teak side table.
Plants, the glass railing and the decking are not modelled here (plants exist, the rest is architecture)."""
import math

import numpy as np

import tex
from kit import Kit


def wicker(size=1024, cells=40, seed=91):
    """Basket-weave rattan (texture spans 1 m on metre UVs): checker cells of three round strands alternating
    horizontal / vertical, darker where a strand dives under, dark gaps, honey colour with per-strand variation."""
    x, y = tex.grid(size, size)
    gx, gy = x * cells, y * cells
    cx, cy = np.floor(gx).astype(int), np.floor(gy).astype(int)
    fx, fy = gx - cx, gy - cy
    horiz = (cx + cy) % 2 == 0
    across = np.where(horiz, fy, fx)
    along = np.where(horiz, fx, fy)
    s = across * 3
    idx = np.floor(s).astype(int)
    t = (s - idx) * 2 - 1
    round_ = np.sqrt(np.clip(1 - t * t, 0, 1))
    dive = 0.72 + 0.28 * np.sin(along * math.pi)
    r = tex.rng(seed)
    var = r.random((cells + 1, cells + 1, 3))[cy % (cells + 1), cx % (cells + 1), np.clip(idx, 0, 2)]
    base = tex.mix(tex.hexc("#9c6d3e"), tex.hexc("#c29260"), var)
    grain = tex.fbm(size, size, 64, 3, seed) * 0.16 - 0.08
    img = base * (0.35 + 0.7 * round_ * dive)[..., None] + grain[..., None] * round_[..., None]
    gap = np.clip(1 - round_ * 3, 0, 1)
    img = tex.mix(img, tex.hexc("#2b1c10"), gap * 0.8)
    return np.clip(img, 0, 1)


def lounge_chair_rattan(e):
    """Woven rattan lounge armchair 0.84 × 0.8 × 0.78: wicker shell (sloping arms rolling into a slightly reclined
    back, solid-rattan rims), short black legs, thick cream seat and back cushions, a grey scatter pillow."""
    k = Kit(e["id"])
    Wc, Dc = 0.84, 0.8
    y0, y1 = -Dc / 2, Dc / 2
    leg, deck = 0.12, 0.32                      # leg height, top of the woven seat deck
    arm_t, back_t = 0.085, 0.09
    # woven shell
    k.box("wicker", (0, 0.0, (leg + deck) / 2 + 0.01), (Wc - 0.02, Dc - 0.04, deck - leg), r=0.03, seg=2)
    for sx in (-1, 1):
        x = sx * (Wc / 2 - arm_t / 2)
        # side panel: front lower (arm 0.6) sloping up towards the back
        k.mesh("wicker", *_side(x, arm_t, y0, y1, leg, 0.6, 0.7), smooth="hard")
        k.tube("rim", _arm_rim(x, y0, y1, 0.6, 0.7), 0.022, seg=8)
    k.box("wicker", (0, y1 - back_t / 2 - 0.01, leg + (0.78 - leg) / 2), (Wc - 2 * arm_t + 0.01, back_t, 0.78 - leg),
          r=0.03, seg=2, rot=(-6, 0, 0))
    k.tube("rim", [(-Wc / 2 + arm_t / 2, y1 - 0.08, 0.72), (-Wc / 2 + arm_t, y1 - 0.06, 0.785),
                   (Wc / 2 - arm_t, y1 - 0.06, 0.785), (Wc / 2 - arm_t / 2, y1 - 0.08, 0.72)], 0.024, seg=8)
    k.tube("rim", [(-Wc / 2 + 0.01, y0 + 0.01, leg + 0.02), (Wc / 2 - 0.01, y0 + 0.01, leg + 0.02)], 0.016, seg=8)
    # legs
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.cyl("legs", (sx * (Wc / 2 - 0.06), sy * (Dc / 2 - 0.07), leg / 2), 0.014, leg, seg=10, rad2=0.018)
    # cushions
    iw = Wc - 2 * arm_t - 0.01
    k.box("cushion", (0, -0.03, deck + 0.075), (iw, Dc - 0.16, 0.15), r=0.05, seg=4, bulge=0.02)
    k.box("cushion", (0, y1 - back_t - 0.1, deck + 0.3), (iw - 0.02, 0.17, 0.4), r=0.06, seg=4, rot=(-14, 0, 0),
          bulge=0.03)
    k.pillow("pillow", (-0.13, y1 - back_t - 0.24, deck + 0.27), (0.4, 0.13, 0.32), rot=(-18, 0, 12))
    return k.finish(e, {"rim": "rattan", "legs": "black_metal", "cushion": "linen_rough#efe6d4",
                        "pillow": "linen_rough#9d9891"},
                    own={"wicker": {"albedo": wicker(), "rough": 0.75}})


def _side(x, t, y0, y1, z0, zf, zb):
    """Closed side panel (prism along X): bottom z0, top sloping from zf at the front to zb at the back."""
    xs = (x - t / 2, x + t / 2)
    prof = [(y0, z0), (y1, z0), (y1, zb), (y0, zf)]
    verts = [(xx, yy, zz) for xx in xs for (yy, zz) in prof]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return verts, faces


def _arm_rim(x, y0, y1, zf, zb, n=10):
    """Rolled rattan rim along the top of an arm, curling down at the front."""
    pts = [(x, y0 - 0.005, zf - 0.08), (x, y0 - 0.01, zf - 0.03)]
    for i in range(n + 1):
        t = i / n
        pts.append((x, y0 + 0.01 + (y1 - y0 - 0.02) * t, zf + (zb - zf) * t + 0.01))
    return pts


def side_table_round_wood(e):
    """Round teak outdoor side table Ø0.5 × 0.55: 30 mm top with a softened edge on three splayed round legs joined by a
    small triangular stretcher."""
    k = Kit(e["id"])
    R, H = 0.25, 0.55
    k.cyl("top", (0, 0, H - 0.015), R, 0.03, seg=48, r=0.006)
    top_r, foot_r, zt = 0.12, 0.22, H - 0.03
    feet = []
    for i in range(3):
        a = math.radians(90 + i * 120)
        p0 = (top_r * math.cos(a), top_r * math.sin(a), zt)
        p1 = (foot_r * math.cos(a), foot_r * math.sin(a), 0.0)
        k.tube("legs", [p0, p1], 0.017, seg=10)
        feet.append(p1)
    zs = 0.2
    ring = []
    for i in range(3):
        a = math.radians(90 + i * 120)
        rr = top_r + (foot_r - top_r) * (1 - zs / zt)
        ring.append((rr * math.cos(a), rr * math.sin(a), zs))
    k.tube("legs", ring + [ring[0]], 0.009, seg=8)
    k.cyl("legs", (0, 0, zt - 0.01), top_r + 0.02, 0.02, seg=24)      # under-top ring plate
    return k.finish(e, {"top": "teak_veneer", "legs": "teak_veneer"})


ENTRIES = [
    ("lounge_chair_rattan", "Кресло плетёное из ротанга с подушками", "outdoor", lounge_chair_rattan, {}),
    ("side_table_round_wood", "Столик круглый из тика на трёх ножках", "outdoor", side_table_round_wood, {}),
]
