"""Walk-in closet (reference tile «Гардеробная»): open walnut wardrobe modules with LED under the shelves (hanging
section with garments, shelves with folded clothes and a drawer block), a drawer island and a tufted rectangular ottoman."""
import math

from kit import Kit

W, D, H = 1.0, 0.6, 2.4          # module: width, depth, height
T = 0.03                         # side / shelf thickness
PLINTH = 0.08
CARCASS = {"carcass": "walnut_veneer", "plinth": "furniture_dark", "led": "led", "rail": "steel"}
CLOTHES = {"cloth_a": "wool_felt#4a4846", "cloth_b": "cotton_poplin#ece7dd", "cloth_c": "linen_rough#b9a88f",
           "cloth_d": "wool_herringbone#7a6552", "box": "linen_rough#ece6da"}


def _carcass(k, shelves):
    """Open module: two sides, back, top, bottom on a recessed plinth; fixed shelves at the given heights (top faces),
    each with an LED strip under its front edge. Back at +Y, front at -Y."""
    x0, x1 = -W / 2, W / 2
    for x in (x0 + T / 2, x1 - T / 2):
        k.box("carcass", (x, 0, H / 2), (T, D, H), r=0.003, seg=1)
    k.box("carcass", (0, D / 2 - 0.009, H / 2), (W - 2 * T + 0.002, 0.018, H - 0.002), seg=1)         # back
    k.box("carcass", (0, 0, H - T / 2), (W - 2 * T + 0.002, D, T), r=0.002, seg=1)                     # top
    k.box("carcass", (0, 0, PLINTH + 0.01), (W - 2 * T + 0.002, D, 0.02), r=0.002, seg=1)              # bottom
    k.box("plinth", (0, 0.02, PLINTH / 2), (W - 2 * T, D - 0.08, PLINTH), seg=1)                        # toe kick
    for z in list(shelves) + [H - T]:
        if z < H - T:
            k.box("carcass", (0, -0.005, z - T / 2), (W - 2 * T + 0.002, D - 0.02, T), r=0.002, seg=1)
        k.box("led", (0, -D / 2 + 0.035, z - T - 0.003), (W - 2 * T - 0.04, 0.012, 0.006))


def _stack(k, x, y, z, n, w=0.32, d=0.3, h=0.05, seed=0, slots=("cloth_a", "cloth_b", "cloth_c", "cloth_d")):
    """Stack of folded clothes: soft slabs, slightly jittered; returns the top height."""
    for i in range(n):
        s = slots[(seed + i * 3 + i // 2) % len(slots)]
        j = ((seed * 7 + i * 5) % 5 - 2) * 0.004
        k.box(s, (x + j, y + j * 0.5, z + h * (i + 0.5)), (w - abs(j) * 2, d, h - 0.004), r=0.016, seg=2, soft=True,
              rot=(0, 0, j * 150))
    return z + n * h


def _storage_box(k, x, y, z, w=0.34, d=0.32, h=0.2):
    """Lidded storage box (fabric), lid slightly bigger."""
    k.box("box", (x, y, z + h / 2 - 0.01), (w, d, h - 0.02), r=0.008, seg=2)
    k.box("box", (x, y, z + h - 0.015), (w + 0.01, d + 0.01, 0.03), r=0.008, seg=2)
    k.box("carcass", (x, y - d / 2 - 0.006, z + h * 0.55), (0.08, 0.006, 0.025), r=0.003, seg=1)   # pull tab


def _garment(k, x, y, top, length, width, thick, slot, lean=0.0, turn=0.0, coat=False):
    """A garment on a hanger seen side-on: tapered soft slab (shoulders on top), with a wire hanger above it."""
    flare = 0.9 if coat else 0.97
    k.box(slot, (x, y, top - length / 2), (thick, width, length), r=min(0.02, thick / 2 - 0.002), seg=2, soft=True,
          taper=(0.55, flare), rot=(lean, 0, turn))
    k.box(slot, (x, y, top - 0.02), (thick * 0.7, width * 0.35, 0.04), r=0.012, seg=2, soft=True, rot=(lean, 0, turn))
    return top


def _hanger(k, x, y, top, rail_z):
    hw = 0.2
    k.tube("rail", [(x, y - hw, top - 0.01), (x, y, top + 0.05), (x, y + hw, top - 0.01), (x, y - hw, top - 0.01)],
           0.004, seg=4)
    k.tube("rail", [(x, y, top + 0.05), (x, y, rail_z + 0.005), (x, y + 0.02, rail_z + 0.025), (x, y + 0.035, rail_z + 0.01)],
           0.0025, seg=4)


def closet_hanging_unit(e):
    """Open walnut module 1.0 × 0.6 × 2.4: hanging rail with eight garments, shelf above with folded items and a box,
    shoe shelf below; LED strips under the shelves. Pivot at the back."""
    k = Kit(e["id"])
    shelf_top, shoe_top = 2.0, 0.36
    _carcass(k, [shelf_top, shoe_top])
    rail_z, ry = 1.9, -0.02
    k.cyl("rail", (0, ry, rail_z), 0.012, W - 2 * T, seg=12, rot=(0, 90, 0))
    for x in (-W / 2 + T + 0.01, W / 2 - T - 0.01):
        k.box("rail", (x, ry, rail_z + 0.01), (0.02, 0.03, 0.05), r=0.004, seg=1)
    # garments: (x, length, width, thickness, slot, coat)
    rows = [(-0.40, 1.05, 0.48, 0.07, "cloth_a", True), (-0.31, 1.0, 0.47, 0.065, "cloth_d", True),
            (-0.22, 0.78, 0.45, 0.045, "cloth_b", False), (-0.14, 0.8, 0.44, 0.045, "cloth_c", False),
            (-0.05, 0.76, 0.45, 0.045, "cloth_b", False), (0.05, 0.95, 0.46, 0.06, "cloth_a", True),
            (0.15, 0.72, 0.44, 0.05, "cloth_c", False), (0.25, 0.9, 0.46, 0.06, "cloth_d", True),
            (0.34, 0.74, 0.44, 0.045, "cloth_a", False), (0.42, 0.78, 0.45, 0.045, "cloth_b", False)]
    for i, (x, ln, wd, th, s, coat) in enumerate(rows):
        top = rail_z - 0.085
        _garment(k, x, ry, top, ln, wd, th, s, lean=(i % 3 - 1) * 1.5, turn=(i % 2 * 2 - 1) * 3, coat=coat)
        _hanger(k, x, ry, top + 0.01, rail_z)
    # upper compartment
    z = shelf_top
    _stack(k, -0.27, -0.02, z, 5, seed=1)
    _stack(k, 0.07, -0.02, z, 4, seed=2)
    _storage_box(k, 0.32, 0.0, z, w=0.26, d=0.34, h=0.24)
    # shoes: four pairs on the bottom shelf
    for i in range(4):
        cx = -0.36 + i * 0.24
        s = ("shoes", "shoes_dark")[i % 2]
        for dx in (-0.055, 0.055):
            k.box(s, (cx + dx, -0.04, shoe_top + 0.045), (0.09, 0.27, 0.09), r=0.03, seg=2, taper=(0.8, 0.55), soft=True)
    # base shelf items: two boxes on the bottom
    _storage_box(k, -0.22, 0.0, PLINTH + 0.02, w=0.4, d=0.4, h=0.22)
    _storage_box(k, 0.22, 0.0, PLINTH + 0.02, w=0.4, d=0.4, h=0.22)
    return k.finish(e, {**CARCASS, **CLOTHES, "shoes": "leather_brown", "shoes_dark": "leather_brown_soft#3a3230"},
                    pivot="back")


def _drawers(k, x0, x1, z0, z1, n, front_y, gap=0.005):
    """A column of n drawer fronts between x0..x1, z0..z1 at front_y (-Y side), with a black bar pull on each."""
    h = (z1 - z0) / n
    for i in range(n):
        zc = z0 + h * (i + 0.5)
        k.box("fronts", ((x0 + x1) / 2, front_y, zc), (x1 - x0 - gap, 0.02, h - gap), r=0.002, seg=1)
        k.box("handle", ((x0 + x1) / 2, front_y - 0.018, zc + h * 0.3), (min(0.4, (x1 - x0) * 0.5), 0.016, 0.012),
              r=0.003, seg=1)
        for dx in (-0.15, 0.15):
            if (x1 - x0) > 0.5:
                k.box("handle", ((x0 + x1) / 2 + dx, front_y - 0.006, zc + h * 0.3), (0.012, 0.014, 0.012), seg=1)


def closet_shelf_unit(e):
    """Open walnut module 1.0 × 0.6 × 2.4: drawer block (3 drawers) at the bottom, four shelves above with stacks of
    folded clothes and lidded storage boxes, LED under every shelf. Pivot at the back."""
    k = Kit(e["id"])
    counter = 0.88
    shelves = [counter + T, 1.25, 1.62, 1.99]
    _carcass(k, shelves)
    _drawers(k, -W / 2 + T, W / 2 - T, PLINTH + 0.02, counter, 3, -D / 2 + 0.012)
    z = shelves[0]
    _stack(k, -0.24, -0.03, z, 5, seed=3)
    _stack(k, 0.2, -0.03, z, 4, seed=4)
    z = shelves[1]
    _storage_box(k, -0.23, -0.02, z, h=0.22)
    _storage_box(k, 0.2, -0.02, z, h=0.22)
    z = shelves[2]
    _stack(k, -0.26, -0.03, z, 4, seed=5, h=0.06)
    _stack(k, 0.05, -0.03, z, 5, seed=6)
    _storage_box(k, 0.33, -0.02, z, w=0.22, d=0.3, h=0.18)
    z = shelves[3]
    _stack(k, -0.25, -0.03, z, 3, seed=7, h=0.07)
    _storage_box(k, 0.18, -0.02, z, w=0.42, h=0.26)
    return k.finish(e, {**CARCASS, **CLOTHES, "fronts": "walnut_veneer", "handle": "black_metal"}, pivot="back")


def closet_drawer_island(e):
    """Closet island 1.2 × 0.6 × 0.9: walnut body on a recessed plinth, three drawers on each long side, bronze-glass
    display top over a shallow jewellery tray."""
    k = Kit(e["id"])
    w, d, h = 1.2, 0.6, 0.9
    k.box("plinth", (0, 0, 0.04), (w - 0.08, d - 0.08, 0.08), seg=1)
    k.box("carcass", (0, 0, 0.08 + (h - 0.08 - 0.02) / 2), (w, d - 0.04, h - 0.1), r=0.003, seg=1)
    for sgn in (-1, 1):
        k.box("carcass", (sgn * (w / 2 - 0.015), 0, 0.08 + (h - 0.1) / 2), (0.03, d, h - 0.1), r=0.003, seg=1)
    for sgn in (-1, 1):
        for x0, x1 in ((-w / 2 + 0.03, 0.0), (0.0, w / 2 - 0.03)):
            n = 3
            zc0, zc1 = 0.1, h - 0.1
            hh = (zc1 - zc0) / n
            for j in range(n):
                zc = zc0 + hh * (j + 0.5)
                y = sgn * (d / 2 - 0.01)
                k.box("fronts", ((x0 + x1) / 2, y, zc), (x1 - x0 - 0.005, 0.02, hh - 0.005), r=0.002, seg=1)
                k.box("handle", ((x0 + x1) / 2, y + sgn * 0.017, zc + hh * 0.3), (0.26, 0.016, 0.012), r=0.003, seg=1)
    # top: walnut frame around a glass lid over a tray
    k.box("carcass", (0, 0, h - 0.095), (w, d, 0.01), seg=1)
    for sgn in (-1, 1):
        k.box("carcass", (0, sgn * (d / 2 - 0.02), h - 0.045), (w, 0.04, 0.09), r=0.003, seg=1)
        k.box("carcass", (sgn * (w / 2 - 0.02), 0, h - 0.045), (0.04, d - 0.08, 0.09), r=0.003, seg=1)
    k.box("tray", (0, 0, h - 0.087), (w - 0.08, d - 0.08, 0.006), seg=1)
    for i in range(5):
        k.box("carcass", (-0.44 + i * 0.22, 0, h - 0.075), (0.012, d - 0.08, 0.02), seg=1)
    k.box("glass", (0, 0, h - 0.004), (w - 0.002, d - 0.002, 0.008), r=0.002, seg=1)
    k.box("led", (0, 0, h - 0.012), (w - 0.1, 0.01, 0.004))
    return k.finish(e, {**CARCASS, "fronts": "walnut_veneer", "handle": "black_metal", "tray": "velvet#3b3431",
                        "glass": "glass"})


def ottoman_rect_tufted(e):
    """Rectangular upholstered ottoman 1.1 × 0.6 × 0.45: rounded body on a recessed dark plinth, domed top with a
    diamond pattern of buttons pulled into the padding, piped rim."""
    k = Kit(e["id"])
    Wo, Do, Ho = 1.1, 0.6, 0.45
    base, rim = 0.035, 0.33
    k.box("plinth", (0, 0, base / 2), (Wo - 0.1, Do - 0.1, base), seg=1)
    k.box("upholstery", (0, 0, base + (rim + 0.012 - base) / 2), (Wo, Do, rim + 0.012 - base), r=0.03, seg=3, soft=True)
    buttons = [(-0.375, -0.15), (-0.125, -0.15), (0.125, -0.15), (0.375, -0.15), (-0.25, 0), (0, 0), (0.25, 0),
               (-0.375, 0.15), (-0.125, 0.15), (0.125, 0.15), (0.375, 0.15)]
    # domed top: height field with dimples at the buttons
    nx, ny = 56, 32
    hw, hd, dome = Wo / 2 + 0.004, Do / 2 + 0.004, Ho - rim
    verts, faces = [], []

    def hgt(x, y):
        dd = min(hw - abs(x), hd - abs(y))
        r = math.sin(min(1.0, dd / 0.07) * math.pi / 2) ** 0.8
        dip = sum(math.exp(-((x - bx) ** 2 + (y - by) ** 2) / 0.0016) for bx, by in buttons)
        crease = 0.0
        for bx, by in buttons:            # soft folds between neighbouring buttons along the diagonals
            u, v = (x - bx) / 0.125, (y - by) / 0.15
            if 0 < u < 1 and abs(v - u) < 0.25:
                crease += (1 - abs(v - u) / 0.25) * math.sin(u * math.pi) * 0.3
        return rim + dome * r - 0.04 * min(1, dip) * r - 0.004 * crease * r

    for j in range(ny + 1):
        for i in range(nx + 1):
            x, y = -hw + 2 * hw * i / nx, -hd + 2 * hd * j / ny
            verts.append((x, y, hgt(x, y)))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    k.mesh("upholstery", verts, faces, smooth="soft")
    for bx, by in buttons:
        k.cyl("button", (bx, by, hgt(bx, by) + 0.003), 0.011, 0.01, seg=12, r=0.003)
    # piping around the top seam
    pts, r0 = [], 0.03
    for cx, cy, a0 in ((Wo / 2 - r0, Do / 2 - r0, 0), (-Wo / 2 + r0, Do / 2 - r0, 90), (-Wo / 2 + r0, -Do / 2 + r0, 180),
                       (Wo / 2 - r0, -Do / 2 + r0, 270)):
        for s in range(5):
            a = math.radians(a0 + s * 22.5)
            pts.append((cx + (r0 + 0.004) * math.cos(a), cy + (r0 + 0.004) * math.sin(a), rim + 0.01))
    pts.append(pts[0])
    k.tube("upholstery", pts, 0.007, seg=6)
    return k.finish(e, {"upholstery": "velvet#8a735f", "button": "velvet#5a4739", "plinth": "furniture_dark"})


ENTRIES = [
    ("closet_hanging_unit", "Гардеробный модуль с одеждой на штанге, орех, LED", "storage", closet_hanging_unit, {"pivot": "back"}),
    ("closet_shelf_unit", "Гардеробный модуль с полками и ящиками, орех, LED", "storage", closet_shelf_unit, {"pivot": "back"}),
    ("closet_drawer_island", "Гардеробный остров с ящиками и витриной 1,2 м", "storage", closet_drawer_island, {}),
    ("ottoman_rect_tufted", "Пуф-банкетка прямоугольная с каретной стяжкой", "seating", ottoman_rect_tufted, {}),
]
