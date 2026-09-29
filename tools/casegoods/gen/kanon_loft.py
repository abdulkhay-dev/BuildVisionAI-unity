"""«Каньон Лофт» (Пинскдрев, П3.0561): living room, bedroom and study in «Дуб Каньон» oak with a black «Черный 660» frame.

Construction (instructions П561.01/.02/.03-1/.09/.12/.18/.19/.20/.28/.30-1/.31 and П3.561.1.01/1.02/1.03):
  * the carcass is ЛДСП 16 oak: sides 322 deep standing on the black back plinth board (88 high), 92 mm above the floor
    (4 mm nail glides + 88), a top 400 deep over everything (2 mm proud of the frame at the sides and the front);
  * the «loft frame» is ЛДСП 16 black boards 76 wide: a post on the front edge of each side (16 wide from the front, 76
    deep: z 322..398) from the glides up to the top, a bar lying under the top between the posts, a bar lying on the floor
    between the posts (the front runner of the sled), the back plinth board and middle boards 250 × 88 under the
    partitions (dowelled to the floor bar): seen from the side the base is a closed black loop;
  * inside: a black bottom (L − 36) × 379 over z 19..398, partitions 379 deep, an oak apron 128 high under the top bar,
    set 16 mm behind the frame face (the LED strip lies in a groove of the top bar in front of it);
  * backs ДВП (венге / черная / белая) on the back edges of the inner panels (z 16..19, stabiliser brackets), split per
    section; vitrines have a black ЛДСП back of their own between their top and bottom shelves;
  * fronts ЛДСП 16 oak without handles (push-to-open): inset doors (inner hinges H=0) between the side and a 50 mm oak
    strip beside the partition; overlay doors and drawer fronts (half-overlay hinges) in front of the frame, their outer
    edge 2 mm in from the carcass side, covering the partition and all but 10–20 mm of the strip;
  * drawer boxes: the front is the box's front wall; sides 350, back standing on the ДВП bottom (in grooves of the sides
    and the front), ball runners 12.75 mm a side;
  * LED variants («с подсветкой», the П3.0561.0.2x/0.3x/0.40 codes) add the strip under the top bar and the vertical
    overlay profiles of the vitrines.
Coordinates: x from the left, y up from the floor, z from the wall (back) to the front; mm.

    /private/tmp/claude-501/venv/bin/python tools/casegoods/gen/kanon_loft.py
"""
import copy
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "kanon-loft"
ZS, ZP = 322.0, 398.0          # sides' front edge / the frame's face
ZI = 19.0                      # the inner panels' back edge (the backs lie at 16..19)
FR = "frame"                   # «Черный 660 ТМ» black ЛДСП role
WG = "wenge"                   # ДВП ламинированная ВЕНГЕ role


class D:
    """A design being written: parts with unique ids, moves."""

    def __init__(self, did, size):
        self.did, self.size, self.parts, self.moves, self.cnt = did, size, [], [], {}

    def add(self, n, box, kind=None, mat=None, pid=None, **kw):
        p = {}
        if n is not None:
            p["n"] = str(n)
        if pid is None:
            key = str(n) if n is not None else "p"
            c = self.cnt.get(key, 0) + 1
            self.cnt[key] = c
            pid = key if (c == 1 and n is not None) else f"{key}-{c}"
        if pid != p.get("n"):
            p["id"] = pid
        if kind:
            p["kind"] = kind
        if mat:
            p["mat"] = mat
        p.update(kw)
        p["box"] = [round(v, 2) for v in box]
        self.parts.append(p)
        return pid

    def move(self, **m):
        self.moves.append(m)

    def write(self):
        return dump(self.did, self.size, self.parts, self.moves)


def glide(d, x, z, r=7):
    d.add(None, [x - r, 0, z - r, x + r, 4, z + r], mat=FR, pid=f"glide-{len([p for p in d.parts if 'glide' in p.get('id', '')]) + 1}",
          shape="circle", edge=0.5, covers=["опора"])


def frame(d, W, H, n, mids=(), apron_h=128.0, zb0=ZI, bottom=True, apron=True, zpost=ZS, mid_len=250.0):
    """The common Каньон carcass and loft frame. n: dict of cut-list numbers: top, sL, sR, pL, pR, tb, ap, fb, bb, bot,
    mid (numbers may be None for modules built by photo)."""
    g = n.get
    d.add(g("top"), [0, H - 16, 0, W, H, 400], grain="x", pid=None if g("top") else "top")
    d.add(g("sL"), [2, 92, 0, 18, H - 16, ZS], pid=None if g("sL") else "side-l")
    d.add(g("sR"), [W - 18, 92, 0, W - 2, H - 16, ZS], pid=None if g("sR") else "side-r")
    d.add(g("pL"), [2, 4, zpost, 18, H - 16, ZP], mat=FR, pid=None if g("pL") else "post-l")
    d.add(g("pR"), [W - 18, 4, zpost, W - 2, H - 16, ZP], mat=FR, pid=None if g("pR") else "post-r")
    d.add(g("tb"), [18, H - 32, ZS, W - 18, H - 16, ZP], mat=FR, pid=None if g("tb") else "bar-top")
    if apron:
        d.add(g("ap"), [18, H - 32 - apron_h, 366, W - 18, H - 32, 382], grain="x", pid=None if g("ap") else "apron")
    d.add(g("fb"), [18, 4, ZS, W - 18, 20, ZP], mat=FR, pid=None if g("fb") else "bar-floor")
    d.add(g("bb"), [2, 4, 0, W - 2, 92, 16], mat=FR, pid=None if g("bb") else "plinth-back")
    if bottom:
        d.add(g("bot"), [18, 92, zb0, W - 18, 108, 382 if zb0 > ZI else ZP], mat=FR, pid=None if g("bot") else "bottom")
    for i, x in enumerate(mids):
        d.add(g("mid"), [x - 8, 4, ZS - mid_len, x + 8, 92, ZS], mat=FR,
              pid=None if g("mid") else f"plinth-mid-{i + 1}")
    # nail glides: under the posts, the back plinth board and the middle boards
    for x in (10, W - 10):
        glide(d, x, 360)
        glide(d, x, 8)
    for x in mids:
        glide(d, x, 300)


def led_top(d, W, H):
    d.add(None, [18, H - 34, 384, W - 18, H - 32, 396], kind="light", mat="led", pid="led-top", covers=["подсветка"])


def led_vert(d, x0, x1, y0, y1, tag):
    d.add(None, [x0, y0, 36, x1, y1, 46], kind="light", mat="led", pid=f"led-{tag}", covers=["подсветка"])


def back(d, n, box, mat=WG, pid=None):
    x0, y0, x1, y1 = box
    return d.add(n, [x0, y0, 16, x1, y1, 19], kind="back", mat=mat, pid=pid)


def door_inset(d, n, x0, x1, y0, y1, hinge, name, pid=None):
    i = d.add(n, [x0, y0, 382, x1, y1, ZP], kind="front", grain="y", pid=pid)
    d.move(type="door", name=name, parts=[i], hinge=hinge, angle=105)
    return i


def door_overlay(d, n, x0, x1, y0, y1, hinge, name, pid=None):
    i = d.add(n, [x0, y0, ZP, x1, y1, 414], kind="front", grain="y", pid=pid)
    d.move(type="door", name=name, parts=[i], hinge=hinge, angle=105)
    return i


def vitrine_door(d, n, x0, x1, y0, y1, w0, w1, hinge, name):
    """ЛДСП 16 + стекло: an oak part under and over the window, a clear glass glued behind the whole door (it shows
    between the oak parts); the row's count is carried by the upper oak part."""
    b = d.add(None, [x0, y0, 382, x1, w0, ZP], kind="front", grain="y", pid=f"{n}-b-{name}")
    t = d.add(None, [x0, w1, 382, x1, y1, ZP], kind="front", grain="y", pid=f"{n}-t-{name}", covers=[str(n)])
    g = d.add(None, [x0, y0, 378, x1, y1, 382], kind="glass", pid=f"{n}-g-{name}")
    d.move(type="door", name=name, parts=[b, t, g], hinge=hinge, angle=105)


def drawer(d, tag, fn, fbox, cx0, cx1, y0, ns, side=(350, 160), back_h=141, bot=(0, 355), zf=ZP, fz1=414):
    """Front fn over fbox [x0, y0, x1, y1] (in front of zf); box between the column's walls cx0..cx1 (12.75 runner gap
    a side), sides side[0] long × side[1] high, the back back_h standing on the bottom, the ДВП bottom in grooves of the
    sides and 5 mm into the front. ns = (side L, side R, back, bottom) cut-list numbers."""
    fx0, fy0, fx1, fy1 = fbox
    ids = [d.add(fn, [fx0, fy0, zf, fx1, fy1, fz1], kind="front", grain="x", pid=f"{fn}-{tag}" if fn else f"front-{tag}")]
    xb0, xb1 = cx0 + 12.75, cx1 - 12.75
    L, h = side
    z0 = zf - L
    k = ns
    ids.append(d.add(k[0], [xb0, y0, z0, xb0 + 16, y0 + h, zf], mat=None, pid=f"{k[0]}-{tag}" if k[0] else f"bs-l-{tag}"))
    ids.append(d.add(k[1], [xb1 - 16, y0, z0, xb1, y0 + h, zf], pid=f"{k[1]}-{tag}" if k[1] else f"bs-r-{tag}"))
    ids.append(d.add(k[2], [xb0 + 16, y0 + h - back_h, z0, xb1 - 16, y0 + h, z0 + 16], pid=f"{k[2]}-{tag}" if k[2] else f"bb-{tag}"))
    bw = bot[0] or (xb1 - xb0 - 32 + 9.5)
    bx = (xb0 + xb1) / 2
    ids.append(d.add(k[3], [bx - bw / 2, y0 + h - back_h - 4.2, z0, bx + bw / 2, y0 + h - back_h - 1, z0 + bot[1]],
                     kind="back", mat=FR, pid=f"{k[3]}-{tag}" if k[3] else f"bot-{tag}"))
    d.move(type="drawer", name=f"drawer_{tag}", parts=ids, travel=int(L * 0.85))
    return ids


def mirror_x(d, W, did):
    """The mirrored variant (-01): x → W − x, hinges swapped."""
    m = D(did, d.size)
    for p in d.parts:
        q = copy.deepcopy(p)
        b = q["box"]
        q["box"] = [round(W - b[3], 2), b[1], b[2], round(W - b[0], 2), b[4], b[5]]
        m.parts.append(q)
    for mv in d.moves:
        q = copy.deepcopy(mv)
        if q.get("hinge") in ("left", "right"):
            q["hinge"] = "right" if q["hinge"] == "left" else "left"
        if "by" in q:
            q["by"] = [-q["by"][0], q["by"][1], q["by"][2]]
        m.moves.append(q)
    return m


def strip_led(d, did):
    """The variant without LED light (the other code of a pair)."""
    m = D(did, d.size)
    m.parts = [copy.deepcopy(p) for p in d.parts if p.get("kind") != "light"]
    m.moves = copy.deepcopy(d.moves)
    return m


# ------------------------------------------------------------------------------------------------ cut lists
O, B, H_, G, Wt, WH = "ЛДСП 16мм ДУБ КАНЬОН", "ЛДСП 16мм ЧЕРНЫЙ 660 ТМ", "ДВП ламинированная", "Стекло прозрачное 6мм", \
    "ЛДСП 16мм БЕЛЫЙ", "ДВП ламинированная БЕЛАЯ"
MATS = {"O": O, "B": B, "H": H_, "G": G, "W": Wt, "WH": WH}
CUT = {
    "IS-P561-01-Komod-1.pdf": [('1', 'Крышка', 'O', 1, 1400, 400), ('2', 'Стенка горизонтальная', 'O', 1, 868, 379), ('3', 'Дверь', 'O', 1, 426, 628), ('4', 'Стенка вертикальная', 'O', 1, 792, 322), ('5', 'Стенка вертикальная', 'O', 1, 792, 322), ('6', 'Стенка вертикальная', 'O', 1, 632, 379), ('7', 'Стенка передняя', 'O', 3, 930, 216), ('8', 'Стенка передняя', 'O', 1, 1364, 128), ('9', 'Стенка горизонтальная', 'O', 1, 480, 328), ('10', 'Стенка задняя ящика', 'O', 3, 810.5, 141), ('11', 'Стенка боковая ящика', 'O', 3, 350, 160), ('12', 'Стенка боковая ящика', 'O', 3, 350, 160), ('13', 'Стенка вертикальная', 'O', 1, 632, 50), ('14', 'Стенка горизонтальная', 'B', 1, 1364, 379), ('15', 'Стенка вертикальная', 'B', 1, 1396, 88), ('16', 'Стенка горизонтальная', 'B', 1, 1364, 76), ('17', 'Стенка горизонтальная', 'B', 1, 1364, 76), ('18', 'Стенка вертикальная', 'B', 1, 880, 76), ('19', 'Стенка вертикальная', 'B', 1, 880, 76), ('20', 'Стенка вертикальная', 'B', 1, 250, 88), ('21', 'Стенка задняя', 'H', 1, 880, 795), ('22', 'Стенка задняя', 'H', 1, 490, 795), ('23', 'Дно ящика', 'H', 3, 820, 355)],
    "IS-P561-02-Komod-1.pdf": [('1', 'Крышка', 'O', 1, 1846, 400), ('2', 'Стенка горизонтальная', 'O', 1, 818, 379), ('3', 'Дверь', 'O', 2, 426, 628), ('5', 'Стенка вертикальная', 'O', 1, 792, 322), ('6', 'Стенка вертикальная', 'O', 1, 792, 322), ('7', 'Стенка вертикальная', 'O', 1, 632, 379), ('8', 'Стенка вертикальная', 'O', 1, 632, 379), ('9', 'Стенка передняя', 'O', 1, 1810, 128), ('10', 'Стенка передняя', 'O', 3, 930, 216), ('11', 'Стенка горизонтальная', 'O', 1, 480, 328), ('12', 'Стенка горизонтальная', 'O', 1, 480, 328), ('13', 'Стенка задняя ящика', 'O', 3, 760.5, 141), ('14', 'Стенка боковая ящика', 'O', 3, 350, 160), ('15', 'Стенка боковая ящика', 'O', 3, 350, 160), ('16', 'Стенка вертикальная', 'O', 1, 144, 303), ('17', 'Стенка вертикальная', 'O', 2, 632, 50), ('19', 'Стенка горизонтальная', 'B', 1, 1810, 379), ('20', 'Стенка вертикальная', 'B', 1, 1842, 88), ('21', 'Стенка горизонтальная', 'B', 1, 1810, 76), ('22', 'Стенка горизонтальная', 'B', 1, 1810, 76), ('23', 'Стенка вертикальная', 'B', 1, 880, 76), ('24', 'Стенка вертикальная', 'B', 1, 880, 76), ('25', 'Стенка вертикальная', 'B', 2, 250, 88), ('26', 'Стенка задняя', 'H', 1, 830, 795), ('27', 'Стенка задняя', 'H', 2, 490, 795), ('28', 'Дно ящика', 'H', 3, 770, 355)],
    "IS-P561-09-Tumba-1.pdf": [('1', 'Дверь', 'O', 1, 486, 978), ('2', 'Крышка', 'O', 1, 900, 400), ('3', 'Стенка вертикальная', 'O', 1, 932, 379), ('4', 'Стенка вертикальная', 'O', 1, 1092, 322), ('5', 'Стенка вертикальная', 'O', 1, 1092, 322), ('6', 'Стенка горизонтальная', 'O', 1, 424, 379), ('7', 'Полка', 'O', 2, 422, 359), ('8', 'Стенка горизонтальная', 'O', 1, 424, 328), ('9', 'Стенка горизонтальная', 'O', 1, 424, 328), ('10', 'Стенка передняя', 'O', 1, 864, 128), ('11', 'Дверь (ЛДСП + стекло)', 'O', 1, 928, 370), ('13', 'Стенка вертикальная', 'O', 1, 932, 50), ('14', 'Стенка горизонтальная', 'B', 1, 864, 379), ('15', 'Стенка вертикальная', 'B', 1, 1180, 76), ('16', 'Стенка вертикальная', 'B', 1, 1180, 76), ('17', 'Стенка вертикальная', 'B', 1, 896, 88), ('18', 'Стенка горизонтальная', 'B', 1, 864, 76), ('19', 'Стенка горизонтальная', 'B', 1, 864, 76), ('20', 'Стенка вертикальная', 'B', 1, 250, 88), ('21', 'Стенка задняя (ЧЕРНЫЙ 660 WML)', 'B', 1, 424, 448), ('22', 'Стенка задняя', 'H', 1, 440, 1095), ('23', 'Стенка задняя', 'H', 1, 430, 255), ('24', 'Стенка задняя', 'H', 1, 430, 390), ('25', 'Полка стеклянная', 'G', 1, 422, 282)],
    "IS-P561-12-Tumba-1.pdf": [('1', 'Крышка', 'O', 1, 1290, 400), ('2', 'Стенка вертикальная', 'O', 1, 932, 379), ('3', 'Стенка вертикальная', 'O', 1, 932, 379), ('4', 'Стенка вертикальная', 'O', 1, 1092, 322), ('5', 'Стенка вертикальная', 'O', 1, 1092, 322), ('6', 'Дверь откидная', 'O', 1, 486, 446), ('7', 'Стенка передняя', 'O', 1, 1254, 128), ('8', 'Стенка горизонтальная', 'O', 1, 374, 379), ('9', 'Стенка горизонтальная', 'O', 1, 374, 379), ('10', 'Стенка горизонтальная', 'O', 2, 424, 328), ('11', 'Стенка горизонтальная', 'O', 1, 424, 328), ('12', 'Стенка горизонтальная', 'O', 1, 424, 328), ('13', 'Дверь (ЛДСП + стекло)', 'O', 2, 928, 370), ('15', 'Стенка передняя', 'O', 3, 486, 174), ('16', 'Стенка вертикальная', 'O', 2, 932, 50), ('17', 'Стенка боковая ящика', 'O', 3, 350, 128), ('18', 'Стенка боковая ящика', 'O', 3, 350, 128), ('19', 'Стенка задняя ящика', 'O', 3, 316.5, 109), ('20', 'Стенка горизонтальная', 'B', 1, 1254, 379), ('21', 'Стенка вертикальная', 'B', 1, 1286, 88), ('22', 'Стенка горизонтальная', 'B', 1, 1254, 76), ('23', 'Стенка горизонтальная', 'B', 1, 1254, 76), ('24', 'Стенка вертикальная', 'B', 1, 1180, 76), ('25', 'Стенка вертикальная', 'B', 1, 1180, 76), ('26', 'Стенка вертикальная', 'B', 2, 250, 88), ('27', 'Стенка задняя (ЧЕРНЫЙ 660 WML)', 'B', 2, 424, 448), ('28', 'Стенка задняя', 'H', 1, 400, 1095), ('29', 'Стенка задняя', 'H', 2, 430, 390), ('30', 'Дно ящика', 'H', 3, 326, 355), ('31', 'Стенка задняя', 'H', 2, 430, 255), ('32', 'Полка стеклянная', 'G', 2, 422, 282)],
    "IS-P561-18-Tumba-1.pdf": [('1', 'Крышка', 'O', 1, 1980, 400), ('2', 'Стенка передняя', 'O', 1, 1944, 96), ('3', 'Стенка вертикальная', 'O', 1, 402, 322), ('4', 'Стенка вертикальная', 'O', 1, 402, 322), ('5', 'Дверь', 'O', 2, 476, 270), ('7', 'Стенка горизонтальная', 'B', 1, 1944, 338), ('8', 'Стенка горизонтальная', 'B', 1, 984, 338), ('9', 'Стенка вертикальная', 'B', 1, 1976, 88), ('10', 'Стенка горизонтальная', 'B', 1, 1944, 76), ('11', 'Стенка горизонтальная', 'B', 1, 1944, 76), ('12', 'Стенка вертикальная', 'B', 1, 338, 258), ('13', 'Стенка вертикальная', 'B', 1, 338, 258), ('14', 'Стенка вертикальная', 'B', 1, 490, 76), ('15', 'Стенка вертикальная', 'B', 1, 490, 76), ('16', 'Стенка вертикальная', 'B', 2, 262, 112), ('17', 'Стенка вертикальная', 'B', 1, 246, 88), ('18', 'Стенка вертикальная', 'B', 1, 246, 88), ('19', 'Стенка задняя', 'H', 1, 968, 405), ('20', 'Стенка задняя', 'H', 2, 490, 405)],
    "IS-P561-19-SHkaf-2.pdf": [('1', 'Дверь', 'O', 1, 436, 1698), ('2', 'Стенка вертикальная', 'O', 1, 1652, 379), ('3', 'Стенка вертикальная', 'O', 1, 1812, 322), ('4', 'Стенка вертикальная', 'O', 1, 1812, 322), ('5', 'Дверь', 'O', 1, 320, 1648), ('6', 'Крышка', 'O', 1, 800, 400), ('7', 'Стенка горизонтальная', 'O', 1, 374, 379), ('8', 'Стенка горизонтальная', 'O', 1, 374, 379), ('9', 'Полка', 'O', 2, 372, 359), ('10', 'Стенка горизонтальная', 'O', 1, 374, 328), ('11', 'Полка', 'O', 3, 372, 312), ('12', 'Стенка передняя', 'O', 1, 764, 128), ('13', 'Стенка вертикальная', 'O', 1, 1652, 50), ('14', 'Стенка горизонтальная', 'B', 1, 764, 379), ('15', 'Стенка вертикальная', 'B', 1, 1900, 76), ('16', 'Стенка вертикальная', 'B', 1, 1900, 76), ('17', 'Стенка вертикальная', 'B', 1, 796, 88), ('18', 'Стенка горизонтальная', 'B', 1, 764, 76), ('19', 'Стенка горизонтальная', 'B', 1, 764, 76), ('20', 'Стенка вертикальная', 'B', 1, 250, 88), ('21', 'Стенка задняя', 'H', 2, 1815, 385)],
    "IS-P561-20-SHkaf-s-vitrinoy-1.pdf": [('1', 'Дверь', 'O', 1, 436, 1698), ('2', 'Стенка вертикальная', 'O', 1, 1652, 379), ('3', 'Стенка вертикальная', 'O', 1, 1812, 322), ('4', 'Стенка вертикальная', 'O', 1, 1812, 322), ('5', 'Крышка', 'O', 1, 800, 400), ('6', 'Стенка горизонтальная', 'O', 1, 374, 379), ('7', 'Стенка горизонтальная', 'O', 1, 374, 379), ('8', 'Полка', 'O', 2, 372, 359), ('9', 'Стенка горизонтальная', 'O', 1, 374, 328), ('10', 'Стенка горизонтальная', 'O', 1, 374, 328), ('11', 'Стенка передняя', 'O', 1, 764, 128), ('12', 'Стенка вертикальная', 'O', 1, 1652, 50), ('13', 'Дверь (ЛДСП + стекло)', 'O', 1, 1648, 320), ('15', 'Стенка задняя (ЧЕРНЫЙ 660 WML)', 'B', 1, 374, 1168), ('16', 'Стенка горизонтальная', 'B', 1, 764, 379), ('17', 'Стенка вертикальная', 'B', 1, 1900, 76), ('18', 'Стенка вертикальная', 'B', 1, 1900, 76), ('19', 'Стенка вертикальная', 'B', 1, 796, 88), ('20', 'Стенка горизонтальная', 'B', 1, 764, 76), ('21', 'Стенка горизонтальная', 'B', 1, 764, 76), ('22', 'Стенка вертикальная', 'B', 1, 250, 88), ('23', 'Стенка задняя', 'H', 1, 1815, 390), ('24', 'Стенка задняя', 'H', 1, 255, 380), ('25', 'Стенка задняя', 'H', 1, 390, 380), ('27', 'Полка стеклянная', 'G', 2, 372, 282)],
    "IS-P561-28-Stol-obedennyiy-razdvijnoy-1.pdf": [('1', 'Полукрышка', 'O', 2, 902, 651), ('2', 'Вставка', 'O', 1, 902, 500), ('3', 'Стенка вертикальная', 'O', 2, 868, 76), ('4', 'Стенка горизонтальная', 'O', 2, 836, 76), ('5', 'Стенка вертикальная', 'O', 2, 76, 632), ('6', 'Стенка вертикальная', 'O', 2, 76, 632), ('7', 'Стенка горизонтальная', 'B', 2, 1148, 108), ('8', 'Царга', 'B', 2, 1256, 76), ('9', 'Накладка', 'B', 2, 702, 100), ('10', 'Стенка горизонтальная', 'B', 2, 868, 76), ('11', 'Накладка', 'B', 2, 651, 100), ('12', 'Накладка', 'B', 2, 651, 100), ('13', 'Стенка вертикальная', 'B', 2, 740, 76), ('14', 'Стенка вертикальная', 'B', 2, 740, 76), ('15', 'Накладка', 'B', 2, 500, 100), ('16', 'Стенка вертикальная', 'B', 2, 648, 76), ('17', 'Стенка вертикальная', 'B', 2, 648, 76), ('18', 'Стенка горизонтальная', 'B', 4, 76, 76)],
    "IS-P561-30-1-Stol-pismennyiy-1.pdf": [('1', 'Крышка', 'O', 1, 1250, 600), ('2', 'Стенка вертикальная', 'O', 1, 642, 466), ('3', 'Стенка вертикальная', 'O', 1, 642, 466), ('4', 'Стенка вертикальная', 'O', 1, 642, 449), ('5', 'Стенка задняя', 'O', 1, 424, 642), ('6', 'Царга', 'O', 1, 681, 332), ('7', 'Стенка передняя', 'O', 1, 1214, 76), ('8', 'Стенка передняя', 'O', 3, 486, 174), ('9', 'Стенка вертикальная', 'O', 1, 730, 110), ('10', 'Стенка боковая ящика', 'O', 3, 400, 128), ('11', 'Стенка боковая ящика', 'O', 3, 400, 128), ('12', 'Стенка задняя ящика', 'O', 3, 366.5, 109), ('13', 'Стенка передняя', 'O', 1, 76, 518), ('14', 'Стенка горизонтальная', 'B', 1, 525, 424), ('15', 'Стенка горизонтальная', 'B', 1, 1214, 76), ('16', 'Стенка горизонтальная', 'B', 1, 1214, 76), ('17', 'Стенка вертикальная', 'B', 1, 730, 76), ('18', 'Стенка вертикальная', 'B', 1, 730, 76), ('19', 'Стенка вертикальная', 'B', 1, 622, 76), ('20', 'Стенка вертикальная', 'B', 1, 622, 76), ('21', 'Стенка вертикальная', 'B', 1, 454, 88), ('22', 'Стенка горизонтальная', 'B', 1, 525, 76), ('23', 'Стенка вертикальная', 'B', 1, 394, 88), ('24', 'Стенка вертикальная', 'B', 2, 449, 76), ('25', 'Стенка горизонтальная', 'B', 1, 479, 76), ('26', 'Стенка горизонтальная', 'B', 1, 424, 76), ('27', 'Стенка горизонтальная', 'B', 1, 76, 74), ('28', 'Дно ящика', 'H', 3, 405, 377)],
    "IS-P561-31-Stol-pismennyiy-1.pdf": [('1', 'Крышка', 'O', 1, 1600, 600), ('2', 'Стенка вертикальная', 'O', 1, 642, 466), ('3', 'Стенка вертикальная', 'O', 1, 642, 466), ('4', 'Стенка вертикальная', 'O', 1, 642, 466), ('5', 'Стенка вертикальная', 'O', 1, 642, 466), ('6', 'Стенка задняя', 'O', 2, 424, 642), ('7', 'Дверь', 'O', 1, 486, 530), ('8', 'Царга', 'O', 1, 684, 336), ('9', 'Полка', 'O', 1, 422, 505), ('10', 'Стенка передняя', 'O', 1, 1564, 76), ('11', 'Стенка передняя', 'O', 3, 486, 174), ('12', 'Стенка боковая ящика', 'O', 3, 400, 128), ('13', 'Стенка боковая ящика', 'O', 3, 400, 128), ('14', 'Стенка задняя ящика', 'O', 3, 366.5, 109), ('15', 'Стенка горизонтальная', 'B', 2, 525, 424), ('16', 'Стенка горизонтальная', 'B', 1, 1564, 76), ('17', 'Стенка горизонтальная', 'B', 1, 1564, 76), ('18', 'Стенка вертикальная', 'B', 1, 730, 76), ('19', 'Стенка вертикальная', 'B', 1, 730, 76), ('20', 'Стенка вертикальная', 'B', 1, 622, 76), ('21', 'Стенка вертикальная', 'B', 1, 622, 76), ('22', 'Стенка вертикальная', 'B', 2, 454, 88), ('23', 'Стенка вертикальная', 'B', 2, 394, 88), ('24', 'Стенка горизонтальная', 'B', 2, 424, 76), ('25', 'Дно ящика', 'H', 3, 405, 377)],
    "IS-P3-561-1-01-Kanon-Krovat-1.pdf": [('1', 'Стенка передняя', 'O', 1, 1680, 870), ('2', 'Стенка передняя', 'B', 1, 1408, 76), ('3', 'Опора', 'B', 1, 970, 76), ('4', 'Опора', 'B', 1, 970, 76), ('5', 'Брусок', 'B', 1, 1714, 76), ('6', 'Брусок', 'B', 1, 1680, 76), ('7', 'Брусок', 'B', 1, 1680, 58), ('8', 'Стенка передняя', 'O', 1, 1680, 335), ('9', 'Брусок', 'B', 1, 1674, 76), ('10', 'Царга', 'O', 2, 2014, 200), ('11', 'Брусок', 'B', 2, 2014, 76)],
    "IS-P3-561-1-02-Kanon-SHkaf-3D-1.pdf": [('1', 'Стенка вертикальная', 'O', 1, 2072, 579), ('2', 'Стенка вертикальная', 'O', 1, 2072, 579), ('3', 'Перегородка', 'W', 1, 2056, 560), ('4', 'Стенка вертикальная', 'W', 1, 698, 585), ('5', 'Стенка передняя', 'O', 1, 1336, 128), ('6', 'Стенка вертикальная', 'B', 1, 2160, 76), ('7', 'Стенка вертикальная', 'B', 1, 2160, 76), ('8', 'Стенка вертикальная', 'O', 1, 1912, 76), ('9', 'Стенка вертикальная', 'O', 1, 1912, 76), ('10', 'Стенка передняя', 'O', 2, 1912, 60), ('11', 'Крышка', 'O', 1, 1372, 657), ('12', 'Стенка горизонтальная', 'B', 1, 1336, 636), ('13', 'Стенка горизонтальная', 'W', 1, 585, 460), ('14', 'Стенка горизонтальная', 'W', 1, 860, 320), ('15', 'Стенка горизонтальная', 'W', 1, 585, 460), ('16', 'Стенка горизонтальная', 'B', 1, 1336, 76), ('17', 'Стенка горизонтальная', 'O', 1, 384, 76), ('18', 'Стенка горизонтальная', 'B', 1, 1336, 76), ('19', 'Полка', 'W', 2, 540, 458), ('20', 'Полка', 'W', 1, 540, 440), ('21', 'Дверь', 'O', 2, 396, 1908), ('22', 'Дверь', 'O', 1, 384, 1958), ('23', 'Брусок', 'B', 1, 1958, 56), ('24', 'Цоколь', 'B', 2, 507, 88), ('25', 'Цоколь', 'B', 1, 1368, 88), ('26', 'Брусок', 'B', 1, 1958, 56), ('27', 'Брусок', 'W', 1, 998, 128), ('28', 'Стенка задняя', 'WH', 1, 1102, 472), ('29', 'Стенка задняя', 'WH', 1, 972, 472), ('30', 'Стенка задняя', 'WH', 1, 872, 340), ('31', 'Стенка задняя', 'WH', 1, 1734, 454), ('32', 'Стенка задняя', 'WH', 1, 1734, 416)],
    "IS-P3-561-1-03---Kanon-Tumba-Prikrovatnaya-1.pdf": [('1', 'Стенка вертикальная', 'O', 1, 352, 322), ('2', 'Стенка вертикальная', 'O', 1, 352, 322), ('3', 'Стенка вертикальная', 'B', 1, 440, 76), ('4', 'Стенка вертикальная', 'B', 1, 440, 76), ('5', 'Крышка', 'O', 1, 462, 400), ('6', 'Стенка горизонтальная', 'O', 1, 426, 379), ('7', 'Стенка горизонтальная', 'B', 1, 426, 379), ('8', 'Стенка горизонтальная', 'B', 2, 426, 76), ('9', 'Стенка передняя', 'O', 1, 438, 216), ('10', 'Стенка боковая ящика', 'W', 1, 350, 160), ('11', 'Стенка боковая ящика', 'W', 1, 350, 160), ('12', 'Стенка задняя ящика', 'W', 1, 368.5, 141), ('13', 'Дно ящика', 'WH', 1, 378, 355), ('14', 'Цоколь', 'B', 1, 458, 88), ('15', 'Цоколь', 'B', 1, 88, 200), ('16', 'Стенка задняя', 'WH', 1, 436, 355)],
}
CUT_SOURCE = {
    "IS-P561-09-Tumba-1.pdf": "table on p. 1 of the instruction (text layer without the column header «Ширина»: read from the page picture)",
    "IS-P561-12-Tumba-1.pdf": "table on p. 1 of the instruction (text layer without the column header «Ширина»: read from the page picture)",
    "IS-P3-561-1-01-Kanon-Krovat-1.pdf": "instruction without a text layer: table read from the picture of p. 1",
    "IS-P3-561-1-02-Kanon-SHkaf-3D-1.pdf": "instruction without a text layer: table read from the picture of p. 1",
    "IS-P3-561-1-03---Kanon-Tumba-Prikrovatnaya-1.pdf": "instruction without a text layer: table read from the picture of p. 2",
}
BLACK_DVP = {"IS-P561-01-Komod-1.pdf", "IS-P561-02-Komod-1.pdf", "IS-P561-18-Tumba-1.pdf", "IS-P561-19-SHkaf-2.pdf",
             "IS-P561-12-Tumba-1.pdf", "IS-P561-30-1-Stol-pismennyiy-1.pdf", "IS-P561-31-Stol-pismennyiy-1.pdf"}


def write_cutlist(did, code, name, pdf):
    rows = []
    for n, nm, m, c, a, b in CUT[pdf]:
        mat = MATS[m]
        if m == "H":
            mat += " ЧЕРНАЯ" if pdf in BLACK_DVP else " ВЕНГЕ"
        size = [float(a), float(b)] if m in ("H", "WH") else [float(a), float(b), 6.0 if m == "G" else 16.0]
        rows.append({"n": n, "name": nm, "material": mat, "size": size, "count": c})
    src = CUT_SOURCE.get(pdf, "table on p. 1 of the instruction (text layer; the reference JSON was empty: format «материал, длина, ширина»)")
    data = {"code": code, "name": name, "is": pdf, "source": src, "rows": rows}
    os.makedirs(os.path.join(HERE, "cutlists"), exist_ok=True)
    with open(os.path.join(HERE, "cutlists", did + ".json"), "w") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)


# ------------------------------------------------------------------------------------------------ living room
def cab_0_40(led=True, did="kanon-loft-0-40"):
    """Шкаф с витриной 800 × 414 × 1920 (П561.20 / П561.20с): vitrine on the left behind an inset glazed door, a closed
    column of shelves on the right behind an overlay door that also covers the partition and the 50 strip."""
    W, H = 800, 1920
    d = D(did, [W, 414, H])
    frame(d, W, H, dict(top=5, sL=3, sR=4, pL=17, pR=18, tb=20, ap=11, fb=21, bb=19, bot=16, mid=22), mids=[400])
    d.add(2, [392, 108, ZI, 408, 1760, ZP])                                   # partition
    d.add(12, [342, 108, 382, 392, 1760, ZP], grain="y")                       # strip beside it
    # right column: its top, a fixed shelf, two loose shelves
    d.add(6, [408, 1744, ZI, 782, 1760, ZP])
    d.add(7, [408, 969, ZI, 782, 985, ZP])
    for y in (591, 1373):
        d.add(8, [409, y, ZI, 781, y + 16, 378])
    # vitrine: bottom / top shelves 328 deep in front of its black back, two glass shelves
    d.add(10, [18, 347, 35, 392, 363, 363])
    d.add(9, [18, 1499, 35, 392, 1515, 363])
    d.add(15, [18, 347, ZI, 392, 1515, 35], mat=FR, grain="y")
    for y in (757, 1117):
        d.add(27, [19, y, 40, 391, y + 6, 322], kind="glass")
    back(d, 23, [402, 92, 792, 1907])
    back(d, 24, [8, 92, 388, 347])
    back(d, 25, [8, 1515, 388, 1905])
    door_overlay(d, 1, 362, 798, 107, 1805, "right", "door")
    vitrine_door(d, 13, 20, 340, 110, 1758, 345, 1530, "left", "vitrine")
    if led:
        led_top(d, W, H)
        led_vert(d, 18, 24, 363, 1499, "v1")
        led_vert(d, 386, 392, 363, 1499, "v2")
    return d


def cab_0_39(led=True, did="kanon-loft-0-39"):
    """Шкаф 800 × 414 × 1920 (П561.19 / П561.19с): as 0.40 with a plain inset door on the left column."""
    W, H = 800, 1920
    d = D(did, [W, 414, H])
    frame(d, W, H, dict(top=6, sL=4, sR=3, pL=16, pR=15, tb=18, ap=12, fb=19, bb=17, bot=14, mid=20), mids=[400])
    d.add(2, [392, 108, ZI, 408, 1760, ZP])
    d.add(13, [342, 108, 382, 392, 1760, ZP], grain="y")
    d.add(7, [408, 1744, ZI, 782, 1760, ZP])
    d.add(8, [408, 969, ZI, 782, 985, ZP])
    for y in (591, 1373):
        d.add(9, [409, y, ZI, 781, y + 16, 378])
    d.add(10, [18, 1744, ZI, 392, 1760, 347])                                  # push latch under it
    for y in (518, 928, 1338):
        d.add(11, [19, y, ZI, 391, y + 16, 331])
    back(d, 21, [10, 92, 395, 1907], mat=FR)
    back(d, 21, [405, 92, 790, 1907], mat=FR)
    door_overlay(d, 1, 362, 798, 107, 1805, "right", "door_right")
    door_inset(d, 5, 20, 340, 110, 1758, "left", "door_left")
    if led:
        led_top(d, W, H)
    return d


def cab_0_29(led=True, did="kanon-loft-0-29"):
    """Тумба 900 × 414 × 1200 (П561.09 / П561.09с): vitrine left, shelves right behind an overlay door."""
    W, H = 900, 1200
    d = D(did, [W, 414, H])
    frame(d, W, H, dict(top=2, sL=4, sR=5, pL=15, pR=16, tb=19, ap=10, fb=18, bb=17, bot=14, mid=20), mids=[450])
    d.add(3, [442, 108, ZI, 458, 1040, ZP])
    d.add(13, [392, 108, 382, 442, 1040, ZP], grain="y")
    d.add(6, [458, 1024, ZI, 882, 1040, ZP])
    for y in (402, 713):
        d.add(7, [459, y, ZI, 881, y + 16, 378])
    d.add(9, [18, 347, 35, 442, 363, 363])
    d.add(8, [18, 781, 35, 442, 797, 363])
    d.add(21, [18, 349, ZI, 442, 797, 35], mat=FR)
    d.add(25, [19, 563, 40, 441, 569, 322], kind="glass")
    back(d, 22, [450, 92, 890, 1187])
    back(d, 23, [8, 92, 438, 347])
    back(d, 24, [8, 797, 438, 1187])
    door_overlay(d, 1, 412, 898, 107, 1085, "right", "door")
    vitrine_door(d, 11, 20, 390, 110, 1038, 360, 784, "left", "vitrine")
    if led:
        led_top(d, W, H)
        led_vert(d, 18, 24, 363, 781, "v1")
        led_vert(d, 436, 442, 363, 781, "v2")
    return d


def cab_0_08():
    """Тумба 900 × 414 × 1200 (by photo): the 0.29 carcass with a plain inset door and shelves on the left column."""
    W, H = 900, 1200
    d = D("kanon-loft-0-08", [W, 414, H])
    frame(d, W, H, {}, mids=[450])
    d.add(None, [442, 108, ZI, 458, 1040, ZP], pid="partition")
    d.add(None, [392, 108, 382, 442, 1040, ZP], pid="strip", grain="y")
    d.add(None, [458, 1024, ZI, 882, 1040, ZP], pid="top-r")
    d.add(None, [18, 1024, ZI, 442, 1040, 347], pid="top-l")
    for i, y in enumerate((402, 713)):
        d.add(None, [459, y, ZI, 881, y + 16, 378], pid=f"shelf-r{i + 1}")
        d.add(None, [19, y, ZI, 441, y + 16, 331], pid=f"shelf-l{i + 1}")
    back(d, None, [450, 92, 890, 1187], mat=FR, pid="back-r")
    back(d, None, [8, 92, 440, 1187], mat=FR, pid="back-l")
    door_overlay(d, None, 412, 898, 107, 1085, "right", "door_right", pid="door-r")
    door_inset(d, None, 20, 390, 110, 1038, "left", "door_left", pid="door-l")
    return d


def cab_0_32(led=True, did="kanon-loft-0-32"):
    """Тумба 1290 × 414 × 1200 (П561.12 / П561.12с): two vitrines, a middle column with a drop-down flap over three
    drawers."""
    W, H = 1290, 1200
    d = D(did, [W, 414, H])
    frame(d, W, H, dict(top=1, sL=5, sR=4, pL=25, pR=24, tb=23, ap=7, fb=22, bb=21, bot=20, mid=26), mids=[450, 840])
    d.add(3, [442, 108, ZI, 458, 1040, ZP])
    d.add(2, [832, 108, ZI, 848, 1040, ZP])
    d.add(16, [392, 108, 382, 442, 1040, ZP], grain="y")
    d.add(16, [848, 108, 382, 898, 1040, ZP], grain="y")
    d.add(8, [458, 1024, ZI, 832, 1040, ZP])
    d.add(9, [458, 621, ZI, 832, 637, ZP])
    for tag, x0, x1, ntop in (("l", 18, 442, 12), ("r", 848, 1272, 11)):
        d.add(10, [x0, 347, 35, x1, 363, 363])
        d.add(ntop, [x0, 781, 35, x1, 797, 363])
        d.add(27, [x0, 349, ZI, x1, 797, 35], mat=FR)
        d.add(32, [x0 + 1, 563, 40, x1 - 1, 569, 322], kind="glass")
    back(d, 28, [445, 92, 845, 1187], mat=FR)
    back(d, 29, [8, 797, 438, 1187], mat=FR)
    back(d, 29, [852, 797, 1282, 1187], mat=FR)
    back(d, 31, [8, 92, 438, 347], mat=FR)
    back(d, 31, [852, 92, 1282, 347], mat=FR)
    vitrine_door(d, 13, 20, 390, 110, 1038, 360, 784, "left", "vitrine_l")
    vitrine_door(d, 13, 900, 1270, 110, 1038, 360, 784, "right", "vitrine_r")
    f = d.add(6, [402, 639, ZP, 888, 1085, 414], kind="front", grain="x")
    d.move(type="flap", name="flap", parts=[f], hinge="bottom", angle=90)
    for i, f0 in enumerate((107, 284, 461)):
        drawer(d, str(i + 1), 15, [402, f0, 888, f0 + 174], 458, 832, f0 + 15, (17, 18, 19, 30), side=(350, 128),
               back_h=109, bot=(326, 355))
    if led:
        led_top(d, W, H)
        for tag, x in (("v1", 18), ("v2", 436), ("v3", 848), ("v4", 1266)):
            led_vert(d, x, x + 6, 363, 781, tag)
    return d


def chest_0_21(led=True, did="kanon-loft-0-21", size=None):
    """Комод 1400 × 414 × 900 (П561.01 / П561.01с): an inset door on the left, three drawers on the right."""
    W, H = 1400, 900
    d = D(did, size or [W, 414, H])
    frame(d, W, H, dict(top=1, sL=5, sR=4, pL=19, pR=18, tb=16, ap=8, fb=17, bb=15, bot=14, mid=20), mids=[506])
    d.add(6, [498, 108, ZI, 514, 740, ZP])
    d.add(13, [448, 108, 382, 498, 740, ZP], grain="y")
    d.add(2, [514, 724, ZI, 1382, 740, ZP])
    d.add(9, [18, 416, ZI, 498, 432, 347])
    back(d, 22, [10, 92, 500, 887], mat=FR)
    back(d, 21, [506, 92, 1386, 887], mat=FR)
    door_inset(d, 3, 20, 446, 110, 738, "left", "door")
    for i, f0 in enumerate((107, 325, 543)):
        drawer(d, str(i + 1), 7, [466, f0, 1396, f0 + 216], 514, 1382, f0 + 15, (11, 12, 10, 23), bot=(820, 355))
    if led:
        led_top(d, W, H)
    return d


def chest_0_22(led=True, did="kanon-loft-0-22"):
    """Комод 1846 × 414 × 900 (П561.02 / П561.02с): inset doors at both ends, three drawers in the middle."""
    W, H = 1846, 900
    d = D(did, [W, 414, H])
    frame(d, W, H, dict(top=1, sL=6, sR=5, pL=24, pR=23, tb=21, ap=9, fb=22, bb=20, bot=19, mid=25), mids=[506, 1340])
    d.add(8, [498, 108, ZI, 514, 740, ZP])
    d.add(7, [1332, 108, ZI, 1348, 740, ZP])
    d.add(17, [448, 108, 382, 498, 740, ZP], grain="y")
    d.add(17, [1348, 108, 382, 1398, 740, ZP], grain="y")
    d.add(2, [514, 724, ZI, 1332, 740, ZP])
    d.add(16, [915, 740, ZI, 931, 884, ZS])                                    # stiffener under the top
    d.add(12, [18, 416, ZI, 498, 432, 347])
    d.add(11, [1348, 416, ZI, 1828, 432, 347])
    back(d, 27, [10, 92, 500, 887], mat=FR)
    back(d, 26, [506, 92, 1336, 887], mat=FR)
    back(d, 27, [1346, 92, 1836, 887], mat=FR)
    door_inset(d, 3, 20, 446, 110, 738, "left", "door_l")
    door_inset(d, 3, 1400, 1826, 110, 738, "right", "door_r")
    for i, f0 in enumerate((107, 325, 543)):
        drawer(d, str(i + 1), 10, [458, f0, 1388, f0 + 216], 514, 1332, f0 + 15, (14, 15, 13, 28), bot=(770, 355))
    if led:
        led_top(d, W, H)
    return d


def tv_0_38(led=True, did="kanon-loft-0-38", W=1980, right_door=True):
    """Тумба ТВ 1980 × 400 × 510 (П561.18 / П561.18с): inset doors at the ends, a black open niche in the middle; inner
    panels 338 deep behind the inset fronts. W=1500 without the right door column = 0.37 / 0.17 (by catalogue)."""
    H = 510
    instr = W == 1980
    d = D(did, [W, 400, H])
    n = dict(top=1, sL=4, sR=3, pL=15, pR=14, tb=10, ap=2, fb=11, bb=9, bot=7) if instr else {}
    zb = 44.0
    frame(d, W, H, n, apron_h=96, zb0=zb, mid_len=246)
    xl, xr = 482, (1482 if right_door else None)
    d.add(13 if instr else None, [xl, 108, zb, xl + 16, 366, 382], mat=FR, pid=None if instr else "partition-l")
    d.add(17 if instr else None, [xl, 4, 76, xl + 16, 92, ZS], mat=FR, pid=None if instr else "plinth-mid-l")
    glide(d, xl + 8, 300)
    if right_door:
        d.add(12 if instr else None, [xr, 108, zb, xr + 16, 366, 382], mat=FR, pid=None if instr else "partition-r")
        d.add(18 if instr else None, [xr, 4, 76, xr + 16, 92, ZS], mat=FR, pid=None if instr else "plinth-mid-r")
        glide(d, xr + 8, 300)
    d.add(8 if instr else None, [498, 366, zb, 1482, 382, 382], mat=FR, pid=None if instr else "niche-top")
    for x in (740, 1224):
        d.add(16 if instr else None, [x, 382, 60, x + 16, 494, ZS], mat=FR, pid=None if instr else f"stiffener-{x}")
    back(d, 20 if instr else None, [10, 92, 500, 497], mat=FR, pid=None if instr else "back-l")
    back(d, 19 if instr else None, [506, 92, 1474 if right_door else W - 10, 497], mat=FR, pid=None if instr else "back-m")
    if right_door:
        back(d, 20, [1480, 92, 1970, 497], mat=FR)
    for p in d.parts:                                  # backs of this piece lie behind the 338-deep inner panels
        if p.get("kind") == "back":
            p["box"][2], p["box"][5] = zb - 3, zb
    door_inset(d, 5 if instr else None, 20, 496, 110, 380, "left", "door_l", pid=None if instr else "door-l")
    if right_door:
        door_inset(d, 5, 1484, 1960, 110, 380, "right", "door_r")
    if led:
        led_top(d, W, H)
    return d


def shelf_0_03():
    """Полка навесная 1400 × 250 × 300 (П561.03-1): oak back and shelf, oak top strip, black end blocks and a black band
    under the top."""
    d = D("kanon-loft-0-03", [1400, 250, 300])
    d.add(2, [0, 0, 0, 1400, 16, 250], grain="x")
    d.add(1, [17.5, 16, 0, 1382.5, 284, 16], grain="x")
    d.add(3, [0, 284, 0, 1400, 300, 78], grain="x")
    d.add(4, [17.5, 208, 16, 1382.5, 284, 32], mat=FR)
    d.add(5, [1.5, 16, 0, 17.5, 284, 76], mat=FR)
    d.add(6, [1382.5, 16, 0, 1398.5, 284, 76], mat=FR)
    return d


def shelf_0_04():
    """Полка навесная 1400 × 250 × 300 (by photo): an oak box with a black front frame, a dark back, an oak partition
    at two thirds and an inset oak door on the right section."""
    d = D("kanon-loft-0-04", [1400, 250, 300])
    d.add(None, [0, 284, 0, 1400, 300, 250], pid="top", grain="x")
    d.add(None, [0, 0, 0, 1400, 16, 250], pid="bottom", mat=FR)
    d.add(None, [0, 16, 0, 16, 284, 174], pid="side-l")
    d.add(None, [1384, 16, 0, 1400, 284, 174], pid="side-r")
    d.add(None, [0, 16, 174, 16, 284, 250], pid="post-l", mat=FR)
    d.add(None, [1384, 16, 174, 1400, 284, 250], pid="post-r", mat=FR)
    d.add(None, [16, 268, 174, 1384, 284, 250], pid="bar-top", mat=FR)
    d.add(None, [16, 16, 19, 1384, 32, 234], pid="floor", grain="x")
    d.add(None, [896, 32, 19, 912, 268, 234], pid="partition")
    back(d, None, [8, 8, 1392, 292], mat=FR, pid="back")
    door_inset(d, None, 914, 1382, 34, 266, "right", "door", pid="door")
    for p in d.parts:
        if p["id"] == "door":
            p["box"][2], p["box"][5] = 234, 250
    return d


def rack(W, did):
    """Стеллаж W × 400 × 1920 (by photo, 0.26 / 0.27): the living-room frame without doors, four oak shelves, black back."""
    H = 1920
    d = D(did, [W, 400, H])
    frame(d, W, H, {}, mids=[W / 2])
    d.add(None, [18, 1744, ZI, W - 18, 1760, ZP], pid="top-inner")
    for i, y in enumerate((438, 768, 1098, 1428)):
        d.add(None, [19, y, ZI, W - 19, y + 16, 378], pid=f"shelf-{i + 1}")
    back(d, None, [8, 92, W - 8, 1907], mat=FR, pid="back")
    return d


def coffee_0_06():
    """Стол журнальный 940 × 600 × 500 (by photo): oak top, black U-legs (posts + floor runner) at the ends, black
    aprons, a drawer through each end (oak fronts on the short sides), an oak shelf low between the legs."""
    d = D("kanon-loft-0-06", [940, 600, 500])
    d.add(None, [0, 484, 0, 940, 500, 600], pid="top", grain="x")
    for tag, x0 in (("l", 30), ("r", 834)):
        for zt, z0 in (("f", 564), ("b", 20)):
            d.add(None, [x0, 20, z0, x0 + 76, 484, z0 + 16], pid=f"leg-{tag}{zt}", mat=FR)
        d.add(None, [x0, 4, 20, x0 + 76, 20, 580], pid=f"runner-{tag}", mat=FR)
        for z in (40, 560):
            glide(d, x0 + 38, z)
    for zt, z0 in (("f", 564), ("b", 20)):
        d.add(None, [106, 374, z0, 834, 484, z0 + 16], pid=f"apron-{zt}", mat=FR)
    d.add(None, [30, 358, 36, 910, 374, 564], pid="drawer-floor", mat=FR)
    d.add(None, [462, 374, 36, 478, 484, 564], pid="divider", mat=FR)
    d.add(None, [36, 150, 36, 904, 166, 564], pid="shelf", grain="x")
    for tag, fx0, sgn in (("l", 30, 1), ("r", 894, -1)):
        ids = []
        ids.append(d.add(None, [fx0, 376, 38, fx0 + 16, 482, 562], kind="front", grain="z", pid=f"front-{tag}"))
        bx0, bx1 = (46, 396) if sgn > 0 else (544, 894)
        ids.append(d.add(None, [bx0, 386, 52, bx1, 470, 68], pid=f"bs1-{tag}"))
        ids.append(d.add(None, [bx0, 386, 532, bx1, 470, 548], pid=f"bs2-{tag}"))
        bk = [bx1 - 16, 386, 68, bx1, 470, 532] if sgn > 0 else [bx0, 386, 68, bx0 + 16, 470, 532]
        ids.append(d.add(None, bk, pid=f"bb-{tag}"))
        ids.append(d.add(None, [bx0, 380, 60, bx1, 383, 540], kind="back", mat=FR, pid=f"bot-{tag}"))
        d.move(type="slide", name=f"drawer_{tag}", parts=ids, by=[-300 * sgn, 0, 0])
    return d


# ------------------------------------------------------------------------------------------------ bedroom
def bed_1_01():
    """Кровать 2-16 1714 × 2120 × 990 (П3.561.1.01): headboard between black posts under a black top bar, a recessed black
    band with two open windows at its ends, oak side rails and foot with black bands, metal base 2000 × 1600 on 8 legs."""
    W, L = 1714, 2120
    d = D("kanon-loft-1-01", [W, L, 990])
    d.add(5, [0, 974, 0, W, 990, 76], mat=FR)
    d.add(3, [1, 4, 0, 17, 974, 76], mat=FR)
    d.add(4, [1697, 4, 0, 1713, 974, 76], mat=FR)
    d.add(6, [17, 882, 0, 1697, 898, 76], mat=FR)
    d.add(2, [153, 898, 0, 1561, 974, 16], mat=FR)
    d.add(1, [17, 12, 58, 1697, 882, 74], grain="x")
    d.add(7, [17, 420, 0, 1697, 436, 58], mat=FR)
    d.add(10, [17, 119, 74, 33, 319, 2088], grain="z")
    d.add(10, [1681, 119, 74, 1697, 319, 2088], grain="z")
    d.add(11, [1, 177, 76, 17, 253, 2090], mat=FR)
    d.add(11, [1697, 177, 76, 1713, 253, 2090], mat=FR)
    d.add(8, [17, 4, 2088, 1697, 339, 2104], grain="x")
    d.add(9, [20, 177, 2104, 1694, 253, 2120], mat=FR)
    for x in (9, 1705):
        glide(d, x, 38)
    for x in (40, 1674):
        glide(d, x, 2096)
    # flexible base f7 (2000 × 1600, 8 legs): black steel frame, a middle beam, birch slats
    fx0, fx1, fz0, fz1 = 57, 1657, 84, 2084
    d.add(None, [fx0, 230, fz0, fx0 + 30, 260, fz1], mat="black", pid="base-rail-l", covers=["f7"])
    d.add(None, [fx1 - 30, 230, fz0, fx1, 260, fz1], mat="black", pid="base-rail-r")
    d.add(None, [fx0 + 30, 230, fz0, fx1 - 30, 260, fz0 + 30], mat="black", pid="base-end-h")
    d.add(None, [fx0 + 30, 230, fz1 - 30, fx1 - 30, 260, fz1], mat="black", pid="base-end-f")
    d.add(None, [842, 230, fz0 + 30, 872, 260, fz1 - 30], mat="black", pid="base-beam")
    legs = [(72, 99), (72, 1084), (72, 2069), (1642, 99), (1642, 1084), (1642, 2069), (857, 700), (857, 1450)]
    for i, (x, z) in enumerate(legs):
        d.add(None, [x - 12, 0, z - 12, x + 12, 230, z + 12], kind="tube", mat="black", pid=f"base-leg-{i + 1}")
    for f, (a, b) in enumerate(((fx0 + 30, 842), (872, fx1 - 30))):
        for i in range(22):
            z = 124 + i * 88.5
            d.add(None, [a, 252, z, b, 260, z + 53], mat="door_enamel_whitey#c9a877", pid=f"slat-{f + 1}-{i + 1}")
    d.add(None, [fx0, 260, fz0, fx1, 460, fz1], kind="mattress", pid="mattress")
    return d


def wardrobe_1_02():
    """Шкаф для одежды 3Д 1372 × 671 × 2180 (П3.561.1.02): the loft frame at wardrobe depth (sides 579), a white partition
    between the hanging section (left + middle, a 853 rail under a hat shelf, a low cabinet with a shelf on the left)
    and a shelved right section; inset side doors, an overlay middle door between black 56 bars (one on the door, one
    fixed) that stands 16 mm proud and rises 46 mm over the side doors."""
    W, H = 1372, 2180
    d = D("kanon-loft-1-02", [W, 671, H])
    Z1, ZF = 579.0, 655.0
    d.add(11, [0, H - 16, 0, W, H, 657], grain="x")
    d.add(2, [2, 92, 0, 18, H - 16, Z1])
    d.add(1, [W - 18, 92, 0, W - 2, H - 16, Z1])
    d.add(7, [2, 4, Z1, 18, H - 16, ZF], mat=FR)
    d.add(6, [W - 18, 4, Z1, W - 2, H - 16, ZF], mat=FR)
    d.add(16, [18, H - 32, Z1, W - 18, H - 16, ZF], mat=FR)
    d.add(5, [18, 2020, 639, W - 18, 2148, ZF], grain="x")
    d.add(27, [187, 2020, 623, 1185, 2148, 639], mat="white")
    d.add(18, [18, 4, Z1, W - 18, 20, ZF], mat=FR)
    d.add(25, [2, 4, 0, W - 2, 92, 16], mat=FR)
    for x in (484, 886):
        d.add(24, [x - 8, 4, 72, x + 8, 92, Z1], mat=FR)
        glide(d, x, 300)
    for x in (10, W - 10):
        glide(d, x, 620)
        glide(d, x, 8)
    d.add(12, [18, 92, ZI, W - 18, 108, ZF], mat=FR)
    d.add(3, [878, 108, ZI, 894, H - 16, Z1], mat="white")
    d.add(9, [878, 108, Z1, 894, 2020, ZF], grain="y")
    d.add(8, [476, 108, Z1, 492, 2020, ZF], grain="y")
    d.add(10, [416, 108, 639, 476, 2020, ZF], grain="y")
    d.add(10, [894, 108, 639, 954, 2020, ZF], grain="y")
    d.add(17, [493, 2004, Z1, 877, 2020, ZF], grain="x")
    # left + middle: hat shelf, rail, a low cabinet on the left
    d.add(14, [18, 1860, ZI, 878, 1876, 339], mat="white")
    d.add(None, [21, 1790, 292, 874, 1820, 307], kind="tube", mat="chrome", pid="rail-853", covers=["d3"])
    d.add(4, [458, 108, ZI, 474, 806, 604], mat="white")
    d.add(20, [18, 806, ZI, 458, 822, 559], mat="white")
    # right section: two fixed shelves, two loose, a rail
    d.add(13, [894, 1601, ZI, W - 18, 1617, 604], mat="white")
    d.add(15, [894, 981, ZI, W - 18, 997, 604], mat="white")
    for y in (570, 1900):
        d.add(19, [895, y, ZI, W - 19, y + 16, 559], mat="white")
    d.add(None, [897, 1520, 292, 1350, 1550, 307], kind="tube", mat="chrome", pid="rail-453")
    for n, box in ((31, [10, 92, 464, 1826]), (32, [464, 92, 880, 1826]), (30, [10, 1826, 882, 2166]),
                   (28, [890, 92, 1362, 1194]), (29, [890, 1194, 1362, 2166])):
        back(d, n, box, mat="white")
    # fronts
    a = d.add(21, [20, 110, 639, 416, 2018, ZF], kind="front", grain="y")
    d.move(type="door", name="door_l", parts=[a], hinge="left", angle=105)
    b = d.add(21, [956, 110, 639, 1352, 2018, ZF], kind="front", grain="y")
    d.move(type="door", name="door_r", parts=[b], hinge="right", angle=105)
    m = d.add(22, [494, 106, ZF, 878, 2064, 671], kind="front", grain="y")
    bar = d.add(23, [438, 106, ZF, 494, 2064, 671], mat=FR)
    d.add(26, [878, 106, ZF, 934, 2064, 671], mat=FR)
    d.move(type="door", name="door_m", parts=[m, bar], hinge="right", angle=100)
    return d


def bedside_1_03():
    """Тумба прикроватная 462 × 414 × 460 (П3.561.1.03): an open niche over a drawer, the loft frame and sled base."""
    W, H = 462, 460
    d = D("kanon-loft-1-03", [W, 414, H])
    d.add(5, [0, 444, 0, W, H, 400], grain="x")
    d.add(1, [2, 92, 0, 18, 444, ZS])
    d.add(2, [444, 92, 0, 460, 444, ZS])
    d.add(3, [2, 4, ZS, 18, 444, ZP], mat=FR)
    d.add(4, [444, 4, ZS, 460, 444, ZP], mat=FR)
    d.add(8, [18, 428, ZS, 444, 444, ZP], mat=FR)
    d.add(8, [18, 4, ZS, 444, 20, ZP], mat=FR)
    d.add(7, [18, 92, ZI, 444, 108, ZP], mat=FR)
    d.add(6, [18, 297, ZI, 444, 313, ZP])
    d.add(14, [2, 4, 0, 460, 92, 16], mat=FR)
    d.add(15, [223, 4, 122, 239, 92, ZS], mat=FR)
    back(d, 16, [13, 92, 449, 447], mat="white")
    for x in (10, 452):
        glide(d, x, 360)
    glide(d, 231, 300)
    glide(d, 231, 8)
    ids = drawer(d, "1", 9, [12, 97, 450, 313], 18, 444, 112, (10, 11, 12, 13), bot=(378, 355))
    for p in d.parts:
        if p.get("id") in ids[1:4]:
            p["mat"] = "white"
        if p.get("id") == ids[4]:
            p["mat"] = "white"
    return d


def mirror_1_05():
    """Зеркало 1050 × 150 × 858 (by photo): an oak board framed in thin black, a bevelled mirror, a black shelf 150 deep
    along the bottom. Hangs on the wall."""
    d = D("kanon-loft-1-05", [1050, 150, 858])
    d.add(None, [0, 0, 0, 1050, 16, 150], pid="shelf", mat=FR)
    d.add(None, [0, 16, 0, 16, 858, 40], pid="frame-l", mat=FR)
    d.add(None, [1034, 16, 0, 1050, 858, 40], pid="frame-r", mat=FR)
    d.add(None, [16, 842, 0, 1034, 858, 40], pid="frame-t", mat=FR)
    d.add(None, [16, 16, 0, 1034, 842, 16], pid="board", grain="x")
    d.add(None, [76, 76, 16, 974, 782, 20], kind="mirror", pid="mirror", covers=["зеркало"])
    return d


def coupe(did, W, ndoors, mirror_mid=False):
    """Шкаф-купе (by catalogue): oak carcass with full-height sides, top, bottom on a front plinth, white interior after the
    catalogue's scheme, sliding doors in two tracks — oak panels (the middle one a mirror in 1.09) in silver aluminium
    frames with vertical handle profiles."""
    H, Dp = 2292, 650
    d = D(did, [W, Dp, H])
    d.add(None, [0, 0, 0, 16, H, Dp], pid="side-l")
    d.add(None, [W - 16, 0, 0, W, H, Dp], pid="side-r")
    d.add(None, [16, H - 16, 0, W - 16, H, Dp], pid="top", grain="x")
    d.add(None, [16, 60, 0, W - 16, 76, 560], pid="bottom", grain="x")
    d.add(None, [16, 0, 590, W - 16, 60, 606], pid="plinth", grain="x")
    d.add(None, [16, 0, 20, W - 16, 60, 36], pid="plinth-back")
    back(d, None, [8, 68, W - 8, H - 8], mat="white", pid="back")
    for p in d.parts:
        if p["id"] == "back":
            p["box"][2], p["box"][5] = 4, 7
    d.add(None, [16, H - 36, 560, W - 16, H - 16, Dp], mat="metal", pid="track-top", edge=0.5, covers=["профиль"])
    d.add(None, [16, 76, 560, W - 16, 80, 645], mat="metal", pid="track-bottom", edge=0.5)
    inner = W - 32

    def shelf(pid, x0, x1, y):
        d.add(None, [x0, y, 10, x1, y + 16, 550], mat="white", pid=pid)

    def rail(pid, x0, x1, y):
        d.add(None, [x0 + 3, y, 262, x1 - 3, y + 30, 277], kind="tube", mat="chrome", pid=pid)

    if ndoors == 2:
        xp = 917
        d.add(None, [xp, 76, 10, xp + 16, H - 36, 560], mat="white", pid="partition")
        shelf("shelf-l1", 16, xp, 1900)
        shelf("shelf-l2", 16, xp, 460)
        rail("rail-l", 16, xp, 1830)
        for i, y in enumerate((490, 820, 1180, 1540, 1900)):
            shelf(f"shelf-r{i + 1}", xp + 16, W - 16, y)
    else:
        xa, xb = 661, 1352
        for pid, x in (("partition-l", xa), ("partition-r", xb)):
            d.add(None, [x, 76, 10, x + 16, H - 36, 560], mat="white", pid=pid)
        for tag, x0, x1 in (("l", 16, xa), ("r", xb + 16, W - 16)):
            shelf(f"shelf-{tag}1", x0, x1, 1854)
            shelf(f"shelf-{tag}2", x0, x1, 467)
            rail(f"rail-{tag}", x0, x1, 1784)
        for i, y in enumerate((467, 832, 1168, 1533, 1854)):
            shelf(f"shelf-m{i + 1}", xa + 16, xb, y)
    ov = 30
    lw = (inner + (ndoors - 1) * ov) / ndoors
    tracks = [622, 590] if ndoors == 2 else [622, 590, 622]
    y0, y1 = 80, H - 36
    for k in range(ndoors):
        x0 = 16 + k * (lw - ov)
        x1 = x0 + lw
        zc = tracks[k]
        tag = f"d{k + 1}"
        mir = mirror_mid and k == 1
        ids = [
            d.add(None, [x0 + 15, y0 + 22, zc - 5, x1 - 15, y1 - 22, zc + 5], kind="mirror" if mir else "front",
                  grain="y", pid=f"panel-{tag}"),
            d.add(None, [x0, y0, zc - 10, x0 + 15, y1, zc + 10], mat="metal", edge=1, pid=f"prof-l-{tag}"),
            d.add(None, [x1 - 15, y0, zc - 10, x1, y1, zc + 10], mat="metal", edge=1, pid=f"prof-r-{tag}"),
            d.add(None, [x0 + 15, y0, zc - 8, x1 - 15, y0 + 22, zc + 8], mat="metal", pid=f"rail-b-{tag}"),
            d.add(None, [x0 + 15, y1 - 22, zc - 8, x1 - 15, y1, zc + 8], mat="metal", pid=f"rail-t-{tag}"),
        ]
        by = (lw - ov) * (1 if k < ndoors / 2 else -1) if ndoors == 2 or k != 1 else -(lw - ov)
        d.move(type="slide", name=f"coupe_{tag}", parts=ids, by=[round(by, 1), 0, 0])
    return d


# ------------------------------------------------------------------------------------------------ study, dining
def desk_2_31():
    """Стол письменный 2т 1600 × 614 × 750 (П561.31): two pedestals on the loft frame (door + shelf left, three drawers
    right), an oak modesty panel between them, a black / oak / black rail band under the top."""
    W = 1600
    d = D("kanon-loft-2-31", [W, 614, 750])
    ZB, ZS2, ZP2, ZF2 = 56.0, 522.0, 598.0, 614.0
    d.add(1, [0, 734, 0, W, 750, 600], grain="x")
    for tag, xo, xi, no, ni, po, pi in (("l", 2, 442, 5, 4, 19, 21), ("r", 1582, 1142, 2, 3, 18, 20)):
        d.add(no, [xo, 92, ZB, xo + 16, 734, ZS2])
        d.add(ni, [xi, 92, ZB, xi + 16, 734, ZS2])
        d.add(po, [xo, 4, ZS2, xo + 16, 734, ZP2], mat=FR)
        d.add(pi, [xi, 4, ZS2, xi + 16, 626, ZP2], mat=FR)
        a, b = min(xo, xi) + 16, max(xo, xi)
        d.add(6, [a, 92, ZB, b, 734, ZB + 16])
        d.add(15, [a, 92, ZB + 16, b, 108, ZP2 - 1], mat=FR)
        d.add(22, [a - 15, 4, ZB, b + 15, 92, ZB + 16], mat=FR)
        d.add(23, [(a + b) / 2 - 8, 4, 128, (a + b) / 2 + 8, 92, ZS2], mat=FR)
        d.add(24, [a, 4, ZS2, b, 20, ZP2], mat=FR)
        for x in (a - 8, b + 8):
            glide(d, x, 560)
            glide(d, x, ZB + 8)
    d.add(16, [18, 718, ZS2, 1582, 734, ZP2], mat=FR)
    d.add(10, [18, 642, 566, 1582, 718, 582], grain="x")
    d.add(17, [18, 626, ZS2, 1582, 642, ZP2], mat=FR)
    d.add(8, [458, 398, ZB, 1142, 734, ZB + 16], grain="x")
    d.add(9, [19, 380, ZB + 16, 441, 396, 577])
    a = d.add(7, [8, 107, ZP2, 494, 637, ZF2], kind="front", grain="y")
    d.move(type="door", name="door", parts=[a], hinge="left", angle=105)
    for i, f0 in enumerate((107, 284, 461)):
        drawer(d, str(i + 1), 11, [1106, f0, 1592, f0 + 174], 1158, 1582, f0 + 15, (12, 13, 14, 25), side=(400, 128),
               back_h=109, bot=(377, 405), zf=ZP2, fz1=ZF2)
    return d


def desk_2_30_01():
    """Стол письменный 1250 × 614 × 750 (П561.30-1): a drawer pedestal on the right, a loft-frame leg on the left (black
    posts round an oak face, two black rails back to an oak rear post, oak end panel, black foot loop)."""
    W = 1250
    d = D("kanon-loft-2-30-01", [W, 614, 750])
    ZB, ZS2, ZP2, ZF2 = 56.0, 522.0, 598.0, 614.0
    d.add(1, [0, 734, 0, W, 750, 600], grain="x")
    # left leg
    d.add(17, [2, 4, ZS2, 18, 734, ZP2], mat=FR)
    d.add(13, [18, 108, 582, 94, 626, ZP2], grain="y")
    d.add(19, [94, 4, ZS2, 110, 626, ZP2], mat=FR)
    d.add(4, [2, 92, 73, 18, 734, ZS2])
    d.add(9, [94, 4, ZB, 110, 734, 166], grain="y")
    for y in (200, 480):
        d.add(24, [110, y, 73, 126, y + 76, ZS2], mat=FR)
    d.add(22, [18, 92, 73, 94, 108, ZP2], mat=FR)
    d.add(27, [18, 4, 524, 94, 20, ZP2], mat=FR)
    d.add(25, [18, 626, 43, 94, 642, ZS2], mat=FR)
    for x, z in ((10, 560), (56, 560), (102, 70), (102, 150)):
        glide(d, x, z)
    # rails and modesty panel
    d.add(16, [18, 718, ZS2, 1232, 734, ZP2], mat=FR)
    d.add(7, [18, 642, 566, 1232, 718, 582], grain="x")
    d.add(15, [18, 626, ZS2, 1232, 642, ZP2], mat=FR)
    d.add(6, [110, 402, ZB, 791, 734, ZB + 16], grain="x")
    # pedestal
    d.add(3, [792, 92, ZB, 808, 734, ZS2])
    d.add(2, [1232, 92, ZB, 1248, 734, ZS2])
    d.add(20, [792, 4, ZS2, 808, 626, ZP2], mat=FR)
    d.add(18, [1232, 4, ZS2, 1248, 734, ZP2], mat=FR)
    d.add(5, [808, 92, ZB, 1232, 734, ZB + 16])
    d.add(14, [808, 92, ZB + 16, 1232, 108, ZP2 - 1], mat=FR)
    d.add(21, [793, 4, ZB, 1247, 92, ZB + 16], mat=FR)
    d.add(23, [1012, 4, 128, 1028, 92, ZS2], mat=FR)
    d.add(26, [808, 4, ZS2, 1232, 20, ZP2], mat=FR)
    for x in (800, 1240):
        glide(d, x, 560)
        glide(d, x, ZB + 8)
    for i, f0 in enumerate((107, 284, 461)):
        drawer(d, str(i + 1), 8, [754, f0, 1240, f0 + 174], 808, 1232, f0 + 15, (10, 11, 12, 28), side=(400, 128),
               back_h=109, bot=(377, 405), zf=ZP2, fz1=ZF2)
    return d


def dining_4_28():
    """Стол обеденный раздвижной 1302 / 1802 × 902 × 776 (П561.28), built open (L1802, the catalogue size): two top halves
    slid out on black runners with the insert between them; two end frames fixed under them (oak end rail on a black
    ledge, U-section legs: black outer board, oak end face, black inner board, black foot block), black long aprons
    and black edge boards (накладки) under the top's rim."""
    W = 1802
    d = D("kanon-loft-4-28", [W, 902, 776])
    d.add(1, [0, 760, 0, 651, 776, 902], grain="x")
    d.add(1, [1151, 760, 0, W, 776, 902], grain="x")
    d.add(2, [651, 760, 0, 1151, 776, 902], grain="x")
    for x0 in (0, 1151):
        d.add(11, [x0, 744, 802, x0 + 651, 760, 902], mat=FR)
        d.add(12, [x0, 744, 0, x0 + 651, 760, 100], mat=FR)
    d.add(9, [0, 744, 100, 100, 760, 802], mat=FR)
    d.add(9, [1702, 744, 100, 1802, 760, 802], mat=FR)
    d.add(15, [651, 744, 0, 1151, 760, 100], mat=FR)
    d.add(15, [651, 744, 802, 1151, 760, 902], mat=FR)
    for side in ("l", "r"):
        def X(a, b):
            return (a, b) if side == "l" else (W - b, W - a)
        xa, xb = X(250, 266)          # the end face (oak)
        xc, xd = X(250, 326)          # through the leg
        d.add(3, [xa, 668, 17, xb, 744, 885], grain="z")
        d.add(10, [xc, 652, 17, xd, 668, 885], mat=FR)
        xe, xf = X(266, 342)
        d.add(4, [xe, 668, 33, xf, 684, 869], grain="z")      # oak ledge behind the end rail, between the aprons
        d.add(13, [xc, 4, 1, xd, 744, 17], mat=FR)
        d.add(14, [xc, 4, 885, xd, 744, 901], mat=FR)
        d.add(5, [xa, 20, 17, xb, 652, 93], grain="y")
        d.add(17, [xc, 4, 93, xd, 652, 109], mat=FR)
        d.add(6, [xa, 20, 809, xb, 652, 885], grain="y")
        d.add(16, [xc, 4, 793, xd, 652, 809], mat=FR)
        d.add(18, [xc, 4, 17, xd, 20, 93], mat=FR)
        d.add(18, [xc, 4, 809, xd, 20, 885], mat=FR)
        for z in (9, 893, 101, 801):
            glide(d, (xc + xd) / 2, z)
    d.add(8, [273, 668, 17, 1529, 744, 33], mat=FR)
    d.add(8, [273, 668, 869, 1529, 744, 885], mat=FR)
    for z in (250, 544):
        d.add(7, [327, 728, z, 1475, 744, z + 108], mat=FR)
    return d


# ------------------------------------------------------------------------------------------------ catalogue
FIN = "kanon-loft-kanon-black"
IS = {"0-40": "IS-P561-20-SHkaf-s-vitrinoy-1.pdf", "0-39": "IS-P561-19-SHkaf-2.pdf", "0-29": "IS-P561-09-Tumba-1.pdf",
      "0-32": "IS-P561-12-Tumba-1.pdf", "0-21": "IS-P561-01-Komod-1.pdf", "0-22": "IS-P561-02-Komod-1.pdf",
      "0-38": "IS-P561-18-Tumba-1.pdf", "0-03": "IS-P561-03-1-Polka-navesnaya-1.pdf",
      "1-01": "IS-P3-561-1-01-Kanon-Krovat-1.pdf", "1-02": "IS-P3-561-1-02-Kanon-SHkaf-3D-1.pdf",
      "1-03": "IS-P3-561-1-03---Kanon-Tumba-Prikrovatnaya-1.pdf", "2-30-01": "IS-P561-30-1-Stol-pismennyiy-1.pdf",
      "2-31": "IS-P561-31-Stol-pismennyiy-1.pdf", "4-28": "IS-P561-28-Stol-obedennyiy-razdvijnoy-1.pdf"}


def main():
    out = []   # (design, code, name, category, page, instruction key or None, note, extra)
    L = "с подсветкой"
    pairs = [
        (cab_0_40, "0-40", "0-20", "Шкаф «Каньон Лофт»", 85, "витрина"),
        (cab_0_39, "0-39", "0-19", "Шкаф «Каньон Лофт»", 85, None),
        (cab_0_29, "0-29", "0-09", "Тумба «Каньон Лофт»", 85, "витрина"),
        (cab_0_32, "0-32", "0-12", "Тумба «Каньон Лофт»", 85, "две витрины, откидная дверь"),
        (chest_0_21, "0-21", "0-01", "Комод «Каньон Лофт»", 85, None),
        (chest_0_22, "0-22", "0-02", "Комод «Каньон Лофт»", 85, None),
        (tv_0_38, "0-38", "0-18", "Тумба «Каньон Лофт»", 85, "ТВ"),
    ]
    for fn, led_code, plain_code, name, page, note in pairs:
        d = fn(led=True, did=f"{SLUG}-{led_code}")
        p = strip_led(d, f"{SLUG}-{plain_code}")
        out.append((d, led_code, name, page, led_code, ", ".join(x for x in (note, L) if x), None))
        out.append((p, plain_code, name, page, led_code, ", ".join(x for x in (note, f"без подсветки (пара к П3.0561.{led_code.replace('-', '.')})") if x), None))
        if led_code == "0-40":
            out.append((mirror_x(d, 800, f"{SLUG}-0-40-01"), "0-40-01", name, page, led_code,
                        "витрина справа (зеркальное исполнение), " + L, "not in index.json: the catalogue lists it on p. 85"))
            out.append((mirror_x(p, 800, f"{SLUG}-0-20-01"), "0-20-01", name, page, led_code,
                        "витрина справа (зеркальное исполнение), без подсветки", None))
    d = tv_0_38(led=True, did=f"{SLUG}-0-37", W=1500, right_door=False)
    out.append((d, "0-37", "Тумба «Каньон Лофт»", 85, None, "ТВ, " + L + "; по каталогу: конструкция П561.18 без правой секции",
                "not in index.json: the catalogue lists it on p. 85"))
    out.append((strip_led(d, f"{SLUG}-0-17"), "0-17", "Тумба «Каньон Лофт»", 85, None,
                "ТВ, без подсветки; по каталогу: конструкция П561.18 без правой секции", None))
    out += [
        (shelf_0_03(), "0-03", "Полка «Каньон Лофт»", 85, "0-03", "навесная", None),
        (shelf_0_04(), "0-04", "Полка «Каньон Лофт»", 85, None, "навесная, по фото", None),
        (coffee_0_06(), "0-06", "Стол журнальный «Каньон Лофт»", 86, None, "по фото, ящики с торцов", None),
        (cab_0_08(), "0-08", "Тумба «Каньон Лофт»", 85, None, "по фото: каркас П561.09 с глухой дверью", None),
        (rack(460, f"{SLUG}-0-26"), "0-26", "Стеллаж «Каньон Лофт»", 85, None, "по фото", None),
        (rack(700, f"{SLUG}-0-27"), "0-27", "Стеллаж «Каньон Лофт»", 85, None, "по фото", None),
        (bed_1_01(), "1-01", "Кровать 2-16 «Каньон Лофт»", 86, "1-01", "спальное место 2000×1600, металлокаркас", None),
        (wardrobe_1_02(), "1-02", "Шкаф для одежды 3Д «Каньон Лофт»", 86, "1-02", None, None),
        (bedside_1_03(), "1-03", "Тумба прикроватная «Каньон Лофт»", 86, "1-03", None, None),
        (chest_0_21(led=True, did=f"{SLUG}-1-04"), "1-04", "Комод «Каньон Лофт»", 86, None,
         "по каталогу: тот же модуль, что П3.0561.0.21 (с подсветкой, как на фото)", None),
        (mirror_1_05(), "1-05", "Зеркало «Каньон Лофт»", 86, None, "по фото, навесное, с полкой", None),
        (coupe(f"{SLUG}-1-06", 1529, 2), "1-06", "Шкаф-купе 2д «Каньон Лофт»", 86, None, "по каталогу", None),
        (coupe(f"{SLUG}-1-07", 2027, 3), "1-07", "Шкаф-купе 3д «Каньон Лофт»", 86, None, "по каталогу, без зеркала", None),
        (coupe(f"{SLUG}-1-09", 2027, 3, mirror_mid=True), "1-09", "Шкаф-купе 3д «Каньон Лофт»", 86, None,
         "по каталогу, с зеркалом", None),
        (desk_2_31(), "2-31", "Стол письменный 2т «Каньон Лофт»", 86, "2-31", None, None),
    ]
    d = desk_2_30_01()
    out.append((d, "2-30-01", "Стол письменный «Каньон Лофт»", 86, "2-30-01", "тумба справа (П561.30-1)", None))
    out.append((mirror_x(d, 1250, f"{SLUG}-2-30"), "2-30", "Стол письменный «Каньон Лофт»", 86, "2-30-01",
                "тумба слева (зеркальное исполнение П561.30-1)", "not in index.json: the catalogue lists it on p. 86"))
    out.append((dining_4_28(), "4-28", "Стол обеденный «Каньон Лофт»", 86, "4-28",
                "раздвижной L1302 / 1802, построен разложенным", None))

    cat_of = {"0-06": "tables", "4-28": "tables", "1-05": "decor"}
    models = []
    for d, code, name, page, inst, note, _ in out:
        d.write()
        did = d.did
        tail = code
        category = cat_of.get(tail) or {"0": "living", "1": "bedroom", "2": "office", "4": "tables"}[tail[0]]
        m = {"id": did, "code": "П3.0561." + tail.replace("-", ".", 1).replace("-", "-", 1), "name": name,
             "collection": SLUG, "category": category, "size": d.size}
        if tail.count("-") == 2:
            a, b, c = tail.split("-")
            m["code"] = f"П3.0561.{a}.{b}-{c}"
        if inst:
            m["is"] = IS[inst]
            if inst != "0-03":
                write_cutlist(did, m["code"], name, IS[inst])
        m["page"] = page
        if tail in ("0-03", "0-04", "1-05"):
            m["mount"] = "wall"
        if note:
            m["note"] = note
        models.append(m)
        print(did)
    frag = {
        "finishes": [
            {"id": FIN, "name": "Дуб Каньон / Черный 660", "body": "door_enamel_whitey#b29e96",
             "front": "door_enamel_whitey#b29e96",
             "roles": {"frame": "door_enamel_whitey#2b2c30", "wenge": "door_enamel_whitey#46382f"},
             "swatch": "#b29e96"}],
        "profiles": {},
        "collections": [{"id": SLUG, "name": "Каньон Лофт", "brand": "Пинскдрев", "finishes": [FIN], "metal": "chrome",
                         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 81–86 (разворот 158–169). Корпус ЛДСП 16 «Дуб Каньон», "
                                 "каркас-«лофт» из ЛДСП 16 «Черный 660»: стойки 76 на передних кромках боковин, бруски под крышкой и на полу, "
                                 "цоколь-салазки; фасады без ручек (push-to-open), вкладные и накладные; подсветка LED в вариантах «с подсветкой»."}],
        "models": models,
    }
    with open(os.path.join(HERE, f"{SLUG}_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
