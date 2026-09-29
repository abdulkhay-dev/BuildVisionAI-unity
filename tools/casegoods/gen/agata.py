"""«Агата» (Pinskdrev, catalogue pp. 26–27): every module by catalogue (no instructions exist for this collection).

Two lines of one collection: П8.986.* (p. 27, the module cut-outs) and БМ8.986.* (p. 26, the interior photos). They are the
same pieces; the БМ codes that give the same model id get the id `agata-bm-…`. Only the БМ 3Д wardrobe differs in size
(B600 against B605 of П8.986.1.06-01) — built as the catalogue writes it.

Construction (one scheme for the whole collection, read off the cut-outs and photos):
  * carcass ЛДСП 16, back ХДФ 3.5 in grooves 6 mm from the back edge, the top over the sides, the bottom between them;
  * cabinets on bent flat metal bracket legs 100 mm high (outer edge flush with the side, curved inner edge), wardrobes
    on a plinth; the bed on chrome block feet;
  * fronts 18 mm, overlaid with a 12 mm reveal of the carcass round them (the side / top / bottom edges show), 3 mm gaps;
  * handles: long bars on the top edge of every drawer and door front (the close-up p. 26), long vertical bars on the
    wardrobe doors; the mirror doors have none (they open by their edge);
  * the vitrine: a fixed top panel, a door with glass over a solid bottom panel, a drawer; glass shelves lit at the edge.
"""
import math

from common import dump, drawer_box

T = 16          # ЛДСП
F = 18          # fronts
LEG = 100       # bracket legs
REV = 12        # reveal of the carcass round the fronts
GAP = 3


# ---------------------------------------------------------------------------------------------------- helpers
def bar(pid, x, y, length, z, direction="right", band=12, t=6, standoff=10):
    """A long bar handle (satin chrome) on a front face at z; `at` is its middle."""
    return {"id": pid, "kind": "handle", "model": "bar", "at": [round(x, 2), round(y, 2)], "dir": direction, "d": length,
            "band": band, "t": t, "standoff": standoff, "z": z}


def top_bar(pid, x0, x1, top, z, length):
    """The edge bar of a drawer / door: right under the front's top edge, centred."""
    return bar(pid, (x0 + x1) / 2, top - 11, length, z)


def bracket(pid, x_outer, side, z0, z1, h=LEG, top_w=134, foot_w=45):
    """A bent flat metal bracket leg seen from the front: its outer edge flush with the carcass side (x_outer), 134 wide
    under the carcass, a concave curve down to a 45 mm foot. side = +1: the leg reaches right of x_outer, -1: left."""
    if side > 0:
        x0, x1 = x_outer, x_outer + top_w
        path = (f"M {x0} 0 L {x0} {h} L {x1} {h} C {x0 + foot_w + 30} {h - 4} {x0 + foot_w} {h * 0.55} {x0 + foot_w} 0 Z")
    else:
        x0, x1 = x_outer - top_w, x_outer
        path = (f"M {x1} 0 L {x1} {h} L {x0} {h} C {x1 - foot_w - 30} {h - 4} {x1 - foot_w} {h * 0.55} {x1 - foot_w} 0 Z")
    return {"id": pid, "kind": "panel", "mat": "metal", "box": [x0, 0, z0, x1, h, z1], "shape": "path", "outline": path,
            "edge": 1.5}


def legs4(x0, x1, zf, zb=10, t=20):
    """Bracket legs at the four corners of a carcass x0..x1 (front plates set 10 mm behind the carcass front zf)."""
    return [bracket("leg-lf", x0, 1, zf - 10 - t, zf - 10), bracket("leg-rf", x1, -1, zf - 10 - t, zf - 10),
            bracket("leg-lb", x0, 1, zb, zb + t), bracket("leg-rb", x1, -1, zb, zb + t)]


def back(pid, x0, x1, y0, y1):
    """ХДФ back in grooves (6 mm from the back edge, 6 mm into the panels round it)."""
    return {"id": pid, "kind": "back", "box": [x0 + 10, y0 + 10, 6, x1 - 10, y1 - 10, 9.5]}


def drawer(tag, fx0, fx1, fy0, fy1, zc, hbar, box_x0, box_x1, box_h=None, depth=None, travel=None):
    """A drawer: its front (fx0..fx1, fy0..fy1 at zc..zc+F), a box between box_x0..box_x1 (13 mm runner gaps) and
    the edge bar handle. Returns (parts, move)."""
    h = box_h or min(160, fy1 - fy0 - 50)
    z0 = zc - (depth or zc - 30)
    y0 = fy0 + 20
    parts = [{"id": f"front-{tag}", "kind": "front", "box": [fx0, fy0, zc, fx1, fy1, zc + F]}]
    parts += drawer_box(tag, box_x0, box_x1, y0, h, z0, zc, n=("ds", "ds", "db", "dbt"))
    for p in parts[1:]:
        p.pop("n", None)
    parts[1]["id"], parts[2]["id"], parts[3]["id"], parts[4]["id"] = (f"box-l-{tag}", f"box-r-{tag}", f"box-b-{tag}",
                                                                       f"box-bottom-{tag}")
    if hbar:
        parts.append(top_bar(f"k-{tag}", fx0, fx1, fy1, zc + F, hbar))
    mv = {"type": "drawer", "name": f"drawer_{tag}", "parts": [p["id"] for p in parts], "travel": travel or int((zc - z0) * 0.75)}
    return parts, mv


# ---------------------------------------------------------------------------------------------------- vitrine
def vitrine(did, hinge):
    """Шкаф-витрина 534×502×2050: a fixed top panel, a glazed door over a solid bottom panel, a drawer; bracket legs."""
    W, B, H = 534, 502, 2050
    C = B - F                                   # carcass depth 484
    yb, yt = LEG, H - T                         # bottom board at 100, top board at 2034
    ys, yd = 305, 1761                          # the drawer compartment's ceiling, the top compartment's floor
    yf = 636                                    # the fixed shelf behind the door's solid bottom
    p = [
        {"id": "side-l", "box": [0, yb, 0, T, yt, C]},
        {"id": "side-r", "box": [W - T, yb, 0, W, yt, C]},
        {"id": "top", "box": [0, yt, 0, W, H, B]},
        {"id": "bottom", "box": [T, yb, 0, W - T, yb + T, C]},
        {"id": "shelf-drawer", "box": [T, ys, 16, W - T, ys + T, C]},
        {"id": "shelf-fixed", "box": [T, yf, 16, W - T, yf + T, C]},
        {"id": "shelf-top", "box": [T, yd, 16, W - T, yd + T, C]},
        {"id": "front-top", "kind": "front", "box": [REV, yd + T + 0, C, W - REV, yt - GAP, B]},
        back("back", 0, W, yb, H),
    ]
    # glass shelves on pins, lit at the edge (the green glow of the catalogue photo): an LED clip on each
    for i, y in enumerate([987, 1380]):
        p.append({"id": f"glass-{i + 1}", "kind": "glass", "box": [T + 2, y, 20, W - T - 2, y + 6, C - 30]})
        p.append({"id": f"led-{i + 1}", "kind": "light", "box": [T + 2, y + 6, 40, T + 10, y + 14, 60]})
    p.append({"id": "led-top", "kind": "light", "shape": "circle", "box": [W / 2 - 20, yd - 4, C / 2 - 20, W / 2 + 20, yd, C / 2 + 20]})
    # the door: glass in a narrow frame over a solid bottom panel (one leaf)
    x0, x1 = REV, W - REV
    dy0, dy1 = ys + T, yd + T - GAP                # 321 .. 1774
    split = yf + T                                 # 652: the solid bottom ends at the fixed shelf
    door = [
        {"id": "door-solid", "kind": "front", "box": [x0, dy0, C, x1, split, B]},
        {"id": "door-glass", "kind": "front", "box": [x0, split, C, x1, dy1, B], "glass": {"frame": 14, "rebate": 6, "t": 4, "tint": "clear"}},
    ]
    hx = x1 - 26 if hinge == "left" else x0 + 26
    door.append(bar("k-door", hx, 978, 210, B, direction="up"))
    p += door
    dp, dmv = drawer("1", x0, x1, LEG + 13, ys + T - GAP, C, 360, T + 13, W - T - 13, box_h=150, depth=440)
    p += dp
    p += legs4(0, W, C)
    moves = [{"type": "door", "name": "door", "parts": [q["id"] for q in door], "hinge": hinge, "angle": 105}, dmv]
    return dump(did, [W, B, H], p, moves)


# ---------------------------------------------------------------------------------------------------- TV unit
def tv():
    """Тумба ТВ 1660×502×560: two doors, an open niche over a drawer in the middle; bracket legs at the ends."""
    W, B, H = 1660, 502, 560
    C = B - F
    yb, yt = LEG, H - T
    xa, xb = 522, 1122                    # partitions centred on the door / drawer joints at 530 and 1130
    ys = 305                              # the niche's floor over the drawer
    p = [
        {"id": "side-l", "box": [0, yb, 0, T, yt, C]},
        {"id": "side-r", "box": [W - T, yb, 0, W, yt, C]},
        {"id": "top", "box": [0, yt, 0, W, H, B]},
        {"id": "bottom", "box": [T, yb, 0, W - T, yb + T, C]},
        {"id": "part-l", "box": [xa, yb + T, 10, xa + T, yt, C]},
        {"id": "part-r", "box": [xb, yb + T, 10, xb + T, yt, C]},
        {"id": "niche-floor", "box": [xa + T, ys, 10, xb, ys + T, C]},
        {"id": "shelf-l", "box": [T + 1, 322, 20, xa - 1, 338, C - 20]},
        {"id": "shelf-r", "box": [xb + T + 1, 322, 20, W - T - 1, 338, C - 20]},
        back("back", 0, W, yb, H),
    ]
    fy0, fy1 = LEG + 13, yt - GAP                 # 113 .. 541
    moves = []
    doors = [("l", REV, 530 - 1.5, "left"), ("r", 1130 + 1.5, W - REV, "right")]
    for tag, x0, x1, hinge in doors:
        p.append({"id": f"door-{tag}", "kind": "front", "box": [x0, fy0, C, x1, fy1, B]})
        p.append(top_bar(f"k-door-{tag}", x0, x1, fy1, B, 356))
        moves.append({"type": "door", "name": f"door_{tag}", "parts": [f"door-{tag}", f"k-door-{tag}"], "hinge": hinge, "angle": 100})
    dp, dmv = drawer("1", 530 + 1.5, 1130 - 1.5, fy0, 300, C, 348, xa + T + 13, xb - 13, box_h=130, depth=430)
    p += dp
    moves.append(dmv)
    p += legs4(0, W, C)
    return dump("agata-0-02", [W, B, H], p, moves)


# ---------------------------------------------------------------------------------------------------- nightstand
def nightstand(did):
    """Тумба прикроватная 500×400×540: two drawers, bracket legs."""
    W, B, H = 500, 400, 540
    C = B - F
    yb, yt = LEG, H - T
    p = [
        {"id": "side-l", "box": [0, yb, 0, T, yt, C]},
        {"id": "side-r", "box": [W - T, yb, 0, W, yt, C]},
        {"id": "top", "box": [0, yt, 0, W, H, B]},
        {"id": "bottom", "box": [T, yb, 0, W - T, yb + T, C]},
        back("back", 0, W, yb, H),
    ]
    fy0, fy1 = LEG + 13, yt - GAP                 # 113 .. 521
    hgt = (fy1 - fy0 - GAP) / 2
    moves = []
    for i, (a, b) in enumerate([(fy0, fy0 + hgt), (fy1 - hgt, fy1)]):
        dp, dmv = drawer(str(i + 1), REV, W - REV, a, b, C, 280, T + 13, W - T - 13, box_h=130, depth=340)
        p += dp
        moves.append(dmv)
    p += legs4(0, W, C)
    return dump(did, [W, B, H], p, moves)


# ---------------------------------------------------------------------------------------------------- dressing table
def dressing_table(did):
    """Стол туалетный 1645×420×749: one top over two pedestals of three drawers, a shallow middle drawer, a modesty panel
    at the back of the knee hole; bracket legs at both edges of each pedestal."""
    W, B, H = 1645, 420, 749
    C = B - F
    yb, yt = LEG, H - T                           # top 733..749
    PW = 500                                      # pedestal width
    peds = [(0, PW), (W - PW, W)]
    p = [{"id": "top", "box": [0, yt, 0, W, H, B]}]
    moves = []
    fy0, fy1 = LEG + 13, yt - GAP                 # 113 .. 730
    hgt = (fy1 - fy0 - 2 * GAP) / 3
    for k, (a, b) in enumerate(peds):
        s = "lr"[k]
        p += [
            {"id": f"side-{s}1", "box": [a, yb, 0, a + T, yt, C]},
            {"id": f"side-{s}2", "box": [b - T, yb, 0, b, yt, C]},
            {"id": f"bottom-{s}", "box": [a + T, yb, 0, b - T, yb + T, C]},
            back(f"back-{s}", a, b, yb, yt + 10),
        ]
        for i in range(3):
            y0 = fy0 + i * (hgt + GAP)
            dp, dmv = drawer(f"{s}{3 - i}", a + REV, b - REV, y0, y0 + hgt, C, 280, a + T + 13, b - T - 13, box_h=130, depth=360)
            p += dp
            moves.append(dmv)
        p += [bracket(f"leg-{s}1f", a, 1, C - 30, C - 10), bracket(f"leg-{s}2f", b, -1, C - 30, C - 10),
              bracket(f"leg-{s}1b", a, 1, 10, 30), bracket(f"leg-{s}2b", b, -1, 10, 30)]
    # the knee hole: a modesty panel at the back, a shallow drawer on runners under the top
    p.append({"id": "modesty", "box": [PW, 234, 16, W - PW, 620, 32]})
    p.append({"id": "rail-back", "box": [PW, 620, 16, W - PW, 636, 32 + 60]})
    dp, dmv = drawer("m", PW + 1.5, W - PW - 1.5, 645, fy1, C, 0, PW + 13, W - PW - 13, box_h=55, depth=330)
    p += dp
    moves.append(dmv)
    return dump(did, [W, B, H], p, moves)


# ---------------------------------------------------------------------------------------------------- mirror
def mirror(did):
    """Зеркало 800×22×1000 (wall): a frame board 18 with a rectangular opening rounded (R155) at its top right corner,
    the mirror 4 mm behind it."""
    W, H = 800, 1000
    l, r, tp, bt, R = 50, 49, 47, 56, 155
    x1, y1 = W - r, H - tp
    k = 0.5523 * R
    hole = (f"M {l} {bt} L {x1} {bt} L {x1} {y1 - R} C {x1} {y1 - R + k} {x1 - R + k} {y1} {x1 - R} {y1} L {l} {y1} Z")
    p = [
        {"id": "frame", "shape": "path", "outline": f"M 0 0 L {W} 0 L {W} {H} L 0 {H} Z {hole}", "box": [0, 0, 4, W, H, 22],
         "edge": 3},
        {"id": "mirror", "kind": "mirror", "box": [l - 20, bt - 20, 0, x1 + 20, y1 + 20, 4]},
    ]
    return dump(did, [W, 22, H], p, [])


# ---------------------------------------------------------------------------------------------------- wardrobes
def wardrobe(did, doors, B):
    """Шкаф для одежды 3Д / 4Д, H2205, on a plinth: 460 mm doors (18 mm), the mirror doors a mirror glued on the front
    leaving a 40 mm strip on the hinge side; vertical bars on the plain doors at their free edges.
    doors: [(kind 'wood' | 'mirror', hinge 'left' | 'right'), ...]; partitions stand behind the joints where a door's
    hinge meets the next one."""
    n = len(doors)
    H = 2205
    C = B - F - 4                                   # the mirror stands 4 mm proud of the door faces
    W = {3: 1388, 4: 1850}[n]
    dw = (W - (n - 1) * GAP) / n
    xs = [(i * (dw + GAP), i * (dw + GAP) + dw) for i in range(n)]
    yb, yt = 50, H - T                              # bottom board 50..66, top 2189..2205
    p = [
        {"id": "side-l", "box": [0, 0, 0, T, H, C]},
        {"id": "side-r", "box": [W - T, 0, 0, W, H, C]},
        {"id": "top", "box": [T, yt, 0, W - T, H, C]},
        {"id": "bottom", "box": [T, yb, 0, W - T, yb + T, C]},
        {"id": "plinth-front", "box": [T, 0, C - T, W - T, yb, C]},
        {"id": "plinth-back", "box": [T, 0, 30, W - T, yb, 30 + T]},
    ]
    # partitions behind the joints between a door and a leaf hinged at that joint
    parts_x = []
    for i in range(n - 1):
        left_hinge_right = doors[i][1] == "right"
        right_hinge_left = doors[i + 1][1] == "left"
        if left_hinge_right or right_hinge_left:
            parts_x.append((xs[i][1] + xs[i + 1][0]) / 2)
    walls = [T] + [x for c in parts_x for x in (c - T / 2, c + T / 2)] + [W - T]
    for j, c in enumerate(parts_x):
        p.append({"id": f"part-{j + 1}", "box": [c - T / 2, yb + T, 10, c + T / 2, yt, C]})
    # backs: one ХДФ sheet per compartment edge to edge (joined on the partitions)
    p.append({"id": "back", "kind": "back", "box": [10, yb + 10, 6, W - 10, H - 6, 9.5]})
    # compartments: a single-door one gets shelves, a double one a hat shelf and a hanging rail
    comps = [(walls[2 * k], walls[2 * k + 1]) for k in range(len(walls) // 2)]
    for k, (a, b) in enumerate(comps):
        if b - a > 600:
            p.append({"id": f"shelf-{k + 1}-top", "box": [a, 1850, 20, b, 1866, C - 20]})
            p.append({"id": f"rail-{k + 1}", "kind": "tube", "mat": "chrome", "box": [a, 1770, C / 2 - 10, b, 1790, C / 2 + 10]})
        else:
            for i, y in enumerate([400, 750, 1100, 1450, 1850]):
                p.append({"id": f"shelf-{k + 1}-{i + 1}", "box": [a + 1, y, 20, b - 1, y + T, C - 20]})
    moves = []
    zf = C + F
    for i, ((x0, x1), (kind, hinge)) in enumerate(zip(xs, doors)):
        did_ = f"door-{i + 1}"
        grp = [did_]
        p.append({"id": did_, "kind": "front", "box": [round(x0, 2), yb, C, round(x1, 2), H - 2, zf]})
        if kind == "mirror":
            m0, m1 = (x0 + 40, x1 - 5) if hinge == "left" else (x0 + 5, x1 - 40)
            p.append({"id": f"mirror-{i + 1}", "kind": "mirror", "box": [round(m0, 2), yb + 5, zf, round(m1, 2), H - 7, zf + 4]})
            grp.append(f"mirror-{i + 1}")
        else:
            hx = x1 - 20 if hinge == "left" else x0 + 20
            p.append(bar(f"k-{i + 1}", hx, 685, 750, zf, direction="up", band=12, t=10, standoff=16))
            grp.append(f"k-{i + 1}")
        moves.append({"type": "door", "name": f"door_{i + 1}", "parts": grp, "hinge": hinge, "angle": 100})
    return dump(did, [W, B, H], p, moves)


# ---------------------------------------------------------------------------------------------------- bed
def bed(did):
    """Кровать 2-16 (sleeping place 1600×2000): a headboard with two upholstered pads between curved side wings, a box
    base of 25 mm rails on chrome block feet, a slatted base on cleats and a middle beam. x = width 1670, z = length."""
    W, L, H = 1670, 2247, 1000
    R = 25                                          # rails
    yr0, yr1 = 70, 330                              # the base rails
    p = [
        {"id": "head", "box": [0, yr0, 0, W, H, R]},
        {"id": "pad-l", "kind": "soft", "box": [R, 420, R, W / 2 - 2, H - 20, R + 150]},
        {"id": "pad-r", "kind": "soft", "box": [W / 2 + 2, 420, R, W - R, H - 20, R + 150]},
    ]
    # the wings: side boards of the headboard, their front edge curving back to the top (the catalogue's side view)
    for s, (x0, x1) in (("l", (0, R)), ("r", (W - R, W))):
        p.append({"id": f"wing-{s}", "box": [x0, 330, R, x1, H, R + 175], "shape": "path",
                  "outline": f"M {R} 330 L {R + 175} 330 C {R + 175} 700 {R + 150} 900 {R + 60} {H} L {R} {H} Z"})
    p += [
        {"id": "rail-l", "box": [0, yr0, R, R, 330, L - R]},
        {"id": "rail-r", "box": [W - R, yr0, R, W, 330, L - R]},
        {"id": "rail-foot", "box": [0, yr0, L - R, W, yr1, L]},
        {"id": "rail-head", "box": [R, yr0, 197, W - R, yr1 - 100, 222]},
        {"id": "cleat-l", "box": [R, 200, 222, R + 30, 230, L - R]},
        {"id": "cleat-r", "box": [W - R - 30, 200, 222, W - R, 230, L - R]},
        {"id": "beam", "box": [W / 2 - 15, 170, 222, W / 2 + 15, 230, L - R]},
        {"id": "beam-leg-1", "kind": "tube", "mat": "black", "box": [W / 2 - 12.5, 0, 900, W / 2 + 12.5, 170, 925]},
        {"id": "beam-leg-2", "kind": "tube", "mat": "black", "box": [W / 2 - 12.5, 0, 1600, W / 2 + 12.5, 170, 1625]},
        {"id": "mattress", "kind": "mattress", "box": [35, 238, 222, W - 35, 438, L - R - 0]},
    ]
    for i in range(24):
        z = 240 + i * 82
        p.append({"id": f"slat-{i + 1}", "kind": "panel", "mat": "#c9a877", "box": [R + 15, 230, z, W - R - 15, 238, z + 53]})
    # chrome block feet: trapezoids 150 wide at the top, 110 at the floor, 70 high, set in at the corners
    for tag, xc, z0 in (("lh", 110, 60), ("rh", W - 110, 60), ("lf", 110, L - 110), ("rf", W - 110, L - 110)):
        p.append({"id": f"foot-{tag}", "kind": "panel", "mat": "metal", "box": [xc - 75, 0, z0, xc + 75, yr0, z0 + 50],
                  "shape": "path", "outline": f"M {xc - 55} 0 L {xc + 55} 0 L {xc + 75} {yr0} L {xc - 75} {yr0} Z", "edge": 2})
    return dump(did, [W, L, H], p, [])


if __name__ == "__main__":
    print(vitrine("agata-0-01", "left"))
    print(vitrine("agata-0-01-01", "right"))
    print(tv())
    for did in ("agata-1-01", "agata-bm-1-01"):
        print(nightstand(did))
    for did in ("agata-1-02", "agata-bm-1-02"):
        print(dressing_table(did))
    for did in ("agata-1-03", "agata-bm-1-03"):
        print(mirror(did))
    for did in ("agata-1-05", "agata-bm-1-05"):
        print(bed(did))
    four = [("wood", "left"), ("mirror", "left"), ("mirror", "right"), ("wood", "right")]
    three = [("wood", "left"), ("mirror", "right"), ("wood", "right")]
    print(wardrobe("agata-1-04-01", four, 605))
    print(wardrobe("agata-bm-1-04-01", four, 605))
    print(wardrobe("agata-1-06-01", three, 605))
    print(wardrobe("agata-bm-1-06-01", three, 600))
