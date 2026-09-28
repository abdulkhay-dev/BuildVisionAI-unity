"""Office (reference tile «Кабинет»): walnut bookcase with LED shelves, executive desk with a drawer pedestal, black mesh
office chair, 27" monitor, keyboard and mouse on a desk pad."""
import math

import numpy as np

import tex
from kit import Kit


# ---------------------------------------------------------------------- local helpers
def shell(k, slot, fn, nu, nv, t, uv="m"):
    """Solid curved plate: front surface fn(u, v) → (x, y, z) on a nu × nv grid, back surface offset by t towards +Y,
    closed along the rim (chair backs, seat shells)."""
    verts = []
    for side in (0, 1):
        for j in range(nv + 1):
            for i in range(nu + 1):
                x, y, z = fn(i / nu, j / nv)
                verts.append((x, y + t * side, z))
    n = (nu + 1) * (nv + 1)

    def vid(i, j, side):
        return side * n + j * (nu + 1) + i

    faces = []
    for j in range(nv):
        for i in range(nu):
            faces.append((vid(i, j, 0), vid(i + 1, j, 0), vid(i + 1, j + 1, 0), vid(i, j + 1, 0)))
            faces.append((vid(i, j, 1), vid(i, j + 1, 1), vid(i + 1, j + 1, 1), vid(i + 1, j, 1)))
    rim = [(i, 0) for i in range(nu)] + [(nu, j) for j in range(nv)] + \
          [(i, nv) for i in range(nu, 0, -1)] + [(0, j) for j in range(nv, 0, -1)]
    for a in range(len(rim)):
        (i0, j0), (i1, j1) = rim[a], rim[(a + 1) % len(rim)]
        faces.append((vid(i0, j0, 0), vid(i0, j0, 1), vid(i1, j1, 1), vid(i1, j1, 0)))
    return k.mesh(slot, verts, faces, smooth="hard", uv=uv)


def mesh_weave(h=512, w=512, cells=110, seed=5):
    """Fine black office-chair mesh: dark ground with a lighter crossed weave."""
    x, y = tex.grid(h, w)
    gx = np.abs(np.sin(x * cells * math.pi))
    gy = np.abs(np.sin(y * cells * 1.2 * math.pi))
    weave = np.maximum(tex.smooth(0.6, 1.0, gx), tex.smooth(0.6, 1.0, gy))
    img = np.ones((h, w, 3)) * tex.hexc("#121212")
    img = tex.mix(img, tex.hexc("#3a3a3a"), weave * 0.8)
    return np.clip(img + (tex.rng(seed).random((h, w)) * 0.02)[..., None], 0, 1)


# ---------------------------------------------------------------------- models
def bookcase_wall_led(e):
    """Walnut bookcase module 1.2 × 0.4 × 2.4: closed dark cabinet below (two push doors on a recessed plinth), four open
    bays above with a warm LED strip under each shelf, books and a few decor objects. Full-height sides so modules stand
    side by side into a wall; pivot at the back."""
    k = Kit(e["id"])
    W, D, H, t = 1.2, 0.4, 2.4, 0.03
    xi = W / 2 - t                                   # inner half width
    fy = -D / 2                                      # front plane
    car = "carcass"
    # sides, top, plinth, cabinet
    for s in (-1, 1):
        k.box(car, (s * (W / 2 - t / 2), 0, H / 2), (t, D, H), r=0.003, seg=2)
    k.box(car, (0, 0, H - t / 2), (W - 2 * t + 0.002, D, t), r=0.002, seg=1)
    k.box("plinth", (0, 0.02, 0.035), (W - 2 * t, D - 0.06, 0.07))
    k.box(car, (0, 0, 0.07 + 0.009), (W - 2 * t + 0.002, D, 0.018))
    ctop = 0.84
    k.box(car, (0, 0, ctop), (W - 2 * t + 0.002, D, 0.035), r=0.002, seg=1)
    dh = ctop - 0.0175 - 0.088 - 0.004
    dw = (2 * xi - 0.004 * 3) / 2
    for s in (-1, 1):
        k.box("fronts", (s * (dw / 2 + 0.002), fy + 0.0105, 0.088 + dh / 2), (dw, 0.019, dh), r=0.0015, seg=1)
    k.box("back", (0, D / 2 - 0.006, (ctop + H) / 2), (W - 2 * t + 0.002, 0.012, H - ctop))
    k.box("back", (0, D / 2 - 0.006, (0.088 + ctop) / 2), (W - 2 * t + 0.002, 0.012, ctop - 0.088))
    # shelves + LED strips (under each shelf and under the top)
    shelves = [1.225, 1.61, 1.995]
    for z in shelves:
        k.box(car, (0, 0.005, z), (W - 2 * t + 0.002, D - 0.01, t), r=0.002, seg=1)
    for z in shelves + [H - t]:
        k.box("led", (0, fy + 0.035, z - t / 2 - 0.003), (2 * xi - 0.04, 0.012, 0.006))
    # books: blocks standing near the back of each bay, two textures alternating
    bd = 0.23
    by = D / 2 - 0.02 - bd / 2
    bays = [ctop + 0.0175] + [z + t / 2 for z in shelves]
    rows = [
        [(-0.545, 0.25, 0.27, "books"), (-0.295, 0.2, 0.23, "books_b"), (0.3, None, 0, "vase")],
        [(-0.1, 0.26, 0.24, "books_b"), (0.16, 0.24, 0.28, "books"), (-0.44, None, 0, "stack")],
        [(-0.545, 0.24, 0.3, "books"), (-0.305, 0.23, 0.26, "books_b"), (0.12, None, 0, "lean"), (0.34, None, 0, "bowl")],
        [(0.07, 0.24, 0.26, "books_b"), (0.31, 0.24, 0.3, "books"), (-0.33, None, 0, "vase_tall")],
    ]
    for z0, row in zip(bays, rows):
        for x0, w, h, kind in row:
            if w is not None:
                k.box(kind, (x0 + w / 2, by, z0 + h / 2), (w, bd, h), r=0.002, seg=1, uv="front")
            elif kind == "stack":
                for n, (hh, ww, a, sl) in enumerate([(0.035, 0.24, 4, "book_a"), (0.03, 0.22, -3, "book_b"), (0.04, 0.2, 6, "book_a")]):
                    zz = z0 + sum([0.035, 0.03, 0.04][:n]) + hh / 2
                    k.box(sl, (x0, by + 0.01, zz), (ww, 0.17, hh), r=0.002, seg=1, rot=(0, 0, a))
            elif kind == "lean":
                k.box("book_b", (x0, by, z0 + 0.12), (0.028, 0.2, 0.26), r=0.002, seg=1, rot=(0, -14, 0))
                k.box("book_a", (x0 - 0.04, by, z0 + 0.12), (0.03, 0.2, 0.25), r=0.002, seg=1, rot=(0, -14, 0))
            elif kind == "vase":
                k.lathe("decor", (x0, by - 0.02, z0), [(0.0, 0.0), (0.05, 0.0), (0.07, 0.05), (0.068, 0.12), (0.04, 0.17),
                                                       (0.028, 0.2), (0.032, 0.21), (0.0, 0.2)], seg=32)
            elif kind == "vase_tall":
                k.lathe("decor_dark", (x0, by - 0.02, z0), [(0.0, 0.0), (0.04, 0.0), (0.055, 0.1), (0.045, 0.22),
                                                            (0.02, 0.28), (0.024, 0.3), (0.0, 0.29)], seg=32)
            elif kind == "bowl":
                k.lathe("decor", (x0, by - 0.03, z0), [(0.0, 0.0), (0.05, 0.0), (0.09, 0.03), (0.11, 0.07), (0.104, 0.072),
                                                       (0.085, 0.035), (0.0, 0.02)], seg=32)
                k.box("decor_dark", (x0 + 0.02, by - 0.03, z0 + 0.055), (0.07, 0.05, 0.05), r=0.01, seg=2)
    books = {"albedo": tex.book_spines(256, 256, 81), "rough": 0.75}
    books_b = {"albedo": tex.book_spines(256, 256, 87, ("#e3ddd1", "#1f1d1b", "#a58866", "#c8c0b2", "#556270", "#7a5a44")),
               "rough": 0.75}
    return k.finish(e, {car: "walnut_veneer", "plinth": "furniture_dark", "fronts": "black_oak_veneer#8a8580",
                        "back": "walnut_smoked", "led": "led", "decor": "ceramic", "decor_dark": "black_glass",
                        "book_a": "linen_rough#d6cec0", "book_b": "linen_rough#3b3835"},
                    own={"books": books, "books_b": books_b}, pivot="back")


def desk_executive(e):
    """Executive desk 1.8 × 0.8 × 0.75: 40 mm walnut top, dark drawer pedestal on the right (two drawers + file drawer,
    black grip channels), slim dark panel leg on the left, recessed modesty panel."""
    k = Kit(e["id"])
    W, D, H, tt = 1.8, 0.8, 0.75, 0.04
    k.box("top", (0, 0, H - tt / 2), (W, D, tt), r=0.004, seg=2)
    under = H - tt
    # left panel leg
    k.box("body", (-W / 2 + 0.08, 0.0, under / 2), (0.05, D - 0.08, under), r=0.003, seg=2)
    # right pedestal
    pw, pd = 0.46, D - 0.06
    px = W / 2 - 0.05 - pw / 2
    k.box("body", (px, 0.0, (under + 0.02) / 2 + 0.005), (pw, pd, under - 0.03), r=0.003, seg=2)
    k.box("plinth", (px, 0.02, 0.0125), (pw - 0.04, pd - 0.06, 0.025))
    fy = -pd / 2 - 0.009
    z = 0.035
    for h in (0.33, 0.155, 0.155):
        k.box("fronts", (px, fy, z + h / 2), (pw - 0.004, 0.018, h - 0.004), r=0.002, seg=1)
        k.box("handle", (px, fy - 0.009, z + h - 0.02), (pw - 0.12, 0.004, 0.012))
        z += h
    # modesty panel between the leg and the pedestal
    x0, x1 = -W / 2 + 0.105, px - pw / 2
    k.box("body", ((x0 + x1) / 2, D / 2 - 0.1, under - 0.2), (x1 - x0, 0.018, 0.36))
    return k.finish(e, {"top": "walnut_smoked#b08a6a", "body": "black_oak_veneer#5d5955", "fronts": "black_oak_veneer#5d5955",
                        "plinth": "furniture_dark", "handle": "black_metal"})


def office_chair_mesh(e):
    """Black ergonomic office chair: five-star base on casters, gas lift, upholstered seat, curved mesh back with lumbar
    bulge in a black frame, T-armrests. Seat 0.47, overall ≈ 0.66 × 0.66 × 1.12."""
    k = Kit(e["id"])
    fr = "frame"
    # base: hub, five tapered spokes, casters
    k.cyl(fr, (0, 0, 0.1), 0.045, 0.05, seg=24, r=0.008)
    R = 0.32
    for i in range(5):
        a = 2 * math.pi * i / 5 + math.pi / 2
        c, s = math.cos(a), math.sin(a)
        k.box(fr, (c * R / 2, s * R / 2, 0.098), (R, 0.045, 0.03), r=0.01, seg=2, rot=(0, 3, math.degrees(a)), taper=(1, 0.8))
        tx, ty = c * (R - 0.01), s * (R - 0.01)
        k.cyl(fr, (tx, ty, 0.07), 0.012, 0.03, seg=12)
        for side in (-1, 1):
            k.cyl("caster", (tx + side * 0.012 * -s, ty + side * 0.012 * c, 0.03), 0.03, 0.018, seg=20, r=0.004,
                  rot=(0, 90, math.degrees(a) + 90))
    # gas lift
    k.cyl(fr, (0, 0, 0.21), 0.03, 0.18, seg=24)
    k.cyl("chrome", (0, 0, 0.35), 0.017, 0.12, seg=20)
    k.box(fr, (0, 0.02, 0.425), (0.22, 0.26, 0.05), r=0.012, seg=2)
    # seat shell + cushion
    k.box(fr, (0, -0.01, 0.46), (0.5, 0.48, 0.03), r=0.012, seg=2)
    k.box("seat", (0, -0.015, 0.49), (0.5, 0.49, 0.05), r=0.022, seg=4, bulge=0.012)
    k.box("seat", (0, -0.25, 0.487), (0.48, 0.05, 0.05), r=0.022, seg=4, rot=(-20, 0, 0), soft=True)   # waterfall edge
    # back: curved mesh plate in a frame, lumbar bulge, reclined 12°
    rec = math.radians(12)
    bz0, bh, by0 = 0.6, 0.52, 0.25

    def back(u, v, grow=0.0):
        w = 0.44 + 0.05 * v - 0.08 * max(0.0, (v - 0.85) / 0.15) ** 2 + grow
        x = (u - 0.5) * w
        y = by0 + 0.07 * (2 * u - 1) ** 2 * -1 - 0.035 * math.exp(-((v - 0.28) / 0.16) ** 2)
        return (x, y + v * bh * math.sin(rec), bz0 + v * bh * math.cos(rec))

    shell(k, "mesh", back, 12, 12, 0.008, uv="front")
    rim = [back(i / 16, 0, 0.012) for i in range(17)] + [back(1, j / 16, 0.012) for j in range(1, 17)] + \
          [back(i / 16, 1, 0.012) for i in range(15, -1, -1)] + [back(0, j / 16, 0.012) for j in range(15, 0, -1)]
    k.tube(fr, [(x, y + 0.004, z) for x, y, z in rim], 0.013, seg=8, closed=True)
    # spine from the mechanism up to the back
    k.tube(fr, [(0, 0.12, 0.43), (0, 0.24, 0.45), (0, by0 + 0.02, 0.52), (0, by0 + 0.04, bz0 + 0.12)], 0.022, seg=12)
    # arms: bracket under the seat, post, pad
    for s in (-1, 1):
        k.box(fr, (s * 0.2, 0.0, 0.44), (0.16, 0.05, 0.022), r=0.006, seg=2)
        k.box(fr, (s * 0.28, 0.02, 0.55), (0.03, 0.05, 0.22), r=0.01, seg=2)
        k.box("arm_pad", (s * 0.28, -0.01, 0.672), (0.08, 0.26, 0.026), r=0.012, seg=3)
    return k.finish(e, {fr: "furniture_dark", "caster": "black_metal", "chrome": "chrome", "seat": "wool_felt#2e2e2e",
                        "arm_pad": "leather_light#2a2a2a"},
                    own={"mesh": {"albedo": mesh_weave(), "rough": 0.7}})


def monitor_27(e):
    """27\" monitor 0.62 × 0.37 on a slim column stand with a flat foot; the screen is its own slot "screen"."""
    k = Kit(e["id"])
    sw, sh = 0.615, 0.365
    zc, tilt = 0.29, -5
    k.box("frame", (0, 0, zc), (sw, 0.012, sh), r=0.003, seg=2, rot=(tilt, 0, 0))
    k.box("frame", (0, 0.018, zc + 0.01), (0.36, 0.03, 0.22), r=0.012, seg=2, rot=(tilt, 0, 0))
    k.panel("screen", (0, -0.0065, zc), sw - 0.012, sh - 0.014, rot=(tilt, 0, 0))
    # stand
    k.box("stand", (0, 0.05, 0.006), (0.24, 0.18, 0.012), r=0.005, seg=2)
    k.box("stand", (0, 0.07, 0.17), (0.07, 0.018, 0.32), r=0.006, seg=2, rot=(-8, 0, 0))
    return k.finish(e, {"frame": "furniture_dark", "stand": "black_metal", "screen": "screen"})


def keyboard_mouse_pad(e):
    """Desk set: felt desk pad 0.8 × 0.35, slim light keyboard with keys and a mouse."""
    k = Kit(e["id"])
    k.box("pad", (0, 0, 0.0015), (0.8, 0.35, 0.003), r=0.0015, seg=1)
    kx, ky, kw, kd = -0.06, 0.02, 0.43, 0.13
    k.box("body", (kx, ky, 0.009), (kw, kd, 0.012), r=0.004, seg=2, rot=(-2, 0, 0))
    rows = [(14, 0), (14, 0), (13, 0.012), (12, 0.02), (11, 0.03)]
    kp = 0.0265
    for r, (n, off) in enumerate(rows):
        yy = ky + kd / 2 - 0.02 - r * 0.022
        x = kx - kw / 2 + 0.018 + off
        for c in range(n):
            wk = kp - 0.004
            if r == 4 and c == 4:
                wk = kp * 4 - 0.004
            k.box("keys", (x + wk / 2, yy, 0.0165), (wk, 0.018, 0.004))
            x += wk + 0.004
            if x > kx + kw / 2 - 0.025:
                break
    k.box("body", (0.28, 0.0, 0.013), (0.062, 0.11, 0.024), r=0.012, seg=3, bulge=0.012)
    return k.finish(e, {"pad": "wool_felt#3a3836", "body": "white_metal", "keys": "soft_white"})


ENTRIES = [
    ("bookcase_wall_led", "Стеллаж-модуль орех с LED-полками, 1,2 × 2,4 м", "storage", bookcase_wall_led, {"pivot": "back"}),
    ("desk_executive", "Стол руководителя 1,8 м с тумбой, орех", "tables", desk_executive, {}),
    ("office_chair_mesh", "Кресло офисное сетчатое, чёрное", "seating", office_chair_mesh, {}),
    ("monitor_27", "Монитор 27\" на подставке", "utility", monitor_27, {}),
    ("keyboard_mouse_pad", "Клавиатура, мышь и коврик на стол", "decor", keyboard_mouse_pad, {}),
]
