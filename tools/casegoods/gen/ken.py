"""«Кен» (П3.596): шкаф 0.02, шкаф-витрина 0.01, тумба ТВ 0.03 — by catalogue (no instructions): the one interior photo on
catalogue p. 70 (no cut-outs, no swatch in the catalogue).

Construction read off the photo: carcass ЛДСП 16 «Дуб Онтарио» — top and bottom over the full width, sides between them,
back ХДФ in grooves; inset fronts ЛДСП 16 flush with the carcass edges, gaps 2 mm; the UV print «ёлочка» on some
fronts (chevrons of thin dark lines at 45°, apexes up, every 70 mm) drawn as fine V-grooves; black edge pulls ~56 mm on
the top edge of the lower fronts; black metal legs Ø20, 150 high, near the corners. B = the carcass depth 400; pulls
stand out of it.

    python3 tools/casegoods/gen/ken.py        # writes Designs/ken-*.json and gen/ken_catalog.json
"""
import json
import os

from common import dump

T, D, HL, G = 16, 400, 150, 2
FZ = D - T                                   # inset fronts: z 384 … 400
PITCH = 70


def carcass(W, H, backs=None):
    p = [
        {"id": "bottom", "box": [0, HL, 0, W, HL + T, D], "grain": "x"},
        {"id": "top", "box": [0, H - T, 0, W, H, D], "grain": "x"},
        {"id": "side-l", "box": [0, HL + T, 0, T, H - T, D], "grain": "y"},
        {"id": "side-r", "box": [W - T, HL + T, 0, W, H - T, D], "grain": "y"},
    ]
    xs = [10] + list(backs or []) + [W - 10]
    for i in range(len(xs) - 1):
        p.append({"id": f"back-{i + 1}" if len(xs) > 2 else "back", "kind": "back",
                  "box": [xs[i], HL + 10, 6, xs[i + 1], H - 10, 9.5]})
    return p


def legs(xs, zs=(36, D - 36)):
    out, k = [], 0
    for x in xs:
        for z in zs:
            k += 1
            out.append({"id": f"leg-{k}", "kind": "tube", "mat": "black", "box": [x - 10, 0, z - 10, x + 10, HL, z + 10]})
    return out


def clip(p0, p1, r):
    """Liang–Barsky: the part of segment p0-p1 inside rect r = (x0, y0, x1, y1), or None."""
    (xa, ya), (xb, yb) = p0, p1
    dx, dy = xb - xa, yb - ya
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, xa - r[0]), (dx, r[2] - xa), (-dy, ya - r[1]), (dy, r[3] - ya)):
        if p == 0:
            if q < 0:
                return None
            continue
        t = q / p
        if p < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 > t1:
            return None
    return (xa + t0 * dx, ya + t0 * dy), (xa + t1 * dx, ya + t1 * dy)


def herringbone(x0, y0, x1, y1, first, margin=5):
    """The «ёлочка» print: chevrons (apex up on the front's middle line) every PITCH mm, the lowest apex `first` mm above
    the front's bottom edge, arms at 45° to the edges."""
    cx, half = (x0 + x1) / 2, (x1 - x0) / 2
    r = (x0 + margin, y0 + margin, x1 - margin, y1 - margin)
    lines, ya = [], y0 + first
    while ya - half < r[3]:
        for s in (-1, 1):
            c = clip((cx, ya), (cx + s * half, ya - half), r)
            if c and abs(c[1][0] - c[0][0]) > 4:
                lines.append([round(v, 1) for v in (*c[0], *c[1])])
        ya += PITCH
    return {"type": "grooves", "w": 2.5, "depth": 1, "flute": "v", "lines": lines}


def front(fid, x0, x1, y0, y1, first=None):
    f = {"id": fid, "kind": "front", "box": [x0, y0, FZ, x1, y1, D], "grain": "y", "edge": 1}
    if first is not None:
        f["face"] = herringbone(x0, y0, x1, y1, first)
    return f


def pull(hid, x, ytop):
    """Black edge pull on the front's top edge."""
    return {"id": hid, "kind": "handle", "model": "bar", "mat": "black", "at": [x, ytop - 6], "dir": "right",
            "d": 56, "band": 10, "t": 6, "standoff": 3, "z": D}


def shelf(pid, x0, x1, ytop, fixed=False):
    return {"id": pid, "box": [x0 + (0 if fixed else 1), ytop - T, 10 if fixed else 20, x1 - (0 if fixed else 1), ytop, FZ - 2],
            "grain": "x"}


def door(p, m, name, fr, hinge, handle=None):
    p.append(fr)
    ids = [fr["id"]]
    if handle:
        p.append(handle)
        ids.append(handle["id"])
    m.append({"type": "door", "name": name, "parts": ids, "hinge": hinge, "angle": 100})


def cabinet_0_02():
    """Шкаф 1040×400×1196: four inset doors 2×2, the print on the upper right and the lower left one, pulls on the lower
    doors' top edges (the upper doors are opened by their bottom edge above the pull)."""
    W, H = 1040, 1196
    p = carcass(W, H)
    y0, y1 = HL + T, H - T                      # opening 166 … 1180
    xm, ym = W / 2, (y0 + y1) / 2               # 520, 673
    p += [shelf("shelf-fixed", T, W - T, ym + 8, fixed=True),
          shelf("shelf-low", T, W - T, 430), shelf("shelf-up", T, W - T, 940)]
    m = []
    xl, xr = (T + G, xm - G / 2), (xm + G / 2, W - T - G)
    lo, up = (y0 + G, ym - G / 2), (ym + G / 2, y1 - G)
    door(p, m, "door_up_l", front("f-up-l", *xl, *up), "left")
    door(p, m, "door_up_r", front("f-up-r", *xr, *up, first=45), "right")
    door(p, m, "door_low_l", front("f-low-l", *xl, *lo, first=87), "left", pull("h-low-l", (xl[0] + xl[1]) / 2, lo[1]))
    door(p, m, "door_low_r", front("f-low-r", *xr, *lo), "right", pull("h-low-r", (xr[0] + xr[1]) / 2, lo[1]))
    p += legs([36, W - 36])
    return dump("ken-0-02", [W, D, H], p, m)


def vitrine_0_01():
    """Шкаф-витрина 540×400×1914: an upper door with a big glass (rails 167 / 180, stiles 20) over a printed lower door."""
    W, H = 540, 1914
    p = carcass(W, H)
    y0, y1 = HL + T, H - T                      # 166 … 1898
    joint = 867.5
    p += [shelf("shelf-fixed", T, W - T, joint + 8, fixed=True), shelf("shelf-low", T, W - T, 526),
          shelf("shelf-glass-1", T, W - T, 1038), shelf("shelf-glass-2", T, W - T, 1390)]
    m = []
    x0, x1 = T + G, W - T - G
    uy0, uy1 = joint + G / 2, y1 - G
    gx0, gx1, gy0, gy1 = x0 + 20, x1 - 20, uy0 + 167, uy1 - 180
    outline = (f"M {x0} {uy0} H {x1} V {uy1} H {x0} Z "
               f"M {gx0} {gy0} V {gy1} H {gx1} V {gy0} Z")
    up = {"id": "f-up", "kind": "front", "box": [x0, uy0, FZ, x1, uy1, D], "shape": "path", "outline": outline, "grain": "y", "edge": 1}
    glass = {"id": "f-up-glass", "kind": "glass", "box": [gx0, gy0, FZ + 6, gx1, gy1, FZ + 10]}
    p += [up, glass]
    m.append({"type": "door", "name": "door_up", "parts": ["f-up", "f-up-glass"], "hinge": "left", "angle": 100})
    lo = (y0 + G, joint - G / 2)
    door(p, m, "door_low", front("f-low", x0, x1, *lo, first=100), "left", pull("h-low", W / 2, lo[1]))
    p += legs([36, W - 36])
    return dump("ken-0-01", [W, D, H], p, m)


def tv_0_03():
    """Тумба ТВ 1540×400×560: printed doors at the ends, an open niche with a shelf between two partitions."""
    W, H = 1540, 560
    p = carcass(W, H)
    y0, y1 = HL + T, H - T                      # 166 … 544
    w = (W - 2 * T - 2 * T) / 3                 # three openings of 492
    a = [T, T + w, T + w + T, T + 2 * w + T, T + 2 * w + 2 * T, W - T]
    p += [{"id": "part-1", "box": [a[1], y0, 10, a[2], y1, D], "grain": "y"},
          {"id": "part-2", "box": [a[3], y0, 10, a[4], y1, D], "grain": "y"},
          {"id": "shelf-niche", "box": [a[2], 347, 10, a[3], 363, D], "grain": "x"},
          shelf("shelf-l", a[0], a[1], 363), shelf("shelf-r", a[4], a[5], 363)]
    m = []
    fy = (y0 + G, y1 - G)
    for name, (x0, x1), hinge in (("door_l", (a[0] + G, a[1] - G), "left"), ("door_r", (a[4] + G, a[5] - G), "right")):
        door(p, m, name, front(f"f-{name}", x0, x1, *fy, first=87), hinge, pull(f"h-{name}", (x0 + x1) / 2, fy[1]))
    p += legs([36, W / 2, W - 36])
    return dump("ken-0-03", [W, D, H], p, m)


FIN = "ken-ontario"
CATALOG = {
    "finishes": [
        {"id": FIN, "name": "Дуб Онтарио + УФ печать «ёлочка»", "body": "door_enamel_whitey#a8937c", "swatch": "#a8937c"}
    ],
    "profiles": {},
    "collections": [
        {"id": "ken", "name": "Кен", "brand": "Пинскдрев", "finishes": [FIN], "metal": "black",
         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 70 (все модули по каталогу, без инструкций). Корпус ЛДСП 16 "
                 "«Дуб Онтарио» (крышка и дно во всю ширину), задняя стенка ХДФ в пазах, вкладные фасады ЛДСП 16 с УФ печатью "
                 "«ёлочка», чёрные торцевые ручки, чёрные металлические опоры Ø20×150."}
    ],
    "models": [
        {"id": "ken-0-01", "code": "П3.596.0.01", "name": "Шкаф-витрина «Кен»", "collection": "ken", "category": "living",
         "size": [540, 400, 1914], "page": 70, "note": "по каталогу, без инструкции"},
        {"id": "ken-0-02", "code": "П3.596.0.02", "name": "Шкаф «Кен»", "collection": "ken", "category": "living",
         "size": [1040, 400, 1196], "page": 70, "note": "по каталогу, без инструкции"},
        {"id": "ken-0-03", "code": "П3.596.0.03", "name": "Тумба ТВ «Кен»", "collection": "ken", "category": "living",
         "size": [1540, 400, 560], "page": 70, "note": "по каталогу, без инструкции"},
    ],
}


def write_catalog():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ken_catalog.json")
    with open(path, "w") as fh:
        json.dump(CATALOG, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


if __name__ == "__main__":
    print(write_catalog())
    print(vitrine_0_01())
    print(cabinet_0_02())
    print(tv_0_03())
