"""«Гранде» (Пинскдрев, П6.606): a frame-and-panel look in a textured oak — corner posts of bars 80 wide, 80 mm aprons
round the top, flat inset fronts, black accent inserts on the front posts, bar handles «скоба С36».

Construction (read off the vector drawings of the instructions: the PDFs are CAD exports to scale; the bedroom ones
(P6-606-1-xx, 4-12) print every size in their table, the living-room ones (IS-P6-606-0-xx, 2-17) print none — the sizes
of those are the drawing's lines, ±1.5 mm — see notes/grande.md):
  * posts: each front corner is an L of a front bar (80 wide, T thick) and a side bar (SD deep, T thick) glued with
    Rastex; each back corner one bar 80 deep; they stand on glides «ФБ 482» (4–5 mm). The bedroom line has T = 25,
    SD = 80 (the post is 80 × 105); the living-room line T = 16, SD = 64 (80 × 80);
  * a black insert «Вставка» (80 × SD+T × 10) caps each front post; the front bars are 10 shorter than the back posts;
  * aprons 80 high round the top (the front one runs the full width, the side ones B − T long) with the 16 mm top panel
    flush inside them; a lower front rail and lower side rails 80 high 75 mm over the glide;
  * the ЛДСП 16 carcass hangs inside the frame: sides T in from the outer faces, standing 82 mm over the glide, the
    bottom 152 over it; runner walls «Перегородка» by the openings, rails 80 deep between drawers, a bar 64 high behind
    the front apron («Брусок» / «Брусок (обманка)»);
  * fronts 16 flush with the frame's face, 3 mm from the bars; frame doors with glass (frame 80) on the vitrines;
  * drawers on ball runners 350 (450 in the TV unit), sides 16, bottom ХДФ in grooves; backs ХДФ 3.5 in grooves;
  * handles: «скоба С36» (170 long) — satin silver with the Юкон oak, black with the Стирлинг oak (finish role handle).
Coordinates: x from the left, y up from the floor, z from the wall (back) to the front; mm.

    /private/tmp/claude-501/venv/bin/python tools/casegoods/gen/grande.py
"""
import json
import os

from common import dump, DESIGNS

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "grande"
MODELS = []
CUTLISTS = {}


def r1(v):
    return round(v + 0.0, 1)


class Design:
    def __init__(self, did, W, B, H, line="new", g=5, Hp=None):
        self.id, self.W, self.B, self.H = did, W, B, H
        self.parts, self.moves = [], []
        self.line = line
        self.T = 25.0 if line == "new" else 16.0     # bar thickness
        self.SD = 80.0 if line == "new" else 64.0    # side bar depth
        self.g = g
        self.Hp = H - g - 80 if Hp is None else Hp   # back post height
        self.yb = g + self.Hp - 10                   # front bars' top = fronts' top
        self.zc = B - self.T                         # carcass front edge (sides, top panel)
        self.fz0, self.fz1 = B - 16, B               # fronts

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

    # ------------------------------------------------------------------------------------------------ frame
    def frame(self, fl, fr, sl, sr, bl, br, apf, apl, apr, rf, rsl, rsr, insl, insr, top, xs=None):
        """Posts, aprons, rails, inserts, glides and the top panel. xs: the posts' x (left, right) when not at the ends."""
        W, B, H, T, SD, g = self.W, self.B, self.H, self.T, self.SD, self.g
        yb, yp = self.yb, g + self.Hp
        # front bars, side bars, back posts
        self.add(fl, [0, g, B - T, 80, yb, B], grain="y")
        self.add(fr, [W - 80, g, B - T, W, yb, B], grain="y")
        self.add(sl, [0, g, B - T - SD, T, yb, B - T], grain="y")
        self.add(sr, [W - T, g, B - T - SD, W, yb, B - T], grain="y")
        self.add(bl, [0, g, 0, T, yp, 80], grain="y")
        self.add(br, [W - T, g, 0, W, yp, 80], grain="y")
        # inserts (black) on the front posts
        zi = B - T - SD
        ol = f"M 0 {zi:g} L {T:g} {zi:g} L {T:g} {B - T:g} L 80 {B - T:g} L 80 {B:g} L 0 {B:g} Z"
        orr = (f"M {W:g} {zi:g} L {W - T:g} {zi:g} L {W - T:g} {B - T:g} L {W - 80:g} {B - T:g} L {W - 80:g} {B:g} "
               f"L {W:g} {B:g} Z")
        self.add(insl, [0, yb, zi, 80, yp, B], mat="black", edge=0.5, shape="path", outline=ol)
        self.add(insr, [W - 80, yb, zi, W, yp, B], mat="black", edge=0.5, shape="path", outline=orr)
        # aprons
        self.add(apf, [0, yp, B - T, W, H, B], grain="x")
        self.add(apl, [0, yp, 0, T, H, B - T], grain="z")
        self.add(apr, [W - T, yp, 0, W, H, B - T], grain="z")
        # lower rails
        if rf:
            self.add(rf, [81, g + 75, B - T, W - 81, g + 155, B], grain="x")
        same = rsl == rsr
        self.add(rsl, [0, g + 75, 80, T, g + 155, B - T - SD], pid=f"{rsl}-l" if same else None, grain="z")
        self.add(rsr, [W - T, g + 75, 80, W, g + 155, B - T - SD], pid=f"{rsr}-r" if same else None, grain="z")
        # top panel flush inside the aprons
        self.add(top, [T + 1, H - 16, 0, W - T - 1, H, B - T], grain="x")
        # glides «ФБ 482» under every post bar
        d = T - 4
        k = 0
        for cx, cz in ((40, B - T / 2), (T / 2, B - T - SD / 2), (T / 2, 40), (W - 40, B - T / 2),
                       (W - T / 2, B - T - SD / 2), (W - T / 2, 40)):
            k += 1
            self.add(None, [cx - d / 2, 0, cz - d / 2, cx + d / 2, g, cz + d / 2], pid=f"glide-{k}", mat="black",
                     shape="circle", edge=0.5)

    def sides(self, n1, n2, y0=None, y1=None):
        T = self.T
        y0 = self.g + 82 if y0 is None else y0
        y1 = self.H - 16 if y1 is None else y1
        self.add(n1, [T, y0, 0, T + 16, y1, self.zc], grain="y")
        self.add(n2, [self.W - T - 16, y0, 0, self.W - T, y1, self.zc], grain="y")

    def bottom(self, n, x0=None, x1=None, pid=None):
        T = self.T
        x0 = T + 17 if x0 is None else x0
        x1 = self.W - T - 17 if x1 is None else x1
        return self.add(n, [x0, self.g + 152, 10, x1, self.g + 168, self.zc], pid=pid, grain="x")

    def hwall(self, n, x0, x1, y, pid=None, z0=10, z1=None):
        """A fixed horizontal wall (shelf) x0..x1, its top face at y."""
        return self.add(n, [x0, y - 16, z0, x1, y, self.zc if z1 is None else z1], pid=pid, grain="x")

    def rail(self, n, x0, x1, yc, pid=None, depth=80):
        """A rail 80 deep, 16 thick, at the front between drawers, centred at yc."""
        return self.add(n, [x0, yc - 8, self.zc - depth, x1, yc + 8, self.zc], pid=pid, grain="x")

    def vwall(self, n, x0, y0, y1, pid=None, z0=10, z1=None):
        return self.add(n, [x0, y0, z0, x0 + 16, y1, self.zc if z1 is None else z1], pid=pid, grain="y")

    def underbar(self, n, x0, x1, pid=None, h=64):
        """The bar behind the front apron under the top panel («Брусок» / «Брусок (обманка)»)."""
        return self.add(n, [x0, self.H - 16 - h, self.zc - 16, x1, self.H - 16, self.zc], pid=pid, grain="x")

    def opora(self, n, xc, pid=None, depth=100):
        """A middle leg «Опора» under the bottom (under a partition)."""
        T, zc = self.T, self.zc / 2
        return self.add(n, [xc - T / 2, self.g, zc - depth / 2, xc + T / 2, self.g + 152, zc + depth / 2], pid=pid,
                        grain="y")

    def back(self, n, x0, y0, x1, y1, pid=None):
        return self.add(n, [x0, y0, 5, x1, y1, 8.5], pid=pid, kind="back")

    def glass_shelf(self, n, x0, x1, y, pid=None, t=6):
        return self.add(n, [x0 + 1, y, 30, x1 - 1, y + t, self.zc - 40], pid=pid, kind="glass")

    def light(self, pid, xc, zc=150, y=None):
        y = self.H - 16 if y is None else y
        return self.add(None, [xc - 30, y - 6, zc - 30, xc + 30, y, zc + 30], pid=pid, kind="light", shape="circle")

    # ------------------------------------------------------------------------------------------------ fronts
    def handle(self, pid, x, y, d="right", z=None):
        """«Скоба С36»: a bar 170 long (160 c-c), 10 × 8, on square posts, 30 mm out of the face."""
        return self.add(None, None, pid=pid, kind="handle", model="bar", mat="handle", at=[r1(x), r1(y)], dir=d, d=170,
                        band=10, t=8, standoff=22, post=10, section="square", z=r1(self.fz1 if z is None else z))

    def front(self, n, x0, y0, x1, y1, pid=None, grain="y", **kw):
        return self.add(n, [x0, y0, self.fz0, x1, y1, self.fz1], pid=pid, kind="front", grain=grain, **kw)

    def door(self, n, x0, y0, x1, y1, hinge, hx=None, hy=None, hdir="up", pid=None, glass=False, covers=None,
             extra=()):
        pid = pid or f"{n}"
        kw = {}
        if glass:
            kw["glass"] = {"frame": 80, "rebate": 10, "t": 4, "tint": "clear"}
        if covers:
            kw["covers"] = covers
        self.front(n, x0, y0, x1, y1, pid=pid, **kw)
        ids = [pid] + list(extra)
        if hy is not None:
            if hx is None:
                hx = x1 - 45 if hinge == "left" else x0 + 45
            self.handle(f"h-{pid}", hx, hy, d=hdir)
            ids.append(f"h-{pid}")
        self.moves.append({"type": "door", "name": f"door_{pid}", "parts": ids, "hinge": hinge, "angle": 105})

    def drawer(self, tag, ns, fx0, fy0, fx1, fy1, bx0, bx1, side_h, L=350, bot_d=None, handle=True):
        """Front ns[0] over [fx0, fx1] × [fy0, fy1]; box x bx0..bx1 (outer, 13 mm runner gap to the walls), sides
        side_h high and L long behind the front, the back between the sides standing 14 over the box's floor, the ХДФ
        bottom in grooves 10 up (5 mm into the sides and the front). ns = (front, side l, side r, back, bottom)."""
        n_f, n_sl, n_sr, n_bk, n_bt = ns
        z1 = self.fz0
        z0 = z1 - L
        bot_d = L + 5 if bot_d is None else bot_d
        y0 = r1(fy0 + (fy1 - fy0 - side_h) / 2)
        ids = []

        def a(n, box, sfx, **kw):
            pid = f"{n}-{tag}" if n else f"{sfx}-{tag}"
            self.add(n, box, pid=pid, **kw)
            ids.append(pid)

        a(n_f, [fx0, fy0, self.fz0, fx1, fy1, self.fz1], "front", kind="front", grain="x")
        a(n_sl, [bx0, y0, z0, bx0 + 16, y0 + side_h, z1], "sl", grain="z")
        a(n_sr, [bx1 - 16, y0, z0, bx1, y0 + side_h, z1], "sr", grain="z")
        a(n_bk, [bx0 + 16, y0 + 14, z0, bx1 - 16, y0 + side_h, z0 + 16], "bk", grain="x")
        a(n_bt, [bx0 + 11, y0 + 10, z1 + 5 - bot_d, bx1 - 11, y0 + 13.5, z1 + 5], "bt", kind="back")
        if handle:
            self.handle(f"h-{tag}", (fx0 + fx1) / 2, (fy0 + fy1) / 2)
            ids.append(f"h-{tag}")
        self.moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": ids, "travel": min(L - 30, 320)})

    # ------------------------------------------------------------------------------------------------ output
    def write(self, code, name, category, page, rows=None, is_pdf=None, note=None, mount=None, cut_note=None,
              size=None):
        size = size or [self.W, self.B, self.H]
        path = dump(self.id, size, self.parts, self.moves)
        m = {"id": self.id, "code": code, "name": name, "collection": SLUG, "category": category, "size": size}
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


def sized_rows(d, rows):
    """Rows (n, name, count) of a table without sizes: the size is that of the design's part with the number (read off
    the vector drawing); rows (n, name, [a, b, c], count) keep the table's own size."""
    out = []
    for r in rows:
        if len(r) == 4:
            n, name, size, count = r
            out.append({"n": n, "name": name, "size": size, "count": count})
            continue
        n, name, count = r
        have = [p for p in d["parts"] if p.get("n") == n and p.get("box")]
        size = None
        if have:
            b = have[0]["box"]
            size = sorted([r1(b[3] - b[0]), r1(b[4] - b[1]), r1(b[5] - b[2])], reverse=True)
        out.append({"n": n, "name": name, "size": size, "count": count})
    return out


BR = "Брусок горизонтальный"
BV = "Брусок вертикальный"
SG = "Стенка горизонтальная"
SV = "Стенка вертикальная"
PG = "Перегородка"
SZ = "Стенка задняя"


# ================================================================================ bedroom line (tables with sizes)
def m1_04():
    """Комод 1002 × 450 × 849: three drawers 190 (P6.606.1.04)."""
    d = Design("grande-1-04", 1002, 450, 849, "new", g=4)
    W = d.W
    d.frame("11", "12", "18", "20", "17", "19", "9", "13", "14", "10", "15", "15", "22", "23", "1")
    d.sides("2", "3")
    d.add("4", [42, 156, 0, 960, 172, d.zc], grain="x")
    d.vwall("5", 73, 172, 833, z0=16)
    d.vwall("6", W - 89, 172, 833, z0=16)
    d.rail("7", 89, W - 89, 364, pid="7-1")
    d.rail("7", 89, W - 89, 564, pid="7-2")
    d.underbar("21", 89, W - 89)
    for i, y0 in enumerate((169, 369, 569)):
        d.drawer(str(i + 1), ("24.1", "24.2", "24.3", "24.4", "24.5"), 83, y0, W - 83, y0 + 190, 102, W - 102, 135)
    d.back("25", 38, 167, 501, 838, pid="25-1")
    d.back("25", 501, 167, 964, 838, pid="25-2")
    rows = [("1", SG, [950, 425, 16], 1), ("2", SV, [747, 425, 16], 1), ("3", SV, [747, 425, 16], 1),
            ("4", SG, [918, 425, 16], 1), ("5", PG, [661, 409, 16], 1), ("6", PG, [661, 409, 16], 1),
            ("7", SG, [824, 80, 16], 2), ("9", BR, [1002, 80, 25], 1), ("10", BR, [840, 80, 25], 1),
            ("11", BV, [755, 80, 25], 1), ("12", BV, [755, 80, 25], 1), ("13", BR, [425, 80, 25], 1),
            ("14", BR, [425, 80, 25], 1), ("15", BR, [265, 80, 25], 2), ("17", BV, [765, 80, 25], 1),
            ("18", BV, [755, 80, 25], 1), ("19", BV, [765, 80, 25], 1), ("20", BV, [755, 80, 25], 1),
            ("21", "Брусок", [824, 64, 16], 1), ("22", "Вставка", [80, 105, 10], 1), ("23", "Вставка", [80, 105, 10], 1),
            ("24.1", "Стенка передняя ящика", [836, 190, 16], 3), ("24.2", "Стенка боковая ящика", [350, 135, 16], 3),
            ("24.3", "Стенка боковая ящика", [350, 135, 16], 3), ("24.4", "Стенка задняя ящика", [766, 121, 16], 3),
            ("24.5", "Дно ящика", [776, 355, 3.5], 3), ("25", SZ, [671, 463, 3.5], 2)]
    d.write("П6.606.1.04", "Комод «Гранде»", "bedroom", 93, rows=rows, is_pdf="P6-606-1-04-Komod-IS.pdf",
            cut_note="table of p. 4 (sizes as printed) with two corrections: row 24 «Ящик выдвижной, в т. ч. — 3»: the "
                     "drawer rows 24.1–24.5 are per drawer, so their count is 3 (the reference parse read 1); 24.5 the "
                     "drawer bottom is printed 776 × 355 × 16 — it slides into grooves like 20.5 of 1.05 and 21.5 of "
                     "1.06 (3.5), so 3.5")


def m1_05():
    """Комод 702 × 450 × 1100: five drawers 160 (P6.606.1.05)."""
    d = Design("grande-1-05", 702, 450, 1100, "new", g=5)
    W = d.W
    d.frame("10", "11", "15", "16", "17", "18", "8", "12", "13", "9", "14", "14", "21", "22", "1")
    d.sides("2", "3")
    d.add("4", [42, 157, 0, 660, 173, d.zc], grain="x")
    d.vwall("5", 73, 173, 1084, z0=16)
    d.vwall("6", W - 89, 173, 1084, z0=16)
    for i, yc in enumerate((335, 505, 675, 845)):
        d.rail("7", 89, W - 89, yc, pid=f"7-{i + 1}")
    d.underbar("19", 89, W - 89)
    for i in range(5):
        y0 = 170 + 170 * i
        d.drawer(str(i + 1), ("20.1", "20.2", "20.3", "20.4", "20.5"), 83, y0, W - 83, y0 + 160, 102, W - 102, 128,
                 bot_d=354)
    d.back("23", 37, 168, 665, 628, pid="23-1")
    d.back("23", 37, 628, 665, 1088, pid="23-2")
    rows = [("1", SG, [650, 425, 16], 1), ("2", SV, [997, 425, 16], 1), ("3", SV, [997, 425, 16], 1),
            ("4", SG, [618, 425, 16], 1), ("5", PG, [911, 409, 16], 1), ("6", PG, [911, 409, 16], 1),
            ("7", SG, [524, 80, 16], 4), ("8", BR, [702, 80, 25], 1), ("9", BR, [540, 80, 25], 1),
            ("10", BV, [1005, 80, 25], 1), ("11", BV, [1005, 80, 25], 1), ("12", BR, [425, 80, 25], 1),
            ("13", BR, [425, 80, 25], 1), ("14", BR, [265, 80, 25], 2), ("15", BV, [1005, 80, 25], 1),
            ("16", BV, [1005, 80, 25], 1), ("17", BV, [1015, 80, 25], 1), ("18", BV, [1015, 80, 25], 1),
            ("19", "Брусок", [524, 64, 16], 1), ("20.1", "Стенка передняя ящика", [536, 160, 16], 5),
            ("20.2", "Стенка боковая ящика", [350, 128, 16], 5), ("20.3", "Стенка боковая ящика", [350, 128, 16], 5),
            ("20.4", "Стенка задняя ящика", [466, 114, 16], 5), ("20.5", "Дно ящика", [476, 354, 3.5], 5),
            ("21", "Вставка", [80, 105, 10], 1), ("22", "Вставка", [80, 105, 10], 1), ("23", SZ, [460, 628, 3.5], 2)]
    d.write("П6.606.1.05", "Комод «Гранде»", "bedroom", 93, rows=rows, is_pdf="P6-606-1-05-Komod-IS.pdf",
            cut_note="table of p. 4 (sizes in the text layer), transcribed; the reference JSON had no rows")


def m1_06():
    """Тумба прикроватная 532 × 450 × 425: one drawer 166 (P6.606.1.06)."""
    d = Design("grande-1-06", 532, 450, 425, "new", g=4)
    W = d.W
    d.frame("9", "10", "15", "17", "16", "18", "8", "11", "12", "22", "13", "13", "19", "20", "1")
    d.sides("2", "3")
    d.add("4", [42, 156, 0, 490, 172, d.zc], grain="x")
    d.vwall("5", 73, 172, 408, z0=16)
    d.vwall("6", W - 89, 172, 408, z0=16)
    d.underbar("7", 89, W - 89)
    d.drawer("1", ("21.1", "21.2", "21.3", "21.4", "21.5"), 83, 169, W - 83, 335, 102, W - 102, 120)
    d.back("23", 37, 168, 495, 413)
    rows = [("1", SG, [480, 425, 16], 1), ("2", SV, [323, 425, 16], 1), ("3", SV, [323, 425, 16], 1),
            ("4", SG, [448, 425, 16], 1), ("5", PG, [236, 409, 16], 1), ("6", PG, [236, 409, 16], 1),
            ("7", "Брусок", [354, 64, 16], 1), ("8", BR, [532, 80, 25], 1), ("9", BV, [331, 80, 25], 1),
            ("10", BV, [331, 80, 25], 1), ("11", BR, [425, 80, 25], 1), ("12", BR, [425, 80, 25], 1),
            ("13", BR, [265, 80, 25], 2), ("15", BV, [331, 80, 25], 1), ("16", BV, [341, 80, 25], 1),
            ("17", BV, [331, 80, 25], 1), ("18", BV, [341, 80, 25], 1), ("19", "Вставка", [80, 105, 10], 1),
            ("20", "Вставка", [80, 105, 10], 1), ("21.1", "Стенка передняя", [366, 166, 16], 1),
            ("21.2", "Стенка боковая", [350, 120, 16], 1), ("21.3", "Стенка боковая", [350, 120, 16], 1),
            ("21.4", "Стенка задняя", [296, 106, 16], 1), ("21.5", "Дно", [306, 355, 3.5], 1),
            ("22", BR, [370, 80, 25], 1), ("23", SZ, [458, 245, 3.5], 1)]
    d.write("П6.606.1.06", "Тумба прикроватная «Гранде»", "bedroom", 93, rows=rows,
            is_pdf="P6-606-1-06-Tumba-prikrovatnaya-IS.pdf",
            cut_note="table of p. 4 (sizes in the text layer), transcribed; the reference JSON had no rows")




def rod(d, x0, x1, y=1840, pid="rod"):
    """Hanger rail «Штанга металлическая» (chrome tube Ø20)."""
    d.add(None, [x0, y - 10, 283, x1, y + 10, 303], pid=pid, kind="tube", mat="chrome")


def m1_01():
    """Шкаф для одежды 3д 1506 × 601 × 2300 (P6.606.1.01): a hanging section behind two doors (rod, shelf 6, a rib 10 at
    the back), a shelf section behind the third door (fixed shelves 7, loose 9); door 30 carries the closing strip 28."""
    d = Design("grande-1-01", 1506, 601, 2300, "new", g=5)
    W = d.W
    d.frame("13", "14", "19", "20", "21", "22", "11", "15", "16", "12", "17", "17", "25", "26", "1")
    d.sides("2", "3")
    d.add("4", [42, 157, 0, 1464, 173, d.zc], grain="x")
    d.vwall("5", 971, 173, 2284, z0=16)
    d.hwall("6", 42, 970, 1925, z0=20, z1=560)
    for i, y in enumerate((1449, 1871)):
        d.hwall("7", 987, 1465, y, pid=f"7-{i + 1}", z0=20, z1=560)
    for i, y in enumerate((593, 1013)):
        d.add("9", [990, y - 16, 22, 1464, y, 562], pid=f"9-{i + 1}", grain="x")
    d.add("10", [442, 173, 8.5, 570, 1909, 24.5], grain="y")
    d.underbar("23", 42, 970)
    d.underbar("24", 987, 1465)
    d.opora("27", 506, pid="27-1")
    d.opora("27", 979, pid="27-2")
    rod(d, 47, 965)
    d.door("29", 83, 170, 523, 2210, "left", hx=303, hy=1190, hdir="right", pid="29-1")
    d.add("28", [492, 180, d.fz0 - 16, 572, 2199, d.fz0], grain="y")
    d.door("30", 532, 170, 972, 2210, "right", hx=752, hy=1190, hdir="right", extra=("28",))
    d.door("29", 983, 170, 1423, 2210, "right", hx=1203, hy=1190, hdir="right", pid="29-2")
    d.back("31", 36.5, 1917, 975.5, 2287)
    d.back("32", 982.5, 1441, 1471.5, 1863, pid="32-1")
    d.back("32", 982.5, 1863, 1471.5, 2285, pid="32-2")
    d.back("33", 982.5, 168, 1471.5, 1441)
    d.back("34", 36.5, 168, 504.5, 1917, pid="34-1")
    d.back("34", 504.5, 168, 972.5, 1917, pid="34-2")
    rows = [("1", SG, [1454, 576, 16], 1), ("2", SV, [2197, 576, 16], 1), ("3", SV, [2197, 576, 16], 1),
            ("4", SG, [1422, 576, 16], 1), ("5", PG, [2111, 560, 16], 1), ("6", SG, [928, 540, 16], 1),
            ("7", SG, [478, 540, 16], 2), ("9", "Полка", [474, 540, 16], 2), ("10", "Брусок", [1737, 128, 16], 1),
            ("11", BR, [1506, 80, 25], 1), ("12", BR, [1344, 80, 25], 1), ("13", BV, [2205, 80, 25], 1),
            ("14", BV, [2205, 80, 25], 1), ("15", BR, [576, 80, 25], 1), ("16", BR, [576, 80, 25], 1),
            ("17", BR, [416, 80, 25], 2), ("19", BV, [2205, 80, 25], 1), ("20", BV, [2205, 80, 25], 1),
            ("21", BV, [2215, 80, 25], 1), ("22", BV, [2215, 80, 25], 1), ("23", "Брусок", [928, 64, 16], 1),
            ("24", "Брусок", [478, 64, 16], 1), ("25", "Вставка", [80, 105, 10], 1), ("26", "Вставка", [80, 105, 10], 1),
            ("27", "Опора", [152, 100, 25], 2), ("28", "Накладка", [2019, 80, 16], 1), ("29", "Дверь", [2040, 440, 16], 2),
            ("30", "Дверь", [2040, 440, 16], 1), ("31", SZ, [370, 939, 3.5], 1), ("32", SZ, [422, 489, 3.5], 2),
            ("33", SZ, [1273, 489, 3.5], 1), ("34", SZ, [1749, 468, 3.5], 2)]
    d.write("П6.606.1.01", "Шкаф для одежды 3д «Гранде»", "bedroom", 93, rows=rows,
            is_pdf="P6-606-1-01-SHkaf-dlya-odejdyi-3d-IS.pdf",
            cut_note="table of p. 4 (sizes in the text layer), transcribed; the reference JSON had no rows")


def m1_02():
    """Шкаф для одежды 2д 1056 × 601 × 2300 (P6.606.1.02): hanging section left (rod under shelf 6), shelves right."""
    d = Design("grande-1-02", 1056, 601, 2300, "new", g=5)
    d.frame("10", "11", "15", "17", "16", "18", "8", "12", "13", "9", "14", "14", "21", "22", "1")
    d.sides("2", "3")
    d.add("5", [42, 157, 0, 1014, 173, d.zc], grain="x")
    d.vwall("4", 520, 173, 2284, z0=16)
    d.hwall("6", 42, 520, 1926, pid="6-1", z0=20, z1=560)
    for i, y in enumerate((1450, 1873)):
        d.hwall("6", 536, 1014, y, pid=f"6-{i + 2}", z0=20, z1=560)
    for i, y in enumerate((593, 1013)):
        d.add("7", [538, y - 16, 22, 1012, y, 562], pid=f"7-{i + 1}", grain="x")
    d.underbar("19", 42, 520, pid="19-1")
    d.underbar("19", 536, 1014, pid="19-2")
    rod(d, 47, 515)
    d.door("20", 83, 170, 523, 2210, "left", hx=303, hy=1190, hdir="right", pid="20-1")
    d.door("20", 533, 170, 973, 2210, "right", hx=753, hy=1190, hdir="right", pid="20-2")
    d.back("23", 35.5, 1918, 526.5, 2289)
    d.back("24", 35.5, 168, 526.5, 1918)
    d.back("25", 529.5, 1442, 1020.5, 1865, pid="25-1")
    d.back("25", 529.5, 1865, 1020.5, 2288, pid="25-2")
    d.back("26", 529.5, 168, 1020.5, 1442)
    rows = [("1", SG, [1004, 576, 16], 1), ("2", SV, [2197, 576, 16], 1), ("3", SV, [2197, 576, 16], 1),
            ("4", PG, [2111, 560, 16], 1), ("5", SG, [972, 576, 16], 1), ("6", SG, [478, 540, 16], 3),
            ("7", "Полка", [474, 540, 16], 2), ("8", BR, [1056, 80, 25], 1), ("9", BR, [894, 80, 25], 1),
            ("10", BV, [2205, 80, 25], 1), ("11", BV, [2205, 80, 25], 1), ("12", BR, [576, 80, 25], 1),
            ("13", BR, [576, 80, 25], 1), ("14", BR, [416, 80, 25], 2), ("15", BV, [2205, 80, 25], 1),
            ("16", BV, [2215, 80, 25], 1), ("17", BV, [2205, 80, 25], 1), ("18", BV, [2215, 80, 25], 1),
            ("19", "Брусок", [478, 64, 16], 2), ("20", "Дверь", [2040, 440, 16], 2), ("21", "Вставка", [80, 105, 10], 1),
            ("22", "Вставка", [80, 105, 10], 1), ("23", SZ, [371, 491, 3.5], 1), ("24", SZ, [1750, 491, 3.5], 1),
            ("25", SZ, [423, 491, 3.5], 2), ("26", SZ, [1274, 491, 3.5], 1)]
    d.write("П6.606.1.02", "Шкаф для одежды 2д «Гранде»", "bedroom", 93, rows=rows,
            is_pdf="P6-606-1-02-SHkaf-dlya-odejdyi-2d-IS.pdf",
            cut_note="table of p. 4 (sizes in the text layer), transcribed; the reference JSON had no rows")


def m1_16():
    """Шкаф для одежды 4д 1956 × 601 × 2300 (P6.606.1.16): shelf sections left and right, a hanging section in the
    middle behind a pair of doors (door 26 carries the closing strip 27)."""
    d = Design("grande-1-16", 1956, 601, 2300, "new", g=5)
    d.frame("16", "17", "20", "21", "22", "23", "14", "18", "19", "15", "24", "24", "28", "29", "1")
    d.sides("2", "3")
    d.add("6", [42, 157, 0, 1914, 173, d.zc], grain="x")
    d.vwall("4", 520, 173, 2284, z0=16)
    d.vwall("5", 1420, 173, 2284, z0=16)
    d.hwall("7", 536, 1420, 1925, z0=20, z1=560)
    k = 0
    for x0, x1 in ((42, 520), (1436, 1914)):
        for y in (1449, 1871):
            k += 1
            d.hwall("8", x0, x1, y, pid=f"8-{k}", z0=20, z1=560)
    k = 0
    for x0, x1 in ((42, 520), (1436, 1914)):
        for y in (593, 1013):
            k += 1
            d.add("9", [x0 + 2, y - 16, 22, x1 - 2, y, 562], pid=f"9-{k}", grain="x")
    d.add("10", [914, 173, 8.5, 1042, 1909, 24.5], grain="y")
    d.underbar("11", 42, 520, pid="11-1")
    d.underbar("12", 536, 1420)
    d.underbar("11", 1436, 1914, pid="11-2")
    d.opora("13", 528, pid="13-1")
    d.opora("13", 1428, pid="13-2")
    rod(d, 541, 1415)
    d.door("25", 83, 170, 523, 2210, "left", hx=303, hy=1190, hdir="right", pid="25-1")
    d.door("25", 532, 170, 972, 2210, "left", hx=752, hy=1190, hdir="right", pid="25-2")
    d.add("27", [938, 177, d.fz0 - 16, 1018, 2202, d.fz0], grain="y")
    d.door("26", 984, 170, 1424, 2210, "right", hx=1204, hy=1190, hdir="right", extra=("27",))
    d.door("25", 1433, 170, 1873, 2210, "right", hx=1653, hy=1190, hdir="right", pid="25-3")
    k = 0
    for x0 in (35.5, 1429.5):
        for y0 in (1441, 1863):
            k += 1
            d.back("30", x0, y0, x0 + 489, y0 + 422, pid=f"30-{k}")
    d.back("31", 35.5, 168, 524.5, 1441, pid="31-1")
    d.back("31", 1429.5, 168, 1918.5, 1441, pid="31-2")
    d.back("32", 529, 1917, 1427, 2287)
    d.back("33", 529, 168, 977, 1917, pid="33-1")
    d.back("33", 977, 168, 1425, 1917, pid="33-2")
    rows = [("1", SG, [1904, 576, 16], 1), ("2", SV, [2197, 576, 16], 1), ("3", SV, [2197, 576, 16], 1),
            ("4", PG, [2111, 560, 16], 1), ("5", PG, [2111, 560, 16], 1), ("6", SG, [1872, 576, 16], 1),
            ("7", SG, [884, 540, 16], 1), ("8", SG, [478, 540, 16], 4), ("9", "Полка", [474, 540, 16], 4),
            ("10", "Брусок", [1737, 128, 16], 1), ("11", "Брусок", [478, 64, 16], 2), ("12", "Брусок", [884, 64, 16], 1),
            ("13", "Опора", [152, 100, 25], 2), ("14", BR, [1956, 80, 25], 1), ("15", BR, [1794, 80, 25], 1),
            ("16", BV, [2205, 80, 25], 1), ("17", BV, [2205, 80, 25], 1), ("18", BR, [576, 80, 25], 1),
            ("19", BR, [576, 80, 25], 1), ("20", BV, [2205, 80, 25], 1), ("21", BV, [2205, 80, 25], 1),
            ("22", BV, [2215, 80, 25], 1), ("23", BV, [2215, 80, 25], 1), ("24", BR, [416, 80, 25], 2),
            ("25", "Дверь", [2040, 440, 16], 3), ("26", "Дверь", [2040, 440, 16], 1), ("27", "Накладка", [2025, 80, 16], 1),
            ("28", "Вставка", [80, 105, 10], 1), ("29", "Вставка", [80, 105, 10], 1), ("30", SZ, [422, 489, 3.5], 4),
            ("31", SZ, [1273, 489, 3.5], 2), ("32", SZ, [370, 898, 3.5], 1), ("33", SZ, [1749, 448, 3.5], 2)]
    d.write("П6.606.1.16", "Шкаф для одежды 4д «Гранде»", "bedroom", 93, rows=rows,
            is_pdf="P6-606-1-16-SHkaf-dlya-odejdyi-4d-IS.pdf",
            cut_note="table of p. 4 as printed (the reference JSON agrees)")

# ================================================================================ living-room line (tables without sizes)
BOX = ("Стенка боковая", "Стенка боковая", "Стенка задняя", "Дно", "Стенка передняя")


def drawer_rows(n, count, order=(1, 2, 3, 4, 5)):
    """Drawer sub-rows n.1 … n.5 in the table's order; BOX gives the names in the order side, side, back, bottom,
    front (the living-room tables' order)."""
    return [(f"{n}.{k}", BOX[k - 1], count) for k in order]


def m0_01():
    """Шкаф 680 × 420 × 2002 с подсветкой (P6.606.0.01): a frame door with glass over three glass shelves, two drawers
    under it; «универсальный» — the door hangs left or right."""
    d = Design("grande-0-01", 680, 420, 2002, "old", g=4)
    W = d.W
    d.frame("12", "13", "16", "20", "17", "21", "10", "14", "18", "11", "15", "19", "23", "24", "3")
    d.sides("1", "2")
    d.bottom("6")
    d.vwall("4", 64, 172, 650)
    d.vwall("5", W - 80, 172, 650)
    d.hwall("7", 33, W - 33, 666)
    d.rail("8", 80, W - 80, 411.5)
    for i, y in enumerate((979, 1290, 1601)):
        d.glass_shelf("9", 33, W - 33, y, pid=f"9-{i + 1}")
    d.underbar("22", 33, W - 33)
    d.light("led", W / 2)
    for i, (y0, y1) in enumerate(((169, 407), (416, 654))):
        d.drawer(str(i + 1), ("26.5", "26.1", "26.2", "26.3", "26.4"), 81, y0, W - 83, y1, 93, W - 93, 150)
    d.door("25", 81, 664, W - 83, 1912, "left", hx=557.5, hy=1293, glass=True)
    d.back("27", 27, 161, W - 27, 1991)
    rows = [("1", SV, 1), ("2", SV, 1), ("3", SG, 1), ("4", PG, 1), ("5", PG, 1), ("6", SG, 1), ("7", SG, 1),
            ("8", SG, 1), ("9", "Полка (стекло)", 3), ("10", BR, 1), ("11", BR, 1), ("12", BV, 1), ("13", BV, 1),
            ("14", BR, 1), ("15", BR, 1), ("16", BV, 1), ("17", BV, 1), ("18", BR, 1), ("19", BR, 1), ("20", BV, 1),
            ("21", BV, 1), ("22", "Брусок", 1), ("23", "Вставка", 1), ("24", "Вставка", 1),
            ("25", "Дверь рамочная", 1)] + drawer_rows("26", 2) + [("27", SZ, 1)]
    d.write("П6.606.0.01", "Шкаф «Гранде»", "living", 93, rows=rows, is_pdf="IS-P6-606-0-01-SHkaf.pdf",
            note="с подсветкой, универсальный (дверь левая или правая)",
            cut_note="row 9 (glass shelves, 3) has no code in the table and was missing from the reference JSON")


def m0_04():
    """Шкаф 980 × 420 × 2002 с подсветкой (P6.606.0.04): two frame doors with glass over two sections of glass shelves,
    two wide drawers under them."""
    d = Design("grande-0-04", 980, 420, 2002, "old", g=4)
    W = d.W
    d.frame("15", "16", "18", "21", "19", "22", "11", "13", "14", "17", "23", "23", "24", "25", "3")
    d.sides("1", "2")
    d.bottom("7")
    d.vwall("5", 64, 172, 650)
    d.vwall("6", W - 80, 172, 650)
    d.hwall("8", 33, W - 33, 666)
    d.rail("9", 80, W - 80, 411)
    d.vwall("4", 482, 666, 1986, z1=d.zc - 16)
    k = 0
    for x0, x1 in ((33, 482), (498, W - 33)):
        for y in (978, 1289, 1600):
            k += 1
            d.glass_shelf("10", x0, x1, y, pid=f"10-{k}")
    d.underbar("12", 33, W - 33)
    d.light("led-1", 257)
    d.light("led-2", 723)
    for i, (y0, y1) in enumerate(((169, 406), (416, 654))):
        d.drawer(str(i + 1), ("28.1", "28.2", "28.3", "28.4", "28.5"), 82, y0, W - 81, y1, 93, W - 93, 150)
    d.door("26", 82, 664, 486, 1912, "left", hx=446, hy=1287, glass=True, covers=["26.4"])
    d.door("27", 494, 664, W - 81, 1912, "right", hx=534.5, hy=1287, glass=True, covers=["26.4"])
    d.back("29", 27, 661, 490, 1991, pid="29-1")
    d.back("29", 490, 661, W - 27, 1991, pid="29-2")
    d.back("30", 27, 161, W - 27, 661)
    rows = [("1", SV, 1), ("2", SV, 1), ("3", SG, 1), ("4", PG, 1), ("5", PG, 1), ("6", PG, 1), ("7", SG, 1),
            ("8", SG, 1), ("9", SG, 1), ("10", "Полка (стекло)", 6), ("11", BR, 1), ("12", "Брусок", 1), ("13", BR, 1),
            ("14", BR, 1), ("15", BV, 1), ("16", BV, 1), ("17", BR, 1), ("18", BV, 1), ("19", BV, 1), ("21", BV, 1),
            ("22", BV, 1), ("23", BR, 2), ("24", "Вставка", 1), ("25", "Вставка", 1), ("26", "Дверь рамочная", 1),
            ("26.4", "Накладка (стекло)", [1108, 264, 4], 2), ("27", "Дверь рамочная", 1),
            ("28.1", "Стенка передняя", 2), ("28.2", "Стенка боковая", 2), ("28.3", "Стенка боковая", 2),
            ("28.4", "Стенка задняя", 2), ("28.5", "Дно", 2), ("29", SZ, 2), ("30", SZ, 1)]
    d.write("П6.606.0.04", "Шкаф «Гранде»", "living", 93, rows=rows, is_pdf="IS-P6-606-0-04-SHkaf-1.pdf",
            note="с подсветкой",
            cut_note="rows 10 (glass shelves, 6) and 26.4 (the doors' glass, 2) have no code in the table and were "
                     "missing from the reference JSON; the drawer (28) rows are per drawer (2 drawers); 26.4 is the glass "
                     "of the frame doors (covers): (1248 − 2 × 80 + 2 × 10) × (404 − 2 × 80 + 2 × 10) = 1108 × 264")


def m0_05():
    """Шкаф 1150 × 420 × 1590 с подсветкой (P6.606.0.05): left two drawers and a door over two shelves, right a frame
    door with glass over four glass shelves."""
    d = Design("grande-0-05", 1150, 420, 1590, "old", g=5)
    W = d.W
    d.frame("13", "14", "19", "22", "21", "20", "11", "15", "16", "12", "18", "17", "25", "24", "1")
    d.sides("3", "2")
    d.bottom("5")
    d.vwall("4", 567, 173, 1574, z1=d.zc - 16)
    d.vwall("8", 64, 173, 710)
    d.hwall("6", 33, 567, 726)
    d.rail("7", 80, 567, 440)
    for i, y in enumerate((979, 1232)):
        d.add("9", [33, y - 16, 30, 566, y, 380], pid=f"9-{i + 1}", grain="x")
    for i, y in enumerate((436, 701, 967, 1231)):
        d.glass_shelf("10", 583, W - 33, y, pid=f"10-{i + 1}")
    d.underbar("23", 33, W - 33)
    d.opora("26", 575)
    d.light("led", 850)
    for i, (y0, y1) in enumerate(((170, 435), (445, 711))):
        d.drawer(str(i + 1), ("27.5", "27.1", "27.2", "27.3", "27.4"), 81, y0, 572, y1, 93, 554, 150)
    d.door("29", 81, 721, 572, 1500, "left", hx=326.5, hy=846, hdir="right")
    d.door("30", 578, 170, W - 82, 1500, "right", hx=607, hy=848, glass=True)
    d.back("31", 578, 162, W - 28, 1579)
    d.back("32", 28, 718, 572, 1579)
    d.back("33", 28, 162, 572, 718)
    rows = [("1", SG, 1), ("2", SV, 1), ("3", SV, 1), ("4", PG, 1), ("5", SG, 1), ("6", SG, 1), ("7", SG, 1),
            ("8", PG, 1), ("9", "Полка", 2), ("10", "Полка (стекло)", 4), ("11", BR, 1), ("12", BR, 1), ("13", BV, 1),
            ("14", BV, 1), ("15", BR, 1), ("16", BR, 1), ("17", BR, 1), ("18", BR, 1), ("19", BV, 1), ("20", BV, 1),
            ("21", BV, 1), ("22", BV, 1), ("23", "Брусок (обманка)", 1), ("24", "Вставка", 1), ("25", "Вставка", 1),
            ("26", "Опора", 1)] + drawer_rows("27", 2) + [("29", "Дверь", 1), ("30", "Дверь рамочная", 1),
                                                           ("31", SZ, 1), ("32", SZ, 1), ("33", SZ, 1)]
    d.write("П6.606.0.05", "Шкаф «Гранде»", "living", 93, rows=rows, is_pdf="IS-P6-606-0-05-SHkaf.pdf",
            note="с подсветкой",
            cut_note="the table has no text layer: transcribed from the picture of p. 1 (there is no row 28)")


def m0_07():
    """Шкаф 1660 × 420 × 1245 с подсветкой (P6.606.0.07): three columns of two drawers; frame doors with glass left and
    right, an open niche with two shelves in the middle."""
    d = Design("grande-0-07", 1660, 420, 1245, "old", g=5)
    W = d.W
    d.frame("19", "20", "23", "27", "24", "28", "17", "21", "25", "18", "22", "26", "32", "33", "1")
    d.sides("2", "3")
    d.bottom("6")
    d.vwall("4", 554, 173, 1229)
    d.vwall("5", 1090, 173, 1229)
    d.vwall("12", 64, 173, 586)
    d.vwall("13", W - 80, 173, 586)
    d.hwall("7", 33, 554, 602)
    d.hwall("8", 570, 1090, 602)
    d.hwall("9", 1106, W - 33, 602)
    d.rail("14", 80, 554, 379.5)
    d.rail("15", 570, 1090, 379.5)
    d.rail("16", 1106, W - 80, 379.5)
    for i, y in enumerate((794, 978)):
        d.hwall("10", 570, 1090, y, pid=f"10-{i + 1}", z0=30, z1=380)
    d.glass_shelf("11", 33, 554, 882, pid="11-1")
    d.glass_shelf("11", 1106, W - 33, 882, pid="11-2")
    d.underbar("29", 33, 554, pid="29-1")
    d.underbar("30", 570, 1090)
    d.underbar("29", 1106, W - 33, pid="29-2")
    d.opora("31", 562, pid="31-1")
    d.opora("31", 1098, pid="31-2")
    d.light("led-1", 318)
    d.light("led-2", 1342)
    cols = (("36", 83, 558, 93, 541), ("37", 565, 1093, 583, 1077), ("38", 1102, 1575, 1119, 1567))
    for n, fx0, fx1, bx0, bx1 in cols:
        for r, (y0, y1) in enumerate(((170, 374), (385, 589))):
            d.drawer(f"{n}-{r + 1}", (f"{n}.5", f"{n}.1", f"{n}.2", f"{n}.3", f"{n}.4"), fx0, y0, fx1, y1, bx0, bx1, 128)
    d.door("34", 82, 600, 558, 1155, "left", hx=518, hy=881.5, glass=True, pid="34-1")
    d.door("34", 1102, 600, W - 82, 1155, "right", hx=1141.5, hy=881.5, glass=True, pid="34-2")
    d.back("39", 28, 597, 562, 1234)
    d.back("40", 562, 597, 1098, 1234)
    d.back("41", 1098, 597, W - 28, 1234)
    for i, (x0, x1) in enumerate(((28, 563), (563, 1098), (1097, W - 28))):
        d.back("42", x0, 162, x1, 597, pid=f"42-{i + 1}")
    rows = [("1", SG, 1), ("2", SV, 1), ("3", SV, 1), ("4", PG, 1), ("5", PG, 1), ("6", SG, 1), ("7", SG, 1),
            ("8", SG, 1), ("9", SG, 1), ("10", "Полка", 2), ("11", "Полка (стекло)", 2), ("12", PG, 1), ("13", PG, 1),
            ("14", SG, 1), ("15", SG, 1), ("16", SG, 1), ("17", BR, 1), ("18", BR, 1), ("19", BV, 1), ("20", BV, 1),
            ("21", BR, 1), ("22", BR, 1), ("23", BV, 1), ("24", BV, 1), ("25", BR, 1), ("26", BR, 1), ("27", BV, 1),
            ("28", BV, 1), ("29", "Брусок (обманка)", 2), ("30", "Брусок (обманка)", 1), ("31", "Опора", 2),
            ("32", "Вставка", 1), ("33", "Вставка", 1), ("34", "Дверь рамочная", 2)] + drawer_rows("36", 2) + \
        drawer_rows("37", 2) + drawer_rows("38", 2) + [("39", SZ, 1), ("40", SZ, 1), ("41", SZ, 1), ("42", SZ, 3)]
    d.write("П6.606.0.07", "Шкаф «Гранде»", "living", 93, rows=rows, is_pdf="IS-P6-606-0-07-SHkaf.pdf",
            note="с подсветкой",
            cut_note="the table has no text layer: transcribed from the picture of p. 1 (row 11 = glass shelves, no "
                     "code; there is no row 35); 36 / 37 / 38 are the drawers of the left / middle / right column")


def m0_09():
    """Тумба 2000 × 450 × 850 (P6.606.0.09): two doors over a shelf each, three drawers in the middle."""
    d = Design("grande-0-09", 2000, 450, 850, "old", g=5)
    W = d.W
    d.frame("11", "12", "15", "18", "16", "19", "9", "13", "17", "10", "14", "14", "25", "26", "1")
    d.sides("2", "3")
    d.bottom("4")
    d.vwall("5", 683, 173, 834)
    d.vwall("6", 1301, 173, 834)
    d.add("7", [33, 454, 30, 682, 470, 414], pid="7-1", grain="x")
    d.add("7", [1318, 454, 30, 1967, 470, 414], pid="7-2", grain="x")
    d.rail("8", 699, 1301, 364.5, pid="8-1")
    d.rail("8", 699, 1301, 565, pid="8-2")
    d.underbar("20", 33, 683, pid="20-1")
    d.underbar("21", 699, 1301)
    d.underbar("20", 1317, W - 33, pid="20-2")
    d.opora("22", 691, pid="22-1")
    d.opora("22", 1309, pid="22-2")
    for i, (y0, y1) in enumerate(((169, 359), (370, 560), (570, 760))):
        d.drawer(str(i + 1), ("23.1", "23.2", "23.3", "23.4", "23.5"), 696, y0, 1304, y1, 712, 1288, 128)
    d.door("24", 83, 169, 687, 760, "left", hx=646.5, hy=464.5, pid="24-1")
    d.door("24", 1314, 169, W - 82, 760, "right", hx=1353.5, hy=464.5, pid="24-2")
    d.back("27", 28, 162, 691, 839, pid="27-1")
    d.back("27", 1309, 162, W - 28, 839, pid="27-2")
    d.back("28", 691, 162, 1309, 839)
    rows = [("1", SG, 1), ("2", SV, 1), ("3", SV, 1), ("4", SG, 1), ("5", PG, 1), ("6", PG, 1), ("7", "Полка", 2),
            ("8", SG, 2), ("9", BR, 1), ("10", BR, 1), ("11", BV, 1), ("12", BV, 1), ("13", BR, 1), ("14", BR, 2),
            ("15", BV, 1), ("16", BV, 1), ("17", BR, 1), ("18", BV, 1), ("19", BV, 1), ("20", "Брусок", 2),
            ("21", "Брусок", 1), ("22", "Опора", 2), ("23.1", "Стенка передняя", 3), ("23.2", "Стенка боковая", 3),
            ("23.3", "Стенка боковая", 3), ("23.4", "Стенка задняя", 3), ("23.5", "Дно", 3), ("24", "Дверь", 2),
            ("25", "Вставка", 1), ("26", "Вставка", 1), ("27", SZ, 2), ("28", SZ, 1)]
    d.write("П6.606.0.09", "Тумба «Гранде»", "living", 93, rows=rows, is_pdf="IS-P6-606-0-09-Tumba.pdf",
            cut_note="the drawer rows 23.1–23.5 are per drawer (row 23 «Ящик выдвижной, в т. ч. (каждый) — 3»)")


def tv(did, W, cols, ns=None):
    """TV units 0.02 / 0.06: drawers along the bottom, open niches over them, the niche floor 5 on the lower walls."""
    d = Design(did, W, 540, 616, "old", g=5)
    d.frame("13", "14", "19", "20", "21", "22", "11", "15", "16", "12", "17", "18", "27", "28", "1")
    d.sides("2", "3")
    d.bottom("4")
    d.hwall("5", 33, W - 33, 374)
    d.vwall("10", 64, 173, 358, pid="10-1")
    d.vwall("10", W - 80, 173, 358, pid="10-2")
    parts_n = (("6", "8"), ("7", "9"))
    for i, xp in enumerate(cols[1:]):
        d.vwall(parts_n[i][0], xp, 173, 358)
        d.vwall(parts_n[i][1], xp, 374, 600, z1=d.zc - 16)
        d.opora("29", xp + 8, pid=f"29-{i + 1}")
    d.underbar("23", 33, W - 33)
    edges = [80] + [x for xp in cols[1:] for x in (xp, xp + 16)] + [W - 80]
    for i in range(len(edges) // 2):
        o0, o1 = edges[2 * i], edges[2 * i + 1]
        fx0 = 84 if i == 0 else o0 - 4
        fx1 = W - 84 if i == len(edges) // 2 - 1 else o1 + 4
        n = str(24 + i)
        d.drawer(n, (f"{n}.5", f"{n}.1", f"{n}.2", f"{n}.3", f"{n}.4"), fx0, 169, fx1, 366, o0 + 13, o1 - 13, 120,
                 L=450)
    d.back("30", 28, 162, W - 28, 366)
    d.back("31", 28, 366, W - 28, 605)
    return d


def m0_02():
    """Тумба ТВ 2000 × 540 × 616 (P6.606.0.02): three drawers under three open niches."""
    d = tv("grande-0-02", 2000, (0, 683, 1301))
    rows = [("1", SG, 1), ("2", SV, 1), ("3", SV, 1), ("4", SG, 1), ("5", SG, 1), ("6", PG, 1), ("7", PG, 1),
            ("8", PG, 1), ("9", PG, 1), ("10", PG, 2), ("11", BR, 1), ("12", BR, 1), ("13", BV, 1), ("14", BV, 1),
            ("15", BR, 1), ("16", BR, 1), ("17", BR, 1), ("18", BR, 1), ("19", BV, 1), ("20", BV, 1), ("21", BV, 1),
            ("22", BV, 1), ("23", "Брусок", 1)] + drawer_rows("24", 1) + drawer_rows("25", 1) + \
        drawer_rows("26", 1) + [("27", "Вставка", 1), ("28", "Вставка", 1), ("29", "Опора", 2), ("30", SZ, 1),
                                ("31", SZ, 1)]
    d.write("П6.606.0.02", "Тумба ТВ «Гранде»", "living", 93, rows=rows, is_pdf="IS-P6-606-0-02-Tumba-TV.pdf",
            cut_note="the table picture of p. 1: the reference parse lost rows 19, 20 and wrote the drawer rows as "
                     "241…265 — they are 24.1…24.5, 25.1…25.5, 26.1…26.5 (per drawer, 1 each)")


def m0_06():
    """Тумба ТВ 1382 × 540 × 616 (by catalogue p. 93: the 0.02 unit with two columns)."""
    d = tv("grande-0-06", 1382, (0, 683))
    d.write("П6.606.0.06", "Тумба ТВ «Гранде»", "living", 93, note="по каталогу (конструкция 0.02)")


def shelf(did, W, code, is_pdf=None):
    """Полка 266 × 270 hung on the wall: the back board 1 (16) and the shelf 2 (16) screwed to it 22 over its edge."""
    d = Design(did, W, 266, 270, "old", g=0)
    d.add("1", [0, 0, 0, W, 270, 16], grain="x")
    d.add("2", [0, 22, 16, W, 38, 266], grain="x")
    return d


def m0_10():
    d = shelf("grande-0-10", 2000, "П6.606.0.10")
    rows = [("1", SV, 1), ("2", SG, 1)]
    d.write("П6.606.0.10", "Полка «Гранде»", "decor", 93, rows=rows, is_pdf="IS-P6-606-0-10-Polka.pdf", mount="wall",
            cut_note="the table has no text layer: transcribed from the picture of p. 1; sizes from the front / side "
                     "views (their x and y scales differ: 8.9 and 6.0 mm/pt)")


def m0_11():
    d = shelf("grande-0-11", 1380, "П6.606.0.11")
    d.write("П6.606.0.11", "Полка «Гранде»", "decor", 93, mount="wall", note="по каталогу (конструкция 0.10)")

# ================================================================================ tables, desks
def leg_l(d, n_a, n_b, x_left, front, pid, h0, h1, ins=True, a_w=80, b_d=80, t=25):
    """A table leg: an L of a face board A (a_w wide along x, t thick) and a side board B (t thick, b_d deep) behind it,
    with a black insert on top (h1 .. h1 + 10). x_left: the leg's outer side is x = 0 (True) or x = W (False); front:
    the face board is at z = B (True) or z = 0 (False)."""
    W, B = d.W, d.B
    xa0, xa1 = (0, a_w) if x_left else (W - a_w, W)
    xb0, xb1 = (0, t) if x_left else (W - t, W)
    za0, za1 = (B - t, B) if front else (0, t)
    zb0, zb1 = (B - t - b_d, B - t) if front else (t, t + b_d)
    d.add(n_a, [xa0, h0, za0, xa1, h1, za1], pid=f"{n_a}-{pid}", grain="y")
    d.add(n_b, [xb0, h0, zb0, xb1, h1, zb1], pid=f"{n_b}-{pid}", grain="y")
    k = len([p for p in d.parts if str(p.get("id", "")).startswith("glide")])
    for cx, cz in (((xa0 + xa1) / 2, (za0 + za1) / 2), ((xb0 + xb1) / 2, (zb0 + zb1) / 2)):
        k += 1
        d.add(None, [cx - 10, 0, cz - 10, cx + 10, h0, cz + 10], pid=f"glide-{k}", mat="black", shape="circle", edge=0.5)
    if ins:
        z0, z1 = min(za0, zb0), max(za1, zb1)
        pts = [(xa0, za0), (xa1, za0), (xa1, za1), (xa0, za1)]
        # outline of the L in the top plane
        if front:
            poly = [(xa0, za1), (xa1, za1), (xa1, za0), (xb1 if x_left else xb0, za0),
                    (xb1 if x_left else xb0, zb0), (xb0 if x_left else xb1, zb0)]
        else:
            poly = [(xa0, za0), (xa1, za0), (xa1, za1), (xb1 if x_left else xb0, za1),
                    (xb1 if x_left else xb0, zb1), (xb0 if x_left else xb1, zb1)]
        ol = "M " + " L ".join(f"{x:g} {z:g}" for x, z in poly) + " Z"
        d.add(None, [min(xa0, xb0), h1, z0, max(xa1, xb1), h1 + 10, z1], pid=f"insert-{pid}", mat="black", edge=0.5,
              shape="path", outline=ol)


def desk(did, W, B=710, H=760, drawers=False):
    """Desks 2.17 / 2.14 and the dressing table 1.17: four L legs (boards 6 + 7, 8 + 9) with black inserts, the top 1
    (25) on them, side panels 2 / 3 between the legs, the modesty panel 4 at the back and the front bar 5 under the top
    (1.17: two drawers in its place)."""
    d = Design(did, W, B, H, "new", g=4)
    top_y = H - 25
    legs = (("6", "7", True, True, "fl"), ("8", "9", False, True, "fr"), ("8", "9", True, False, "bl"),
            ("6", "7", False, False, "br"))
    for na, nb, xl, fr, tag in legs:
        leg_l(d, na, nb, xl, fr, tag, 4, top_y - 10)
    d.add("1", [0, top_y, 0, W, H, B], grain="x")
    d.add("2", [5, 86, 105, 21, top_y, B - 105], grain="z")
    d.add("3", [W - 21, 86, 105, W - 5, top_y, B - 105], grain="z")
    d.add("4", [21, 240, 105, W - 21, top_y, 121], grain="x")
    if not drawers:
        d.add("5", [21, top_y - 80, B - 130, W - 21, top_y, B - 105], grain="x")
        return d
    # dressing table: a floor 10 for two drawers, a middle wall 11, fronts flush with the legs' faces
    xm = W / 2
    d.add("10", [25, top_y - 121, 121, W - 25, top_y - 105, B - 25], grain="x")
    d.add("11", [xm - 8, top_y - 105, 121, xm + 8, top_y, B - 16], grain="y")
    for i, (fx0, fx1, bx0, bx1) in enumerate(((83, xm - 3, 96, xm - 21), (xm + 3, W - 83, xm + 21, W - 96))):
        d.drawer(str(i + 1), ("12", "13", "14", "15", "16"), fx0, top_y - 105, fx1, top_y - 5, bx0, bx1, 70, L=300)
    return d


def m2_17():
    d = desk("grande-2-17", 1160)
    rows = [("1", "Крышка", 1), ("2", SV, 1), ("3", SV, 1), ("4", "Царга", 1), ("5", "Брусок", 1), ("6", "Опора", 2),
            ("7", "Опора", 2), ("8", "Опора", 2), ("9", "Опора", 2)]
    d.write("П6.606.2.17", "Стол письменный «Гранде»", "office", 93, rows=rows, is_pdf="P6-606-2-17-Stol-pismennyiy.pdf",
            cut_note="the table prints no sizes: read off the front / side views of p. 1 (1160 × 710 as the catalogue; the "
                     "top view's dimension says 1150 × 700 — see notes); the black inserts are hardware («Декоративная "
                     "вставка», 2 + 2)")


def m2_14():
    d = desk("grande-2-14", 1610)
    d.write("П6.606.2.14", "Стол письменный «Гранде»", "office", 93, note="по каталогу (конструкция 2.17)")


def m1_17():
    d = desk("grande-1-17", 1156, B=456, drawers=True)
    d.write("П6.606.1.17", "Стол туалетный «Гранде»", "bedroom", 93,
            note="по каталогу (конструкция стола 2.17, два ящика в царге)")


def m2_15():
    """Тумба 420 × 400 × 600 on four castors (by catalogue p. 92–93): a plain box, top 25, three drawers."""
    d = Design("grande-2-15", 420, 400, 600, "new", g=0)
    W, B = 420, 400
    for i, (x, z) in enumerate(((40, 40), (W - 40, 40), (40, B - 60), (W - 40, B - 60))):
        d.add(None, [x - 18, 0, z - 18, x + 18, 40, z + 18], pid=f"castor-{i + 1}", kind="tube", mat="black")
    d.add("1", [0, 575, 0, W, 600, B], grain="x")
    d.add("2", [0, 40, 0, 16, 575, B - 16], grain="y")
    d.add("3", [W - 16, 40, 0, W, 575, B - 16], grain="y")
    d.add("4", [16, 40, 0, W - 16, 56, B - 16], grain="x")
    d.back("5", 11, 45, W - 11, 580)
    for i, (y0, y1) in enumerate(((42, 217), (220, 395), (398, 573))):
        d.drawer(str(i + 1), ("6", "7", "8", "9", "10"), 2, y0, W - 2, y1, 29, W - 29, 120)
    d.write("П6.606.2.15", "Тумба «Гранде»", "office", 93, note="по каталогу, на колёсах")


def m0_13():
    """Стол журнальный 1300 × 650 × 500 (by catalogue p. 91 / 93): four L legs with inserts, aprons, a shelf below."""
    d = Design("grande-0-13", 1300, 650, 500, "new", g=4)
    W, B = 1300, 650
    for na, nb, xl, fr, tag in (("2", "3", True, True, "fl"), ("2", "3", False, True, "fr"),
                                ("2", "3", True, False, "bl"), ("2", "3", False, False, "br")):
        leg_l(d, na, nb, xl, fr, tag, 4, 465)
    d.add("1", [0, 475, 0, W, 500, B], grain="x")
    d.add("4", [80, 395, 9, W - 80, 475, 25], pid="4-1", grain="x")
    d.add("4", [80, 395, B - 25, W - 80, 475, B - 9], pid="4-2", grain="x")
    d.add("5", [9, 395, 105, 25, 475, B - 105], pid="5-1", grain="z")
    d.add("5", [W - 25, 395, 105, W - 9, 475, B - 105], pid="5-2", grain="z")
    d.add("6", [25, 100, 25, W - 25, 125, B - 25], grain="x")
    d.write("П6.606.0.13", "Стол журнальный «Гранде»", "tables", 93, note="по каталогу")


def m4_12():
    """Стол обеденный раздвижной 1500 / 2000 × 900 × 760 (P6.606.4.12), built extended (the leaf 8 in place): the frame
    of long bars 2 (16) and end bars 3 (25) with cross bars 9 carrying the runners, L legs 4 + 6 / 5 + 7 bolted to the
    frame's corners outside (125 × 125), the top halves 1 slide apart on the runners."""
    d = Design("grande-4-12", 2000, 900, 760, "new", g=5)
    W, B = 2000, 900
    xl, xr = 253.5, 1746.5              # the legs' outer faces (frame 1443 + 2 × 25)
    for n_a, n_b, x0, sgn in (("4", "6", xl, 1), ("5", "7", xr, -1)):
        for zf, tag in ((True, "f"), (False, "b")):
            za0, za1 = (B - 28, B - 3) if zf else (3, 28)
            zb0, zb1 = (B - 128, B - 28) if zf else (28, 128)
            xa = (x0, x0 + 125) if sgn > 0 else (x0 - 125, x0)
            xb = (x0, x0 + 25) if sgn > 0 else (x0 - 25, x0)
            d.add(n_a, [xa[0], 5, za0, xa[1], 735, za1], pid=f"{n_a}-{tag}", grain="y")
            d.add(n_b, [xb[0], 5, zb0, xb[1], 735, zb1], pid=f"{n_b}-{tag}", grain="y")
            for cx, cz in (((xa[0] + xa[1]) / 2, (za0 + za1) / 2), ((xb[0] + xb[1]) / 2, (zb0 + zb1) / 2)):
                d.add(None, [cx - 10, 0, cz - 10, cx + 10, 5, cz + 10], pid=f"glide-{n_a}{tag}{int(cx)}", mat="black",
                      shape="circle", edge=0.5)
    d.add("2", [xl + 25, 615, 28, xr - 25, 735, 44], pid="2-1", grain="x")
    d.add("2", [xl + 25, 615, B - 44, xr - 25, 735, B - 28], pid="2-2", grain="x")
    d.add("3", [xl + 25, 615, 44, xl + 50, 735, B - 44], pid="3-1", grain="z")
    d.add("3", [xr - 50, 615, 44, xr - 25, 735, B - 44], pid="3-2", grain="z")
    d.add("9", [892, 615, 44, 908, 735, B - 44], pid="9-1", grain="z")
    d.add("9", [1092, 615, 44, 1108, 735, B - 44], pid="9-2", grain="z")
    d.add("1", [0, 735, 0, 750, 760, B], pid="1-1", grain="x")
    d.add("8", [750, 735, 0, 1250, 760, B], grain="z")
    d.add("1", [1250, 735, 0, W, 760, B], pid="1-2", grain="x")
    rows = [("1", None, [750, 900, 25], 2), ("2", None, [1443, 120, 16], 2), ("3", None, [812, 120, 25], 2),
            ("4", None, [730, 125, 25], 2), ("5", None, [730, 125, 25], 2), ("6", None, [730, 100, 25], 2),
            ("7", None, [730, 100, 25], 2), ("8", None, [500, 900, 25], 1), ("9", None, [813, 120, 16], 2)]
    d.write("П6.606.4.12", "Стол обеденный «Гранде»", "tables", 93, rows=rows,
            is_pdf="P6-606-4-12-stol-obedennyiy-ispr.pdf", note="раздвижной 1500 / 2000; построен разложенным",
            cut_note="table of p. 4 as printed (the reference JSON agrees); 9 is built 812 (between the long bars 2, "
                     "±1 mm)")


# ================================================================================ beds, mirrors
def bed(did, W):
    """Beds «Гранде» (P6.606.1.09 and by catalogue the doubles): x = width, z from the headboard (wall) to the foot.
    Headboard 1 (25) framed on its face by strips 4 (top, full width) and 5 (sides); side rails 3 (200 × 25) between
    the headboard and the footboard 2, whose outer face carries a frame of strips 6 (top), 7 (corner legs) and 8
    (bottom); glides «ФБ 482» (4 mm); the metal base «m» and a mattress on it."""
    d = Design(did, W, 2085, 954, "new", g=4)
    L = 2085
    fx0, fx1 = 78, W - 78
    d.add("1", [0, 4, 0, W, 954, 25], grain="x")
    d.add("4", [0, 874, 25, W, 954, 50], grain="x")
    d.add("5", [0, 4, 25, 80, 874, 50], pid="5-1", grain="y")
    d.add("5", [W - 80, 4, 25, W, 874, 50], pid="5-2", grain="y")
    d.add("3", [80, 144, 25, 105, 344, L - 50], pid="3-1", grain="z")
    d.add("3", [W - 105, 144, 25, W - 80, 344, L - 50], pid="3-2", grain="z")
    d.add("2", [fx0, 4, L - 50, fx1, 344, L - 25], grain="x")
    d.add("6", [fx0, 264, L - 25, fx1, 344, L], grain="x")
    d.add("7", [fx0, 4, L - 25, fx0 + 80, 264, L], pid="7-1", grain="y")
    d.add("7", [fx1 - 80, 4, L - 25, fx1, 264, L], pid="7-2", grain="y")
    d.add("8", [fx0 + 80, 4, L - 25, fx1 - 80, 84, L], grain="x")
    k = 0
    for cx, cz in ((40, 12.5), (W - 40, 12.5), (fx0 + 40, L - 37.5), (fx1 - 40, L - 37.5), (40, 37.5),
                   (W - 40, 37.5)):
        k += 1
        d.add(None, [cx - 10, 0, cz - 10, cx + 10, 4, cz + 10], pid=f"glide-{k}", mat="black", shape="circle", edge=0.5)
    mw = W - 220
    x0 = (W - mw) / 2
    d.add(None, [x0, 250, 30, x0 + 30, 290, 2030], pid="base-l", mat="black", covers=["m"])
    d.add(None, [W - x0 - 30, 250, 30, W - x0, 290, 2030], pid="base-r", mat="black")
    d.add(None, [x0 + 30, 282, 30, W - x0 - 30, 290, 2030], pid="slats", mat="door_enamel_whitey#c8b089")
    d.add(None, [x0, 290, 30, W - x0, 490, 2030], pid="mattress", kind="mattress")
    return d


def m1_09():
    d = bed("grande-1-09", 1120)
    rows = [("1", "Спинка", [1120, 950, 25], 1), ("2", "Спинка", [964, 340, 25], 1), ("3", "Царга", [2010, 200, 25], 2),
            ("4", "Накладка", [1120, 80, 25], 1), ("5", "Накладка", [870, 80, 25], 2), ("6", "Накладка", [964, 80, 25], 1),
            ("7", "Накладка", [260, 80, 25], 2), ("8", "Накладка", [804, 80, 25], 1)]
    d.write("П6.606.1.09", "Кровать 1-09 «Гранде»", "bedroom", 93, rows=rows, is_pdf="P6-606-1-09-Krovat-1-09-IS.pdf",
            size=[1120, 2085, 954], note="сп. место 900 × 2000, металлокаркас в комплекте",
            cut_note="table of p. 4 (sizes in the text layer), transcribed; the reference JSON had no rows")


def m_bed(tail, W, sleep):
    d = bed(f"grande-{tail}", W)
    d.write(f"П6.606.{tail.replace('-', '.')}", f"Кровать {'1' if W < 1500 else '2'}-{sleep // 100} «Гранде»", "bedroom",
            93, size=[W, 2085, 954], note=f"по каталогу (конструкция 1.09), сп. место {sleep} × 2000")


def m1_11():
    m_bed("1-11", 1420, 1200)


def m1_12():
    m_bed("1-12", 1620, 1400)


def m1_08():
    m_bed("1-08", 1820, 1600)


def m1_13():
    m_bed("1-13", 2020, 1800)


def m1_10():
    """Зеркало 1000 × 20 × 700 (P6.606.1.10): the mirror 2 glued on the board 1, 20 mm of oak round it."""
    d = Design("grande-1-10", 1000, 20, 700, "new", g=0)
    d.add("1", [0, 0, 0, 1000, 700, 16], grain="x")
    d.add("2", [20, 20, 16, 980, 680, 20], kind="mirror")
    rows = [("1", "Щит", [700, 1000, 16], 1), ("2", "Зеркало", [660, 960, 4], 1)]
    d.write("П6.606.1.10", "Зеркало «Гранде»", "decor", 93, rows=rows, is_pdf="P6-606-1-10-Zerkalo-IS.pdf",
            mount="wall", note="каталог с. 93: B21, с. 91 и инструкция: 16 + 4 = 20",
            cut_note="table of p. 4 as printed (the reference JSON agrees)")


# ================================================================================ hall (by catalogue)
def m3_05():
    """Зеркало 1150 × 32 × 680: a board 16 with the mirror, framed by 80 mm strips 16 thick."""
    d = Design("grande-3-05", 1150, 32, 680, "old", g=0)
    W, H = 1150, 680
    d.add("1", [0, 0, 0, W, H, 16], grain="x")
    d.add("2", [0, 0, 16, W, 80, 32], pid="2-1", grain="x")
    d.add("2", [0, H - 80, 16, W, H, 32], pid="2-2", grain="x")
    d.add("3", [0, 80, 16, 80, H - 80, 32], pid="3-1", grain="y")
    d.add("3", [W - 80, 80, 16, W, H - 80, 32], pid="3-2", grain="y")
    d.add("4", [80, 80, 16, W - 80, H - 80, 20], kind="mirror")
    d.write("П6.606.3.05", "Зеркало «Гранде»", "hall", 93, mount="wall", note="по каталогу")


def m3_04():
    """Вешалка 1150 × 240 × 1475 on the wall: a recessed panel in a frame of 80 mm bars, a shelf 240 on top, five
    black hooks."""
    d = Design("grande-3-04", 1150, 240, 1475, "old", g=0)
    W, H = 1150, 1475
    d.add("1", [80, 80, 0, W - 80, H - 80, 16], grain="y")
    d.add("2", [0, 0, 0, 80, H - 80, 32], pid="2-1", grain="y")
    d.add("2", [W - 80, 0, 0, W, H - 80, 32], pid="2-2", grain="y")
    d.add("3", [80, 0, 0, W - 80, 80, 32], grain="x")
    d.add("4", [0, H - 80, 0, W, H - 25, 32], grain="x")
    d.add("5", [0, H - 25, 0, W, H, 240], grain="x")
    for i, (x, y) in enumerate(((380, 1150), (575, 1150), (770, 1150), (477, 1000), (672, 1000))):
        d.add(None, None, pid=f"hook-{i + 1}", kind="handle", model="knob", mat="black", at=[x, y], d=22, t=12,
              standoff=40, z=16)
    d.write("П6.606.3.04", "Вешалка «Гранде»", "hall", 93, mount="wall", note="по каталогу, 5 крючков")


def hall(did, W, H, g=5):
    d = Design(did, W, 420, H, "old", g=g)
    d.frame("12", "13", "16", "20", "17", "21", "10", "14", "18", "11", "15", "19", "23", "24", "3")
    d.sides("1", "2")
    d.bottom("6")
    d.underbar("22", 33, W - 33)
    return d


def m3_01():
    """Шкаф для одежды 680 × 420 × 2002 (by catalogue: the 0.01 carcass behind one full-height door, shelves)."""
    d = hall("grande-3-01", 680, 2002, g=4)
    W = d.W
    d.hwall("7", 33, W - 33, 1650)
    for i, y in enumerate((520, 900, 1280)):
        d.add("9", [34, y - 16, 30, W - 34, y, 380], pid=f"9-{i + 1}", grain="x")
    d.door("25", 81, 169, W - 83, 1912, "left", hx=557.5, hy=1050)
    d.back("27", 27, 161, W - 27, 1991)
    d.write("П6.606.3.01", "Шкаф для одежды «Гранде»", "hall", 93, note="по каталогу (конструкция 0.01)")


def m3_02():
    """Тумба 1150 × 420 × 525 (a bench): one wide drawer under the top."""
    d = hall("grande-3-02", 1150, 525)
    W = d.W
    d.vwall("4", 64, 173, 509, z1=d.zc - 16)
    d.vwall("5", W - 80, 173, 509, z1=d.zc - 16)
    d.drawer("1", ("26.5", "26.1", "26.2", "26.3", "26.4"), 81, 169, W - 81, 435, 93, W - 93, 150)
    d.back("27", 27, 162, W - 27, 514)
    d.write("П6.606.3.02", "Тумба «Гранде»", "hall", 93, note="по каталогу")


def m3_03():
    """Тумба 1150 × 420 × 1124: two drawers over two doors, a partition in the middle."""
    d = hall("grande-3-03", 1150, 1124)
    W = d.W
    d.vwall("4", 567, 173, 1108, z1=d.zc - 16)
    d.hwall("7", 33, 567, 854, pid="7-1")
    d.hwall("7", 583, W - 33, 854, pid="7-2")
    d.vwall("5", 64, 854, 1108, z1=d.zc - 16)
    d.vwall("8", W - 80, 854, 1108, z1=d.zc - 16)
    d.add("9", [34, 494, 30, 566, 510, 380], pid="9-1", grain="x")
    d.add("9", [584, 494, 30, W - 34, 510, 380], pid="9-2", grain="x")
    d.drawer("1", ("26.5", "26.1", "26.2", "26.3", "26.4"), 81, 859, 572, 1034, 93, 554, 128)
    d.drawer("2", ("26.5", "26.1", "26.2", "26.3", "26.4"), 578, 859, W - 81, 1034, 596, W - 93, 128)
    d.door("25", 81, 169, 572, 849, "left", hx=480, hy=790, hdir="right", pid="25-1")
    d.door("25", 578, 169, W - 81, 849, "right", hx=670, hy=790, hdir="right", pid="25-2")
    d.back("27", 27, 162, W - 27, 1113)
    d.write("П6.606.3.03", "Тумба «Гранде»", "hall", 93, note="по каталогу")

# ================================================================================ output
FINISHES = [
    {"id": "grande-yukon", "name": "Дуб Юкон 358 SWN", "body": "door_enamel_whitey#8c8685", "swatch": "#8c8685",
     "roles": {"handle": "chrome#b3b3b3"}},
    {"id": "grande-stirling", "name": "Дуб Стирлинг 374 SWN", "body": "door_enamel_whitey#8b6b4b", "swatch": "#8b6b4b",
     "roles": {"handle": "black"}},
]
COLLECTION = {"id": SLUG, "name": "Гранде", "brand": "Пинскдрев", "finishes": ["grande-yukon", "grande-stirling"],
              "metal": "chrome",
              "note": "Каталог «Корпусная мебель ч. II» 2025, PDF с. 87–93 (каталог 170–183). Рамочная конструкция: угловые "
                      "стойки из брусков 80 (гостиная — 16 мм, стойка 80 × 80; спальня — 25 мм, 80 × 105) на опорах "
                      "ФБ 482, чёрные вставки 10 мм на передних стойках, царги 80 вокруг крышки 16, нижние царги 80; "
                      "корпус ЛДСП 16 внутри рамы; фасады 16 заподлицо с рамой, рамочные двери со стеклом у витрин; "
                      "ящики на шариковых направляющих; ручки-скобы С36 (серебро у «Дуб Юкон», чёрные у «Дуб Стирлинг»)."}

ALL = [m0_01, m0_02, m0_04, m0_05, m0_06, m0_07, m0_09, m0_10, m0_11, m0_13, m1_01, m1_02, m1_04, m1_05, m1_06, m1_08, m1_09, m1_10, m1_11, m1_12, m1_13, m1_16, m1_17, m2_14, m2_15, m2_17, m3_01, m3_02, m3_03, m3_04, m3_05, m4_12]


def main():
    for f in ALL:
        f()
    frag = {"finishes": FINISHES, "profiles": {}, "collections": [COLLECTION], "models": MODELS}
    with open(os.path.join(HERE, f"{SLUG}_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)
    for did, (code, rows, note) in CUTLISTS.items():
        with open(os.path.join(DESIGNS, did + ".json")) as fh:
            d = json.load(fh)
        sized = all(len(r) == 4 for r in rows)
        src = ("the instruction's table (numbers, names, sizes, counts)" if sized else
               "the instruction's table (numbers, names, counts; the table prints no sizes): the sizes are read off the "
               "vector drawing (front / side / top views, scale from the overall size, ±1.5 mm) and the collection's "
               "construction — see notes/grande.md")
        out = {"code": code, "source": src, "rows": sized_rows(d, rows)}
        if note:
            out["note"] = note
        with open(os.path.join(HERE, "cutlists", did + ".json"), "w") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"{len(MODELS)} designs, {len(CUTLISTS)} cut lists")


if __name__ == "__main__":
    main()
