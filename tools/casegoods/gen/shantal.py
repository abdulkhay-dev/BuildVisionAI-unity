"""«Шанталь» (П6.952): all 8 modules by instruction (IS-P6-952-*: the cut lists of reference/shantal/cutlists, the tables of
1-01 / 1-02 / 1-04 read from the PDF's text layer into gen/cutlists/, the front / interior views on the table pages).

Construction (the same in every piece, from the instructions):
  * carcass ЛДСП 16 «Пепел»: the sides stand on a separate plinth box and run up to the top; the top and bottom
    horizontals (379 / 577 deep) between them; the plinth (МДФ 16.5 front with an arched lower edge, ЛДСП sides and back,
    80 high) lies under the bottom only, 16 mm in from the sides, on 4-mm glides ФБ 482;
  * living room (0.0x): ХДФ backs nailed on the back edges (z 0…3.5), a cornice frame of 25-mm МДФ strips «Дуб Сахара»
    (front + two sides mitred, a plain back strip) 14 mm over the carcass, and the top 17 over it, 13 mm further out;
    bedroom (1.0x): one 42-mm top («крышка») 27 mm over the carcass; 1.01 has its backs in grooves (the top is 625 =
    582 + 16.5 + 26.5), 1.02 / 1.04 nailed;
  * fronts МДФ 16.5, overlay (2–2.5 mm reveal, 3 mm gaps): a milled frame round sunk wainscot panels — vertical boards on
    doors, one horizontal joint on drawers — with a cove where the panel meets the frame; glazed doors with a 50-mm frame
    and a glazing bead; antique-nickel knobs Ø30 on doors, bar pulls c-c 128 on drawers;
  * drawer boxes ЛДСП 16, ХДФ bottom in grooves, 350 runners (13 mm each side).

    python3 tools/casegoods/gen/shantal.py        # Designs/shantal-*.json, gen/shantal_catalog.json
"""
import json
import os

from kit_w3a import (back, bar, box, dump, fmt, frame_front, glides, hlines, ids, knob, metal_base, part, vlines,
                     cornice, ring, drawer_box)

HERE = os.path.dirname(os.path.abspath(__file__))
T, FT = 16, 16.5
GR = {"type": "grooves", "w": 3, "depth": 1.5, "flute": "v"}


# ------------------------------------------------------------------------------------------------------------ pieces
def arch_bottom(x0, x1, y0, rise=32, foot=42):
    """The arched lower edge (commands from (x0, y0) to (x1, y0)): flat feet at the ends, a small shoulder, a shallow
    arch between."""
    a, b = x0 + foot, x1 - foot
    s = 8                                       # the shoulder: a quarter step up at each foot
    w = b - a - 2 * s
    ym = y0 + rise
    return (f"L {fmt(a)} {fmt(y0)} Q {fmt(a + s)} {fmt(y0)} {fmt(a + s)} {fmt(y0 + s)} "
            f"C {fmt(a + s + w * 0.12)} {fmt(ym)} {fmt(a + s + w * 0.3)} {fmt(ym)} {fmt(a + s + w / 2)} {fmt(ym)} "
            f"C {fmt(a + s + w * 0.7)} {fmt(ym)} {fmt(b - s - w * 0.12)} {fmt(ym)} {fmt(b - s)} {fmt(y0 + s)} "
            f"Q {fmt(b - s)} {fmt(y0)} {fmt(b)} {fmt(y0)} L {fmt(x1)} {fmt(y0)}")


def arch(x0, x1, y0, y1, rise=32, foot=42):
    """The plinth front's outline (front plane)."""
    return f"M {fmt(x0)} {fmt(y0)} {arch_bottom(x0, x1, y0, rise, foot)} L {fmt(x1)} {fmt(y1)} L {fmt(x0)} {fmt(y1)} Z"


def plinth(ns, x0, x1, zb, zf, rise=32, gl=None):
    """Plinth box under the bottom, x0..x1 = between the carcass sides: front МДФ 16.5 (arched), sides 16, back 16
    between them; glides under it. ns = (front, side l, side r, back)."""
    nf, nl, nr, nb = ns
    y0, y1 = 4, 84
    p = [part(None, [x0, y0, zf - FT, x1, y1, zf], nf, kind="front", shape="path", outline=arch(x0, x1, y0, y1, rise)),
         part(None, [x0, y0, zb + T, x0 + T, y1, zf - FT], nl),
         part(None, [x1 - T, y0, zb + T, x1, y1, zf - FT], nr),
         part(None, [x0 + T, y0, zb, x1 - T, y1, zb + T], nb)]
    xs = gl or [x0 + 25, x1 - 25]
    p += glides(xs, [zb + 25, zf - 25])
    return p


def door(pid, n, x0, y0, x1, y1, z0, rails=None, st=55, top=58, bot=66, mid=None):
    """A wainscot door: stiles `st`, top / bottom rails, optional middle rail(s) → panels with vertical boards."""
    ys = [y0 + bot]
    if mid:
        for (m0, m1) in mid:
            ys += [m0, m1]
    ys.append(y1 - top)
    holes = []
    for k in range(0, len(ys), 2):
        holes.append((x0 + st, ys[k], x1 - st, ys[k + 1]))
    w = x1 - x0 - 2 * st
    face = dict(GR, lines=vlines(w / 3))
    return frame_front(pid, n, x0, y0, x1, y1, z0, FT, holes, sink=4, pt=10, face=face, bead="shantal-cove")


def dfront(pid, n, x0, y0, x1, y1, z0, st=61):
    """A drawer front (the instructions' drawing): stiles `st` at the ends and between them a wainscot band — milled
    joints along the stiles and two horizontal joints at a quarter of the height from the edges."""
    h = y1 - y0
    lines = [[fmt(x0 + st), fmt(y0), fmt(x0 + st), fmt(y1)], [fmt(x1 - st), fmt(y0), fmt(x1 - st), fmt(y1)],
             [fmt(x0 + st), fmt(y0 + min(60, h * 0.25)), fmt(x1 - st), fmt(y0 + min(60, h * 0.25))],
             [fmt(x0 + st), fmt(y1 - min(60, h * 0.25)), fmt(x1 - st), fmt(y1 - min(60, h * 0.25))]]
    return [part(pid, [x0, y0, z0, x1, y1, z0 + FT], n, kind="front", face=dict(GR, lines=lines))]


def crown(n, W, D, y0):
    """The bedroom pieces' 42-mm top «крышка» (the instructions' front views: a 20-mm board over an ogee step that
    runs back to the carcass): the board over the whole top and the profiled step under its overhang, both «Дуб
    Сахара»; the moulding stands for the cut-list part."""
    return [part(f"{n}-board", [0, y0 + 22, 0, W, y0 + 42, D], mat="top", edge=4, grain="x", covers=[str(n)]),
            cornice(f"{n}-step", 0, W, 0, D, y0, "shantal-crown", mat="top")]


def glazed(pid, n, glass_n, x0, y0, x1, y1, z0):
    fr = part(pid, [x0, y0, z0, x1, y1, z0 + FT], n, kind="front",
              glass={"frame": 50, "rebate": 12, "t": 4, "tint": "clear"}, covers=[glass_n])
    zg = z0 + FT / 2 + 2
    bead = ring(f"{pid}-gb", x0 + 62, y0 + 62, x1 - 62, y1 - 62, zg, "shantal-gbead")
    return [fr, bead]


def pull(pid, x, y, z):
    return bar(pid, x, y, z, d=160, band=9, t=9, standoff=24, post=12)


def door_move(name, parts, hinge):
    return {"type": "door", "name": name, "parts": ids(parts), "hinge": hinge, "angle": 105}


def drawer_move(name, parts, travel=320):
    return {"type": "drawer", "name": name, "parts": ids(parts), "travel": travel}


def living_top(W, xc0, xc1, y, fr_ns, back_n, top_n, fz=417.5):
    """Cornice frame (moulding covering the front and side strips) + back strip + the 17 top over it (Дуб Сахара)."""
    x0, x1 = xc0 - 14, xc1 + 14
    p = [cornice("cornice", x0, x1, 3.5, fz, y, "shantal-cornice", mat="top", covers=fr_ns),
         part(None, [x0 + 70, y, 3.5, x1 - 70, y + 25, 63.5], back_n, mat="top"),
         part(None, [0, y + 25, 0, W, y + 42, 427], top_n, mat="top", edge=5, grain="x")]
    return p


# --------------------------------------------------------------------------------------------------- 0.01 / 0.03
def shkaf_0_01():
    W, B, H = 604, 427, 1997
    X0, X1 = 27, 577                     # carcass
    ZS0, ZS1 = 3.5, 387.5                # sides
    ZH1 = 382.5                          # horizontals 379 deep
    p, m = [], []
    p += [part(None, [X0, 84, ZS0, X0 + T, 1955, ZS1], 1), part(None, [X1 - T, 84, ZS0, X1, 1955, ZS1], 2),
          part(None, [X0 + T, 1939, ZS0, X1 - T, 1955, ZH1], 3), part(None, [X0 + T, 84, ZS0, X1 - T, 100, ZH1], 4),
          part(None, [X0 + T, 824, ZS0, X1 - T, 840, ZH1], 5),
          part(None, [44, 444, 5, 560, 460, 379], 6)]
    for k, y in enumerate([1230, 1590]):
        p.append(part(f"7-{k + 1}", [44, y - 6, 10, 560, y, 370], 7, kind="glass"))
        p.append({"id": f"led-{k + 1}", "kind": "light", "box": box(150, y - 10, 350, 454, y - 6, 362), "covers": ["L1"]})
    p += [back(None, [32, 84, 0, 572, 831, 3.5], 20), back(None, [32, 833, 0, 572, 1955, 3.5], 19)]
    p += plinth(("15", "16", "17", "18"), X0 + T, X1 - T, ZS0, ZS1 - 0.5, gl=[68, 214, 390, 536])      # 8 glides
    p += living_top(W, X0, X1, 1955, ["11", "12", "12.1"], "13", "14")
    # doors (hinged right, knobs at the free left edge)
    up = glazed("8", "8", "8.1", 29, 834, 575, 1954, ZS1) + [knob("k-up", 29 + 30, 1400, ZS1 + FT)]
    low = door("9", "9", 29, 85, 575, 831, ZS1) + [knob("k-low", 29 + 30, 715, ZS1 + FT)]
    p += up + low
    m += [door_move("door_up", up, "right"), door_move("door_low", low, "right")]
    return dump("shantal-0-01", [W, B, H], p, m)


def shkaf_0_03():
    W, B, H = 1154, 427, 1997
    X0, X1 = 27, 1127
    ZS0, ZS1, ZH1 = 3.5, 387.5, 382.5
    p, m = [], []
    p += [part(None, [X0, 84, ZS0, X0 + T, 1955, ZS1], 1), part(None, [X1 - T, 84, ZS0, X1, 1955, ZS1], 2),
          part(None, [569, 100, ZS0, 585, 823, ZH1], 3),
          part(None, [X0 + T, 1939, ZS0, X1 - T, 1955, ZH1], 4), part(None, [X0 + T, 84, ZS0, X1 - T, 100, ZH1], 5),
          part(None, [X0 + T, 823, ZS0, X1 - T, 839, ZH1], 6),
          part(None, [586, 444, 5, 1110, 460, 379], 7)]
    for k, y in enumerate([1230, 1590]):
        p.append(part(f"8-{k + 1}", [44, y - 6, 10, 1110, y, 370], 8, kind="glass"))
        for j, xc in enumerate([300, 850]):
            p.append({"id": f"led-{k + 1}-{j + 1}", "kind": "light", "box": box(xc - 110, y - 10, 350, xc + 110, y - 6, 362),
                      "covers": ["L1"]})
    p += [back(None, [32, 833, 0, 1122, 1955, 3.5], 23),
          back("24-1", [32, 84, 0, 576, 831, 3.5], 24), back("24-2", [578, 84, 0, 1122, 831, 3.5], 24)]
    p += plinth(("19", "20", "21", "22"), X0 + T, X1 - T, ZS0, ZS1 - 0.5, gl=[68, 400, 754, 1086])     # 8 glides
    p += living_top(W, X0, X1, 1955, ["14", "15", "16"], "17", "18")
    # glazed doors: 12 left (hinge left), 11 right (hinge right)
    dl = glazed("12", "12", "12.2", 29, 834, 575, 1954, ZS1) + [knob("k-12", 575 - 30, 1400, ZS1 + FT)]
    dr = glazed("11", "11", "11.1", 579, 834, 1125, 1954, ZS1) + [knob("k-11", 579 + 30, 1400, ZS1 + FT)]
    d10 = door("10", "10", 579, 85, 1125, 831, ZS1) + [knob("k-10", 579 + 30, 715, ZS1 + FT)]
    p += dl + dr + d10
    m += [door_move("door_left", dl, "left"), door_move("door_right", dr, "right"), door_move("door_low", d10, "right")]
    y = 85
    for k in range(3):
        y0, y1 = y, y + 246.5
        f = dfront(f"9.1-{k + 1}", "9.1", 29, y0, 575, y1, ZS1)
        bx = drawer_box(f"dr{k + 1}", 56, 556, y0 + 22, 170, ZS1 - 350, ZS1, ns=("9.2", "9.3", "9.4", "9.5"),
                        bottom_size=(478, 344))
        for q in bx:
            q["id"] = q["id"]
        h = [pull(f"k2-{k + 1}", 302, (y0 + y1) / 2, ZS1 + FT)]
        p += f + bx + h
        m.append(drawer_move(f"drawer_{k + 1}", f + bx + h))
        y = y1 + 3
    return dump("shantal-0-03", [W, B, H], p, m)



# ------------------------------------------------------------------------------------------------------------ 0.02
def tumba_0_02():
    W, B, H = 1434, 427, 610
    X0, X1 = 27, 1407
    ZS0, ZS1, ZH1 = 3.5, 387.5, 382.5
    p, m = [], []
    p += [part(None, [X0, 84, ZS0, X0 + T, 568, ZS1], 1), part(None, [X1 - T, 84, ZS0, X1, 568, ZS1], 2),
          part(None, [503, 100, ZS0, 519, 552, ZH1], 3), part(None, [915, 100, ZS0, 931, 552, ZH1], 4),
          part(None, [X0 + T, 552, ZS0, X1 - T, 568, ZH1], 5), part(None, [X0 + T, 84, ZS0, X1 - T, 100, ZH1], 6),
          part(None, [519, 326, ZS0, 915, 342, ZH1], 7)]
    p += [back("21-1", [29, 84.5, 0, 507, 567.5, 3.5], 21), back(None, [511.5, 84.5, 0, 922.5, 567.5, 3.5], 22),
          back("21-2", [927, 84.5, 0, 1405, 567.5, 3.5], 21)]
    p += plinth(("12", "13", "14", "15"), X0 + T, X1 - T, ZS0, ZS1 - 0.5, rise=30, gl=[68, 511, 717, 923, 1366])
    p += living_top(W, X0, X1, 568, ["16", "17", "18"], "19", "20")
    d8 = door("8", "8", 29.5, 85, 514.5, 567, ZS1, bot=62) + [knob("k-8", 514.5 - 30, 460, ZS1 + FT)]
    d9 = door("9", "9", 919.5, 85, 1404.5, 567, ZS1, bot=62) + [knob("k-9", 919.5 + 30, 460, ZS1 + FT)]
    p += d8 + d9
    m += [door_move("door_left", d8, "left"), door_move("door_right", d9, "right")]
    f = dfront("10.1", "10.1", 517, 85, 917, 324.5, ZS1, st=55)
    bx = drawer_box("dr", 532, 902, 107, 170, ZS1 - 350, ZS1, ns=("10.2", "10.3", "10.4", "10.5"), bottom_size=(348, 344))
    h = [pull("k2", 717, 204.75, ZS1 + FT)]
    p += f + bx + h
    m.append(drawer_move("drawer", f + bx + h))
    return dump("shantal-0-02", [W, B, H], p, m)


# ------------------------------------------------------------------------------------------------------------ 1.01
def shkaf_1_01():
    W, B, H = 1702, 625, 2200
    X0, X1 = 27, 1675
    ZS1 = 582                                          # sides 0…582, backs in grooves at z 5…8.5
    ZH1 = 577
    p, m = [], []
    p += [part(None, [X0, 84, 0, X0 + T, 2158, ZS1], 1), part(None, [X1 - T, 84, 0, X1, 2158, ZS1], 2),
          part(None, [1117, 100, 0, 1133, 2142, ZH1], 3), part(None, [569, 100, 0, 585, 324, ZH1], 4),
          part(None, [X0 + T, 2142, 0, X1 - T, 2158, ZH1], 5), part(None, [X0 + T, 84, 0, X1 - T, 100, ZH1], 6),
          part(None, [X0 + T, 1826, 0, 1117, 1842, ZH1], 7), part(None, [X0 + T, 324, 0, 1117, 340, ZH1], "7.1"),
          part("8-1", [1133, 691, 0, X1 - T, 707, ZH1], 8), part("8-2", [1133, 1427, 0, X1 - T, 1443, ZH1], 8),
          part(None, [1133, 324, 0, X1 - T, 340, ZH1], "8.1"),
          part("9-1", [1134, 1053, 5, 1658, 1069, ZH1], 9), part("9-2", [1134, 1783, 5, 1658, 1799, ZH1], 9),
          part(None, [516, 340, 8.5, 644, 1826, 24.5], 10)]
    p.append({"id": "w1", "kind": "tube", "mat": "chrome", "box": box(45, 1715, 280, 1115, 1740, 305), "covers": ["w1"]})
    p += [back("29-1", [35, 332, 5, 580, 1833, 8.5], 29), back("29-2", [580, 332, 5, 1125, 1833, 8.5], 29),
          back(None, [35, 92, 5, 1127, 339, 8.5], 28), back(None, [35, 1830, 5, 1127, 2153, 8.5], 30),
          back(None, [1125, 92, 5, 1669, 705, 8.5], 27),
          back("26-1", [1125, 697, 5, 1669, 1426, 8.5], 26), back("26-2", [1125, 1421, 5, 1669, 2150, 8.5], 26)]
    p += plinth(("17", "18", "19", "20"), X0 + T, X1 - T, 0.5, 581.5, rise=34, gl=[68, 480, 851, 1222, 1634])
    p += crown(25, W, 625, 2158)
    # doors: 11 hinge left, 12 / 13 hinge right; knobs at y 1083 (the drawing)
    xs = [(29.5, 575.5), (578, 1124), (1126.5, 1672.5)]
    hinges = ["left", "right", "right"]
    for (x0, x1), n, hg in zip(xs, ["11", "12", "13"], hinges):
        d = door(n, n, x0, 334.5, x1, 2156.5, ZS1, st=58, top=58, bot=64, mid=[(1023, 1150)])
        kx = x1 - 30 if hg == "left" else x0 + 30
        d.append(knob(f"k1-{n}", kx, 1083, ZS1 + FT))
        p += d
        m.append(door_move(f"door_{n}", d, hg))
    # drawers under the doors: 14 left, 16 middle (box 506), 15 right
    cols = [("14", 43, 569, 468), ("16", 585, 1117, 474), ("15", 1133, 1659, 468)]
    for (tag, c0, c1, bk), (x0, x1) in zip(cols, xs):
        bw = bk + 2 * T
        bx0 = (c0 + c1) / 2 - bw / 2
        f = dfront(f"{tag}.1", f"{tag}.1", x0, 85, x1, 331.5, ZS1)
        bxs = drawer_box(f"dr{tag}", bx0, bx0 + bw, 110, 170, ZS1 - 500, ZS1, ns=(f"{tag}.2", f"{tag}.3", f"{tag}.4", f"{tag}.5"),
                         bottom_size=(bk + 10, 494))
        h = [pull(f"k2-{tag}", (x0 + x1) / 2, 208, ZS1 + FT)]
        p += f + bxs + h
        m.append(drawer_move(f"drawer_{tag}", f + bxs + h, 420))
    return dump("shantal-1-01", [W, B, H], p, m)


# ------------------------------------------------------------------------------------------------------ 1.02 / 1.04
def komod_1_02():
    W, B, H = 1154, 427, 910
    X0, X1 = 27, 1127
    ZS0, ZS1, ZH1 = 3.5, 387.5, 382.5
    p, m = [], []
    p += [part(None, [X0, 84, ZS0, X0 + T, 868, ZS1], 1), part(None, [X1 - T, 84, ZS0, X1, 868, ZS1], 2),
          part(None, [X0 + T, 852, ZS0, X1 - T, 868, ZH1], 3), part(None, [X0 + T, 84, ZS0, X1 - T, 100, ZH1], 4),
          part(None, [X0 + T, 412, ZS0, X1 - T, 540, ZS0 + T], 7)]
    p += [back("17-1", [32, 84, 0, 1122, 475, 3.5], 17), back("17-2", [32, 477, 0, 1122, 868, 3.5], 17)]
    p += plinth(("8", "9", "10", "11"), X0 + T, X1 - T, ZS0, ZS1 - 0.5, rise=30, gl=[68, 441, 813, 1086])
    p += crown(16, W, 427, 868)
    rows = [("6", 85, 381, 226, 1), ("5", 384, 623.5, 170, 1), ("5", 626.5, 866, 170, 2)]
    for k, (tag, y0, y1, bh, c) in enumerate(rows):
        f = dfront(f"{tag}.1-{c}", f"{tag}.1", 29, y0, 1125, y1, ZS1)
        bx = drawer_box(f"dr{k + 1}", 56, 1098, y0 + 22, bh, ZS1 - 350, ZS1, ns=(f"{tag}.2", f"{tag}.3", f"{tag}.4", f"{tag}.5"),
                        bottom_size=(1020, 344))
        for q in bx:
            q["id"] = f"{q['id']}"
        h = [pull(f"k2-{k + 1}", 577, (y0 + y1) / 2, ZS1 + FT)]
        p += f + bx + h
        m.append(drawer_move(f"drawer_{k + 1}", f + bx + h))
    return dump("shantal-1-02", [W, B, H], p, m)


def tumba_1_04():
    W, B, H = 458, 427, 491
    X0, X1 = 27, 431
    ZS0, ZS1, ZH1 = 3.5, 387.5, 382.5
    p, m = [], []
    p += [part(None, [X0, 84, ZS0, X0 + T, 449, ZS1], 1), part(None, [X1 - T, 84, ZS0, X1, 449, ZS1], 2),
          part(None, [X0 + T, 433, ZS0, X1 - T, 449, ZH1], 3), part(None, [X0 + T, 326, ZS0, X1 - T, 342, ZH1], "3.1"),
          part(None, [X0 + T, 84, ZS0, X1 - T, 100, ZH1], 4)]
    p.append(back(None, [32, 84, 0, 426, 449, 3.5], 15))
    p += plinth(("6", "7", "8", "9"), X0 + T, X1 - T, ZS0, ZS1 - 0.5, rise=36, gl=[68, 175, 283, 390])
    p += crown(14, W, 427, 449)
    f = dfront("5.1", "5.1", 29, 85, 429, 324.5, ZS1, st=55)
    bx = drawer_box("dr", 56, 402, 110, 170, ZS1 - 350, ZS1, ns=("5.2", "5.3", "5.4", "5.5"), bottom_size=(324, 344))
    h = [pull("k2", 229, 204.75, ZS1 + FT)]
    p += f + bx + h
    m.append(drawer_move("drawer", f + bx + h))
    return dump("shantal-1-04", [W, B, H], p, m)


# ------------------------------------------------------------------------------------------------------------ 1.03
def mirror_1_03():
    p = [part(None, [0, 0, 0, 1000, 700, 16], 1, edge=2),
         part(None, [20, 20, 16, 980, 680, 20], 2, kind="mirror", edge=1)]
    return dump("shantal-1-03", [1000, 20, 700], p, [])


# ------------------------------------------------------------------------------------------------------------ 1.05
def bed_1_05():
    """Кровать 2-16: x = width 1840 (the headboard), z = length 2043 = 16.5 + 2010 + 16.5, headboard at z 0."""
    W, L, H = 1840, 2043, 921
    p = []
    hb_holes = [(55, 600, 890, 830), (950, 600, 1785, 830)]
    hb = frame_front("1", "1", 0, 3, W, 879, 0, FT, hb_holes, sink=4, pt=10, kind="panel",
                     face=dict(GR, lines=vlines(835 / 7)), bead="shantal-cove", mat="body")
    p += hb
    p.append(part(None, [0, 879, 0, W, 921, 43], "1.1", mat="top", edge=8, grain="x"))
    # footboard 2: 1646 × 482 on glides, arched lower edge, two panels facing out (+z); no bead (the checker would
    # count a front-plane moulding 16 mm deep out of B)
    fx0, fx1 = 97, 1743
    zf0 = L - FT
    fb_holes = [(fx0 + 55, 170, 895, 430), (945, 170, fx1 - 55, 430)]
    fb = frame_front("2", "2", fx0, 3, fx1, 485, zf0, FT, fb_holes, sink=4, pt=10, kind="panel",
                     face=dict(GR, lines=vlines(740 / 6)), mat="body", bottom=arch_bottom(fx0, fx1, 3, rise=90, foot=70))
    p += fb
    # side rails 3 (2010 × 200 × 16) inside the footboard's ends, between the two boards
    p += [part("3-1", [fx0, 240, FT, fx0 + T, 440, L - FT], 3), part("3-2", [fx1 - T, 240, FT, fx1, 440, L - FT], 3)]
    g = glides([60, 640, 1200, 1780], [8.25], h=3, d=16) + glides([fx0 + 35, fx1 - 35], [L - 8.25], h=3, d=16)
    for k, q in enumerate(g):
        q["id"] = f"g-{k + 1}"
    p += g
    base = metal_base(fx0 + T + 7, fx1 - T - 7, FT + 5, L - FT - 5, 410, leg_xs=[W / 2], leg_zs=[700, 1400], mattress=200)
    p += base
    return dump("shantal-1-05", [W, L, H], p, [])


def catalog():
    frag = {
        "finishes": [
            {"id": "shantal-pepel-sahara", "name": "Пепел / Дуб Сахара", "body": "door_enamel_whitey#dcddd6",
             "roles": {"top": "door_enamel_whitey#7a6a55"}, "swatch": "#dcddd6"}],
        "profiles": {
            "shantal-cornice": {"name": "Карниз «Шанталь»: рамка 70 × 25 МДФ, выкружка под свесом 14",
                                "pts": [[14, 0], [13.2, 3.5], [11, 7.5], [7.5, 11.5], [4, 15], [2, 18], [0.8, 20], [0, 21],
                                        [0, 25], [70, 25], [70, 0]]},
            "shantal-cove": {"name": "Фасад «Шанталь»: фрезерованный переход рамки к филёнке (выкружка 6 × 4)",
                             "pts": [[0, 0], [0, 4], [0.8, 2.6], [2, 1.4], [3.6, 0.5], [6, 0]]},
            "shantal-crown": {"name": "Крышка «Шанталь» 42: профильный уступ под свесом (22 × 27, каблучок)",
                              "pts": [[27, 0], [24, 1], [20.5, 2.8], [17, 5.5], [14, 9], [11, 12.5], [8, 15],
                                      [5, 16.8], [3, 18.5], [2, 20], [2, 22], [40, 22], [40, 0]]},
            "shantal-gbead": {"name": "Штапик остекления «Шанталь» 10 × 6",
                              "pts": [[0, 0], [0, 6], [4, 6], [7, 4.5], [9, 2.5], [10, 0]]}},
        "collections": [{"id": "shantal", "name": "Шанталь", "brand": "Пинскдрев", "finishes": ["shantal-pepel-sahara"],
                         "metal": "chrome#8c8983",
                         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 43–44. Все модули по инструкциям IS-P6-952-*. Корпус ЛДСП 16 «Пепел» на цоколе с аркой, фасады МДФ 16.5 фрезерованные (рамка и филёнка «вагонка»), карниз-рамка и крышка «Дуб Сахара», ручки-скобы и кнопки «античный никель»."}],
        "models": [
            {"id": "shantal-0-01", "code": "П6.952.0.01", "name": "Шкаф «Шанталь»", "collection": "shantal", "category": "living",
             "size": [604, 427, 1997], "is": "P6-952-0-01-SHkaf-1-8-2.pdf", "page": 43, "note": "с подсветкой"},
            {"id": "shantal-0-02", "code": "П6.952.0.02", "name": "Тумба «Шанталь»", "collection": "shantal", "category": "living",
             "size": [1434, 427, 610], "is": "P6-952-0-02-Tumba-1-8-3.pdf", "page": 43},
            {"id": "shantal-0-03", "code": "П6.952.0.03", "name": "Шкаф «Шанталь»", "collection": "shantal", "category": "living",
             "size": [1154, 427, 1997], "is": "P6-952-0-03-SHkaf-1-9-1.pdf", "page": 43, "note": "с подсветкой"},
            {"id": "shantal-1-01", "code": "П6.952.1.01", "name": "Шкаф для одежды 3Д «Шанталь»", "collection": "shantal",
             "category": "bedroom", "size": [1702, 625, 2200], "is": "IS-P6-952-1-01.pdf", "page": 44},
            {"id": "shantal-1-02", "code": "П6.952.1.02", "name": "Комод «Шанталь»", "collection": "shantal", "category": "bedroom",
             "size": [1154, 427, 910], "is": "IS-P6-952-1-02.pdf", "page": 44},
            {"id": "shantal-1-03", "code": "П6.952.1.03", "name": "Зеркало «Шанталь»", "collection": "shantal", "category": "decor",
             "size": [1000, 20, 700], "is": "IS-P6-952-1-03.pdf", "page": 44, "mount": "wall"},
            {"id": "shantal-1-04", "code": "П6.952.1.04", "name": "Тумба прикроватная «Шанталь»", "collection": "shantal",
             "category": "bedroom", "size": [458, 427, 491], "is": "IS-P6-952-1-04.pdf", "page": 44},
            {"id": "shantal-1-05", "code": "П6.952.1.05", "name": "Кровать 2-16 «Шанталь»", "collection": "shantal",
             "category": "bedroom", "size": [1840, 2043, 921], "is": "IS-P6-952-1-05.pdf", "page": 44,
             "note": "сп. место 2000×1600, металлокаркас"}]}
    with open(os.path.join(HERE, "shantal_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    for f in (shkaf_0_01, tumba_0_02, shkaf_0_03, shkaf_1_01, komod_1_02, mirror_1_03, tumba_1_04, bed_1_05):
        print(f())
    catalog()
