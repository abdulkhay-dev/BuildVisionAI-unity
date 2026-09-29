"""«Лайн» (П6.619, Пинскдрев, Фабрика столов): two carcasses in one — an outer shell in «Дуб Вотан» (sides, top, bottom) screwed
round an inner carcass in black ЛДСП (sides, top, bottom, partitions, shelves), a black plinth on ФБ 482 glides (or black
metal frame legs / wheels), fronts «Камень серый» set inside the shell 10 mm in from the inner carcass' outer faces (so a
10-mm black border shows round every front), milled diagonal lines on the fronts, black bar handles СПА-1 (96 mm), ДВП
backs nailed on the inner carcass.

Every instruction of the collection has a table without sizes and a front view without inner dimensions: the positions
here were measured on the instruction's vector drawings (PyMuPDF line coordinates, scale = catalogue size / drawn size,
±1 mm) — see notes/layn.md.

    python3 tools/casegoods/gen/layn.py
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))

GL = 4.0            # ФБ 482 glides
PL = 100.0          # plinth height
T = 16.0            # ЛДСП
REV = 10.0          # black border round the fronts
GROOVE = {"type": "grooves", "w": 3, "depth": 1.5, "flute": "v"}
MODELS = []


# ------------------------------------------------------------------------------------------------ helpers
def P(n, box, pid=None, **kw):
    p = {"n": n} if n is not None else {}
    if pid:
        p["id"] = pid
    p.update(kw)
    p["box"] = [round(v, 1) for v in box]
    return p


class Case:
    """The shell / inner-carcass stack of one module. y0 = the underside of the outer bottom (top of plinth or legs)."""

    def __init__(self, W, H, B, y0=GL + PL):
        self.W, self.H, self.B, self.y0 = W, H, B, y0
        self.ob = (y0, y0 + T)                       # outer bottom
        self.ib = (y0 + T, y0 + 2 * T)               # inner bottom
        self.it = (H - 2 * T, H - T)                 # inner top
        self.ot = (H - T, H)                         # outer top
        self.xi = (17.0, W - 17.0)                   # inner carcass outer faces
        self.zi = (3.0, B - 23.0)                    # inner carcass depth (ДВП 3 behind it; door 16 + glass 4 in front)
        self.zf = (B - 18.0, B - 2.0)                # fronts
        self.fx = (self.xi[0] + REV, self.xi[1] - REV)
        self.fy = (self.ib[0] + REV, self.it[1] - REV)

    def shell(self, n_l, n_r, n_top, n_bot, ids=(None, None, None, None), mat="body"):
        W, H, B = self.W, self.H, self.B
        return [
            P(n_l, [1, self.ob[1], 0, 17, self.ot[0], B - 1], ids[0], mat=mat),
            P(n_r, [W - 17, self.ob[1], 0, W - 1, self.ot[0], B - 1], ids[1], mat=mat),
            P(n_top, [0, self.ot[0], 0, W, H, B], ids[2], mat=mat, grain="x"),
            P(n_bot, [0, self.ob[0], 0, W, self.ob[1], B], ids[3], mat=mat, grain="x"),
        ]

    def inner(self, n_l, n_r, n_top, n_bot, ids=(None, None, None, None)):
        (x0, x1), (z0, z1) = self.xi, self.zi
        return [
            P(n_l, [x0, self.ib[1], z0, x0 + T, self.it[0], z1], ids[0], mat="inner"),
            P(n_r, [x1 - T, self.ib[1], z0, x1, self.it[0], z1], ids[1], mat="inner"),
            P(n_top, [x0, self.it[0], z0, x1, self.it[1], z1], ids[2], mat="inner"),
            P(n_bot, [x0, self.ib[0], z0, x1, self.ib[1], z1], ids[3], mat="inner"),
        ]

    def hor(self, n, x0, x1, y, pid=None, loose=False, glass=False):
        """A horizontal inside the inner carcass with its top face at y: fixed (full depth) or a loose shelf."""
        z0, z1 = self.zi
        if glass:
            return P(n, [x0 + 2, y - 6, z0 + 17, x1 - 2, y, z1 - 20], pid, kind="glass")
        if loose:
            return P(n, [x0 + 1, y - T, z0 + 2, x1 - 1, y, z1 - 10], pid, mat="inner")
        return P(n, [x0, y - T, z0, x1, y, z1], pid, mat="inner")

    def ver(self, n, x, y0, y1, pid=None):
        """A partition, x = its left face."""
        return P(n, [x, y0, self.zi[0], x + T, y1, self.zi[1]], pid, mat="inner")

    def back(self, n, x0, y0, x1, y1, pid=None):
        return P(n, [x0, y0, 0, x1, y1, 3], pid, kind="back", mat="back")

    def plinth(self, n_front, n_side):
        W, B = self.W, self.B
        x0, x1 = self.xi
        zb, zf = 20.0, B - 20.0
        GL = self.y0 - PL
        return [
            P(n_front, [x0, GL, zf - T, x1, GL + PL, zf], f"{n_front}-front", mat="inner", grain="x"),
            P(n_front, [x0, GL, zb, x1, GL + PL, zb + T], f"{n_front}-back", mat="inner", grain="x"),
            P(n_side, [x0, GL, zb + T, x0 + T, GL + PL, zf - T], f"{n_side}-l", mat="inner"),
            P(n_side, [x1 - T, GL, zb + T, x1, GL + PL, zf - T], f"{n_side}-r", mat="inner"),
        ] + self.glides()

    def glides(self):
        W, B = self.W, self.B
        x0, x1 = self.xi
        zb, zf = 20.0, B - 20.0
        pts = []
        xs = [x0 + 75, x1 - 75] + ([W / 2] if W > 1000 else [])
        for x in xs:
            pts += [(x, zf - T / 2), (x, zb + T / 2)]
        for z in (zb + T + (zf - zb - 2 * T) * 0.25, zb + T + (zf - zb - 2 * T) * 0.75):
            pts += [(x0 + T / 2, z), (x1 - T / 2, z)]
        gl = self.y0 - PL
        return [{"id": f"g-{k + 1}", "kind": "tube", "mat": "black", "box": [round(x - 7, 1), 0, round(z - 7, 1), round(x + 7, 1), gl, round(z + 7, 1)]}
                for k, (x, z) in enumerate(pts)]

    def front(self, n, x0, y0, x1, y1, lines=(), pid=None, outline=None, grain="y"):
        z0, z1 = self.zf
        p = P(n, [x0, y0, z0, x1, y1, z1], pid, kind="front", grain=grain)
        if outline:
            p["shape"] = "path"
            p["outline"] = outline
        if lines:
            p["face"] = dict(GROOVE, lines=[[round(v, 1) for v in ln] for ln in clip_lines(lines, x0, y0, x1, y1)])
        return p

    def glass(self, n, x0, y0, x1, y1, pid=None):
        z1 = self.zf[0]
        return P(n, [x0, y0, z1 - 4, x1, y1, z1], pid, kind="glass")

    def handle(self, pid, x, y, dir="up", z=None, d=124.0):
        """Ручка СПА-1 (96 mm c-c): a slim black bar."""
        return {"id": pid, "kind": "handle", "model": "bar", "mat": "metal", "at": [round(x, 1), round(y, 1)], "dir": dir, "d": d,
                "band": 9, "t": 8, "standoff": 10, "z": self.zf[1] if z is None else z}

    def light(self, pid, x, z):
        y = self.it[0]
        return {"id": pid, "kind": "light", "shape": "circle", "box": [round(x - 35, 1), y - 6, round(z - 35, 1), round(x + 35, 1), y, round(z + 35, 1)]}


def drawer_box(tag, ns, x0, x1, y0, h, zf, depth=350.0):
    """Box between x0..x1 (outer) behind the front (zf = the front's back face): sides full depth, the back standing on the
    ДВП bottom, the bottom in grooves of the front and the sides (nailed under the back). ns = (side, side, back, bottom);
    ids are <n>-<tag>."""
    zb = zf - depth
    return [
        P(ns[0], [x0, y0, zb, x0 + T, y0 + h, zf], f"{ns[0]}-{tag}", mat="inner"),
        P(ns[1], [x1 - T, y0, zb, x1, y0 + h, zf], f"{ns[1]}-{tag}", mat="inner"),
        P(ns[2], [x0 + T, y0 + 14, zb, x1 - T, y0 + h, zb + T], f"{ns[2]}-{tag}", mat="inner"),
        P(ns[3], [x0 + 10, y0 + 10, zb, x1 - 10, y0 + 13, zf + 6], f"{ns[3]}-{tag}", kind="back", mat="back"),
    ]


def drawer_move(name, front_id, box, handle_id=None, travel=300):
    return {"type": "drawer", "name": name, "parts": [front_id] + [q["id"] for q in box] + ([handle_id] if handle_id else []),
            "travel": travel}


def tube(pid, box, covers=None):
    """Square black steel tube of a metal base (20×20)."""
    p = {"id": pid, "kind": "panel", "mat": "metal", "edge": 1, "box": [round(v, 1) for v in box]}
    if covers:
        p["covers"] = covers
    return p


def sled_base(xs, B, h=200.0, t=20.0, z0=19.5, z1=None, letter="22", rails=True):
    """«Металлическое опорное основание»: at each x (the frame's left face) a closed rectangular frame of 20×20 tube
    (two posts, a floor tube, a top tube) in the side plane, the frames joined by top rails along the front and back."""
    z1 = B - z0 if z1 is None else z1
    out = []
    for i, x in enumerate(xs):
        out += [
            tube(f"base-{i + 1}-pf", [x, 0, z1 - t, x + t, h, z1], [letter] if i == 0 else None),
            tube(f"base-{i + 1}-pb", [x, 0, z0, x + t, h, z0 + t]),
            tube(f"base-{i + 1}-floor", [x, 0, z0 + t, x + t, t, z1 - t]),
            tube(f"base-{i + 1}-top", [x, h - t, z0 + t, x + t, h, z1 - t]),
        ]
    if rails:
        for i in range(len(xs) - 1):
            a, b = xs[i] + t, xs[i + 1]
            out += [tube(f"base-rail-f{i + 1}", [a, h - t, z1 - t, b, h, z1]), tube(f"base-rail-b{i + 1}", [a, h - t, z0, b, h, z0 + t])]
    return out


def clip_lines(lines, x0, y0, x1, y1):
    """Groove lines clipped to the front (a line may run over two fronts); end points within 3 mm of an edge snap onto it."""
    out = []
    for a0, b0, a1, b1 in lines:
        t0, t1 = 0.0, 1.0
        da, db = a1 - a0, b1 - b0
        ok = True
        for pp, q in ((-da, a0 - x0), (da, x1 - a0), (-db, b0 - y0), (db, y1 - b0)):
            if abs(pp) < 1e-9:
                if q < 0:
                    ok = False
            else:
                t = q / pp
                if pp < 0:
                    t0 = max(t0, t)
                else:
                    t1 = min(t1, t)
        if not ok or t1 - t0 < 1e-6:
            continue
        pts = []
        for t in (t0, t1):
            a, b = a0 + t * da, b0 + t * db
            a = x0 if abs(a - x0) < 3 else x1 if abs(a - x1) < 3 else a
            b = y0 if abs(b - y0) < 3 else y1 if abs(b - y1) < 3 else b
            pts += [a, b]
        if abs(pts[0] - pts[2]) + abs(pts[1] - pts[3]) > 10:
            out.append(pts)
    return out


def mirror_lines(lines, W):
    return [[W - a0, b0, W - a1, b1] for a0, b0, a1, b1 in lines]


def door_move(name, parts, hinge):
    return {"type": "door", "name": name, "parts": parts, "hinge": hinge, "angle": 105}


def model(did, code, name, category, size, is_=None, note=None, **kw):
    m = {"id": did, "code": code, "name": name, "collection": "layn", "category": category, "size": size}
    if is_:
        m["is"] = is_
    m["page"] = 69
    if note:
        m["note"] = note
    m.update(kw)
    MODELS.append(m)


def cutlist(did, code, source, rows):
    path = os.path.join(HERE, "cutlists", did + ".json")
    data = {"code": code, "source": source,
            "rows": [dict({"n": n, "name": name, "size": None, "count": c}, **({"code": k} if k else {})) for n, k, name, c in rows]}
    with open(path, "w") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


# ------------------------------------------------------------------------------------------------ 0.01 / 0.01-01 шкаф с витриной
def m001(did, code, right):
    """Tall vitrine 566×390×2084. One door: a 150 stile on the hinge side and a solid lower panel (to 610.5), the rest of
    the door's field is the glass «накладка» 14 screwed on its back; the handle is on the glass. П6.619.0.01 = «правый»
    (hinges on the right, as drawn); 0.01-01 = «левый» (mirror image)."""
    W, H, B = 566, 2084, 390
    c = Case(W, H, B, y0=104.5)
    p = c.shell("4", "5", "6", "7") + c.inner("1", "2", "3", "3", ids=(None, None, "3-top", "3-bottom"))
    x0, x1 = 33.0, W - 33.0
    p += [
        c.hor("8", x0, x1, 610.5),
        c.hor("10", x0, x1, 373, loose=True),
        c.hor("9", x0, x1, 948.2, "9-1", glass=True),
        c.hor("9", x0, x1, 1317.7, "9-2", glass=True),
        c.hor("9", x0, x1, 1687.3, "9-3", glass=True),
        c.back("16", 17, c.ob[1], W - 17, 602.5),
        c.back("15", 17, 602.5, W - 17, c.ot[0]),
        c.light("led", W / 2, 200),
    ]
    p += c.plinth("11", "12")
    fx0, fx1 = c.fx
    fy0, fy1 = c.fy
    gy = 610.5
    lines = [[148.4, 610.5, 420.0, 129.5], [26.2, 245.9, 247.2, 432.9], [247.2, 432.9, 539.0, 510.2]]   # as drawn (0.01, «правый»)
    st = 150.0
    if right:        # hinges right: the stile on the right
        sx = fx1 - st
        outline = f"M {fx0} {fy0} L {fx1} {fy0} L {fx1} {fy1} L {sx} {fy1} L {sx} {gy} L {fx0} {gy} Z"
        glass = c.glass("14", fx0, gy - 20, sx + 20, fy1)
        hx, hinge = 84.7, "right"
    else:
        sx = fx0 + st
        outline = f"M {fx0} {fy0} L {fx1} {fy0} L {fx1} {gy} L {sx} {gy} L {sx} {fy1} L {fx0} {fy1} Z"
        glass = c.glass("14", sx - 20, gy - 20, fx1, fy1)
        lines = mirror_lines(lines, W)
        hx, hinge = W - 84.7, "left"
    p.append(c.front("13", fx0, fy0, fx1, fy1, lines, outline=outline))
    p.append(glass)
    p.append(c.handle("k", hx, 1130, z=c.zf[0]))
    moves = [door_move("door", ["13", "14", "k"], hinge)]
    note = "по инструкции; «правый» — петли справа (как на чертеже)" if right else "по инструкции; «левый» — зеркальный вариант 0.01"
    model(did, code, "Шкаф «Лайн»", "living", [W, B, H], "P6-619-0-01-P6-619-0-01-01.pdf", note + "; с подсветкой")
    cutlist(did, code, "table of IS P6-619-0-01 (two marking columns 0.01 / 0.01-01, read from the page: the PDF parser lost it); "
            "no sizes in the table — positions measured on the front view",
            [("1", None, "Стенка вертикальная", 1), ("2", None, "Стенка вертикальная", 1), ("3", None, "Стенка горизонтальная", 2),
             ("4", None, "Стенка вертикальная", 1), ("5", None, "Стенка вертикальная", 1), ("6", None, "Стенка горизонтальная", 1),
             ("7", None, "Стенка горизонтальная", 1), ("8", None, "Стенка горизонтальная", 1), ("9", None, "Полка (стекло)", 3),
             ("10", None, "Полка", 1), ("11", None, "Стенка передняя", 2), ("12", None, "Стенка боковая", 2),
             ("13", None, "Дверь", 1), ("14", None, "Накладка (стекло)", 1), ("15", None, "Стенка задняя", 1),
             ("16", None, "Стенка задняя", 1)])
    return dump(did, [W, B, H], p, moves)


# ------------------------------------------------------------------------------------------------ 0.04 шкаф (тумба)
def m004():
    """854×390×1480: a door on the left section (shelves behind it), an open right section with three fixed shelves."""
    W, H, B = 854, 1480, 390
    c = Case(W, H, B, y0=103.5)
    p = c.shell("6", "6", "7", "8", ids=("6-l", "6-r", None, None)) + c.inner("1", "2", "4", "5")
    xp = 525.0                                  # partition 3 (the door covers 14 of its 16 mm)
    p += [
        c.ver("3", xp, c.ib[1], c.it[0]),
        c.hor("9", xp + T, W - 33, 467.6, "9-1"),
        c.hor("10", xp + T, W - 33, 799.7),
        c.hor("9", xp + T, W - 33, 1131.9, "9-2"),
        c.hor("11", 33, xp, 799.7),
        c.hor("12", 33, xp, 467.6, "12-1", loose=True),
        c.hor("12", 33, xp, 1131.9, "12-2", loose=True),
        c.back("16", 17, c.ob[1], xp + 8, 791.7, "16-1"),
        c.back("16", 17, 791.7, xp + 8, c.ot[0], "16-2"),
        c.back("17", xp + 8, c.ob[1], W - 17, 791.7, "17-1"),
        c.back("17", xp + 8, 791.7, W - 17, c.ot[0], "17-2"),
    ]
    p += c.plinth("13", "14")
    lines = [[27.3, 230.0, 361.5, 418.0], [361.5, 418.0, 538.9, 405.3], [437.6, 129.8, 176.9, 1109.4],
             [27.3, 1130.5, 538.9, 1059.0], [177.5, 1109.4, 340.0, 1453.7]]
    p.append(c.front("15", c.fx[0], c.fy[0], xp + 14, c.fy[1], lines))
    p.append(c.handle("k", 481, 958))
    moves = [door_move("door", ["15", "k"], "left")]
    model("layn-0-04", "П6.619.0.04", "Шкаф «Лайн»", "living", [W, B, H], "P6-619-0-04.pdf", "по инструкции (в инструкции — «Тумба»)")
    cutlist("layn-0-04", "П6.619.0.04", "reference rows + row 11 read from the page (its marking «П6.619.0.04011» broke the parser); "
            "no sizes in the table — positions measured on the front view",
            [("1", None, "Стенка вертикальная", 1), ("2", None, "Стенка вертикальная", 1), ("3", None, "Перегородка", 1),
             ("4", None, "Стенка горизонтальная", 1), ("5", None, "Стенка горизонтальная", 1), ("6", None, "Стенка вертикальная", 2),
             ("7", None, "Стенка горизонтальная", 1), ("8", None, "Стенка горизонтальная", 1), ("9", None, "Стенка горизонтальная", 2),
             ("10", None, "Стенка горизонтальная", 1), ("11", None, "Стенка горизонтальная", 1), ("12", None, "Полка", 2),
             ("13", None, "Стенка передняя", 2), ("14", None, "Стенка боковая", 2), ("15", None, "Дверь", 1),
             ("16", None, "Стенка задняя", 2), ("17", None, "Стенка задняя", 2)])
    return dump("layn-0-04", [W, B, H], p, moves)


# ------------------------------------------------------------------------------------------------ 0.10 шкаф 2д с витриной
def m010():
    """1080×390×2084: two doors like 0.01 (a 150 stile on each hinge side, glass «накладки» on the backs), glass shelves
    over a fixed horizontal 6, a partition 5 and a shelf on each side below."""
    W, H, B = 1080, 2084, 390
    c = Case(W, H, B, y0=104.5)
    p = c.shell("7", "8", "9", "10") + c.inner("1", "2", "3", "4")
    x0, x1 = 33.0, W - 33.0
    gy = 610.5
    p += [
        c.hor("6", x0, x1, gy),
        c.ver("5", W / 2 - 8, c.ib[1], gy - T),
        c.hor("12", x0, W / 2 - 8, 373, "12-1", loose=True),
        c.hor("12", W / 2 + 8, x1, 373, "12-2", loose=True),
        c.hor("11", x0, x1, 948.2, "11-1", glass=True),
        c.hor("11", x0, x1, 1317.7, "11-2", glass=True),
        c.hor("11", x0, x1, 1688.3, "11-3", glass=True),
        c.back("18", 17, c.ob[1], W / 2, gy - 8, "18-1"),
        c.back("18", W / 2, c.ob[1], W - 17, gy - 8, "18-2"),
        c.back("17", 17, gy - 8, W - 17, c.ot[0]),
        c.light("led-1", 290, 200), c.light("led-2", W - 290, 200),
    ]
    p += c.plinth("13", "14")
    fx0, fx1 = c.fx
    fy0, fy1 = c.fy
    m = W / 2
    lines = [[27.2, 508.5, 319.2, 434.2], [319.2, 434.2, 539.0, 248.0], [148.6, 130.0, 420.4, 610.5]]
    rl = mirror_lines(lines, W)
    st = 150.0
    L = f"M {fx0} {fy0} L {m - 1} {fy0} L {m - 1} {gy} L {fx0 + st} {gy} L {fx0 + st} {fy1} L {fx0} {fy1} Z"
    R = f"M {m + 1} {fy0} L {fx1} {fy0} L {fx1} {fy1} L {fx1 - st} {fy1} L {fx1 - st} {gy} L {m + 1} {gy} Z"
    p += [
        c.front("15.1", fx0, fy0, m - 1, fy1, lines, outline=L),
        c.glass("15.2", fx0 + st - 20, gy - 20, m - 1, fy1),
        c.handle("k-1", 481, 1130, z=c.zf[0]),
        c.front("16.1", m + 1, fy0, fx1, fy1, rl, outline=R),
        c.glass("16.2", m + 1, gy - 20, fx1 - st + 20, fy1),
        c.handle("k-2", W - 481, 1130, z=c.zf[0]),
    ]
    moves = [door_move("door_left", ["15.1", "15.2", "k-1"], "left"), door_move("door_right", ["16.1", "16.2", "k-2"], "right")]
    model("layn-0-10", "П6.619.0.10", "Шкаф 2д «Лайн»", "living", [W, B, H], "P6-619-0-10.pdf", "по инструкции; с подсветкой")
    cutlist("layn-0-10", "П6.619.0.10", "reference rows with the sub-numbers restored from the page (15.1 / 15.2, 16.1 / 16.2 — "
            "the table prints the second «накладка» as 15.2 too); no sizes in the table — positions measured on the front view",
            [("1", None, "Стенка вертикальная", 1), ("2", None, "Стенка вертикальная", 1), ("3", None, "Стенка горизонтальная", 1),
             ("4", None, "Стенка горизонтальная", 1), ("5", None, "Перегородка", 1), ("6", None, "Стенка горизонтальная", 1),
             ("7", None, "Стенка вертикальная", 1), ("8", None, "Стенка вертикальная", 1), ("9", None, "Стенка горизонтальная", 1),
             ("10", None, "Стенка горизонтальная", 1), ("11", None, "Полка (стекло)", 3), ("12", None, "Полка", 2),
             ("13", None, "Стенка передняя", 2), ("14", None, "Стенка боковая", 2), ("15.1", None, "Дверь", 1),
             ("15.2", None, "Накладка (стекло)", 1), ("16.1", None, "Дверь", 1), ("16.2", None, "Накладка (стекло; в таблице 15.2)", 1),
             ("17", None, "Стенка задняя", 1), ("18", None, "Стенка задняя", 2)])
    return dump("layn-0-10", [W, B, H], p, moves)


# ------------------------------------------------------------------------------------------------ 0.12 тумба на металлическом основании
def m012():
    """1973×420×910 on the metal base 22 (three rectangular 20×20 frames 200 high, front and back top rails): a door, a
    drawer over a door, an open niche with two shelves, a door; horizontal handles near the fronts' tops."""
    W, H, B = 1973, 910, 420
    c = Case(W, H, B, y0=200.0)
    p = c.shell("8", "8", "9", "10", ids=("8-l", "8-r", None, None)) + c.inner("1", "2", "6", "7")
    x3, x4, x5 = 557.7, 1097.5, 1400.6          # partitions' left faces
    yb, yt = c.ib[1], c.it[0]
    y11 = 718.5
    p += [
        c.ver("3", x3, yb, yt), c.ver("4", x4, yb, yt), c.ver("5", x5, yb, yt),
        c.hor("11", x3 + T, x4, y11),
        c.hor("12", 33, x3, 563.4, "12-1", loose=True),
        c.hor("12", x3 + T, x4, 467.0, "12-2", loose=True),
        c.hor("12", x5 + T, W - 33, 563.4, "12-3", loose=True),
        c.hor("13", x4 + T, x5, 448.2, "13-1", loose=True),
        c.hor("13", x4 + T, x5, 671.1, "13-2", loose=True),
        c.back("18", 17, c.ob[1], x3 + 8, c.ot[0], "18-1"),
        c.back("18", x5 + 8, c.ob[1], W - 17, c.ot[0], "18-2"),
        c.back("20", x3 + 8, c.ob[1], x4 + 8, y11 - 8),
        c.back("19", x3 + 8, y11 - 8, x4 + 8, c.ot[0]),
        c.back("21", x4 + 8, c.ob[1], x5 + 8, c.ot[0]),
    ]
    fy0, fy1 = c.fy
    lines = [[27.1, 634.5, 564.8, 696.5], [87.2, 226.2, 199.0, 654.1], [199.0, 654.1, 147.3, 884.6],
             [566.5, 696.5, 836.6, 388.1], [836.6, 388.1, 1104.2, 419.0], [767.2, 226.2, 1043.9, 884.6],
             [1409.0, 413.5, 1946.7, 476.2], [1826.5, 226.2, 1774.9, 455.8], [1774.9, 455.8, 1886.6, 884.6]]
    p += [
        c.front("14", c.fx[0], fy0, 564.8, fy1, lines),
        c.handle("k-14", 445.9, 810.5, dir="right"),
        c.front("16", 566.5, fy0, 1104.2, 716.8, lines),
        c.handle("k-16", 835.4, 643.1, dir="right"),
        c.front("15", 1409.0, fy0, c.fx[1], fy1, lines),
        c.handle("k-15", 1528.0, 810.5, dir="right"),
        c.front("17.1", 566.5, 720.2, 1104.2, fy1, lines, grain="x"),
        c.handle("k-17", 835.4, 810.5, dir="right"),
    ]
    box = drawer_box("17", ("17.2", "17.3", "17.4", "17.5"), x3 + T + 13, x4 - 13, 736, 124, c.zf[0])
    p += box
    p += sled_base([101.6, 977.2, 1851.9], B)
    moves = [door_move("door_left", ["14", "k-14"], "left"), door_move("door_middle", ["16", "k-16"], "right"),
             door_move("door_right", ["15", "k-15"], "right"), drawer_move("drawer", "17.1", box, "k-17")]
    model("layn-0-12", "П6.619.0.12", "Тумба «Лайн»", "living", [W, B, H], "P6-619-0-12.pdf",
          "по инструкции; на металлическом опорном основании")
    cutlist("layn-0-12", "П6.619.0.12", "reference rows with the drawer's sub-numbers 17.1–17.5 restored and row 22 (the metal "
            "base) added from the page; the group row «17 Ящик выдвижной, в т. ч.» is left out (its parts are listed); "
            "no sizes in the table — positions measured on the front and side views",
            [("1", None, "Стенка вертикальная", 1), ("2", None, "Стенка вертикальная", 1), ("3", None, "Перегородка", 1),
             ("4", None, "Перегородка", 1), ("5", None, "Перегородка", 1), ("6", None, "Стенка горизонтальная", 1),
             ("7", None, "Стенка горизонтальная", 1), ("8", None, "Стенка вертикальная", 2), ("9", None, "Стенка горизонтальная", 1),
             ("10", None, "Стенка горизонтальная", 1), ("11", None, "Стенка горизонтальная", 1), ("12", None, "Полка", 3),
             ("13", None, "Полка", 2), ("14", None, "Дверь", 1), ("15", None, "Дверь", 1), ("16", None, "Дверь", 1),
             ("17.1", None, "Стенка передняя ящика", 1), ("17.2", None, "Стенка боковая ящика", 1),
             ("17.3", None, "Стенка боковая ящика", 1), ("17.4", None, "Стенка задняя ящика", 1), ("17.5", None, "Дно ящика", 1),
             ("18", None, "Стенка задняя", 2), ("19", None, "Стенка задняя", 1), ("20", None, "Стенка задняя", 1),
             ("21", None, "Стенка задняя", 1), ("22", None, "Металлическое опорное основание", 1)])
    return dump("layn-0-12", [W, B, H], p, moves)


# ------------------------------------------------------------------------------------------------ shift / mirror
def shift(parts, dx, tag=None):
    """Move parts along x (a pedestal built at 0); tag suffixes their ids (two pedestals in one design)."""
    out = []
    for q in parts:
        q = json.loads(json.dumps(q))
        if "box" in q:
            b = q["box"]
            q["box"] = [round(b[0] + dx, 1), b[1], b[2], round(b[3] + dx, 1), b[4], b[5]]
        if "at" in q:
            q["at"] = [round(q["at"][0] + dx, 1), q["at"][1]]
        if q.get("face", {}).get("lines"):
            q["face"]["lines"] = [[round(l[0] + dx, 1), l[1], round(l[2] + dx, 1), l[3]] for l in q["face"]["lines"]]
        if tag and "id" in q:
            q["id"] = f"{q['id']}-{tag}"
        out.append(q)
    return out


def mirror(parts, moves, W):
    """The mirror image of a design across x = W/2 (the «-01» variants)."""
    out = []
    for q in parts:
        q = json.loads(json.dumps(q))
        if "box" in q:
            b = q["box"]
            q["box"] = [round(W - b[3], 1), b[1], b[2], round(W - b[0], 1), b[4], b[5]]
        if "at" in q:
            q["at"] = [round(W - q["at"][0], 1), q["at"][1]]
            q["dir"] = {"left": "right", "right": "left"}.get(q.get("dir"), q.get("dir"))
        if q.get("face", {}).get("lines"):
            q["face"]["lines"] = [[round(W - l[0], 1), l[1], round(W - l[2], 1), l[3]] for l in q["face"]["lines"]]
        if q.get("from"):
            q["from"][0] = W - q["from"][0]
            q["to"][0] = W - q["to"][0]
        out.append(q)
    mv = json.loads(json.dumps(moves))
    for m in mv:
        if m.get("hinge") in ("left", "right"):
            m["hinge"] = {"left": "right", "right": "left"}[m["hinge"]]
    return out, mv


# ------------------------------------------------------------------------------------------------ 1.02 / 1.11 комод
def commode(did, code, H, y0, fronts, hys, lines, base, backs_n):
    """1000×505: four drawers (8 on top: its own box; 9–11 share 9.2–9.4), boxes on 450 runners, the backs joined across by a
    plastic profile. 1.02 on the plinth, 1.11 on the metal base (frames under the inner carcass' sides)."""
    W, B = 1000, 505
    c = Case(W, H, B, y0=y0)
    p = c.shell("5", "5", "6", "7", ids=("5-l", "5-r", None, None)) + c.inner("1", "2", "3", "3", ids=(None, None, "3-top", "3-bottom"))
    ym = (c.ob[1] + c.ot[0]) / 2
    p += [c.back(backs_n, 17, c.ob[1], W - 17, ym, f"{backs_n}-1"), c.back(backs_n, 17, ym, W - 17, c.ot[0], f"{backs_n}-2")]
    moves = []
    x0, x1 = 33 + 13, W - 33 - 13
    for (fn, ns, tag, (fy0, fy1)), hy in zip(fronts, hys):
        p.append(c.front(fn, c.fx[0], fy0, c.fx[1], fy1, lines, grain="x"))
        h = 100 if fy1 - fy0 < 170 else 150
        box = drawer_box(tag, ns, x0, x1, fy0 + 22, h, c.zf[0], depth=450)
        p += box
        p.append(c.handle(f"k-{tag}", W / 2, hy, dir="right", d=128))
        moves.append(drawer_move(f"drawer_{tag}", fn, box, f"k-{tag}", 400))
    if base:
        p += sled_base([16.9, W - 37.3], B, h=y0, z0=20.3)
    else:
        p += c.plinth("12", "13")
    return p, moves


def m102():
    fronts = [("8.1", ("8.2", "8.3", "8.4", "8.5"), "8", (768.6, 913.7)), ("9.1", ("9.2", "9.3", "9.4", "8.5"), "9", (554.8, 765.2)),
              ("10.1", ("9.2", "9.3", "9.4", "8.5"), "10", (341.9, 552.3)), ("11.1", ("9.2", "9.3", "9.4", "8.5"), "11", (128.1, 338.5))]
    lines = [[213.2, 910.7, 435.6, 122.8], [27.7, 208.5, 325.1, 503.2], [325.1, 503.2, 973.4, 680.4]]
    p, moves = commode("layn-1-02", "П6.619.1.02", 940, 101.8, fronts, [841.2, 660.0, 446.7, 233.3], lines, False, "14")
    model("layn-1-02", "П6.619.1.02", "Комод «Лайн»", "bedroom", [1000, 505, 940], "P6-619-1-02-1.pdf", "по инструкции; на цоколе")
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Стенка горизонтальная", 2), ("5", "Стенка вертикальная", 2),
            ("6", "Крышка", 1), ("7", "Дно", 1), ("8.1", "Стенка передняя", 1), ("8.2", "Стенка боковая", 1), ("8.3", "Стенка боковая", 1),
            ("8.4", "Стенка задняя", 1), ("8.5", "Дно (ящиков 8–11)", 4), ("9.1", "Стенка передняя", 1), ("9.2", "Стенка боковая (ящиков 9–11)", 3),
            ("9.3", "Стенка боковая (ящиков 9–11)", 3), ("9.4", "Стенка задняя (ящиков 9–11)", 3), ("10.1", "Стенка передняя", 1),
            ("11.1", "Стенка передняя", 1), ("12", "Стенка передняя", 2), ("13", "Стенка боковая", 2), ("14", "Стенка задняя", 2)]
    cutlist("layn-1-02", "П6.619.1.02", "table of the page with the drawers' rows summed over the drawers (8.5 in all four, 9.2–9.4 in "
            "9, 10, 11); group rows «Ящик выдвижной, в т.ч.» left out; no sizes — positions measured on the front view",
            [(n, None, nm, k) for n, nm, k in rows])
    return dump("layn-1-02", [1000, 505, 940], p, moves)


def m111():
    fronts = [("8.1", ("8.2", "8.3", "8.4", "8.5"), "8", (865.0, 1009.8)), ("9.1", ("9.2", "9.3", "9.4", "8.5"), "9", (651.7, 861.6)),
              ("10.1", ("9.2", "9.3", "9.4", "8.5"), "10", (439.3, 649.2)), ("11.1", ("9.2", "9.3", "9.4", "8.5"), "11", (226.0, 435.9))]
    lines = [[212.7, 1007.9, 435.8, 219.1], [27.4, 305.9, 325.5, 600.3], [325.5, 600.3, 973.2, 776.9]]
    p, moves = commode("layn-1-11", "П6.619.1.11", 1036, 199.8, fronts, [937.4, 756.7, 543.8, 331.0], lines, True, "12")
    model("layn-1-11", "П6.619.1.11", "Комод «Лайн»", "bedroom", [1000, 505, 1036], "P6-619-1-11-2.pdf", "по инструкции; на металлическом опорном основании")
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Стенка горизонтальная", 2), ("5", "Стенка вертикальная", 2),
            ("6", "Крышка", 1), ("7", "Дно", 1), ("8.1", "Стенка передняя", 1), ("8.2", "Стенка боковая", 1), ("8.3", "Стенка боковая", 1),
            ("8.4", "Стенка задняя", 1), ("8.5", "Дно (ящиков 8–11)", 4), ("9.1", "Стенка передняя", 1), ("9.2", "Стенка боковая (ящиков 9–11)", 3),
            ("9.3", "Стенка боковая (ящиков 9–11)", 3), ("9.4", "Стенка задняя (ящиков 9–11)", 3), ("10.1", "Стенка передняя", 1),
            ("11.1", "Стенка передняя", 1), ("12", "Стенка задняя", 2)]
    cutlist("layn-1-11", "П6.619.1.11", "table of the page (the PDF parser lost most rows) with the drawers' rows summed over the "
            "drawers; the metal base is «в комплект также входит» (no row); no sizes — positions measured on the front and side views",
            [(n, None, nm, k) for n, nm, k in rows])
    return dump("layn-1-11", [1000, 505, 1036], p, moves)


# ------------------------------------------------------------------------------------------------ 1.04 / 1.12 тумбы прикроватные
def bedside(did, H, y0, fronts, lines, base, back_n):
    W, B = 500, 390
    c = Case(W, H, B, y0=y0)
    p = c.shell("3", "3", "4", "5", ids=("3-l", "3-r", None, None)) + c.inner("1", "1", "2", "2", ids=("1-l", "1-r", "2-top", "2-bottom"))
    p.append(c.back(back_n, 17, c.ob[1], W - 17, c.ot[0]))
    moves = []
    for fn, tag, (fy0, fy1), hy in fronts:
        p.append(c.front(fn, c.fx[0], fy0, c.fx[1], fy1, lines, grain="x"))
        box = drawer_box(tag, ("6.2", "6.3", "6.4", "6.5"), 46, W - 46, fy0 + 20, 100, c.zf[0], depth=350)
        p += box
        p.append(c.handle(f"k-{tag}", W / 2, hy, dir="right"))
        moves.append(drawer_move(f"drawer_{tag}", fn, box, f"k-{tag}"))
    if base:
        p += sled_base([16.9, W - 37.2], B, h=y0, z0=19.8)
    else:
        p += c.plinth("8", "9")
    return p, moves


def m104():
    p, mv = bedside("layn-1-04", 449, 101.8, [("6.1", "top", (277.0, 422.8), 350.2), ("7.1", "bottom", (128.0, 273.8), 200.9)],
                    [[87.9, 127.0, 413.9, 422.0]], False, "10")
    model("layn-1-04", "П6.619.1.04", "Тумба прикроватная «Лайн»", "bedroom", [500, 390, 449], "P6-619-1-04-1.pdf", "по инструкции; на цоколе")
    rows = [("1", "Стенка вертикальная", 2), ("2", "Стенка горизонтальная", 2), ("3", "Стенка вертикальная", 2), ("4", "Крышка", 1),
            ("5", "Дно", 1), ("6.1", "Стенка передняя", 1), ("6.2", "Стенка боковая (ящиков 6, 7)", 2), ("6.3", "Стенка боковая (ящиков 6, 7)", 2),
            ("6.4", "Стенка задняя (ящиков 6, 7)", 2), ("6.5", "Дно (ящиков 6, 7)", 2), ("7.1", "Стенка передняя", 1),
            ("8", "Стенка передняя", 2), ("9", "Стенка боковая", 2), ("10", "Стенка задняя", 1)]
    cutlist("layn-1-04", "П6.619.1.04", "table of the page (the PDF parser lost the drawers' rows) with the drawers' rows summed; "
            "no sizes — positions measured on the front view", [(n, None, nm, k) for n, nm, k in rows])
    return dump("layn-1-04", [500, 390, 449], p, mv)


def m112():
    p, mv = bedside("layn-1-12", 397, 199.9, [("6.1", "d", (226.3, 371.1), 298.5)], [[251.6, 226.1, 412.9, 371.2]], True, "7")
    model("layn-1-12", "П6.619.1.12", "Тумба прикроватная «Лайн»", "bedroom", [500, 390, 397], "P6-619-1-12-2.pdf",
          "по инструкции; на металлическом опорном основании")
    rows = [("1", "Стенка вертикальная", 2), ("2", "Стенка горизонтальная", 2), ("3", "Стенка вертикальная", 2), ("4", "Крышка", 1),
            ("5", "Дно", 1), ("6.1", "Стенка передняя", 1), ("6.2", "Стенка боковая", 1), ("6.3", "Стенка боковая", 1),
            ("6.4", "Стенка задняя", 1), ("6.5", "Дно", 1), ("7", "Стенка задняя", 1)]
    cutlist("layn-1-12", "П6.619.1.12", "table of the page (the PDF parser lost rows 5 and 6.x); the metal base is «в комплект также "
            "входит» (no row); no sizes — positions measured on the front and side views", [(n, None, nm, k) for n, nm, k in rows])
    return dump("layn-1-12", [500, 390, 397], p, mv)


# ------------------------------------------------------------------------------------------------ 1.28 шкаф для одежды 2д
def m128():
    W, H, B = 950, 2300, 585
    c = Case(W, H, B, y0=104.3)
    p = c.shell("5", "5", "6", "7", ids=("5-l", "5-r", None, None)) + c.inner("1", "2", "3", "4")
    yh = 1870.0
    p += [
        c.hor("8", 33, W - 33, yh),
        P("9", [W / 2 - 8, c.ib[1], 3, W / 2 + 8, yh - T, 63], mat="inner"),
        c.back("14", 17, c.ob[1], W / 2, yh - 8, "14-1"), c.back("14", W / 2, c.ob[1], W - 17, yh - 8, "14-2"),
        c.back("13", 17, yh - 8, W - 17, c.ot[0]),
        {"id": "rail", "kind": "tube", "mat": "chrome", "box": [36.5, 1782, 272, 913.5, 1807, 297]},
    ]
    lines = [[27.1, 1476.5, 922.5, 928.5], [115.0, 1424.5, 474.3, 1718.9], [475.7, 1717.0, 922.5, 1849.5],
             [27.1, 554.0, 474.3, 686.0], [475.7, 687.0, 835.8, 980.0]]
    p += [c.front("12", c.fx[0], c.fy[0], 474.3, c.fy[1], lines, pid="12-l"), c.handle("k-l", 424.0, 1202.0, d=123),
          c.front("12", 475.7, c.fy[0], c.fx[1], c.fy[1], lines, pid="12-r"), c.handle("k-r", 525.6, 1202.0, d=123)]
    p += c.plinth("10", "11")
    moves = [door_move("door_left", ["12-l", "k-l"], "left"), door_move("door_right", ["12-r", "k-r"], "right")]
    model("layn-1-28", "П6.619.1.28", "Шкаф для одежды 2Д «Лайн»", "bedroom", [W, B, H], "P6-619-1-28-3.pdf",
          "по инструкции; полка и штанга 877 мм")
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Стенка горизонтальная", 1), ("4", "Стенка горизонтальная", 1),
            ("5", "Стенка вертикальная", 2), ("6", "Стенка горизонтальная", 1), ("7", "Стенка горизонтальная", 1), ("8", "Стенка горизонтальная", 1),
            ("9", "Брусок жесткости", 1), ("10", "Стенка передняя", 2), ("11", "Стенка боковая", 2), ("12", "Дверь", 2),
            ("13", "Стенка задняя", 1), ("14", "Стенка задняя", 2)]
    cutlist("layn-1-28", "П6.619.1.28", "reference rows (complete); no sizes — positions measured on the front view (the hat shelf 8, "
            "the rib 9 and the rail are hidden behind the doors: placed by the exploded view)", [(n, None, nm, k) for n, nm, k in rows])
    return dump("layn-1-28", [W, B, H], p, moves)


# ------------------------------------------------------------------------------------------------ 2.11 стеллаж
def m211():
    W, H, B = 566, 2084, 390
    c = Case(W, H, B, y0=104.1)
    p = c.shell("3", "3", "4", "5", ids=("3-l", "3-r", None, None)) + c.inner("1", "1.1", "2", "2", ids=(None, None, "2-top", "2-bottom"))
    for i, y in enumerate((522.1, 908.4, 1296.4, 1681.8)):
        p.append(c.hor("6", 33, W - 33, y, f"6-{i + 1}"))
    p += [c.back("9", 17, c.ob[1], W - 17, 514.1, "9-1"), c.back("10", 17, 514.1, W - 17, 1673.8), c.back("9", 17, 1673.8, W - 17, c.ot[0], "9-2")]
    p += c.plinth("7", "8")
    model("layn-2-11", "П6.619.2.11", "Стеллаж «Лайн»", "living", [W, B, H], "IS-P6-619-2-11-2.pdf", "по инструкции; открытый, 4 неподвижные полки")
    rows = [("1", "Стенка вертикальная", 1), ("1.1", "Стенка вертикальная", 1), ("2", "Стенка горизонтальная", 2), ("3", "Стенка вертикальная", 2),
            ("4", "Стенка горизонтальная", 1), ("5", "Стенка горизонтальная", 1), ("6", "Стенка горизонтальная", 4), ("7", "Стенка передняя", 2),
            ("8", "Стенка боковая", 2), ("9", "Стенка задняя", 2), ("10", "Стенка задняя", 1)]
    cutlist("layn-2-11", "П6.619.2.11", "reference rows (complete); no sizes — positions measured on the front view; the backs' joints "
            "(two equal 9 and the long 10) put on the first and the last shelf", [(n, None, nm, k) for n, nm, k in rows])
    return dump("layn-2-11", [W, B, H], p, [])


# ------------------------------------------------------------------------------------------------ столы письменные
def pedestal(n, fronts, y0=109.5, W=492.0, H=763.0, B=654.0):
    """A desk pedestal (local x 0..W): outer sides n['l'], n['r'], outer bottom n['bot'] (the desk top is separate), the inner
    carcass n['il'], n['ir'], n['it'] ×2 (top and bottom share a number), a ЛДСП back n['back'] between the outer sides,
    the plinth n['pf'], n['ps']; fronts: (n, kind, y0, y1, handle y, box numbers) with kind drawer / door."""
    c = Case(W, H, B, y0=y0)
    c.zi = (T, B - 23.0)
    sh = c.shell(n["l"], n["r"], "top", n["bot"], ids=(n.get("l_id"), n.get("r_id"), None, n.get("bot_id")))
    p = [q for q in sh if q.get("n") != "top"]
    p += c.inner(n["il"], n["ir"], n["it"], n["it"], ids=(None, None, f"{n['it']}-top", f"{n['it']}-bottom"))
    p.append(P(n["back"], [17, c.ob[1], 0, W - 17, c.ot[0], T], n.get("back_id"), mat="inner"))
    p += c.plinth(n["pf"], n["ps"])
    items = []
    for fn, kind, fy0, fy1, hy, ns, tag in fronts:
        if kind == "drawer":
            p.append(c.front(fn, c.fx[0], fy0, c.fx[1], fy1, (), pid=f"{fn}-{tag}" if tag else None, grain="x"))
            box = drawer_box(tag or fn, ns, 46, W - 46, fy0 + 25, 150, c.zf[0], depth=450)
            p += box
            items.append(("drawer", f"{fn}-{tag}" if tag else fn, box, f"k-{tag or fn}"))
        else:
            p.append(c.front(fn, c.fx[0], fy0, c.fx[1], fy1, ()))
            items.append(("door", fn, None, f"k-{fn}"))
        p.append(c.handle(f"k-{tag or fn}", W / 2, hy, dir="right", d=129))
    return c, p, items


def add_lines(parts, lines):
    """Groove lines (absolute) onto every front of a design, clipped to each."""
    for q in parts:
        if q.get("kind") == "front":
            b = q["box"]
            ls = clip_lines(lines, b[0], b[1], b[3], b[4])
            if ls:
                q["face"] = dict(GROOVE, lines=[[round(v, 1) for v in l] for l in ls])


def moves_of(items, hinge=None):
    mv = []
    for kind, fid, box, hid in items:
        if kind == "drawer":
            mv.append(drawer_move(f"drawer_{fid}", fid, box, hid, 400))
        else:
            mv.append(door_move(f"door_{fid}", [fid, hid], hinge))
    return mv


def m215():
    W, H, B = 1524, 763, 654
    nl = {"l": "8", "r": "9", "l_id": "8-l", "bot": "11", "bot_id": "11-l", "il": "1", "ir": "2", "it": "5", "back": "14", "back_id": "14-l",
          "pf": "20", "ps": "21"}
    dn = ("15.2", "15.3", "15.4", "15.5")
    cl, pl, il = pedestal(nl, [("15.1", "drawer", 538.1, 737.1, 638.05, dn, "a"), ("16.1", "drawer", 337.3, 535.3, 436.25, dn, "b"),
                               ("17.1", "drawer", 135.5, 334.4, 234.45, dn, "c")])
    nr = {"l": "10", "r": "8", "r_id": "8-r", "bot": "11", "bot_id": "11-r", "il": "3", "ir": "4", "it": "5", "back": "14", "back_id": "14-r",
          "pf": "20", "ps": "21"}
    cr, pr, ir = pedestal(nr, [("15.1", "drawer", 538.1, 737.1, 638.05, dn, "d"), ("19", "door", 135.5, 535.3, 436.25, None, None)])
    pr += [cr.hor("6", 17 + T, 492 - 17 - T, 536.7), cr.hor("7", 17 + T, 492 - 17 - T, 337.0, loose=True)]
    pl = [dict(q, id=q["id"] + "-L") if q.get("id") and q.get("n") in ("5", "20", "21") else q for q in pl]
    pr = shift(pr, 1032.0)
    pr = [dict(q, id=q["id"] + "-R") if q.get("id") and q.get("n") in ("5", "20", "21") else q for q in pr]
    for q in pr:
        if q.get("kind") == "tube" and q["id"].startswith("g-"):
            q["id"] += "-R"
    p = pl + pr + [P("13", [0, H - T, 0, W, H, B], mat="body", grain="x"), P("12", [491.0, 429.5, 20, 1033.0, H - T, 36], mat="body", grain="x")]
    add_lines(p, [[21.1, 708.9, 364.4, 133.1], [80.4, 614.7, 364.8, 737.7], [127.9, 135.5, 294.7, 250.0],
                  [1056.9, 708.7, 1397.8, 130.7], [1112.2, 614.5, 1396.7, 737.5], [1059.4, 232.3, 1279.3, 333.4]])
    ir = [(k, f, b, h) for k, f, b, h in ir]
    mv = moves_of(il) + [{"type": m["type"], **{kk: vv for kk, vv in m.items() if kk != "type"}} for m in []]
    mv += [drawer_move("drawer_d", "15.1-d", [q for q in pr if q.get("id", "").endswith("-d") and q.get("n") in dn], "k-d", 400),
           door_move("door", ["19", "k-19"], "right")]
    model("layn-2-15", "П6.619.2.15", "Стол письменный 2т «Лайн»", "office", [W, B, H], "P6-619-2-15-1.pdf",
          "по инструкции; две тумбы на цоколях, царга между ними")
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Стенка вертикальная", 1), ("4", "Стенка вертикальная", 1),
            ("5", "Стенка горизонтальная", 4), ("6", "Стенка горизонтальная", 1), ("7", "Полка", 1), ("8", "Стенка вертикальная", 2),
            ("9", "Стенка вертикальная", 1), ("10", "Стенка вертикальная", 1), ("11", "Стенка горизонтальная", 2), ("12", "Царга", 1),
            ("13", "Крышка", 1), ("14", "Стенка задняя", 2), ("15.1", "Стенка передняя (ящиков 15, ×2)", 2),
            ("15.2", "Стенка боковая (ящиков 15, 16, 17)", 4), ("15.3", "Стенка боковая (ящиков 15, 16, 17)", 4),
            ("15.4", "Стенка задняя (ящиков 15, 16, 17)", 4), ("15.5", "Дно (ящиков 15, 16, 17)", 4), ("16.1", "Стенка передняя", 1),
            ("17.1", "Стенка передняя", 1), ("19", "Дверь", 1), ("20", "Стенка передняя", 4), ("21", "Стенка боковая", 4)]
    cutlist("layn-2-15", "П6.619.2.15", "table of the page with the drawers' rows summed (drawer 15 twice, 16 and 17 share 15.2–15.5); "
            "group rows left out; no sizes — positions measured on the front and side views", [(n, None, nm, k) for n, nm, k in rows])
    return dump("layn-2-15", [W, B, H], p, mv)


def desk216():
    """П6.619.2.16: a panel leg 4 on the left (on two glides), a three-drawer pedestal on the right, the modesty panel 9 between."""
    W, H, B = 1051, 763, 654
    n = {"l": "5", "r": "6", "bot": "7", "il": "1", "ir": "2", "it": "3", "back": "10", "pf": "14", "ps": "15"}
    dn = ("11.2", "11.3", "11.4", "11.5")
    c, pp, items = pedestal(n, [("11.1", "drawer", 538.1, 737.1, 637.6, dn, None), ("12.1", "drawer", 336.3, 535.3, 436.25, dn, None),
                                ("13.1", "drawer", 135.5, 333.5, 234.45, dn, None)])
    # boxes of 12 / 13 need their own ids: rebuild with tags
    pp = [q for q in pp if not (q.get("n") in dn)]
    boxes = {}
    for fn, fy0 in (("11.1", 538.1), ("12.1", 336.3), ("13.1", 135.5)):
        tag = fn.split(".")[0]
        boxes[fn] = drawer_box(tag, dn, 46, 492 - 46, fy0 + 25, 150, c.zf[0], depth=450)
        pp += boxes[fn]
    pp = shift(pp, W - 492.0)
    for fn in boxes:
        boxes[fn] = [dict(q, box=[q["box"][0] + W - 492.0, q["box"][1], q["box"][2], q["box"][3] + W - 492.0, q["box"][4], q["box"][5]]) for q in boxes[fn]]
    p = pp + [
        P("8", [0, H - T, 0, W, H, B], mat="body", grain="x"),
        P("4", [1, 10, 0, 17.5, H - T, B], mat="body"),
        P("9", [17.5, 429.5, 20, W - 492.0 + 1, H - T, 36], mat="body", grain="x"),
        {"id": "g4-1", "kind": "tube", "mat": "black", "box": [2.3, 0, 40, 16.3, 10, 54]},
        {"id": "g4-2", "kind": "tube", "mat": "black", "box": [2.3, 0, B - 54, 16.3, 10, B - 40]},
    ]
    add_lines(p, [[685.3, 136.1, 1024.2, 709.2], [685.3, 737.1, 970.5, 611.9], [925.5, 135.5, 757.0, 253.0], [757.0, 253.0, 862.0, 433.0]])
    mv = [drawer_move(f"drawer_{fn.split('.')[0]}", fn, boxes[fn], f"k-{fn}", 400) for fn in ("11.1", "12.1", "13.1")]
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Стенка горизонтальная", 2), ("4", "Стенка вертикальная", 1),
            ("5", "Стенка вертикальная", 1), ("6", "Стенка вертикальная", 1), ("7", "Стенка горизонтальная", 1), ("8", "Крышка", 1),
            ("9", "Царга", 1), ("10", "Стенка задняя", 1), ("11.1", "Стенка передняя", 1), ("11.2", "Стенка боковая (ящиков 11–13)", 3),
            ("11.3", "Стенка боковая (ящиков 11–13)", 3), ("11.4", "Стенка задняя (ящиков 11–13)", 3), ("11.5", "Дно (ящиков 11–13)", 3),
            ("12.1", "Стенка передняя", 1), ("13.1", "Стенка передняя", 1), ("14", "Стенка передняя", 2), ("15", "Стенка боковая", 2)]
    return p, mv, rows


def m216():
    W, H, B = 1051, 763, 654
    p, mv, rows = desk216()
    model("layn-2-16", "П6.619.2.16", "Стол письменный «Лайн»", "office", [W, B, H], "P6-619-2-16-1.pdf", "по инструкции; тумба справа")
    cutlist("layn-2-16", "П6.619.2.16", "table of the page with the drawers' rows summed (11.2–11.5 in drawers 11, 12, 13); group rows "
            "left out; no sizes — positions measured on the front view", [(n, None, nm, k) for n, nm, k in rows])
    return dump("layn-2-16", [W, B, H], p, mv)


def m21601():
    W, H, B = 1051, 763, 654
    p, mv, rows = desk216()
    p, mv = mirror(p, mv, W)
    model("layn-2-16-01", "П6.619.2.16-01", "Стол письменный «Лайн»", "office", [W, B, H], "P6-619-2-16-01-2.pdf",
          "по инструкции; тумба слева (зеркально 2.16, как на чертеже)")
    cutlist("layn-2-16-01", "П6.619.2.16-01", "table of the page (same rows as 2.16) with the drawers' rows summed; group rows left out; "
            "no sizes — the front view is the mirror image of 2.16", [(n, None, nm, k) for n, nm, k in rows])
    return dump("layn-2-16-01", [W, B, H], p, mv)


# ------------------------------------------------------------------------------------------------ 0.06 стол журнальный
def m006():
    """1000×600×422 on four wheels (KM-00-50-D20): an oak C-shape (top 4, bottom 5, end 3) 880 long round a black open box
    (horizontals 2, ends 1) that runs through it and stands out 120 mm at the other end, a black lengthwise partition 6
    in the box. Built as the catalogue shows it (the black box on the left); the instruction draws the mirror image."""
    W, H, B = 1000, 422, 600
    yb = 60.3
    p = [
        P("5", [0, yb, 0, 880, yb + 15.6, B], mat="body", grain="x"),
        P("4", [0, H - 15.6, 0, 880, H, B], mat="body", grain="x"),
        P("3", [1, yb + 15.6, 0, 17, H - 15.6, B], mat="body"),
        P("2", [340, yb + 15.6, 19.7, W, yb + 31.8, 580.3], "2-bottom", mat="inner", grain="x"),
        P("2", [340, H - 31.8, 19.7, W, H - 15.6, 580.3], "2-top", mat="inner", grain="x"),
        P("1", [341, yb + 31.8, 19.7, 357, H - 31.8, 580.3], "1-l", mat="inner"),
        P("1", [983, yb + 31.8, 19.7, 999, H - 31.8, 580.3], "1-r", mat="inner"),
        P("6", [357, yb + 31.8, 292, 983, H - 31.8, 308], mat="inner", grain="x"),
    ]
    k = 0
    for x in (109.4, 770.7):
        for z in (60.0, 540.0):
            k += 1
            p += [{"id": f"wheel-{k}", "kind": "panel", "mat": "black", "shape": "circle", "edge": 3, "box": [x - 10, 0, z - 25, x + 10, 50, z + 25]},
                  {"id": f"wheel-{k}-fork", "kind": "panel", "mat": "black", "edge": 1, "box": [x - 20, 50, z - 20, x + 20, yb, z + 20]}]
    p, _ = mirror(p, [], W)
    model("layn-0-06", "П6.619.0.06", "Стол журнальный «Лайн»", "tables", [W, B, H], "P6-619-0-06.pdf",
          "по инструкции; на колёсных опорах; черный короб слева, как в каталоге (в инструкции — зеркально)")
    cutlist("layn-0-06", "П6.619.0.06", "reference rows (complete); no sizes — positions measured on the front and top views",
            [("1", None, "Стенка вертикальная", 2), ("2", None, "Стенка горизонтальная", 2), ("3", None, "Стенка вертикальная", 1),
             ("4", None, "Крышка", 1), ("5", None, "Дно", 1), ("6", None, "Перегородка", 1)])
    return dump("layn-0-06", [W, B, H], p, [])


# ------------------------------------------------------------------------------------------------ 0.08 / 0.09 полки
def shelf(did, code, W):
    """A wall board 250 high with a shelf 16 × 200 under the front 24 mm above its lower edge, 24 mm shorter at each end."""
    p = [P("1", [0, 0, 0, W, 250, 16], mat="body", grain="x"), P("2", [24, 24, 16, W - 24, 40, 216], mat="body", grain="x")]
    model(did, code, "Полка «Лайн»", "living", [W, 216, 250], f"P6-619-{code[-4:].replace('.', '-')}{'-1' if W == 1670 else ''}.pdf",
          "по инструкции; навесная", mount="wall")
    cutlist(did, code, "reference rows (complete); no sizes — positions measured on the front and side views",
            [("1", None, "Стенка передняя", 1), ("2", None, "Стенка горизонтальная", 1)])
    return dump(did, [W, 216, 250], p, [])


# ------------------------------------------------------------------------------------------------ 1.26 шкаф 4д (по каталогу)
def m126():
    """1852×585×2300, by the catalogue (p. 69 cut-out, its interior sketch, the p. 68 photo): 1.28's construction with four
    doors (hinges L, L, R, R), partitions behind the joints 1|2 and 3|4; the middle section is 1.28's (hat shelf, rail,
    rib), the outer ones have four loose shelves each; the milled lines read off the cut-out (squashed ±30 mm)."""
    W, H, B = 1852, 2300, 585
    c = Case(W, H, B, y0=104.3)
    p = c.shell("side-l", "side-r", "top", "bottom") + c.inner("in-side-l", "in-side-r", "in-top", "in-bottom")
    p = [dict({k: v for k, v in q.items() if k != "n"}, id=q["n"]) for q in p]
    fx0, fx1 = c.fx
    dw = (fx1 - fx0 - 3 * 1.4) / 4
    xs = [fx0 + i * (dw + 1.4) for i in range(4)]
    j1, j3 = xs[1] - 0.7, xs[3] - 0.7                     # joints 1|2 and 3|4
    yh = 1870.0
    p += [
        c.ver(None, j1 - 8, c.ib[1], c.it[0], "partition-l"), c.ver(None, j3 - 8, c.ib[1], c.it[0], "partition-r"),
        c.hor(None, j1 + 8, j3 - 8, yh, "hat-shelf"),
        P(None, [W / 2 - 8, c.ib[1], 3, W / 2 + 8, yh - T, 63], "rib", mat="inner"),
        {"id": "rail", "kind": "tube", "mat": "chrome", "box": [round(W / 2 - 438.5, 1), 1782, 272, round(W / 2 + 438.5, 1), 1807, 297]},
        c.back(None, 17, c.ob[1], j1, c.ot[0], "back-l"), c.back(None, j3, c.ob[1], W - 17, c.ot[0], "back-r"),
        c.back(None, j1, c.ob[1], W / 2, yh - 8, "back-m1"), c.back(None, W / 2, c.ob[1], j3, yh - 8, "back-m2"),
        c.back(None, j1, yh - 8, j3, c.ot[0], "back-m3"),
    ]
    for side, (a, b) in (("l", (33, j1 - 8)), ("r", (j3 + 8, W - 33))):
        for k, y in enumerate((554, 989, 1424, 1865)):
            p.append(c.hor(None, a, b, y, f"shelf-{side}{k + 1}", loose=True))
    lines = [[27, 1932, 470, 1662], [27, 1305, 470, 1375], [579, 1336, 918, 1662], [579, 1336, 1346, 1057], [1382, 1063, 1825, 1105],
             [27, 659, 184, 701], [184, 701, 470, 584], [470, 584, 918, 784], [918, 784, 1225, 1090],
             [1382, 1843, 1673, 1703], [1673, 1703, 1825, 1773], [1152, 1787, 1370, 1848]]
    hinges = ["left", "left", "right", "right"]
    hx = [419, 867, 973, 1418]
    moves = []
    for i in range(4):
        fid, kid = f"door-{i + 1}", f"k-{i + 1}"
        p.append(c.front(None, xs[i], c.fy[0], xs[i] + dw, c.fy[1], lines, pid=fid))
        p.append(c.handle(kid, hx[i], 1202.0, d=123))
        moves.append(door_move(fid, [fid, kid], hinges[i]))
    pl = c.plinth("pf", "ps")
    for q in pl:
        if q.get("n"):
            del q["n"]
    p += pl
    model("layn-1-26", "П6.619.1.26", "Шкаф для одежды 4д «Лайн»", "bedroom", [W, B, H], None,
          "по каталогу, без инструкции; конструкция шкафа 2Д П6.619.1.28, четыре двери (петли Л, Л, П, П)")
    return dump("layn-1-26", [W, B, H], p, moves)


# ------------------------------------------------------------------------------------------------ 1.03 зеркало (по каталогу)
def m103():
    p = [P(None, [0, 0, 0, 1000, 700, 16], "board", mat="body", grain="x"),
         {"id": "mirror", "kind": "mirror", "box": [25, 25, 16, 975, 675, 20]}]
    model("layn-1-03", "П6.619.1.03", "Зеркало «Лайн»", "decor", [1000, 20, 700], None,
          "по каталогу, без инструкции; зеркало на щите «Дуб Вотан», рамка 25 мм", mount="wall")
    return dump("layn-1-03", [1000, 20, 700], p, [])


# ------------------------------------------------------------------------------------------------ кровати (по каталогу)
def bed(did, code, name, W, sleep, L=2142, H=950):
    """By the catalogue (p. 67–69 photos): an oak box (side rails and the foot, 260 high) on a black plinth set in 50 mm,
    the headboard at the head end: an oak back board with oak edge strips round a black field and a grey «Камень серый»
    panel with milled lines (the fronts' look); the metal frame (металлокаркас) with slats inside the box, a mattress.
    x = width, z = length from the head."""
    yp, yr = 90.0, 350.0               # plinth top, rails' top
    hb = 56.0                          # headboard thickness
    p = [
        P(None, [0, 0, 0, W, H, T], "hb-back", mat="body", grain="x"),
        P(None, [0, 0, T, T, H, hb], "hb-side-l", mat="body"),
        P(None, [W - T, 0, T, W, H, hb], "hb-side-r", mat="body"),
        P(None, [T, H - T, T, W - T, H, hb], "hb-top", mat="body", grain="x"),
        P(None, [T, yp, T, W - T, H - T, hb - T], "hb-field", mat="inner", grain="x"),
        P(None, [0, yp, hb, T, yr, L], "rail-l", mat="body", grain="z"),
        P(None, [W - T, yp, hb, W, yr, L], "rail-r", mat="body", grain="z"),
        P(None, [T, yp, L - T, W - T, yr, L], "foot", mat="body", grain="x"),
        P(None, [T, yp, hb, W - T, yr, hb + T], "rail-head", mat="inner", grain="x"),
        P(None, [50, 4, 106, 50 + T, yp, L - 50], "plinth-l", mat="inner", grain="z"),
        P(None, [W - 50 - T, 4, 106, W - 50, yp, L - 50], "plinth-r", mat="inner", grain="z"),
        P(None, [50 + T, 4, 106, W - 50 - T, yp, 106 + T], "plinth-h", mat="inner", grain="x"),
        P(None, [50 + T, 4, L - 50 - T, W - 50 - T, yp, L - 50], "plinth-f", mat="inner", grain="x"),
    ]
    p.append({"id": "hb-panel", "kind": "front", "grain": "x", "box": [T + REV, yr + 30, hb - T, W - T - REV, H - T - REV, hb],
              "face": dict(GROOVE, lines=[[round(v, 1) for v in l] for l in clip_lines(
                  [[T + REV, yr + 30 + 0.25 * (H - yr - 56), 0.45 * W, yr + 30 + 0.62 * (H - yr - 56)],
                   [0.45 * W, yr + 30 + 0.62 * (H - yr - 56), W - T - REV, yr + 30 + 0.74 * (H - yr - 56)],
                   [0.45 * W, yr + 30 + 0.62 * (H - yr - 56), 0.6 * W, H - T - REV]],
                  T + REV, yr + 30, W - T - REV, H - T - REV)])})
    # glides under the plinth corners and the headboard
    k = 0
    for x in (50 + 8, W - 50 - 8):
        for z in (114, L - 58):
            k += 1
            p.append({"id": f"g-{k}", "kind": "tube", "mat": "black", "box": [x - 7, 0, z - 7, x + 7, 4, z + 7]})
    # металлокаркас: a black steel frame round the sleeping place, a middle beam and leg, slats, the mattress
    mx0, mx1 = (W - sleep) / 2, (W + sleep) / 2
    mz0, mz1 = hb + T + (L - T - hb - T - 2000) / 2, hb + T + (L - T - hb - T - 2000) / 2 + 2000
    ym = 255.0
    p += [
        tube("m-l", [mx0, ym, mz0, mx0 + 30, ym + 40, mz1]), tube("m-r", [mx1 - 30, ym, mz0, mx1, ym + 40, mz1]),
        tube("m-h", [mx0 + 30, ym, mz0, mx1 - 30, ym + 40, mz0 + 30]), tube("m-f", [mx0 + 30, ym, mz1 - 30, mx1 - 30, ym + 40, mz1]),
    ]
    if sleep >= 1200:
        c = W / 2
        p += [tube("m-c", [c - 15, ym, mz0 + 30, c + 15, ym + 40, mz1 - 30]),
              tube("m-leg-1", [c - 12.5, 4, 700, c + 12.5, ym, 725]), tube("m-leg-2", [c - 12.5, 4, 1400, c + 12.5, ym, 1425])]
    n = 24
    step = (mz1 - mz0 - 60) / n
    for i in range(n):
        z = mz0 + 30 + i * step + (step - 53) / 2
        p.append({"id": f"slat-{i + 1}", "kind": "panel", "mat": "#c9a877", "box": [round(mx0 + 20, 1), ym + 40, round(z, 1), round(mx1 - 20, 1), ym + 48, round(z + 53, 1)]})
    p.append({"id": "mattress", "kind": "mattress", "box": [mx0, ym + 48, mz0, mx1, ym + 248, mz1]})
    model(did, code, name, "bedroom", [W, L, H], None, f"по каталогу, без инструкции; спальное место 2000×{sleep}, металлокаркас")
    return dump(did, [W, L, H], p, [])


# ------------------------------------------------------------------------------------------------ catalogue fragment
FINISHES = [
    {"id": "layn-kamen-votan", "name": "Камень серый / Дуб Вотан 376 WML / Черный",
     "body": "door_enamel_whitey#c4a58c", "front": "door_enamel_whitey#4a4a4a", "back": "door_enamel_whitey#272825",
     "roles": {"inner": "door_enamel_whitey#272825"}, "swatch": "#4a4a4a"},
]
COLLECTION = {"id": "layn", "name": "Лайн", "brand": "Пинскдрев", "finishes": ["layn-kamen-votan"], "metal": "black",
              "note": "Каталог «Корпусная мебель ч. II» 2025, с. 65–69 (PDF; с. 126–135 по нумерации каталога). Наружный корпус ЛДСП 16 "
                      "«Дуб Вотан 376 WML» (крышка и дно на всю ширину, боковины между ними) вокруг внутреннего корпуса ЛДСП 16 черный "
                      "(стяжка шурупами 4×30), фасады «Камень серый» внутри наружного корпуса с черной рамкой 10 мм, фрезерованные "
                      "диагональные линии, ручки СПА-1 96 мм черные, черный цоколь на опорах ФБ 482 или черные металлические опоры-рамы, "
                      "задние стенки ДВП на гвоздях; кровати с металлокаркасом."}


def write_catalog():
    frag = {"finishes": FINISHES, "profiles": {}, "collections": [COLLECTION], "models": MODELS}
    with open(os.path.join(HERE, "layn_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


if __name__ == "__main__":
    print(m001("layn-0-01", "П6.619.0.01", True))
    print(m001("layn-0-01-01", "П6.619.0.01-01", False))
    print(m004())
    print(m010())
    print(m012())
    for f in (m102, m111, m104, m112, m128, m211, m215, m216, m21601, m006):
        print(f())
    print(shelf("layn-0-08", "П6.619.0.08", 1670))
    print(shelf("layn-0-09", "П6.619.0.09", 1973))
    print(m126())
    print(m103())
    for did, code, name, w, sl in [("layn-1-18", "П6.619.1.18", "Кровать 1-08 «Лайн»", 876, 800),
                                   ("layn-1-17", "П6.619.1.17", "Кровать 1-09 «Лайн»", 976, 900),
                                   ("layn-1-13", "П6.619.1.13", "Кровать 1-12 «Лайн»", 1276, 1200),
                                   ("layn-1-14", "П6.619.1.14", "Кровать 2-14 «Лайн»", 1476, 1400),
                                   ("layn-1-05", "П6.619.1.05", "Кровать 2-16 «Лайн»", 1676, 1600),
                                   ("layn-1-15", "П6.619.1.15", "Кровать 2-18 «Лайн»", 1876, 1800),
                                   ("layn-1-16", "П6.619.1.16", "Кровать 2-20 «Лайн»", 2076, 2000)]:
        print(bed(did, code, name, w, sl))
    write_catalog()
