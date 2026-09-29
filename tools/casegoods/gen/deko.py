"""«Деко» (Пинскдрев / Бобруйскмебель line БМ2.776, catalogue «Корпусная мебель ч. II» 2025, PDF pp. 72–74 = printed
140–145): living room and bedroom in «Дуб Наварра» with black slatted fronts. 13 designs, all by catalogue and photo (no
instructions exist): the module cut-outs with sizes on p. 74, the interior photos p. 72 / 73 / 74, the close-up of a
slatted front on p. 74, and the product photos of pinskdrev.by (studio shots, several of them front-on or open).

Construction (read off the photos; the common Pinskdrev БМ2 scheme):
  * carcass ЛДСП 16 «Дуб Наварра»: the bottom runs the full width under the sides, the sides stand on it, the top lies
    over the sides (full width and depth) — the 0.05 photo shows the bottom's end under the side and the top's edge over
    it; ХДФ backs 3.5 in grooves 6 mm from the back edge; partitions and fixed shelves behind the fronts;
  * fronts ЛДСП 16 inset between the sides / top / bottom, flush with the carcass edges (the carcass edges frame every
    front in the photos), 2 mm to the carcass, 3 mm between fronts;
  * the slatted front: a black ЛДСП 16 board with solid birch slats (site: «Фасад: ЛДСП; массив берёзы») 30 × 20 glued on
    it upright; the slats' faces are flush with the carcass edges, the board 20 mm behind them (the photos from the side
    show the slats standing proud with the black board in their shadow; the open vitrine 0.05 shows the slats' ends at
    the free edge of the swung door). Living pieces: 4 slats at the free edge of the right door + a flat black field;
    chest: 7 slats over the whole door; bedside: 3 slats + an oak panel on one black drawer front; wardrobes: a sliding
    door of 8 slats;
  * black aluminium edge pulls over the top edge of the oak fronts (the close-up p. 74), ≈ 152 long; a black upright bar
    on the glazed doors' free edge; the slatted doors have no handle (the slats are the grip);
  * glazed doors: a black aluminium frame ≈ 22 mm round bronze-tinted glass (0.05 / 0.06 photos);
  * living pieces stand on black plastic glides 14 mm (photos), the chest and the bedside on black metal legs (a flat
    arm under the bottom and a tapered post), the wardrobes' sides on the floor over a recessed black plinth.

    /private/tmp/claude-501/venv/bin/python tools/casegoods/gen/deko.py   # Designs/deko-*.json + gen/deko_catalog.json
"""
import copy
import json
import os

from common import dump

T = 16            # ЛДСП carcass and fronts
BK = 3.5          # ХДФ back
SL_W, SL_T = 30, 20   # birch slat
GL = 14           # plastic glide height (living pieces)
PULL = dict(model="edge", d=152, band=14, t=2, standoff=18, dir="down")   # black edge pull (dir only for the 2D preview)


def r1(v):
    return round(v, 1)


def P(pid, box, **kw):
    p = {"id": pid, "box": [r1(v) for v in box]}
    p.update(kw)
    return p


def pull(pid, x, ytop, z, d=152):
    h = {"id": pid, "kind": "handle"}
    h.update(PULL)
    h.update({"d": d, "at": [r1(x), r1(ytop)], "z": r1(z)})
    return h


def carcass(W, D, H, y0, backs=None):
    """Bottom (full width) on glides / legs at y0, the sides on it, the top over the sides; backs in grooves split at xs."""
    p = [
        P("bottom", [0, y0, 0, W, y0 + T, D]),
        P("side-l", [0, y0 + T, 0, T, H - T, D]),
        P("side-r", [W - T, y0 + T, 0, W, H - T, D]),
        P("top", [0, H - T, 0, W, H, D]),
    ]
    xs = [10] + list(backs or []) + [W - 10]
    for i in range(len(xs) - 1):
        p.append(P("back" if len(xs) == 2 else f"back-{i + 1}", [xs[i], y0 + T - 6, 6, xs[i + 1], H - T + 6, 6 + BK],
                   kind="back"))
    return p


def glides(W, D, xs=None):
    """Black plastic glides 90 × 14 × 40 under the bottom, front and back."""
    xs = xs or [60, W - 60]
    out = []
    for i, x in enumerate(xs):
        for s, (z0, z1) in (("f", (D - 70, D - 30)), ("b", (30, 70))):
            out.append(P(f"glide-{i + 1}{s}", [x - 45, 0, z0, x + 45, GL, z1], mat="black"))
    return out


def bracket_leg(tag, x, z, h, inward):
    """Black metal leg: a flat arm under the bottom (140 mm along x, towards `inward` = ±1), a tapered post splayed 8 mm
    out, a glide under it (the glide gives the floor line: the checker does not count rods)."""
    xp = x - inward * 8
    return [
        {"id": f"leg{tag}-arm", "kind": "rod", "section": "square", "mat": "metal", "d": 12,
         "from": [x - inward * 14, h - 6, z], "to": [x + inward * 140, h - 6, z]},
        {"id": f"leg{tag}", "kind": "rod", "mat": "metal", "d": 26, "d2": 18, "from": [x, h - 12, z], "to": [xp, 20, z]},
        P(f"leg{tag}-glide", [xp - 9, 0, z - 9, xp + 9, 20, z + 9], kind="tube", mat="metal"),
    ]


def legs4(W, D, h, inset=30, zin=45):
    out = []
    for tag, x, inward in (("-l", inset, 1), ("-r", W - inset, -1)):
        for s, z in (("f", D - zin), ("b", zin)):
            out += bracket_leg(tag + s, x, z, h, inward)
    return out


def partition(pid, xc, y0, y1, zf):
    return P(pid, [xc - T / 2, y0, 10, xc + T / 2, y1, zf])


def shelf(pid, x0, x1, ytop, zf, glass=False):
    """A loose shelf on pins: 1 mm off the sides, 20 mm off the back, zf = its front edge. Glass shelves are 6 mm."""
    t = 6 if glass else T
    return P(pid, [x0 + 1, ytop - t, 20, x1 - 1, ytop, zf], **({"kind": "glass"} if glass else {}))


def fixed_shelf(pid, x0, x1, ytop, zf):
    return P(pid, [x0, ytop - T, 10, x1, ytop, zf])


def drawer_box(tag, x0, x1, y0, h, z0, z1):
    """Drawer box ЛДСП 16 between x0..x1 (13 mm runner gap already taken off), y0..y0+h, z0 (back) .. z1 (the facade's
    back): sides, back, inner front board, ХДФ bottom in grooves."""
    return [
        P(f"dr{tag}-l", [x0, y0, z0, x0 + T, y0 + h, z1]),
        P(f"dr{tag}-r", [x1 - T, y0, z0, x1, y0 + h, z1]),
        P(f"dr{tag}-back", [x0 + T, y0, z0, x1 - T, y0 + h, z0 + T]),
        P(f"dr{tag}-front", [x0 + T, y0, z1 - T, x1 - T, y0 + h, z1]),
        P(f"dr{tag}-bottom", [x0 + T - 6, y0 + 10, z0 + T - 6, x1 - T + 6, y0 + 10 + BK, z1 - T + 6], kind="back"),
    ]


def slats(tag, xs, y0, y1, z0, w=SL_W):
    """Birch slats glued upright on a black board whose face is z0."""
    return [P(f"{tag}-slat{i + 1}", [x, y0, z0, x + w, y1, z0 + SL_T], mat="slat", grain="y") for i, x in enumerate(xs)]


def slat_door(tag, x0, x1, y0, y1, zface, rel, w=SL_W):
    """Black board 16 (face zface − 20) with slats at x0 + rel[i]; the slats' faces at zface."""
    board = P(f"{tag}", [x0, y0, zface - SL_T - T, x1, y1, zface - SL_T], kind="front", mat="accent", grain="y")
    return [board] + slats(tag, [x0 + r for r in rel], y0, y1, zface - SL_T, w)


def ids(parts):
    return [p["id"] for p in parts]


def mirror_x(parts, moves, W):
    """The mirror-image variant: every x → W − x, hinges on the other side."""
    parts, moves = copy.deepcopy(parts), copy.deepcopy(moves)
    for p in parts:
        if "box" in p:
            b = p["box"]
            b[0], b[3] = r1(W - b[3]), r1(W - b[0])
        if "at" in p:
            p["at"][0] = r1(W - p["at"][0])
        for k in ("from", "to"):
            if k in p:
                p[k][0] = r1(W - p[k][0])
        if "outline" in p:
            raise ValueError("mirror an outline by hand")
    for m in moves:
        if m.get("hinge") in ("left", "right"):
            m["hinge"] = "right" if m["hinge"] == "left" else "left"
    return parts, moves


# ================================================================================================= living room (B 400)
D_L = 400
ZF = D_L - T            # an oak front's back face (inset flush)
LIVING_SLATS = [5, 62, 119, 176]      # 4 slats at the free edge (pitch 57; cut-outs p. 74 and the 0.05 / 0.06 photos)


def tumba_034():
    """Тумба 1542 × 400 × 896: three columns (cut-out p. 74: joints at 517 / 1020) — a door (left), three drawers
    210 / 213 / 420, the slatted door (right)."""
    W, D, H = 1542, D_L, 896
    y0, yt = GL + T, H - T                    # the opening 30 … 880
    p = carcass(W, D, H, GL) + glides(W, D, [60, W / 2, W - 60])
    p += [partition("partition-1", 517, y0, yt, ZF - 2), partition("partition-2", 1018, y0, yt, D - SL_T - T - 2)]
    p += [shelf("shelf-l", T, 509, 471, ZF - 20), shelf("shelf-r", 1026, W - T, 471, D - SL_T - T - 20)]
    moves = []
    door = P("door-l", [18, y0 + 2, ZF, 515.5, yt - 2, D], kind="front", grain="y")
    k = pull("k-door", (18 + 515.5) / 2, yt - 2, D)
    p += [door, k]
    moves.append({"type": "door", "name": "door_left", "parts": ["door-l", "k-door"], "hinge": "left", "angle": 105})
    fronts = [(32, 452), (455, 667.5), (670.5, 878)]
    boxes = [(42, 250), (470, 150), (685, 150)]
    for i, ((a, b), (by, bh)) in enumerate(zip(fronts, boxes)):
        tag = str(i + 1)
        fr = P(f"drawer-{tag}", [518.5, a, ZF, 1016.5, b, D], kind="front", grain="x")
        k = pull(f"k-{tag}", (518.5 + 1016.5) / 2, b, D)
        bx = drawer_box(tag, 525 + 13, 1010 - 13, by, bh, 32, ZF)
        p += [fr] + bx + [k]
        moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": [fr["id"]] + ids(bx) + [k["id"]], "travel": 300})
    sd = slat_door("door-r", 1019.5, W - 18, y0 + 2, yt - 2, D, LIVING_SLATS + [])
    p += sd
    moves.append({"type": "door", "name": "door_right", "parts": ids(sd), "hinge": "right", "angle": 105})
    return dump("deko-0-34", [W, D, H], p, moves)


def tv_033():
    """Тумба ТВ 1542 × 400 × 450: an open niche over one wide drawer (left, 982 wide inside), the slatted door (right)."""
    W, D, H = 1542, D_L, 450
    y0, yt = GL + T, H - T                    # 30 … 434
    p = carcass(W, D, H, GL) + glides(W, D, [60, W / 2, W - 60])
    p += [partition("partition", 1006, y0, yt, ZF - 2),
          fixed_shelf("niche-floor", T, 998, 300, ZF - 2),
          shelf("shelf-r", 1014, W - T, 248, D - SL_T - T - 20)]
    fr = P("drawer", [18, y0 + 2, ZF, 1012, 300, D], kind="front", grain="x")
    ks = [pull("k-1", 18 + 994 * 0.25, 300, D), pull("k-2", 18 + 994 * 0.75, 300, D)]
    bx = drawer_box("1", T + 13, 998 - 13, 42, 200, 32, ZF)
    p += [fr] + bx + ks
    moves = [{"type": "drawer", "name": "drawer", "parts": [fr["id"]] + ids(bx) + ids(ks), "travel": 300}]
    sd = slat_door("door", 1016, W - 18, y0 + 2, yt - 2, D, [8, 66.5, 125, 183.5])
    p += sd
    moves.append({"type": "door", "name": "door", "parts": ids(sd), "hinge": "right", "angle": 105})
    return dump("deko-0-33", [W, D, H], p, moves)


def vitrine(did, H, joint, shelves_l, glass_l, shelves_r):
    """Шкаф-витрина 941 × 400 × H: left column (505 inside) — an oak door under a glazed door (black aluminium frame,
    bronze glass), each hinged left, a fixed shelf behind their joint; right column — the slatted door hinged right."""
    W, D = 941, D_L
    y0, yt = GL + T, H - T
    zg = D - 20                                # the glazed door is 20 thick (aluminium frame)
    zs = D - SL_T - T                          # the slatted door's board
    p = carcass(W, D, H, GL) + glides(W, D)
    p += [partition("partition", 513, y0, yt, zs - 2),
          fixed_shelf("fixed-l", T, 505, joint - 1.5, zg - 2),
          fixed_shelf("fixed-r", 521, W - T, joint - 1.5, zs - 2)]
    for i, y in enumerate(shelves_l):
        p.append(shelf(f"shelf-l{i + 1}", T, 505, y, ZF - 20))
    for i, y in enumerate(glass_l):
        p.append(shelf(f"glass-l{i + 1}", T, 505, y, zg - 20, glass=True))
    for i, y in enumerate(shelves_r):
        p.append(shelf(f"shelf-r{i + 1}", 521, W - T, y, zs - 20))
    x0, x1 = 18, 511.5
    lo = P("door-oak", [x0, y0 + 2, ZF, x1, joint - 1.5, D], kind="front", grain="y")
    k1 = pull("k-oak", (x0 + x1) / 2, joint - 1.5, D)
    gl = P("door-glass", [x0, joint + 1.5, zg, x1, yt - 2, D], kind="front", mat="metal",
           glass={"frame": 22, "rebate": 5, "t": 4, "tint": "bronze"})
    k2 = {"id": "k-glass", "kind": "handle", "model": "bar", "dir": "up", "d": 160, "band": 12, "t": 8,
          "standoff": 16, "at": [x1 - 11, r1((joint + yt) / 2)], "z": D}
    p += [lo, k1, gl, k2]
    moves = [{"type": "door", "name": "door_oak", "parts": ["door-oak", "k-oak"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_glass", "parts": ["door-glass", "k-glass"], "hinge": "left", "angle": 105}]
    sd = slat_door("door-r", 514.5, W - 18, y0 + 2, yt - 2, D, LIVING_SLATS)
    p += sd
    moves.append({"type": "door", "name": "door_right", "parts": ids(sd), "hinge": "right", "angle": 105})
    return dump(did, [W, D, H], p, moves)


def polka_051():
    """Полка 1542 × 266 × 250 on the wall: an oak back board 1441 × 250 (50.5 in from the shelf's ends), the shelf 22 in
    front of it at 22 … 44 over the full length, a black board over the back's right part above the shelf with 4 slats."""
    W, D, H = 1542, 266, 250
    p = [
        P("back-board", [50.5, 0, 0, W - 50.5, H, T], grain="x"),
        P("shelf", [0, 22, T, W, 44, D], grain="x"),
        P("black-board", [1016, 44, T, W - 50.5, H, 2 * T], mat="accent"),
    ]
    p += slats("black-board", [1021, 1076, 1131, 1186], 44, H, 2 * T)
    return dump("deko-0-51", [W, D, H], p, [])


# ================================================================================================= bedroom (B 460)
D_B = 460
ZFB = D_B - T


def komod_131():
    """Комод 1471 × 460 × 970 on four legs 175: the slatted door on the left (7 slats over it, hinged left, a partition
    at 470 behind its joint), three drawers 251 on the right with two pulls each."""
    W, D, H, hl = 1471, D_B, 970, 175
    y0, yt = hl + T, H - T                    # 191 … 954
    zs = D - SL_T - T
    p = carcass(W, D, H, hl) + legs4(W, D, hl)
    p += [partition("partition", 470, y0, yt, zs - 2),
          shelf("shelf-1", T, 462, 445, zs - 20), shelf("shelf-2", T, 462, 700, zs - 20)]
    rel = [30 + 60 * i for i in range(7)]
    sd = slat_door("door", 18, 468.5, y0 + 2, yt - 2, D, rel)
    p += sd
    moves = [{"type": "door", "name": "door", "parts": ids(sd), "hinge": "left", "angle": 105}]
    fx0, fx1 = 471.5, W - 18
    fronts = [(193, 444), (447, 698), (701, 952)]
    for i, (a, b) in enumerate(fronts):
        tag = str(i + 1)
        fr = P(f"drawer-{tag}", [fx0, a, ZFB, fx1, b, D], kind="front", grain="x")
        ks = [pull(f"k-{tag}a", fx0 + (fx1 - fx0) * 0.25, b, D), pull(f"k-{tag}b", fx0 + (fx1 - fx0) * 0.75, b, D)]
        by = a + 20 if i else y0 + 12
        bx = drawer_box(tag, 478 + 13, W - T - 13, by, 180, 44, ZFB)
        p += [fr] + bx + ks
        moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": [fr["id"]] + ids(bx) + ids(ks), "travel": 350})
    return dump("deko-1-31", [W, D, H], p, moves)


def tumba_130(left_slats=True):
    """Тумба прикроватная 481 × 460 × 466 on four legs 150: one drawer whose front is a black board 445 × 280 with 3
    slats on its left part and an oak panel 268 on its right part; the edge pull on the oak panel's top edge from its
    slat-side end. 1.30-01 = slats on the left (the p. 73 photo, the p. 74 cut-out and the site's main photos);
    1.30 = the mirror image (slats on the right; the site's «kopiya-2» photo)."""
    W, D, H, hl = 481, D_B, 466, 150
    y0, yt = hl + T, H - T                    # 166 … 450
    p = carcass(W, D, H, hl) + legs4(W, D, hl)
    a, b = y0 + 2, yt - 2
    board = P("drawer", [18, a, D - SL_T - T, W - 18, b, D - SL_T], kind="front", mat="accent", grain="x")
    sl = slats("drawer", [41, 102, 163], a, b, D - SL_T)
    oak = P("drawer-oak", [195, a, D - SL_T, W - 18, b, D - SL_T + T], kind="front", grain="x")
    k = pull("k-1", 195 + 76, b, D - SL_T + T)
    bx = drawer_box("1", T + 13, W - T - 13, y0 + 16, 200, 64, D - SL_T - T)
    p += [board] + sl + [oak] + bx + [k]
    moves = [{"type": "drawer", "name": "drawer", "parts": ["drawer"] + ids(sl) + ["drawer-oak"] + ids(bx) + ["k-1"],
              "travel": 300}]
    did = "deko-1-30-01"
    if not left_slats:
        p, moves = mirror_x(p, moves, W)
        did = "deko-1-30"
    return dump(did, [W, D, H], p, moves)


def mirror_132():
    """Зеркало 1100 × 5 × 600 on the wall: a 4 mm mirror with corners rounded R30 and a black border 10 mm (the cut-out
    p. 74) — drawn as a 1 mm black ring on its face (the printed / framed edge)."""
    W, D, H = 1100, 5, 600

    def rr(x0, y0, x1, y1, r):
        return (f"M {x0 + r} {y0} L {x1 - r} {y0} A {r} {r} 0 0 1 {x1} {y0 + r} L {x1} {y1 - r} "
                f"A {r} {r} 0 0 1 {x1 - r} {y1} L {x0 + r} {y1} A {r} {r} 0 0 1 {x0} {y1 - r} L {x0} {y0 + r} "
                f"A {r} {r} 0 0 1 {x0 + r} {y0} Z")
    p = [
        P("mirror", [0, 0, 0, W, H, 4], kind="mirror", radius=30),
        P("border", [0, 0, 4, W, H, D], mat="black", shape="path",
          outline=rr(0, 0, W, H, 30) + " " + rr(10, 10, W - 10, H - 10, 20), edge=0.3),
    ]
    return dump("deko-1-32", [W, D, H], p, [])


# ------------------------------------------------------------------------------------------------ wardrobes (B 621)
def wardrobe(did, W):
    """Шкаф для одежды H 2200 × B 621: sides on the floor, the top over them, a fascia 54 under the top's front edge,
    a recessed black plinth 60 under an oak front rail, the bottom at 82 … 98 with the aluminium double track on it.
    Left section (984 inside, the mirror pair): two drawers 243 with two pulls each, a fixed shelf, two hinged doors with
    a mirror glued on (hinged on the side and on the partition, a black upright pull on each meeting edge), inside a hat
    shelf and a rail. The sliding slatted door (front track) closes the next section (a rail, a fixed shelf) and slides over
    the mirror doors (the site's photo shows it moved there). 1.65-01 (2032) adds a section with a sliding oak door on the
    rear track and shelves."""
    D, H = 621, 2200
    pa = 1008                                   # partition A centre (1000 … 1016)
    p = [
        P("side-l", [0, 0, 0, T, H - T, D]),
        P("side-r", [W - T, 0, 0, W, H - T, D]),
        P("top", [0, H - T, 0, W, H, D]),
        P("fascia", [T, 2130, D - T, W - T, H - T, D], grain="x"),
        P("track-top", [T, 2174, 563, W - T, H - T, D - T], mat="chrome"),
        P("bottom", [T, 82, 0, W - T, 98, D]),
        P("rail-front", [T, 60, D - T, W - T, 82, D], grain="x"),
        P("plinth", [T, 0, D - 36, W - T, 60, D - 20], mat="accent"),
        P("plinth-back", [T, 0, 30, W - T, 82, 46]),
        P("track-bottom", [T, 98, 563, W - T, 100, D], mat="chrome"),
        partition("partition-a", pa, 98, H - T, 531),
    ]
    joints = [pa]
    if W > 1600:
        joints.append(1516)
        p.append(partition("partition-b", 1516, 98, H - T, 561))
    xs = [10] + joints + [W - 10]
    for i in range(len(xs) - 1):
        p.append(P(f"back-{i + 1}", [xs[i], 92, 6, xs[i + 1], H - T + 6, 6 + BK], kind="back"))
    # ---- left section: drawers, fixed shelf, mirror doors, hat shelf, rail
    zf = 553                                    # the fronts' face behind the sliding zone (mirror / drawer fronts)
    p += [fixed_shelf("fixed-l", T, 1000, 591, 531),
          shelf("hat-shelf", T, 1000, 1816, 511),
          P("rail-l", [20, 1715, 253, 996, 1740, 278], kind="tube", mat="chrome")]
    moves = []
    for i, (a, b) in enumerate([(101, 344), (347, 590)]):
        tag = str(i + 1)
        fr = P(f"drawer-{tag}", [18, a, zf - T, 998, b, zf], kind="front", grain="x")
        ks = [pull(f"k-{tag}a", 18 + 980 * 0.25, b, zf), pull(f"k-{tag}b", 18 + 980 * 0.75, b, zf)]
        bx = drawer_box(tag, T + 13, 1000 - 13, a + (14 if i == 0 else 16), 190, 87, zf - T)
        p += [fr] + bx + ks
        moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": [fr["id"]] + ids(bx) + ids(ks), "travel": 400})
    for tag, (a, b), hinge, kx in (("l", (18, 506.5), "left", 506.5 - 7), ("r", (509.5, 998), "right", 509.5 + 7)):
        door = P(f"door-{tag}", [a, 593, zf - T - 4, b, 2100, zf - 4], kind="front", grain="y")
        mir = P(f"mirror-{tag}", [a + 3, 596, zf - 4, b - 3, 2097, zf], kind="mirror")
        k = {"id": f"k-door-{tag}", "kind": "handle", "model": "bar", "dir": "up", "d": 150, "band": 10, "t": 6,
             "standoff": 6, "at": [r1(kx), 1100], "z": zf}
        p += [door, mir, k]
        moves.append({"type": "door", "name": f"door_{tag}", "parts": [door["id"], mir["id"], k["id"]], "hinge": hinge,
                      "angle": 100})
    # ---- section B (behind the slatted door): a fixed shelf, a rail
    xb1 = joints[1] - 8 if len(joints) > 1 else W - T
    p += [fixed_shelf("fixed-b", 1016, xb1, 591, 561),
          P("rail-b", [1020, 1905, 270, xb1 - 4, 1930, 295], kind="tube", mat="chrome")]
    # the slatted sliding door (front track): black board 16 + 8 slats 32 at pitch 58.6 (photo), 31.5 margins
    rel = [r1(31.5 + 58.6 * i) for i in range(8)]
    sd = slat_door("door-slats", 1009, 1515 if W > 1600 else W - T, 100, 2128, D, rel, w=32)
    p += sd
    moves.append({"type": "slide", "name": "door_slats", "parts": ids(sd), "by": [-700, 0, 0]})
    # ---- 1.65-01: section C with shelves behind a sliding oak door on the rear track
    if W > 1600:
        p.append(fixed_shelf("fixed-c", 1524, W - T, 591, 561))
        for i, y in enumerate([330, 950, 1300, 1650]):
            p.append(shelf(f"shelf-c{i + 1}", 1524, W - T, y, 541))
        oak = P("door-oak", [1509, 100, 563, W - T, 2128, 579], kind="front", grain="y")
        p.append(oak)
        moves.append({"type": "slide", "name": "door_oak", "parts": ["door-oak"], "by": [-500, 0, 0]})
    return dump(did, [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------------ beds
def bed(did, W, sleep_w):
    """Кровать с подъёмным механизмом: headboard ЛДСП 25 W × 1050 with a black upholstered panel (2 × 6 quilted cells)
    over the box's width; the box (sleeping width + 52: the site gives 2109 × 1652 for 1600) of rails ЛДСП 25 × 320 on a
    recessed plinth frame, a storage bottom; the black metal lift frame with birch slats and the mattress inside the box.
    W (catalogue B) = the headboard's width: 80.5 mm wider than the box each side."""
    L, H = 2109, 1050
    wb = sleep_w + 52
    x0, x1 = (W - wb) / 2, (W + wb) / 2
    z0 = 55                                     # the box starts in front of the upholstered panel
    zb = L - 25                                 # the foot rail
    yb, yt = 40, 360                            # the box's rails
    p = [
        P("headboard", [0, 0, 0, W, H, 25], grain="x"),
        P("headboard-soft", [x0, 477, 25, x1, 990, z0], kind="soft", tufts=[6, 2]),
        P("rail-l", [x0, yb, z0, x0 + 25, yt, zb], grain="z"),
        P("rail-r", [x1 - 25, yb, z0, x1, yt, zb], grain="z"),
        P("rail-head", [x0 + 25, yb, z0, x1 - 25, yt, z0 + 25], grain="x"),
        P("rail-foot", [x0, yb, zb, x1, yt, L], grain="x"),
        P("plinth-l", [x0 + 40, 0, z0 + 40, x0 + 56, yb, zb - 15]),
        P("plinth-r", [x1 - 56, 0, z0 + 40, x1 - 40, yb, zb - 15]),
        P("plinth-head", [x0 + 56, 0, z0 + 40, x1 - 56, yb, z0 + 56]),
        P("plinth-foot", [x0 + 56, 0, zb - 31, x1 - 56, yb, zb - 15]),
        P("storage-bottom", [x0 + 25, yb, z0 + 25, x1 - 25, yb + T, zb], grain="z"),
    ]
    # the lift frame (black steel tubes 30 × 25) with its slats; the mattress on it
    f0, f1 = x0 + 26, x1 - 26
    fz0, fz1 = z0 + 26.5, zb - 1.5
    p += [
        P("lift-l", [f0, 320, fz0, f0 + 30, 345, fz1], mat="black"),
        P("lift-r", [f1 - 30, 320, fz0, f1, 345, fz1], mat="black"),
        P("lift-head", [f0 + 30, 320, fz0, f1 - 30, 345, fz0 + 25], mat="black"),
        P("lift-foot", [f0 + 30, 320, fz1 - 25, f1 - 30, 345, fz1], mat="black"),
        P("lift-mid", [W / 2 - 15, 320, fz0 + 25, W / 2 + 15, 345, fz1 - 25], mat="black"),
    ]
    n = 26 if sleep_w < 1700 else 28
    step = (fz1 - fz0 - 60) / n
    for i in range(n):
        z = fz0 + 30 + i * step + (step - 53) / 2
        p.append(P(f"slat-{i + 1}", [f0 + 5, 345, z, f1 - 5, 353, z + 53], mat="slat", grain="x"))
    mz = (fz0 + fz1) / 2
    p.append(P("mattress", [f0, 353, mz - 1000, f1, 553, mz + 1000], kind="mattress"))
    return dump(did, [W, L, H], p, [])


# ================================================================================================= catalogue fragment
NOTE = "по каталогу, без инструкции; по фото каталога (с. 72–74) и сайта pinskdrev.by"
MODELS = [
    ("deko-0-34", "БМ2.776.0.34", "Тумба «Деко»", "living", [1542, 400, 896], 74, None),
    ("deko-0-33", "БМ2.776.0.33", "Тумба ТВ «Деко»", "living", [1542, 400, 450], 74, None),
    ("deko-0-06", "БМ2.776.0.06", "Шкаф-витрина 2Д «Деко»", "living", [941, 400, 1820], 74, None),
    ("deko-0-05", "БМ2.776.0.05", "Шкаф-витрина «Деко»", "living", [941, 400, 1201], 74, None),
    ("deko-0-51", "БМ2.776.0.51", "Полка «Деко»", "living", [1542, 266, 250], 74, "wall"),
    ("deko-1-31", "БМ2.776.1.31", "Комод «Деко»", "bedroom", [1471, 460, 970], 74, None),
    ("deko-1-30-01", "БМ2.776.1.30-01", "Тумба прикроватная «Деко»", "bedroom", [481, 460, 466], 74, None),
    ("deko-1-30", "БМ2.776.1.30", "Тумба прикроватная «Деко»", "bedroom", [481, 460, 466], 74, None),
    ("deko-1-32", "БМ2.776.1.32", "Зеркало «Деко»", "decor", [1100, 5, 600], 74, "wall"),
    ("deko-1-44-01", "БМ2.776.1.44-01", "Шкаф для одежды 3Д «Деко»", "bedroom", [1530, 621, 2200], 74, None),
    ("deko-1-65-01", "БМ2.776.1.65-01", "Шкаф для одежды «Деко»", "bedroom", [2032, 621, 2200], 74, None),
    ("deko-1-10", "БМ2.776.1.10", "Кровать 2-16 «Деко»", "bedroom", [1813, 2109, 1050], 74, None),
    ("deko-1-15", "БМ2.776.1.15", "Кровать 2-18 «Деко»", "bedroom", [2013, 2109, 1050], 74, None),
]
EXTRA = {
    "deko-1-30-01": "планки слева (как на с. 73–74 и на основном фото сайта)",
    "deko-1-30": "планки справа — зеркальное исполнение 1.30-01",
    "deko-1-44-01": "две распашные зеркальные двери над двумя ящиками + раздвижная дверь с планками",
    "deko-1-65-01": "как 1.44-01 + секция с полками за раздвижной дверью «Дуб Наварра»",
    "deko-1-10": "сп. место 2000×1600, с подъёмным механизмом; L каталога = длина (x = ширина изголовья)",
    "deko-1-15": "сп. место 2000×1800, с подъёмным механизмом; L каталога = длина (x = ширина изголовья)",
    "deko-1-32": "в index.json нет — по с. 74",
}


def write_catalog():
    cat = {
        "finishes": [{
            "id": "deko-navarra",
            "name": "Дуб Наварра / черный",
            "body": "door_enamel_whitey#956b40",
            "front": "door_enamel_whitey#956b40",
            "back": "door_enamel_whitey#956b40",
            "roles": {
                "accent": "door_enamel_whitey#312821",
                "slat": "door_enamel_whitey#8b653e",
                "fabric": "velvet#16110e",
            },
            "swatch": "#956b40",
        }],
        "profiles": {},
        "collections": [{
            "id": "deko", "name": "Деко", "brand": "Пинскдрев", "finishes": ["deko-navarra"], "metal": "black",
            "note": "Каталог «Корпусная мебель ч. II» 2025, с. 72–74 (PDF; 140–145 по нумерации каталога) и фото сайта "
                    "pinskdrev.by; все модули по каталогу / фото, без инструкций. Корпус ЛДСП 16 «Дуб Наварра» (дно под "
                    "боковинами, крышка на них), вкладные фасады заподлицо с кромками корпуса, фасады с планками — черная "
                    "ЛДСП 16 с наклеенными планками из массива березы 30×20, черные ручки-профили на верхней кромке "
                    "фасадов, витрины в черной алюминиевой рамке с тонированным стеклом, черные металлические опоры "
                    "(комод, тумба прикроватная) или пластиковые подпятники; шкафы — распашные зеркальные двери и "
                    "раздвижная дверь с планками; кровати с подъемным механизмом."
        }],
        "models": [],
    }
    for mid, code, name, catg, size, page, mount in MODELS:
        m = {"id": mid, "code": code, "name": name, "collection": "deko", "category": catg, "size": size, "page": page,
             "note": NOTE + ("; " + EXTRA[mid] if mid in EXTRA else "")}
        if mount:
            m["mount"] = mount
        cat["models"].append(m)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deko_catalog.json")
    with open(path, "w") as fh:
        json.dump(cat, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


if __name__ == "__main__":
    print(tumba_034())
    print(tv_033())
    print(vitrine("deko-0-05", 1201, 478, shelves_l=[281], glass_l=[836], shelves_r=[281, 842]))
    print(vitrine("deko-0-06", 1820, 881, shelves_l=[514], glass_l=[1195, 1499], shelves_r=[518, 1223, 1513]))
    print(polka_051())
    print(komod_131())
    print(tumba_130(True))
    print(tumba_130(False))
    print(mirror_132())
    print(wardrobe("deko-1-44-01", 1530))
    print(wardrobe("deko-1-65-01", 2032))
    print(bed("deko-1-10", 1813, 1600))
    print(bed("deko-1-15", 2013, 1800))
    print(write_catalog())
