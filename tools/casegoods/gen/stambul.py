"""«Стамбул» (Бобруйскмебель line БМ2.773, catalogue p. 106 = pp. 208–209): bedroom set in «Белый глянец», all modules by
catalogue (no instructions): the module cut-outs on p. 209 (front-on: wardrobe, mirror, chest; the bedside table and the
bed in perspective) and the interior photo of p. 208 give the look, the printed sizes the scale.

Construction: white ЛДСП 16 carcass (tops over the sides, bottoms between them, ХДФ backs in grooves), МДФ 18 white gloss
fronts laid over the carcass; milled vertical grooves on part of some fronts; thin gold inlay strips (an 8 mm metal
strip let into the face / standing in a front joint); gold "staple" handles; the wardrobe stands on four gold
trapezoid feet, the chest and the bedside table on gold bracket legs (a flat arm under the front edge and a tapered
post). Bed: white frame headboard / footboard with an upholstered channelled velour panel in a gold frame, white side
rails hung on a black metal base (legs, slats on it), mattress 2000 × 1600 (1800).
"""
import copy

from common import dump
from skarlett import P, box_drawer

T, F = 16, 18
HS = dict(model="bar", d=144, band=12, t=10, standoff=25)   # gold staple handle, ≈ 144 long (cut-outs: 126–155)


def handle(pid, at, z, dir="up"):
    h = {"id": pid, "kind": "handle"}
    h.update(HS)
    h.update({"dir": dir, "at": [round(at[0], 1), round(at[1], 1)], "z": z})
    return h


def inlay(pid, a, b, z, d=8):
    """The gold strip: a square metal bar a → b, its middle 2 mm under the face z (it stands 2 mm proud)."""
    return {"id": pid, "kind": "rod", "section": "square", "mat": "metal", "d": d,
            "from": [a[0], a[1], z + 2 - d / 2], "to": [b[0], b[1], z + 2 - d / 2]}


def grooves(xs, y0, y1, w=3, depth=1.5):
    return {"type": "grooves", "w": w, "depth": depth, "flute": "u", "lines": [[x, y0, x, y1] for x in xs]}


def bracket_leg(tag, x, z, h, inward):
    """Gold bracket leg: a flat arm under the carcass edge (120 mm towards `inward` = ±1), a tapered post a little splayed
    out, a glide under it."""
    xp = x - inward * 4                       # the post's foot stands 4 mm further out than its top
    return [
        {"id": f"leg{tag}-arm", "kind": "rod", "section": "square", "mat": "metal", "d": 12,
         "from": [x - inward * 12, h - 6, z], "to": [x + inward * 120, h - 6, z]},
        {"id": f"leg{tag}", "kind": "rod", "mat": "metal", "d": 24, "d2": 15, "from": [x, h - 12, z], "to": [xp, 14, z]},
        P(f"leg{tag}-glide", [xp - 7, 0, z - 7, xp + 7, 14, z + 7], kind="tube", mat="metal"),
    ]


def mirror_x(parts, moves, W):
    """The left-hand variant: every x → W − x, doors hinged on the other side."""
    parts, moves = copy.deepcopy(parts), copy.deepcopy(moves)
    for p in parts:
        if "box" in p:
            b = p["box"]
            b[0], b[3] = round(W - b[3], 1), round(W - b[0], 1)
        if "at" in p:
            p["at"][0] = round(W - p["at"][0], 1)
        for k in ("from", "to"):
            if k in p:
                p[k][0] = round(W - p[k][0], 1)
        if p.get("face", {}).get("lines"):
            p["face"]["lines"] = [[W - l[0], l[1], W - l[2], l[3]] for l in p["face"]["lines"]]
        if "outline" in p:
            raise ValueError("mirror an outline by hand")
    for m in moves:
        if m.get("hinge") in ("left", "right"):
            m["hinge"] = "right" if m["hinge"] == "left" else "left"
    return parts, moves


# ------------------------------------------------------------------------------------------------ wardrobe
def wardrobe():
    W, D, H = 1940, 610, 2110
    C = D - F - 4                  # carcass 588: doors 18 + the mirror 4 glued on the middle doors
    ft = 50                        # gold feet (cut-out: 21 px of 892 for 2110)
    trap = "M {a} 50 L {b} 50 L {c} 0 L {d} 0 Z"
    p = []
    for s, (a, b) in (("l", (0, 138)), ("r", (W - 138, W))):
        o = trap.format(a=a, b=b, c=b - 15 if s == "l" else b - 15, d=a + 15)
        for zs, (z0, z1) in (("f", (C - 40, C)), ("b", (0, 40))):
            p.append(P(f"foot-{s}{zs}", [a, 0, z0, b, ft, z1], mat="metal", shape="path", outline=o, edge=1.5))
    p += [
        P("side-l", [0, ft, 0, T, H - T, C]),
        P("side-r", [W - T, ft, 0, W, H - T, C]),
        P("top", [0, H - T, 0, W, H, C + F], mat="gloss"),
        P("bottom", [T, ft, 0, W - T, ft + T, C]),
    ]
    for i, (a, b) in enumerate([(477, 493), (1447, 1463)]):
        p.append(P(f"partition-{i + 1}", [a, ft + T, 9.5, b, H - T, C]))
    for i, (a, b) in enumerate([(10, 485), (485, 1455), (1455, W - 10)]):
        p.append(P(f"back-{i + 1}", [a, ft + 10, 6, b, H - T + 6, 9.5], kind="back"))
    for s, (a, b) in (("l", (T, 477)), ("r", (1463, W - T))):
        for j, y in enumerate([420, 770, 1120, 1470, 1820]):
            p.append(P(f"shelf-{s}{j + 1}", [a + 1, y, 20, b - 1, y + T, C - 20]))
    p.append(P("shelf-m", [493, 1820, 20, 1447, 1836, C - 20]))
    p.append(P("rail", [497, 1730, C / 2 - 10, 1443, 1750, C / 2 + 10], kind="tube", mat="chrome"))
    # four doors 482 wide, 3 mm gaps, y 63..2091; 1–2 hinged left, 3–4 right; handles 38 mm in from the free edge
    y0, y1 = ft + 3, H - T - 3
    zf = C + F
    hy = 1075                                   # handle centre (cut-out)
    moves = []
    for i in range(4):
        a, b = 1.5 + i * 485, 483.5 + i * 485
        tag = str(i + 1)
        hinge = "left" if i < 2 else "right"
        free = b if hinge == "left" else a
        hx = free - 38 if hinge == "left" else free + 38
        k = handle(f"k-{tag}", [hx, hy], zf)
        if i in (0, 3):
            # outer doors: a band of six milled grooves and the gold strip (152…282 / 322 mm from the outer edge)
            sgn = 1 if i == 0 else -1
            edge = a if i == 0 else b
            xs = [round(edge + sgn * o, 1) for o in (152, 178, 204, 230, 256, 282)]
            xg = edge + sgn * 322
            door = P(f"door{tag}", [a, y0, C, b, y1, zf], kind="front", mat="gloss", face=grooves(xs, y0, y1))
            ids = [door["id"], f"strip-{tag}", k["id"]]
            p += [door, inlay(ids[1], [xg, y0], [xg, y1], zf), k]
        else:
            # mirror doors: the mirror glued on, a 75 mm white stile on the handle side
            door = P(f"door{tag}", [a, y0, C, b, y1, zf], kind="front", mat="gloss")
            ma, mb = (a + 10, b - 75) if hinge == "left" else (a + 75, b - 10)
            mir = P(f"mirror-{tag}", [ma, y0 + 10, zf, mb, y1 - 10, D], kind="mirror")
            ids = [door["id"], mir["id"], k["id"]]
            p += [door, mir, k]
        moves.append({"type": "door", "name": f"door_{tag}", "parts": ids, "hinge": hinge, "angle": 100})
    return dump("stambul-1-27-01", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------------ chest
def komod():
    W, D, H = 1190, 423, 842
    C, lg = D - F, 150
    p = [
        P("side-l", [0, lg, 0, T, H - T, C]),
        P("side-r", [W - T, lg, 0, W, H - T, C]),
        P("top", [0, H - T, 0, W, H, D], mat="gloss"),
        P("bottom", [T, lg, 0, W - T, lg + T, C]),
        P("partition", [698, lg + T, 9.5, 714, H - T, C]),
        P("back", [10, lg + 10, 6, W - 10, H - T + 6, 9.5], kind="back"),
        inlay("strip", [706, lg], [706, H - T], C + F - 2),
    ]
    for tag, x, inward in (("-lf", 25, 1), ("-rf", W - 25, -1)):
        p += bracket_leg(tag, x, C - 25, lg, inward)
    for tag, x, inward in (("-lb", 25, 1), ("-rb", W - 25, -1)):
        p += bracket_leg(tag, x, 30, lg, inward)
    moves = []
    rows = [(153, 374), (377, 598), (601, 823)]
    cols = [("l", 1.5, 700, T + 13, 685), ("r", 712, W - 1.5, 727, W - T - 13)]
    for r, (ya, yb) in enumerate(rows):
        for c, xa, xb, ba, bb in cols:
            tag = f"{c}{r + 1}"
            face = grooves([452 + 33 * i for i in range(8)], ya, yb) if c == "l" else None
            fr = P(f"front-{tag}", [xa, ya, C, xb, yb, D], kind="front", mat="gloss")
            if face:
                fr["face"] = face
            hx = 221 if c == "l" else (xa + xb) / 2          # left: centred on the plain part of the front
            k = handle(f"k-{tag}", [hx, (ya + yb) / 2], D, dir="right")
            by0 = ya + 20 if r else lg + T + 10
            box = box_drawer(tag, ba, bb, by0, yb - 20 - by0, 30, C)
            p += [fr] + box + [k]
            moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": [fr["id"]] + [q["id"] for q in box] + [k["id"]],
                          "travel": 280})
    return dump("stambul-1-31", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------------ bedside table
def tumba(left=False):
    W, D, H = 690, 423, 513
    C, lg = D - F, 160
    p = [
        P("side-l", [0, lg, 0, T, H - T, C]),
        P("side-r", [W - T, lg, 0, W, H - T, C]),
        P("top", [0, H - T, 0, W, H, D], mat="gloss"),
        P("bottom", [T, lg, 0, W - T, lg + T, C]),
        P("shelf", [T + 1, 330, 20, W - T - 1, 346, C - 20]),
        P("back", [10, lg + 10, 6, W - 10, H - T + 6, 9.5], kind="back"),
        # the narrow false front and the gold strip in the joint (cut-out: door 470, strip, panel 207)
        P("panel", [482, lg + 3, C, W - 1.5, H - T - 3, D], kind="front", mat="gloss"),
        inlay("strip", [476, lg + 3], [476, H - T - 3], D - 2),
    ]
    for tag, x, inward in (("-lf", 25, 1), ("-rf", W - 25, -1), ("-lb", 25, 1), ("-rb", W - 25, -1)):
        p += bracket_leg(tag, x, C - 25 if tag.endswith("f") else 30, lg, inward)
    door = P("door", [1.5, lg + 3, C, 470, H - T - 3, D], kind="front", mat="gloss")
    k = handle("k-1", [390, 345], D, dir="right")
    p += [door, k]
    moves = [{"type": "door", "name": "door", "parts": ["door", "k-1"], "hinge": "left", "angle": 100}]
    did = "stambul-1-30"
    if left:
        p, moves = mirror_x(p, moves, W)
        did = "stambul-1-30-01"
    return dump(did, [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------------ mirror
def mirror():
    W, D, H = 1190, 24, 557
    p = [
        P("base", [0, 0, 0, W, H, T]),
        P("mirror", [12, 50, T, 960, 507, T + 4], kind="mirror"),
        P("frame-top", [0, 507, T, W, H, D], kind="front", mat="gloss"),
        P("frame-bottom", [0, 0, T, W, 50, D], kind="front", mat="gloss"),
        P("frame-left", [0, 50, T, 12, 507, D], kind="front", mat="gloss"),
        P("frame-right", [960, 50, T, W, 507, D], kind="front", mat="gloss"),
        inlay("strip", [994, 0], [994, H], D),
    ]
    return dump("stambul-1-32", [W, D, H], p, [])


# ------------------------------------------------------------------------------------------------ beds
def bed(did, W, L, sleep_w, channels):
    """Headboard 0..44 and footboard L−44..L: a white panel, a white frame, a channelled velour panel in a gold frame;
    side rails hung between them, a black metal base inside with legs, slats, the mattress."""
    H, hb, fh = 1200, 44, 560
    inner0, inner1 = hb, L - hb
    p = [
        P("headboard", [0, 0, 0, W, H, T]),
        P("head-frame-top", [0, 1110, T, W, H, T + F], kind="front", mat="gloss"),
        P("head-frame-l", [0, 380, T, 100, 1110, T + F], kind="front", mat="gloss"),
        P("head-frame-r", [W - 100, 380, T, W, 1110, T + F], kind="front", mat="gloss"),
        P("head-frame-bottom", [100, 380, T, W - 100, 420, T + F], kind="front", mat="gloss"),
        P("head-soft", [100, 420, T, W - 100, 1110, hb], kind="soft", channels=channels),
        P("footboard", [0, 0, L - hb, W, fh, L - hb + T]),
        P("foot-frame-top", [0, fh - 70, L - hb + T, W, fh, L - hb + T + F], kind="front", mat="gloss"),
        P("foot-frame-bottom", [0, 0, L - hb + T, W, 70, L - hb + T + F], kind="front", mat="gloss"),
        P("foot-frame-l", [0, 70, L - hb + T, 70, fh - 70, L - hb + T + F], kind="front", mat="gloss"),
        P("foot-frame-r", [W - 70, 70, L - hb + T, W, fh - 70, L - hb + T + F], kind="front", mat="gloss"),
        P("foot-soft", [70, 70, L - hb + T, W - 70, fh - 70, L], kind="soft", channels=channels),
        P("rail-l", [0, 110, inner0, T, 340, inner1]),
        P("rail-r", [W - T, 110, inner0, W, 340, inner1]),
    ]
    # gold frames round the velour panels
    for tag, (x0, y0, x1, y1, z) in (("head", (100, 420, W - 100, 1110, T + F)),
                                      ("foot", (70, 70, W - 70, fh - 70, L - hb + T + F))):
        for k, (a, b) in enumerate([((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]):
            q = inlay(f"{tag}-gold-{k + 1}", a, b, z, d=6)
            p.append(q)
    # black metal base: two side members and a middle beam on legs, the slats on them
    m0 = (W - sleep_w) / 2                     # the base's inner width = the sleeping place
    for tag, (a, b) in (("l", (m0 - 40, m0)), ("r", (W - m0, W - m0 + 40)), ("m", (W / 2 - 20, W / 2 + 20))):
        p.append(P(f"base-{tag}", [a, 280, inner0, b, 320, inner1], mat="black"))
        for j, z in enumerate([inner0 + 40, (inner0 + inner1) / 2 - 20, inner1 - 80]):
            p.append(P(f"base-leg-{tag}{j + 1}", [a, 0, z, b, 280, z + 40], kind="tube", mat="black"))
    n = 24
    step = (inner1 - inner0 - 80) / n
    for i in range(n):
        z = inner0 + 40 + i * step + (step - 53) / 2
        p.append(P(f"slat-{i + 1}", [m0 - 30, 320, z, W - m0 + 30, 328, z + 53], mat="#c9a877"))
    p.append(P("mattress", [m0, 328, inner0 + (inner1 - inner0 - 2000) / 2, W - m0, 528,
                            inner0 + (inner1 - inner0 + 2000) / 2], kind="mattress"))
    return dump(did, [W, L, H], p, [])


if __name__ == "__main__":
    print(wardrobe())
    print(komod())
    print(tumba())
    print(tumba(left=True))
    print(mirror())
    print(bed("stambul-1-10", 1774, 2091, 1600, 6))
    print(bed("stambul-1-15", 1974, 2108, 1800, 7))
