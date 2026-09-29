"""«Гресс» (Пинскдрев, П6.501): Дуб Сонома 325, cross-grain reeded strips («накладки») on the front edges.

Construction (read off the vector drawings of the instructions IS-P6-501-*: the PDFs are CAD exports to scale, so the
front / side views give every visible edge to ±1.5 mm — see notes/gress.md):
  * a 25 mm top and a 25 mm bottom run the full width and depth B; the bottom stands on grey «Валмакс» feet 20 high
    (90 × 56, 11 mm in from the ends); ЛДСП 16 sides stand between them, 3 mm in from the back (the ДВП back is nailed
    over the back edges) and 23 mm short of B at the front;
  * the fronts (doors, drawer fronts, the reeded strips) are 16 thick and lie over the sides' front edges: their faces
    are 7 mm behind the top's edge (B − 7);
  * «Накладка»: an 80 mm strip over each side's front edge (1 mm in from the side's face), horizontally reeded
    (grooves 3 mm every 10 mm, plain ends 8 mm); tall pieces carry two strips per side, butted at mid height. Doors hang
    on the strips with 180° hinges; drawers slide on rollers screwed to small partitions behind the strips;
  * drawer fronts are reeded like the strips (living room / hall) or plain (the TV units' and chests' drawers, as drawn);
  * backs ДВП 3 nailed on, split at the fixed shelves; handles: satin bar «скоба» 128 mm with square posts.
Coordinates: x from the left, y up from the floor, z from the wall (back) to the front; mm.

    /private/tmp/claude-501/venv/bin/python tools/casegoods/gen/gress.py
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "gress"
FEET_H = 20.0
TB = 25.0            # top / bottom thickness
LIP = 7.0            # the top stands this much in front of the fronts' faces
FT = 16.0            # fronts
REED_X = {"type": "fluted", "dir": "x", "pitch": 10, "depth": 1.5, "flute": "groove", "gap": 7, "margin": 8}
MODELS = []
CUTLISTS = {}


def r1(v):
    return round(v, 1)


class Design:
    def __init__(self, did, W, B, H):
        self.id, self.W, self.B, self.H = did, W, B, H
        self.parts, self.moves = [], []
        self.fz1 = B - LIP          # fronts' face
        self.fz0 = B - LIP - FT     # fronts' back = the carcass' front edge
        self.cz0 = 3.0              # carcass' back edge (the ДВП back is nailed behind it)

    def add(self, n=None, box=None, pid=None, **kw):
        p = {}
        if n is not None:
            p["n"] = str(n)
        if pid:
            p["id"] = pid
        p.update(kw)
        if box is not None:
            p["box"] = [r1(v) for v in box]
        self.parts.append(p)
        return p

    # ---------------------------------------------------------------- carcass
    def feet(self, xs=None, zs=None):
        """«Валмакс» feet 90 × 56 × 20 (grey plastic), 11 mm in from the ends, 1 / 3 mm in from the back / front."""
        W, B = self.W, self.B
        xs = xs if xs is not None else [11, W - 101]
        zs = zs if zs is not None else [1, B - 59]
        k = 0
        for x in xs:
            for z in zs:
                k += 1
                self.add(None, [x, 0, z, x + 90, FEET_H, z + 56], pid=f"foot-{k}", mat="feet", edge=2)

    def top(self, n, y0=None, x0=0, x1=None, z1=None):
        y0 = self.H - TB if y0 is None else y0
        return self.add(n, [x0, y0, 0, self.W if x1 is None else x1, y0 + TB, self.B if z1 is None else z1], grain="x")

    def bottom(self, n, y0=FEET_H):
        return self.add(n, [0, y0, 0, self.W, y0 + TB, self.B], grain="x")

    def sides(self, n1, n2, y0=FEET_H + TB, y1=None):
        y1 = self.H - TB if y1 is None else y1
        self.add(n1, [0, y0, self.cz0, 16, y1, self.fz0], grain="y")
        self.add(n2, [self.W - 16, y0, self.cz0, self.W, y1, self.fz0], grain="y")

    def vpanel(self, n, x0, y0, y1, pid=None, z1=None):
        return self.add(n, [x0, y0, self.cz0, x0 + 16, y1, self.fz0 if z1 is None else z1], pid=pid, grain="y")

    def shelf(self, n, x0, x1, y, pid=None, loose=False):
        """A fixed shelf (horizontal wall) between x0 and x1, top face at y + 16; loose shelves 1 mm shorter each side
        and 20 mm shallower."""
        if loose:
            return self.add(n, [x0 + 1, y, self.cz0 + 2, x1 - 1, y + 16, self.fz0 - 18], pid=pid, grain="x")
        return self.add(n, [x0, y, self.cz0, x1, y + 16, self.fz0], pid=pid, grain="x")

    def back(self, n, x0, y0, x1, y1, pid=None):
        return self.add(n, [x0, y0, 0, x1, y1, 3], pid=pid, kind="back")

    def strip(self, n, x0, y0, y1, pid=None, reed=True):
        p = self.add(n, [x0, y0, self.fz0, x0 + 80, y1, self.fz1], pid=pid, kind="front", grain="y")
        if reed:
            p["face"] = dict(REED_X)
        return p

    def strips(self, ns, y0, y1, split=True):
        """ns = (lower left, lower right, upper left, upper right) or (left, right)."""
        W = self.W
        if split and len(ns) == 4:
            ym = (y0 + y1) / 2
            self.strip(ns[0], 1, y0, ym - 0.5)
            self.strip(ns[1], W - 81, y0, ym - 0.5)
            self.strip(ns[2], 1, ym + 0.5, y1)
            self.strip(ns[3], W - 81, ym + 0.5, y1)
        else:
            self.strip(ns[0], 1, y0, y1)
            self.strip(ns[1], W - 81, y0, y1)

    # ---------------------------------------------------------------- fronts
    def front(self, n, x0, y0, x1, y1, pid=None, reed=False, grain="y"):
        p = self.add(n, [x0, y0, self.fz0, x1, y1, self.fz1], pid=pid, kind="front", grain=grain)
        if reed:
            p["face"] = dict(REED_X)
        return p

    def handle(self, pid, x, y, d="right", length=136, z=None):
        """Satin bar «скоба» 128 c-c (drawn 128 long), 10 × 8 bar on square posts, 29 mm from the face in all."""
        return self.add(None, None, pid=pid, kind="handle", model="bar", mat="metal", at=[r1(x), r1(y)], dir=d, d=length,
                        band=10, t=8, standoff=21, post=8, section="square", z=r1(self.fz1 if z is None else z))

    def door(self, n, x0, y0, x1, y1, hinge, hy=None, pid=None, hx=None, hdir="right", reed=False):
        pid = pid or f"{n}"
        self.front(n, x0, y0, x1, y1, pid=pid, reed=reed)
        ids = [pid]
        if hy is not None:
            hx = hx if hx is not None else (x0 + x1) / 2
            self.handle(f"h-{pid}", hx, hy, d=hdir)
            ids.append(f"h-{pid}")
        self.moves.append({"type": "door", "name": f"door_{pid}", "parts": ids, "hinge": hinge, "angle": 105})

    def drawer(self, tag, ns, fx0, fy0, fx1, fy1, ox0, ox1, by0, bh, depth=350, reed=True, hy=None, fn="14.1"):
        """Front ns[0] over [fx0, fx1] × [fy0, fy1]; box between the runners' faces ox0..ox1 (12.5 mm roller runners
        each side), sides bh high from by0 + 3 (standing on the ДВП bottom, which is nailed to the back and slides into
        the front's groove); the back between the sides."""
        n_f, n_sl, n_sr, n_bk, n_bt = ns
        z1 = self.fz0
        z0 = z1 - depth
        x0, x1 = ox0 + 12.5, ox1 - 12.5
        ids = []

        def a(n, box, suffix, **kw):
            pid = f"{n}-{tag}" if n else f"{suffix}-{tag}"
            self.add(n, box, pid=pid, **kw)
            ids.append(pid)

        a(n_f, [fx0, fy0, self.fz0, fx1, fy1, self.fz1], "front", kind="front", grain="x",
          **({"face": dict(REED_X)} if reed else {}))
        a(n_bt, [x0, by0, z0, x1, by0 + 3, z1 + 5], "bottom", kind="back")
        a(n_sl, [x0, by0 + 3, z0, x0 + 16, by0 + 3 + bh, z1], "sl", grain="z")
        a(n_sr, [x1 - 16, by0 + 3, z0, x1, by0 + 3 + bh, z1], "sr", grain="z")
        a(n_bk, [x0 + 16, by0 + 3, z0, x1 - 16, by0 + 3 + bh - 10, z0 + 16], "bk", grain="x")
        if hy is None:
            hy = (fy0 + fy1) / 2
        if hy is not False:
            self.handle(f"h-{tag}", (fx0 + fx1) / 2, hy)
            ids.append(f"h-{tag}")
        self.moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": ids, "travel": min(depth - 30, 320)})

    # ---------------------------------------------------------------- output
    def write(self, code, name, category, page, rows=None, is_pdf=None, note=None, mount=None, cut_note=None):
        path = dump(self.id, [self.W, self.B, self.H], self.parts, self.moves)
        m = {"id": self.id, "code": code, "name": name, "collection": SLUG, "category": category,
             "size": [self.W, self.B, self.H]}
        if is_pdf:
            m["is"] = is_pdf
        m["page"] = page
        if mount:
            m["mount"] = mount
        if note:
            m["note"] = note
        MODELS.append(m)
        if rows is not None:
            CUTLISTS[self.id] = (code, rows, cut_note)
        return path


def cutlist_rows(d, rows):
    """Rows (n, name, count) transcribed from the instruction's table; the sizes are those of the design's part with
    that number (read off the vector drawing, see the note)."""
    out = []
    for n, name, count in rows:
        have = [p for p in d.parts if p.get("n") == n and p.get("box")]
        size = None
        if have:
            b = have[0]["box"]
            size = sorted([r1(b[3] - b[0]), r1(b[4] - b[1]), r1(b[5] - b[2])], reverse=True)
        out.append({"n": n, "name": name, "size": size, "count": count})
    return out


# ================================================================================ 630 × 390 × 1920 family
ROWS_630 = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
            ("4", "Перегородка", 1), ("5", "Стенка горизонтальная", 1), ("6", "Стенка горизонтальная", 1),
            ("7", "Стенка горизонтальная", 2), ("8", "Стенка горизонтальная", 1), ("9", "Полка", 1),
            ("10", "Накладка", 1), ("11", "Накладка", 1), ("12", "Накладка", 1), ("13", "Накладка", 1),
            ("14.1", "Стенка передняя", 1), ("14.2", "Стенка боковая", 1), ("14.3", "Стенка боковая", 1),
            ("14.4", "Стенка задняя", 1), ("14.5", "Дно", 1)]


def tall630(did, top_wall, glass_shelf=False):
    """The carcass of 2.01 / 0.04 / 1.27: fixed shelves 7 at 664 and 1479, the drawer under wall 8 (top face at
    top_wall), its runners on the partitions 3 / 4 behind the strips."""
    d = Design(did, 630, 390, 1920)
    d.feet()
    d.bottom("6")
    d.top("5")
    d.sides("1", "2")
    d.shelf("7", 16, 614, 664, pid="7-1")
    d.shelf("7", 16, 614, 1479, pid="7-2")
    d.shelf("8", 16, 614, top_wall - 16)
    d.vpanel("3", 65, 45, top_wall - 16)
    d.vpanel("4", 549, 45, top_wall - 16)
    # strips: 10 upper left, 11 upper right, 12 lower left, 13 lower right (the instruction's scheme)
    d.strips(("12", "13", "10", "11"), 46, 1894)
    d.drawer("1", ("14.1", "14.2", "14.3", "14.4", "14.5"), 84, 47, 546, top_wall - 1, 81, 549, 58, 150)
    return d


def m2_01():
    """Шкаф 630 × 390 × 1920: open shelving over a reeded drawer (P6.501.2.01, drawn with the niche open)."""
    d = tall630("gress-2-01", 271)
    d.shelf("9", 16, 614, 1077, loose=True)
    d.back("17", 2, 45, 628, 672)
    d.back("16", 2, 672, 628, 1487)
    d.back("15", 2, 1487, 628, 1895)
    rows = ROWS_630 + [("15", "Стенка задняя", 1), ("16", "Стенка задняя", 1), ("17", "Стенка задняя", 1)]
    d.write("П6.501.2.01", "Шкаф «Гресс»", "living", 104, rows=rows, is_pdf="IS-P6-501-2-01-1.pdf", note="открытый")


def m1_27():
    """Шкаф для одежды 630 × 390 × 1920: one plain door over the reeded drawer (P6.501.1.27)."""
    d = tall630("gress-1-27", 262)
    d.shelf("9", 16, 614, 1077, loose=True)
    d.back("18", 2, 45, 628, 672)
    d.back("17", 2, 672, 628, 1487)
    d.back("16", 2, 1487, 628, 1895)
    d.door("15", 84, 264, 546, 1893, "left", hy=1078.5)
    rows = ROWS_630 + [("15", "Дверь", 1), ("16", "Стенка задняя", 1), ("17", "Стенка задняя", 1),
                       ("18", "Стенка задняя", 1)]
    d.write("П6.501.1.27", "Шкаф для одежды «Гресс»", "living", 104, rows=rows, is_pdf="IS-P6-501-1-27-1.pdf")


def m0_04():
    """Шкаф 630 × 390 × 1920 с витриной (P6.501.0.04): a glass door (bronze glass 4 mm the full height, two decor panels
    glued on it, the knob screwed through the glass with a bush), a glass shelf with a clip-on light."""
    d = tall630("gress-0-04", 262)
    d.add("9", [18, 1077, 25, 612, 1083, 345], kind="glass")
    d.add(None, [251, 1083, 26, 379, 1088, 40], pid="light", kind="light")
    d.back("18", 2, 45, 628, 672)
    d.back("17", 2, 672, 628, 1487)
    d.back("16", 2, 1487, 628, 1895)
    z0, z1 = d.fz0, d.fz1
    # the pane as a glazed front with a 1 mm rim (the engine tints glass only inside a glazed front)
    d.add("15", [84, 264, z0, 546, 1893, z0 + 5], pid="15", kind="front",
          glass={"frame": 1, "rebate": 0, "t": 4, "tint": "bronze"})
    d.add(None, [84, 264, z0 + 5, 546, 677, z1], pid="15-low", kind="front", grain="y")
    d.add(None, [84, 1481, z0 + 5, 546, 1893, z1], pid="15-up", kind="front", grain="y")
    d.add(None, None, pid="h-15", kind="handle", model="knob", mat="metal", at=[445.5, 1593.5], d=24, t=10,
          standoff=18, z=z1)
    d.moves.append({"type": "door", "name": "door_15", "parts": ["15", "15-low", "15-up", "h-15"], "hinge": "left",
                    "angle": 105})
    rows = ROWS_630[:8] + [("9", "Полка", 1)] + ROWS_630[9:] + [("15", "Дверь", 1), ("16", "Стенка задняя", 1),
                                                                ("17", "Стенка задняя", 1), ("18", "Стенка задняя", 1)]
    d.write("П6.501.0.04", "Шкаф «Гресс»", "living", 104, rows=rows, is_pdf="IS-P6-501-0-04.pdf", note="с подсветкой")


# ================================================================================ wardrobes, B 587
def rail(d, x0, x1, y):
    """Hanging rail (a metal oval tube on two holders, hardware): its centre at the section's mid-depth."""
    zc = (d.cz0 + d.fz0) / 2
    d.add(None, [x0 + 3, y - 10, zc - 10, x1 - 3, y + 10, zc + 10], pid=f"rail-{int(x0)}", kind="tube", mat="metal")


def batten(d, n, xc, y0, y1):
    """«Брусок»: a 50 × 16 batten behind the joint of two backs (they are nailed to it)."""
    d.add(n, [xc - 25, y0, d.cz0, xc + 25, y1, d.cz0 + 16], grain="y")


def m1_12(mirror=False):
    """Шкаф для одежды 3д 1562 × 587 × 1920 (P6.501.1.12; 1.13-01 = the middle door with a mirror): hanging section
    behind the left and middle doors (rail 984 between the left side and partition 3), shelves behind the right door, three
    reeded drawers below."""
    did = "gress-1-13-01" if mirror else "gress-1-12"
    d = Design(did, 1562, 587, 1920)
    W = d.W
    d.feet(xs=[11, 736, W - 101])
    d.bottom("8")
    d.top("7")
    d.sides("1", "2")
    d.vpanel("3", 1006, 45, 1895)
    d.shelf("9", 16, 1006, 246)
    d.shelf("11", 1022, W - 16, 246)
    # three identical drawers (one cut-list row ×3): equal openings 453.5 between the partitions 4 | 5, 5 | 3 and 3 | 6
    d.vpanel("4", 67, 45, 246)
    d.vpanel("5", 536.5, 45, 246)
    d.vpanel("6", 1475.5, 45, 246)
    d.shelf("10", 1022, W - 16, 664, pid="10-1")
    d.shelf("10", 1022, W - 16, 1479, pid="10-2")
    d.shelf("12", 1022, W - 16, 1077, loose=True)
    rail(d, 16, 1006, 1780)
    # backs: two over the hanging section (joint on the batten 21), three over the shelves (joints on the shelves 10)
    d.back("22", 2, 45, 511, 1895)
    d.back("23", 511, 45, 1014, 1895)
    batten(d, "21", 511, 262, 1895)
    d.back("26", 1014, 45, W - 2, 672)
    d.back("25", 1014, 672, W - 2, 1487)
    d.back("24", 1014, 1487, W - 2, 1895)
    # strips: 13 upper left, 15 lower left, 14 upper right, 16 lower right
    d.strips(("15", "16", "13", "14"), 46, 1894)
    dn = ("17.1", "17.2", "17.3", "17.4", "17.5")
    d.drawer("l", dn, 84, 47, 547, 262, 83, 536.5, 58, 150, depth=500, hy=155)
    d.drawer("m", dn, 550, 47, 1013, 262, 552.5, 1006, 58, 150, depth=500, hy=155)
    d.drawer("r", dn, 1016, 47, 1479, 262, 1022, 1475.5, 58, 150, depth=500, hy=155)
    d.door("18", 83, 266, 547, 1894, "left", hy=1079.5)
    if mirror:
        d.front("20", 550, 266, 1012, 1894, pid="20")
        d.add(None, [581, 299, d.fz1, 983, 1882, d.fz1 + 4], pid="20-mirror", kind="mirror")
        d.moves.append({"type": "door", "name": "door_20", "parts": ["20", "20-mirror"], "hinge": "right", "angle": 105})
        d.door("19", 1017, 266, 1479, 1894, "right", hy=1079.5)
    else:
        d.door("19", 550, 266, 1012, 1894, "right", hy=1079.5, pid="19-m")
        d.door("19", 1017, 266, 1479, 1894, "right", hy=1079.5, pid="19-r")
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
            ("4", "Перегородка", 1), ("5", "Перегородка", 1), ("6", "Перегородка", 1),
            ("7", "Стенка горизонтальная", 1), ("8", "Стенка горизонтальная", 1), ("9", "Стенка горизонтальная", 1),
            ("10", "Стенка горизонтальная", 2), ("11", "Стенка горизонтальная", 1), ("12", "Полка", 1),
            ("13", "Накладка", 1), ("14", "Накладка", 1), ("15", "Накладка", 1), ("16", "Накладка", 1),
            ("17.1", "Стенка передняя", 3), ("17.2", "Стенка боковая", 3), ("17.3", "Стенка боковая", 3),
            ("17.4", "Стенка задняя", 3), ("17.5", "Дно", 3), ("18", "Дверь", 1)]
    rows += [("19", "Дверь", 1), ("20", "Дверь", 1)] if mirror else [("19", "Дверь", 2)]
    rows += [("21", "Брусок", 1)] + [(str(k), "Стенка задняя", 1) for k in range(22, 27)]
    if mirror:
        d.write("П6.501.1.13-01", "Шкаф для одежды 3д «Гресс»", "bedroom", 104, rows=rows,
                is_pdf="IS-P6-501-1-13-01-1.pdf", note="с зеркалом")
    else:
        d.write("П6.501.1.12", "Шкаф для одежды 3д «Гресс»", "bedroom", 104, rows=rows, is_pdf="IS-P6-501-1-12.pdf")


def wardrobe930(did, H):
    """The 930-wide two-door wardrobes 1.14 (H 1920) and 3.01 (H 2120): hanging section over one wide drawer."""
    d = Design(did, 930, 587, H)
    W = d.W
    d.feet()
    d.sides("1", "2")
    d.vpanel("3", 67, 45, 246)
    d.vpanel("4", 847, 45, 246)
    return d


def m1_14():
    """Шкаф для одежды 2д 930 × 587 × 1920 (P6.501.1.14): hanging rail 890, one wide drawer with two handles."""
    d = wardrobe930("gress-1-14", 1920)
    W = d.W
    d.top("5")
    d.bottom("6")
    d.shelf("7", 16, W - 16, 246)
    rail(d, 16, W - 16, 1780)
    d.back("16", 2, 45, 465, 1895, pid="16-1")
    d.back("16", 465, 45, W - 2, 1895, pid="16-2")
    batten(d, "15", 465, 262, 1895)
    d.strips(("10", "11", "8", "9"), 46, 1894)
    d.drawer("1", ("12.1", "12.2", "12.3", "12.4", "12.5"), 83, 47, 847, 262, 83, 847, 58, 150, depth=500, hy=False)
    d.handle("h-1a", 241, 155)
    d.handle("h-1b", 689, 155)
    d.moves[-1]["parts"] += ["h-1a", "h-1b"]
    d.door("13", 83, 265, 463, 1894, "left", hy=1079.5, hx=273)
    d.door("14", 466, 265, 847, 1894, "right", hy=1079.5, hx=656)
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
            ("4", "Перегородка", 1), ("5", "Стенка горизонтальная", 1), ("6", "Стенка горизонтальная", 1),
            ("7", "Стенка горизонтальная", 1), ("8", "Накладка", 1), ("9", "Накладка", 1), ("10", "Накладка", 1),
            ("11", "Накладка", 1), ("12.1", "Стенка передняя", 1), ("12.2", "Стенка боковая", 1),
            ("12.3", "Стенка боковая", 1), ("12.4", "Стенка задняя", 1), ("12.5", "Дно", 1), ("13", "Дверь", 1),
            ("14", "Дверь", 1), ("15", "Брусок", 1), ("16", "Стенка задняя", 2)]
    d.write("П6.501.1.14", "Шкаф для одежды 2д «Гресс»", "bedroom", 104, rows=rows, is_pdf="IS-P6-501-1-14.pdf")


def m3_01():
    """Шкаф для одежды 2д 930 × 587 × 2120 (P6.501.3.01, hall): hat shelf 7 under the top, rail under it, backs 16 (above
    the hat shelf), 17 × 2 (hanging section, joint on the batten 9) and 18 (behind the drawer)."""
    d = wardrobe930("gress-3-01", 2120)
    W, H = d.W, d.H
    d.top("5")
    d.bottom("6")
    d.shelf("8", 16, W - 16, 246)
    d.shelf("7", 16, W - 16, 1745)
    rail(d, 16, W - 16, 1690)
    d.back("18", 2, 45, W - 2, 254)
    d.back("17", 2, 254, 465, 1753, pid="17-1")
    d.back("17", 465, 254, W - 2, 1753, pid="17-2")
    d.back("16", 2, 1753, W - 2, H - 25)
    batten(d, "9", 465, 262, 1745)
    d.strips(("12", "13", "10", "11"), 46, H - 26)
    d.drawer("1", ("15.1", "15.2", "15.3", "15.4", "15.5"), 83, 47, 847, 262, 83, 847, 58, 150, depth=500, hy=False)
    d.handle("h-1a", 239.5, 154.5)
    d.handle("h-1b", 688.5, 154.5)
    d.moves[-1]["parts"] += ["h-1a", "h-1b"]
    d.door("14", 83, 265, 463, H - 26, "left", hy=1180, hx=273, pid="14-l")
    d.door("14", 466, 265, 847, H - 26, "right", hy=1180, hx=656, pid="14-r")
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
            ("4", "Перегородка", 1), ("5", "Стенка горизонтальная", 1), ("6", "Стенка горизонтальная", 1),
            ("7", "Стенка горизонтальная", 1), ("8", "Стенка горизонтальная", 1), ("9", "Брусок", 1),
            ("10", "Накладка", 1), ("11", "Накладка", 1), ("12", "Накладка", 1), ("13", "Накладка", 1),
            ("14", "Дверь", 2), ("15.1", "Стенка передняя", 1), ("15.2", "Стенка боковая", 1),
            ("15.3", "Стенка боковая", 1), ("15.4", "Стенка задняя", 1), ("15.5", "Дно", 1),
            ("16", "Стенка задняя", 1), ("17", "Стенка задняя", 2), ("18", "Стенка задняя", 1)]
    d.write("П6.501.3.01", "Шкаф для одежды 2д «Гресс»", "hall", 104, rows=rows, is_pdf="IS-P6-501-3-01-1.pdf")


def mezzanine(did, W):
    """Секция антресольная, 480 high, stands on a wardrobe of the same width: sides from its underside, a 16 mm bottom
    between them, the 25 mm top, strips the full height of the sides, doors 1..453 above the underside."""
    d = Design(did, W, 587, 480)
    d.add("1", [0, 0, d.cz0, 16, 455, d.fz0], grain="y")
    d.add("2", [W - 16, 0, d.cz0, W, 455, d.fz0], grain="y")
    d.top("4", y0=455)
    d.add("5", [16, 0, d.cz0, W - 16, 16, d.fz0], grain="x")
    return d


def m1_21():
    """Секция антресольная 1562 × 587 × 480 (P6.501.1.21): three doors like the 3-door wardrobe, partition 3 over the
    wardrobe's partition."""
    d = mezzanine("gress-1-21", 1562)
    W = d.W
    d.vpanel("3", 1006, 16, 455)
    d.back("10", 2, 0, 1014, 455)
    d.back("11", 1014, 0, W - 2, 455)
    d.strip("6", 1, 0, 454)
    d.strip("7", W - 81, 0, 454)
    d.door("8", 83, 1, 545, 453, "left", hy=108.5)
    d.door("9", 549, 1, 1012, 453, "right", hy=108.5, pid="9-m")
    d.door("9", 1016, 1, 1478, 453, "right", hy=108.5, pid="9-r")
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
            ("4", "Стенка горизонтальная", 1), ("5", "Стенка горизонтальная", 1), ("6", "Накладка", 1),
            ("7", "Накладка", 1), ("8", "Дверь", 1), ("9", "Дверь", 2), ("10", "Стенка задняя", 1),
            ("11", "Стенка задняя", 1)]
    d.write("П6.501.1.21", "Секция антресольная «Гресс»", "bedroom", 104, rows=rows, is_pdf="IS-P6-501-1-21-1.pdf")


def m1_34():
    """Секция антресольная 930 × 587 × 480 (no instruction; by the catalogue cut-out p. 104 and 1.21): two doors like
    the 2-door wardrobe."""
    d = mezzanine("gress-1-34", 930)
    W = d.W
    d.back(None, 2, 0, W - 2, 455, pid="back")
    d.strip(None, 1, 0, 454, pid="strip-l")
    d.strip(None, W - 81, 0, 454, pid="strip-r")
    d.door(None, 83, 1, 463, 453, "left", hy=108.5, hx=273, pid="door-l")
    d.door(None, 466, 1, 847, 453, "right", hy=108.5, hx=656, pid="door-r")
    d.write("П6.501.1.34", "Секция антресольная «Гресс»", "bedroom", 104, note="по каталогу (как 1.21)")


# ================================================================================ living room chests
def low(did, W, B, H, feet_x=None):
    d = Design(did, W, B, H)
    d.feet(xs=feet_x)
    return d


def m0_02():
    """Тумба ТВ 1400 × 550 × 510 (P6.501.0.02): doors left and right, the middle: an open niche over a reeded drawer."""
    d = low("gress-0-02", 1400, 550, 510, feet_x=[11, 655, 1289])
    W, H = d.W, d.H
    d.bottom("6")
    d.top("5")
    d.sides("1", "2")
    d.vpanel("3", 452, 45, H - 25)
    d.vpanel("4", 932, 45, H - 25)
    d.shelf("7", 468, 932, 245)
    d.strip("8", 1, 46, H - 26, pid="8-l")
    d.strip("8", W - 81, 46, H - 26, pid="8-r")
    for k in range(3):     # three equal sheets, the joints on the partitions' back edges
        d.back("12", 2 + k * (W - 4) / 3, 45, 2 + (k + 1) * (W - 4) / 3, H - 25, pid=f"12-{k + 1}")
    d.door("9", 84, 46, 468, 482, "left", hy=375, hx=275)
    d.door("10", 934, 46, 1316, 482, "right", hy=375, hx=1125)
    d.drawer("1", ("11.1", "11.2", "11.3", "11.4", "11.5"), 469, 46, 931, 261, 468, 932, 58, 150, hy=153)
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
            ("4", "Перегородка", 1), ("5", "Крышка", 1), ("6", "Стенка горизонтальная", 1),
            ("7", "Стенка горизонтальная", 1), ("8", "Накладка", 2), ("9", "Дверь", 1), ("10", "Дверь", 1),
            ("11.1", "Стенка передняя", 1), ("11.2", "Стенка боковая", 1), ("11.3", "Стенка боковая", 1),
            ("11.4", "Стенка задняя", 1), ("11.5", "Дно", 1), ("12", "Стенка задняя", 3)]
    d.write("П6.501.0.02", "Тумба «Гресс»", "living", 104, rows=rows, is_pdf="IS-P6-501-0-02-2.pdf", note="ТВ")


def glass_door(d, n, x0, x1, y0, y1, g0, g1, hinge, hx, hy):
    """A vitrine door as in 0.04: bronze glass 4 mm the full height with two decor panels glued on (below g0 and above
    g1); the handle screwed through the upper panel and the glass."""
    z0, z1 = d.fz0, d.fz1
    d.add(n, [x0, y0, z0, x1, y1, z0 + 5], pid=n, kind="front", glass={"frame": 1, "rebate": 0, "t": 4, "tint": "bronze"})
    d.add(None, [x0, y0, z0 + 5, x1, g0, z1], pid=f"{n}-low", kind="front", grain="y")
    d.add(None, [x0, g1, z0 + 5, x1, y1, z1], pid=f"{n}-up", kind="front", grain="y")
    d.handle(f"h-{n}", hx, hy)
    d.moves.append({"type": "door", "name": f"door_{n}", "parts": [n, f"{n}-low", f"{n}-up", f"h-{n}"], "hinge": hinge,
                    "angle": 105})


def m0_05():
    """Тумба 1400 × 390 × 1180 с подсветкой (P6.501.0.05): glazed doors left and right (glass shelves with lights), the
    middle: a door over two drawers and a reeded bottom drawer."""
    d = low("gress-0-05", 1400, 390, 1180, feet_x=[11, 655, 1289])
    W, H = d.W, d.H
    d.bottom("6")
    d.top("5")
    d.sides("1", "2")
    d.vpanel("3", 452, 45, H - 25)
    d.vpanel("4", 932, 45, H - 25)
    for k, (x0, x1) in enumerate(((16, 452), (948, W - 16))):
        n = "8" if k == 0 else "9"
        d.shelf(n, x0, x1, 244, pid=f"{n}-1")
        d.shelf(n, x0, x1, 923, pid=f"{n}-2")
        d.add("10", [x0 + 2, 596, 25, x1 - 2, 602, 345], pid=f"10-{k + 1}", kind="glass")
        d.add(None, [(x0 + x1) / 2 - 64, 602, 26, (x0 + x1) / 2 + 64, 607, 40], pid=f"light-{k + 1}", kind="light")
    d.shelf("7", 468, 932, 682)
    d.back("17", 2, 45, 460, H - 25, pid="17-1")
    d.back("18", 460, 45, 940, H - 25)
    d.back("17", 940, 45, W - 2, H - 25, pid="17-2")
    d.strip("11", 1, 46, H - 26, pid="11-l")
    d.strip("11", W - 81, 46, H - 26, pid="11-r")
    glass_door(d, "12", 84, 468, 46, 1153, 260, 939, "left", 275.5, 1046)
    glass_door(d, "13", 934, 1316, 46, 1153, 260, 939, "right", 1125, 1046)
    d.door("16", 469, 700, 931, 1153, "left", hy=1046)
    d.drawer("b", ("14.1", "14.2", "14.3", "14.4", "14.5"), 469, 46, 931, 260, 468, 932, 58, 150, hy=153)
    dn = ("15.1", "15.2", "15.3", "15.4", "15.5")
    d.drawer("m", dn, 469, 264, 931, 478, 468, 932, 276, 150, reed=False, hy=371)
    d.drawer("t", dn, 469, 482, 931, 697, 468, 932, 494, 150, reed=False, hy=590)
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
            ("4", "Перегородка", 1), ("5", "Крышка", 1), ("6", "Стенка горизонтальная", 1),
            ("7", "Стенка горизонтальная", 1), ("8", "Стенка горизонтальная", 2), ("9", "Стенка горизонтальная", 2),
            ("10", "Полка", 2), ("11", "Накладка", 2), ("12", "Дверь", 1), ("13", "Дверь", 1),
            ("14.1", "Стенка передняя", 1), ("14.2", "Стенка боковая", 1), ("14.3", "Стенка боковая", 1),
            ("14.4", "Стенка задняя", 1), ("14.5", "Дно", 1), ("15.1", "Стенка передняя", 2),
            ("15.2", "Стенка боковая", 2), ("15.3", "Стенка боковая", 2), ("15.4", "Стенка задняя", 2),
            ("15.5", "Дно", 2), ("16", "Дверь", 1), ("17", "Стенка задняя", 2), ("18", "Стенка задняя", 1)]
    d.write("П6.501.0.05", "Тумба «Гресс»", "living", 104, rows=rows, is_pdf="IS-P6-501-0-05-1.pdf",
            note="с подсветкой")


def m0_17():
    """Тумба 1562 × 390 × 470 (P6.501.0.17, TV): three open niches over three plain drawers. The drawer walls 9 / 11 / 10
    carry the niche partitions 3 / 4; the drawers run on the partitions 5 / 6 behind the strips and on the sides of
    the middle drawer's opening (runner blocks, not listed)."""
    d = low("gress-0-17", 1562, 390, 470, feet_x=[11, 736, 1461])
    W, H = d.W, d.H
    d.bottom("8")
    d.top("7")
    d.sides("1", "2")
    d.shelf("9", 16, 548, 245)
    d.shelf("11", 548, 1014, 245)
    d.shelf("10", 1014, W - 16, 245)
    d.vpanel("3", 540, 261, H - 25)
    d.vpanel("4", 1006, 261, H - 25)
    d.vpanel("5", 65, 45, 245)
    d.vpanel("6", W - 81, 45, 245)
    d.strip("12", 1, 46, H - 26)
    d.strip("13", W - 81, 46, H - 26)
    d.back("15", 2, 45, W - 2, H - 25)
    dn = ("14.1", "14.2", "14.3", "14.4", "14.5")
    d.drawer("l", dn, 85, 47, 546, 260, 81, 551, 58, 150, reed=False, hy=159)
    d.drawer("m", dn, 550, 47, 1012, 260, 546, 1016, 58, 150, reed=False, hy=159)
    d.drawer("r", dn, 1016, 47, 1477, 260, 1011, 1481, 58, 150, reed=False, hy=159)
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
            ("4", "Перегородка", 1), ("5", "Перегородка", 1), ("6", "Перегородка", 1), ("7", "Крышка", 1),
            ("8", "Стенка горизонтальная", 1), ("9", "Стенка горизонтальная", 1), ("10", "Стенка горизонтальная", 1),
            ("11", "Стенка горизонтальная", 1), ("12", "Накладка", 1), ("13", "Накладка", 1),
            ("14.1", "Стенка передняя", 3), ("14.2", "Стенка боковая", 3), ("14.3", "Стенка боковая", 3),
            ("14.4", "Стенка задняя", 3), ("14.5", "Дно", 3), ("15", "Стенка задняя", 1)]
    d.write("П6.501.0.17", "Тумба «Гресс»", "living", 104, rows=rows, is_pdf="IS-P6-501-0-17.pdf", note="ТВ",
            cut_note="parts 5 / 6 have the codes of 3 / 4 in the table (6.501.0.17.03 / .04); sizes here as built")


def m0_25():
    """Тумба 1400 × 390 × 942 (P6.501.0.25): doors left and right with a fixed shelf 7 behind each, four drawers in the
    middle, the top one reeded (10), three plain (11)."""
    d = low("gress-0-25", 1400, 390, 942, feet_x=[11, 655, 1289])
    W, H = d.W, d.H
    d.bottom("6")
    d.top("5")
    d.sides("1", "2")
    d.vpanel("3", 452, 45, H - 25)
    d.vpanel("4", 932, 45, H - 25)
    d.shelf("7", 16, 452, 470, pid="7-1")
    d.shelf("7", 948, W - 16, 470, pid="7-2")
    for k in range(3):     # three equal sheets, the joints on the partitions' back edges
        d.back("14", 2 + k * (W - 4) / 3, 45, 2 + (k + 1) * (W - 4) / 3, H - 25, pid=f"14-{k + 1}")
    d.strip("12", 1, 46, H - 26)
    d.strip("13", W - 81, 46, H - 26)
    d.door("8", 84, 47, 468, 915, "left", hy=808.5, hx=275.5)
    d.door("9", 934, 47, 1316, 915, "right", hy=808.5, hx=1125)
    dn = ("11.1", "11.2", "11.3", "11.4", "11.5")
    d.drawer("1", dn, 469, 47, 931, 262, 468, 932, 58, 150, reed=False, hy=154.5)
    d.drawer("2", dn, 469, 266, 931, 480, 468, 932, 277, 150, reed=False, hy=373)
    d.drawer("3", dn, 469, 484, 931, 698, 468, 932, 495, 150, reed=False, hy=590)
    d.drawer("4", ("10.1", "10.2", "10.3", "10.4", "10.5"), 469, 702, 931, 915, 468, 932, 713, 150, hy=808.5)
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
            ("4", "Перегородка", 1), ("5", "Крышка", 1), ("6", "Стенка горизонтальная", 1),
            ("7", "Стенка горизонтальная", 2), ("8", "Дверь", 1), ("9", "Дверь", 1),
            ("10.1", "Стенка передняя", 1), ("10.2", "Стенка боковая", 1), ("10.3", "Стенка боковая", 1),
            ("10.4", "Стенка задняя", 1), ("10.5", "Дно", 1), ("11.1", "Стенка передняя", 3),
            ("11.2", "Стенка боковая", 3), ("11.3", "Стенка боковая", 3), ("11.4", "Стенка задняя", 3),
            ("11.5", "Дно", 3), ("12", "Накладка", 1), ("13", "Накладка", 1), ("14", "Стенка задняя", 3)]
    d.write("П6.501.0.25", "Тумба «Гресс»", "living", 104, rows=rows, is_pdf="IS-P6-501-0-25-1.pdf",
            cut_note="row 7 reads 1 in the table, the scheme labels a shelf 7 in both side sections: built 2")


# ================================================================================ bedroom / hall chests
def chest(did, W, H, rows_top=None):
    d = Design(did, W, 390, H)
    d.feet()
    return d


def m1_10():
    """Тумба прикроватная 630 × 390 × 288 (P6.501.1.10): one plain drawer between the strips."""
    d = chest("gress-1-10", 630, 288)
    d.bottom("6")
    d.top("5")
    d.sides("1", "2")
    d.vpanel("3", 65, 45, 263)
    d.vpanel("4", 549, 45, 263)
    d.strip("7", 1, 46, 262, pid="7-l")
    d.strip("7", 549, 46, 262, pid="7-r")
    d.back("9", 2, 45, 628, 263)
    d.drawer("1", ("8.1", "8.2", "8.3", "8.4", "8.5"), 84, 47, 546, 261, 81, 549, 58, 150, reed=False, hy=154.5)
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
            ("4", "Перегородка", 1), ("5", "Крышка", 1), ("6", "Стенка горизонтальная", 1), ("7", "Накладка", 2),
            ("8.1", "Стенка передняя", 1), ("8.2", "Стенка боковая", 1), ("8.3", "Стенка боковая", 1),
            ("8.4", "Стенка задняя", 1), ("8.5", "Дно", 1), ("9", "Стенка задняя", 1)]
    d.write("П6.501.1.10", "Тумба прикроватная «Гресс»", "bedroom", 104, rows=rows, is_pdf="IS-P6-501-1-10.pdf")


def m1_11():
    """Комод 930 × 390 × 942 (P6.501.1.11): four wide plain drawers with two handles each; the bottom one (9) has its own
    front and bottom codes, the other three (10) are identical; backs 11 × 2 joined by a profile 870."""
    d = chest("gress-1-11", 930, 942)
    W, H = d.W, d.H
    d.bottom("6")
    d.top("5")
    d.sides("1", "2")
    d.vpanel("3", 67, 45, H - 25)
    d.vpanel("4", 847, 45, H - 25)
    d.strip("7", 1, 46, H - 26)
    d.strip("8", W - 81, 46, H - 26)
    d.back("11", 2, 45, 465, H - 25, pid="11-1")
    d.back("11", 465, 45, W - 2, H - 25, pid="11-2")
    fr = [(47, 262), (265, 479), (483, 697), (701, 915)]
    for k, (y0, y1) in enumerate(fr):
        ns = ("9.1", "9.2", "9.3", "9.4", "9.5") if k == 0 else ("10.1", "10.2", "10.3", "10.4", "10.5")
        tag = str(k + 1)
        d.drawer(tag, ns, 85, y0, 845, y1, 83, 847, y0 + 11, 150, reed=False, hy=False)
        hy = (y0 + y1) / 2 + 0.5
        d.handle(f"h-{tag}a", 241, hy)
        d.handle(f"h-{tag}b", 689, hy)
        d.moves[-1]["parts"] += [f"h-{tag}a", f"h-{tag}b"]
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
            ("4", "Перегородка", 1), ("5", "Крышка", 1), ("6", "Стенка горизонтальная", 1), ("7", "Накладка", 1),
            ("8", "Накладка", 1), ("9.1", "Стенка передняя", 1), ("9.2", "Стенка боковая", 1),
            ("9.3", "Стенка боковая", 1), ("9.4", "Стенка задняя", 1), ("9.5", "Дно", 1),
            ("10.1", "Стенка передняя", 3), ("10.2", "Стенка боковая", 3), ("10.3", "Стенка боковая", 3),
            ("10.4", "Стенка задняя", 3), ("10.5", "Дно", 3), ("11", "Стенка задняя", 2)]
    d.write("П6.501.1.11", "Комод «Гресс»", "bedroom", 104, rows=rows, is_pdf="IS-P6-501-1-11.pdf",
            cut_note="the table labels the rows of drawer 10 «9.2 … 9.5» (a misprint): written 10.2 … 10.5")


def m1_26():
    """Комод 630 × 390 × 1180 (P6.501.1.26): a reeded bottom drawer (8) under four plain ones (9); strips 7 / 7.1; backs
    10 × 2 joined upright by a profile 1108."""
    d = chest("gress-1-26", 630, 1180)
    W, H = d.W, d.H
    d.bottom("6")
    d.top("5")
    d.sides("1", "2")
    d.vpanel("3", 65, 45, H - 25)
    d.vpanel("4", 549, 45, H - 25)
    d.strip("7", 1, 46, H - 26)
    d.strip("7.1", W - 81, 46, H - 26)
    d.back("10", 2, 45, 315, H - 25, pid="10-1")
    d.back("10", 315, 45, W - 2, H - 25, pid="10-2")
    d.drawer("1", ("8.1", "8.2", "8.3", "8.4", "8.5"), 84, 47, 546, 281, 81, 549, 58, 170, hy=163)
    for k, (y0, y1, hy) in enumerate(((284, 498, 391.5), (503, 716, 609.5), (720, 934, 827), (938, 1152, 1045.5))):
        d.drawer(str(k + 2), ("9.1", "9.2", "9.3", "9.4", "9.5"), 84, y0, 546, y1, 81, 549, y0 + 11, 150, reed=False,
                 hy=hy)
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
            ("4", "Перегородка", 1), ("5", "Крышка", 1), ("6", "Стенка горизонтальная", 1), ("7", "Накладка", 1),
            ("7.1", "Накладка", 1), ("8.1", "Стенка передняя", 1), ("8.2", "Стенка боковая", 1),
            ("8.3", "Стенка боковая", 1), ("8.4", "Стенка задняя", 1), ("8.5", "Дно", 1),
            ("9.1", "Стенка передняя", 4), ("9.2", "Стенка боковая", 4), ("9.3", "Стенка боковая", 4),
            ("9.4", "Стенка задняя", 4), ("9.5", "Дно", 4), ("10", "Стенка задняя", 2)]
    d.write("П6.501.1.26", "Комод «Гресс»", "bedroom", 104, rows=rows, is_pdf="IS-P6-501-1-26-1.pdf")


def m3_04():
    """Тумба 900 × 390 × 510 (P6.501.3.04, hall bench): two doors, a shelf 5 behind them; handles «С-25» 96."""
    d = chest("gress-3-04", 900, 510)
    W, H = d.W, d.H
    d.bottom("4")
    d.top("3")
    d.sides("1", "2")
    d.shelf("5", 16, W - 16, 270)
    d.strip("6", 1, 46, H - 26, pid="6-l")
    d.strip("6", W - 81, 46, H - 26, pid="6-r")
    d.back("9", 2, 45, W - 2, H - 25)
    d.door("7", 84, 47, 449, 483, "left", hy=376, hx=274)
    d.door("8", 451, 47, 816, 483, "right", hy=376, hx=625.5)
    for p in d.parts:
        if p.get("kind") == "handle":
            p["d"] = 104
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Крышка", 1), ("4", "Дно", 1),
            ("5", "Стенка горизонтальная", 1), ("6", "Накладка", 2), ("7", "Дверь", 1), ("8", "Дверь", 1),
            ("9", "Стенка задняя", 1)]
    d.write("П6.501.3.04", "Тумба «Гресс»", "hall", 104, rows=rows, is_pdf="IS-P6-501-3-04.pdf")


def tilt_box(d, tag, ns, x0, x1, y0, y1, hy, extra=None):
    """A tilting shoe box: front ns[0] over [x0, x1] × [y0, y1], two triangular sides, a bottom and two shoe rests
    (ns = front, side, side, rest ×2, bottom); it tips forward about the front's lower edge."""
    f, sl, sr, rest, bt = ns
    z1 = d.fz0
    depth = 190
    zb = z1 - depth
    bx0, bx1 = x0 + 4, x1 - 4
    ids = []

    def a(n, box, pid, **kw):
        d.add(n, box, pid=pid, **kw)
        ids.append(pid)

    a(f, [x0, y0, d.fz0, x1, y1, d.fz1], f"{f}-{tag}", kind="front", grain="x")
    tri = f"M {z1} {y0 + 3} L {z1} {y1 - 10} L {zb} {y0 + 3} Z"
    a(sl, [bx0, y0 + 3, zb, bx0 + 16, y1 - 10, z1], f"{sl}-{tag}", shape="path", outline=tri, grain="z")
    a(sr, [bx1 - 16, y0 + 3, zb, bx1, y1 - 10, z1], f"{sr}-{tag}", shape="path", outline=tri, grain="z")
    a(bt, [bx0 + 16, y0 + 3, zb + 5, bx1 - 16, y0 + 19, z1], f"{bt}-{tag}", grain="x")
    h = y1 - y0 - 13
    for k, fr in enumerate((0.35, 0.7)):
        yy = y0 + 3 + h * fr
        zz = z1 - depth * (1 - 0.7) + 6       # shoe rests of one size (one cut-list row)
        a(rest, [bx0 + 16, yy, zz - 2, bx1 - 16, yy + 16, z1 - 16], f"{rest}-{tag}-{k + 1}", grain="x")
    if extra:
        a(extra, [bx0 + 16, y0 + 19, z1 - 16, bx1 - 16, y1 - 12, z1], f"{extra}-{tag}", grain="x")
    d.handle(f"h-{tag}", (x0 + x1) / 2, hy)
    ids.append(f"h-{tag}")
    d.moves.append({"type": "flap", "name": f"shoes_{tag}", "parts": ids, "hinge": "bottom", "angle": 25})


def m3_02():
    """Тумба для обуви 820 × 290 × 1073 (P6.501.3.02, hung to the wall): two tilting shoe boxes (10 upper, 11 lower)
    under a drawer 9; 12 = the lower box's inner front (the tables list it on its own); the partitions 3 / 4 carry the
    drawer runners and the boxes' pivots."""
    d = Design("gress-3-02", 820, 290, 1073)
    W, H = d.W, d.H
    d.feet()
    d.bottom("6")
    d.top("5")
    d.sides("1", "2")
    d.vpanel("3", 65, 45, H - 25)
    d.vpanel("4", W - 81, 45, H - 25)
    d.strip("7", 1, 46, H - 26)
    d.strip("8", W - 81, 46, H - 26)
    d.back("13", 2, 45, W - 2, 866)
    d.back("14", 2, 866, W - 2, H - 25)
    tilt_box(d, "low", ("11.1", "10.2", "10.3", "10.4", "10.5"), 84, 736, 49, 455, 350, extra="12")
    tilt_box(d, "up", ("10.1", "10.2", "10.3", "10.4", "10.5"), 84, 736, 459, 865, 761)
    d.drawer("1", ("9.1", "9.2", "9.3", "9.4", "9.5"), 84, 870, 736, 1045, 81, 739, 880, 110, depth=250, reed=False,
             hy=953)
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
            ("4", "Перегородка", 1), ("5", "Стенка горизонтальная", 1), ("6", "Стенка горизонтальная", 1),
            ("7", "Накладка", 1), ("8", "Накладка", 1), ("9.1", "Стенка передняя", 1), ("9.2", "Стенка боковая", 1),
            ("9.3", "Стенка боковая", 1), ("9.4", "Стенка задняя", 1), ("9.5", "Дно", 1),
            ("10.1", "Стенка передняя", 1), ("10.2", "Стенка боковая", 2), ("10.3", "Стенка боковая", 2),
            ("10.4", "Стенка", 4), ("10.5", "Дно", 2), ("11.1", "Стенка передняя", 1), ("12", "Стенка передняя", 1),
            ("13", "Стенка задняя", 1), ("14", "Стенка задняя", 1)]
    d.write("П6.501.3.02", "Тумба для обуви «Гресс»", "hall", 104, rows=rows, is_pdf="IS-P6-501-3-02.pdf",
            cut_note="the table lists the two tilting boxes 10 and 11 «(каждый)» with the shared rows 10.2–10.5 "
                     "(written here ×2, 10.4 ×4) and the fronts 10.1 / 11.1")


# ================================================================================ wall pieces
def m_shelf(did, code, W, is_pdf, page=104):
    """Полка 930 / 1390 × 220 × 300 (P6.501.0.20 / 0.19): a back board 1 with a reeded strip 3 over each end and a
    25 mm shelf 2 between the strips 50 mm above its lower edge; hung on two brackets «079»."""
    d = Design(did, W, 220, 300)
    d.add("1", [0, 0, 0, W, 300, 16], grain="x")
    for k, x in enumerate((0, W - 80)):
        p = d.add("3", [x, 0, 16, x + 80, 300, 32], pid=f"3-{k + 1}", kind="front", grain="y")
        p["face"] = dict(REED_X)
    d.add("2", [80, 50, 16, W - 80, 75, 220], grain="x")
    rows = [("1", "Стенка вертикальная", 1), ("2", "Стенка горизонтальная", 1), ("3", "Накладка", 2)]
    d.write(code, "Полка «Гресс»", "living", page, rows=rows, is_pdf=is_pdf, mount="wall")


def m3_05():
    """Вешалка 900 × 266 × 1400 (P6.501.3.05): a board 1 with two reeded strips 3 on each edge (butted at mid height),
    a shelf 2 near the top, five double hooks. The instruction draws H 1400 (catalogue: 1412 / 412)."""
    d = Design("gress-3-05", 900, 266, 1400)
    W = d.W
    d.add("1", [0, 0, 0, W, 1400, 16], grain="y")
    k = 0
    for x in (0, W - 80):
        for y0, y1 in ((0, 699.5), (700.5, 1400)):
            k += 1
            p = d.add("3", [x, y0, 16, x + 80, y1, 32], pid=f"3-{k}", kind="front", grain="y")
            p["face"] = dict(REED_X)
    d.add("2", [80, 1120, 16, W - 80, 1136, 266], grain="x")
    for k, (x, y) in enumerate(((235, 1000), (450, 1000), (665, 1000), (340, 720), (560, 720))):
        d.add(None, None, pid=f"hook-{k + 1}", kind="handle", model="knob", mat="metal", at=[x, y], d=18, t=14,
              standoff=40, z=16)
    rows = [("1", "Основание", 1), ("2", "Стенка горизонтальная", 1), ("3", "Накладка", 4)]
    d.write("П6.501.3.05", "Вешалка «Гресс»", "hall", 104, rows=rows, is_pdf="IS-P6-501-3-05.pdf", mount="wall",
            note="по инструкции H1400 (каталог: 1412)")


def mirror(did, code, W, H, page):
    """Зеркало (no instruction; by the catalogue p. 103 / 104): a 19 mm board, a reeded strip 80 × 16 over each side
    edge, the mirror 4 mm glued between them with 60 mm of the board showing top and bottom."""
    d = Design(did, W, 35, H)
    d.add(None, [0, 0, 0, W, H, 19], pid="board", grain="x")
    for k, x in enumerate((0, W - 80)):
        p = d.add(None, [x, 0, 19, x + 80, H, 35], pid=f"strip-{k + 1}", kind="front", grain="y")
        p["face"] = dict(REED_X)
    d.add(None, [85, 60, 19, W - 85, H - 60, 23], pid="mirror", kind="mirror")
    d.write(code, "Зеркало «Гресс»", "decor" if page != 103 else "hall", page, mount="wall", note="по каталогу")


# ================================================================================ tables
def l_leg(d, na, nb, x, z, sx, sz, h, w=100, t=22, tag=""):
    """An L-shaped leg of two boards: `na` along x (on the outer face z), `nb` along z behind it; (x, z) = the outer
    corner, sx / sz = +1 / −1 towards the inside."""
    xa0, xa1 = sorted((x, x + sx * w))
    za0, za1 = sorted((z, z + sz * t))
    d.add(na, [xa0, 0, za0, xa1, h, za1], pid=f"{na}-{tag}", grain="y")
    xb0, xb1 = sorted((x, x + sx * t))
    zb0, zb1 = sorted((z + sz * t, z + sz * w))
    d.add(nb, [xb0, 0, zb0, xb1, h, zb1], pid=f"{nb}-{tag}", grain="y")


def m0_16():
    """Стол журнальный 750 × 750 × 500 (P6.501.0.16): top 1 on an apron frame (7 / 8), four L legs of two boards
    (2 + 5, 3 + 4), a shelf 6 low between the inner boards; plastic glides ФБ 482."""
    d = Design("gress-0-16", 750, 750, 500)
    W, B, H = 750, 750, 500
    d.add("1", [0, H - 22, 0, W, H, B], grain="x")
    hl = H - 22
    i = 45
    l_leg(d, "2", "5", i, i, 1, 1, hl, tag="fl")
    l_leg(d, "3", "4", W - i, i, -1, 1, hl, tag="fr")
    l_leg(d, "3", "4", i, B - i, 1, -1, hl, tag="bl")
    l_leg(d, "2", "5", W - i, B - i, -1, -1, hl, tag="br")
    # aprons between the legs, flush with the legs' outer faces
    d.add("7", [i + 100, hl - 80, i, W - i - 100, hl, i + 16], pid="7-1", grain="x")
    d.add("7", [i + 100, hl - 80, B - i - 16, W - i - 100, hl, B - i], pid="7-2", grain="x")
    d.add("8", [i, hl - 80, i + 100, i + 16, hl, B - i - 100], pid="8-1", grain="z")
    d.add("8", [W - i - 16, hl - 80, i + 100, W - i, hl, B - i - 100], pid="8-2", grain="z")
    d.add("6", [i + 22, 150, i + 22, W - i - 22, 166, B - i - 22], grain="x", shape="path",
          outline=f"M {i + 22 + 78} {i + 22} L {W - i - 100} {i + 22} L {W - i - 100} {i + 100} L {W - i - 22} {i + 100} "
                  f"L {W - i - 22} {B - i - 100} L {W - i - 100} {B - i - 100} L {W - i - 100} {B - i - 22} "
                  f"L {i + 100} {B - i - 22} L {i + 100} {B - i - 100} L {i + 22} {B - i - 100} L {i + 22} {i + 100} "
                  f"L {i + 100} {i + 100} Z")
    rows = [("1", "Крышка", 1), ("2", "Опора", 2), ("3", "Опора", 2), ("4", "Опора", 2), ("5", "Опора", 2),
            ("6", "Стенка горизонтальная", 1), ("7", "Царга", 2), ("8", "Царга", 2)]
    d.write("П6.501.0.16", "Стол журнальный «Гресс»", "tables", 104, rows=rows, is_pdf="IS-P6-501-0-16.pdf")


def m0_22():
    """Стол 1600 (2100) × 910 × 770 (P6.501.0.22): two top halves 1 on a slide mechanism (800 × 910), the leaf 8
    (500) stored under them on the supports 9, aprons 2 / 3, four L legs of two 25 mm boards (4 + 6, 5 + 7) 115 × 129
    as drawn; glides ФБ 482."""
    d = Design("gress-0-22", 1600, 910, 770)
    W, B, H = 1600, 910, 770
    t = 25
    hl = H - t
    d.add("1", [0, hl, 0, 800, H, B], pid="1-1", grain="x")
    d.add("1", [800, hl, 0, W, H, B], pid="1-2", grain="x")

    def leg(na, nb, x, z, sx, sz, tag):
        xa0, xa1 = sorted((x, x + sx * 115))
        za0, za1 = sorted((z, z + sz * t))
        d.add(na, [xa0, 0, za0, xa1, hl, za1], pid=f"{na}-{tag}", grain="y")
        xb0, xb1 = sorted((x, x + sx * t))
        zb0, zb1 = sorted((z + sz * t, z + sz * 129))
        d.add(nb, [xb0, 0, zb0, xb1, hl, zb1], pid=f"{nb}-{tag}", grain="y")

    leg("4", "6", 0, 0, 1, 1, "fl")
    leg("5", "7", W, 0, -1, 1, "fr")
    leg("5", "7", 0, B, 1, -1, "bl")
    leg("4", "6", W, B, -1, -1, "br")
    d.add("2", [115, hl - 100, 0, W - 115, hl, 16], pid="2-1", grain="x")
    d.add("2", [115, hl - 100, B - 16, W - 115, hl, B], pid="2-2", grain="x")
    d.add("3", [0, hl - 100, 129, 16, hl, B - 129], pid="3-1", grain="z")
    d.add("3", [W - 16, hl - 100, 129, W, hl, B - 129], pid="3-2", grain="z")
    d.add("9", [520, hl - 70, 16, 580, hl - 45, B - 16], pid="9-1", grain="z")
    d.add("9", [1020, hl - 70, 16, 1080, hl - 45, B - 16], pid="9-2", grain="z")
    d.add("8", [550, hl - 45, 20, 1050, hl - 20, B - 20], grain="x")
    rows = [("1", "Полукрышка", 2), ("2", "Царга", 2), ("3", "Царга", 2), ("4", "Опора", 2), ("5", "Опора", 2),
            ("6", "Опора", 2), ("7", "Опора", 2), ("8", "Вкладыш", 1), ("9", "Элемент опорный", 2)]
    d.write("П6.501.0.22", "Стол «Гресс»", "tables", 104, rows=rows, is_pdf="IS-P6-501-0-22-1.pdf",
            note="раздвижной: L1600/2100 (вкладыш 500)")


def pedestal_feet(d, x0, x1):
    B = d.B
    k = len([p for p in d.parts if p.get("id", "").startswith("foot-")])
    for x in (x0 + 11, x1 - 101):
        for z in (1, B - 59):
            k += 1
            d.add(None, [x, 0, z, x + 90, FEET_H, z + 56], pid=f"foot-{k}", mat="feet", edge=2)


def m2_15():
    """Стол письменный 2т 1550 × 670 × 760 (P6.501.2.15): a door pedestal (left) and a three-drawer pedestal (right),
    each with an open niche under the top; a keyboard shelf 20 between them, a modesty panel 12, reeded strips 13 / 14
    on the outer front edges and 15 × 4 on the pedestals' back edges (the desk may stand in the room)."""
    d = Design("gress-2-15", 1550, 670, 760)
    W, B, H = d.W, d.B, d.H
    fz0, fz1 = d.fz0, d.fz1
    d.add("1", [0, H - 25, 0, W, H, B], grain="x")
    pedestal_feet(d, 0, 425)
    pedestal_feet(d, W - 425, W)
    y0, y1 = 45, H - 25
    # left pedestal x 0..425: sides 2 / 3, bottom 8, niche floor 10, back 7, loose shelf 26
    d.add("2", [0, y0 - 25, 3, 16, y1, fz0], grain="y")
    d.add("3", [409, y0 - 25, 3, 425, y1, fz0], grain="y")
    d.add("8", [16, 20, 3, 409, 45, fz0], grain="x")
    d.add("10", [16, 572, 3, 409, 588, fz0], grain="x")
    d.add("26", [17, 300, 5, 408, 316, fz0 - 20], grain="x")
    d.back("7", 2, 20, 423, H - 25, pid="7-1")
    # right pedestal x 1125..1550: sides 4 / 5, bottom 9, niche floor 11, partition 6 for the runners, back 7
    d.add("4", [W - 425, y0 - 25, 3, W - 409, y1, fz0], grain="y")
    d.add("5", [W - 16, y0 - 25, 3, W, y1, fz0], grain="y")
    d.add("9", [W - 409, 20, 3, W - 16, 45, fz0], grain="x")
    d.add("11", [W - 409, 572, 3, W - 16, 588, fz0], grain="x")
    d.add("6", [W - 81, 45, 3, W - 65, 572, fz0], grain="y")
    d.back("7", W - 423, 20, W - 2, H - 25, pid="7-2")
    # strips: 13 / 14 on the outer front edges, 15 × 4 on the back edges of the four pedestal sides (z 0..16; the
    # pedestals' carcass starts 19 mm in, behind the backs 7 nailed on at z 16..19)
    d.strip("13", 1, 20, H - 26)
    d.strip("14", W - 81, 20, H - 26)
    for k, x in enumerate((0, 345, W - 425, W - 80)):
        p = d.add("15", [x, 20, 0, x + 80, H - 26, 16], pid=f"15-{k + 1}", kind="front", grain="y")
        p["face"] = dict(REED_X, side="-")
    for p in d.parts:
        if p.get("n") in ("2", "3", "4", "5", "8", "9", "10", "11", "6", "26"):
            p["box"][2] = max(p["box"][2], 19)
        if p.get("n") == "7":
            p["box"][2], p["box"][5] = 16, 19
    # knee space: modesty panel 12 behind, keyboard shelf 20 under the top
    d.add("12", [425, 400, 16, W - 425, H - 25, 32], grain="x")
    kb = [d.add("20", [440, 650, 60, W - 440, 666, fz0 - 20], grain="x")]
    d.moves.append({"type": "drawer", "name": "keyboard", "parts": ["20"], "travel": 300})
    d.door("19", 84, 47, 422, 570, "left", hy=460, hx=380, hdir="right")
    dn = ("21.1", "21.2", "21.3", "21.4", "21.5")
    for k, (a, b, hy) in enumerate(((47, 219, 133), (222, 394, 308), (397, 569, 483))):
        d.drawer(str(k + 1), dn, W - 422, a, W - 84, b, W - 409, W - 81, a + 10, 110, depth=350, reed=False, hy=hy)
    rows = [("1", "Крышка", 1), ("2", "Стенка вертикальная", 1), ("3", "Стенка вертикальная", 1),
            ("4", "Стенка вертикальная", 1), ("5", "Стенка вертикальная", 1), ("6", "Перегородка", 1),
            ("7", "Стенка задняя", 2), ("8", "Стенка горизонтальная", 1), ("9", "Стенка горизонтальная", 1),
            ("10", "Стенка горизонтальная", 1), ("11", "Стенка горизонтальная", 1), ("12", "Царга", 1),
            ("13", "Накладка", 1), ("14", "Накладка", 1), ("15", "Накладка", 4), ("19", "Дверь", 1),
            ("20", "Полка выдвижная", 1), ("21.1", "Стенка передняя", 3), ("21.2", "Стенка боковая", 3),
            ("21.3", "Стенка боковая", 3), ("21.4", "Стенка задняя", 3), ("21.5", "Дно", 3), ("26", "Полка", 1)]
    d.write("П6.501.2.15", "Стол письменный 2т «Гресс»", "office", 104, rows=rows, is_pdf="IS-P6-501-2-15-1.pdf",
            cut_note="the table skips 16–18 and numbers the drawer's parts 21–25 (written 21.1–21.5); sizes as built")



def m2_23(mirrored=False):
    """Стол письменный 1150 × 670 × 760 (P6.501.2.23-01: the pedestal on the left, as the instruction draws it; 2.23 =
    the mirror image, the pedestal on the right, by the catalogue cut-out p. 104): a three-drawer pedestal with an open
    niche under the top, the far end on a side panel 5 with two reeded strips 11 on its front edge, a modesty panel 6,
    a rail 9 under the top at the back, a keyboard shelf 12."""
    did = "gress-2-23" if mirrored else "gress-2-23-01"
    d = Design(did, 1150, 670, 760)
    W, B, H = d.W, d.B, d.H
    fz0 = d.fz0
    X = (lambda x: W - x) if mirrored else (lambda x: x)

    def bx(n, x0, y0, z0, x1, y1, z1, **kw):
        a, b = sorted((X(x0), X(x1)))
        return d.add(n, [a, y0, z0, b, y1, z1], **kw)

    d.add("1", [0, H - 25, 0, W, H, B], grain="x")
    xs = [X(11), X(327)] if not mirrored else [X(101), X(417)]
    for k, x in enumerate(sorted(xs)):
        for z in (1, B - 59):
            d.add(None, [x, 0, z, x + 90, FEET_H, z + 56], pid=f"foot-{k}-{int(z)}", mat="feet", edge=2)
    bx("2", 0, 20, 3, 16, H - 25, fz0, grain="y")                        # pedestal's outer side
    bx("4", 412, 20, 3, 428, H - 25, fz0, grain="y")                     # pedestal's inner side
    bx("3", 65, 45, 3, 81, 572, fz0, grain="y")                          # runner partition behind the strip
    bx("7", 16, 20, 3, 412, 45, fz0, grain="x")                          # pedestal bottom
    bx("8", 16, 572, 3, 412, 588, fz0, grain="x")                        # niche floor
    bx("5", W - 16, 0, 3, W, H - 25, fz0, grain="y")                     # the far side panel (on glides)
    bx("6", 428, 400, 16, W - 16, H - 125, 32, grain="x")                # modesty panel
    bx("9", 428, H - 125, 3, W - 16, H - 25, 19, grain="x")              # rail under the top
    bx("10", 1, 20, fz0, 81, H - 26, d.fz1, kind="front", grain="y", face=dict(REED_X))
    bx("11", W - 81, 0, fz0, W - 1, 367, d.fz1, pid="11-1", kind="front", grain="y", face=dict(REED_X))
    bx("11", W - 81, 368, fz0, W - 1, H - 26, d.fz1, pid="11-2", kind="front", grain="y", face=dict(REED_X))
    bx("12", 440, 650, 60, W - 97, 666, fz0 - 20, grain="x")
    d.moves.append({"type": "drawer", "name": "keyboard", "parts": ["12"], "travel": 300})
    dn = ("13.1", "13.2", "13.3", "13.4", "13.5")
    for k, (a, b, hy) in enumerate(((47, 219, 133), (222, 394, 308), (397, 569, 483))):
        x0, x1 = sorted((X(84), X(410)))
        o0, o1 = sorted((X(81), X(412)))
        d.drawer(str(k + 1), dn, x0, a, x1, b, o0, o1, a + 10, 110, depth=350, reed=False, hy=hy)
    if mirrored:
        d.write("П6.501.2.23", "Стол письменный «Гресс»", "office", 104,
                note="по каталогу: зеркальное исполнение П6.501.2.23-01 (тумба справа)")
    else:
        rows = [("1", "Крышка", 1), ("2", "Стенка вертикальная", 1), ("3", "Перегородка", 1),
                ("4", "Стенка вертикальная", 1), ("5", "Стенка вертикальная", 1), ("6", "Стенка задняя", 1),
                ("7", "Стенка горизонтальная", 1), ("8", "Стенка горизонтальная", 1), ("9", "Царга", 1),
                ("10", "Накладка", 1), ("11", "Накладка", 2), ("12", "Полка выдвижная", 1),
                ("13.1", "Стенка передняя", 3), ("13.2", "Стенка боковая", 3), ("13.3", "Стенка боковая", 3),
                ("13.4", "Стенка задняя", 3), ("13.5", "Дно", 3)]
        d.write("П6.501.2.23-01", "Стол письменный «Гресс»", "office", 104, rows=rows, is_pdf="P6-501-2-23-01-IS.pdf")


# ================================================================================ beds
def bed(did, code, B, mattress_w):
    """Кровать 2051 × B × 850 (no instruction; by the catalogue p. 101 / 102 / 104): a 25 mm headboard as wide as B
    (wider than the frame) with reeded strips over its side edges and along its top, the frame of side rails and a
    footboard 25 mm (y 0..400) round the sleeping place, the metal base (hardware) at 230 and the mattress 200."""
    L = 2051
    d = Design(did, B, L, 850)
    fw = mattress_w + 50
    x0 = (B - fw) / 2
    d.add(None, [0, 0, 0, B, 850, 25], pid="headboard", grain="x")
    for k, x in enumerate((0, B - 80)):
        d.add(None, [x, 0, 25, x + 80, 770, 41], pid=f"strip-{k + 1}", kind="front", grain="y", face=dict(REED_X))
    d.add(None, [0, 770, 25, B, 850, 41], pid="strip-top", kind="front", grain="x",
          face={"type": "fluted", "dir": "y", "pitch": 10, "depth": 1.5, "flute": "groove", "gap": 7, "margin": 8})
    d.add(None, [x0, 0, 41, x0 + 25, 400, L - 25], pid="rail-l", grain="z")
    d.add(None, [B - x0 - 25, 0, 41, B - x0, 400, L - 25], pid="rail-r", grain="z")
    d.add(None, [x0, 0, L - 25, B - x0, 400, L], pid="footboard", grain="x")
    d.add(None, [x0 + 25, 230, 45, B - x0 - 25, 260, L - 29], pid="base", kind="panel", mat="black", covers=[])
    d.add(None, [x0 + 25, 260, 45, B - x0 - 25, 460, L - 29], pid="mattress", kind="mattress")
    d.write(code, bed_name(mattress_w), "bedroom", 104,
            note=f"сп. место 2000×{mattress_w}, металлокаркас; по каталогу")


def bed_name(w):
    return {900: "Кровать 1-09 «Гресс»", 1200: "Кровать 2-12 «Гресс»", 1400: "Кровать 2-14 «Гресс»",
            1600: "Кровать 2-16 «Гресс»", 1800: "Кровать 2-18 «Гресс»"}[w]


# ================================================================================ output
FINISHES = [
    {"id": "gress-sonoma", "name": "Дуб Сонома 325", "body": "door_enamel_whitey#caab92", "swatch": "#caab92",
     "roles": {"feet": "door_enamel_whitey#8e8f90"}},
]
COLLECTION = {"id": SLUG, "name": "Гресс", "brand": "Пинскдрев", "finishes": ["gress-sonoma"], "metal": "chrome#a9abad",
              "note": "Каталог «Корпусная мебель ч. II» 2025, PDF с. 98–104 (каталог 192–205). Корпус ЛДСП «Дуб Сонома»: "
                      "крышка и дно 25 мм во всю ширину и глубину, дно на серых опорах «Валмакс» 20 мм, боковины 16 между "
                      "ними; фасады 16 накладные с лицом на 7 мм глубже кромки крышки; на торцах боковин — накладки 80 мм "
                      "с поперечными канавками (шаг 10), двери на петлях 180° к накладкам; ящики на роликовых "
                      "направляющих к перегородкам за накладками; задние стенки ДВП на гвоздях; ручки-скобы 128."}


def main():
    for f in (m2_01, m1_27, m0_04, m1_12, lambda: m1_12(True), m1_14, m3_01, m1_21, m1_34, m0_02, m0_05, m0_17, m0_25,
              m1_10, m1_11, m1_26, m3_04, m3_02, m3_05,
              lambda: m_shelf("gress-0-20", "П6.501.0.20", 930, "IS-P6-501-0-20-1.pdf"),
              lambda: m_shelf("gress-0-19", "П6.501.0.19", 1390, "IS-P6-501-019-1.pdf"),
              lambda: mirror("gress-3-06", "П6.501.3.06", 820, 962, 103),
              lambda: mirror("gress-1-18", "П6.501.1.18", 930, 705, 104), m0_16, m0_22, m2_15, m2_23,
              lambda: m2_23(True),
              lambda: bed("gress-1-28", "П6.501.1.28", 1124, 900), lambda: bed("gress-1-29", "П6.501.1.29", 1424, 1200),
              lambda: bed("gress-1-30", "П6.501.1.30", 1624, 1400), lambda: bed("gress-1-09", "П6.501.1.09", 1824, 1600),
              lambda: bed("gress-1-31", "П6.501.1.31", 2024, 1800)):
        f()
    frag = {"finishes": FINISHES, "profiles": {}, "collections": [COLLECTION], "models": MODELS}
    with open(os.path.join(HERE, f"{SLUG}_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)
    # completed cut lists: the instruction's table (numbers, names, counts) with the sizes read off the drawings
    import importlib
    for did, (code, rows, note) in CUTLISTS.items():
        with open(os.path.join(common_designs(), did + ".json")) as fh:
            parts = json.load(fh)["parts"]
        d = Design(did, 0, 0, 0)
        d.parts = parts
        out = {"code": code, "source": "table picture of the instruction (numbers, names, counts); sizes read off the "
                                       "vector drawing (front / side views, scale from the overall size, ±1.5 mm) "
                                       "and the collection's construction — see notes/gress.md",
               "rows": cutlist_rows(d, rows)}
        if note:
            out["note"] = note
        with open(os.path.join(HERE, "cutlists", did + ".json"), "w") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"{len(MODELS)} designs, {len(CUTLISTS)} cut lists")
    import sys
    if "--check" in sys.argv:
        check_all()


# the instruction's front view in the 100-dpi page images (reference/gress/pages): box = the view's extent, read off the
# vector drawing (px = pt × 100 / 72)
REFS = {
    "gress-2-01": ("gress-2-01.png", "121,184,199,421"), "gress-1-27": ("gress-1-27-p1.png", "109,178,186,414"),
    "gress-0-04": ("gress-0-04.png", "108,156,186,392"), "gress-1-12": ("gress-1-12-p1.png", "137,190,306,398"),
    "gress-1-13-01": ("gress-1-13-01-p1.png", "137,190,306,398"), "gress-1-14": ("gress-1-14-p1.png", "157,179,257,387"),
    "gress-3-01": ("gress-3-01.png", "105,178,219,438"), "gress-1-21": ("gress-1-21-p1.png", "111,216,303,275"),
    "gress-0-02": ("gress-0-02.png", "131,206,303,269"), "gress-0-05": ("gress-0-05.png", "102,196,274,341"),
    "gress-0-17": ("gress-0-17-p1.png", "121,184,352,253"), "gress-0-25": ("gress-0-25-p1.png", "102,198,274,314"),
    "gress-1-10": ("gress-1-10-p1.png", "122,186,277,257"), "gress-1-11": ("gress-1-11-p1.png", "139,171,276,310"),
    "gress-1-26": ("gress-1-26.png", "144,185,236,358"), "gress-3-04": ("gress-3-04.png", "105,177,282,278"),
    "gress-3-02": ("gress-3-02.png", "105,171,222,323"),
}


def check_all():
    """Run gen/check.py on every Гресс design (with the instruction's front view where there is one)."""
    import subprocess
    import sys
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    bad = []
    for m in MODELS:
        did = m["id"]
        cmd = [sys.executable, os.path.join(HERE, "check.py"), os.path.join(common_designs(), did + ".json"),
               "--out", os.path.join(root, "tools/casegoods/pilot", did + ".png")]
        if did in REFS:
            cmd += ["--ref", os.path.join(root, "tools/casegoods/reference/gress/pages", REFS[did][0]),
                    "--ref-box", REFS[did][1]]
        out = subprocess.run(cmd, capture_output=True, text=True, cwd=root).stdout
        ok = any(l.startswith("ok") for l in out.splitlines())
        print(f"{did:16s} {'ok' if ok else 'FAIL'}")
        if not ok:
            bad.append(did)
            print(out)
    return bad


def common_designs():
    from common import DESIGNS
    return DESIGNS


if __name__ == "__main__":
    main()
