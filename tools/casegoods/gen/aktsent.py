"""«Акцент» (Pinskdrev П3.595, hall set): all 10 modules by catalogue + product photos (no instructions exist).

Sources: catalogue p. 132 (printed 260–261: the interior with 3.05, 3.09, 3.04, 3.02, 3.03; 3/4 cut-outs of every module
closed and open; the swatches «Персидский жемчуг» (fronts) / «Дуб Мадура» (carcass)) and the product photos of every
module on pinskdrev.by (front-on, 3/4, open). The site photos are printed ≈ 4–8 % wider than their true proportion:
x is scaled by the catalogue L and y by the catalogue H, each on its own.

Construction (one scheme, measured on the photos):
* carcass ЛДСП 16 «Дуб Мадура»: a bottom over the full width on metal feet, the sides on it, a top over the sides; ХДФ
  back (white, «Персидский жемчуг») in grooves 6 mm from the back edge;
* fronts ЛДСП 16 «Персидский жемчуг», INSET between sides, top and bottom, flush with the carcass edges, 2–3 mm gaps;
* shoe cabinets (B 200): the front bands beside the flaps are 32–35 mm wide on every photo — a 16 mm side plus a 16 mm
  stile (the flap mechanism's mounting strip) at the front; tilt-out flaps hinged at the bottom, opening ≈ 80° (nearly
  flat on the photos), each carrying a grey-blue steel shoe tray (floor on the flap, a 110 mm wall at the hinge end,
  sloped side cheeks, a front lip); feet: satin metal blocks 56 × 56 × 50;
* handles: satin chrome bow handles 208 long, horizontal and centred 50 mm under a front's top edge (the lift-up flap of
  3.08: 50 mm over its bottom edge), vertical by the meeting edge of the 3.05 doors;
* drawer boxes: ЛДСП 16 in the front colour (white on the open photos), ХДФ bottoms, 13 mm runner gaps.

    python3 tools/casegoods/gen/aktsent.py        # writes Designs/aktsent-*.json and gen/aktsent_catalog.json
"""
import json
import os

from common import dump

T = 16                  # ЛДСП
B = 200                 # shoe cabinets' depth
ZF = B - T              # inset fronts' back face
STILE = 16              # mechanism stile behind the front band
BAND = T + STILE        # 32: the carcass band beside the flaps
G = 2                   # front gaps
FEET = 50
TRAY = "door_enamel_whitey#8a9ba7"     # grey-blue steel shoe trays (3.01 / 3.07 open photos: #8496a2 … #8d9fab)
FOOT = "metal"
HERE = os.path.dirname(os.path.abspath(__file__))


def r(v):
    return round(v * 2) / 2


def bow(hid, x, y, z, vertical=False):
    """Satin chrome bow handle 208 (the ends ≈ 30, the middle ≈ 18 high): a bar on two square posts."""
    return {"id": hid, "kind": "handle", "model": "bar", "mat": "metal", "at": [r(x), r(y)], "dir": "up" if vertical else "right",
            "d": 208, "band": 22, "t": 8, "standoff": 22, "post": 12, "section": "square", "z": z}


def feet(x0, x1, zs=(22, B - 22 - 56), inset=35, w=56, h=FEET, xs=None):
    out = []
    xs = xs or [x0 + inset, x1 - inset - w]
    for i, x in enumerate(xs):
        for j, z in enumerate(zs):
            out.append({"id": f"foot-{i + 1}{'ab'[j]}", "mat": FOOT, "edge": 2, "box": [x, 0, z, x + w, h, z + w]})
    return out


def tray(tag, xa, xb, yb, yt, zi=ZF, wall=110):
    """The steel shoe tray behind a tilt-out flap (closed position): floor on the flap's inner face zi, a wall at the hinge
    (bottom) end reaching `wall` into the cabinet, sloped side cheeks, a front lip. Moves with the flap."""
    a, b = xa + 12, xb - 12
    y0, y1 = yb + 12, yt - 12
    zw = zi - wall
    p = [
        {"id": f"tray-floor-{tag}", "mat": TRAY, "edge": 0.5, "box": [a + 1.5, y0, zi - 1.5, b - 1.5, y1, zi]},
        {"id": f"tray-wall-{tag}", "mat": TRAY, "edge": 0.5, "box": [a + 1.5, y0, zw, b - 1.5, y0 + 1.5, zi - 1.5]},
        {"id": f"tray-lip-{tag}", "mat": TRAY, "edge": 0.5, "box": [a + 1.5, y1 - 1.5, zi - 16, b - 1.5, y1, zi - 1.5]},
    ]
    cheek = f"M {zi} {y0} L {zw} {y0} L {zi - 16} {y1} L {zi} {y1} Z"
    for s, (c0, c1) in (("l", (a, a + 1.5)), ("r", (b - 1.5, b))):
        p.append({"id": f"tray-{s}-{tag}", "mat": TRAY, "edge": 0.5, "box": [c0, y0, zw, c1, y1, zi], "shape": "path", "outline": cheek})
    return p


def flap(p, m, tag, x0, x1, y0, y1, handle=False, angle=80):
    """A tilt-out shoe flap (inset front) hinged at the bottom with its tray."""
    f = {"id": f"flap-{tag}", "kind": "front", "box": [r(x0), r(y0), ZF, r(x1), r(y1), B]}
    grp = [f]
    if handle:
        grp.append(bow(f"h-flap-{tag}", (x0 + x1) / 2, y1 - 50, B))
    grp += tray(tag, x0, x1, r(y0), r(y1))
    p += grp
    m.append({"type": "flap", "name": f"flap_{tag}", "parts": [q["id"] for q in grp], "hinge": "bottom", "angle": angle})


def drawer(p, m, tag, x0, x1, y0, y1, bx0, bx1, zb, h=None, depth=None, zf=ZF, zface=B, travel=None):
    """Inset drawer front + ЛДСП box (front colour) with a ХДФ bottom, 13 mm runner gaps already in bx0..bx1."""
    h = h or min(140, y1 - y0 - 45)
    yb = y0 + 18
    z0 = zb
    f = {"id": f"front-{tag}", "kind": "front", "box": [r(x0), r(y0), zf, r(x1), r(y1), zface]}
    box = [
        {"id": f"dr-l-{tag}", "mat": "front", "box": [bx0, yb, z0, bx0 + T, yb + h, zf]},
        {"id": f"dr-r-{tag}", "mat": "front", "box": [bx1 - T, yb, z0, bx1, yb + h, zf]},
        {"id": f"dr-b-{tag}", "mat": "front", "box": [bx0 + T, yb, z0, bx1 - T, yb + h, z0 + T]},
        {"id": f"dr-bottom-{tag}", "kind": "back", "box": [bx0 + 10, yb + 8, z0 + 4, bx1 - 10, yb + 11.5, zf - 2]},
    ]
    hd = bow(f"h-{tag}", (x0 + x1) / 2, y1 - 50, zface)
    grp = [f] + box + [hd]
    p += grp
    m.append({"type": "drawer", "name": f"drawer_{tag}", "parts": [q["id"] for q in grp], "travel": travel or int((zf - z0) * 0.8)})


def shoe_carcass(W, H, x0=0, right_side=True, stiles=True):
    """Bottom (full width) on feet, sides on it, top over the sides, stiles behind the front bands, ХДФ back."""
    yb, yt = FEET + T, H - T
    p = [
        {"id": "bottom", "box": [x0, FEET, 0, x0 + W, yb, B]},
        {"id": "side-l", "box": [x0, yb, 0, x0 + T, yt, B]},
        {"id": "top", "box": [x0, yt, 0, x0 + W, H, B]},
    ]
    if right_side:
        p.append({"id": "side-r", "box": [x0 + W - T, yb, 0, x0 + W, yt, B]})
    if stiles:
        p.append({"id": "stile-l", "box": [x0 + T, yb, B - 76, x0 + BAND, yt, B]})
        p.append({"id": "stile-r", "box": [x0 + W - BAND, yb, B - 76, x0 + W - T, yt, B]})
    p.append({"id": "back", "kind": "back", "box": [x0 + T - 6, yb - 6, 6, x0 + W - T + 6, yt + 6, 9.5]})
    return p


def stack(y0, y1, heights):
    """Fronts from y0 (bottom) up to y1 with 2 mm gaps: heights = list with one None filled to fit."""
    free = y1 - y0 - G * (len(heights) + 1) - sum(h for h in heights if h)
    n = sum(1 for h in heights if not h)
    hs = [h if h else free / n for h in heights]
    out, y = [], y0 + G
    for h in hs:
        out.append((r(y), r(y + h)))
        y += h + G
    return out


# ---------------------------------------------------------------------------------------------------- shoe cabinets
def shoe_3_01():
    """Тумба для обуви 544×200×966: a drawer over two tilt-out flaps (photos: front-on, 3/4, open)."""
    W, H = 544, 966
    p, m = shoe_carcass(W, H), []
    xs = (BAND + 3, W - BAND - 3)
    (f1, f2, d) = stack(FEET + T, H - T, [None, None, 173])
    flap(p, m, "1", *xs, *f1)
    flap(p, m, "2", *xs, *f2, handle=True)
    p.append({"id": "shelf-drawer", "mat": "front", "box": [BAND, d[0] - 9, 10, W - BAND, d[0] + 7, ZF - 1]})
    drawer(p, m, "1", *xs, *d, BAND + 13, W - BAND - 13, 30, h=110)
    p += feet(0, W)
    return dump("aktsent-3-01", [W, B, H], p, m)


def shoe_3_07():
    """Тумба для обуви 544×200×1936: flaps 2 + drawer + 3 flaps from the bottom; handles on the 2nd flap, the drawer and
    the 3rd flap (front-on photo)."""
    W, H = 544, 1936
    p, m = shoe_carcass(W, H), []
    xs = (BAND + 3, W - BAND - 3)
    fr = stack(FEET + T, H - T, [None, None, 170, None, None, None])
    flap(p, m, "1", *xs, *fr[0])
    flap(p, m, "2", *xs, *fr[1], handle=True)
    d = fr[2]
    p.append({"id": "shelf-drawer", "mat": "front", "box": [BAND, d[1] - 7, 10, W - BAND, d[1] + 9, ZF - 1]})
    drawer(p, m, "1", *xs, *d, BAND + 13, W - BAND - 13, 30, h=110)
    flap(p, m, "3", *xs, *fr[3], handle=True)
    flap(p, m, "4", *xs, *fr[4])
    flap(p, m, "5", *xs, *fr[5])
    p += feet(0, W)
    return dump("aktsent-3-07", [W, B, H], p, m)


def shoe_3_08():
    """Тумба для обуви 544×200×1798: four tilt-out flaps under a lift-up flap (gas struts) over an organiser; handles on
    the top flap (by its bottom edge) and the 3rd front from the top (photos: front-on, open)."""
    W, H = 544, 1798
    p, m = shoe_carcass(W, H), []
    xs = (BAND + 3, W - BAND - 3)
    fr = stack(FEET + T, H - T, [None] * 5)
    for i in range(4):
        flap(p, m, str(i + 1), *xs, *fr[i], handle=(i == 2))
    t0, t1 = fr[4]
    ys = r((fr[3][1] + t0) / 2)                       # the organiser's floor behind the joint
    p += [
        {"id": "shelf-org", "mat": "front", "box": [BAND, ys - 8, 10, W - BAND, ys + 8, ZF - 1]},
        {"id": "org-div-l", "mat": "front", "box": [165, ys + 8, 10, 181, ys + 262, 170]},
        {"id": "org-div-r", "mat": "front", "box": [363, ys + 8, 10, 379, ys + 262, 170]},
        {"id": "org-shelf", "mat": "front", "box": [181, ys + 120, 10, 363, ys + 136, 170]},
    ]
    f = {"id": "flap-top", "kind": "front", "box": [xs[0], t0, ZF, xs[1], t1, B]}
    h = bow("h-flap-top", W / 2, t0 + 50, B)
    p += [f, h]
    m.append({"type": "flap", "name": "flap_top", "parts": ["flap-top", "h-flap-top"], "hinge": "top", "angle": 95})
    p += feet(0, W)
    return dump("aktsent-3-08", [W, B, H], p, m)


def shoe_3_06():
    """Тумба для обуви 803×200×1798: the 544 flap column (five tilt-out flaps, a handle on the 3rd from the top) and an
    open column 259 wide, 1447 high on its right: three flat shelves over four sloped shoe shelves (front edge up),
    pearl-white shelves, no back above the third shelf (the site photos; the p. 132 cut-out shows it mirrored)."""
    W, H, WM, HO = 803, 1798, 544, 1447
    p, m = shoe_carcass(WM, H), []
    p[0]["box"][3] = W                                  # one bottom under both columns
    xs = (BAND + 3, WM - BAND - 3)
    fr = stack(FEET + T, H - T, [None] * 5)
    for i in range(5):
        flap(p, m, str(i + 1), *xs, *fr[i], handle=(i == 2))
    yb = FEET + T
    x0, x1 = WM, W - T                                  # the open column's inside
    p += [
        {"id": "side-o", "box": [W - T, yb, 0, W, HO - T, B]},
        {"id": "top-o", "mat": "front", "box": [WM, HO - T, 0, W, HO, B]},
        {"id": "back-o", "kind": "back", "box": [x0 - 6, yb - 6, 6, x1 + 6, 1005, 9.5]},
        {"id": "shelf-o1", "mat": "front", "box": [x0, 997, 10, x1, 1013, B]},
        {"id": "shelf-o2", "mat": "front", "box": [x0 + 1, 1218, 0, x1 - 1, 1234, B]},
    ]
    # sloped shoe shelves: the front top edge at yf, falling ≈ 29° to the back (heel stop at the back)
    # (the board turns about its front bottom edge, so its front top edge stays inside B and ends ≈ 2 mm under yf)
    L = 205
    for i, yf in enumerate([787, 604, 422, 239]):
        p.append({"id": f"shelf-s{i + 1}", "mat": "front", "box": [x0 + 1, yf - T, B - L, x1 - 1, yf, B],
                  "rot": {"axis": "x", "deg": -29, "about": [(x0 + x1) / 2, yf - T, B]}})
    p += feet(0, W, xs=[35, W - 15 - 56])
    return dump("aktsent-3-06", [W, B, H], p, m)


# ---------------------------------------------------------------------------------------------------- 3.05
def wardrobe_3_05():
    """Шкаф комбинированный 1102×581×2064: a 2-door wardrobe (902) with a shoe column on its LEFT END — six tilt-out
    flaps facing left (−x), their trays inside the 186 deep column; one top and one bottom over both; black glides.
    Handles: vertical bows by the doors' meeting edge; bows on the 3rd and 4th flaps from the top (photos 0–3)."""
    W, D, H = 1102, 581, 2064
    GL = 10
    yb, yt = GL + T, H - T
    XC = 186                                            # the column's depth (x), then the wardrobe's left side
    p, m = [], []
    p += [
        {"id": "bottom", "box": [0, GL, 0, W, yb, D]},
        {"id": "top", "box": [0, yt, 0, W, H, D]},
        {"id": "side-m", "box": [XC, yb, 0, XC + T, yt, D]},
        {"id": "side-r", "box": [W - T, yb, 0, W, yt, D]},
        {"id": "col-front", "box": [0, yb, D - T, XC, yt, D]},
        {"id": "col-back", "box": [0, yb, 0, XC, yt, T]},
        {"id": "col-stile-f", "box": [0, yb, D - BAND, 76, yt, D - T]},
        {"id": "col-stile-b", "box": [0, yb, T, 76, yt, BAND]},
    ]
    for i, x in enumerate([40, 540, 1040]):
        for j, z in enumerate([30, D - 70]):
            p.append({"id": f"glide-{i + 1}{'ab'[j]}", "mat": "black", "edge": 3, "box": [x, 0, z, x + 40, GL, z + 40]})
    # wardrobe: backs joined behind a pearl rail, hat shelf, rail, lower shelf (the open photo 2)
    xa, xb = XC + T, W - T
    p += [
        {"id": "back-low", "kind": "back", "box": [xa - 6, yb - 6, 6, xb + 6, 1035, 9.5]},
        {"id": "back-up", "kind": "back", "box": [xa - 6, 1035, 6, xb + 6, yt + 6, 9.5]},
        {"id": "back-rail", "mat": "front", "box": [xa, 965, 9.5, xb, 1100, 25.5]},
        {"id": "shelf-hat", "mat": "front", "box": [xa + 1, 1733, 26, xb - 1, 1749, D - 22]},
        {"id": "rail", "kind": "tube", "mat": "chrome", "box": [xa + 1, 1682, 278, xb - 1, 1707, 303]},
        {"id": "shelf-low", "mat": "front", "box": [xa + 1, 278, 26, xb - 1, 294, D - 22]},
    ]
    ZD = D - T
    dl = (xa + 2, r((xa + xb) / 2 - 1.5))
    dr = (r((xa + xb) / 2 + 1.5), xb - 2)
    for tag, (x0, x1), hinge, hx in (("l", dl, "left", dl[1] - 50), ("r", dr, "right", dr[0] + 50)):
        p.append({"id": f"door-{tag}", "kind": "front", "box": [x0, yb + 3, ZD, x1, yt - 3, D]})
        p.append(bow(f"h-door-{tag}", hx, 1050, D, vertical=True))
        m.append({"type": "door", "name": f"door_{tag}", "parts": [f"door-{tag}", f"h-door-{tag}"], "hinge": hinge, "angle": 100})
    # the shoe column: six flaps facing −x (x 0..16) inset between the column panels / stiles, trays behind them (+x)
    za, zb = BAND + 3, D - BAND - 3
    zc = (za + zb) / 2
    for i, (y0, y1) in enumerate(stack(yb, yt, [None] * 6)):
        tag = f"c{i + 1}"
        p.append({"id": f"flap-{tag}", "kind": "front", "box": [0, y0, za, T, y1, zb]})
        a, b = za + 12, zb - 12
        q0, q1 = y0 + 12, y1 - 12
        p += [
            {"id": f"tray-floor-{tag}", "mat": TRAY, "edge": 0.5, "box": [T, q0, a + 1.5, T + 1.5, q1, b - 1.5]},
            {"id": f"tray-wall-{tag}", "mat": TRAY, "edge": 0.5, "box": [T + 1.5, q0, a + 1.5, T + 110, q0 + 1.5, b - 1.5]},
            {"id": f"tray-lip-{tag}", "mat": TRAY, "edge": 0.5, "box": [T + 1.5, q1 - 1.5, a + 1.5, T + 16, q1, b - 1.5]},
        ]
        cheek = f"M {T} {q0} L {T + 110} {q0} L {T + 16} {q1} L {T} {q1} Z"
        for s, (c0, c1) in (("f", (b - 1.5, b)), ("b", (a, a + 1.5))):
            p.append({"id": f"tray-{s}-{tag}", "mat": TRAY, "edge": 0.5, "box": [T, q0, c0, T + 110, q1, c1], "shape": "path",
                      "outline": cheek})
        if i in (2, 3):                                  # the 3rd and 4th flaps from the top: bow handles on the −x face
            yh = y1 - 50
            p.append({"id": f"h-{tag}", "kind": "rod", "mat": "metal", "section": "square", "d": 14,
                      "from": [-22, yh, zc - 104], "to": [-22, yh, zc + 104]})
            for s, dz in (("a", -83), ("b", 83)):
                p.append({"id": f"h-{tag}-{s}", "kind": "rod", "mat": "metal", "section": "square", "d": 11,
                          "from": [0, yh, zc + dz], "to": [-22, yh, zc + dz]})
    return dump("aktsent-3-05", [W, D, H], p, m)


# ---------------------------------------------------------------------------------------------------- 3.03 / 3.02
def chest_3_03():
    """Тумба 700×404×859: four equal drawers (front-on photo 1, open 3/4 photo 2: ball-bearing runners, white boxes)."""
    W, D, H = 700, 404, 859
    F15 = 15
    yb, yt = F15 + T, H - T
    ZD = D - T
    p, m = [], []
    p += [
        {"id": "bottom", "box": [0, F15, 0, W, yb, D]},
        {"id": "side-l", "box": [0, yb, 0, T, yt, D]},
        {"id": "side-r", "box": [W - T, yb, 0, W, yt, D]},
        {"id": "top", "box": [0, yt, 0, W, H, D]},
        {"id": "back", "kind": "back", "box": [T - 6, yb - 6, 6, W - T + 6, yt + 6, 9.5]},
    ]
    for i, x in enumerate([32, W - 32 - 86]):
        for j, z in enumerate([30, D - 70]):
            p.append({"id": f"foot-{i + 1}{'ab'[j]}", "mat": FOOT, "edge": 2, "box": [x, 0, z, x + 86, F15, z + 40]})
    for i, (y0, y1) in enumerate(stack(yb, yt, [None] * 4)):
        drawer(p, m, str(4 - i), T + 3, W - T - 3, y0, y1, T + 13, W - T - 13, 20, h=140, zf=ZD, zface=D, travel=300)
    return dump("aktsent-3-03", [W, D, H], p, m)


def bench_3_02():
    """Тумба для обуви 800×400×450 with a seat cushion: an open box with a middle partition and a loose shelf each side,
    a fixed shelf under a set-back pearl rail, the top over the sides, the cushion (≈ 35 thick on a thin base) on top
    (front-on photo 0, 3/4 photo 1). H 450 is to the cushion's top."""
    W, D, H = 800, 400, 450
    GL = 10
    yb, yt = GL + T, 396
    p = [
        {"id": "bottom", "box": [0, GL, 0, W, yb, D]},
        {"id": "side-l", "box": [0, yb, 0, T, yt, D]},
        {"id": "side-r", "box": [W - T, yb, 0, W, yt, D]},
        {"id": "top", "box": [0, yt, 0, W, yt + T, D]},
        {"id": "back", "kind": "back", "box": [T - 6, yb - 6, 6, W - T + 6, yt + 6, 9.5]},
        {"id": "shelf-fixed", "box": [T, 306, 10, W - T, 322, D]},
        {"id": "rail", "mat": "front", "box": [T, 322, D - 36, W - T, yt, D - 20]},
        {"id": "partition", "box": [W / 2 - 8, yb, 10, W / 2 + 8, 306, D]},
        {"id": "shelf-l", "box": [T + 1, 159, 20, W / 2 - 9, 175, D - 20]},
        {"id": "shelf-r", "box": [W / 2 + 9, 159, 20, W - T - 1, 175, D - 20]},
        {"id": "seat-base", "mat": "black", "edge": 0.5, "box": [12, yt + T, 12, W - 12, yt + T + 3, D - 12]},
        {"id": "cushion", "kind": "soft", "edge": 12, "box": [12, yt + T + 3, 12, W - 12, H, D - 12]},
    ]
    for i, x in enumerate([30, W - 60]):
        for j, z in enumerate([25, D - 55]):
            p.append({"id": f"foot-{i + 1}{'ab'[j]}", "mat": FOOT, "edge": 2, "box": [x, 0, z, x + 30, GL, z + 30]})
    return dump("aktsent-3-02", [W, D, H], p, [])


# ---------------------------------------------------------------------------------------------------- wall pieces
def dshape(x0, y0, x1, y1):
    """A 'D': a half disc (R = half the height) on the left, straight top, right and bottom edges."""
    R = (y1 - y0) / 2
    cx, cy = x0 + R, (y0 + y1) / 2
    k = 0.5523 * R
    return (f"M {cx} {y0} L {x1} {y0} L {x1} {y1} L {cx} {y1} C {cx - k} {y1} {x0} {cy + k} {x0} {cy} "
            f"C {x0} {cy - k} {cx - k} {y0} {cx} {y0} Z")


def mirror_3_04():
    """Зеркало 558×21×708: a 4 mm facetted mirror, straight on the right, a half disc R 354 on the left (the product photo:
    R = H/2 fits the outline to 2 mm), on a hidden ЛДСП 16 backing inset 20 (1 mm tape between). Hangs either way
    (the site gives it as 700×20×550)."""
    W, D, H = 558, 21, 708
    p = [
        {"id": "backing", "box": [20, 20, 0, W - 20, H - 20, T], "shape": "path", "outline": dshape(20, 20, W - 20, H - 20)},
        {"id": "mirror", "kind": "mirror", "box": [0, 0, T + 1, W, H, D], "shape": "path", "outline": dshape(0, 0, W, H)},
    ]
    return dump("aktsent-3-04", [W, D, H], p, [])


def hook_outline(y0, zw=T):
    """A black double coat hook seen from the side (z, y): a stem on the wall, the upper arm curving out to a tip 131 up,
    a J at the bottom."""
    return (f"M {zw} {y0 + 10} L {zw} {y0 + 75} Q {zw + 4} {y0 + 120} {zw + 42} {y0 + 131} L {zw + 44} {y0 + 124} "
            f"Q {zw + 11} {y0 + 112} {zw + 8} {y0 + 72} L {zw + 8} {y0 + 14} Q {zw + 10} {y0 + 8} {zw + 18} {y0 + 8} "
            f"Q {zw + 26} {y0 + 9} {zw + 28} {y0 + 30} L {zw + 34} {y0 + 30} Q {zw + 34} {y0} {zw + 18} {y0} "
            f"Q {zw} {y0} {zw} {y0 + 10} Z")


def hanger_3_09():
    """Вешалка 760×216×1410 (wall): three pearl ЛДСП 16 boards 230 wide (19 apart; the right one 1410 high, the others
    802), a Мадура shelf 760×200 on two black steel brackets, four black double hooks (photos 0, 1)."""
    W, D, H = 760, 216, 1410
    PW, GAP = 230, 19
    xs = [16 + i * (PW + GAP) for i in range(3)]
    p = [
        {"id": "board-l", "kind": "panel", "mat": "front", "box": [xs[0], 471, 0, xs[0] + PW, 1273, T]},
        {"id": "board-m", "kind": "panel", "mat": "front", "box": [xs[1], 540, 0, xs[1] + PW, 1342, T]},
        {"id": "board-r", "kind": "panel", "mat": "front", "box": [xs[2], 0, 0, xs[2] + PW, H, T]},
        {"id": "shelf", "box": [0, 1111, T, W, 1127, D]},
    ]
    for tag, xc in (("l", xs[0] + 47.5), ("r", xs[2] + PW - 47.5)):
        p.append({"id": f"bracket-{tag}", "mat": "black", "edge": 0.5, "box": [xc - 10, 990, T, xc + 10, 1111, T + 4]})
        p.append({"id": f"bracket-arm-{tag}", "mat": "black", "edge": 0.5, "box": [xc - 6, 1030, T + 4, xc + 6, 1111, 150],
                  "shape": "path",
                  "outline": f"M {T + 4} 1030 Q {T + 4} 1111 100 1111 L 150 1111 L 150 1106 L 100 1106 Q {T + 9} 1106 {T + 9} 1030 Z"})
    hooks = [(xs[0] + PW / 2, 882), (xs[1] + PW / 2, 882), (xs[2] + PW / 2, 882), (xs[2] + PW / 2, 368)]
    for i, (xc, y0) in enumerate(hooks):
        p.append({"id": f"hook-{i + 1}", "mat": "black", "edge": 0.8, "box": [xc - 4, y0, T, xc + 4, y0 + 131, T + 44],
                  "shape": "path", "outline": hook_outline(y0)})
    return dump("aktsent-3-09", [W, D, H], p, [])


def keyholder_3_10():
    """Ключница 200×29×470 (wall): a moulded Мадура frame 28 wide round a pearl board, three black L hooks (photos 0, 1)."""
    W, D, H = 200, 29, 470
    p = [
        {"id": "frame", "kind": "moulding", "profile": "aktsent-frame", "closed": True, "plane": "front", "z": 0, "mat": "body",
         "path": [[0, 0], [W, 0], [W, H], [0, H]]},
        {"id": "board", "kind": "panel", "mat": "front", "box": [27, 27, 2, W - 27, H - 27, 12]},
    ]
    for i, (xc, y0) in enumerate([(125, 327), (75, 213), (125, 100)]):
        p.append({"id": f"hook-{i + 1}", "mat": "black", "edge": 1, "box": [xc - 5, y0, 12, xc + 5, y0 + 50, D], "shape": "path",
                  "outline": f"M 12 {y0} L {D} {y0} L {D} {y0 + 12} L 20 {y0 + 12} L 20 {y0 + 44} Q 20 {y0 + 50} 16 {y0 + 50} "
                             f"L 12 {y0 + 50} Z"})
    return dump("aktsent-3-10", [W, D, H], p, [])


# ---------------------------------------------------------------------------------------------------- catalogue
NOTE = "по каталогу и фото сайта, без инструкции"
MODELS = [
    ("aktsent-3-01", "П3.595.3.01", "Тумба для обуви «Акцент»", "hall", [544, 200, 966], {}),
    ("aktsent-3-02", "П3.595.3.02", "Тумба для обуви «Акцент»", "hall", [800, 400, 450], {"note": NOTE + "; H до верха подушки"}),
    ("aktsent-3-03", "П3.595.3.03", "Тумба «Акцент»", "hall", [700, 404, 859], {}),
    ("aktsent-3-04", "П3.595.3.04", "Зеркало «Акцент»", "decor", [558, 21, 708],
     {"mount": "wall", "note": NOTE + "; сайт 700×20×550 (то же зеркало, повешенное боком) — взят каталог"}),
    ("aktsent-3-05", "П3.595.3.05", "Шкаф комбинированный «Акцент»", "hall", [1102, 581, 2064], {}),
    ("aktsent-3-06", "П3.595.3.06", "Тумба для обуви «Акцент»", "hall", [803, 200, 1798],
     {"note": NOTE + "; сайт 828×200×1936, фото сайта в пропорции каталога — взят каталог; открытая секция справа, как на фото (вырезка с. 132 — зеркально)"}),
    ("aktsent-3-07", "П3.595.3.07", "Тумба для обуви «Акцент»", "hall", [544, 200, 1936], {}),
    ("aktsent-3-08", "П3.595.3.08", "Тумба для обуви «Акцент»", "hall", [544, 200, 1798], {"note": NOTE + "; сайт H1766 — взят каталог"}),
    ("aktsent-3-09", "П3.595.3.09", "Вешалка «Акцент»", "hall", [760, 216, 1410], {"mount": "wall"}),
    ("aktsent-3-10", "П3.595.3.10", "Ключница «Акцент»", "hall", [200, 29, 470], {"mount": "wall", "note": NOTE + "; сайт B32 — взят каталог"}),
]


def catalog():
    models = []
    for mid, code, name, cat, size, extra in MODELS:
        e = {"id": mid, "code": code, "name": name, "collection": "aktsent", "category": cat, "size": size, "page": 132}
        if "mount" in extra:
            e["mount"] = extra["mount"]
        e["note"] = extra.get("note", NOTE)
        models.append(e)
    frag = {
        "finishes": [{
            "id": "aktsent-zhemchug-madura", "name": "Персидский жемчуг / Дуб Мадура",
            "body": "door_enamel_whitey#beb1a1", "front": "door_enamel_whitey#dfe3e2", "back": "door_enamel_whitey#dfe3e2",
            "swatch": "#dfe3e2", "roles": {"fabric": "velvet#b0a28c"},
        }],
        "profiles": {
            "aktsent-frame": {"name": "Рамка ключницы «Акцент» 28×29 (плоская полка, скос внутрь)",
                              "pts": [[0, 0], [0, 26], [2, 29], [12, 29], [14, 27], [24, 20], [28, 18], [28, 0]]},
        },
        "collections": [{
            "id": "aktsent", "name": "Акцент", "brand": "Пинскдрев", "finishes": ["aktsent-zhemchug-madura"], "metal": "chrome",
            "note": "Каталог «Корпусная мебель ч. II» 2025, с. 132 (разворот 260–261) и фото сайта pinskdrev.by; инструкций нет — "
                    "всё по каталогу и фото. Корпус ЛДСП 16 «Дуб Мадура» (дно во всю ширину на металлических опорах, боковины на "
                    "дне, крышка на боковинах), вкладные фасады ЛДСП 16 «Персидский жемчуг» с зазором 2–3 мм, у обувниц — стойка "
                    "16 мм за полосой корпуса (полоса 32 мм), откидные ящики с металлическими лотками, ручки-скобы 208 мм "
                    "(сатин-хром), задние стенки ХДФ белые.",
        }],
        "models": models,
    }
    path = os.path.join(HERE, "aktsent_catalog.json")
    with open(path, "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


if __name__ == "__main__":
    for fn in (shoe_3_01, bench_3_02, chest_3_03, mirror_3_04, wardrobe_3_05, shoe_3_06, shoe_3_07, shoe_3_08, hanger_3_09,
               keyholder_3_10):
        print(fn())
    print(catalog())
