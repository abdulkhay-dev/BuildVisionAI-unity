"""«Монако» (П6.528): Pinskdrev case furniture — a frame of 25 mm «Дуб Саттер» ЛДСП (sides standing on ФБ 482 glides,
the top 25 on them), the fronts (МДФ 19.5 «6G Белый глянец» or «Серый Мокко») set 27 mm deep inside that frame, with
milled V-grooves every ~300 mm and the collection's «handle»: a crescent cut into a front's top edge that shows the oak
front rail (living room) or the oak «накладка» (bedroom doors) behind it.

Sizes come from the instructions' cut lists, or — where the table lists names only — from the dimension-true vector
drawings of the instruction PDFs (read with PyMuPDF, ±1 mm). See tools/casegoods/notes/monako.md.

    python3 tools/casegoods/gen/monako.py            # writes Designs/monako-*.json and gen/monako_catalog.json
"""
import json
import math
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------------------------------- living room
T = 25.0            # sides / tops
GL = 5.0            # ФБ 482 glide under the sides
SD, TD = 420.0, 421.0
FP = 373.0          # the carcass' front plane: fixed panels 370 deep from z 3, front rails 16 at z 357..373
FZ = 393.0          # the fronts' face (19.5: z 373.5..393) — 27 mm inside the oak frame
GROOVE = {"type": "grooves", "w": 8, "depth": 3, "flute": "v"}


def P(n, box, pid=None, **kw):
    p = {"n": n, "box": [round(v, 1) for v in box]}
    if pid:
        p["id"] = pid
    p.update(kw)
    return p


def back(n, x0, y0, x1, y1, pid=None, z0=0.0, t=3.0):
    """ХДФ back nailed on the carcass' rear edges (counted into the carcass depth: it sits over the rear 3 mm)."""
    return P(n, [x0, y0, z0, x1, y1, z0 + t], pid, kind="back")


def glides(xs, zs, letter="g"):
    out, k = [], 0
    for x in xs:
        for z in zs:
            k += 1
            out.append({"id": f"{letter}-{k}", "kind": "tube", "mat": "black", "box": [x - 10, 0, z - 10, x + 10, GL, z + 10],
                        "covers": [letter]})
    return out


def arc_pts(x0, x1, depth, low="mid", n=12):
    """(x, depth) samples of a circular crescent from x0 to x1 (depth 0 at the ends of a symmetric lens)."""
    pts = []
    if low == "mid":
        c, h = (x0 + x1) / 2, (x1 - x0) / 2
        r = (h * h + depth * depth) / (2 * depth)
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            pts.append((x, depth - (r - math.sqrt(max(r * r - (x - c) ** 2, 0)))))
    return pts


def notched_outline(x0, y0, x1, y1, top=None, bottom=None, notch=None):
    """A front's outline (front plane): `top` = [(x, depth), …] of a crescent cut down from the top edge, `bottom` the
    same up from the bottom edge, `notch` = (nx0, ny0, nx1, ny1) a window open to the left or right edge. A crescent that
    is deepest at the front's edge leaves that corner out."""
    near = lambda a, b: abs(a - b) < 0.6
    pts = [(x0, y0)]
    if bottom:
        for x, d in sorted(bottom):
            pts.append((x, y0 + d))
    pts.append((x1, y0))
    if notch and notch[2] >= x1 - 0.5:
        nx0, ny0, _, ny1 = notch
        pts += [(x1, ny0), (nx0, ny0), (nx0, ny1), (x1, ny1)]
    tchain = sorted(top or [], key=lambda q: -q[0])
    if not (tchain and near(tchain[0][0], x1) and tchain[0][1] > 0.5):
        pts.append((x1, y1))
    for x, d in tchain:
        pts.append((x, y1 - d))
    if not (tchain and near(tchain[-1][0], x0) and tchain[-1][1] > 0.5):
        pts.append((x0, y1))
    if notch and notch[0] <= x0 + 0.5:
        nx0, ny0, nx1, ny1 = notch
        pts += [(x0, ny1), (nx1, ny1), (nx1, ny0), (x0, ny0)]
    out = []
    for q in pts:
        q = (round(q[0], 1), round(q[1], 1))
        if not out or out[-1] != q:
            out.append(q)
    if out[0] == out[-1]:
        out.pop()
    return "M " + " L ".join(f"{a:g} {b:g}" for a, b in out) + " Z"


def front(n, x0, y0, x1, y1, pid=None, t=19.5, fz=FZ, top=None, bottom=None, notch=None, grooves=(), gx=None, mat=None):
    """A front (МДФ gloss), face at fz. top / bottom crescents clipped to the front's own span; grooves = y of V-grooves
    across the front (gx = (a, b): only across that x-span, e.g. the strip beside a glass window)."""
    p = P(n, [x0, y0, fz - t, x1, y1, fz], pid, kind="front")
    if mat:
        p["mat"] = mat
    clip = lambda pts: [(x, d) for x, d in pts if x0 - 0.01 <= x <= x1 + 0.01] if pts else None
    top, bottom = clip(top), clip(bottom)
    if top or bottom or notch:
        p["shape"] = "path"
        p["outline"] = notched_outline(x0, y0, x1, y1, top, bottom, notch)
    if grooves:
        a, b = gx or (x0, x1)
        p["face"] = dict(GROOVE, lines=[[round(a, 1), round(y, 1), round(b, 1), round(y, 1)] for y in grooves])
    return p


def crescent(pts, y_top):
    """Drawing samples (x, y) of a crescent → (x, depth below y_top)."""
    return [(x, round(y_top - y, 1)) for x, y in pts]


def mirror(parts, moves, W):
    """The mirror-image variant (-01): flip x."""
    import re
    fx = lambda x: round(W - x, 1)
    out = []
    for p in parts:
        q = json.loads(json.dumps(p))
        if "box" in q:
            b = q["box"]
            q["box"] = [fx(b[3]), b[1], b[2], fx(b[0]), b[4], b[5]]
        if "outline" in q:
            nums = re.findall(r"[A-Z]|-?\d+(?:\.\d+)?", q["outline"])
            res, i, cmd, k = [], 0, None, 0
            for tkn in nums:
                if tkn.isalpha():
                    res.append(tkn)
                    k = 0
                    continue
                res.append(f"{fx(float(tkn)):g}" if k % 2 == 0 else tkn)
                k += 1
            q["outline"] = " ".join(res)
        if q.get("face", {}).get("lines"):
            q["face"]["lines"] = [[fx(l[2]), l[1], fx(l[0]), l[3]] for l in q["face"]["lines"]]
        if q.get("face", {}).get("area"):
            a = q["face"]["area"]
            q["face"]["area"] = [fx(a[2]), a[1], fx(a[0]), a[3]]
        if "at" in q:
            q["at"] = [fx(q["at"][0]), q["at"][1]]
        if "from" in q:
            q["from"] = [fx(q["from"][0])] + q["from"][1:]
            q["to"] = [fx(q["to"][0])] + q["to"][1:]
        out.append(q)
    mv = json.loads(json.dumps(moves))
    for m in mv:
        if m.get("hinge") in ("left", "right"):
            m["hinge"] = "right" if m["hinge"] == "left" else "left"
        if "by" in m:
            m["by"] = [-m["by"][0]] + m["by"][1:]
    return out, mv


def door(name, parts, hinge, angle=100):
    return {"type": "door", "name": name, "parts": parts, "hinge": hinge, "angle": angle}


def drawer_box(tag, ns, x0, x1, y0, h, z0, depth, back_h=None, bottom_t=3.0, bottom_len=None, bw=None):
    """Drawer box outer x0..x1: sides 16 full height and depth, the back between them (h − 14) standing on the ХДФ
    bottom that runs in the sides' grooves and 5 mm into the front's groove. ns = (left, right, back, bottom).
    bottom_t 16 = a chipboard bottom between the sides, the back behind it."""
    zb = z0 - depth
    bh = back_h if back_h is not None else h - 14
    out = [
        P(ns[0], [x0, y0, zb, x0 + 16, y0 + h, z0], f"{ns[0]}-{tag}"),
        P(ns[1], [x1 - 16, y0, zb, x1, y0 + h, z0], f"{ns[1]}-{tag}"),
    ]
    if bottom_t < 10:
        out.append(P(ns[2], [x0 + 16, y0 + h - bh, zb, x1 - 16, y0 + h, zb + 16], f"{ns[2]}-{tag}"))
        bl = bottom_len or (depth + 5)
        e = (x1 - x0 - bw) / 2 if bw else 11
        out.append(P(ns[3], [x0 + e, y0 + 10, z0 + 5 - bl, x1 - e, y0 + 10 + bottom_t, z0 + 5], f"{ns[3]}-{tag}", kind="back"))
    else:
        out.append(P(ns[2], [x0 + 16, y0 + h - bh, zb, x1 - 16, y0 + h, zb + 16], f"{ns[2]}-{tag}"))
        bl = bottom_len or (depth - 16)
        out.append(P(ns[3], [x0 + 16, y0, zb + 16, x1 - 16, y0 + bottom_t, zb + 16 + bl], f"{ns[3]}-{tag}"))
    return out


def dmove(name, parts, travel=300):
    return {"type": "drawer", "name": name, "parts": parts, "travel": travel}


def box_ids(box):
    return [q["id"] for q in box]


# ------------------------------------------------------------------------------------ 0.01 / 0.01-01 шкаф-витрина
def m0_01(mirrored=False):
    """Шкаф 634×421×1900 (instruction P6-528-0-01): a glass door 10.1 with a window notch open to its free edge (the
    glass 10.2 behind it), a plain door 11 whose top edge carries the crescent over the rail 8."""
    W = 634
    p = [
        P("1", [0, GL, 0, T, GL + 1870, SD]),
        P("2", [W - T, GL, 0, W, GL + 1870, SD]),
        P("3", [0, 1875, 0, W, 1900, TD], grain="x"),
        P("9", [27, GL, FP - 16, 607, 61, FP], "9-f"),
        P("9", [27, GL, 3, 607, 61, 19], "9-b"),
        P("4", [27, 61, 3, 607, 77, FP]),
        P("6", [27, 352, 3, 607, 368, FP]),
        P("8", [27, 593, FP - 16, 607, 663, FP]),
        P("5", [27, 663, 3, 607, 679, FP]),
    ]
    for k, y in enumerate((966, 1266, 1566)):
        p.append(P("7", [28, y, 13, 606, y + 6, 363], f"7-{k + 1}", kind="glass"))
    p += [back("13", 8, 63, 626, 671), back("12", 8, 671, 626, 1893)]
    # door 11: the crescent is deepest at the free-edge side of the glass window, running out 426 mm along
    cres = crescent([(29, 623.1), (48.8, 623.1), (130.6, 624.3), (212.3, 629.6), (293.5, 637.3), (374.7, 648.4),
                     (455.3, 663)], 663)
    p.append(front("10.1", 29, 667, 605, 1872, notch=(29, 817, 455, 1722), grooves=(970, 1270, 1570), gx=(455, 605)))
    p.append(P("10.2", [29, 795, FZ - 19.5 - 4, 475, 1745, FZ - 19.5], kind="glass"))
    p.append(front("11", 29, 63, 605, 663, top=cres, grooves=(364,)))
    p += glides((12.5, W - 12.5), (25, 395))
    moves = [door("door_top", ["10.1", "10.2"], "right"), door("door_bottom", ["11"], "right")]
    if mirrored:
        p, moves = mirror(p, moves, W)
    return dump("monako-0-01-01" if mirrored else "monako-0-01", [W, 421, 1900], p, moves)


# ---------------------------------------------------------------------------------------------- 0.02 тумба ТВ
def m0_02():
    W = 1704
    p = [
        P("1", [0, GL, 0, T, 565, SD]),
        P("2", [W - T, GL, 0, W, 565, SD]),
        P("5", [0, 565, 0, W, 590, TD], grain="x"),
        P("9", [27, GL, FP - 16, 1677, 61, FP], "9-f"),
        P("9", [27, GL, 3, 1677, 61, 19], "9-b"),
        P("6", [27, 61, 3, 1677, 77, FP]),
        P("3", [569, 77, 3, 585, 565, FP]),
        P("10", [27, 495, FP - 16, 569, 565, FP]),
        P("7", [27, 304, 3, 569, 320, FP]),
        P("4", [1118.5, 77, 3, 1134.5, 397, FP - 16]),
        P("11", [585, 327, FP - 16, 1677, 397, FP]),
        P("8", [585, 397, FP - 354, 1677, 413, FP]),
        back("15", 10, 63, 578, 586),
        back("16", 578, 63, 1696, 586),
    ]
    c12 = [(179.5, 0), (191.3, 8.9), (204, 16.5), (217.1, 23.3), (230.7, 29.2), (244.2, 33.9), (258.6, 37.7), (273, 40.6),
           (287.8, 42.3), (302.6, 42.8)]
    c12 += [(605.2 - x, d) for x, d in reversed(c12[:-1])]
    c13 = [(819.8, 0), (879.9, 14.4), (940.5, 25.4), (1001.8, 33.4), (1063.2, 38.5), (1125, 40.2), (1128, 40.2),
           (1189.8, 38.5), (1251.1, 33.4), (1312.1, 25.4), (1373, 14.4), (1432.7, 0)]
    p += [
        front("12", 29, 61, 576, 558, top=c12, grooves=(312,)),
        front("13", 578, 61, 1125, 413, top=c13, grooves=(312,)),
        front("14", 1128, 61, 1675, 413, top=c13, grooves=(312,)),
    ]
    p += glides((12.5, 577, 1126.5, W - 12.5), (25, 395))
    moves = [door("door_left", ["12"], "left"), door("door_mid", ["13"], "left"), door("door_right", ["14"], "right")]
    return dump("monako-0-02", [W, 421, 590], p, moves)


# ---------------------------------------------------------------------------------------------- 0.03 тумба
def m0_03():
    W = 1424
    p = [
        P("1", [0, GL, 0, T, 815, SD]),
        P("2", [W - T, GL, 0, W, 815, SD]),
        P("7", [0, 815, 0, W, 840, TD], grain="x"),
        P("12", [27, GL, FP - 16, 1397, 61, FP], "12-f"),
        P("12", [27, GL, 3, 1397, 61, 19], "12-b"),
        P("8", [27, 61, 3, 1397, 77, FP]),
        P("5", [473, 77, 3, 489, 633, FP - 16]),
        P("6", [935, 77, 3, 951, 633, FP - 16]),
        P("11", [27, 563, FP - 16, 1397, 633, FP]),
        P("9", [27, 633, 3, 1397, 649, FP]),
        P("3", [473, 649, 3, 489, 815, FP]),
        P("4", [935, 649, 3, 951, 815, FP]),
        P("10", [27, 338, 3, 473, 354, FP - 16], "10-1"),
        P("10", [951, 338, 3, 1397, 354, FP - 16], "10-2"),
        back("20", 10, 63, 482, 836),
        back("22", 482, 63, 942, 836),
        back("21", 942, 63, 1414, 836),
    ]
    moves = []
    # top drawers 13 / 15 / 14 (boxes all numbered 13.x: the table lists 13.2 … 13.5 three times)
    for fn, x0, x1, op in (("13.1", 29, 483, (27, 473)), ("15.1", 485, 939, (489, 935)), ("14.1", 941, 1395, (951, 1397))):
        tag = fn.split(".")[0]
        p.append(front(fn, x0, 638, x1, 813))
        c = (op[0] + op[1]) / 2
        bx = drawer_box(tag, ("13.2", "13.3", "13.4", "13.5"), c - 219, c + 219, 660, 114, FZ - 19.5, 350, bw=416)
        p += bx
        moves.append(dmove(f"drawer_{tag}", [fn] + box_ids(bx)))
    # middle column: drawer 16 (244) and the push-to-open drawer 17 (284, front 16.5, chipboard bottom)
    p.append(front("16.1", 485, 352, 939, 596))
    b16 = drawer_box("16", ("16.2", "16.3", "16.4", "16.5"), 493, 931, 380, 174, FZ - 19.5, 360, bw=416)
    p += b16
    moves.append(dmove("drawer_16", ["16.1"] + box_ids(b16)))
    p.append(front("17.1", 485, 66, 939, 350, t=16.5))
    b17 = drawer_box("17", ("17.2", "17.3", "17.4", "17.5"), 493, 931, 90, 174, FZ - 16.5, 360, back_h=164, bottom_t=16,
                     bottom_len=343)
    p += b17
    moves.append(dmove("drawer_17", ["17.1"] + box_ids(b17)))
    cres = [(178.3, 0), (238.1, 14.3), (299, 25.9), (359.8, 33.9), (421.2, 38.6), (483.1, 40.2),
            (940.9, 40.2), (1002.8, 38.6), (1064.2, 33.9), (1125.5, 25.9), (1185.9, 14.3), (1246.2, 0)]
    p.append(front("18", 29, 66, 483, 636, top=cres, grooves=(351,)))
    p.append(front("19", 941, 66, 1395, 636, top=cres, grooves=(351,)))
    moves += [door("door_left", ["18"], "left"), door("door_right", ["19"], "right")]
    p += glides((12.5, 481, 943, W - 12.5), (25, 395))
    return dump("monako-0-03", [W, 421, 840], p, moves)


# ---------------------------------------------------------------------------------------------- 0.05 шкаф
def m0_05():
    W = 934
    p = [
        P("1", [0, GL, 0, T, 1875, SD]),
        P("2", [W - T, GL, 0, W, 1875, SD]),
        P("5", [0, 1875, 0, W, 1900, TD], grain="x"),
        P("13", [27, GL, FP - 16, 907, 61, FP], "13-f"),
        P("13", [27, GL, 3, 907, 61, 19], "13-b"),
        P("6", [27, 61, 3, 907, 77, FP]),
        P("4", [311, 77, 3, 327, 663, FP - 16]),
        P("12", [27, 593, FP - 16, 907, 663, FP]),
        P("7", [27, 663, 3, 907, 679, FP]),
        P("3", [311, 679, 3, 327, 1875, FP]),
        P("10", [27, 352, 3, 311, 368, FP - 16]),
        P("8", [327, 352, 3, 907, 368, FP - 16]),
    ]
    for k, y in enumerate((965, 1268, 1571)):
        p.append(P("9", [27, y, 3, 311, y + 16, FP], f"9-{k + 1}"))
    for k, y in enumerate((966, 1266, 1566)):
        p.append(P("11", [328, y, 13, 906, y + 6, 363], f"11-{k + 1}", kind="glass"))
    p += [back("19", 8, 63, 926, 671), back("18", 8, 671, 926, 1893)]
    c = [(179.3, 0), (207.8, 11.1), (236.9, 20.1), (266.6, 28.1), (296.7, 33.9), (326.8, 38.6),
         (329, 40.2), (349.1, 40.2), (427.9, 38.6), (480.2, 36), (517.2, 31.8), (559.6, 29.6), (593.4, 25.9),
         (674.3, 14.3), (754.7, 0)]
    p += [
        front("16", 29, 667, 327, 1872, grooves=(970, 1270, 1570)),
        front("17", 29, 63, 327, 663, top=c, grooves=(364,)),
        front("14.1", 329, 667, 905, 1872, notch=(329, 817, 755, 1722), grooves=(970, 1270, 1570), gx=(755, 905)),
        P("14.2", [329, 795, FZ - 19.5 - 4, 775, 1745, FZ - 19.5], kind="glass"),
        front("15", 329, 63, 905, 663, top=c, grooves=(364,)),
    ]
    p += glides((12.5, 319, W - 12.5), (25, 395))
    moves = [door("door_left_top", ["16"], "left"), door("door_left_bottom", ["17"], "left"),
             door("door_right_top", ["14.1", "14.2"], "right"), door("door_right_bottom", ["15"], "right")]
    return dump("monako-0-05", [W, 421, 1900], p, moves)


# ---------------------------------------------------------------------------------------------- 0.06 тумба ТВ
def m0_06():
    W = 1424
    p = [
        P("1", [0, GL, 0, T, 465, SD]),
        P("2", [W - T, GL, 0, W, 465, SD]),
        P("5", [0, 465, 0, W, 490, TD], grain="x"),
        P("9", [27, GL, FP - 16, 1397, 61, FP], "9-f"),
        P("9", [27, GL, 3, 1397, 61, 19], "9-b"),
        P("6", [27, 61, 3, 1397, 77, FP]),
        P("4", [704, 77, 3, 720, 297, FP - 16]),
        P("8", [27, 243, FP - 16, 1397, 313, FP]),
        P("7", [27, 297, 3, 1397, 313, FP - 16]),
        P("3", [704, 313, 3, 720, 465, 327]),
        back("12", 9, 63, 712, 485),
        back("13", 712, 63, 1415, 485),
    ]
    c = [(406, 0), (466.1, 14.4), (526.6, 25.9), (588, 33.9), (649.4, 38.6), (711.2, 40.2), (712.8, 40.2),
         (774.6, 38.6), (836, 33.9), (897.4, 25.9), (957.9, 14.4), (1018.1, 0)]
    moves = []
    for side, x0, x1, op in (("10", 29, 711, (25, 704)), ("11", 713, 1395, (720, 1399))):
        fn = side + ".1"
        p.append(front(fn, x0, 61, x1, 313, top=c, grooves=(212,)))
        cx = (op[0] + op[1]) / 2
        bx = drawer_box(side, (side + ".2", side + ".3", side + ".4", side + ".5"), cx - 334.5, cx + 334.5, 95, 114,
                        FZ - 19.5, 350, bw=646)
        p += bx
        moves.append(dmove(f"drawer_{side}", [fn] + box_ids(bx)))
    p += glides((12.5, 712, W - 12.5), (25, 395))
    return dump("monako-0-06", [W, 421, 490], p, moves)


# ---------------------------------------------------------------------------------------------- 0.07 / 0.08 полки
def shelf(did, L):
    """Wall shelf: a back board 1 (L × 340 × 25) with the shelf board 2 (L × 215 × 25) screwed to its face at the bottom."""
    p = [
        P("1", [0, 0, 0, L, 340, 25], grain="x"),
        P("2", [0, 0, 25, L, 25, 240], grain="x"),
    ]
    return dump(did, [L, 240, 340], p, [])


# ------------------------------------------------------------------------------------------------ common (2)
def half_lens(xa, xb, depth, n=16):
    """A crescent running out at xa (depth 0) and deepest (horizontal tangent) at xb: a circular arc."""
    if xb >= xa:
        return [(x, d) for x, d in arc_pts(xa, 2 * xb - xa, depth, n=n) if x <= xb + 0.01]
    return [(x, d) for x, d in arc_pts(2 * xb - xa, xa, depth, n=n) if x >= xb - 0.01]


def fz_of(D):
    return D - 27.0          # the fronts' face: 27 mm inside the oak frame (D = the sides' depth)


def fp_of(D):
    return D - 47.0          # the carcass front plane (fixed panels end here, front rails 16 behind the fronts)


def rail_tube(pid, x0, x1, y, z, letter="штанга"):
    return {"id": pid, "kind": "tube", "mat": "chrome", "box": [x0, y - 12.5, z - 12.5, x1, y + 12.5, z + 12.5],
            "covers": [letter]}


def carcass(W, D, H, n_side=("1", "2"), n_top="3", n_bot="4", n_plinth="9", inset=0.0, top_d=None):
    """Sides 25 on glides, the top 25 over them, plinths 56 front / back and the bottom 16 on them."""
    fp = fp_of(D)
    a, b = inset, W - inset
    return [
        P(n_side[0], [a, GL, 0, a + T, H - T, D]),
        P(n_side[1], [b - T, GL, 0, b, H - T, D]),
        P(n_top, [0, H - T, 0, W, H, top_d or D], grain="x"),
        P(n_plinth, [a + T, GL, fp - 16, b - T, 61, fp], f"{n_plinth}-f"),
        P(n_plinth, [a + T, GL, 3, b - T, 61, 19], f"{n_plinth}-b"),
        P(n_bot, [a + T, 61, 3, b - T, 77, fp]),
    ]


def door_xs(x_in0, x_in1, n, gap=2.0):
    w = (x_in1 - x_in0 - (n + 1) * gap) / n
    return [(x_in0 + gap + i * (w + gap), x_in0 + gap + i * (w + gap) + w) for i in range(n)]


G_UP = (1779, 1444, 1109)
G_LOW = (418,)


def split_door(ns, x0, x1, D, cres=None, lower_top=776.0, pids=None, mirror=False, grooves=True):
    """A bedroom / hall door: upper part (778…2112), lower part (61…lower_top) with the crescent cut in its top edge,
    joined behind by the oak «накладка» that shows through the crescent. Mirror doors carry glued mirrors."""
    fz = fz_of(D)
    pids = pids or (None, None, None)
    up = front(ns[0], x0, 778, x1, 2112, pids[0], fz=fz, grooves=G_UP if grooves and not mirror else
               ((G_UP[0],) if grooves else ()))
    lo = front(ns[1], x0, 61, x1, lower_top, pids[1], fz=fz, top=cres, grooves=G_LOW if grooves else ())
    nak = P(ns[2], [x0 + 15, 715, fz - 19.5 - 16, x1 - 15, 840, fz - 19.5], pids[2])
    parts = [up, lo, nak]
    if mirror:
        tag = pids[0] or ns[0]
        parts.append({"id": f"mir-u-{tag}", "kind": "mirror", "box": [x0 + 2, 781, fz, x1 - 2, 1775, fz + 4]})
        parts.append({"id": f"mir-l-{tag}", "kind": "mirror", "box": [x0 + 2, 421, fz, x1 - 2, lower_top - 3, fz + 4]})
    return parts, [q.get("id") or q["n"] for q in parts]


def bed_glides(W, D):
    return glides((12.5, W / 2, W - 12.5), (25, D - 25))


# ------------------------------------------------------------------------------------------------ 1.08 / 3.01 шкаф 2д
def m1_08(did="monako-1-08", hall=False):
    W, D, H = 970, 605.0, 2140
    fp = fp_of(D)
    p = carcass(W, D, H, n_top="4", n_bot="5", n_plinth="9", inset=2)
    p.append(P("3", [477, 77, 3, 493, H - T, fp]))
    for k, y in enumerate((1872, 411)):
        p.append(P("6", [27, y, 3, 477, y + 16, fp], f"6-{k + 1}"))
        p.append(P("7", [493, y, 3, 943, y + 16, fp], f"7-{k + 1}"))
    if hall:
        p.append(rail_tube("rail-2", 493, 943, 1830, 290))
    else:
        for k, y in enumerate((1509, 1139, 783)):
            p.append(P("8", [494, y, 3, 942, y + 16, fp - 18], f"8-{k + 1}"))
    p.append(rail_tube("rail-1", 27, 477, 1830, 290))
    p += [back("12", 8, 1880, 962, 2133), back("13", 8, 63, 485, 1880, "13-1"), back("13", 485, 63, 962, 1880, "13-2")]
    (a0, a1), (b0, b1) = door_xs(27, 943, 2)
    ca = half_lens(a0 + 151, a1, 40)
    cb = half_lens(b1 - 151, b0, 40)
    da, ida = split_door(("10.1", "10.2", "10.3"), a0, a1, D, ca, pids=(None, None, "10.3-l"))
    db, idb = split_door(("11.1", "11.2", "10.3"), b0, b1, D, cb, pids=(None, None, "10.3-r"))
    p += da + db
    p += glides((14.5, W / 2, W - 14.5), (25, D - 25))
    moves = [door("door_left", ida, "left"), door("door_right", idb, "right")]
    return dump(did, [W, 605, H], p, moves)


# ------------------------------------------------------------------------------------------------ 1.09 / 1.09-01 шкаф 1д
def m1_09(mirrored):
    """Drawn as П6.528.1.09-01 (crescent deepest at the right, free edge; hinges left); 1.09 is its mirror image."""
    W, D, H = 513, 605.0, 2140
    fp = fp_of(D)
    p = carcass(W, D, H, n_top="3", n_bot="4", n_plinth="7", inset=2)
    for k, y in enumerate((1872, 411)):
        p.append(P("5", [27, y, 3, 486, y + 16, fp], f"5-{k + 1}"))
    for k, y in enumerate((1509, 1139, 783)):
        p.append(P("6", [28, y, 3, 485, y + 16, fp - 18], f"6-{k + 1}"))
    p.append(rail_tube("rail", 27, 486, 1830, 290))
    p.append(back("9", 8, 63, 505, 2133))
    (a0, a1), = door_xs(27, 486, 1)
    d, ids = split_door(("8.1", "8.2", "8.3"), a0, a1, D, half_lens(a0 + 151, a1, 40))
    p += d
    p += glides((14.5, W - 14.5), (25, D - 25))
    moves = [door("door", ids, "left")]
    if mirrored:
        p, moves = mirror(p, moves, W)
    return dump("monako-1-09" if mirrored else "monako-1-09-01", [W, 605, H], p, moves)


# ------------------------------------------------------------------------------------------------ 1.01-01 шкаф 4д
def m1_01_01():
    W, D, H = 1885, 605.0, 2140
    fp = fp_of(D)
    p = carcass(W, D, H, n_top="6", n_bot="7", n_plinth="16", inset=2)
    p += [
        P("3", [935, 77, 3, 951, H - T, fp]),
        P("8", [27, 1852, 3, 935, 1868, fp]),
        P("15", [461, 77, 3, 501, 1852, 19]),
        P("9", [951, 1852, 3, 1858, 1868, fp]),
        P("4", [1391.5, 797, 3, 1407.5, 1852, fp]),
        P("10", [951, 781, 3, 1858, 797, fp - 32]),
        P("17", [951, 711, fp - 32, 1858, 781, fp - 16]),
        P("5", [1391.5, 77, 3, 1407.5, 781, fp - 32]),
        P("11", [951, 413, 3, 1391.5, 429, fp - 16]),
        P("12", [1407.5, 413, 3, 1858, 429, fp - 16]),
    ]
    for k, y in enumerate((1483, 1136)):
        p.append(P("13", [952, y, 3, 1390.5, y + 16, fp - 18], f"13-{k + 1}"))
        p.append(P("14", [1408.5, y, 3, 1857, y + 16, fp - 18], f"14-{k + 1}"))
    p.append(rail_tube("rail-911", 27, 935, 1810, 290))
    p.append(rail_tube("rail-446", 1407.5, 1858, 1810, 290))
    p += [back("22", 8, 63, 481, 2133, "22-1"), back("22", 481, 63, 943, 2133, "22-2"),
          back("23", 943, 1860, 1877, 2133), back("24", 943, 63, 1399.5, 1860), back("25", 1399.5, 63, 1877, 1860)]
    xs = door_xs(27, 1858, 4)
    (a0, a1), (b0, b1), (c0, c1), (d0, d1) = xs
    d18, i18 = split_door(("18.1", "18.2", "18.3"), a0, a1, D, half_lens(a0 + 151, a1, 40), pids=(None, None, "18.3-a"))
    d20, i20 = split_door(("20.1", "20.2", "18.3"), b0, b1, D, None, lower_top=735, pids=(None, None, "18.3-b"), mirror=True)
    d21, i21 = split_door(("21.1", "21.2", "18.3"), c0, c1, D, None, lower_top=735, pids=(None, None, "18.3-c"), mirror=True)
    d19, i19 = split_door(("19.1", "19.2", "18.3"), d0, d1, D, half_lens(d1 - 151, d0, 40), pids=(None, None, "18.3-d"))
    p += d18 + d20 + d21 + d19
    p += glides((14.5, 943, W - 14.5), (25, D - 25)) + glides((475,), (D - 60,), "g2")
    moves = [door("door_18", i18, "left"), door("door_20", i20, "right"), door("door_21", i21, "left"),
             door("door_19", i19, "right")]
    return dump("monako-1-01-01", [W, 605, H], p, moves)


# ------------------------------------------------------------------------------------------------ 1.07-01 шкаф 3д (by catalogue)
def m1_07_01():
    W, D, H = 1428, 605.0, 2140
    fp = fp_of(D)
    p = carcass(W, D, H, n_top="top", n_bot="bottom", n_plinth="plinth", inset=2)
    xs = door_xs(27, 1401, 3)
    (a0, a1), (b0, b1), (c0, c1) = xs
    p += [
        P("partition", [934.7, 77, 3, 950.7, H - T, fp]),
        P("hat", [27, 1852, 3, 934.7, 1868, fp]),
        P("shelf", [950.7, 1852, 3, 1401, 1868, fp], "shelf-1"),
        P("shelf", [950.7, 411, 3, 1401, 427, fp], "shelf-2"),
    ]
    for k, y in enumerate((1483, 1136, 781)):
        p.append(P("loose", [951.7, y, 3, 1400, y + 16, fp - 18], f"loose-{k + 1}"))
    p.append(rail_tube("rail", 27, 934.7, 1810, 290))
    p += [back("back", 8, 63, 942.7, 2133, "back-1"), back("back", 942.7, 63, 1420, 2133, "back-2")]
    da, ia = split_door(("d1u", "d1l", "d1n"), a0, a1, D, half_lens(a0 + 151, a1, 40))
    db, ib = split_door(("d2u", "d2l", "d2n"), b0, b1, D, None, lower_top=735, mirror=True)
    dc, ic = split_door(("d3u", "d3l", "d3n"), c0, c1, D, half_lens(c1 - 151, c0, 40))
    p += da + db + dc
    p += glides((14.5, 942.7, W - 14.5), (25, D - 25))
    moves = [door("door_1", ia, "left"), door("door_2", ib, "right"), door("door_3", ic, "right")]
    return dump("monako-1-07-01", [W, 605, H], p, moves)


# ------------------------------------------------------------------------------------------------ 1.15 шкаф-купе (by catalogue)
def m1_15():
    """Шкаф-купе 1885×654×2140: the oak frame, two sliding doors (gloss, V-grooves every ~330) in two tracks inside the
    frame, chrome pull profiles on the doors' outer edges; hanging left, shelves right."""
    W, D, H = 1885, 654.0, 2140
    p = [
        P("side", [0, GL, 0, T, H - T, D], "side-l"),
        P("side", [W - T, GL, 0, W, H - T, D], "side-r"),
        P("top", [0, H - T, 0, W, H, D], grain="x"),
        P("plinth", [T, GL, 560, W - T, 61, 576], "plinth-f"),
        P("plinth", [T, GL, 3, W - T, 61, 19], "plinth-b"),
        P("bottom", [T, 61, 3, W - T, 77, 576]),
        P("partition", [1000, 77, 3, 1016, H - T, 560]),
        P("hat", [T, 1852, 3, 1000, 1868, 560]),
        P("track-top", [T, H - T - 20, 576, W - T, H - T, 640]),
        P("track-bottom", [T, 61, 576, W - T, 71, 640]),
    ]
    for k, y in enumerate((1852, 411)):
        p.append(P("shelf", [1016, y, 3, W - T, y + 16, 560], f"shelf-{k + 1}"))
    for k, y in enumerate((1483, 1136, 781)):
        p.append(P("loose", [1017, y, 3, W - T - 1, y + 16, 545], f"loose-{k + 1}"))
    p.append(rail_tube("rail", T, 1000, 1810, 300))
    p += [back("back", 8, 63, 1008, 2133, "back-1"), back("back", 1008, 63, 1877, 2133, "back-2")]
    dw = (W - 2 * T + 50) / 2
    ya, yb = 72, H - T - 21
    gr = [ya + (yb - ya) * k / 6 for k in range(1, 6)]
    rear = front("door-rear", T, ya, T + dw, yb, t=19.5, fz=604, grooves=gr)
    frnt = front("door-front", W - T - dw, ya, W - T, yb, t=19.5, fz=630, grooves=gr)
    ha = {"id": "pull-rear", "kind": "handle", "model": "bar", "mat": "chrome", "at": [T + 25, 1100], "dir": "up",
          "d": 400, "band": 12, "t": 10, "standoff": 8, "z": 604, "covers": ["профиль"]}
    hb = dict(ha, id="pull-front", at=[W - T - 25, 1100], z=630)
    p += [rear, frnt, ha, hb]
    p += glides((12.5, 1008, W - 12.5), (25, D - 25))
    moves = [{"type": "slide", "name": "coupe_front", "parts": ["door-front", "pull-front"], "by": [-(dw - 60), 0, 0]},
             {"type": "slide", "name": "coupe_rear", "parts": ["door-rear", "pull-rear"], "by": [dw - 60, 0, 0]}]
    return dump("monako-1-15", [W, 654, H], p, moves)


# ------------------------------------------------------------------------------------------------ 1.12 стеллаж
def m1_12():
    W, D, H = 634, 420.0, 2140
    fz = 413.0
    p = [
        P("1", [0, GL, 0, T, H - T, D]),
        P("2", [W - T, GL, 0, W, H - T, D]),
        P("3", [0, H - T, 0, W, H, 421], grain="x"),
        P("6", [T, GL, fz - 16, W - T, 61, fz], "6-f"),
        P("6", [T, GL, 3, W - T, 61, 19], "6-b"),
        P("4", [T, 61, 3, W - T, 77, fz]),
    ]
    ys = (405, 747, 1089, 1431, 1773)
    for k, y in enumerate(ys):
        p.append(P("5", [T, y, 3, W - T, y + 16, fz], f"5-{k + 1}"))
    js = [63] + [y + 8 for y in ys] + [2133]
    for k in range(6):
        n = "7" if k in (0, 5) else "8"
        p.append(back(n, 8, js[k], W - 8, js[k + 1], f"{n}-{k + 1}"))
    p += glides((12.5, W - 12.5), (25, 395))
    return dump("monako-1-12", [W, 421, H], p, [])


# ------------------------------------------------------------------------------------------------ 1.10 комод
def m1_10():
    W, D, H = 1054, 422.0, 1077
    fz, fp = fz_of(D), fp_of(D)
    p = carcass(W, D, H, n_side=("1", "2"), n_top="3", n_bot="4", n_plinth="6", inset=1)
    p += [P("5", [26, 408, fp - 16, 1028, 478, fp], "5-1"), P("5", [26, 696, fp - 16, 1028, 766, fp], "5-2")]
    p += [back("10", 8, 63, 527, 1070, "10-1"), back("10", 527, 63, 1046, 1070, "10-2")]
    c8 = crescent([(229.2, 763.3), (427.3, 745.6), (626.7, 733.4), (826.1, 726.7), (1025.5, 723.9)], 763.3)
    c9 = crescent([(28.5, 436.4), (227.9, 437.7), (427.3, 444.5), (626.7, 456.7), (824.8, 477.1)], 477.1)
    moves = []
    for tag, y0, y1, cres, bh, by in (("7", 766, 1051, None, 150, 800), ("8", 479, 763, c8, 150, 510),
                                      ("9", 61, 477, c9, 250, 90)):
        fn = tag + ".1"
        p.append(front(fn, 28.5, y0, 1025.5, y1, fz=fz, top=cres))
        bx = drawer_box(tag, (tag + ".2", tag + ".3", tag + ".4", tag + ".5"), 39, 1015, by, bh, fz - 19.5, 350)
        p += bx
        moves.append(dmove(f"drawer_{tag}", [fn] + box_ids(bx)))
    p += glides((13.5, W / 2, W - 13.5), (25, D - 25))
    return dump("monako-1-10", [W, 422, H], p, moves)


# ------------------------------------------------------------------------------------------------ 1.06 стол туалетный
def m1_06():
    W, D, H = 1054, 422.0, 770
    fz, fp = fz_of(D), fp_of(D)
    p = [
        P("1", [1, GL, 0, 26, 745, D]),
        P("2", [1028, GL, 0, 1053, 745, D]),
        P("3", [0, 745, 0, W, H, D], grain="x"),
        P("4", [26, 600, 3, 1028, 616, fp]),
        P("5", [26, 425, 3, 1028, 600, 19]),
        front("6.1", 28.5, 616, 1024.5, 743, fz=fz),
    ]
    bx = drawer_box("6", ("6.2", "6.3", "6.4", "6.5"), 39, 1015, 628, 90, fz - 19.5, 350)
    zb = fz - 19.5 - 350
    bx.append(P("6.6", [519, 638, zb + 16, 535, 718, fz - 19.5], "6.6-6"))
    p += bx
    p += glides((13.5, W - 13.5), (25, D - 25))
    return dump("monako-1-06", [W, 422, H], p, [dmove("drawer", ["6.1"] + box_ids(bx))])


# ------------------------------------------------------------------------------------------------ 1.04 / 1.04-01 тумба прикроватная (by catalogue)
def m1_04(mirrored):
    """By the catalogue (the instruction linked to П6.528.1.04 is the bed's): a small Монако carcass 444×421×445, an open
    niche on top, a drawer below with the crescent over the oak rail; 1.04-01 as the p. 42 cut-out, 1.04 its mirror."""
    W, D, H = 444, 420.0, 445
    p = carcass(W, D, H, n_side=("side-l", "side-r"), n_top="top", n_bot="bottom", n_plinth="plinth", top_d=421)
    p += [
        P("rail", [T, 213, FP - 16, W - T, 283, FP]),
        P("shelf", [T, 283, 3, W - T, 299, FP]),
        back("back", 8, 63, W - 8, 443),
        front("drawer-front", 27, 63, 417, 281, top=half_lens(290, 27, 40)),
    ]
    bx = drawer_box("d", ("box-l", "box-r", "box-b", "box-bottom"), 38, 406, 85, 120, FZ - 19.5, 350)
    p += bx
    p += glides((12.5, W - 12.5), (25, 395))
    moves = [dmove("drawer", ["drawer-front"] + box_ids(bx), 280)]
    if mirrored:
        p, moves = mirror(p, moves, W)
    return dump("monako-1-04" if mirrored else "monako-1-04-01", [W, 421, H], p, moves)


# ------------------------------------------------------------------------------------------------ mirrors 1.03 / 3.05 (by catalogue)
def m_mirror(did, W, H, margin=35):
    p = [P("board", [0, 0, 0, W, H, 16]),
         {"id": "mirror", "kind": "mirror", "box": [margin, margin, 17, W - margin, H - margin, 21]}]
    return dump(did, [W, 21, H], p, [])


# ------------------------------------------------------------------------------------------------ 3.02 / 3.03 тумбы прихожей (by catalogue)
def m3_02():
    W, D, H = 970, 420.0, 980
    p = carcass(W, D, H, n_side=("side-l", "side-r"), n_top="top", n_bot="bottom", n_plinth="plinth", top_d=421)
    p += [
        P("rail", [T, 698, FP - 16, W - T, 768, FP]),
        P("shelf-fixed", [T, 768, 3, W - T, 784, FP]),
        P("shelf", [T + 1, 400, 3, W - T - 1, 416, FP - 18]),
        back("back", 8, 63, W - 8, 973),
    ]
    (a0, a1), (b0, b1) = door_xs(T, W - T, 2)
    lens = arc_pts(a0 + 0.16 * (b1 - a0), b1 - 0.16 * (b1 - a0), 40, n=16)
    p += [front("drawer-front", 27, 772, W - 27, 953),
          front("door-l", a0, 63, a1, 768, top=lens, grooves=(418,)),
          front("door-r", b0, 63, b1, 768, top=lens, grooves=(418,))]
    bx = drawer_box("d", ("box-l", "box-r", "box-b", "box-bottom"), 38, W - 38, 800, 130, FZ - 19.5, 350)
    p += bx
    p += glides((12.5, W - 12.5), (25, 395))
    moves = [dmove("drawer", ["drawer-front"] + box_ids(bx)), door("door_left", ["door-l"], "left"),
             door("door_right", ["door-r"], "right")]
    return dump("monako-3-02", [W, 421, H], p, moves)


def m3_03():
    W, D, H = 900, 420.0, 460
    p = carcass(W, D, H, n_side=("side-l", "side-r"), n_top="top", n_bot="bottom", n_plinth="plinth", top_d=421)
    p += [P("rail", [T, 362, FP - 16, W - T, 432, FP]), back("back", 8, 63, W - 8, 453)]
    (a0, a1), (b0, b1) = door_xs(T, W - T, 2)
    lens = arc_pts(a0 + 0.16 * (b1 - a0), b1 - 0.16 * (b1 - a0), 40, n=16)
    p += [front("door-l", a0, 63, a1, 432, top=lens), front("door-r", b0, 63, b1, 432, top=lens),
          P("shelf", [T + 1, 240, 3, W - T - 1, 256, FP - 18])]
    p += glides((12.5, W - 12.5), (25, 395))
    return dump("monako-3-03", [W, 421, H], p, [door("door_left", ["door-l"], "left"), door("door_right", ["door-r"], "right")])


# ------------------------------------------------------------------------------------------------ 3.04 вешалка (by catalogue)
def m3_04():
    W, H = 900, 1650
    p = [P("panel", [0, 0, 0, W, H, 25], grain="y"),
         P("shelf", [0, 1395, 25, W, 1420, 266], grain="x"),
         P("bracket", [80, 1335, 25, 96, 1395, 150], "bracket-l"),
         P("bracket", [804, 1335, 25, 820, 1395, 150], "bracket-r")]
    k = 0
    for xs, y in (((180, 360, 540, 720), 1140), ((360, 540), 800)):
        for x in xs:
            k += 1
            p.append({"id": f"hook-{k}", "kind": "handle", "model": "knob", "mat": "chrome", "at": [x, y], "d": 28,
                      "standoff": 55, "z": 25, "covers": ["крючок"]})
    return dump("monako-3-04", [W, 266, H], p, [])


# ------------------------------------------------------------------------------------------------ 3.08 / 3.09 обувницы (by catalogue)
def m_shoe(did, W, H, bins):
    """Shoe cabinet W×320×H: the oak frame, a drawer on top, tilt-out bins (fronts hinged at the bottom, a two-tier
    shoe rack behind each) with the crescent in their top edges."""
    D = 320.0
    fz, fp = fz_of(D), fp_of(D)
    p = carcass(W, D, H, n_side=("side-l", "side-r"), n_top="top", n_bot="bottom", n_plinth="plinth")
    top_y = H - T - 3
    dy0 = top_y - 135
    p.append(P("shelf-top", [T, dy0 - 18, 3, W - T, dy0 - 2, fp]))
    p.append(back("back", 8, 63, W - 8, H - 7))
    fr = front("drawer-front", 27, dy0, W - 27, top_y, fz=fz)
    bx = drawer_box("d", ("box-l", "box-r", "box-b", "box-bottom"), 38, W - 38, dy0 + 15, 100, fz - 19.5, 230)
    p += [fr] + bx
    moves = [dmove("drawer", ["drawer-front"] + box_ids(bx), 200)]
    y_lo, y_hi = 63, dy0 - 4
    hb = (y_hi - y_lo - 4 * (bins - 1)) / bins
    for i in range(bins):
        b0 = y_lo + i * (hb + 4)
        b1 = b0 + hb
        tag = f"bin{i + 1}"
        lens = arc_pts(27 + 0.22 * (W - 54), W - 27 - 0.28 * (W - 54), 40, n=16)
        f = front(f"{tag}-front", 27, b0, W - 27, b1, fz=fz, top=lens)
        rack = [P(f"{tag}-rack", [T + 3, b0 + 20, fp - 150, W - T - 3, b0 + 36, fp - 20], f"{tag}-rack1"),
                P(f"{tag}-rack", [T + 3, b0 + hb * 0.5, fp - 120, W - T - 3, b0 + hb * 0.5 + 16, fp - 20], f"{tag}-rack2"),
                P(f"{tag}-end", [T + 3, b0 + 20, fp - 20, T + 19, b1 - 30, fp], f"{tag}-end-l"),
                P(f"{tag}-end", [W - T - 19, b0 + 20, fp - 20, W - T - 3, b1 - 30, fp], f"{tag}-end-r")]
        p += [f] + rack
        moves.append({"type": "flap", "name": f"bin_{i + 1}", "parts": [f["n"]] + [q["id"] for q in rack],
                      "hinge": "bottom", "angle": 35})
    p += glides((12.5, W - 12.5), (25, D - 25))
    return dump(did, [W, 320, H], p, moves)


# ------------------------------------------------------------------------------------------------ desks 2.14 / 2.15 / 2.15-01
def desk_drawer(tag, ns, x0, x1, y0, y1, fz, opening, h, cres=None, depth=500):
    fr = front(ns[0], x0, y0, x1, y1, pid=f"{ns[0]}-{tag}", fz=fz, top=cres)
    c = (opening[0] + opening[1]) / 2
    w = opening[1] - opening[0] - 26
    bx = drawer_box(tag, ns[1:], c - w / 2, c + w / 2, y0 + 25, h, fz - 19.5, depth)
    return [fr] + bx, dmove(f"drawer_{tag}", [fr["id"]] + box_ids(bx), 400)


def m2_15(mirrored):
    W, D, H = 1200, 650.0, 770
    fz, fp = fz_of(D), fp_of(D)
    p = [
        P("1", [2, GL, 0, 27, 745, D]),
        P("3", [758, GL, 0, 783, 745, D]),
        P("2", [1173, GL, 0, 1198, 745, D]),
        P("4", [0, 745, 0, W, H, D], grain="x"),
        P("8", [783, GL, fp - 16, 1173, 61, fp], "8-f"),
        P("8", [783, GL, 3, 1173, 61, 19], "8-b"),
        P("5", [783, 61, 3, 1173, 77, fp]),
        P("7", [783, 444, fp - 16, 1173, 514, fp], "7-1"),
        P("7", [783, 217, fp - 16, 1173, 287, fp], "7-2"),
        P("13", [783, 77, 3, 1173, 745, 19]),
        P("6", [27, 598, 3, 758, 614, fp]),
        P("9", [27, 435, 3, 758, 598, 19]),
    ]
    moves = []
    x0, x1 = 784.4, 1170.8
    ped = (783, 1173)
    for tag, ns, y0, y1, cres in (
            ("10", ("10.1", "10.2", "10.3", "10.4", "10.5"), 516.5, 742.5, None),
            ("11a", ("11.1", "11.2", "11.3", "11.4", "11.5"), 288.3, 514.4, half_lens(1019.8, x0, 41.7)),
            ("11b", ("11.1", "11.2", "11.3", "11.4", "11.5"), 61.3, 287.3, half_lens(1019.8, x0, 40.6))):
        q, m = desk_drawer(tag, ns, x0, x1, y0, y1, fz, ped, 120 if cres else 150, cres)
        p += q
        moves.append(m)
    q, m = desk_drawer("12", ("12.1", "12.2", "12.3", "12.4", "12.5"), 29.2, 756.2, 614.4, 742.5, fz, (27, 758), 80)
    p += q
    moves.append(m)
    p += glides((14.5, 770.5, 1185.5), (25, D - 25))
    if mirrored:
        p, moves = mirror(p, moves, W)
    return dump("monako-2-15-01" if mirrored else "monako-2-15", [W, 650, H], p, moves)


def m2_14():
    W, D, H = 1520, 650.0, 770
    fz, fp = fz_of(D), fp_of(D)
    p = [
        P("1", [2.5, GL, 0, 27.5, 745, D]),
        P("3", [417.5, GL, 0, 442.5, 745, D]),
        P("4", [1077.5, GL, 0, 1102.5, 745, D]),
        P("2", [1492.5, GL, 0, 1517.5, 745, D]),
        P("5", [0, 745, 0, W, H, D], grain="x"),
    ]
    for side, (a, b) in (("l", (27.5, 417.5)), ("r", (1102.5, 1492.5))):
        p += [P("11", [a, GL, fp - 16, b, 61, fp], f"11-f{side}"), P("11", [a, GL, 3, b, 61, 19], f"11-b{side}"),
              P("6", [a, 61, 3, b, 77, fp], f"6-{side}"), P("17", [a, 77, 3, b, 745, 19], f"17-{side}")]
    p += [
        P("10", [27.5, 444, fp - 16, 417.5, 514, fp], "10-1"),
        P("10", [27.5, 217, fp - 16, 417.5, 287, fp], "10-2"),
        P("10", [1102.5, 444, fp - 16, 1492.5, 514, fp], "10-3"),
        P("7", [1102.5, 514, 19, 1492.5, 530, fp]),
        P("8", [1103.5, 280, 19, 1491.5, 296, fp - 18]),
        P("9", [442.5, 598, 3, 1077.5, 614, fp]),
        P("12", [442.5, 434, 3, 1077.5, 598, 19]),
    ]
    moves = []
    L, R = (29.8, 415.9), (1105.5, 1491.6)
    specs = [
        ("13l", ("13.1", "13.2", "13.3", "13.4", "13.5"), L, 517.1, 743.3, None, (27.5, 417.5)),
        ("14a", ("14.1", "14.2", "14.3", "14.4", "14.5"), L, 289.5, 514.4, half_lens(180.2, 415.9, 39.3), (27.5, 417.5)),
        ("14b", ("14.1", "14.2", "14.3", "14.4", "14.5"), L, 60.5, 286.8, half_lens(180.2, 415.9, 39.3), (27.5, 417.5)),
        ("13r", ("13.1", "13.2", "13.3", "13.4", "13.5"), R, 517.1, 743.3, None, (1102.5, 1492.5)),
    ]
    for tag, ns, (x0, x1), y0, y1, cres, op in specs:
        q, m = desk_drawer(tag, ns, x0, x1, y0, y1, fz, op, 120 if cres else 150, cres)
        p += q
        moves.append(m)
    q, m = desk_drawer("15", ("15.1", "15.2", "15.3", "15.4", "15.5"), 444.3, 1077.0, 614.6, 743.3, fz, (442.5, 1077.5), 80)
    p += q
    moves.append(m)
    p.append(front("16", 1105.5, 60.5, 1491.6, 514.4, fz=fz, top=half_lens(1341.2, 1105.5, 44.3), grooves=(288,)))
    moves.append(door("door", ["16"], "right"))
    p += glides((15, 430, 1090, 1505), (25, D - 25))
    return dump("monako-2-14", [W, 650, H], p, moves)


# ------------------------------------------------------------------------------------------------ 0.09 стол обеденный
def m0_09():
    """Folded 1500×900×760: two half-tops 1 on a sliding mechanism over the rail frame (2 long, 3 short) and the two
    support elements 9; corner legs of two 25 mm boards (4 + 6, 5 + 7) in an L. Unfolded 2000 with the insert 8 (500)."""
    W, D, H = 1500, 900, 760
    p = [
        P("1", [0, 735, 0, 750, 760, D], "1-l", grain="z", covers=["8"]),
        P("1", [750, 735, 0, 1500, 760, D], "1-r", grain="z"),
    ]
    for tag, x0, sgn in (("l", 4, 1), ("r", 1496, -1)):
        xa, xb = sorted((x0, x0 + sgn * 123.5))
        xi0, xi1 = sorted((x0, x0 + sgn * 25))
        for zt, z0, z1, zi0, zi1 in (("f", 873, 898, 773, 873), ("b", 2, 27, 27, 127)):
            nA, nB = ("4", "6") if tag == "l" else ("5", "7")
            p.append(P(nA, [xa, GL, z0, xb, 735, z1], f"{nA}-{zt}"))
            p.append(P(nB, [xi0, GL, zi0, xi1, 735, zi1], f"{nB}-{zt}"))
    p += [
        P("2", [127.5, 615, 2, 1372.5, 735, 27], "2-b"),
        P("2", [127.5, 615, 873, 1372.5, 735, 898], "2-f"),
        P("3", [4, 615, 127, 29, 735, 773], "3-l"),
        P("3", [1471, 615, 127, 1496, 735, 773], "3-r"),
        P("9", [560, 675, 27, 576, 735, 873], "9-1"),
        P("9", [924, 675, 27, 940, 735, 873], "9-2"),
    ]
    p += glides((65.75, 1434.25), (14.5, 885.5))
    moves = [{"type": "slide", "name": "extend_left", "parts": ["1-l"], "by": [-250, 0, 0]},
             {"type": "slide", "name": "extend_right", "parts": ["1-r"], "by": [250, 0, 0]}]
    return dump("monako-0-09", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------------ 0.04 стол журнальный (by catalogue)
def m0_04():
    W, D, H = 1000, 750, 446
    WH = "gloss#f3f4f4"
    p = [P("top", [0, 421, 0, W, H, D], grain="x")]
    for tag, xe, sx in (("l", 0, 1), ("r", W, -1)):
        for zt, ze, sz in (("b", 0, 1), ("f", D, -1)):
            xa, za = xe + sx * 2, ze + sz * 2          # the legs stand 2 mm inside the top's edges
            x0, x1 = sorted((xa, xa + sx * 120))
            z0, z1 = sorted((za, za + sz * 25))
            p.append(P("leg-a", [x0, GL, z0, x1, 421, z1], f"leg-a-{tag}{zt}"))
            bx0, bx1 = sorted((xa, xa + sx * 25))
            bz0, bz1 = sorted((za + sz * 25, za + sz * 120))
            p.append(P("leg-b", [bx0, GL, bz0, bx1, 421, bz1], f"leg-b-{tag}{zt}"))
            # the white decorative inserts on the two outer faces near the top (2 mm, flush with the top's edge)
            iz0, iz1 = sorted((ze, za))
            p.append({"id": f"ins-a-{tag}{zt}", "kind": "panel", "mat": WH, "edge": 0.5,
                      "box": [x0 + 20, 372, iz0, x1 - 20, 386, iz1]})
            ix0, ix1 = sorted((xe, xa))
            p.append({"id": f"ins-b-{tag}{zt}", "kind": "panel", "mat": WH, "edge": 0.5,
                      "box": [ix0, 372, min(bz0, bz1) + 5, ix1, 386, max(bz0, bz1) - 5]})
    p += [
        P("apron", [122, 321, 11, 878, 421, 27], "apron-b"),
        P("apron", [122, 321, D - 27, 878, 421, D - 11], "apron-f"),
        P("apron", [11, 321, 122, 27, 421, 628], "apron-l"),
        P("apron", [W - 27, 321, 122, W - 11, 421, 628], "apron-r"),
        P("cleat", [27, 84, 122, 43, 110, 628], "cleat-l"),
        P("cleat", [W - 43, 84, 122, W - 27, 110, 628], "cleat-r"),
        P("shelf", [43, 110, 122, W - 43, 126, 628], grain="x"),
    ]
    p += glides((60, W - 60), (12.5, D - 12.5))
    return dump("monako-0-04", [W, D, H], p, [])


# ------------------------------------------------------------------------------------------------ beds
def m_bed(did, W, instructed=False):
    """Bed (instruction П6.528.1.05 for 2-16; the other widths by the same construction): headboard 1 (W × 935 × 25) and
    footboard 2 (W × 335 × 25) on glides, side rails 3 (2011 × 200 × 25) between them, two gloss overlays on the
    headboard — 4 (150) above, 5 (310) below with the crescent across its top — and the metal frame with slats."""
    L = 2060
    p = [
        P("1", [0, GL, 0, W, 940, 25], grain="x"),
        P("2", [0, GL, L - 25, W, 340, L], grain="x"),
        P("3", [0, 120, 25, 25, 320, L - 25], "3-l"),
        P("3", [W - 25, 120, 25, W, 320, L - 25], "3-r"),
    ]
    o0, o1 = 50.0, W - 50.0
    wide = W >= 1300
    grooves = []
    if wide:
        t = (o1 - o0) / 3
        g1, g2 = o0 + t, o0 + 2 * t
        cres = half_lens(g1 - 336, g1, 39.3) + [(g2, 39.3)] + half_lens(g2 + 336, g2, 39.3)
        grooves = [g1, g2]
    else:
        cres = arc_pts(o0 + 150, o1 - 150, 39.3, n=16)
    face = lambda: dict(GROOVE, w=5, lines=[[round(g, 1), 0, round(g, 1), 2000] for g in grooves]) if grooves else None
    up = P("4", [o0, 740, 25, o1, 890, 44], kind="front")
    lo = P("5", [o0, 425, 25, o1, 735, 44], kind="front", shape="path",
           outline=notched_outline(o0, 425, o1, 735, cres))
    if grooves:
        up["face"] = dict(GROOVE, w=5, lines=[[round(g, 1), 740, round(g, 1), 890] for g in grooves])
        lo["face"] = dict(GROOVE, w=5, lines=[[round(g, 1), 425, round(g, 1), 735] for g in grooves])
    p += [up, lo]
    # the metal frame «металлокаркас» (not in the cut list): black tubes, beech slats, legs
    B = "black"
    fx0, fx1 = 54.0, W - 54.0
    fr = lambda i, box: {"id": f"frame-{i}", "kind": "panel", "mat": B, "edge": 1, "box": box, "covers": ["каркас"]}
    p += [fr("l", [fx0, 320, 30, fx0 + 40, 400, 2030]), fr("r", [fx1 - 40, 320, 30, fx1, 400, 2030]),
          fr("h", [fx0 + 40, 360, 30, fx1 - 40, 400, 70]), fr("f", [fx0 + 40, 360, 1990, fx1 - 40, 400, 2030])]
    mid = W >= 1300
    if mid:
        p.append(fr("m", [W / 2 - 20, 360, 70, W / 2 + 20, 400, 1990]))
    legs_x = [fx0 + 20, fx1 - 20] + ([W / 2] if mid else [])
    k = 0
    for z in (150, 1050, 1950):
        for x in legs_x:
            k += 1
            p.append({"id": f"leg-{k}", "kind": "tube", "mat": B, "box": [x - 20, 0, z - 20, x + 20, 320, z + 20],
                      "covers": ["каркас"]})
    spans = [(fx0 + 40, W / 2 - 20), (W / 2 + 20, fx1 - 40)] if mid else [(fx0 + 40, fx1 - 40)]
    n = 0
    for i in range(22):
        z = 95 + i * 88
        for a, b in spans:
            n += 1
            p.append({"id": f"slat-{n}", "kind": "panel", "mat": "door_enamel_whitey#c9a77c", "edge": 1,
                      "box": [a + 5, 400, z, b - 5, 408, z + 53], "covers": ["каркас"]})
    p.append({"id": "mattress", "kind": "mattress", "box": [fx0 + 1, 408, 45, fx1 - 1, 608, 2030]})
    p += glides((20, W / 2, W - 20), (12.5,)) + glides((20, W / 2, W - 20), (L - 12.5,), "g2")
    return dump(did, [W, L, 940], p, [])


# =================================================================================================== catalogue
FIN = [
    {"id": "monako-white-oak", "name": "6G Белый глянец / Дуб Саттер 369 SWA", "body": "door_enamel_whitey#7f4e31",
     "front": "door_enamel_whitey#f9fbfc@gloss", "swatch": "#f9fbfc"},
    {"id": "monako-mokko-oak", "name": "Серый Мокко / Дуб Саттер 369 SWA", "body": "door_enamel_whitey#7f4e31",
     "front": "door_enamel_whitey#61594e", "swatch": "#61594e"},
]

MODELS = []


def model(mid, code, name, cat, size, page, is_=None, note=None, **kw):
    m = {"id": mid, "code": code, "name": name, "collection": "monako", "category": cat, "size": size}
    if is_:
        m["is"] = is_
    m["page"] = page
    if note:
        m["note"] = note
    m.update(kw)
    MODELS.append(m)


def write_catalog():
    cat = {
        "finishes": FIN,
        "profiles": {},
        "collections": [{"id": "monako", "name": "Монако", "brand": "Пинскдрев",
                         "finishes": [f["id"] for f in FIN], "metal": "chrome",
                         "note": NOTE}],
        "models": MODELS,
    }
    path = os.path.join(HERE, "monako_catalog.json")
    with open(path, "w") as fh:
        json.dump(cat, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


NOTE = ("Каталог «Корпусная мебель ч. II» 2025, с. 34–42 (разворот 64–81). Рама из ЛДСП 25 «Дуб Саттер 369 SWA»: "
        "боковины на опорах ФБ 482, крышка 25 сверху; фасады МДФ 19,5 «6G Белый глянец» / «Серый Мокко» утоплены в раму на "
        "27 мм, с V-фрезеровками через ~300 мм; ручка — полумесяц, вырезанный в верхней кромке фасада, в котором видна "
        "дубовая царга (гостиная) или дубовая накладка-ручка двери (спальня, прихожая); задние стенки ХДФ 3.")

BUILD = []


def build(fn, *a, **kw):
    BUILD.append((fn, a, kw))


model("monako-0-01", "П6.528.0.01", "Шкаф «Монако»", "living", [634, 421, 1900], 39, "P6-528-0-01-SHkaf.pdf",
      "витрина: стекло в вырезе двери слева, дверь на правых петлях")
build(m0_01)
model("monako-0-01-01", "П6.528.0.01-01", "Шкаф «Монако»", "living", [634, 421, 1900], 34, "P6-528-0-01-01-SHkaf.pdf",
      "зеркальное исполнение П6.528.0.01: витрина справа, дверь на левых петлях")
build(m0_01, True)
model("monako-0-02", "П6.528.0.02", "Тумба ТВ «Монако»", "living", [1704, 421, 590], 41, "P6-528-0-02-Tumba.pdf")
build(m0_02)
model("monako-0-03", "П6.528.0.03", "Тумба «Монако»", "living", [1424, 421, 840], 41, "P6-528-0-03-Tumba.pdf",
      "средний нижний ящик — push-to-open")
build(m0_03)
model("monako-0-05", "П6.528.0.05", "Шкаф «Монако»", "living", [934, 421, 1900], 41, "P6-528-0-05-SHkaf.pdf",
      "витрина справа (в каталоге с. 41 — зеркальное П6.528.0.05-01)")
build(m0_05)
model("monako-0-06", "П6.528.0.06", "Тумба ТВ «Монако»", "living", [1424, 421, 490], 41, "P6-528-0-06-Tumba-TV.pdf")
build(m0_06)
model("monako-0-07", "П6.528.0.07", "Полка «Монако»", "living", [1704, 240, 340], 41,
      note="по каталогу, без инструкции: как П6.528.0.08, длина 1704", mount="wall")
build(shelf, "monako-0-07", 1704)
model("monako-0-08", "П6.528.0.08", "Полка «Монако»", "living", [1420, 240, 340], 41, "P6-528-0-08-Polka-1.pdf",
      mount="wall")
build(shelf, "monako-0-08", 1420)


model("monako-0-04", "П6.528.0.04", "Стол журнальный «Монако»", "tables", [1000, 750, 446], 41,
      note="по каталогу, без инструкции; декоративные вставки на ножках только белые")
build(m0_04)
model("monako-0-09", "П6.528.0.09", "Стол «Монако»", "tables", [1500, 900, 760], 41, "P6-528-0-09-ispr.pdf",
      "раздвижной: L1500, в положении «разложено» L2000 со вставкой 500 (вставка показана covers на левой полукрышке)")
build(m0_09)
model("monako-1-01-01", "П6.528.1.01-01", "Шкаф для одежды 4д «Монако»", "bedroom", [1885, 605, 2140], 42, "P6-528-1-01-01.pdf",
      "две средние двери с зеркалами")
build(m1_01_01)
model("monako-1-03", "П6.528.1.03", "Зеркало «Монако»", "decor", [1000, 21, 700], 42, note="по каталогу, без инструкции",
      mount="wall")
build(m_mirror, "monako-1-03", 1000, 700)
model("monako-1-04", "П6.528.1.04", "Тумба прикроватная «Монако»", "bedroom", [444, 421, 445], 42,
      note="по каталогу (инструкция на сайте — от кровати П6.528.1.05); зеркальное исполнение П6.528.1.04-01")
build(m1_04, True)
model("monako-1-04-01", "П6.528.1.04-01", "Тумба прикроватная «Монако»", "bedroom", [444, 421, 445], 42,
      note="по каталогу, без инструкции (как на вырезке с. 42)")
build(m1_04, False)
model("monako-1-05", "П6.528.1.05", "Кровать 2-16 «Монако»", "bedroom", [1710, 2060, 940], 42, "P6-528-1-05.pdf",
      "спальное место 2000×1600, металлокаркас; каталог L2060×B1710 (L — длина)")
build(m_bed, "monako-1-05", 1710, True)
model("monako-1-06", "П6.528.1.06", "Стол туалетный «Монако»", "bedroom", [1054, 422, 770], 42, "P6-528-1-06.pdf")
build(m1_06)
model("monako-1-07-01", "П6.528.1.07-01", "Шкаф для одежды 3д «Монако»", "bedroom", [1428, 605, 2140], 42,
      note="по каталогу, без инструкции; средняя дверь с зеркалом")
build(m1_07_01)
model("monako-1-08", "П6.528.1.08", "Шкаф для одежды 2д «Монако»", "bedroom", [970, 605, 2140], 42, "P6-528-1-08.pdf")
build(m1_08)
model("monako-1-09", "П6.528.1.09", "Шкаф для одежды «Монако»", "bedroom", [513, 605, 2140], 42, "P6-528-1-09-09-01.pdf",
      "дверь на правых петлях (зеркально П6.528.1.09-01, как на вырезке с. 42)")
build(m1_09, True)
model("monako-1-09-01", "П6.528.1.09-01", "Шкаф для одежды «Монако»", "bedroom", [513, 605, 2140], 42,
      "P6-528-1-09-09-01-1.pdf", "дверь на левых петлях (как на чертеже инструкции)")
build(m1_09, False)
model("monako-1-10", "П6.528.1.10", "Комод «Монако»", "bedroom", [1054, 422, 1077], 42, "P6-528-1-10.pdf")
build(m1_10)
model("monako-1-11", "П6.528.1.11", "Кровать 1-09 «Монако»", "bedroom", [1010, 2060, 940], 42,
      note="по каталогу и инструкции кровати 2-16; спальное место 2000×900, металлокаркас")
build(m_bed, "monako-1-11", 1010)
model("monako-1-12", "П6.528.1.12", "Стеллаж «Монако»", "bedroom", [634, 421, 2140], 42, "P6-528-1-12.pdf")
build(m1_12)
model("monako-1-15", "П6.528.1.15", "Шкаф-купе 2д «Монако»", "bedroom", [1885, 654, 2140], 42,
      note="по каталогу, без инструкции")
build(m1_15)
model("monako-1-22", "П6.528.1.22", "Кровать 2-18 «Монако»", "bedroom", [1910, 2060, 940], 42,
      note="по каталогу и инструкции кровати 2-16; спальное место 2000×1800, металлокаркас")
build(m_bed, "monako-1-22", 1910)
model("monako-1-23", "П6.528.1.23", "Кровать 2-14 «Монако»", "bedroom", [1510, 2060, 940], 42,
      note="по каталогу и инструкции кровати 2-16; спальное место 2000×1400, металлокаркас")
build(m_bed, "monako-1-23", 1510)
model("monako-1-24", "П6.528.1.24", "Кровать 1-12 «Монако»", "bedroom", [1310, 2060, 940], 42,
      note="по каталогу и инструкции кровати 2-16; спальное место 2000×1200, металлокаркас")
build(m_bed, "monako-1-24", 1310)
model("monako-2-14", "П6.528.2.14", "Стол письменный 2т «Монако»", "office", [1520, 650, 770], 41, "P5-528-2-14-1.pdf")
build(m2_14)
model("monako-2-15", "П6.528.2.15", "Стол письменный «Монако»", "office", [1200, 650, 770], 41, "P6-528-2-15.pdf",
      "тумба справа")
build(m2_15, False)
model("monako-2-15-01", "П6.528.2.15-01", "Стол письменный «Монако»", "office", [1200, 650, 770], 41, "P6-528-2-15-01.pdf",
      "тумба слева")
build(m2_15, True)
model("monako-3-01", "П6.528.3.01", "Шкаф для одежды 2д «Монако»", "hall", [970, 605, 2140], 42,
      note="по каталогу (инструкция на сайте — от шкафа П6.528.0.01) и конструкции П6.528.1.08; внутри две штанги")
build(m1_08, "monako-3-01", True)
model("monako-3-02", "П6.528.3.02", "Тумба «Монако»", "hall", [970, 421, 980], 42,
      note="по каталогу (инструкция на сайте — от тумбы П6.528.0.02)")
build(m3_02)
model("monako-3-03", "П6.528.3.03", "Тумба «Монако»", "hall", [900, 421, 460], 42,
      note="по каталогу (инструкция на сайте — от тумбы П6.528.0.03)")
build(m3_03)
model("monako-3-04", "П6.528.3.04", "Вешалка «Монако»", "hall", [900, 266, 1650], 42, note="по каталогу, без инструкции",
      mount="wall")
build(m3_04)
model("monako-3-05", "П6.528.3.05", "Зеркало «Монако»", "decor", [670, 21, 970], 42, note="по каталогу, без инструкции",
      mount="wall")
build(m_mirror, "monako-3-05", 670, 970)
model("monako-3-08", "П6.528.3.08", "Тумба для обуви «Монако»", "hall", [750, 320, 1100], 42,
      note="по каталогу, без инструкции; ящик и две откидные секции; крепление к стене")
build(m_shoe, "monako-3-08", 750, 1100, 2)
model("monako-3-09", "П6.528.3.09", "Тумба для обуви «Монако»", "hall", [600, 320, 1503], 42,
      note="по каталогу, без инструкции; ящик и три откидные секции; крепление к стене")
build(m_shoe, "monako-3-09", 600, 1503, 3)


if __name__ == "__main__":
    for fn, a, kw in BUILD:
        print(fn(*a, **kw))
    print(write_catalog())
