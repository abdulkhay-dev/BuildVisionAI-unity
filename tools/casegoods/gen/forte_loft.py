"""«Форте Лофт» (Пинскдрев П3.0583): six living-room modules.

Construction (instructions IS-P3-583-0-08 шкаф 2Д and IS-P3-583-0-05 стол журнальный, measured on their vector drawings):
* ЛДСП 16 «Дуб Канзас». The top and the bottom run the full L × B; the sides (B − 20 deep, flush at the back) stand
  between them; the carcass stands on black metal legs 128 high: sleds «Опора 350×70×128» (a 3 mm pad under each end,
  two square posts 30×30, a bar 25 high 10 above the floor) at the ends and a single post «Опора 70×70×128» in the middle.
* A partition 294 deep stands between top and bottom at x = L/2 with a black ЛДСП bar («Брусок» 60 × 16) laid flat on
  its front edge, flush with the sides: the dark strip between the doors. The backs (ДВП чёрная) sit in grooves 17 mm
  from the back edge (z 16.8–20), 4 mm into top / bottom / sides, and meet behind the partition and the fixed shelf.
* Fronts ЛДСП 16 overlay the carcass (накладные петли), 2.5 mm in from the ends, 2 mm gaps top / bottom / between, 41 mm
  apart over the black bar. The vitrine doors are two stiles 100 × 16 with a clear glass 6 mm (304 wide) screwed behind
  them (200 of it shows). Handles «Ручка-скоба СПА-3 320» black matt: a round bar ~336 long, across the door centre.
* Coffee table: top and bottom 1207 × 604 with the sides between them; a black cross partition 500 deep and a black
  lengthwise panel between the left side and it at mid-depth: two niches open to the front and to the back; sleds
  «Опора 465×80×128» and «Опора 70×70×128».
The other modules (0.09, 0.02, 0.01, 0.06) are built the same way from the product photos and the catalogue cut-outs
(p. 71).

z: 0 = the back (wall), B = the front of the top; y up from the floor.
"""
import json
import math
import os

from common import dump, ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
T = 16            # ЛДСП
LEG = 128         # legs «Опора …×128»
PAD = 3           # the legs' top plates
DOOR_Z_GAP = 1    # the doors' back face 1 mm off the sides' front edge (overlay hinges)
BACK_Z = (16.8, 20.0)   # ДВП чёрная in grooves
HANDLE = {"kind": "handle", "model": "bar", "dir": "right", "d": 336, "band": 10, "t": 10, "standoff": 25, "post": 10,
          "covers": ["011"]}


class Case:
    def __init__(self, did, size):
        self.did, self.size = did, list(size)
        self.parts, self.moves = [], []

    def add(self, *ps):
        self.parts += ps
        return ps[-1]

    def dump(self):
        return dump(self.did, self.size, self.parts, self.moves)


# ------------------------------------------------------------------------------------------------------------ helpers
def metal_box(pid, box, covers):
    return {"id": pid, "mat": "metal", "edge": 1, "box": [round(v, 2) for v in box], "covers": [covers]}


def sled(c, tag, x0, x1, zs, pads, post_x, bar_y, covers):
    """A sled leg: pads (3 mm plates) under the bottom, two square posts 30 × 30, a bar between the posts near the floor.
    x0..x1 = the pads' x; zs = the posts' z starts; pads = [(z0, z1), (z0, z1)]; post_x = the posts' x start."""
    ps = []
    for k, (a, b) in enumerate(pads):
        ps.append(metal_box(f"{tag}-pad{k + 1}", [x0, LEG - PAD, a, x1, LEG, b], covers))
    for k, z in enumerate(zs):
        ps.append(metal_box(f"{tag}-post{k + 1}", [post_x, 0, z, post_x + 30, LEG - PAD, z + 30], covers))
    ps[-1]["covers"] = []           # one covers entry per leg (on the first pad)
    for p in ps[1:]:
        p["covers"] = []
    ps.append(metal_box(f"{tag}-bar", [post_x, bar_y[0], zs[0] + 30, post_x + 30, bar_y[1], zs[1]], covers))
    ps[-1]["covers"] = []
    for p in ps:
        if not p["covers"]:
            del p["covers"]
    c.add(*ps)


def post_leg(c, tag, xc, zc, covers, pad=70):
    c.add(metal_box(f"{tag}-pad", [xc - pad / 2, LEG - PAD, zc - pad / 2, xc + pad / 2, LEG, zc + pad / 2], covers),
          {"id": f"{tag}-post", "mat": "metal", "edge": 1, "box": [xc - 15, 0, zc - 15, xc + 15, LEG - PAD, zc + 15]})


def handle(pid, x, y, z):
    h = dict(HANDLE)
    h.update({"id": pid, "at": [round(x, 2), round(y, 2)], "z": z})
    return h


def door(c, name, fid, box, hinge, hy, n=None, grain="y"):
    """A plain door: front box + a handle across its centre at y = hy."""
    p = {"id": fid, "kind": "front", "grain": grain, "box": box}
    if n:
        p = {"n": n, **p}
    c.add(p)
    hid = c.add(handle(f"h-{name}", (box[0] + box[3]) / 2, hy, box[5]))["id"]
    c.moves.append({"type": "door", "name": name, "parts": [fid, hid], "hinge": hinge, "angle": 105})


def vitrine_door(c, name, x0, x1, y0, y1, z0, hinge, hy, n_out, n_in, n_glass, gid):
    """Two stiles 100 wide and a clear glass 304 × 6 screwed behind them (silicone bushings)."""
    z1 = z0 + T
    left = hinge == "left"
    outer = [x0, x0 + 100] if left else [x1 - 100, x1]
    inner = [x1 - 100, x1] if left else [x0, x0 + 100]
    so, si = f"{n_out}-{name}", f"{n_in}-{name}"
    xm = (x0 + x1) / 2
    c.add({"n": n_out, "id": so, "kind": "front", "grain": "y", "box": [outer[0], y0, z0, outer[1], y1, z1]},
          {"n": n_in, "id": si, "kind": "front", "grain": "y", "box": [inner[0], y0, z0, inner[1], y1, z1]},
          {"n": n_glass, "id": gid, "kind": "glass", "box": [xm - 152, y0, z0 - 6, xm + 152, y1, z0]})
    hid = c.add(handle(f"h-{name}", xm, hy, z1))["id"]
    c.moves.append({"type": "door", "name": name, "parts": [so, si, gid, hid], "hinge": hinge, "angle": 105,
                    "axis": [x0 if left else x1, z1]})


def circle_pts(cx, cy, r, k=24):
    return " ".join(("M" if i == 0 else "L") + f" {cx + r * math.cos(2 * math.pi * i / k):.1f} {cy + r * math.sin(2 * math.pi * i / k):.1f}"
                    for i in range(k)) + " Z"


# ------------------------------------------------------------------------------------------------------------ vitrines
def vitrine(did, H, variant):
    """П3.0583.0.08 (by instruction) / 0.09 (by photo): 845 × 350 × H."""
    L, B = 845, 350
    c = Case(did, [L, B, H])
    SD = B - 20                          # sides 330
    yb, yt = LEG + T, H - T              # 144, the top's underside
    zf0 = SD + DOOR_Z_GAP                # doors' back face 331
    zf1 = zf0 + T                        # 347
    xp = L / 2                           # the partition's middle
    c.add({"n": "1", "box": [0, yt, 0, L, H, B]},
          {"n": "2", "box": [0, LEG, 0, L, yb, B]},
          {"n": "3", "box": [0, yb, 0, T, yt, SD]},
          {"n": "4", "box": [L - T, yb, 0, L, yt, SD]},
          {"n": "6", "box": [xp - 8, yb, 20, xp + 8, yt, SD - T]},
          {"n": "10", "mat": "accent", "box": [xp - 30, yb, SD - T, xp + 30, yt - 2, SD]})
    xl0, xl1 = T + 1.25, xp - 8 - 1.25            # a shelf 396 in the left section
    xr0, xr1 = xp + 8 + 1.25, L - T - 1.25
    bx = [(T - 4.5, xp), (xp, L - T + 4.5)]        # backs 411 wide, meeting behind the partition
    dl, dr = (2.5, 402.5), (442.5, 842.5)          # doors 400, 41 apart over the black bar
    if variant == "0.08":
        ys = 545                                   # the fixed shelves' middle = the doors' joint
        c.add({"n": "7", "box": [xl0, ys - 8, 20, xl1, ys + 8, SD - T]},
              {"n": "8", "box": [xr0, ys - 8, 20, xr1, ys + 8, SD - T]})
        for k, (a, b) in enumerate(bx):
            side = "l" if k == 0 else "r"
            c.add({"n": "18", "id": f"18-{side}", "kind": "back", "box": [a, yb - 4, BACK_Z[0], b, ys, BACK_Z[1]]},
                  {"n": "5", "id": f"5-{side}", "kind": "back", "box": [a, ys, BACK_Z[0], b, yt + 4, BACK_Z[1]]})
        for k, y in enumerate((1002, 1463)):
            for side, (a, b) in (("l", (xl0, xl1)), ("r", (xr0, xr1))):
                c.add({"n": "9", "id": f"9-{side}{k + 1}", "kind": "glass", "box": [a, y, 22, b, y + 6, 310]})
        uy0, uy1 = ys + 1, yt - 2                  # 546 … 1917 = 1371
        vitrine_door(c, "door_top_left", *dl, uy0, uy1, zf0, "left", 1016.5, "13", "15", "11", "11-l")
        vitrine_door(c, "door_top_right", *dr, uy0, uy1, zf0, "right", 1016.5, "12", "14", "11", "11-r")
        door(c, "door_bottom_left", "16", [dl[0], yb + 2, zf0, dl[1], ys - 1, zf1], "left", 487, n="16")
        door(c, "door_bottom_right", "17", [dr[0], yb + 2, zf0, dr[1], ys - 1, zf1], "right", 487, n="17")
    else:
        # 0.09: one column of glass shelves behind the vitrine door, ЛДСП shelves behind the solid door (photos)
        for k, (a, b) in enumerate(bx):
            c.add({"id": f"back-{'l' if k == 0 else 'r'}", "kind": "back", "box": [a, yb - 4, BACK_Z[0], b, yt + 4, BACK_Z[1]]})
        for k, y in enumerate((470, 800, 1110)):
            c.add({"id": f"glass-shelf-{k + 1}", "kind": "glass", "box": [xl0, y, 22, xl1, y + 6, 310]})
        for k, y in enumerate((505, 842, 1180)):
            c.add({"id": f"shelf-{k + 1}", "box": [xr0, y, 22, xr1, y + T, 312]})
        vitrine_door(c, "door_left", *dl, yb + 2, yt - 2, zf0, "left", 1118, "st-out", "st-in", "glass", "glass-l")
        for p in c.parts:
            if p.get("n") in ("st-out", "st-in", "glass"):
                del p["n"]
        door(c, "door_right", "door-r", [dr[0], yb + 2, zf0, dr[1], yt - 2, zf1], "right", 1118)
    # legs: sleds 350 × 70 at the ends (pads 70 × 70, posts 30 × 30 at x 20–50), a single post in the middle
    for tag, x0 in (("leg-l", 0), ("leg-r", L - 70)):
        sled(c, tag, x0, x0 + 70, [20, 300], [(0, 70), (280, 350)], x0 + 20, (10, 35), "007")
    post_leg(c, "leg-m", xp, 175, "008")
    return c.dump()


# ------------------------------------------------------------------------------------------------------------ chest
def chest():
    """П3.0583.0.02 Комод 1574 × 420 × 925 (by the catalogue cut-out p. 71 and the room photo): two doors with the black
    bar between them, a column of four drawers; top and bottom overhang the sides by 10 mm (cut-out)."""
    L, B, H = 1574, 420, 925
    c = Case("forte-loft-0-02", [L, B, H])
    SD = B - 20
    yb, yt = LEG + T, H - T
    zf0, zf1 = SD + DOOR_Z_GAP, SD + DOOR_Z_GAP + T
    xs0, xs1 = 10, L - 10                          # the sides' outer faces
    p1, p2 = 528.5, 1048                           # partition middles: behind the black bar / the door–drawer joint
    c.add({"id": "top", "box": [0, yt, 0, L, H, B]},
          {"id": "bottom", "box": [0, LEG, 0, L, yb, B]},
          {"id": "side-l", "box": [xs0, yb, 0, xs0 + T, yt, SD]},
          {"id": "side-r", "box": [xs1 - T, yb, 0, xs1, yt, SD]},
          {"id": "partition-1", "box": [p1 - 8, yb, 20, p1 + 8, yt, SD - T]},
          {"id": "bar", "mat": "accent", "box": [p1 - 30, yb, SD - T, p1 + 30, yt - 2, SD]},
          {"id": "partition-2", "box": [p2 - 8, yb, 20, p2 + 8, yt, SD]})
    # loose shelves in the door compartments (one each, 2 mm narrower than the compartment)
    for sid, (a, b) in (("shelf-l", (xs0 + T, p1 - 8)), ("shelf-m", (p1 + 8, p2 - 8))):
        c.add({"id": sid, "box": [a + 1, 520, 22, b - 1, 520 + T, SD - T - 2]})
    for bid, (a, b) in (("back-l", (xs0 + T - 4.5, p1)), ("back-m", (p1, p2)), ("back-r", (p2, xs1 - T + 4.5))):
        c.add({"id": bid, "kind": "back", "box": [a, yb - 4, BACK_Z[0], b, yt + 4, BACK_Z[1]]})
    fy0, fy1 = yb + 2, yt - 2                      # 146 … 907
    door(c, "door_left", "door-l", [xs0 + 2, fy0, zf0, xs0 + 502, fy1, zf1], "left", fy1 - 66)
    door(c, "door_right", "door-m", [545, fy0, zf0, 1045, fy1, zf1], "right", fy1 - 66)
    # drawers: fronts 192 / 196 / 196 / 168 with 3 mm gaps, boxes on 350 runners (13 mm each side)
    dx0, dx1 = p2, xs1 - 2
    fronts = [(146, 338), (341, 537), (540, 736), (739, 907)]
    bx0, bx1 = p2 + 8 + 13, xs1 - T - 13
    for k, (a, b) in enumerate(fronts):
        tag = str(k + 1)
        h = b - a - 46
        y0 = a + 20
        z0, z1 = zf0 - 350, zf0 - 1
        ids = [f"df-{tag}", f"ds-l-{tag}", f"ds-r-{tag}", f"db-{tag}", f"dd-{tag}"]
        c.add({"id": ids[0], "kind": "front", "box": [dx0 + 1.5, a, zf0, dx1, b, zf1]},
              {"id": ids[1], "box": [bx0, y0, z0, bx0 + T, y0 + h, z1]},
              {"id": ids[2], "box": [bx1 - T, y0, z0, bx1, y0 + h, z1]},
              {"id": ids[3], "box": [bx0 + T, y0, z0, bx1 - T, y0 + h, z0 + T]},
              {"id": ids[4], "kind": "back", "box": [bx0 + 11, y0 + 10, z0 + 4, bx1 - 11, y0 + 13.5, z1]})
        hid = c.add(handle(f"h-drawer-{tag}", (dx0 + 1.5 + dx1) / 2, b - 66, zf1))["id"]
        c.moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": ids + [hid], "travel": 300})
    # legs: sleds 400 × 70 with the posts at x 73–103 from the ends (cut-out), two single posts
    for tag, x0 in (("leg-l", 53), ("leg-r", L - 53 - 70)):
        sled(c, tag, x0, x0 + 70, [30, 360], [(10, 80), (340, 410)], x0 + 20, (10, 35), "opora-sled")
    post_leg(c, "leg-m1", 556, 210, "opora")
    post_leg(c, "leg-m2", 1000, 210, "opora")
    return c.dump()


# ------------------------------------------------------------------------------------------------------------ TV unit
def tv_unit():
    """П3.0583.0.01 Тумба ТВ 1704 × 420 × 540 (by the catalogue cut-out and the room photo p. 71): two doors round an
    open niche with black partitions and a black back with two cable holes."""
    L, B, H = 1704, 420, 540
    c = Case("forte-loft-0-01", [L, B, H])
    SD = B - 20
    yb, yt = LEG + T, H - T
    zf0, zf1 = SD + DOOR_Z_GAP, SD + DOOR_Z_GAP + T
    pa, pb = 534, L - 534                          # the niche partitions' middles (niche 620 between them)
    c.add({"id": "top", "box": [0, yt, 0, L, H, B]},
          {"id": "bottom", "box": [0, LEG, 0, L, yb, B]},
          {"id": "side-l", "box": [0, yb, 0, T, yt, SD]},
          {"id": "side-r", "box": [L - T, yb, 0, L, yt, SD]},
          {"id": "partition-l", "mat": "accent", "box": [pa - 8, yb, 20, pa + 8, yt, SD]},
          {"id": "partition-r", "mat": "accent", "box": [pb - 8, yb, 20, pb + 8, yt, SD]})
    for bid, (a, b) in (("back-l", (T - 4.5, pa)), ("back-r", (pb, L - T + 4.5))):
        c.add({"id": bid, "kind": "back", "box": [a, yb - 4, BACK_Z[0], b, yt + 4, BACK_Z[1]]})
    # the niche's back: two cable holes Ø60 on the middle line (cut-out), an outline in the front plane
    x0, x1, y0, y1 = pa, pb, yb - 4, yt + 4
    outline = f"M {x0} {y0} L {x1} {y0} L {x1} {y1} L {x0} {y1} Z " + circle_pts(L / 2, 300, 30) + " " + circle_pts(L / 2, 413, 30)
    c.add({"id": "back-niche", "kind": "back", "shape": "path", "outline": outline, "box": [x0, y0, BACK_Z[0], x1, y1, BACK_Z[1]]})
    fy0, fy1 = yb + 2, yt - 2                      # 146 … 522
    door(c, "door_left", "door-l", [2.5, fy0, zf0, 522.5, fy1, zf1], "left", fy1 - 66)
    door(c, "door_right", "door-r", [L - 522.5, fy0, zf0, L - 2.5, fy1, zf1], "right", fy1 - 66)
    for tag, x0 in (("leg-l", 6), ("leg-r", L - 6 - 70)):
        sled(c, tag, x0, x0 + 70, [30, 360], [(10, 80), (340, 410)], x0 + 20, (10, 35), "opora-sled")
    post_leg(c, "leg-m1", 580, 210, "opora")
    post_leg(c, "leg-m2", L - 580, 210, "opora")
    return c.dump()


# ------------------------------------------------------------------------------------------------------------ coffee table
def coffee_table():
    """П3.0583.0.05 Стол журнальный 1207 × 604 × 426 (by instruction)."""
    L, B, H = 1207, 604, 426
    c = Case("forte-loft-0-05", [L, B, H])
    yb, yt = LEG + T, H - T                        # 144, 410
    c.add({"n": "1", "grain": "x", "box": [0, yt, 0, L, H, B]},
          {"n": "5", "grain": "x", "box": [0, LEG, 0, L, yb, B]},
          {"n": "2", "id": "2-l", "box": [0, yb, 2, T, yt, B - 2]},
          {"n": "2", "id": "2-r", "box": [L - T, yb, 2, L, yt, B - 2]},
          {"n": "4", "mat": "accent", "box": [688, yb, 52, 704, yt, 552]},
          {"n": "3", "mat": "accent", "box": [T, yb, 294, 688, yt, 310]})
    # sleds 465 × 80 × 128: pads 80 × 60 at both ends, posts 30 × 30 near the pads' inner side, a bar 20 high
    for tag, (px0, pst) in (("leg-l", (71, 116)), ("leg-r", (L - 151, L - 146))):
        sled(c, tag, px0, px0 + 80, [94, 480], [(70, 130), (474, 534)], pst, (8, 28), "005")
    post_leg(c, "leg-m", 700, 302, "004")
    return c.dump()


# ------------------------------------------------------------------------------------------------------------ wall shelf
def shelf():
    """П3.0583.0.06 Полка 1370 × 240 × 210 (by the catalogue cut-out and the room photo): a board 1370 × 240, a back
    board 1246 × 190 standing on it against the wall, two black flat-bar brackets over the back board."""
    L, B, H = 1370, 240, 210
    c = Case("forte-loft-0-06", [L, B, H])
    c.add({"id": "board", "grain": "x", "box": [0, 0, 0, L, T, B]},
          {"id": "back-board", "grain": "x", "box": [62, T, 0, L - 62, T + 190, T]})
    for tag, x0 in (("bracket-l", 90), ("bracket-r", L - 120)):
        c.add({"id": f"{tag}-front", "mat": "metal", "edge": 0.5, "box": [x0, T, T, x0 + 30, H, T + 4]},
              {"id": f"{tag}-top", "mat": "metal", "edge": 0.5, "box": [x0, T + 190, 0, x0 + 30, H, T]})
    return c.dump()


# ------------------------------------------------------------------------------------------------------------ catalogue
FINISH = "forte-loft-kanzas-antracit"


def catalog():
    frag = {
        "finishes": [{
            "id": FINISH, "name": "Дуб Канзас / Антрацит",
            "body": "door_enamel_whitey#705b4e", "back": "door_enamel_whitey#222b38",
            "roles": {"accent": "door_enamel_whitey#222b38"}, "swatch": "#705b4e"}],
        "profiles": {},
        "collections": [{
            "id": "forte-loft", "name": "Форте Лофт", "brand": "Пинскдрев", "finishes": [FINISH], "metal": "black",
            "note": "Каталог «Корпусная мебель ч. II» 2025, с. 71 (PDF; с. 138–139 по нумерации каталога). Корпус ЛДСП 16 "
                    "«Дуб Канзас»: крышка и дно на всю ширину, боковины между ними; перегородка с чёрным бруском 60 мм "
                    "между дверями; накладные двери ЛДСП 16 (витрины — две стойки 100 и прозрачное стекло 6 мм за ними); "
                    "ручки-скобы СПА-3 320 чёрные матовые; задние стенки ДВП чёрная в пазах; чёрные металлические "
                    "опоры-салазки и одиночные опоры 128 мм."}],
        "models": [
            {"id": "forte-loft-0-08", "code": "П3.0583.0.08", "name": "Шкаф 2Д «Форте Лофт»", "collection": "forte-loft",
             "category": "living", "size": [845, 350, 1935], "is": "IS-P3-583-0-08-Forte-SHkaf-2d-1.pdf", "page": 71,
             "note": "витрина: две застеклённые двери над двумя глухими"},
            {"id": "forte-loft-0-09", "code": "П3.0583.0.09", "name": "Шкаф 2Д «Форте Лофт»", "collection": "forte-loft",
             "category": "living", "size": [845, 350, 1535], "page": 71,
             "note": "по фото сайта и каталогу, без инструкции; левая дверь-витрина, правая глухая"},
            {"id": "forte-loft-0-02", "code": "П3.0583.0.02", "name": "Комод «Форте Лофт»", "collection": "forte-loft",
             "category": "living", "size": [1574, 420, 925], "page": 71,
             "note": "по каталогу, без инструкции; две двери и четыре ящика"},
            {"id": "forte-loft-0-01", "code": "П3.0583.0.01", "name": "Тумба ТВ «Форте Лофт»", "collection": "forte-loft",
             "category": "living", "size": [1704, 420, 540], "page": 71,
             "note": "по каталогу, без инструкции; открытая ниша с чёрными стенками"},
            {"id": "forte-loft-0-05", "code": "П3.0583.0.05", "name": "Стол журнальный «Форте Лофт»", "collection": "forte-loft",
             "category": "tables", "size": [1207, 604, 426], "is": "IS-P3-583-0-05-Forte-Stol-Jurn-1.pdf", "page": 71},
            {"id": "forte-loft-0-06", "code": "П3.0583.0.06", "name": "Полка «Форте Лофт»", "collection": "forte-loft",
             "category": "living", "size": [1370, 240, 210], "page": 71, "mount": "wall",
             "note": "по каталогу, без инструкции; навесная, чёрные кронштейны"},
        ],
    }
    path = os.path.join(HERE, "forte-loft_catalog.json")
    with open(path, "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return path


if __name__ == "__main__":
    print(vitrine("forte-loft-0-08", 1935, "0.08"))
    print(vitrine("forte-loft-0-09", 1535, "0.09"))
    print(chest())
    print(tv_unit())
    print(coffee_table())
    print(shelf())
    print(catalog())
